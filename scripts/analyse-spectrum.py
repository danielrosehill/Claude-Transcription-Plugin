#!/usr/bin/env python3
"""
Diagnose problematic frequencies in a recording.

Reads a (preferably normalised mono 16kHz WAV) audio file and reports:
- Dominant non-speech noise frequencies (hum, rumble, narrow-band whines)
- Estimated noise floor
- Likely AC hum (50/60 Hz + harmonics) presence
- Low-end rumble energy
- Broadband hiss energy

Outputs a structured JSON report. Used by the messy-audio-fix skill.

Run with:
  uv run --with numpy --with soundfile --with scipy analyse-spectrum.py INPUT.wav
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--out", type=Path, default=None,
                   help="Optional path to write JSON report")
    args = p.parse_args()

    audio, sr = sf.read(str(args.input), dtype="float32", always_2d=True)
    if audio.shape[1] > 1:
        audio = audio.mean(axis=1)
    else:
        audio = audio[:, 0]

    n = len(audio)
    duration_s = n / sr

    # Welch-style averaged FFT for stable estimate
    win_size = min(8192, n)
    hop = win_size // 2
    win = np.hanning(win_size).astype(np.float32)
    n_windows = max(1, (n - win_size) // hop + 1)

    psd_accum = np.zeros(win_size // 2 + 1, dtype=np.float64)
    for i in range(n_windows):
        start = i * hop
        chunk = audio[start : start + win_size]
        if len(chunk) < win_size:
            break
        spec = np.fft.rfft(chunk * win)
        psd_accum += (np.abs(spec) ** 2)
    psd = psd_accum / max(1, n_windows)
    freqs = np.fft.rfftfreq(win_size, 1 / sr)

    # Convert to dB
    eps = 1e-12
    psd_db = 10 * np.log10(psd + eps)

    def band_energy_db(low_hz: float, high_hz: float) -> float:
        mask = (freqs >= low_hz) & (freqs < high_hz)
        if not mask.any():
            return float("-inf")
        return float(10 * np.log10(psd[mask].sum() + eps))

    # Bands
    rumble_db   = band_energy_db(20, 80)        # AC, traffic, handling
    voice_lo_db = band_energy_db(80, 300)       # voice fundamentals
    voice_mid_db= band_energy_db(300, 3500)     # voice intelligibility
    voice_hi_db = band_energy_db(3500, 8000)    # consonants, sibilants
    hf_hiss_db  = band_energy_db(8000, sr // 2) # broadband hiss / fan / electronic

    # AC hum check: peaks at 50/60 Hz and harmonics
    def peak_at(f0: float, bw: float = 3.0) -> float:
        mask = (freqs >= f0 - bw) & (freqs <= f0 + bw)
        if not mask.any():
            return float("-inf")
        return float(psd_db[mask].max())

    hum_50_score = max(peak_at(50), peak_at(100), peak_at(150), peak_at(200))
    hum_60_score = max(peak_at(60), peak_at(120), peak_at(180), peak_at(240))
    voice_ref = (peak_at(200) + peak_at(500) + peak_at(1000)) / 3
    hum_50_rel = hum_50_score - voice_ref
    hum_60_rel = hum_60_score - voice_ref

    # Narrow-band whines: find peaks above 1.5kHz that are >15dB above local median
    whines = []
    above_voice = freqs > 1500
    for idx in np.where(above_voice)[0]:
        if idx < 5 or idx >= len(psd_db) - 5:
            continue
        local = np.median(psd_db[max(0, idx - 50) : idx + 50])
        if psd_db[idx] - local > 15 and psd_db[idx] - psd_db.mean() > 10:
            whines.append((float(freqs[idx]), float(psd_db[idx] - local)))
    whines.sort(key=lambda x: -x[1])
    whines = whines[:5]  # top 5

    # Clipping check
    clipped = float((np.abs(audio) >= 0.99).sum() / n)

    # Diagnoses
    diagnoses = []
    suggestions = []

    if rumble_db > voice_mid_db - 3:
        diagnoses.append("Excessive low-end rumble (20–80 Hz)")
        suggestions.append("highpass=f=90 (drops rumble below speech fundamentals)")

    # AC hum: voice fundamentals already produce ~5-8 dB lift in 50-60 Hz region.
    # Real hum stands out much more (15+ dB) AND is narrowband (sharp peak at exactly 50 or 60).
    # Only flag the higher of the two — you can't have both 50 and 60 Hz mains in one location.
    HUM_THRESHOLD_DB = 15
    if hum_50_rel > HUM_THRESHOLD_DB and hum_50_rel > hum_60_rel:
        diagnoses.append(f"Likely 50 Hz AC hum ({hum_50_rel:+.1f} dB above voice reference)")
        suggestions.append("Notch 50/100/150/200 Hz: equalizer=f=50:t=q:w=2:g=-25,equalizer=f=100:t=q:w=2:g=-20")
    elif hum_60_rel > HUM_THRESHOLD_DB:
        diagnoses.append(f"Likely 60 Hz AC hum ({hum_60_rel:+.1f} dB above voice reference)")
        suggestions.append("Notch 60/120/180/240 Hz: equalizer=f=60:t=q:w=2:g=-25,equalizer=f=120:t=q:w=2:g=-20")

    # Only meaningful when the input has bandwidth above 8 kHz (i.e. not already 16 kHz)
    if sr > 16000 and hf_hiss_db > voice_mid_db - 6:
        diagnoses.append("High broadband hiss above 8 kHz")
        suggestions.append("DeepFilterNet preferred over EQ — broadband noise needs ML denoising")

    for hz, prom in whines:
        diagnoses.append(f"Narrow-band whine at ~{hz:.0f} Hz (+{prom:.1f} dB above local floor)")
        suggestions.append(f"Notch: equalizer=f={hz:.0f}:t=q:w=3:g=-25")

    if clipped > 0.001:
        diagnoses.append(f"Clipping detected on {clipped*100:.2f}% of samples")
        suggestions.append("Cannot recover clipped audio. Re-record with lower input gain if possible. ASR may still cope.")

    if not diagnoses:
        diagnoses.append("No major problems detected — normal preprocess-for-transcription should suffice")

    report = {
        "input": str(args.input),
        "duration_seconds": round(duration_s, 2),
        "sample_rate": sr,
        "bands_db": {
            "rumble_20_80": round(rumble_db, 1),
            "voice_low_80_300": round(voice_lo_db, 1),
            "voice_mid_300_3500": round(voice_mid_db, 1),
            "voice_high_3500_8000": round(voice_hi_db, 1),
            "hf_hiss_8000_plus": round(hf_hiss_db, 1) if hf_hiss_db != float("-inf") else None,
        },
        "ac_hum": {
            "50hz_relative_db": round(hum_50_rel, 1),
            "60hz_relative_db": round(hum_60_rel, 1),
        },
        "narrowband_whines": [
            {"frequency_hz": round(hz, 1), "prominence_db": round(prom, 1)}
            for hz, prom in whines
        ],
        "clipping_pct": round(clipped * 100, 3),
        "diagnoses": diagnoses,
        "suggested_filters": suggestions,
    }

    out = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
