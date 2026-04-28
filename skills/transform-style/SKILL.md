---
name: transform-style
description: Apply a stylistic / formatting transformation to a transcript using a named prompt from the user's Text-Transformation-Prompt-Library (206 transformations covering blog outlines, briefs, business correspondence, analysis documents, meeting notes, and more). Use when the user asks to "convert this to <style>", "format like a <type>", or names a specific transformation. Fetches the catalog on demand and caches it; never commits the prompts into this plugin.
---

# Transform style

Take a transcript (any stage) and reformat it according to a named transformation from the user's prompt library at https://github.com/danielrosehill/Text-Transformation-Prompt-Library.

## Source of transformations

Authoritative URL:
```
https://raw.githubusercontent.com/danielrosehill/Text-Transformation-Prompt-Library/main/prompts.json
```

Schema (per entry):
```json
{
  "name": "Analysis Document",
  "description": "",
  "system_prompt_text": "Your task is to take the text provided by the user, …",
  "expected_output_format": "",
  "delivers_structured_output": "",
  "converted_at": "2025-05-28"
}
```

206 entries as of 2026-04. The catalog evolves upstream — never commit a snapshot into this plugin.

## Cache

```
~/.cache/claude-transcription/transformations/prompts.json
~/.cache/claude-transcription/transformations/.last-refresh   (timestamp)
```

Refresh policy: fetch on first use, then re-fetch if cache is older than 7 days **or** the user passes `--refresh`. Fall back to cached version silently if upstream is unreachable.

## Picking a transformation

Three input modes:

1. **Exact name**: `transform-style "Analysis Document" <transcript>` → match `name` case-insensitively
2. **Fuzzy / partial**: `transform-style "blog outline" <transcript>` → fuzzy-match against `name` and `description`; if multiple hits, present the top 5 and ask
3. **No name given**: list categories (derived from name patterns) and offer browse:
   ```
   What kind of transformation? e.g.:
     - Blog / writing:       "blog outline", "analysis document", "newsletter"
     - Business:             "business correspondence", "brief", "meeting summary"
     - Personal / notes:     "diary entry", "journal", "reflection"
     - Structural:           "basic text fixes", "bullet points", "executive summary"
   Or pass --list to dump all 206.
   ```

## Applying the transformation

Send Claude (current session) two parts:
- `system`: the entry's `system_prompt_text` (verbatim)
- `user`: the transcript content

Don't add wrapping text or modify the system prompt. The library's prompts are the spec.

If `delivers_structured_output` is truthy and indicates a specific format (JSON, table, etc.), respect it in the output filename suffix.

## Output convention

```
<stem>.<transform-slug>.md
```

Slug = `name` lowercased, spaces → hyphens, non-alphanumerics stripped.

Examples:
- `recording.structured.md` + "Analysis Document" → `recording.structured.analysis-document.md`
- `recording.cleaned.md` + "Blog Outline" → `recording.cleaned.blog-outline.md`

If the transformation produces JSON, suffix `.json` instead of `.md`.

Outputs go in `transcripts/` (same folder as source).

## Header

Each output begins with:

```markdown
_Transformed from <source-filename> via "<transformation-name>" — 2026-04-28_
```

So provenance is traceable.

## Flags

- `--refresh` — force re-fetch of the prompt catalog
- `--list` — dump all 206 transformation names (one per line) and exit
- `--show <name>` — print the full prompt for a transformation without applying it (for inspection)
- `--out-dir <path>` — override default `transcripts/`

## Composing with other skills

This skill is terminal — its output is what the user wanted. But it composes naturally:

- Run `iterative-refine` first (to get from raw → structured), then `transform-style` for the stylistic conversion. Most transformation prompts assume cleanish input.
- Run `translate-transcript` after `transform-style` if the output should be in a different language than the source. (Translating then transforming usually works worse — the transformation prompts are written in English and assume English input.)

## What not to do

- Don't bundle / commit the prompts.json into this repo. It's the user's separate repo with its own update cadence.
- Don't modify `system_prompt_text` in any way — even small tweaks defeat the point of having a curated library.
- Don't apply multiple transformations in one pass. Chain them as separate invocations so each intermediate is preserved.
- Don't overwrite the source. Always emit a new file with the transform-slug suffix.

## Failure modes

- **Upstream unreachable, no cache**: bail with a clear error pointing the user to the repo URL
- **Name matches multiple entries**: present top 5, ask user to pick
- **Name matches nothing**: suggest the 3 closest by string distance
- **Transcript is huge (>50k tokens)**: warn before submitting; some transformations don't degrade well at length and a chunked approach may be needed (the library's prompts generally don't account for chunking)
