---
name: iterative-refine
description: Stepwise transcript refinement that never overwrites prior stages. Stage 1 removes filler words and adds paragraphs; stage 2 adds subheadings; stage 3 asks the user what's next (notes, blog, summary, PDF, translation, or stop). Use when the user hands over a raw transcript and wants it progressively improved with all intermediate versions preserved.
---

# Iterative refinement

Take a raw transcript through a controlled, reversible refinement pipeline. Every stage writes a new file with a distinct suffix — **never overwrite a prior stage**.

## The chain

```
recording.raw.md         (input — from transcribe-* skill)
  └─► recording.cleaned.md     (stage 1, automatic)
        └─► recording.structured.md   (stage 2, automatic)
              └─► (stage 3 — ask user)
```

All files live in `transcripts/` (create if missing) alongside the source.

## Stage 1 — clean (automatic)

**Input:** `<stem>.raw.md`
**Output:** `<stem>.cleaned.md`

Operations:
- Remove filler words: "um", "uh", "you know", "like" (only as filler), "kind of", "sort of", "I mean", "basically", "actually", false starts ("the — the"), immediate self-corrections
- Fix obvious mistranscriptions where context makes the intended word unambiguous
- Add paragraph breaks at natural topic shifts (every 3–6 sentences for solo dictation)
- Preserve all substantive content — do not summarise or rephrase

**Do not:**
- Reword sentences for "better flow"
- Reorder content
- Drop digressions or tangents (those are the user's thoughts; preserve them)

## Stage 2 — structure (automatic)

**Input:** `<stem>.cleaned.md`
**Output:** `<stem>.structured.md`

Operations:
- Add `##` subheadings at logical section breaks
- Group related paragraphs under each heading
- Add a 1-line `_Topic: …_` italic header at the very top capturing the gist
- Optional: add a brief table-of-contents block if there are 5+ sections

**Do not:**
- Modify the prose itself (that was stage 1's job)
- Invent content for a heading — if a section is short, leave it short

## Stage 3 — ask (interactive)

After stage 2, **stop and ask the user** what's next. Present a menu:

```
Stage 2 complete: transcripts/recording.structured.md

What next?
  1. Convert to meeting notes / study notes  (transcript-to-notes)
  2. Convert to blog post                     (transcript-to-blog)
  3. Generate executive summary               (transcript-to-summary)
  4. Render to PDF                            (transcript-to-pdf)
  5. Translate to another language            (translate-transcript — when built)
  6. Extract personal context                 (extract-context — when built)
  7. Split into prompts/context/actions       (split-transcript — when built)
  8. Stop here

Pick one (or several), or describe what you want.
```

Each option invokes the corresponding skill against `<stem>.structured.md` (or whichever stage is most appropriate). Outputs follow that skill's own naming — they don't overwrite the structured version.

## Naming and folder rules

- Suffix-based: `.raw.md`, `.cleaned.md`, `.structured.md`, then per-skill suffixes downstream
- All intermediate transcripts in `transcripts/`
- If the source isn't named `*.raw.md`, treat it as raw and rename a copy (don't move the original) before starting
- If `<stem>.cleaned.md` already exists, suffix `.v2.md`, `.v3.md` and ask the user whether to start fresh or continue from the existing cleaned version

## When to skip stages

If the user explicitly says "just clean it, don't add headings," run stage 1 only and stop. If they say "give me a blog post from this raw transcript," run stages 1+2, then jump to `transcript-to-blog` without prompting.

## Why this exists

The trap this skill avoids: an AI agent doing all transformations in one pass and overwriting the source. Voice memos contain raw thinking that's valuable to refer back to — preserving each stage means the user can always roll back, diff between versions, or re-fork from any point.
