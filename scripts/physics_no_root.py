#!/usr/bin/env python3
"""Physics check: enforce userland-only constraints and schema receipts."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ALLOW_PHRASES = (
    "no root required",
    "root not required",
    "does not require root",
    "without root",
    "no sudo",
    "without sudo",
    "does not require sudo",
    "non-root",
    "non root",
)

ROOT_REQUIREMENT_PATTERNS = (
    r"\broot required\b",
    r"\brequires root\b",
    r"\bmust be root\b",
    r"\brun as root\b",
    r"\bneed root\b",
    r"\bneeds root\b",
    r"\broot privileges\b",
    r"\broot access\b",
    r"\broot-only\b",
)

PROHIBITED_WORD_PATTERNS = (
    r"\bsudo\b",
    r"\bdoas\b",
    r"\bpkexec\b",
    r"\bsetuid\b",
    r"\bcap_sys_admin\b",
    r"chmod\s+4755",
    r"\bchown\s+root\b",
)


def _git_files() -> list[str]:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    return [line.strip() for line in output.splitlines() if line.strip()]


def _is_allowed_line(line: str) -> bool:
    lowered = line.lower()
    return any(phrase in lowered for phrase in ALLOW_PHRASES)


def _scan_text(path: Path, text: str) -> list[str]:
    violations: list[str] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if _is_allowed_line(line):
            continue
        lowered = line.lower()
        for pattern in ROOT_REQUIREMENT_PATTERNS:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                violations.append(f"{path}:{idx}: root requirement: {line.strip()}")
                break
        for pattern in PROHIBITED_WORD_PATTERNS:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                violations.append(f"{path}:{idx}: prohibited root tooling: {line.strip()}")
                break
    return violations


def _scan_docs_and_scripts(repo_root: Path) -> list[str]:
    violations: list[str] = []
    for rel in _git_files():
        path = Path(rel)
        if path.name == "physics_no_root.py":
            continue
        if path.suffix.lower() == ".md" or path.parts[:1] == ("scripts",):
            content = (repo_root / path).read_text(encoding="utf-8")
            violations.extend(_scan_text(path, content))
    return violations


def _validate_example_receipt(repo_root: Path) -> list[str]:
    example_path = repo_root / "examples" / "guard_receipt.example.json"
    if not example_path.exists():
        return []
    if importlib.util.find_spec("jsonschema") is None:
        return []
    from jsonschema import Draft202012Validator

    schema_path = repo_root / "blux_guard" / "contracts" / "phase0" / "guard_receipt.schema.json"
    payload = json.loads(example_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    return [
        f"{example_path}:{'/'.join([str(p) for p in err.path])}:{err.message}"
        for err in errors
    ]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    violations = _scan_docs_and_scripts(repo_root)
    violations.extend(_validate_example_receipt(repo_root))
    if violations:
        print("Blocked: userland-only enforcement violations detected")
        for violation in violations:
            print(f"- {violation}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
