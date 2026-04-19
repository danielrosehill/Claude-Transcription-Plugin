---
name: transcribe-whisper-local
description: Transcribe audio locally using Whisper (offline, no cloud). Use when the user asks for a local transcription, offline transcription, privacy-preserving transcription, or explicitly requests Whisper.
---

# Transcribe (local Whisper)

Offline transcription with Whisper. Requires `setup-whisper` to have been run once.

## Preferred implementation

**faster-whisper** (CTranslate2 backend) — 4x faster than openai-whisper at similar accuracy.

```bash
uv run --with faster-whisper python <<'PY'
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe("INPUT.wav", beam_size=5, vad_filter=True)
for s in segments:
    print(f"[{s.start:.2f}s -> {s.end:.2f}s] {s.text}")
PY
```

## Model selection

- `base` / `small` → fast, decent quality, good default for English
- `medium` → good balance (default)
- `large-v3` → best quality, slow on CPU

Config `whisper_model` in config.json (default `medium`).

## GPU

Daniel's workstation has an AMD GPU. faster-whisper supports ROCm via CTranslate2 builds but it's fragile; default CPU unless user has set `whisper_device: "cuda"` / `"rocm"`.

## Output convention

`<source_stem>.whisper.md` — timestamped plain text.
`<source_stem>.whisper.json` — segments with start/end/text for downstream use.

## If not set up

If `which faster-whisper` fails, tell the user to run `/setup-whisper` first.
