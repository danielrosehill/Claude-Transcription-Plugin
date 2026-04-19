---
name: transcribe-gemini-raw
description: Transcribe an audio file to a raw verbatim transcript using the gemini-transcription MCP server. Preserves every word including fillers. Use when the user asks for a raw transcript, verbatim transcription, or unedited text via Gemini.
---

# Transcribe (Gemini, raw verbatim)

Produce a word-for-word transcript including fillers (ums, ahs, repetitions).

## How

Call the `gemini-transcription` MCP tool `transcribe_audio_raw` (or `transcribe_audio` with `style: "raw"` / `preset: "verbatim"`). Check available presets first with `list_transcription_presets`.

## System prompt (if tool accepts custom)

> Transcribe this audio verbatim. Include every word the speaker says, including filler words (um, uh, like), false starts, and repetitions. Do not paraphrase. Do not clean up grammar. Output plain text only, no speaker labels unless multiple speakers are clearly present.

## Output convention

Save to `<source_stem>.raw.txt` in the source directory (or user-specified path).

## Errors

- If the MCP server is not available, tell the user to install the `gemini-transcription` MCP and point them at the server's docs.
- If the file is too large for a single Gemini request, suggest chunking via the `normalize-format` skill first or splitting with ffmpeg.
