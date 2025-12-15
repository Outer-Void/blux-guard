"""Configuration helpers for BLUX Guard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

_BASE_DIR = Path(os.environ.get("BLUX_GUARD_CONFIG_DIR", Path.home() / ".config" / "blux-guard"))
_LOG_DIR = Path(os.environ.get("BLUX_GUARD_LOG_DIR", _BASE_DIR / "logs"))


def config_dir() -> Path:
    """Return the root configuration directory."""

    return _BASE_DIR


def log_dir() -> Path:
    """Return the log directory path."""

    return _LOG_DIR


def default_paths() -> Dict[str, str]:
    """Expose standard paths for docs and CLIs."""

    return {
        "config_dir": str(config_dir()),
        "log_dir": str(log_dir()),
        "audit_log": str(log_dir() / "audit.jsonl"),
        "devshell_log": str(log_dir() / "devshell.jsonl"),
        "sqlite_db": str(log_dir() / "telemetry.db"),
    }
