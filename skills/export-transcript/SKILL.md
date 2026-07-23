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

When attaching the transcript file, the same staging rule as Drive applies — the GWS MCP runs on `residencehome` and can't read workstation paths. Stage via MinIO (`python3 ~/.claude/lib/minio-stage.py …`) and pass the presigned URL as the attachment's `sourceUrl`. The send-* email skills cover this.

### Google Drive

Use the `gws-personal` MCP. **The GWS MCP runs on `residencehome`** — it cannot read workstation paths like `/home/daniel/...`. The canonical upload path is **MinIO staging + `sourceUrl`**:

1. Stage the transcript via MinIO to get a presigned URL:
   ```bash
   python3 ~/.claude/lib/minio-stage.py /path/to/transcript.md --expires 3600
   # → {"url":"http://10.0.0.2:9100/mcp-staging/<uuid>/transcript.md?X-Amz-...",...}
   ```
2. `create_folder` if the user specified a new folder name (or reuse an existing one via `search`).
3. Call `mcp__gateway__google-workspace-personal__create_drive_file` with `sourceUrl: <presigned URL>` and `parents: [<folder-id>]`. **Do not** pass a workstation `file_path`/`sourcePath` — that param is residencehome-local only.
4. If the transcript is markdown and the user wants it editable, use `create_google_doc` with the content inline instead.
5. Optionally `share_file` if the user wants a shareable link.

Report back the Drive `webViewLink`.

**Do NOT** reach for `rclone`, `scp`, `gcloud`, `gdrive`, direct Drive API `curl`, or any other workaround. MinIO staging + `sourceUrl` is the only supported route from this workstation; the staging bucket (`mcp-staging` on `10.0.0.2:9100`) self-cleans after 1 day.


### Clipboard

Copy file contents to clipboard: `wl-copy < FILE` (Wayland) or `xclip -selection clipboard < FILE` (X11). Detect which is available.

For PDF or binary, warn that clipboard export isn't meaningful and suggest email/Drive instead.

## Accepted inputs

Any file produced by this plugin: `.raw.txt`, `.cleaned.md`, `.structured.md`, `.blog.md`, `.summary.md`, `.notes.md`, `.combined.md`, `.combined.pdf`.

Also accept arbitrary paths the user supplies.

## Multiple destinations

Allow chaining: "email it and upload to Drive" should do both.
