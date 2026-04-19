---
name: extract-speaker-samples
description: Cluster unique voices in an audio recording and extract a short sample of each to a file, then prompt the user to label them. Feeds diarization in downstream transcription. Use when the user asks to identify speakers, extract voice samples, prep for diarization, or label voices.
---

# Extract speaker samples

Cluster distinct voices in a recording, save a representative clip of each, and ask the user to put names to voices. The labeled samples feed diarized transcription.

## Backend

**pyannote.audio** (best quality, requires HuggingFace token for pyannote/speaker-diarization-3.1)

```bash
uv run --with pyannote.audio --with torch --with torchaudio python <<'PY'
from pyannote.audio import Pipeline
import os, torchaudio
pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
    use_auth_token=os.environ["HF_TOKEN"])
diar = pipe("INPUT.wav")
# for each SPEAKER_XX, save a 5s clip from their first turn >5s
PY
```

**resemblyzer** (lighter, no auth) — fallback if no HF token.

## Workflow

1. Load source audio.
2. Run diarization → list of (speaker_id, start, end) turns.
3. For each unique speaker_id, pick the first turn ≥ 5s.
4. Extract that 5s slice to `speakers/<source_stem>_speaker_<id>.wav` via ffmpeg.
5. Write `speakers/<source_stem>_speakers.json` with `{"speaker_1": {"sample": "...", "label": null}, ...}`.
6. Present the list of sample files to the user, asking them to listen and label.

## After labeling

User updates the JSON or renames the sample files. Downstream transcription skills (e.g. `transcribe-assemblyai`) consume `_speakers.json` for speaker name mapping.

## Output convention

Directory: `speakers/` next to the source audio.
Files: `<stem>_speaker_1.wav`, `<stem>_speaker_2.wav`, ..., `<stem>_speakers.json`.
