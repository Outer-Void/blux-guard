"""Physics checks for guard-only posture."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}

CODE_SUFFIXES = {".py", ".sh"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}

EXEC_PATTERNS = [
    re.compile(r"\bsubprocess\b"),
    re.compile(r"os\.system"),
    re.compile(r"\bexec\("),
    re.compile(r"create_subprocess"),
    re.compile(r"\bshell\b"),
]

PRIV_PATTERNS = [
    re.compile(r"\bsudo\b", re.IGNORECASE),
    re.compile(r"\broot required\b", re.IGNORECASE),
    re.compile(r"\brequires root\b", re.IGNORECASE),
    re.compile(r"\brun as root\b", re.IGNORECASE),
    re.compile(r"\broot-only\b", re.IGNORECASE),
    re.compile(r"\bprivileged escalation\b", re.IGNORECASE),
]

TOKEN_PATTERNS = [
    re.compile(r"\bverify_tokens?\b"),
    re.compile(r"\bissue_token\b"),
    re.compile(r"\bmint_token\b"),
]

DOCTRINE_PATTERNS = [
    re.compile(r"\bdoctrine\b", re.IGNORECASE),
    re.compile(r"policy engine", re.IGNORECASE),
]

CONTRACT_PATTERNS = [
    re.compile(r"canonical contract", re.IGNORECASE),
    re.compile(r"canonical contracts", re.IGNORECASE),
]


def _iter_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        paths.append(path)
    return paths


def _scan_file(path: Path) -> list[str]:
    violations: list[str] = []
    if path.resolve() == Path(__file__).resolve():
        return violations
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    suffix = path.suffix.lower()
    if suffix in CODE_SUFFIXES:
        for pattern in EXEC_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in TOKEN_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in DOCTRINE_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")

    if suffix in TEXT_SUFFIXES:
        for pattern in PRIV_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")
        for pattern in CONTRACT_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path}:{pattern.pattern}")

    return violations


def main() -> int:
    violations: list[str] = []
    for path in _iter_files(ROOT):
        violations.extend(_scan_file(path))
    if violations:
        print("Physics check failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
