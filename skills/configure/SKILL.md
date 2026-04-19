---
name: configure
description: Onboarding for Claude-Transcription — sets denoise provider, transcription provider, default output directory, cloud-vs-local preference. Writes ~/.config/claude-transcription/config.json. Use when the user asks to configure claude-transcription, set up the plugin, change defaults, or pick providers.
---

# Configure Claude-Transcription

Interactive (or argument-driven) setup for plugin defaults.

## Config path

`~/.config/claude-transcription/config.json`

Create parent directories if missing.

## Default config if file absent

```json
{
  "denoise_provider": "auphonic",
  "transcription_provider": "gemini",
  "default_output_dir": null,
  "prefer_local": false,
  "whisper_model": "medium",
  "whisper_device": "cpu",
  "auphonic_api_key_env": "AUPHONIC_API_KEY",
  "elevenlabs_api_key_env": "ELEVENLABS_API_KEY",
  "assemblyai_api_key_env": "ASSEMBLYAI_API_KEY",
  "dolby_api_key_env": "DOLBY_API_KEY",
  "hf_token_env": "HF_TOKEN"
}
```

## Interactive flow

If no args given, ask the user:

1. **Denoise provider** — `auphonic` (default, cheapest cloud), `elevenlabs`, `dolby`, `deepfilternet` (local ML), `afftdn` (local non-ML)
2. **Transcription provider** — `gemini` (default), `assemblyai` (timestamps + diarization), `whisper-local`
3. **Default output directory** — path or blank (means: alongside source file)
4. **Prefer local over cloud?** — y/N
5. **Check env vars** — for the chosen cloud provider(s), verify `$AUPHONIC_API_KEY` / `$ASSEMBLYAI_API_KEY` / etc. are set. If not, list which env vars need to be set and point the user at their shell profile.

## Argument-driven

Accept flags: `--denoise auphonic --transcribe gemini --prefer-local false --output-dir ~/Transcripts`.

## Show current config

If the user runs `/configure show` or similar, print the current config contents.

## Validation

- Reject unknown providers.
- Warn if `prefer_local: true` is set but no local backend is installed (no whisper, no deepfilternet).
