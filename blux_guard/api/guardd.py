"""Daemon process that starts the FastAPI server and polls agents."""

from __future__ import annotations

import asyncio
from typing import Callable

import uvicorn

from ..agents import common, linux_agent, mac_agent, termux_agent, windows_agent
from ..core import telemetry
from .server import app

_AGENT_MAP = {
    "linux": linux_agent.get_agent,
    "mac": mac_agent.get_agent,
    "windows": windows_agent.get_agent,
    "termux": termux_agent.get_agent,
}


async def _poll_agents() -> None:
    info = common.detect_agent()
    factory: Callable[[], object] | None = _AGENT_MAP.get(info.name)
    agent = factory() if factory else None
    while True:
        if agent and hasattr(agent, "collect"):
            telemetry.record_event("daemon.poll", getattr(agent, "collect")())
        await asyncio.sleep(30)


def start() -> None:
    """Entry point for the ``bluxqd`` console script."""

    telemetry.record_event("daemon.start", {})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner() -> None:
        poller = loop.create_task(_poll_agents())
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        poller.cancel()

    try:
        loop.run_until_complete(runner())
    finally:
        loop.close()
