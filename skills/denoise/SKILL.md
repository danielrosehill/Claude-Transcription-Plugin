---
name: denoise
description: Remove background noise from an audio file. Cloud providers (Auphonic default, ElevenLabs, Dolby.io) or local (DeepFilterNet ML, ffmpeg afftdn non-ML). Use when the user asks to denoise, clean up noise, remove hum/hiss, or enhance speech audio before transcription.
---

# Denoise audio

Reduce background noise in a speech recording.

## Before invoking — sanity check

If the goal is **transcription**, denoising is usually not necessary. POC at
https://github.com/danielrosehill/Crying-Baby-Audio-Scrub showed Whisper handles
moderate background noise (e.g. baby crying) without preprocessing — the cleaned
and uncleaned transcripts differed by only 5–6 word choices over 119 seconds.

Reach for this skill when:

- Severe noise is degrading even-for-humans intelligibility (wind, heavy traffic, music)
- Audio is destined for human listening rather than ASR
- ASR was tried on the raw audio and produced an unusable transcript

For mild/moderate noise prepping for transcription, skip this skill — go directly
to `preprocess-for-transcription` and then transcribe.

## Provider selection

Read `~/.config/claude-transcription/config.json` for `denoise_provider` and `prefer_local`. If config missing, default to **Auphonic** (cheapest cloud option).

User may override per-invocation: "denoise with elevenlabs", "use deepfilternet", "local denoise".

## Providers

### Cloud (default)

**Auphonic** (default — ~$0.15/hr equivalent)
- API: `https://auphonic.com/api/`
- POST to `/simple/productions.json` with `input_file`, `preset`, or direct algorithm flags (`denoise=true`)
- Requires `AUPHONIC_API_KEY`
- Docs: https://auphonic.com/help/api/

**ElevenLabs Voice Isolator**
- API: `https://api.elevenlabs.io/v1/audio-isolation`
- Requires `ELEVENLABS_API_KEY`

**Dolby.io Media Enhance**
- API: `https://api.dolby.com/media/enhance`
- Requires `DOLBY_API_KEY` and an input URL (upload to Dolby temp storage first)
- Expensive (~$0.50/min) — avoid unless user explicitly requests

### Local

**DeepFilterNet** (ML, CPU-efficient)
- Install: `uv tool install deepfilternet` or `pipx install deepfilternet`
- Run: `deepFilter <input.wav> -o <output.wav>`
- Works fine on CPU; AMD GPU support via ONNX Runtime ROCm is experimental and usually not worth the setup.

**ffmpeg afftdn** (non-ML, instant)
- `ffmpeg -i input.wav -af afftdn=nf=-25 output.wav`
- Lower quality but zero dependencies and immediate.

## Output convention

Write to `<source_stem>.denoised.<ext>` in the same directory as source, unless user specifies a path.

## Error handling

- If API key env var missing → report which var and which provider, suggest running `/configure`.
- If `ffmpeg` missing → tell user to install it.
- If cloud API returns error → report status + body, don't silently fall back.
