---
name: combine-then-transcribe
description: Concatenate multiple audio recordings into one file and send as a single transcription job. Preserves a segment map so timestamps in the unified transcript can be traced back to their source files. Use when the user has several voice memos / chapters / interview parts that belong to one session and wants a single combined transcript instead of N separate ones.
---

# Combine then transcribe

Stitch together multiple audio files and run them through preprocessing + ASR as a single job. Cheaper (one upload, one job) and produces a coherent single transcript.

## When to use

- Several voice memos recorded in one sitting that the user thinks of as one piece
- Recording was split across files due to app/device limits (e.g. WhatsApp 16MB cap, phone storage)
- Multi-part interview where each part is a separate file
- Anything where the user says "combine these and transcribe"

## Inputs

- A list of files, a glob, or a folder
- Optional order override (otherwise sort by filename, which usually matches recording order if filenames have timestamps)

## Pipeline

### 1. Validate / harmonise

Before concatenation, all files must share the same sample rate, channel count, and codec. If they don't, normalise each one first via the `preprocess-for-transcription` skill (or just the format-normalise pass of it). Cheapest: normalise all to mono / 16kHz / opus, then concat.

### 2. Concatenate

Use ffmpeg's concat demuxer (lossless when codecs match):

```bash
# Build the concat list
{
  for f in "${FILES[@]}"; do
    printf "file '%s'\n" "$(realpath "$f")"
  done
} > /tmp/concat-list.txt

ffmpeg -f concat -safe 0 -i /tmp/concat-list.txt -c copy COMBINED.opus
```

If a boundary marker is desired (helps the user / ASR see file breaks), insert a short silence between segments. Easiest approach: insert a 1s silent opus snippet between every two files in the concat list.

### 3. Emit segment map

Write `<combined-stem>.segments.json` capturing where each source file lives in the combined timeline:

```json
{
  "combined": "audio/processed/session.combined.opus",
  "boundary_silence_seconds": 1.0,
  "segments": [
    {"index": 0, "source": "memo-01.opus", "start": 0.0,    "end": 312.4},
    {"index": 1, "source": "memo-02.opus", "start": 313.4,  "end": 654.1},
    {"index": 2, "source": "memo-03.opus", "start": 655.1,  "end": 901.2}
  ]
}
```

Durations come from `ffprobe -i <file> -show_entries format=duration`. This sidecar is what makes diarisation timestamps and "where in the recording" references traceable back to the original files.

### 4. Preprocess + transcribe

Invoke `preprocess-for-transcription` on the combined file (silence-trim is fine here — boundary silences are 1s, well under the 2.5s threshold, so they'll be preserved as boundary cues). Then invoke `transcribe-assemblyai` (or whichever ASR the user picked).

### 5. Optional — split transcript by source

After transcription, offer to split the resulting transcript back into per-source files using the segment map and AssemblyAI's word-level timestamps. Output: `transcripts/<source-stem>.from-combined.md` for each source.

## Folder convention

- Sources stay in place (or `audio/raw/` if user is organising)
- Combined file: `audio/processed/<session-name>.combined.opus`
- Segment map: `audio/processed/<session-name>.segments.json`
- Transcript: `transcripts/<session-name>.combined.raw.md` (then iterative-refine takes over)

## Output report

```
Inputs:       3 files, 26m 48s total
Combined:     audio/processed/session.combined.opus (mono 16kHz, 4.1 MB)
Segment map:  audio/processed/session.segments.json
Boundaries:   1.0s silence between each source

Next: send to AssemblyAI? (y/n)
```

## Edge cases

- **Mixed codecs / sample rates**: must re-encode (lossy concat, but for ASR purposes irrelevant). Warn the user.
- **One file is corrupt / unreadable**: skip it, log warning, continue with the rest. Don't fail the whole job.
- **Total combined length > 4 hours**: AssemblyAI handles it but costs add up — flag the estimated cost (~$0.37/hr with diarisation) before submitting.
- **User passes a single file**: just route directly to `preprocess-for-transcription` + transcribe; no concat needed.
