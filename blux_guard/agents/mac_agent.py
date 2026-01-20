"""macOS agent for system metrics."""

from __future__ import annotations

from ..core import telemetry


class MacAgent:
    def collect(self) -> dict:
        data = {"uptime": "unavailable"}
        telemetry.record_event("agent.mac", actor="agent", payload=data)
        return data


def get_agent() -> MacAgent:
    return MacAgent()
