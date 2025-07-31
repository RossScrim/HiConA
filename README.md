# HiConA

A Python package which integrates for preprocessing **Hi**gh-**Con**tent **A**nalysis (HiConA) of imaging data from the Opera Phenix with open-source image analysis packages in a GUI workflow. 

---

## 📦 Features

- Launchable from the command line via `Opera_Data_Processor`
- Detects all archived measurements from Opera Phenix "hs" directories
- GUI which allows the user to select batch and pre-process steps to apply to Opera Phenix data
- Integrates with `ImageJ` via the `OperaGUI_ImageJ` class

---

## 🧩 Project Structure

```
Opera_Phenix_Data_Handler/
├── setup.py                  # Installation script
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation (this file)
└── OperaPhenixDataHandler/   # Main package
    ├── __init__.py
    ├── main.py               # Entry point for CLI
    ├── CellProfiler.py
    ├── CellposeSegmentation.py
    ├── ConfigReader.py
    ├── FileManagement.py
    ├── ImageJAfterStitching.py
    ├── ImageProcessing.py
    ├── StitchingImageJ.py
    ├── arg.json
    ├── imagej_config.json
    ├── macro.ijm
    ├── saved_variables.json
    └── OperaGUI_ImageJ.py    # GUI interaction module
	



```

> 🔸 Each folder containing `.py` files should include an `__init__.py` to be recognized as a package.


---
## 🚀 Prerequisites

**Python 3.9 is required** - please ensure you have installed python 3.9 before installation our packages. 
you can follow the instrustions below on how to clone the repository and setup the package or download lastest release v1.1.0 and follow the instructions below under **Source Code Installation**

---

## 🛠️ Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/RossScrim/HiConA.git
cd HiConA
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install the package

Install in **editable mode** so you can make changes without reinstalling:

```bash
pip install -e .
```

This installs dependencies from `requirements.txt` and registers the CLI command `Opera_Processor`.

---

## 🚀 Usage

Once installed, simply run:

```bash
HiConA.run
```

This executes the `main()` function from:

```
HiConA/main.py
```

---

✅ This ensures relative imports work properly.

> ❌ Do **not** run it like `python main.py` — this may break imports.

---

## 🔄 Uninstall / Cleanup

To uninstall the package:

```bash
pip uninstall Opera_Processor
```

To remove the virtual environment:

```bash
deactivate
rm -rf .venv        # macOS/Linux
rd /s /q .venv      # Windows
```

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
