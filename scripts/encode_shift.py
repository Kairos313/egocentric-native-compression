#!/usr/bin/env python3
"""
Encode all clips for a worker shift using AV1.

Usage:
    python encode_shift.py --input worker_001/ --output compressed/ --fps 10 --crf 42
    python encode_shift.py --input worker_001/ --output compressed/ --fps 30 --crf 34
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def encode_clip(src, dst, fps, crf):
    """Encode a single clip. Returns (encoded_size, encode_time)."""
    t0 = time.time()
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vf", "fps={},scale=456:256".format(fps) if fps < 30 else "scale=456:256",
        "-c:v", "libaom-av1", "-crf", str(crf),
        "-cpu-used", "8", "-row-mt", "1",
        "-pix_fmt", "yuv420p10le", "-an", str(dst)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.time() - t0
    size = os.path.getsize(dst) if os.path.exists(dst) else 0
    return size, elapsed


def main():
    parser = argparse.ArgumentParser(description="Encode worker shift with AV1")
    parser.add_argument("--input", required=True, help="Worker data directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--fps", type=int, default=10, choices=[10, 15, 30])
    parser.add_argument("--crf", type=int, default=42)
    parser.add_argument("--max-clips", type=int, default=0, help="Limit clips (0=all)")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    clips = sorted(input_dir.rglob("video.mp4"))
    if args.max_clips > 0:
        clips = clips[:args.max_clips]

    print("Egocentric-Native Compression")
    print("  Input: {} ({} clips)".format(input_dir, len(clips)))
    print("  Output: {}".format(output_dir))
    print("  Config: AV1 CRF{} @{}fps 456x256 10-bit".format(args.crf, args.fps))
    print()

    total_src = 0
    total_enc = 0
    total_time = 0

    for i, clip in enumerate(clips):
        clip_name = clip.parent.name
        dst = output_dir / "{}.mp4".format(clip_name)

        src_size = os.path.getsize(clip)
        enc_size, elapsed = encode_clip(clip, dst, args.fps, args.crf)

        total_src += src_size
        total_enc += enc_size
        total_time += elapsed

        if (i + 1) % 10 == 0 or i == 0 or i == len(clips) - 1:
            ratio = src_size / enc_size if enc_size > 0 else 0
            print("[{:3d}/{}] {} | {:.1f} MB → {:.0f} KB | {:.0f}x | {:.1f}s".format(
                i + 1, len(clips), clip_name,
                src_size / 1048576, enc_size / 1024, ratio, elapsed))

    # Summary
    duration_s = len(clips) * 180
    kbps = total_enc * 8 / duration_s / 1000 if duration_s > 0 else 0
    scale = 8 * 3600 / duration_s if duration_s > 0 else 1
    mb_8hr = total_enc * scale / 1048576

    print()
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print("  Clips: {}".format(len(clips)))
    print("  Duration: {:.1f} hours".format(duration_s / 3600))
    print("  Source: {:.2f} GB".format(total_src / 1073741824))
    print("  Compressed: {:.2f} MB".format(total_enc / 1048576))
    print("  Ratio: {:.1f}x".format(total_src / total_enc if total_enc > 0 else 0))
    print("  Bitrate: {:.1f} kbps".format(kbps))
    print("  8hr estimate: {:.0f} MB".format(mb_8hr))
    print("  Encode speed: {:.1f}s/clip ({:.0f}x realtime)".format(
        total_time / len(clips), 180 / (total_time / len(clips)) if total_time > 0 else 0))
    print("  Upload 1K devices @500Mbps: {:.1f} hours".format(
        mb_8hr * 1000 * 1048576 * 8 / 500e6 / 3600))

    # Save results
    results = {
        "config": {"codec": "libaom-av1", "crf": args.crf, "fps": args.fps,
                   "resolution": "456x256", "bit_depth": 10},
        "clips": len(clips),
        "source_bytes": total_src,
        "compressed_bytes": total_enc,
        "ratio": round(total_src / total_enc, 1) if total_enc > 0 else 0,
        "bitrate_kbps": round(kbps, 1),
        "est_8hr_mb": round(mb_8hr, 0),
    }
    with open(str(output_dir / "results.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
