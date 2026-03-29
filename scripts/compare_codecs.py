#!/usr/bin/env python3
"""
Compare AV1 vs H.265 at various CRF/fps settings.

Usage:
    python compare_codecs.py --input video.mp4 --duration 10
"""

import argparse
import json
import os
import subprocess
import sys


def run(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_ssim(test, ref):
    r = subprocess.run(
        "ffmpeg -i {} -i {} -filter_complex [0:v][1:v]ssim -f null -".format(test, ref),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in r.stderr.decode().split("\n"):
        if "All:" in line:
            return float(line.split("All:")[1].split()[0])
    return 0


def main():
    parser = argparse.ArgumentParser(description="Compare AV1 vs H.265")
    parser.add_argument("--input", required=True)
    parser.add_argument("--duration", type=int, default=10, help="Seconds to test")
    args = parser.parse_args()

    src = args.input
    dur = args.duration

    # Create references
    for fps in [10, 30]:
        ref = "/tmp/ref_{}fps.mp4".format(fps)
        vf = "fps={},scale=456:256".format(fps) if fps < 30 else "scale=456:256"
        run("ffmpeg -y -i {} -t {} -vf '{}' -c:v libx264 -crf 0 -pix_fmt yuv420p -an {}".format(
            src, dur, vf, ref))

    configs = []

    # H.265 configs
    for fps in [30, 10]:
        for crf in [23, 28, 32, 36]:
            configs.append(("H.265", fps, crf,
                            "-c:v libx265 -crf {} -preset medium -pix_fmt yuv420p".format(crf)))

    # AV1 configs
    for fps in [30, 10]:
        for crf in [28, 34, 38, 42, 46, 50]:
            configs.append(("AV1", fps, crf,
                            "-c:v libaom-av1 -crf {} -cpu-used 8 -row-mt 1 -pix_fmt yuv420p10le".format(crf)))

    print("{:<8} {:>4} {:>5} {:>8} {:>8} {:>8}".format(
        "Codec", "FPS", "CRF", "kbps", "SSIM", "8hr MB"))
    print("-" * 46)

    for codec, fps, crf, flags in configs:
        ref = "/tmp/ref_{}fps.mp4".format(fps)
        out = "/tmp/compare_test.mp4"
        run("ffmpeg -y -i {} {} -an {}".format(ref, flags, out))

        sz = os.path.getsize(out) if os.path.exists(out) else 0
        if sz == 0:
            continue
        kbps = round(sz * 8 / dur / 1000, 1)
        mb8hr = round(kbps * 8 * 3600 / 8 / 1024, 0)
        ssim = get_ssim(out, ref)

        print("{:<8} {:>4} {:>5} {:>8} {:>7.4f} {:>8}".format(
            codec, fps, crf, kbps, ssim, int(mb8hr)))

    print()
    print("Tip: Use --duration 30 for more accurate results (slower)")


if __name__ == "__main__":
    main()
