#!/usr/bin/env bash
# Full preprocessing pipeline: optional denoise → mono/16kHz/opus + EBU R128 → silence collapse.
# Used by the preprocess-for-transcription skill.
#
# Usage:
#   preprocess-audio.sh [--denoise] [--no-silence-trim] [--min-gap SEC] [--out-dir DIR] INPUT
#
# Output: <OUT_DIR>/<stem>.preprocessed.opus  (default OUT_DIR = ./audio/processed)
# Side files: <OUT_DIR>/<stem>.vad-stats.json (when silence-trim runs)

set -euo pipefail

DENOISE=0
TRIM_SILENCE=1
MIN_GAP=2.5
OUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --denoise)         DENOISE=1; shift ;;
    --no-silence-trim) TRIM_SILENCE=0; shift ;;
    --min-gap)         MIN_GAP="$2"; shift 2 ;;
    --out-dir)         OUT_DIR="$2"; shift 2 ;;
    -h|--help)         sed -n '2,8p' "$0"; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *)  break ;;
  esac
done

INPUT="${1:-}"
if [[ -z "$INPUT" || ! -f "$INPUT" ]]; then
  echo "error: input file required and must exist" >&2
  exit 2
fi

STEM=$(basename "$INPUT")
STEM="${STEM%.*}"
OUT_DIR="${OUT_DIR:-$(dirname "$INPUT")/../processed}"
mkdir -p "$OUT_DIR"

# Avoid overwriting an existing preprocessed file
OUTPUT="$OUT_DIR/$STEM.preprocessed.opus"
v=2
while [[ -e "$OUTPUT" ]]; do
  OUTPUT="$OUT_DIR/$STEM.preprocessed.v$v.opus"
  ((v++))
done

SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT

CURRENT="$INPUT"

# Pass 1: optional denoise
if [[ "$DENOISE" == "1" ]]; then
  echo "[preprocess] pass 1/3: denoise (afftdn)"
  ffmpeg -y -hide_banner -loglevel error \
    -i "$CURRENT" -af "afftdn=nf=-25" -c:a pcm_s16le \
    "$SCRATCH/denoised.wav"
  CURRENT="$SCRATCH/denoised.wav"
fi

# Passes 2+3: format normalise + EBU R128 loudnorm (single ffmpeg invocation)
# When silence-trim is enabled, emit WAV here so the python script can read it without
# needing audio-codec deps; we re-encode to opus at the very end.
echo "[preprocess] pass 2/3: mono/16kHz + EBU R128 loudnorm"
if [[ "$TRIM_SILENCE" == "1" ]]; then
  NORMALISED="$SCRATCH/normalised.wav"
  ffmpeg -y -hide_banner -loglevel error \
    -i "$CURRENT" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -ac 1 -ar 16000 -c:a pcm_s16le \
    "$NORMALISED"
else
  NORMALISED="$SCRATCH/normalised.opus"
  ffmpeg -y -hide_banner -loglevel error \
    -i "$CURRENT" \
    -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
    -ac 1 -ar 16000 -c:a libopus -b:a 24k \
    "$NORMALISED"
fi
CURRENT="$NORMALISED"

# Pass 4: silence collapse via silero-vad
if [[ "$TRIM_SILENCE" == "1" ]]; then
  echo "[preprocess] pass 3/3: silence collapse (silero-vad, min-gap=${MIN_GAP}s)"
  COLLAPSED="$SCRATCH/collapsed.wav"
  STATS="$OUT_DIR/$STEM.vad-stats.json"
  uv run --quiet --with silero-vad --with soundfile --with numpy \
    "$(dirname "$0")/silence-collapse.py" \
    --min-gap "$MIN_GAP" \
    --stats "$STATS" \
    "$CURRENT" "$COLLAPSED"
  ffmpeg -y -hide_banner -loglevel error \
    -i "$COLLAPSED" -c:a libopus -b:a 24k "$OUTPUT"
else
  cp "$CURRENT" "$OUTPUT"
fi

# Report
in_dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$INPUT")
out_dur=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$OUTPUT")
in_size=$(stat -c%s "$INPUT")
out_size=$(stat -c%s "$OUTPUT")
removed=$(awk -v a="$in_dur" -v b="$out_dur" 'BEGIN{printf "%.1f", a-b}')

echo
echo "Input:   $INPUT"
echo "         $(awk -v d="$in_dur" 'BEGIN{printf "%dm %ds", d/60, d%60}'), $(numfmt --to=iec --suffix=B "$in_size")"
echo "Output:  $OUTPUT"
echo "         $(awk -v d="$out_dur" 'BEGIN{printf "%dm %ds", d/60, d%60}'), $(numfmt --to=iec --suffix=B "$out_size")"
echo "Removed: ${removed}s of silence/dead air"
[[ "$DENOISE" == "1" ]] && echo "Denoise: applied" || echo "Denoise: skipped"
