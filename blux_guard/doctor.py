"""Environment checks for BLUX Guard."""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Dict, List

from . import audit
from .config import default_paths
from .core import telemetry


def _check_python() -> Dict[str, str]:
    version = sys.version.split()[0]
    ok = sys.version_info >= (3, 9)
    return {"name": "python", "status": "ok" if ok else "warn", "detail": version}


def _check_textual() -> Dict[str, str]:
    try:
        import textual  # noqa: F401

        return {"name": "textual", "status": "ok", "detail": "installed"}
    except Exception:
        return {"name": "textual", "status": "warn", "detail": "missing"}


def _check_typer() -> Dict[str, str]:
    try:
        import typer  # noqa: F401

        return {"name": "typer", "status": "ok", "detail": "installed"}
    except Exception:
        return {"name": "typer", "status": "warn", "detail": "missing"}


def _check_log_dir() -> Dict[str, str]:
    paths = default_paths()
    log_dir = paths["log_dir"]
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        return {"name": "log_dir", "status": "ok", "detail": log_dir}
    except Exception as exc:
        return {"name": "log_dir", "status": "warn", "detail": str(exc)}


def run_doctor() -> Dict[str, List[Dict[str, str]]]:
    checks = [_check_python(), _check_textual(), _check_typer(), _check_log_dir()]
    overall = "ok" if all(item["status"] == "ok" for item in checks) else "warn"
    telemetry.record_event("doctor.run", actor="cli", payload={"overall": overall})
    audit.record("cli.doctor", actor="cli", payload={"overall": overall})
    return {"overall": overall, "checks": checks, "platform": platform.platform()}


def run_verify() -> Dict[str, str]:
    paths = default_paths()
    writable = telemetry.ensure_log_dir()
    status = "ok" if writable else "warn"
    telemetry.record_event("verify.run", actor="cli", payload={"status": status})
    audit.record("cli.verify", actor="cli", payload={"status": status, "paths": paths})
    return {"status": status, "audit_log": paths["audit_log"]}
