"""Common utilities for host agents."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Protocol


class Agent(Protocol):
    def collect(self) -> dict:
        ...


@dataclass
class AgentInfo:
    name: str
    platform: str


def detect_agent() -> AgentInfo:
    system = platform.system().lower()
    if "linux" in system:
        name = "linux"
    elif "darwin" in system:
        name = "mac"
    elif "windows" in system:
        name = "windows"
    else:
        name = "termux" if "android" in system else "unknown"
    return AgentInfo(name=name, platform=system)
