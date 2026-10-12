"""Check that every exercise is solvable and every assert cell passes.

Learner notebooks contain blanks (___), so this script builds the solved version
of each notebook and runs all code cells in order, with notebooks/ as the working
directory (the way Jupyter runs them). Cells with IPython syntax (%magic, ?) are
marked validate_skip and ignored.

Run:  uv run python scripts/validate_notebooks.py
"""

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_notebooks import load_all  # noqa: E402
from nbkit import NOTEBOOK_DIR, to_notebook  # noqa: E402


def main():
    os.chdir(NOTEBOOK_DIR)
    failures = 0
    for module in load_all():
        nb = to_notebook(module.CELLS, mode="solution")
        env = {"display": print}
        n_code = 0
        for i, cell in enumerate(nb["cells"]):
            if cell["cell_type"] != "code" or cell["metadata"].get("validate_skip"):
                continue
            n_code += 1
            src = "".join(cell["source"])
            try:
                exec(compile(src, f"{module.FILENAME}[cell {i}]", "exec"), env)
            except Exception:
                failures += 1
                print(f"[FAIL] {module.FILENAME}, cell {i}")
                traceback.print_exc()
                print("Mã của ô:\n" + src)
                break
        else:
            print(f"[OK] {module.FILENAME}: {n_code} code cells ran successfully")
    if failures:
        sys.exit(1)
    print("[OK] All notebooks ran cleanly and every assert passed.")


if __name__ == "__main__":
    main()
