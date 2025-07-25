# Opera Data Processor

A command-line tool for processing high-content imaging data from Opera Phenix systems.

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
    └── OperaGUI_ImageJ.py    # GUI interaction module
```

> 🔸 Each folder containing `.py` files should include an `__init__.py` to be recognized as a package.

---

## 🛠️ Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/RossScrim/Opera_Phenix_Data_Handler.git
cd Opera_Phenix_Data_Handler
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
Opera_Processor
```

This executes the `main()` function from:

```
OperaPhenixDataHandler/main.py
```

---

## 🧾 JSON Configuration Files

Store your `.json` files in the `data/` folder. Access them in code like this:

```python
import json
from pathlib import Path

config_path = Path(__file__).resolve().parent.parent / "data" / "example_config.json"
with open(config_path, "r") as f:
    config = json.load(f)
```

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
