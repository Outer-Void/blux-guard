"""Daemon process that starts the FastAPI server and polls agents."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Callable

import uvicorn

from ..agents import common, linux_agent, mac_agent, termux_agent, windows_agent
from ..core import runtime, telemetry
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
            telemetry.record_event(
                "daemon.poll",
                actor="daemon",
                payload=getattr(agent, "collect")(),
            )
        await asyncio.sleep(30)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose telemetry")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args(argv)


def start() -> None:
    """Entry point for the ``bluxqd`` console script."""

    args = _parse_args(sys.argv[1:])
    runtime.set_debug(args.debug)
    runtime.set_verbose(args.verbose)
    telemetry.set_debug(args.debug)
    telemetry.set_verbose(args.verbose)

    runtime.ensure_supported_python("bluxqd")
    if not telemetry.ensure_log_dir():
        telemetry.record_event(
            "startup.degrade",
            level="warn",
            actor="daemon",
            payload={"component": "bluxqd", "reason": "log_dir_unavailable"},
        )

    telemetry.record_event("daemon.start", actor="daemon", payload={})

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner() -> None:
        poller = loop.create_task(_poll_agents())
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            log_level="debug" if args.debug else "info",
        )
        server = uvicorn.Server(config)
        await server.serve()
        poller.cancel()

    try:
        loop.run_until_complete(runner())
    finally:
        loop.close()
