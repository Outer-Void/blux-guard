#!/usr/bin/env python3
"""Audit repository scripts for shebangs, CRLF, and permissions."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "scripts" / "perms_manifest.txt"


def load_manifest() -> List[Path]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST}")

    entries: List[Path] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        entries.append((REPO_ROOT / stripped).resolve())
    return entries


def read_shebang(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            first_line = handle.readline().rstrip("\n")
    except OSError:
        return ""
    return first_line


def has_crlf(path: Path) -> bool:
    try:
        sample = path.read_bytes()
    except OSError:
        return False
    return b"\r\n" in sample


def is_executable(path: Path) -> bool:
    mode = path.stat().st_mode
    return bool(mode & stat.S_IXUSR)


def collect_shebang_files() -> Iterable[Path]:
    for path in REPO_ROOT.rglob("*.sh"):
        yield path
    for path in REPO_ROOT.rglob("*.py"):
        # Only treat as script if the file declares a shebang
        if read_shebang(path).startswith("#!"):
            yield path


def audit() -> Tuple[List[str], int]:
    issues: List[str] = []
    manifest_entries = load_manifest()
    manifest_set = set(manifest_entries)

    for entry in manifest_entries:
        if not entry.exists():
            issues.append(f"Missing manifest entry: {entry.relative_to(REPO_ROOT)}")
            continue
        if not is_executable(entry):
            issues.append(
                f"Not executable (manifest): {entry.relative_to(REPO_ROOT)}"
            )

    for path in collect_shebang_files():
        shebang = read_shebang(path)
        rel_path = path.relative_to(REPO_ROOT)

        if not shebang.startswith("#!"):
            issues.append(f"Missing shebang: {rel_path}")
        if "/bin/bash" in shebang:
            issues.append(f"Hardcoded bash path: {rel_path}")
        if "python" in shebang and "python3" not in shebang:
            issues.append(f"Non-python3 shebang: {rel_path}")
        if has_crlf(path):
            issues.append(f"CRLF line endings: {rel_path}")
        if path in manifest_set:
            continue
        if shebang.startswith("#!") and is_executable(path):
            issues.append(f"Executable not in manifest: {rel_path}")

    return issues, len(manifest_entries)


def main() -> int:
    try:
        issues, manifest_count = audit()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1

    print(f"Checked {manifest_count} manifest entries.")
    if issues:
        print("Issues detected:")
        for problem in issues:
            print(f" - {problem}")
        return 1

    print("No script issues detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
