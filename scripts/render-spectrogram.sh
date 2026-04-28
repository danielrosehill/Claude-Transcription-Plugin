#!/usr/bin/env bash
# Render a visual spectrogram PNG for an audio file. Used by messy-audio-fix.
#
# Usage: render-spectrogram.sh INPUT [OUTPUT.png]

set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-${INPUT%.*}.spectrogram.png}"

if [[ -z "$INPUT" || ! -f "$INPUT" ]]; then
  echo "usage: render-spectrogram.sh INPUT [OUTPUT.png]" >&2
  exit 2
fi

ffmpeg -y -hide_banner -loglevel error -i "$INPUT" \
  -lavfi "showspectrumpic=s=1600x800:mode=combined:legend=enabled:scale=log:color=intensity" \
  "$OUTPUT"

echo "spectrogram: $OUTPUT"
