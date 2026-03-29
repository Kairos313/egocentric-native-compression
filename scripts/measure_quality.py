#!/usr/bin/env python3
"""
Measure compression quality using VMAF, SSIM, and PSNR.

Usage:
    python measure_quality.py --original source.mp4 --compressed compressed.mp4
    python measure_quality.py --original source.mp4 --compressed compressed.mp4 --vmaf
"""

import argparse
import json
import os
import re
import subprocess
import sys


def measure_ssim_psnr(original, compressed):
    """Measure SSIM and PSNR using ffmpeg."""
    # Match fps and resolution
    cmd = (
        "ffmpeg -i {} -i {} "
        "-filter_complex '[0:v]scale=456:256[a];[1:v]scale=456:256[b];[a][b]ssim;[a][b]psnr' "
        "-f null -"
    ).format(compressed, original)

    r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = r.stderr.decode()

    result = {}
    for line in output.split("\n"):
        if "All:" in line and "SSIM" in line.upper():
            match = re.search(r'All:([0-9.]+)', line)
            if match:
                result["ssim"] = float(match.group(1))
        if "average:" in line and "PSNR" in line.upper():
            match = re.search(r'average:([0-9.]+)', line)
            if match:
                result["psnr"] = float(match.group(1))

    return result


def measure_vmaf(original, compressed, vmaf_ffmpeg="ffmpeg-vmaf"):
    """Measure VMAF. Requires ffmpeg built with libvmaf."""
    cmd = (
        "{} -i {} -i {} "
        "-lavfi libvmaf=log_fmt=json:log_path=/dev/stdout "
        "-f null -"
    ).format(vmaf_ffmpeg, compressed, original)

    r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        data = json.loads(r.stdout.decode())
        return {"vmaf": round(data["pooled_metrics"]["vmaf"]["mean"], 2)}
    except (json.JSONDecodeError, KeyError):
        # Try parsing from stderr
        for line in r.stderr.decode().split("\n"):
            if "VMAF score" in line:
                match = re.search(r'([0-9.]+)', line.split(":")[-1])
                if match:
                    return {"vmaf": float(match.group(1))}
        return {"vmaf": None, "error": "libvmaf not available. Install static ffmpeg."}


def main():
    parser = argparse.ArgumentParser(description="Measure compression quality")
    parser.add_argument("--original", required=True, help="Original source video")
    parser.add_argument("--compressed", required=True, help="Compressed video")
    parser.add_argument("--vmaf", action="store_true", help="Also measure VMAF")
    parser.add_argument("--vmaf-ffmpeg", default="ffmpeg-vmaf",
                        help="Path to ffmpeg with libvmaf (default: ffmpeg-vmaf)")
    args = parser.parse_args()

    src_size = os.path.getsize(args.original)
    enc_size = os.path.getsize(args.compressed)

    print("Original:   {} ({:.1f} MB)".format(args.original, src_size / 1048576))
    print("Compressed: {} ({:.1f} MB)".format(args.compressed, enc_size / 1048576))
    print("Ratio:      {:.1f}x".format(src_size / enc_size if enc_size > 0 else 0))
    print()

    # SSIM + PSNR
    metrics = measure_ssim_psnr(args.original, args.compressed)

    if "ssim" in metrics:
        print("SSIM:  {:.6f}".format(metrics["ssim"]))
    if "psnr" in metrics:
        print("PSNR:  {:.2f} dB".format(metrics["psnr"]))

    # VMAF
    if args.vmaf:
        vmaf = measure_vmaf(args.original, args.compressed, args.vmaf_ffmpeg)
        if vmaf.get("vmaf") is not None:
            print("VMAF:  {:.2f}".format(vmaf["vmaf"]))
        else:
            print("VMAF:  {} (install: wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz)".format(
                vmaf.get("error", "unavailable")))
        metrics.update(vmaf)

    print()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
