"""Telemetry, auditing, and metrics aggregation utilities."""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Iterable

_LOG_BASE = pathlib.Path(os.environ.get("BLUX_GUARD_LOG_DIR", pathlib.Path.home() / ".config" / "blux-guard" / "logs"))
_AUDIT_LOG = _LOG_BASE / "audit.jsonl"
_DEVSHELL_LOG = _LOG_BASE / "devshell.jsonl"
_SQLITE_DB = _LOG_BASE / "telemetry.sqlite3"


def _ensure_dirs() -> None:
    _LOG_BASE.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: pathlib.Path, payload: Dict[str, Any]) -> None:
    _ensure_dirs()
    line = json.dumps(payload, sort_keys=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _ensure_sqlite() -> None:
    _ensure_dirs()
    with sqlite3.connect(_SQLITE_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                ts REAL NOT NULL,
                channel TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.commit()


def record_event(channel: str, payload: Dict[str, Any]) -> None:
    """Persist a telemetry event across JSONL and SQLite sinks."""

    timestamp = time.time()
    body = {"ts": timestamp, "channel": channel, **payload}
    _append_jsonl(_AUDIT_LOG if channel.startswith("audit") else _DEVSHELL_LOG, body)
    _ensure_sqlite()
    with sqlite3.connect(_SQLITE_DB) as conn:
        conn.execute(
            "INSERT INTO events (ts, channel, payload) VALUES (?, ?, ?)",
            (timestamp, channel, json.dumps(payload, sort_keys=True)),
        )
        conn.commit()


async def collect_status() -> Dict[str, Any]:
    """Return a simplified status snapshot for CLI consumption."""

    _ensure_dirs()
    return {
        "log_dir": str(_LOG_BASE),
        "audit_log": str(_AUDIT_LOG),
        "devshell_log": str(_DEVSHELL_LOG),
        "sqlite_db": str(_SQLITE_DB),
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
        Metric(name="blux_guard_heartbeat", value=time.time(), description="Wall clock timestamp"),
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
def scoped_event(channel: str, **payload: Any) -> Iterable[None]:
    """Context manager that automatically records start/stop events."""

    start_payload = {**payload, "phase": "start"}
    record_event(channel, start_payload)
    try:
        yield
    finally:
        end_payload = {**payload, "phase": "end"}
        record_event(channel, end_payload)
