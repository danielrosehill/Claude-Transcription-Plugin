---
name: preprocess-for-transcription
description: Prepare audio for transcription — format normalise (mono/16kHz/opus), loudness normalise (EBU R128), and collapse long silences (silero-vad). Optional denoise pass. Use before sending to AssemblyAI or any ASR for cleaner results, smaller uploads, and lower cost. Use when the user asks to "preprocess audio", "prep for transcription", "clean up a recording before sending it", or just hands over a raw voice memo to be transcribed.
---

# Preprocess audio for transcription

Single orchestrator that takes a raw recording and emits a transcription-ready file. Source is never modified.

## Pipeline (order matters)

| Pass | Default | Notes |
|---|---|---|
| 1. Denoise | **off** (flag `--denoise`) | turn on for noisy field recordings, leave off for clean voice memos |
| 2. Format normalise | **on** | mono, 16 kHz, opus 24k |
| 3. Loudness normalise | **on** | EBU R128 via ffmpeg `loudnorm` |
| 4. Silence cap | **on** | silero-vad detects speech, every gap capped at 0.4s max (no speech ever clipped). Sub-0.4s natural pauses pass through untouched. |

Passes 2+3 run in a single ffmpeg invocation (one decode/encode). Pass 4 runs after.

## Folder convention

If invoked inside an existing project structure with `audio/` or `context/` already present, respect it. Otherwise:

- Source stays where it is, or moves to `audio/raw/<basename>` if the user is OK with that
- Output: `audio/processed/<stem>.preprocessed.opus`
- Side-files (loudnorm stats, VAD segment data): `audio/processed/<stem>.<ext>`

Never overwrite — if `<stem>.preprocessed.opus` exists, suffix `.v2`, `.v3`, etc.

## Implementation

The full pipeline is shipped as a reusable script. **Invoke it directly** rather than reimplementing:

```bash
scripts/preprocess-audio.sh [--denoise] [--no-silence-trim] [--max-gap SEC] [--out-dir DIR] INPUT
```

The script handles all four passes and writes `<stem>.preprocessed.opus` to the output dir.

Internals (for reference):

- **Pass 1 — denoise (optional)**: `ffmpeg -af "afftdn=nf=-25"`. Off by default. Enable with `--denoise` for noisy field recordings.
- **Passes 2+3 — format + loudness (combined ffmpeg invocation)**: `ffmpeg -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ac 1 -ar 16000 -c:a pcm_s16le` (WAV intermediate so the python step doesn't need codec deps).
- **Pass 4 — silence cap**: `scripts/silence-collapse.py` — silero-vad detects speech segments (ML, used inside Whisper / NeMo), then **every gap between speech segments is capped at `--max-gap` (default 0.4s)**. Speech is never clipped; only the dead air between speech is truncated. Sub-`max-gap` natural pauses pass through untouched.
- **Final encode**: opus 24k.

Output stats (size, duration, removed seconds, removal %, speech segment count) are written to `<stem>.vad-stats.json`.

### Why `--max-gap` cap and not `>min-gap collapse`

Earlier iteration used "collapse silences over 2.5s." That preserved natural cadence but felt loose because medium-length pauses (1–2.5s) survived intact. The cap-gap approach uniformly truncates every gap longer than the threshold, eliminating all dead air without ever cutting speech.

Validated on a 41-minute voice memo: cap@0.4s removes ~14% (vs ~3.6% with the old collapse>2.5s approach), no perceptible word clipping. Auto-editor was tried and rejected — its energy-threshold approach chops mid-syllable on quiet speech.

## Output report

After running, print:

```
Input:        recording.m4a (12m 04s, stereo 48kHz, 14 MB)
Output:       audio/processed/recording.preprocessed.opus (9m 18s, mono 16kHz, 1.6 MB)
Removed:      2m 46s of silence (23%)
Loudness:     normalised to -16 LUFS
Denoise:      skipped (use --denoise to enable)
```

## Flags

- `--denoise` — enable pass 1
- `--no-silence-trim` — skip pass 4 (keep all silence)
- `--max-gap <seconds>` — override default 0.4s gap cap (lower = tighter)
- `--out-dir <path>` — override default `audio/processed/`

## When to skip this skill

- Audio is already `mono 16kHz opus` and was recorded in a controlled environment → just transcribe directly
- User explicitly wants raw audio sent (e.g. needs maximum fidelity for diarisation testing)

## Defaults locked against

Validated 2026-04-28 against a 41-minute combined voice memo (Job-Search-Planning-0426). With `--max-gap 0.4`:
- Input: 41:43, 20 MB
- Output: 35:54, 5.9 MB
- Removed 349s (13.9%) of dead air
- No word clipping (silero is speech-aware, unlike energy-threshold tools)
