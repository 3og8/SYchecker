# SYchecker

**Check your computer's components and see how good they are.**

SYchecker is a simple, cross-platform CLI tool that detects your hardware and runs quick performance tests. It gives you a clear overall score (top-tier systems land around **6000**) plus breakdowns for single-core, multi-core, and memory.

Works on **Linux**, **Windows**, and **macOS**.

---

## Quick Start

```bash
git clone https://github.com/3og8/SYchecker.git
cd SYchecker
pip install -r requirements.txt
python sychecker.py
```

Or with a virtual environment (recommended):

```bash
git clone https://github.com/3og8/SYchecker.git
cd SYchecker
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
python sychecker.py
```

---

## What it does

- Detects CPU model, cores, threads, and architecture
- Shows RAM amount and basic info
- Runs quick single-core and multi-core CPU tests
- Rough memory bandwidth test
- Calculates an overall score (calibrated so high-end systems approach ~6000)
- Clean, readable terminal output

---

## Example output

```
SYchecker Results
─────────────────
CPU:        AMD Ryzen 9 7950X (16 cores / 32 threads)
RAM:        64 GB

Single-core :  2840
Multi-core  :  31250
Memory      :  4120

Overall Score:  5840   ← Top Tier
```

---

## Requirements

- Python 3.9+
- `psutil`, `py-cpuinfo`, `rich`

All dependencies are listed in `requirements.txt`.

---

## License

MIT
