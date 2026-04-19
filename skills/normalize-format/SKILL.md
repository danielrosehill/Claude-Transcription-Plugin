---
name: normalize-format
description: Convert audio to a transcription-friendly format — stereo to mono, resample to 16kHz, compress WAV to opus or mp3, reduce bitrate. Use when the user asks to normalize audio format, downmix, resample, compress, or prepare audio for transcription.
---

# Normalize audio format

Standardize audio for transcription pipelines. Transcription engines generally work best at 16kHz mono, and compressed formats (opus) are faster to upload without quality loss for speech.

## Default transform

```bash
ffmpeg -i INPUT -ac 1 -ar 16000 -c:a libopus -b:a 24k OUTPUT.opus
```

- `-ac 1` → mono
- `-ar 16000` → 16 kHz sample rate
- `libopus @ 24k` → excellent speech quality at ~11 MB/hr

## Variants

- **Whisper-native WAV**: `-ac 1 -ar 16000 -c:a pcm_s16le OUTPUT.wav`
- **MP3 (compatibility)**: `-ac 1 -ar 16000 -c:a libmp3lame -b:a 32k OUTPUT.mp3`
- **Preserve sample rate**: omit `-ar`

## Output convention

`<source_stem>.normalized.<ext>`

## Parameters

User may specify:
- target format (`opus`/`mp3`/`wav`)
- bitrate
- keep stereo (`--stereo`)
- preserve sample rate (`--keep-sr`)
