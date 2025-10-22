#!/usr/bin/env python3
"""Update the README with a generated repository file tree."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BEGIN = "<!-- FILETREE:BEGIN -->"
END = "<!-- FILETREE:END -->"


def generate_tree() -> str:
    output = subprocess.check_output([sys.executable, str(ROOT / "scripts" / "gen_filetree.py")], text=True)
    return output.strip()


def build_block(tree: str) -> str:
    return (
        f"{BEGIN}\n"
        "<!-- generated; do not edit manually -->\n"
        "<details><summary><strong>Repository File Tree</strong> (click to expand)</summary>\n\n"
        f"```text\n{tree}\n```\n"
        "</details>\n"
        f"{END}\n"
    )


def update_readme(tree: str) -> None:
    block = build_block(tree)
    if README.exists():
        text = README.read_text(encoding="utf-8")
    else:
        text = "# BLUX Guard\n\n"

    pattern = re.compile(rf"{BEGIN}.*?{END}", re.S)
    if pattern.search(text):
        updated = pattern.sub(block, text)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"

    README.write_text(updated, encoding="utf-8")


def main() -> int:
    tree = generate_tree()
    update_readme(tree)
    print("README file tree updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
