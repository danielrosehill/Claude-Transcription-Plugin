---
name: clean-transcript
description: Remove filler words, false starts, and immediate repetitions from an existing transcript file. Preserves meaning, tone, and structure. Use when the user asks to clean a transcript, remove fillers, or tidy up a raw transcription.
---

# Clean transcript

Post-processing pass on an existing transcript to strip disfluencies.

## Input

A transcript file, typically `<stem>.raw.txt` produced by `transcribe-gemini-raw` or `transcribe-whisper-local`.

## What to remove

- Filler words: `um`, `uh`, `er`, `ah`, `like` (as filler), `you know` (as filler), `I mean` (as filler), `sort of`, `kind of` (as hedges only)
- Immediate repetitions: "I-I-I think", "the the"
- Obvious false starts: "I was going to— I wanted to say"
- Stutters and single-word restarts

## What to preserve

- All content words and real intent
- Speaker's phrasing and vocabulary
- Paragraph breaks and any speaker labels
- Tone, register, and idiom
- Lists, enumerations, technical terms

## What NOT to do

- Do not summarize
- Do not reorder sentences
- Do not add headers
- Do not paraphrase
- Do not correct grammar unless the raw transcript has a clear transcription error

## Output convention

`<source_stem>.cleaned.md` in the same directory as the input transcript.

## Implementation

This is an LLM task — read the input file, apply the rules above, write the cleaned version. No external tools needed.
