#!/usr/bin/env bash
# Encode a single clip with AV1
# Usage: ./encode_clip.sh input.mp4 output.mp4 [fps] [crf]
#
# Examples:
#   ./encode_clip.sh video.mp4 compressed.mp4            # 10fps CRF42 (balanced)
#   ./encode_clip.sh video.mp4 compressed.mp4 30 34      # 30fps CRF34 (high quality)
#   ./encode_clip.sh video.mp4 compressed.mp4 10 50      # 10fps CRF50 (compact)

set -euo pipefail

INPUT="${1:?Usage: encode_clip.sh input.mp4 output.mp4 [fps] [crf]}"
OUTPUT="${2:?Usage: encode_clip.sh input.mp4 output.mp4 [fps] [crf]}"
FPS="${3:-10}"
CRF="${4:-42}"

if [ "$FPS" -lt 30 ]; then
    VF="fps=${FPS},scale=456:256"
else
    VF="scale=456:256"
fi

echo "Encoding: $INPUT → $OUTPUT"
echo "Config: AV1 CRF${CRF} @${FPS}fps 456x256 10-bit"

ffmpeg -y -i "$INPUT" \
    -vf "$VF" \
    -c:v libaom-av1 -crf "$CRF" -cpu-used 8 -row-mt 1 \
    -pix_fmt yuv420p10le -an "$OUTPUT"

SRC_SIZE=$(stat -f%z "$INPUT" 2>/dev/null || stat -c%s "$INPUT" 2>/dev/null)
ENC_SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
RATIO=$((SRC_SIZE / ENC_SIZE))

echo ""
echo "Source: $((SRC_SIZE / 1024)) KB"
echo "Encoded: $((ENC_SIZE / 1024)) KB"
echo "Ratio: ${RATIO}x"
