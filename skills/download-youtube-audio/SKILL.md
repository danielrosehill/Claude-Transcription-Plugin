---
name: download-youtube-audio
description: Use when the user wants to download audio from a YouTube URL (or YouTube playlist). Triggers on phrases like "download audio from youtube", "grab the audio from this yt link", "yt-dlp this", or any YouTube URL paired with a request to save audio. Saves to ~/audio/yt-raw using yt-dlp.
---

# Download YouTube Audio

Download the audio track from a YouTube URL using `yt-dlp` and save it to `~/audio/yt-raw/`.

## Steps

1. **Ensure the output directory exists**:
   ```bash
   mkdir -p ~/audio/yt-raw
   ```

2. **Run yt-dlp** with audio extraction. Default to m4a (no re-encode when source is already AAC, otherwise best available). As of yt-dlp 2026.03.17, YouTube requires a JS runtime + remote EJS challenge solver or extraction fails with `This video is not available`:
   ```bash
   yt-dlp -x --audio-format m4a --audio-quality 0 \
     --js-runtimes "node:$(which node)" \
     --remote-components ejs:github \
     -o "$HOME/audio/yt-raw/%(title)s.%(ext)s" \
     "<URL>"
   ```

   - `-x` extracts audio only
   - `--audio-format m4a` — default; if the user asks for mp3, swap to `mp3`
   - `--audio-quality 0` — best available
   - `--js-runtimes node:<path>` — point at Node (deno is the only default; not always available). Resolve via `which node`.
   - `--remote-components ejs:github` — pulls the signature/n challenge solver from yt-dlp's EJS release. Without this, formats resolve to nothing.
   - Filename is the video title

3. **Report** the final saved file path to the user. Use `ls -lt ~/audio/yt-raw/ | head -3` if you need to confirm.

## Notes

- If the URL is a playlist, yt-dlp will download every entry into the same folder — confirm with the user first if the URL looks like a playlist (`list=` param) and they only wanted one track.
- If `yt-dlp` is missing, install via `pipx install yt-dlp` or `pip install --user -U yt-dlp`.
- Do not re-encode unnecessarily; `-x --audio-format m4a` is fast when the source is already AAC.
- For mp3 requests, add `--embed-thumbnail --add-metadata` so tags and cover art carry over.
