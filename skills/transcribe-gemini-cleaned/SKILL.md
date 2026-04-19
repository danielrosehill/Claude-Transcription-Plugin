---
name: transcribe-gemini-cleaned
description: Transcribe audio via Gemini with filler words and pause-words removed at transcription time. Produces a lightly cleaned transcript in one pass. Use when the user asks for a cleaned transcript, filler-free transcription, or a readable first-pass transcript via Gemini.
---

# Transcribe (Gemini, cleaned)

Single-pass transcription that drops fillers while preserving meaning.

## How

Call the `gemini-transcription` MCP tool with a cleaned preset or custom system prompt.

## System prompt

> Transcribe this audio. Remove filler words (um, uh, er, ah, you know, like when used as a filler, I mean as a filler). Remove false starts and immediate repetitions. Preserve the speaker's meaning, tone, and vocabulary. Do NOT paraphrase, summarize, or reorder. Do NOT add headers or structure. Output plain running prose, paragraph breaks only at natural topic shifts.

## Output convention

Save to `<source_stem>.cleaned.md`.

## When to use instead of `clean-transcript`

- Fresh transcription → use this (one API call instead of two).
- Existing raw transcript → use the `clean-transcript` post-processing skill.
