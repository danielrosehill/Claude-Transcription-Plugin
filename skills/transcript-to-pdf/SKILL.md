---
name: transcript-to-pdf
description: Render a single transcript to a PDF using Typst, with the source file's modification timestamp and page numbers in the footer. Use when the user asks to "make a PDF of this transcript", "render to PDF", "transcript as PDF", or otherwise wants a printable single-version document. For multi-version (raw + cleaned + structured + blog) bundles, use `combine-versions` instead.
---

# Transcript → PDF

Take one transcript file and render a clean PDF via Typst. Footer carries the original transcript timestamp on the left and page numbers on the right.

## Inputs

- **Transcript path** (markdown or plain text). Required.
- **Title** (optional) — defaults to the filename stem.
- **Timestamp** (optional) — defaults to the transcript file's `mtime` formatted as `YYYY-MM-DD HH:MM`.

## Output

`<stem>.pdf` written next to the input file (or to `--out` if the user supplies one).

## Typst template

Write a temporary `.typ` file with:

```typst
#set document(title: "<title>")
#set page(
  paper: "a4",
  margin: (x: 2cm, y: 2.2cm),
  footer: context [
    #set text(size: 9pt, fill: gray)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [<timestamp>],
      [Page #counter(page).display() of #counter(page).final().first()],
    )
  ],
)
#set text(font: "IBM Plex Sans", size: 11pt)
#set par(justify: true, leading: 0.7em)

= <title>

<body — markdown converted to Typst>
```

Substitute `<title>`, `<timestamp>`, and `<body>` before compiling. Font: IBM Plex Sans if available, otherwise Typst default.

## Markdown → Typst conversion (minimal)

| Markdown | Typst |
|---|---|
| `# H1` | `= H1` |
| `## H2` | `== H2` |
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `` `code` `` | `` `code` `` |
| `- item` | `- item` |
| Blank line | Blank line (paragraph break) |

Plain prose passes through unchanged. For anything richer (tables, code blocks, links), do a per-element pass.

## Render

```bash
typst compile <stem>.typ <stem>.pdf
```

Delete the intermediate `.typ` after a successful compile unless the user asks to keep it.

## Edge cases

- **No `typst` binary**: instruct the user to install via `cargo install --locked typst-cli` or their distro's package manager. Do not silently fall back to a different format.
- **Very long transcripts** (50+ pages): Typst handles this fine; just confirm with the user before rendering anything over ~200 pages so they can opt into a smaller font / tighter leading.
- **Diarized transcript** (speaker-prefixed lines like `Speaker 1: ...`): preserve as-is; the bold/italic conversion already handles the `**Speaker 1:**` form many transcribers emit.
