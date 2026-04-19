---
name: combine-versions
description: Concatenate multiple transcript variants (raw, cleaned, structured, blog, summary, notes) into a single combined document — markdown with variant headers, or Typst-rendered PDF with page numbers and variant name in the footer. Use when the user asks to combine versions, merge transcript variants, or produce a single multi-version document.
---

# Combine transcript versions

Merge multiple variants of the same transcript into one document so the user can compare or archive them together.

## Inputs

Detect available variants for a given source stem by checking for:
- `<stem>.raw.txt`
- `<stem>.cleaned.md`
- `<stem>.structured.md`
- `<stem>.blog.md`
- `<stem>.summary.md`
- `<stem>.notes.md`

User may specify which to include; default is "all available".

## Output formats

### Markdown (default)

`<stem>.combined.md` — each variant under an H1 header with metadata:

```markdown
# Transcript: <stem>

_Generated: YYYY-MM-DD_
_Source: <source audio filename>_

---

# Variant: Raw transcript

_Source file: <stem>.raw.txt_
_Produced by: transcribe-gemini-raw_

<content>

---

# Variant: Cleaned

_Source file: <stem>.cleaned.md_
_Produced by: clean-transcript_

<content>

---

# Variant: Structured

<content>

...
```

### Typst → PDF

`<stem>.combined.pdf` — styled PDF via Typst.

Typst template:
```typst
#set document(title: "Transcript: <stem>")
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2cm),
  header: [#h(1fr) <stem>],
  footer: context [
    #h(1fr)
    Variant: #variant-name #h(2em) Page #counter(page).display()
  ],
)
#set text(font: "IBM Plex Sans", size: 10pt)
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #set text(size: 16pt, weight: "bold")
  #it
]

// For each variant:
#let variant-name = "Raw transcript"
= Raw transcript

<content converted from md to typst>

#let variant-name = "Cleaned"
= Cleaned

...
```

**Note:** the `variant-name` state needs to be tracked per-section so the footer updates correctly — use Typst's `state()` or per-page context resolution.

Render:
```bash
typst compile <stem>.combined.typ <stem>.combined.pdf
```

Use IBM Plex Sans (per Daniel's typst-document-generator convention). If not installed, fall back to the default Typst font.

## Markdown → Typst conversion

For the PDF path, convert markdown content to Typst:
- `# H1` → `= H1` (but we're already using `=` for variant headers; demote markdown H1 within content to `==`)
- `## H2` → `==`
- `**bold**` → `*bold*`
- `*italic*` → `_italic_`
- `- list` → `- list` (Typst supports markdown-like lists)
- Code blocks → `raw()` blocks

For complex markdown, consider piping through `pandoc -t typst` if available.

## Parameters

- `--variants raw,cleaned,structured` — pick subset
- `--format md|pdf|both` — output format(s)
- `--output <path>` — custom path
