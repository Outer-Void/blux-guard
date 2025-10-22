"""Telemetry collection for Termux environments."""

from __future__ import annotations

import shutil
from typing import Dict

from . import common
from ..core import telemetry


class TermuxAgent:
    def collect(self) -> Dict[str, str]:
        data = {
            "storage": shutil.disk_usage("/").free // (1024 * 1024),
        }
        telemetry.record_event("agent.termux", data)
        return data


def get_agent() -> TermuxAgent:
    return TermuxAgent()
