---
name: structure-transcript
description: Add section headers, logical groupings, and paragraph breaks to a cleaned transcript, while preserving the speaker's wording. Use when the user asks to structure a transcript, add headers, organize by topic, or make a transcript readable without rewriting it.
---

# Structure transcript

Reorganize a cleaned transcript into a readable document with headers and sections — without paraphrasing.

## Input

Preferably `<stem>.cleaned.md`. Falls back to raw if cleaned is unavailable (warn user that fillers will remain).

## What to do

1. Identify topic shifts and thematic groupings.
2. Insert markdown headers (`##`, `###`) naming each section descriptively.
3. Merge fragmented paragraphs on the same topic.
4. Split overly long paragraphs at natural breaks.
5. Preserve every content word.

## What NOT to do

- Do not paraphrase or reword
- Do not drop content
- Do not add information the speaker didn't say
- Do not insert editorial commentary

## Output convention

`<source_stem>.structured.md`

## Example transformation

Before:
> So we started the project in January and the first thing we did was set up the infrastructure. That took about three weeks. Then we moved on to the API layer which was actually the hardest part because we had to integrate with the legacy system.

After:
> ## Project Timeline
>
> ### Infrastructure Setup (January, ~3 weeks)
>
> So we started the project in January and the first thing we did was set up the infrastructure. That took about three weeks.
>
> ### API Layer
>
> Then we moved on to the API layer which was actually the hardest part because we had to integrate with the legacy system.
