"""Developer workflow orchestration for the BLUX Guard suite."""

from __future__ import annotations

import asyncio
import pathlib
from typing import Iterable

from . import doctrine_integration, sandbox, telemetry


async def initialise_workspace(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    telemetry.record_event("dev.init", actor="devsuite", payload={"path": str(path)})
    telemetry.record_event("dev.init", {"path": str(path)})
    doctrine_integration.ensure_doctrine_loaded()


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
    telemetry.record_event("dev.build", {"phase": "start"})
    await asyncio.sleep(0)
    telemetry.record_event("dev.build", {"phase": "complete"})


async def run_scan(target: pathlib.Path) -> None:
    telemetry.record_event("dev.scan", {"target": str(target)})
    await asyncio.sleep(0)


async def run_deploy(safe: bool = True) -> None:
    telemetry.record_event(
        "dev.deploy",
        actor="devsuite",
        payload={"safe": safe},
    )
    telemetry.record_event("dev.deploy", {"safe": safe})
    await asyncio.sleep(0)


async def run_doctrine_check(check: bool = True) -> None:
    telemetry.record_event(
        "dev.doctrine",
        actor="devsuite",
        payload={"check": check},
    )
    telemetry.record_event("dev.doctrine", {"check": check})
    if check:
        doctrine_integration.ensure_doctrine_loaded()
        await asyncio.sleep(0)


async def run_guarded_command(command: Iterable[str] | str) -> int:
    return await sandbox.run_command(command)
