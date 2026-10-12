"""Rebuild every notebook in notebooks/ from the content_XX.py files.

Run:  uv run python scripts/build_notebooks.py
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nbkit import write_notebook  # noqa: E402

CONTENT_MODULES = ["content_00", "content_01", "content_02", "content_03"]


def load_all():
    return [importlib.import_module(name) for name in CONTENT_MODULES]


if __name__ == "__main__":
    for module in load_all():
        path = write_notebook(module.FILENAME, module.CELLS)
        print(f"Wrote {path.name}")
