---
name: transcribe-gemini-raw
description: Transcribe an audio file to a raw verbatim transcript using the gemini-transcription MCP server. Preserves every word including fillers. Use when the user asks for a raw transcript, verbatim transcription, or unedited text via Gemini.
---

# Transcribe (Gemini, raw verbatim)

Produce a word-for-word transcript including fillers (ums, ahs, repetitions).

## How

Call the `gemini-transcription` MCP tool `transcribe_audio_raw` (or `transcribe_audio` with `style: "raw"` / `preset: "verbatim"`). Check available presets first with `list_transcription_presets`.

## Getting the audio to Gemini (`file_url`)

The MCP fetches audio by URL, so a local file needs one. Default route: stage it in the
Wasabi bucket `danielrosehill-ephemeral-staging` and pass a presigned URL
(`~/.claude/context/file-staging.md`).

**Build-in-public shortcut.** When the audio is going into a **public** repo anyway (an idea
voice note seeding a new public repo, a recording that is part of the project), skip staging:
commit and push the file, then pass its raw URL as `file_url`:

```
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path/to/file.mp3>
```

(`https://github.com/<owner>/<repo>/raw/<branch>/<path>` also works; it redirects there.)
Check it with `curl -sIL <url>` (expect 200 and a non-zero `content-length`) before calling
the tool.

- **Public repos only.** Private raw URLs need a token; Gemini cannot fetch them and you get
  a fetch error or an empty result. Use Wasabi for those.
- **Size:** GitHub rejects files over 100 MB and warns above 50 MB. Compress
  (`normalize-format`) or use Wasabi.
- **Permanent:** the file stays in public git history even if deleted later. Only use this
  when publishing the audio is the intent, not as a convenience for private recordings.
- **Filenames:** URL-encode spaces (`%20`) or rename the file to a slug before committing.

## System prompt (if tool accepts custom)

> Transcribe this audio verbatim. Include every word the speaker says, including filler words (um, uh, like), false starts, and repetitions. Do not paraphrase. Do not clean up grammar. Output plain text only, no speaker labels unless multiple speakers are clearly present.

## Output convention

Save to `<source_stem>.raw.txt` in the source directory (or user-specified path).

## Errors

- If the MCP server is not available, tell the user to install the `gemini-transcription` MCP and point them at the server's docs.
- If the file is too large for a single Gemini request, suggest chunking via the `normalize-format` skill first or splitting with ffmpeg.
