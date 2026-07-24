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

When attaching the transcript file, the same staging rule as Drive applies — the GWS MCP runs on `residencehome` and can't read workstation paths. Stage via the minio MCP presign flow (below) and pass the presigned GET URL as the attachment's `url`. The send-* email skills cover this.

### Google Drive

Use the `gws-personal` MCP. **The GWS MCP runs on `residencehome`** — it cannot read workstation paths like `/home/daniel/...`. The canonical upload path is **MinIO staging + `fileUrl`**:

1. Stage the transcript via the `minio` MCP: presign a PUT URL
   (`minio__presign_url(bucket="personal-transient", key="staging/transcript.md", method="put")`),
   upload with `curl -sSf -X PUT -T /path/to/transcript.md "<put-url>"`,
   then presign a GET URL for the same key (`method="get"`).
2. `create_folder` if the user specified a new folder name (or reuse an existing one via `search`).
3. Call `mcp__gateway__google-workspace-personal__create_drive_file` with `fileUrl: <presigned URL>` and `folder_id: <folder-id>`. **Do not** pass a workstation `file_path`/`sourcePath` — that param is residencehome-local only.
4. If the transcript is markdown and the user wants it editable, use `create_google_doc` with the content inline instead.
5. Optionally `share_file` if the user wants a shareable link.

Report back the Drive `webViewLink`.

**Do NOT** reach for `rclone`, `scp`, `gcloud`, `gdrive`, direct Drive API `curl`, or any other workaround. MinIO staging + `fileUrl` is the only supported route from this workstation; the `*-transient` staging buckets at `https://s3.residencejlm.com` self-clean after 1 day.


### Clipboard

Copy file contents to clipboard: `wl-copy < FILE` (Wayland) or `xclip -selection clipboard < FILE` (X11). Detect which is available.

For PDF or binary, warn that clipboard export isn't meaningful and suggest email/Drive instead.

## Accepted inputs

Any file produced by this plugin: `.raw.txt`, `.cleaned.md`, `.structured.md`, `.blog.md`, `.summary.md`, `.notes.md`, `.combined.md`, `.combined.pdf`.

Also accept arbitrary paths the user supplies.

## Multiple destinations

Allow chaining: "email it and upload to Drive" should do both.
