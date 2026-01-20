"""Unified audit writer for BLUX Guard."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .core import telemetry


def generate_correlation_id() -> str:
    """Return a correlation id (UUID4) with optional override from env."""

    return os.environ.get("BLUX_GUARD_CORRELATION_ID", str(uuid.uuid4()))


def audit_log_path() -> Path:
    """Return the resolved audit log path."""

    status = telemetry.collect_status_sync()
    return Path(status["audit_log"])




@dataclass
class AuditEvent:
    action: str
    level: str = "info"
    actor: str = "local"
    stream: str = "audit"
    payload: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    component: Optional[str] = None

    def as_payload(self) -> Dict[str, Any]:
        merged = dict(self.payload or {})
        if self.correlation_id:
            merged.setdefault("correlation_id", self.correlation_id)
        if self.component:
            merged.setdefault("component", self.component)
        return merged


def record(
    action: str,
    *,
    level: str = "info",
    actor: str = "local",
    stream: str = "audit",
    payload: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    component: Optional[str] = None,
) -> str:
    """Write an audit record and return the correlation id used."""

    cid = correlation_id or generate_correlation_id()
    event = AuditEvent(
        action=action,
        level=level,
        actor=actor,
        stream=stream,
        payload=payload,
        correlation_id=cid,
        component=component,
    )
    telemetry.record_event(
        event.action,
        level=event.level,
        actor=event.actor,
        payload=event.as_payload(),
        stream=event.stream,
    )
    return cid

