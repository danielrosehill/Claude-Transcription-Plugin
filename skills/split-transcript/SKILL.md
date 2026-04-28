---
name: split-transcript
description: Segment a mixed-intent transcript into separate files by category — prompts, context, action items, background, decisions. Useful when the user has dictated a dev brief, code review, or planning session that interleaves multiple kinds of content. Use when the user says "split this transcript", "separate the prompts from the context", or hands over a transcript that is clearly multi-purpose.
---

# Split transcript by intent

Take a transcript that mixes several kinds of content — instructions, background, decisions, todos — and emit one file per category. The user can then route each piece to its appropriate destination (prompts to a dev tool, action items to Todoist, context to the project's context folder, etc.).

## When to use

- Dictated dev brief: "Here's what I want built [prompt], the system currently does X [context], we need to handle case Y [requirement], and remind me to email Bob tomorrow [action item]"
- Voice-dictated code review mixing observations and asks
- Planning session that produced both decisions and follow-ups
- Any transcript where the user explicitly says "split this up"

## Categories

| Category | Filename | What goes in |
|---|---|---|
| Prompts / asks | `prompts.md` | Direct instructions to an AI or developer — "build me X", "refactor Y", "write a script that …" |
| Context / background | `context.md` | Existing-state explanations, system descriptions, "the way it currently works is…" |
| Action items | `action-items.md` | Personal todos, reminders, things to follow up on. Format as a checklist. |
| Decisions | `decisions.md` | "We're going with X because Y" — durable choices worth recording |
| Questions / open items | `open-questions.md` | Unresolved questions raised but not answered |
| Notes / asides | `notes.md` | Tangents and observations that don't fit the above but are worth keeping |

Skip any category that has no content. Don't create empty files.

## Output location

Create a `split/` subdir alongside the source transcript:

```
transcripts/recording.structured.md       (source)
transcripts/recording.split/
  ├── prompts.md
  ├── context.md
  ├── action-items.md
  └── notes.md
```

If the user is working inside a project that already has `prompts/`, `context/`, `actions/` at top level, route into those instead and prefix each file with the source stem (e.g. `context/recording.context.md`).

## Format

Each output file gets a small header tying it back to the source:

```markdown
# Prompts from recording.structured.md
_Split 2026-04-28_

---

[content]
```

For `action-items.md`, render as a checklist:
```markdown
- [ ] Email Bob about the staging deploy
- [ ] Check whether the new MCP env vars are loaded
- [ ] Test the silence threshold on the long memo
```

Preserve the user's wording — don't paraphrase. Splitting is reorganisation, not summarisation.

## Boundary heuristics

The hard part of splitting is deciding where one category ends and another begins. Cues:

- **Discourse markers**: "so first, ...", "then, ...", "also, ...", "remind me to ..."
- **Tense / mood**: imperative ("build X") → prompt; descriptive ("the system does Y") → context; conditional ("if we do X") → open question or decision
- **Pronoun shifts**: "you should" / "I want you to" → prompt; "we" / "the system" → context
- **Topical shifts** marked by short pauses (in voice memos these often produce sentence-final punctuation in the structured stage)

When uncertain, prefer over-inclusion in `notes.md` rather than guessing. The user can re-route manually.

## What not to do

- Don't drop content. Every sentence from the source should land somewhere.
- Don't merge multiple speakers' turns if the source has speaker labels — preserve them in each split file.
- Don't generate new content. If a category has only one ambiguous fragment, include it as-is rather than padding.
- Don't overwrite a previous split if `<stem>.split/` already exists — suffix `.split-v2/`, `.split-v3/`.

## Followups (handoffs)

After splitting, offer:
- Pipe `prompts.md` into a dev tool / new Claude session
- Pipe `action-items.md` into Todoist (when `schedule-manager` integration lands)
- Pipe `context.md` into `extract-context` for further mining
- Render `decisions.md` to PDF for a meeting record
