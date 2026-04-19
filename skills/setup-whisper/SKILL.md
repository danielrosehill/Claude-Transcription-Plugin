---
name: setup-whisper
description: One-time setup for local Whisper transcription — installs faster-whisper and downloads a default model. Use when the user asks to set up whisper, install whisper, or prepare for local transcription.
---

# Setup local Whisper

One-time install for offline transcription.

## Steps

1. Ensure `uv` is available (`which uv`). If not, install: `curl -LsSf https://astral.sh/uv/install.sh | sh`.

2. Install `faster-whisper` as a tool:
   ```bash
   uv tool install faster-whisper
   ```
   (Or create a dedicated venv if the user prefers — check preference.)

3. Pre-download the default model (`medium`) so first real transcription doesn't block:
   ```bash
   uv run --with faster-whisper python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
   ```

4. Write/update `~/.config/claude-transcription/config.json` with:
   ```json
   { "whisper_installed": true, "whisper_model": "medium", "whisper_device": "cpu" }
   ```

5. Confirm with a 5-second synthetic test (optional) — or just tell the user setup is complete.

## Model size guidance

Ask the user which model they want pre-downloaded:
- `base` — 150 MB, fastest
- `small` — 500 MB, good for most use
- `medium` — 1.5 GB, default balance
- `large-v3` — 3 GB, highest accuracy

## AMD GPU note

If the user wants ROCm acceleration, warn that CTranslate2 ROCm support is experimental and document the extra steps (install `ctranslate2` built against ROCm, set `whisper_device: "cuda"`). Default to CPU.
