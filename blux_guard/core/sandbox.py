"""Secure sandbox utilities for interactive sessions and subprocesses."""

from __future__ import annotations

import asyncio
import os
import platform
import shlex
from typing import Iterable, Optional

from . import telemetry

_DEFAULT_ENV_WHITELIST = {
    "TERM",
    "COLORTERM",
    "HOME",
    "PATH",
    "LANG",
}


def _base_shell() -> str:
    system = platform.system().lower()
    if "windows" in system:
        return os.environ.get("COMSPEC", "powershell")
    if "darwin" in system:
        return os.environ.get("SHELL", "/bin/zsh")
    return os.environ.get("SHELL", "/bin/bash")


async def launch_interactive_shell(command: Optional[str] = None) -> None:
    """Launch a sandboxed shell session using asyncio subprocess APIs."""

    shell = command or _base_shell()
    env = {k: v for k, v in os.environ.items() if k in _DEFAULT_ENV_WHITELIST}
    telemetry.record_event(
        "sandbox.shell",
        actor="sandbox",
        payload={"shell": shell, "mode": "interactive"},
        stream="devshell",
    )
    process = await asyncio.create_subprocess_exec(
        shell,
        stdin=None,
        stdout=None,
        stderr=None,
        env=env if env else None,
    )
    await process.wait()


async def run_command(command: Iterable[str] | str) -> int:
    """Run a command in the sandbox and return the exit status."""

    if isinstance(command, str):
        display = command
        args = shlex.split(command)
    else:
        args = list(command)
        display = " ".join(args)
    telemetry.record_event(
        "sandbox.exec",
        actor="sandbox",
        payload={"command": display},
        stream="devshell",
    )
    process = await asyncio.create_subprocess_exec(*args)
    return await process.wait()
