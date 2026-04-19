---
name: transcribe-assemblyai
description: Transcribe audio via AssemblyAI with word-level timestamps and speaker diarization. Best for meetings, interviews, and anything needing speaker labels or timecodes. Use when the user asks for a timestamped transcript, diarized transcript, or multi-speaker transcription.
---

# Transcribe (AssemblyAI, timestamped + diarized)

Produce a transcript with word-level timestamps and speaker turns.

## Requirements

- `ASSEMBLYAI_API_KEY` env var (name configurable in config.json).
- Source audio accessible — AssemblyAI accepts URL or uploaded file.

## How

1. Upload file: `POST https://api.assemblyai.com/v2/upload` (bytes of audio, `Authorization: <key>`).
2. Create transcript: `POST https://api.assemblyai.com/v2/transcript` with
   ```json
   {
     "audio_url": "<upload_url>",
     "speaker_labels": true,
     "punctuate": true,
     "format_text": true
   }
   ```
3. Poll `GET /v2/transcript/<id>` until `status == "completed"`.
4. Render output.

## Speaker name mapping

If `<source_stem>_speakers.json` exists (from `extract-speaker-samples`), remap AssemblyAI's `A`/`B`/`C` labels to user-provided names.

## Output convention

Save to `<source_stem>.timestamped.md`. Format:

```
[00:00:03] **Alice:** Welcome to the call.
[00:00:07] **Bob:** Thanks for having me.
```

Also save raw AssemblyAI JSON to `<source_stem>.assemblyai.json` for downstream use.

## Cost

Roughly $0.37/hr with speaker labels. Flag this if the audio is very long (>4 hours).
