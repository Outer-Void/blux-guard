"""Developer workflow orchestration for the BLUX Guard suite."""

from __future__ import annotations

import asyncio
import pathlib

from . import telemetry


async def initialise_workspace(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    telemetry.record_event("dev.init", actor="devsuite", payload={"path": str(path)})


async def run_build() -> None:
    telemetry.record_event(
        "dev.build",
        actor="devsuite",
        payload={"phase": "start"},
    )
    await asyncio.sleep(0)
    telemetry.record_event(
        "dev.build",
        actor="devsuite",
        payload={"phase": "complete"},
    )


async def run_scan(target: pathlib.Path) -> None:
    telemetry.record_event(
        "dev.scan",
        actor="devsuite",
        payload={"target": str(target)},
    )
    await asyncio.sleep(0)


async def run_deploy(safe: bool = True) -> None:
    telemetry.record_event(
        "dev.deploy",
        actor="devsuite",
        payload={"safe": safe},
    )
    await asyncio.sleep(0)

