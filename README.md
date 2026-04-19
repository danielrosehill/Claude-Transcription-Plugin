# Claude-Transcription

End-to-end audio-to-transcript pipeline as a Claude Code plugin. Preprocess long-form recordings, transcribe via cloud or local engines, post-process into clean/structured/blog/summary formats, combine versions, and export.

## Pipeline

```
audio ──► preprocess ──► transcribe ──► post-process ──► combine ──► export
```

## Skills

### Preprocessing
- `denoise` — remove background noise. Cloud: Auphonic (default, cheapest), ElevenLabs Voice Isolator, Dolby.io. Local: DeepFilterNet (ML) or ffmpeg `afftdn` (non-ML).
- `truncate-silence` — VAD-based silence removal (silero-vad or ffmpeg `silenceremove`).
- `normalize-format` — stereo→mono, 16kHz resample, compress WAV to opus/mp3.
- `extract-speaker-samples` — cluster unique voices in the audio, emit short per-speaker samples for user to label (feeds diarization).

### Transcription
- `transcribe-gemini-raw` — verbatim via gemini-transcription MCP.
- `transcribe-gemini-cleaned` — filler words removed at transcription time.
- `transcribe-assemblyai` — timestamped + diarization via AssemblyAI.
- `transcribe-whisper-local` — offline transcription via local Whisper.
- `setup-whisper` — one-time local Whisper installation.

### Post-processing
- `clean-transcript` — strip fillers (ums, likes, repetitions) from an existing transcript.
- `structure-transcript` — add headers, logical sections, paragraph breaks.
- `transcript-to-blog` — rewrite as a publishable blog post.
- `transcript-to-summary` — executive summary + bullet highlights.
- `transcript-to-notes` — structured meeting/study notes.

### Compilation & Export
- `combine-versions` — concatenate raw + cleaned + structured into one doc. Markdown (variant headers) or Typst → PDF (page numbers, variant in footer).
- `export-transcript` — email, upload to Google Drive, or copy to clipboard.

### Config
- `configure` — onboarding: pick denoise + transcription providers, set default output directory, toggle cloud/local preference.

## Defaults

- **Cloud over local** for every skill that offers both. Override via `configure` or per-invocation.
- **Denoise**: Auphonic (cheapest cloud option at ~$0.15/hr).
- **Transcription**: Gemini (raw or cleaned).

See [CLAUDE.md](CLAUDE.md) for config file schema and conventions.

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install claude-transcription@danielrosehill
```

Then restart Claude Code.

## External requirements

- `ffmpeg` — preprocessing
- `python3` + `uv` — for skills that shell out to Python (DeepFilterNet, silero-vad, pyannote, whisper)
- MCP servers: `gemini-transcription`, `gws-personal` (for Drive export)
- API keys (set as env vars, names configurable): `AUPHONIC_API_KEY`, `ELEVENLABS_API_KEY`, `ASSEMBLYAI_API_KEY`, `DOLBY_API_KEY`

## License

MIT
