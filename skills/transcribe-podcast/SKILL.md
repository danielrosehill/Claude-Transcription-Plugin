---
name: transcribe-podcast
description: Transcribe a podcast episode and produce two outputs in one pass — (1) the raw API transcript exactly as the provider returned it, and (2) a podcast-formatted reading version with filler words removed, section headers added, and speaker labels preserved. Use whenever the user provides a podcast audio file or says "transcribe this podcast".
---

# Transcribe Podcast (raw + reading version)

Single skill that yields **both** outputs the user wants every time for a podcast:

1. **Raw transcript** — exactly what the transcription API returned, no editing. Source of truth.
2. **Podcast reading version** — same content, formatted for human reading: filler words removed, false starts cleaned, paragraph breaks at natural topic shifts, section headers (`## Topic`) added, speaker labels preserved (`**Daniel:** ...`).

Both files are written to disk. The reading version is what gets pasted into blog posts, show notes, or summaries; the raw version stays for verification.

## Provider order

Per plugin CLAUDE.md: **AssemblyAI first, Gemini MCP as fallback.**

1. Try `transcribe-assemblyai` (gives diarization + timestamps for free).
2. If AssemblyAI is unavailable or fails, fall back to `transcribe-gemini-raw`.

Do not ask the user which provider — just use AssemblyAI unless they specified one.

## Procedure

1. **Transcribe via AssemblyAI** (`speaker_labels: true`, `punctuate: true`, `format_text: true`).
   - Save raw output to `<source_stem>.raw.md` — speaker-labelled prose, no timestamps in this file (timestamps are kept in the sidecar JSON for downstream skills). One paragraph per speaker turn.
   - Also save `<source_stem>.assemblyai.json` (full API payload) for downstream tools.
2. **Produce the reading version** at `<source_stem>.podcast.md`:
   - Remove filler words: `um`, `uh`, `er`, `ah`, `you know` (filler use), `like` (filler use), `I mean` (filler use), `sort of`, `kind of` (filler use), `right?` (tic).
   - Remove false starts and immediate self-repetitions.
   - **Do not paraphrase, summarize, or reorder.** Preserve the speaker's meaning, vocabulary, and tone. This is a cleaned transcript, not a rewrite.
   - Preserve speaker labels: `**Daniel:**`, `**Guest:**`, etc. If `<source_stem>_speakers.json` exists, use those names; otherwise use AssemblyAI's `A`/`B`/`C` mapped to `Speaker A` / `Speaker B` etc., and ask the user to confirm names if it's a 2+ speaker episode.
   - Add `## ` section headers at natural topic transitions. Aim for one header every 3–8 minutes of content. Headers should be short, descriptive, sentence-case (`## Why diarization matters`, not `## Diarization`). Do not invent topics — derive headers from what's actually said.
   - Add a single `# <Episode Title>` at the top if the user supplied one (or it's inferable from the source filename); otherwise skip the H1.
3. **Report** both file paths to the user, plus a one-line word-count and duration summary.

## Output files

| File | Contents |
|------|----------|
| `<stem>.raw.md` | Raw transcript, speaker labels, no editing |
| `<stem>.assemblyai.json` | Full AssemblyAI JSON (timestamps, confidences) |
| `<stem>.podcast.md` | Reading version — fillers removed, headers added |

## When to use

- User provides podcast audio and asks for a transcript.
- User says "transcribe this podcast", "transcribe this episode", "give me a podcast transcript".
- User wants both a verifiable raw transcript and a clean reading version (the common case for show-notes / blog repurposing).

## When NOT to use

- Single-speaker memo, voice note, or dictation → use `transcribe-assemblyai` or `transcribe-gemini-cleaned` directly.
- Meeting / interview where the user only wants timestamps → `transcribe-assemblyai`.
- User explicitly wants only one output → use the underlying single-output skill.

## Notes

- AssemblyAI cost is ~$0.37/hr with speaker labels. Flag if the audio is >4 hours.
- The reading version is derived from the raw transcript, not re-transcribed — one API call total.
- If section-header inference is unreliable on a particular episode (e.g. very meandering conversation), produce the cleaned prose with paragraph breaks only and tell the user headers were skipped.
