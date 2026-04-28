---
name: extract-context
description: Mine a transcript for durable personal context — facts about the speaker (location, role, projects, preferences, relationships, ongoing work) — and write them to a context file for later reuse. De-duplicates against existing context so the same facts aren't re-extracted on every memo. Use when the user wants to build a knowledge base from voice memos, or asks to "pull out context from this".
---

# Extract context from transcript

Read a transcript and pull out *durable* facts about the speaker — things that would be useful to know in future conversations or for downstream agents. Volatile content (today's plan, this week's tasks, transient frustrations) is **not** context — skip it.

## What counts as context

| Yes | No |
|---|---|
| "I live in Jerusalem" | "I'm running late today" |
| "I work for DSR Holdings" | "This morning I had coffee" |
| "My business email is daniel@dsrholdings.cloud" | "I just sent that email" |
| "I prefer tabs over spaces" | "I'm annoyed at this bug" |
| "I'm working on the Claude-Transcription-Plugin repo" | "I committed to that branch" |
| "My partner's name is …" | "She called me earlier" |

Rule of thumb: if the fact would still be true in a month, it's context. If it'll be stale by tomorrow, it's not.

## Output location

Default: `context/extracted-YYYY-MM-DD.md` alongside the transcript.

If a project-level context folder already exists upstream (e.g. the user is working inside a repo with `context/` already), write there instead.

## Output format

```markdown
# Context extracted from <source-transcript>
_Extracted 2026-04-28 from recording.structured.md_

## Identity
- Name: Daniel Rosehill
- Location: Jerusalem, Israel

## Work
- Runs DSR Holdings (dsrholdings.cloud)
- Currently building: Claude-Transcription-Plugin

## Preferences
- Prefers Train-Case for repo names
- Voice-types most input

## Open initiatives
- Sprint 2026-04 in Claude-Transcription-Plugin
```

Group by category (Identity / Work / Preferences / Relationships / Open initiatives / Other). Skip categories with no entries.

## De-duplication

Before writing, scan existing `context/extracted-*.md` files (and optionally `~/.claude/projects/-home-daniel/memory/` if asked). For each candidate fact:

1. **Already recorded, identical** → skip silently
2. **Already recorded, contradicting** → flag in output under `## Updates / contradictions` so the user can adjudicate (don't auto-overwrite)
3. **New** → include

The output file should only contain *new or contradicting* facts, not a full restatement of every known fact. This keeps each extraction lightweight and reviewable.

If nothing new was found, write a one-line stub:
```
_No new context extracted from <source>. All facts already on file._
```

## Optional: write to auto-memory

If the user has `~/.claude/projects/-home-daniel/memory/` (Daniel does), offer to also append durable facts there:

```
Found 3 new facts. Save to:
  [x] context/extracted-2026-04-28.md
  [ ] ~/.claude/projects/-home-daniel/memory/  (auto-memory, persists across sessions)
```

Default off — only write to memory when the user explicitly opts in. Auto-memory has its own structure (one fact per file, frontmatter, MEMORY.md index) and shouldn't be polluted casually.

## What not to do

- Don't paraphrase or interpret. If the user said "I live in Jerusalem", record that, not "user is based in Israel"
- Don't extract from rhetorical/hypothetical statements ("if I lived in Tel Aviv" → not context)
- Don't extract third-party facts unless they're durable relationships ("my brother lives in London" → yes; "John from work said X" → no)
- Never write secrets / credentials to a context file even if the user mentions them in the transcript. Flag them and ask separately.
