---
name: messy-audio-fix
description: Diagnose-and-treat workflow for very messy recordings where the standard preprocessor isn't enough. Generates a spectrogram, identifies problematic frequency bands (AC hum, rumble, narrow-band whines, broadband hiss, clipping), and proposes targeted ffmpeg filters. ONLY use when the user explicitly invokes it — the normal pipeline runs `preprocess-for-transcription` directly and skips diagnostic work. Trigger phrases the user might use — "this audio is messy", "transcription failed because of noise", "fix this rough recording", "the audio is bad and the transcript is garbage".
---

# Messy audio fix

Deliberate, opt-in workflow for audio that the standard pipeline can't handle. Diagnoses what's wrong, recommends targeted remediations, and only applies them once the user confirms.

## When NOT to use this skill

- Routine voice memos — modern ASR is robust to moderate noise (see your own POC at https://github.com/danielrosehill/Crying-Baby-Audio-Scrub). The normal `preprocess-for-transcription` is the right tool.
- "Just clean it up before sending" — that's `preprocess-for-transcription`.
- Ambiguous noise that hasn't actually broken transcription — try transcribing first; ASR may handle it fine.

## When to use it

- A previous transcription attempt produced garbage and you suspect the audio is the cause
- The recording is *audibly* bad — humming, whining, rumbling, clipping, or so much hiss that even humans struggle
- The user explicitly asks to "diagnose" or "fix" a recording

## Workflow

### Step 1 — diagnose (always do this first, do not auto-apply)

Render a spectrogram and run a numerical analysis:

```bash
scripts/render-spectrogram.sh INPUT.opus
uv run --quiet --with numpy --with soundfile --with scipy \
  scripts/analyse-spectrum.py INPUT.opus
```

The analyser produces a JSON report covering:

- **Band energies (dB)** — rumble (20–80 Hz), voice low/mid/high, HF hiss (>8 kHz)
- **AC hum scoring** — peaks at 50 Hz and 60 Hz + harmonics, relative to voice
- **Narrow-band whines** — top 5 spectral peaks above 1.5 kHz that stick out >15 dB above local median (typical of HDD seek, fans, switching power supplies, monitor whine)
- **Clipping** — % of samples at full scale
- **Diagnoses** — plain-English problem statements
- **Suggested filters** — concrete ffmpeg `-af` strings, ready to drop into a pipeline

Show the user:
1. The spectrogram (open it visually if a display is available)
2. The diagnoses list
3. The suggested filters

Do NOT apply anything yet.

### Step 2 — confirm

Ask the user which suggestions to apply. They may want all, some, or none. They may also want to skip the messy-audio-fix entirely after seeing the diagnosis ("looks fine to me, just transcribe it").

If multiple narrow-band whines are detected, treat them as a single block — applying or skipping all of them together is fine; cherry-picking individual whines is over-engineering for ASR prep.

### Step 3 — apply (only on user confirmation)

Build the ffmpeg filter chain in order:

1. **High-pass** (if rumble flagged) — `highpass=f=90`
2. **Notches** (if hum or whines flagged) — chain `equalizer=...` filters with `t=q:w=2:g=-25`
3. **Loudness normalise** — `loudnorm=I=-16:TP=-1.5:LRA=11`
4. **Resample to mono 16 kHz** — `-ac 1 -ar 16000`
5. **Encode to opus 24k** — `-c:a libopus -b:a 24k`

If broadband HF hiss was flagged, EQ won't fix it — invoke the standalone `denoise` skill (DeepFilterNet or Auphonic) **before** building the filter chain. Then run this skill's filter chain on the denoised output.

If clipping was flagged, warn the user that no amount of filtering can recover the clipped peaks. Proceed anyway — ASR usually copes — but flag that the source recording was already damaged.

Output: `<stem>.fixed.opus` in `audio/processed/`.

### Step 4 — verify

After applying, re-render the spectrogram on the output and present it side-by-side with the original. Visual confirmation that the targeted bands actually got attenuated.

Then either:
- Hand off to `transcribe-assemblyai` (or whichever ASR), OR
- If the result still looks bad, escalate to `denoise` with a stronger backend, OR
- Conclude that the audio is unsalvageable and report.

## Folder convention

- `<stem>.spectrogram.png` and `<stem>.spectrogram.fixed.png` in `audio/processed/`
- `<stem>.spectrum-analysis.json` (the diagnostic report)
- `<stem>.fixed.opus` (final cleaned output)

## Honest expectations

- **Hum / rumble / narrow-band whines**: highly fixable with targeted notches. EQ is the right tool.
- **Broadband hiss / fan / room tone**: EQ can't help much. ML denoising (DeepFilterNet) is the right tool.
- **Wind, mouth noise, plosives**: very hard to fix post-hoc. Often unsalvageable for ASR.
- **Clipping**: unrecoverable. Source-side fix only.
- **Multiple overlapping speakers** when only one is wanted: not a denoising problem — needs source separation (`pyannote-audio` / `ElevenLabs Voice Isolator`), out of scope for this skill.

## What this skill does not do

- Auto-apply any filter without user confirmation
- Replace the standard preprocess pipeline (it's a deliberate diagnostic detour)
- Promise that messy audio becomes good audio — sets expectations honestly when source is unsalvageable
