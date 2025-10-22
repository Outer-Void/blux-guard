#!/usr/bin/env python3
"""Generate a repository file tree without external dependencies."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
IGNORE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
    ".config",
    "dist",
    "build",
}


def build_tree(root: pathlib.Path, prefix: str = "") -> list[str]:
    entries: list[str] = []
    try:
        items = sorted(
            [p for p in root.iterdir() if p.name not in IGNORE],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
    except FileNotFoundError:
        return entries

    last_idx = len(items) - 1
    for idx, path in enumerate(items):
        tee = "└── " if idx == last_idx else "├── "
        entries.append(f"{prefix}{tee}{path.name}")
        if path.is_dir():
            extension = f"{prefix}{'    ' if idx == last_idx else '│   '}"
            entries.extend(build_tree(path, extension))
    return entries


def main() -> int:
    tree = [ROOT.name + "/"] + build_tree(ROOT)
    print("\n".join(tree))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
