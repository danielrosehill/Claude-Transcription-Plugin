---
name: export-transcript
description: Export a transcript (or any pipeline output) by emailing it, uploading to Google Drive, or copying to clipboard. Use when the user asks to send, email, upload, save to Drive, or copy a transcript.
---

# Export transcript

Send a transcript file (or post-processed variant) to a destination.

## 1. Load your settings

Read `export-transcript.md` from `$CLAUDE_USER_DATA/transcription-pipeline/`, else `~/.claude-user-data/transcription-pipeline/`, if it exists; its notes win over the defaults below.

## Destinations

### Email

Use the `email-skills` skill set (`send-personal-email` or `send-business-email`).

Prompt user for:
- To: address
- Subject (default: file's H1 heading or stem)
- Body: either inline content or short cover note with the transcript as attachment

When attaching the transcript file, the same staging rule as Drive applies — the Google Workspace MCP typically runs on a remote host and can't read workstation paths. Stage it with the `cloud-storage:stage-file` skill (below) and pass the presigned GET URL as the attachment's `url`. The send-* email skills cover this.

### Google Drive

Use the `gws-personal` MCP. **The Google Workspace MCP runs on a remote server** — it cannot read workstation paths like `/home/<user>/...`. The canonical upload path is **staging + `fileUrl`**:

1. Stage the transcript with the `cloud-storage:stage-file` skill (use the staging script path from your notes). It prints JSON `{store,bucket,key,url}`; use `.url` (presigned GET) below.
2. `create_folder` if the user specified a new folder name (or reuse an existing one via `search`).
3. Call the MCP's `create_drive_file` tool with `fileUrl: <presigned URL>` and `folder_id: <folder-id>`. **Do not** pass a workstation `file_path`/`sourcePath` — that param is server-local only.
4. If the transcript is markdown and the user wants it editable, use `create_google_doc` with the content inline instead.
5. Optionally `share_file` if the user wants a shareable link.

Report back the Drive `webViewLink`, then delete the staged object (`stage.sh --rm <store> <bucket> <key>`).

**Do NOT** reach for `rclone`, `scp`, `gcloud`, `gdrive`, direct Drive API `curl`, or any other workaround. MinIO staging + `fileUrl` is the only supported route from this workstation; the `*-transient` staging buckets at `https://s3.example.com` self-clean after 1 day.


### Clipboard

Copy file contents to clipboard: `wl-copy < FILE` (Wayland) or `xclip -selection clipboard < FILE` (X11). Detect which is available.

For PDF or binary, warn that clipboard export isn't meaningful and suggest email/Drive instead.

## Accepted inputs

Any file produced by this plugin: `.raw.txt`, `.cleaned.md`, `.structured.md`, `.blog.md`, `.summary.md`, `.notes.md`, `.combined.md`, `.combined.pdf`.

Also accept arbitrary paths the user supplies.

## Multiple destinations

Allow chaining: "email it and upload to Drive" should do both.
