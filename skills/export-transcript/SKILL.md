---
name: export-transcript
description: Export a transcript (or any pipeline output) by emailing it, uploading to Google Drive, or copying to clipboard. Use when the user asks to send, email, upload, save to Drive, or copy a transcript.
---

# Export transcript

Send a transcript file (or post-processed variant) to a destination.

## Destinations

### Email

Use the `email-skills` skill set (`send-personal-email` or `send-business-email`).

Prompt user for:
- To: address
- Subject (default: file's H1 heading or stem)
- Body: either inline content or short cover note with the transcript as attachment

### Google Drive

Use the `gws-personal` MCP:
1. `create_folder` if user specifies a folder name (or reuse an existing one via `search`).
2. `upload_file` with the local file path and target folder ID.
3. If transcript is markdown and user wants it editable, use `create_google_doc` with the content instead.
4. Optionally `share_file` if the user wants a link.

Report back the Drive URL.

### Clipboard

Copy file contents to clipboard: `wl-copy < FILE` (Wayland) or `xclip -selection clipboard < FILE` (X11). Detect which is available.

For PDF or binary, warn that clipboard export isn't meaningful and suggest email/Drive instead.

## Accepted inputs

Any file produced by this plugin: `.raw.txt`, `.cleaned.md`, `.structured.md`, `.blog.md`, `.summary.md`, `.notes.md`, `.combined.md`, `.combined.pdf`.

Also accept arbitrary paths the user supplies.

## Multiple destinations

Allow chaining: "email it and upload to Drive" should do both.
