# Egocentric-Native Compression

**Compressing egocentric factory video for Physical AI data pipelines.**

A data collection device produces 10 GB per worker-day. 1,000 devices deployed into a single factory yields 10 TB/day that needs to be uploaded. A typical industrial ISP in India provisions 500 Mbps of shared upload. Under these conditions, the minimum cycle time per factory is **44 hours** — nearly 2 days to upload a single day of data.

This project develops an egocentric-native compression pipeline that reduces upload time from **44 hours to 2-7 hours** while maintaining quality sufficient for Physical AI (robot learning) applications.

## Results

### AV1 vs Standard H.265 — Full Scene at 456x256

Both codecs tested at the Egocentric-100K product resolution (456x256).

#### At 30fps (matching Egocentric-100K)

| Method | SSIM | Bitrate | 8hr Size | Upload 1K@500Mbps | Saving |
|---|---|---|---|---|---|
| **H.265 CRF23** (industry standard) | 0.965 | 1770 kbps | 6,222 MB | 17.4 hr | baseline |
| **H.265 CRF28** | 0.936 | 842 kbps | 2,958 MB | 8.3 hr | 52% |
| **AV1 CRF34 10-bit** | 0.960 | 1344 kbps | 4,724 MB | 13.2 hr | **24% vs H.265** |
| **AV1 CRF42 10-bit** | 0.942 | 681 kbps | 2,393 MB | 6.7 hr | **61%** |
| **AV1 CRF50 10-bit** | 0.923 | 363 kbps | 1,277 MB | 3.6 hr | **79%** |

#### At 10fps (Physical AI models typically subsample to 10fps)

| Method | VMAF | SSIM | Bitrate | 8hr Size | Upload 1K@500Mbps |
|---|---|---|---|---|---|
| H.265 CRF28 | 96.2 | 0.948 | 637 kbps | 2,239 MB | 6.3 hr |
| H.265 CRF32 | 89.9 | 0.920 | 354 kbps | 1,243 MB | 3.5 hr |
| **AV1 CRF34 10-bit** | **98.1** | **0.956** | **673 kbps** | **2,367 MB** | **6.6 hr** |
| **AV1 CRF42 10-bit** | **93.5** | **0.939** | **357 kbps** | **1,255 MB** | **3.5 hr** |
| **AV1 CRF50 10-bit** | **87.0** | **0.914** | **202 kbps** | **709 MB** | **2.0 hr** |

### Why AV1 Outperforms H.265

- **30-37% smaller** at equivalent perceptual quality (VMAF)
- Better entropy coding, larger block sizes (128x128 vs 64x64)
- 10-bit internal precision improves quantization efficiency
- Superior rate-distortion optimization at low bitrates

### Impact on Upload Bottleneck

| Scenario | Daily Data (1K devices) | Upload @500Mbps |
|---|---|---|
| **Uncompressed source** (1080p 30fps) | 10 TB | **44 hours** |
| Egocentric-100K product (H.265 456x256 30fps) | ~4 TB | ~11 hours |
| **AV1 CRF42 30fps** (high quality) | 2.4 TB | **6.7 hours** |
| **AV1 CRF42 10fps** (balanced) | 1.3 TB | **3.5 hours** |
| **AV1 CRF50 10fps** (compact) | 845 GB | **2.4 hours** |

## Pipeline

```
DEVICE (ARM edge):
  1080p 30fps → downsample to 456x256 → optional: reduce to 10fps
  → AV1 encode (libaom, cpu-used=8, 20x realtime) → upload

SERVER:
  AV1 decode → 456x256 video ready for Physical AI training
```

No neural network, no GPU, no custom hardware needed on device. Standard ffmpeg with libaom-av1.

## Quick Start

### Encode a single clip

```bash
# 30fps (matches Egocentric-100K format)
ffmpeg -y -i input_1080p.mp4 \
    -vf "scale=456:256" \
    -c:v libaom-av1 -crf 42 -cpu-used 8 -row-mt 1 \
    -pix_fmt yuv420p10le -an output.mp4

# 10fps (smaller upload, sufficient for most Physical AI)
ffmpeg -y -i input_1080p.mp4 \
    -vf "fps=10,scale=456:256" \
    -c:v libaom-av1 -crf 42 -cpu-used 8 -row-mt 1 \
    -pix_fmt yuv420p10le -an output.mp4
```

### Encode an entire worker shift

```bash
python3 scripts/encode_shift.py \
    --input /path/to/worker_001/ \
    --output /path/to/compressed/ \
    --fps 10 \
    --crf 42
```

### Measure quality

```bash
python3 scripts/measure_quality.py \
    --original /path/to/source.mp4 \
    --compressed /path/to/compressed.mp4
```

## Recommended Profiles

| Profile | FPS | CRF | VMAF | 8hr Size | Use Case |
|---|---|---|---|---|---|
| **High Quality 30fps** | 30 | 34 | ~98 | 4,724 MB | Maximum fidelity, matches E100K |
| **Balanced 30fps** | 30 | 42 | ~94 | 2,393 MB | Good quality at 30fps |
| **Compact 30fps** | 30 | 50 | ~87 | 1,277 MB | Aggressive 30fps compression |
| **High Quality 10fps** | 10 | 34 | 98 | 2,367 MB | Best quality at 10fps |
| **Balanced 10fps** | 10 | 42 | 93 | 1,255 MB | Recommended for most PI models |
| **Compact 10fps** | 10 | 50 | 87 | 709 MB | Maximum compression |

## Quality Measurement

**Use VMAF (Netflix's perceptual quality metric), not SSIM.** VMAF has the highest correlation with human perception (PCC 0.89) and is what Netflix uses for quality decisions.

- **VMAF > 93:** High quality, minimal artifacts
- **VMAF > 87:** Good quality, acceptable for Physical AI
- **VMAF > 75:** Minimum acceptable threshold

SSIM can be misleading — a frame with 0.94 SSIM can have VMAF 93 (excellent quality). Always use VMAF for decisions.

```bash
# Install ffmpeg with VMAF support (static build)
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-static/ffmpeg /usr/local/bin/ffmpeg-vmaf

# Measure VMAF
ffmpeg-vmaf -i compressed.mp4 -i original.mp4 \
    -lavfi libvmaf=log_fmt=json:log_path=vmaf.json \
    -f null -
```

## What Doesn't Work (Experimentally Validated)

| Approach | Result | Why |
|---|---|---|
| Cycle-aware compression via IMU | No gain | Workers aren't periodic at the signal level (autocorrelation <0.3) |
| Background subtraction | 5% gain | H.265 already handles static regions via skip blocks |
| Motion-based ROI detection | Wrong target | Detects swinging strips/machines, not hands |
| Frame interpolation 2fps→30fps | VMAF drops 87→39 | 500ms gap too large — 49% of pixels change, flow estimation fails |
| VQ-VAE patch tokenization | 17.9 dB PSNR | Too low quality; codebook can't represent fine hand details |
| Frame deduplication at 0.85 similarity | Loses signal | 69% of pixels changed >20 levels — the "redundant" part is the foreground (hands/tools) |

## Dataset

Experiments use the [Egocentric-100K](https://huggingface.co/datasets/builddotai/Egocentric-100K) dataset format:
- 100 unique workers, head-mounted fisheye camera
- 87 clips per worker, 3 minutes each
- 1080p 30fps HEVC at ~4.7 Mbps, with paired IMU at 30Hz
- Target output: 456x256 (matching Egocentric-100K product resolution)

```bash
# Download test data
gsutil -m cp -r gs://build-ai-egocentric-native-compression/worker_001 .
```

## References

1. **Video Compression Research** — Build AI Internal (2026). Pixel binning + H.265 achieves 25-134x compression at >0.97 SSIM with server-side Real-ESRGAN reconstruction.
2. **HEVC Standard** — Sullivan et al., IEEE TCSVT 2012. H.265 achieves ~50% bitrate reduction over H.264.
3. **OneVision Encoder** — LMMs-Lab et al., 2026. Only 3-25% of video patches carry new information per GOP — validated causally.
4. **AutoGaze** — Shi, Fu, Lian et al., 2026. Egocentric video has extreme spatiotemporal redundancy (~1% gazing ratio at 4K).
5. **Video Quality Metrics** — Herb et al., PCS 2025. VMAF is the most reliable metric for both neural and traditional codecs (PCC 0.89).

## Project Structure

```
egocentric-native-compression/
├── README.md
├── scripts/
│   ├── encode_shift.py          # Encode all clips for a worker
│   ├── encode_clip.sh           # Single clip encoding (bash)
│   ├── measure_quality.py       # VMAF + SSIM quality measurement
│   └── compare_codecs.py        # AV1 vs H.265 comparison sweep
├── samples/                     # Sample compressed videos
│   ├── source_456x256_30fps.mp4
│   ├── av1_crf42_30fps.mp4
│   ├── av1_crf42_10fps.mp4
│   └── h265_crf28_30fps.mp4
└── results/
    └── codec_comparison.json    # Full benchmark results
```

## License

Apache 2.0

## Contact

eddy@build.ai | [www.egocentric.org/compression](http://www.egocentric.org/compression)
