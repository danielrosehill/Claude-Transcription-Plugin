---
name: preprocess-for-transcription
description: Prepare audio for transcription — format normalise (mono/16kHz/opus), loudness normalise (EBU R128), and collapse long silences (silero-vad). Optional denoise pass. Use before sending to AssemblyAI or any ASR for cleaner results, smaller uploads, and lower cost. Use when the user asks to "preprocess audio", "prep for transcription", "clean up a recording before sending it", or just hands over a raw voice memo to be transcribed.
---

# Preprocess audio for transcription

Single orchestrator that takes a raw recording and emits a transcription-ready file. Source is never modified.

## Pipeline (order matters)

| Pass | Default | Notes |
|---|---|---|
| 1. Denoise | **off** (flag `--denoise`) | turn on for noisy field recordings, leave off for clean voice memos |
| 2. Format normalise | **on** | mono, 16 kHz, opus 24k |
| 3. Loudness normalise | **on** | EBU R128 via ffmpeg `loudnorm` |
| 4. Silence collapse | **on** | silero-vad, only collapse silences > 2.5s, compress to 0.5s, preserve 0.3s head/tail |

Passes 2+3 run in a single ffmpeg invocation (one decode/encode). Pass 4 runs after.

## Folder convention

If invoked inside an existing project structure with `audio/` or `context/` already present, respect it. Otherwise:

- Source stays where it is, or moves to `audio/raw/<basename>` if the user is OK with that
- Output: `audio/processed/<stem>.preprocessed.opus`
- Side-files (loudnorm stats, VAD segment data): `audio/processed/<stem>.<ext>`

Never overwrite — if `<stem>.preprocessed.opus` exists, suffix `.v2`, `.v3`, etc.

## Implementation

### Pass 1 — denoise (optional)

```bash
# rnnoise via ffmpeg (zero extra deps if ffmpeg built with --enable-librnnoise)
ffmpeg -i INPUT -af "arnndn=m=/path/to/model.rnnn" -c:a pcm_s16le DENOISED.wav
```

If rnnoise model unavailable, fall back to:
```bash
ffmpeg -i INPUT -af "afftdn=nf=-25" DENOISED.wav
```

### Passes 2 + 3 — format + loudness (combined)

Two-pass loudnorm is more accurate but slower. For voice memos, single-pass is fine:

```bash
ffmpeg -i INPUT \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ac 1 -ar 16000 -c:a libopus -b:a 24k \
  STEM.normalised.opus
```

Targets: `-16 LUFS` integrated, `-1.5 dBTP` true peak, `11 LU` range — standard for spoken content.

### Pass 4 — silence collapse via silero-vad

silero is far more reliable than ffmpeg's energy threshold for soft dictation. Run via uv:

```bash
uv run --with silero-vad --with torchaudio --with soundfile python <<'PY'
import torch, torchaudio, soundfile as sf, sys, json
from silero_vad import load_silero_vad, get_speech_timestamps, collect_chunks

INPUT  = "STEM.normalised.opus"
OUTPUT = "STEM.preprocessed.opus"
MIN_GAP_S = 2.5      # only collapse silences longer than this
PAD_S     = 0.5      # replace long gaps with this much silence
HEAD_TAIL_S = 0.3    # preserve at start/end

model = load_silero_vad()
wav, sr = torchaudio.load(INPUT)
wav = wav.mean(dim=0)  # mono
if sr != 16000:
    wav = torchaudio.functional.resample(wav, sr, 16000); sr = 16000

speech = get_speech_timestamps(wav, model, sampling_rate=sr, return_seconds=True)
# Build output by concatenating speech regions, inserting PAD_S of silence between
# any two regions whose gap exceeds MIN_GAP_S; keep gaps shorter than that intact.
out = []
prev_end = 0.0
silence_pad = torch.zeros(int(PAD_S * sr))
for i, seg in enumerate(speech):
    start, end = seg["start"], seg["end"]
    if i == 0:
        # preserve a small head before first speech
        head = max(0.0, start - HEAD_TAIL_S)
        out.append(wav[int(head*sr):int(end*sr)])
    else:
        gap = start - prev_end
        if gap > MIN_GAP_S:
            out.append(silence_pad)
            out.append(wav[int(start*sr):int(end*sr)])
        else:
            # keep the natural pause as-is
            out.append(wav[int(prev_end*sr):int(end*sr)])
    prev_end = end

# preserve a small tail
tail_end = min(len(wav)/sr, prev_end + HEAD_TAIL_S)
if tail_end > prev_end:
    out.append(wav[int(prev_end*sr):int(tail_end*sr)])

result = torch.cat(out).numpy()
sf.write("STEM.preprocessed.wav", result, sr)
# stats
total_in = len(wav)/sr
total_out = len(result)/sr
json.dump({
    "input_seconds": round(total_in, 2),
    "output_seconds": round(total_out, 2),
    "removed_seconds": round(total_in - total_out, 2),
    "speech_segments": len(speech),
}, open("STEM.vad-stats.json", "w"), indent=2)
PY

# Re-encode to opus 24k
ffmpeg -y -i STEM.preprocessed.wav -c:a libopus -b:a 24k STEM.preprocessed.opus
rm STEM.preprocessed.wav STEM.normalised.opus
```

## Output report

After running, print:

```
Input:        recording.m4a (12m 04s, stereo 48kHz, 14 MB)
Output:       audio/processed/recording.preprocessed.opus (9m 18s, mono 16kHz, 1.6 MB)
Removed:      2m 46s of silence (23%)
Loudness:     normalised to -16 LUFS
Denoise:      skipped (use --denoise to enable)
```

## Flags

- `--denoise` — enable pass 1
- `--no-silence-trim` — skip pass 4 (keep all silence)
- `--silence-threshold <seconds>` — override default 2.5s
- `--out-dir <path>` — override default `audio/processed/`

## When to skip this skill

- Audio is already `mono 16kHz opus` and was recorded in a controlled environment → just transcribe directly
- User explicitly wants raw audio sent (e.g. needs maximum fidelity for diarisation testing)

## Defaults locked against

Tested against `~/repos/github/my-repos/Job-Search-Planning-0426/context/2026_04_28_16_05_22.opus` — a long voice memo with sip/think pauses. The 2.5s threshold preserves natural pacing while removing dead air.
