#!/usr/bin/env python3
"""
Silero-VAD-based silence collapsing.

Replaces silences longer than --min-gap with a fixed-length pause (--pad), preserving
shorter natural pauses unchanged. Designed for solo voice memos where think/sip pauses
should survive but dead air should not.

Input must be a WAV file (caller pre-decodes via ffmpeg). This keeps the deps minimal
and avoids torchaudio's codec entanglement.

Run with: uv run --with silero-vad --with soundfile --with numpy silence-collapse.py ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from silero_vad import get_speech_timestamps, load_silero_vad


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="Input WAV file (mono 16kHz preferred; downmix/resample applied if not)")
    p.add_argument("output", type=Path, help="Output WAV file (caller re-encodes if needed)")
    p.add_argument("--max-gap", type=float, default=0.4,
                   help="Cap every silence at this length (seconds). Gaps shorter than this are preserved as-is; longer gaps are truncated.")
    p.add_argument("--head-tail", type=float, default=0.3,
                   help="Preserve this much audio before first / after last speech (seconds)")
    # legacy / no-op — kept for backward compat with old callers
    p.add_argument("--min-gap", type=float, default=None, help=argparse.SUPPRESS)
    p.add_argument("--pad", type=float, default=None, help=argparse.SUPPRESS)
    p.add_argument("--stats", type=Path, default=None,
                   help="Optional JSON file to write stats to")
    args = p.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1

    model = load_silero_vad()
    audio, sr = sf.read(str(args.input), dtype="float32", always_2d=True)
    # Mono downmix
    if audio.shape[1] > 1:
        audio = audio.mean(axis=1)
    else:
        audio = audio[:, 0]
    if sr != 16000:
        # Caller is expected to have resampled; bail loudly if not
        print(f"error: expected 16kHz input, got {sr} Hz — resample upstream", file=sys.stderr)
        return 1
    wav = torch.from_numpy(audio)

    speech = get_speech_timestamps(wav, model, sampling_rate=sr, return_seconds=True)
    if not speech:
        print("warning: no speech detected; copying input unchanged", file=sys.stderr)
        sf.write(str(args.output), wav.numpy(), sr, subtype="PCM_16")
        return 0

    max_gap_samples = int(args.max_gap * sr)
    cap_pad = torch.zeros(max_gap_samples)

    parts: list[torch.Tensor] = []
    head_start = max(0.0, speech[0]["start"] - args.head_tail)
    parts.append(wav[int(head_start * sr) : int(speech[0]["end"] * sr)])

    for prev, cur in zip(speech, speech[1:]):
        gap = cur["start"] - prev["end"]
        if gap > args.max_gap:
            # truncate the gap to max_gap (no speech ever clipped)
            parts.append(cap_pad)
        else:
            # keep natural pause exactly as recorded
            parts.append(wav[int(prev["end"] * sr) : int(cur["start"] * sr)])
        parts.append(wav[int(cur["start"] * sr) : int(cur["end"] * sr)])

    tail_end = min(len(wav) / sr, speech[-1]["end"] + args.head_tail)
    if tail_end > speech[-1]["end"]:
        parts.append(wav[int(speech[-1]["end"] * sr) : int(tail_end * sr)])

    result = torch.cat(parts).numpy()
    sf.write(str(args.output), result, sr, subtype="PCM_16")

    in_s = len(wav) / sr
    out_s = len(result) / sr
    stats = {
        "input_seconds": round(in_s, 2),
        "output_seconds": round(out_s, 2),
        "removed_seconds": round(in_s - out_s, 2),
        "removed_pct": round(100 * (in_s - out_s) / in_s, 1) if in_s else 0,
        "speech_segments": len(speech),
        "max_gap": args.max_gap,
    }
    if args.stats:
        args.stats.write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
