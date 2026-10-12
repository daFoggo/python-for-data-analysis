# Python for Data Analysis: Applied Engineering Edition

An applied, interactive curriculum based on the core principles of Wes McKinney's *Python for Data Analysis (3rd Edition)*, grounded in real-world **Building Sensor Telemetry & IoT Time Series** (Building Data Genome 2).

Every session is designed as a self-contained Jupyter Notebook (`.ipynb`) with natural narrative explanations, runnable code, automated self-checking assertions, and practical engineering challenges.

---

## 🚀 Quick Start

This project uses [**`uv`**](https://github.com/astral-sh/uv) for ultra-fast, zero-friction Python dependency management (Python 3.12+, NumPy 2.x, pandas 3.0+, pyarrow, JupyterLab).

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/daFoggo/python-for-data-analysis.git
cd python-for-data-analysis

# Sync virtual environment automatically
uv sync
```

### 2. Launch Jupyter Lab
Launch Jupyter Lab directly in your browser:
```bash
uv run jupyter lab
```
*(Or open the repository in VS Code and select the `.venv` Python environment as your Jupyter kernel).*

---

## 📚 Curriculum Structure

| Session | Topic | Focus |
|---|---|---|
| **[Roadmap](./notebooks/00_roadmap_and_orientation.ipynb)** | Course Orientation & Schedule | 14-session core plan, dataset overview, progress tracker |
| **[Session 01](./notebooks/session_01_environment_ipython.ipynb)** | Modern Environment & Fast Execution | C-buffers vs Python lists, vectorization speedup, IPython introspection |
| **[Session 02](./notebooks/session_02_numpy_arrays.ipynb)** | Multi-Channel Signals & NumPy ndarrays | Shapes, memory optimization with `float32`/`int16`, multi-channel broadcasting |
| **[Session 03](./notebooks/session_03_numpy_filtering.ipynb)** | Boolean Masking, Views vs Copies & Signal Filtering | Telemetry conditioning, `np.where`, `np.clip`, memory safety with `.copy()` |
| **Session 04 – 14** | Upcoming Modules | pandas Series/DataFrames, chunked Parquet loading, time series resampling, and energy audit capstone |

---

## 📊 Dataset: Building Data Genome 2 (Sample)

Located in `data/`:
- `building_metadata.csv`: 10 buildings across 3 regional sites with floor areas and usage types.
- `weather.parquet`: 26,280 hourly weather observations (temperature, humidity, dew point, wind speed).
- `building_telemetry.parquet`: 87,600 hourly electrical power readings (kW) reflecting seasonal and occupancy profiles.

To regenerate sample data:
```bash
uv run python scripts/prepare_sample_data.py
```

---

## 🧪 Automated Notebook Validation

Verify that all notebooks and assertions execute with zero errors:
```bash
uv run python scripts/validate_notebooks.py
```
