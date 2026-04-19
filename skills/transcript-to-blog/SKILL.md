---
name: transcript-to-blog
description: Rewrite a transcript into a publishable blog post — narrative flow, tightened prose, engaging title, and intro/outro. Use when the user asks to turn a transcript into a blog post, convert recording to article, or draft a post from an interview.
---

# Transcript → blog post

Convert a transcript into a first-person blog post suitable for publication.

## Input

Preferably `<stem>.structured.md` or `<stem>.cleaned.md`.

## What the output should include

- **Title** — specific and attention-grabbing, not generic
- **Intro (2-4 sentences)** — hook + what the post is about
- **Body** — tightened prose preserving the speaker's voice and key points, with descriptive H2/H3 headers
- **Conclusion** — short wrap-up or call to action if appropriate

## Style

- Match the speaker's register (formal vs conversational) — infer from the transcript
- Keep the first-person POV if the transcript is first-person
- Tighten run-on sentences, cut redundancy
- Keep technical terms and specific examples
- Don't invent stories, numbers, or quotes

## What to drop

- Digressions that don't serve the post's thesis
- Meta-talk ("let me think about this", "as I was saying")
- Speaker labels (if present)

## Output convention

`<source_stem>.blog.md`

Include YAML frontmatter if useful:
```yaml
---
title: "..."
date: YYYY-MM-DD
tags: []
---
```
