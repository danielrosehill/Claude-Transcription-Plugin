---
name: truncate-silence
description: Remove long silences from an audio file using VAD (voice activity detection). Use when the user asks to truncate silence, remove gaps, trim pauses, or apply VAD to an audio recording.
---

# Truncate silence

Strip long silent regions from a recording before transcription.

## Backends

### ffmpeg silenceremove (default, zero-deps)

```bash
ffmpeg -i INPUT \
  -af "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-40dB:detection=peak,\
       silenceremove=stop_periods=-1:stop_duration=1.0:stop_threshold=-40dB:detection=peak" \
  OUTPUT
```

Thresholds tuned for speech. Expose `--threshold-db` and `--min-silence` params.

### silero-vad (ML, more accurate)

```bash
uv run --with silero-vad --with torch --with torchaudio python -c '...'
```

Use when ffmpeg leaves residual silence or when recording has low-volume speech.

## Output convention

`<source_stem>.trimmed.<ext>`

## When to use which

- Short recording, clear voice, loud noise floor → ffmpeg.
- Long meeting, quiet speakers, background hum → silero-vad.
- If user says "use VAD" → silero-vad.
