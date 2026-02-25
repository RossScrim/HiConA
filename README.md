<p align="center">
  <img src="https://raw.githubusercontent.com/RossScrim/HiConA/main/docs/logo.png" width="180" alt="HiConA Logo"/>
</p>

<h1 align="center">HiConA</h1>

<p align="center">
  <b>Hi</b>gh-<b>Con</b>tent <b>A</b>nalysis Preprocessing Pipeline for Opera Phenix Imaging
</p>

<p align="center">
  <a href="https://github.com/RossScrim/HiConA/releases">
    <img src="https://img.shields.io/github/v/release/RossScrim/HiConA?style=for-the-badge" />
  </a>
  <a href="https://github.com/RossScrim/HiConA/blob/main/License.txt">
    <img src="https://img.shields.io/github/license/RossScrim/HiConA?style=for-the-badge" />
  </a>
  <img src="https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey?style=for-the-badge" />
  <img src="https://img.shields.io/badge/GUI-enabled-success?style=for-the-badge" />
</p>

---

## Overview

**HiConA** is a Python package designed for preprocessing high-content imaging data acquired with the **Opera Phenix** system.

It integrates leading open-source bioimage analysis tools into a unified, GUI-driven workflow for scalable, reproducible, and automated processing.

Designed for:
- High-throughput screening  
- Multi-tile stitching workflows  
- Z-stack projections 
- Automated segmentation pipelines  

---

#  Features
## Automated Detection
- Automatically detects archived Opera Phenix `hs` measurement directories.
- Identifies valid imaging runs without manual navigation.

## Batch Pre-processing
- Apply configurable pipelines to multi-tile datasets.
- Process large experiments through an intuitive GUI.
- Designed for reproducibility and structured output.

## Structured Output
- Organized export directories.
- Downstream-analysis-ready formats.
- Consistent naming conventions for automation.

---

# 🔗 Integrated Tools

<p align="center">
  <img src="https://img.shields.io/badge/Cellpose-Deep%20Learning-green?style=flat-square" />
  <img src="https://img.shields.io/badge/ImageJ-Fiji-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/EDF-Wavelet%20Fusion-purple?style=flat-square" />
</p>

###  Cellpose
Deep learning-based generalist cell segmentation.  
*Stringer et al., Nature Methods (2021)*

### Extended Depth of Field (EDF)
Wavelet-based z-stack fusion for multi-channel microscopy images.  
*Forster et al., Microscopy Research and Technique (2004)*

### ImageJ / Fiji Integration
Execute custom `.ijm` macros directly inside the pipeline.

---

# Project Structure

```bash
.
├── HiConA/
│   ├── Backend/              # Processing logic
│   ├── GUI/                  # Interface + JSON configs
│   ├── Utilities/            # IO + config readers
│   └── main.py               # Entry point
├── ImageJ Macro Examples/
├── LICENSE
├── requirements.txt
└── setup.py
```

> ⚠️ Every directory containing Python modules must include `__init__.py`.

---

# Requirements

- **Python 3.12**
- Windows or Linux
- Opera Phenix imaging datasets

---

# Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/RossScrim/HiConA.git
cd HiConA
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

## 3️⃣ Install in Editable Mode

```bash
pip install -e .
```

This:
- Installs dependencies
- Registers CLI entry point
- Enables development modifications without reinstalling

---

# ▶️ Usage

Run the application:

```bash
HiConA.run
```

This executes:

```python
HiConA/main.py
```

✅ Ensures correct relative imports  
❌ Do NOT run `python main.py`

---

# Example Workflow

1. Select Opera Phenix dataset
2. Detect `hs` measurement folders
3. Choose processing steps:
   - Z projection method
   - Stitching
   - Segmentation
4. Execute batch processing
5. Export in a standardise structure

---

# Uninstall

```bash
pip uninstall HiConA
```

Remove environment:

```bash
deactivate
rm -rf .venv      # macOS/Linux
rd /s /q .venv    # Windows
```

---

# References

- Forster B. et al., *Complex Wavelets for Extended Depth-of-Field*, 2004  
- Stringer C. et al., *Cellpose*, Nature Methods (2021)
- S. Preibisch, S. Saalfeld, P. Tomancak (2009) Globally optimal stitching of tiled 3D microscopic image acquisitions”, Bioinformatics, 25(11):1463-1465
---

# 📄 License

Licensed under **CC-BY-SA 4.0**.  
See `LICENSE` for full terms.

---

<p align="center">
  Built for scalable microscopy workflows 🔬
</p>
