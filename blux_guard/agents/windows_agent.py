"""Windows agent for telemetry."""

from __future__ import annotations

import platform

from ..core import telemetry


class WindowsAgent:
    def collect(self) -> dict:
        data = {"platform": platform.platform()}
        telemetry.record_event("agent.windows", actor="agent", payload=data)
        telemetry.record_event("agent.windows", data)
        return data


def get_agent() -> WindowsAgent:
    return WindowsAgent()
