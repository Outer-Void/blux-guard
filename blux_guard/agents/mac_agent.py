"""macOS agent for system metrics."""

from __future__ import annotations

import subprocess

from ..core import telemetry


class MacAgent:
    def collect(self) -> dict:
        try:
            output = subprocess.check_output(["uptime"], text=True).strip()
        except Exception:
            output = "unavailable"
        data = {"uptime": output}
        telemetry.record_event("agent.mac", actor="agent", payload=data)
        telemetry.record_event("agent.mac", data)
        return data


def get_agent() -> MacAgent:
    return MacAgent()
