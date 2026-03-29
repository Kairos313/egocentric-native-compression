# Research Papers: Egocentric Native Compression

A curated collection of papers on scene-aware, generative, and novel-representation-based compression methods relevant to egocentric native compression.

---

## 1. Image Compression Using Novel View Synthesis Priors

- **File:** `nvs_priors_compression_2024.pdf`
- **Authors:** Luyuan Peng, Mandar Chitre, Hari Vishnu, Yuen Min Too, Bharath Kalyan, Rajat Mishra, Soo Pieng Tan
- **Venue:** arXiv preprint, 2024 (arXiv:2411.13862)
- **Relevance:** Demonstrates using trained novel view synthesis (NVS) models as scene priors for image compression, transmitting only residuals between camera images and model-rendered views -- directly applicable to leveraging 3D scene understanding for egocentric stream compression.

## 2. GSVC: Efficient Video Representation and Compression Through 2D Gaussian Splatting

- **File:** `gsvc_2d_gaussian_splatting_2025.pdf`
- **Authors:** Longan Wang, Yuang Shi, Wei Tsang Ooi
- **Venue:** arXiv preprint, 2025 (arXiv:2501.12060)
- **Relevance:** Proposes using 2D Gaussian splats as a native video representation for compression, achieving rate-distortion comparable to AV1/HEVC with 1500 fps rendering -- a key reference for Gaussian-splatting-based alternatives to pixel-grid codecs.

## 3. Scene Matters: Model-based Deep Video Compression

- **File:** `scene_matters_deep_video_compression_2023.pdf`
- **Authors:** Lv Tang, Xinfeng Zhang, Gai Zhang, Xiaoqi Ma
- **Venue:** arXiv preprint, 2023 (arXiv:2303.04557)
- **Relevance:** Introduces a model-based video compression (MVC) framework that treats entire scenes as fundamental units and uses implicit neural representations, achieving 20% bitrate reduction over H.266 -- validates the scene-level compression paradigm central to egocentric native compression.

## 4. Diffusion-Aided Extreme Video Compression with Lightweight Semantics Guidance

- **File:** `diffusion_extreme_compression_2026.pdf`
- **Authors:** Maojun Zhang, Haotian Wu, Richeng Jin, Deniz Gunduz, Krystian Mikolajczyk
- **Venue:** arXiv preprint, 2026 (arXiv:2602.05201)
- **Relevance:** Uses conditional diffusion models to reconstruct video frames from compressed high-level semantic representations (camera pose, segmentation masks), enabling extreme low-bitrate compression -- directly relevant to semantic-first egocentric pipelines.

## 5. DiSCo: Low-Bitrate Video Compression through Semantic-Conditioned Diffusion

- **File:** `disco_semantic_compression_2025.pdf`
- **Authors:** Lingdong Wang, Guan-Ming Su, Divya Kothandaraman, Tsung-Wei Huang, Mohammad Hajiesmaili, Ramesh K. Sitaraman
- **Venue:** arXiv preprint, 2025 (arXiv:2512.00408)
- **Relevance:** Decomposes video into text descriptions, degraded video, and sketches/poses, then reconstructs via a conditional video diffusion model -- outperforms traditional codecs by 2-10x on perceptual metrics at low bitrates, demonstrating the power of semantic decomposition for compression.
