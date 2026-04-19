---
name: transcript-to-notes
description: Convert a transcript into structured meeting or study notes with headers, bullets, and callouts. Use when the user asks for notes from a recording, study notes, meeting minutes, or structured notes from a transcript.
---

# Transcript → structured notes

Convert a transcript into skimmable, reference-quality notes.

## Output shape

```markdown
# Notes: <inferred title>

**Date:** <if inferable, else omit>
**Participants:** <if diarized and labeled, else omit>

## Topics covered

### <Topic 1>

- Point
- Point
- Sub-point
  - Detail

### <Topic 2>
...

## Action items

- [ ] <item> — <owner if stated>

## Questions raised

- <question>

## References mentioned

- <book / URL / person / tool>
```

## Rules

- Hierarchical bullets, not prose.
- Capture specifics (names, numbers, URLs, timeframes).
- Preserve terminology exactly.
- Omit sections that don't apply.
- Notes should be readable standalone — without the original recording.

## Output convention

`<source_stem>.notes.md`
