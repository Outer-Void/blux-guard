"""Telemetry, auditing, and metrics aggregation utilities."""

from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, Optional

# Resolve the telemetry directory, allowing overrides for testing or custom deployments.
_LOG_DIR = Path(
    os.environ.get("BLUX_GUARD_LOG_DIR", Path.home() / ".config" / "blux-guard" / "logs")
)
_JSONL = _LOG_DIR / "audit.jsonl"
_DB = _LOG_DIR / "telemetry.db"

_warned_once: Dict[str, bool] = {"json": False, "sqlite": False, "dir": False}
_lock = threading.Lock()
_DEBUG = False
_VERBOSE = False


def _telemetry_enabled() -> bool:
    """Return True when telemetry sinks should be active."""

    return os.getenv("BLUX_GUARD_TELEMETRY", "on").lower() not in {
        "0",
        "off",
        "false",
        "no",
    }


def _warn_once(channel: str, message: str) -> None:
    """Emit a single degrade warning to stderr per channel."""

    if os.getenv("BLUX_GUARD_TELEMETRY_WARN", "once").lower() != "once":
        return

    if not _warned_once.get(channel):
        _warned_once[channel] = True
        print(f"[blux-guard] telemetry degrade: {message}", file=sys.stderr)


def _ensure_dirs() -> bool:
    """Create the telemetry directory if possible."""

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("dir", f"cannot create log dir {_LOG_DIR}: {exc}")
        return False


def ensure_log_dir() -> bool:
    """Public helper to prepare the telemetry directory."""

    return _ensure_dirs()


def set_debug(enabled: bool) -> None:
    """Enable or disable debug mode for telemetry outputs."""

    global _DEBUG
    _DEBUG = enabled


def set_verbose(enabled: bool) -> None:
    """Enable or disable verbose mode for telemetry outputs."""

    global _VERBOSE
    _VERBOSE = enabled


def debug_enabled() -> bool:
    return _DEBUG


def verbose_enabled() -> bool:
    return _VERBOSE


def _safe_jsonl_write(path: Path, obj: Dict[str, Any]) -> None:
    try:
        with _lock:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("json", f"jsonl write failed ({path}): {exc}")


def _safe_sqlite_write(table: str, obj: Dict[str, Any]) -> None:
    try:
        with _lock:
            conn = sqlite3.connect(_DB)
            try:
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        ts REAL,
                        level TEXT,
                        actor TEXT,
                        action TEXT,
                        stream TEXT,
                        payload TEXT
                    )
                    """
                )
                conn.execute(
                    f"""
                    INSERT INTO {table} (ts, level, actor, action, stream, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        obj.get("ts"),
                        obj.get("level"),
                        obj.get("actor"),
                        obj.get("action"),
                        obj.get("stream"),
                        json.dumps(obj.get("payload", {}), ensure_ascii=False),
                    ),
                )
                conn.commit()
            finally:
                conn.close()
    except Exception as exc:  # pragma: no cover - defensive
        _warn_once("sqlite", f"sqlite write failed ({_DB}): {exc}")


def record_event(
    action: str,
    level: str = "info",
    actor: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    *,
    stream: str = "audit",
) -> None:
    """Best-effort event recorder that never raises."""

    if not _telemetry_enabled():
        return

    stream = "audit"
    payload = payload or {}
    ensure_log_dir()

    obj = {
        "ts": time.time(),
        "level": level,
        "actor": actor or "local",
        "action": action,
        "payload": payload,
        "stream": stream,
        "channel": action,
    }

    _safe_jsonl_write(_JSONL, obj)
    _safe_sqlite_write("events", obj)

    if _DEBUG or _VERBOSE:
        preview = json.dumps(obj, ensure_ascii=False, sort_keys=True)
        print(f"[telemetry] {preview}", file=sys.stderr)


async def collect_status() -> Dict[str, Any]:
    """Return a simplified status snapshot for guard reporting."""

    ensure_log_dir()
    return {
        "log_dir": str(_LOG_DIR),
        "audit_log": str(_JSONL),
        "sqlite_db": str(_DB),
        "telemetry_enabled": _telemetry_enabled(),
        "debug": _DEBUG,
        "verbose": _VERBOSE,
    }


def collect_status_sync() -> Dict[str, Any]:
    """Synchronous wrapper over :func:`collect_status`."""

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(collect_status())
    finally:
        loop.close()


@dataclass
class Metric:
    """Container for Prometheus-style metrics."""

    name: str
    value: float
    description: str = ""

    def to_prometheus(self) -> str:
        header = f"# HELP {self.name} {self.description}" if self.description else ""
        type_line = f"# TYPE {self.name} gauge"
        return "\n".join(filter(None, [header, type_line, f"{self.name} {self.value}"]))


async def iter_prometheus_metrics() -> AsyncIterator[str]:
    """Yield Prometheus metric strings asynchronously."""

    metrics = [
        Metric(
            name="blux_guard_heartbeat",
            value=time.time(),
            description="Wall clock timestamp",
        ),
    ]
    for metric in metrics:
        yield metric.to_prometheus()
        await asyncio.sleep(0)


def export_prometheus() -> str:
    """Return metrics in Prometheus exposition format."""

    loop = asyncio.get_event_loop()
    if loop.is_running():
        raise RuntimeError("export_prometheus must not be called from a running loop")

    metrics: list[str] = []

    async def _collect() -> None:
        async for chunk in iter_prometheus_metrics():
            metrics.append(chunk)

    loop.run_until_complete(_collect())
    return "\n".join(metrics)


@contextmanager
def scoped_event(action: str, **payload: Any) -> Iterable[None]:
    """Context manager that automatically records start/stop events."""

    start_payload = {**payload, "phase": "start"}
    record_event(action, payload=start_payload)
    try:
        yield
    finally:
        end_payload = {**payload, "phase": "end"}
        record_event(action, payload=end_payload)
