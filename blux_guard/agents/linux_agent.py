"""Linux agent for system metrics."""

from __future__ import annotations

import os

from ..core import telemetry


class LinuxAgent:
    def collect(self) -> dict:
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
        data = {
            "load": load,
        }
        telemetry.record_event("agent.linux", actor="agent", payload=data)
        return data


def get_agent() -> LinuxAgent:
    return LinuxAgent()
