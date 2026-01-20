"""Self-check routines for the BLUX Guard runtime."""

from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, List

from . import telemetry


def _check_config_files() -> Dict[str, str]:
    config_dir = Path(__file__).resolve().parents[1] / "config"
    default = config_dir / "default.yaml"
    local = config_dir / "local.yaml"
    if default.exists():
        detail = "default.yaml present"
        status = "ok"
    else:
        detail = "default.yaml missing"
        status = "fail"
    if not local.exists():
        detail += "; local.yaml optional"
    return {"name": "config.files", "status": status, "detail": detail}


def _check_log_writable() -> Dict[str, str]:
    if not telemetry.ensure_log_dir():
        return {
            "name": "logs.directory",
            "status": "warn",
            "detail": f"unable to create {telemetry.collect_status_sync()['log_dir']}",
        }
    status = telemetry.collect_status_sync()
    path = Path(status["log_dir"])
    test_file = path / ".write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return {
            "name": "logs.directory",
            "status": "ok",
            "detail": f"writable {path}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "name": "logs.directory",
            "status": "warn",
            "detail": f"write failed: {exc}",
        }


def _check_sqlite() -> Dict[str, str]:
    status = telemetry.collect_status_sync()
    db_path = Path(status["sqlite_db"])
    try:
        telemetry.ensure_log_dir()
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.close()
        return {"name": "sqlite.telemetry", "status": "ok", "detail": str(db_path)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"name": "sqlite.telemetry", "status": "warn", "detail": str(exc)}


async def _check_api() -> Dict[str, str]:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, lambda: None)
        _reader, writer = await asyncio.open_connection("127.0.0.1", 8000)
        writer.close()
        await writer.wait_closed()
        return {"name": "api.endpoint", "status": "ok", "detail": "localhost:8000 reachable"}
    except OSError:
        return {
            "name": "api.endpoint",
            "status": "warn",
            "detail": "daemon not reachable on 127.0.0.1:8000",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {"name": "api.endpoint", "status": "warn", "detail": str(exc)}


def _aggregate_status(checks: List[Dict[str, str]]) -> str:
    precedence = {"fail": 2, "warn": 1, "ok": 0}
    score = max(precedence.get(check["status"], 1) for check in checks)
    for state, value in precedence.items():
        if value == score:
            return state
    return "warn"


async def run_self_check() -> Dict[str, object]:
    """Run all checks and return a structured report."""

    results: List[Dict[str, str]] = []
    results.append(_check_config_files())
    results.append(_check_log_writable())
    results.append(_check_sqlite())
    results.append(await _check_api())

    overall = _aggregate_status(results)
    telemetry.record_event(
        "selfcheck.complete",
        actor="cli",
        payload={"overall": overall, "checks": results},
    )
    return {"checks": results, "overall": overall}
