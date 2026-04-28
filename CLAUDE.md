# Claude-Transcription — Plugin Instructions

End-to-end pipeline for recording, transcribing, and post-processing long-form audio.

## Default preference: cloud over local

When the user invokes a skill that has both a cloud and a local option (denoise, transcription), **default to the cloud provider** unless:

1. The user has run `/configure` and set `prefer_local: true` in `~/.config/claude-transcription/config.json`, or
2. The user explicitly requests local in the invocation ("transcribe locally", "use whisper", "offline").

Rationale: cloud providers are faster, higher-quality, and the cost is negligible at the user's volume. Local is a fallback for offline/privacy scenarios.

## Transcription provider preference order

When a skill needs a transcript and the user hasn't named a provider, choose in this order:

1. **AssemblyAI** — preferred default. Word-level timestamps, speaker diarization, robust on long-form audio. Cost ~$0.37/hr.
2. **Gemini MCP** (`gemini-transcription`) — fallback when AssemblyAI is unavailable, the user explicitly asks for it, or the audio is short enough that diarization is unnecessary.
3. **Whisper local** — only if `prefer_local: true` or explicitly requested.

Skills that orchestrate transcription (e.g. `transcribe-podcast`) should call AssemblyAI first and fall back to Gemini only on failure.

## Config file

All skills read from `~/.config/claude-transcription/config.json`. Created/edited by the `configure` skill.

Schema:
```json
{
  "denoise_provider": "auphonic|elevenlabs|dolby|deepfilternet|afftdn",
  "transcription_provider": "gemini|assemblyai|whisper-local",
  "default_output_dir": "/path/or/null",
  "prefer_local": false,
  "auphonic_api_key_env": "AUPHONIC_API_KEY",
  "elevenlabs_api_key_env": "ELEVENLABS_API_KEY",
  "assemblyai_api_key_env": "ASSEMBLYAI_API_KEY",
  "dolby_api_key_env": "DOLBY_API_KEY"
}
```

Defaults if config missing:
- `denoise_provider`: `auphonic` (cheapest cloud option)
- `transcription_provider`: `assemblyai`
- `default_output_dir`: directory of source audio file
- `prefer_local`: `false`

## Pipeline stages

1. **Preprocess** — `denoise`, `truncate-silence`, `normalize-format`, `extract-speaker-samples`
2. **Transcribe** — `transcribe-gemini-raw`, `transcribe-gemini-cleaned`, `transcribe-assemblyai`, `transcribe-whisper-local` (requires `setup-whisper`)
3. **Post-process** — `clean-transcript`, `structure-transcript`, `transcript-to-blog`, `transcript-to-summary`, `transcript-to-notes`
4. **Combine** — `combine-versions` (markdown or Typst→PDF)
5. **Export** — `export-transcript` (email, Drive, clipboard)

## File naming convention

All skills emit files with a predictable suffix so downstream skills can find them:

- `recording.wav` → source
- `recording.denoised.wav`
- `recording.normalized.wav`
- `recording.raw.txt` → raw transcript
- `recording.cleaned.md` → filler-word removed
- `recording.structured.md` → headers added
- `recording.blog.md`
- `recording.summary.md`
- `recording.notes.md`
- `recording.combined.md` / `recording.combined.pdf`

Preserving this convention lets users chain skills without re-specifying paths.

## MCP dependencies

This plugin assumes the following MCP servers are available (not bundled):

- **gemini-transcription** — for Gemini transcription
- **gws-personal** — for Google Drive upload
- **email-skills** (not MCP, skill-set) — for emailing transcripts

If a required MCP is missing, the skill should report it clearly rather than silently fail.
