"""Small toolkit for building notebooks from content written in Python.

Each cell is a dict:
  md      : markdown cell
  code    : code cell that runs as-is (demos, assert checks)
  ex      : exercise cell. The learner notebook gets `skeleton` (blanks ___ or an
            empty cell); `solution` is only used by validate_notebooks.py to
            confirm the exercise can actually be solved.
"""

import json
import uuid
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def md(text):
    return {"kind": "md", "src": text.strip("\n")}


def code(src, skip=False):
    """Demo code cell. skip=True for cells using IPython syntax (%magic, ?) or meant to fail."""
    return {"kind": "code", "src": src.strip("\n"), "skip": skip}


def ex(skeleton, solution):
    return {
        "kind": "ex",
        "skeleton": skeleton.strip("\n"),
        "solution": solution.strip("\n"),
    }


def details(summary, body):
    """Collapsible answer block (markdown/HTML that works in Jupyter)."""
    return md(f"<details>\n<summary><b>{summary}</b></summary>\n\n{body.strip()}\n\n</details>")


def _cell_id():
    return uuid.uuid4().hex[:8]


def to_notebook(cells, mode="learner"):
    """mode='learner' -> exercise cells are skeletons; mode='solution' -> solutions."""
    out = []
    for c in cells:
        if c["kind"] == "md":
            out.append({"cell_type": "markdown", "id": _cell_id(), "metadata": {},
                        "source": c["src"].splitlines(keepends=True)})
        else:
            if c["kind"] == "ex":
                src = c["solution"] if mode == "solution" else c["skeleton"]
                skip = False
            else:
                src, skip = c["src"], c.get("skip", False)
            meta = {"validate_skip": True} if skip else {}
            out.append({"cell_type": "code", "id": _cell_id(), "metadata": meta,
                        "execution_count": None, "outputs": [],
                        "source": src.splitlines(keepends=True)})
    return {
        "cells": out,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(filename, cells):
    NOTEBOOK_DIR.mkdir(exist_ok=True)
    path = NOTEBOOK_DIR / filename
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(to_notebook(cells), f, indent=1, ensure_ascii=False)
        f.write("\n")
    return path
