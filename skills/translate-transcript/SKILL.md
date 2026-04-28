---
name: translate-transcript
description: Translate a transcript from its source language into a target language while preserving structure (paragraphs, subheadings, speaker labels, timestamps). Use when the user wants a transcript in another language — for sharing with someone who doesn't speak the source language, for publishing in a target market, or for review.
---

# Translate transcript

Translate a transcript file end-to-end while preserving every structural element. Source file is never modified — output is a new file with a language-suffix.

## Inputs

- A transcript file (any stage: `.raw.md`, `.cleaned.md`, `.structured.md`, etc.)
- Target language (ISO 639-1 code preferred — `en`, `he`, `es`, `fr`, `de`, `ar`, etc.; full names also accepted)
- Source language is auto-detected unless overridden

## Output convention

`<stem>.<source-lang>-to-<target-lang>.md`

Examples:
- `recording.structured.md` → `recording.structured.he-to-en.md`
- `interview.cleaned.md` → `interview.cleaned.en-to-es.md`

If the source filename already encodes a stage (`.cleaned.md`), keep that stage suffix; the language suffix goes after.

## Backend choice

| Backend | When |
|---|---|
| Claude (current session) | Default — high quality, preserves nuance, no extra config |
| Gemini via OpenRouter | When transcript is very long (cheaper at scale) and `OPENROUTER_API_KEY` is set |
| External MT API (DeepL, Google Translate) | Only on explicit request — generally lower quality for nuanced/idiomatic content |

## Preserve, don't translate

These elements pass through unchanged:

- Markdown structure: headings, lists, blockquotes, code blocks, tables
- Timestamps: `[00:12:34]`
- Speaker labels: `**Alice:**`
- Inline code, URLs, file paths, technical identifiers
- Proper nouns (names, brands, places) — translate only if there's an established target-language form (e.g. "Jerusalem" / "ירושלים")

The italic source-attribution header stays in the source language and gains a translation note:

```markdown
_Topic: …_
_Translated 2026-04-28: he → en, Claude_
```

## Translation guidance

- **Register**: match the source's register. Casual voice memo → casual translation. Formal meeting transcript → formal.
- **Idiom**: translate idioms by meaning, not literally. Hebrew "על הפנים" → "terrible" / "awful", not "on the face".
- **Hedging and filler**: if the input is a `.cleaned.md` (filler already removed), don't add filler back.
- **Cultural references**: keep the reference, but add a brief parenthetical gloss only if the target audience genuinely won't recognise it.
- **Code-switched content**: if the speaker switched languages mid-sentence (common in Hebrew-English mixed memos), translate the whole result into the target language rather than preserving the switch.

## Long inputs

For transcripts > ~30 minutes / >10k words:
- Translate in chunks of ~2k words, overlapping by one paragraph for continuity
- Re-stitch chunks, removing the overlap from the second chunk
- Pass a glossary of recurring proper nouns / technical terms to each chunk for consistency

## Output report

```
Source:       transcripts/recording.structured.md (he, 4,820 words)
Target:       transcripts/recording.structured.he-to-en.md (en, 4,610 words)
Backend:      Claude
Glossary:     12 proper nouns held consistent
```

## What not to do

- Don't summarise. Translation preserves length and content.
- Don't "improve" the source. If the speaker rambled, the translation rambles.
- Don't drop or merge speaker turns.
- Don't translate file paths, command names, or code — only natural-language content.
