import re
import json
import os
import sys

def convert_md_to_ipynb(md_path, ipynb_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by python and bash code blocks
    pattern = re.compile(r'(```(?:python|bash|sh)?\n[\s\S]*?\n```)', re.MULTILINE)
    tokens = pattern.split(content)

    cells = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.startswith('```python'):
            code = token[len('```python'):-3].strip()
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code.splitlines(keepends=True)
            })
        elif token.startswith('```bash') or token.startswith('```sh'):
            # Convert bash commands to Jupyter/Colab shell commands with !
            code_lines = token[token.find('\n')+1:-3].strip().splitlines()
            colab_lines = []
            for line in code_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    colab_lines.append(f"!{stripped}\n")
                else:
                    colab_lines.append(f"{line}\n")
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": colab_lines
            })
        else:
            # Markdown block
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + '\n' for line in token.splitlines()]
            })

    notebook = {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python"
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    os.makedirs(os.path.dirname(ipynb_path), exist_ok=True)
    with open(ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    print(f"Successfully converted {md_path} -> {ipynb_path}")

if __name__ == '__main__':
    lessons_dir = "lessons"
    notebooks_dir = "notebooks"
    for fname in os.listdir(lessons_dir):
        if fname.endswith(".md"):
            in_file = os.path.join(lessons_dir, fname)
            out_file = os.path.join(notebooks_dir, fname.replace(".md", ".ipynb"))
            convert_md_to_ipynb(in_file, out_file)
