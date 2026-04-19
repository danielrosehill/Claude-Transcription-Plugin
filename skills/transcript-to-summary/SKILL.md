---
name: transcript-to-summary
description: Produce an executive summary and bullet-point highlights from a transcript. Use when the user asks for a summary, TL;DR, exec summary, key takeaways, or highlights of a recording.
---

# Transcript → summary

Produce a concise summary of a transcript.

## Output shape

```markdown
# Summary: <inferred title>

## Executive summary

<2-4 sentence overview of what was discussed and the main thrust>

## Key points

- <bullet>
- <bullet>
- ...

## Decisions / action items

<only if applicable — meetings, planning calls>
- <bullet>

## Open questions

<only if raised in the transcript>
- <bullet>
```

## Rules

- Stay faithful: every claim must be supported by the transcript.
- Omit sections (decisions, open questions) if they don't apply.
- 5-10 bullets for key points — more means it's a bad summary.
- Use the speaker's terminology.

## Output convention

`<source_stem>.summary.md`
