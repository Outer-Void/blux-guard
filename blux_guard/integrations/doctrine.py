"""Doctrine policy integration stub."""

from __future__ import annotations

from typing import Dict, List

from ..core import telemetry


def fetch_policies() -> List[Dict[str, str]]:
    """Return loaded doctrine policies (placeholder implementation)."""

    telemetry.record_event("doctrine.fetch", actor="integration", payload={"status": "stub"})
    return [
        {"id": "default-observe", "status": "active", "description": "Observe-only fallback"}
    ]


def safe_mode_active() -> bool:
    """Return True when doctrine enforcement is unavailable."""

    policies = fetch_policies()
    return not policies
