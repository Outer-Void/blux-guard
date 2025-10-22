"""Entry point for the BLUX Guard Developer Suite CLI."""

from __future__ import annotations

import asyncio
import json
import pathlib
from typing import Optional

import typer

try:
    from blux_cli import blux as legacy_cli
except Exception:  # pragma: no cover - defensive import guard
    legacy_cli = None

from blux_guard.core import devsuite, sandbox, telemetry
from blux_guard.tui import dashboard

app = typer.Typer(help="BLUX Guard Developer Suite (Quantum namespace)")

guard_app = typer.Typer(help="Guard management commands")

dev_app = typer.Typer(help="Developer workflow commands")


@app.callback()
def main() -> None:
    """Root CLI callback.

    The callback is intentionally empty so Typer can manage sub-commands.
    """

    if not telemetry.ensure_log_dir():
        telemetry.record_event(
            "startup.degrade",
            level="warn",
            actor="cli",
            payload={"component": "bluxq", "reason": "log_dir_unavailable"},
        )


def _ensure_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


@guard_app.command("status")
def guard_status() -> None:
    """Print a high level status report for the guard runtime."""

    loop = _ensure_event_loop()
    status = loop.run_until_complete(telemetry.collect_status())
    typer.echo(json.dumps(status, indent=2, sort_keys=True))


@guard_app.command("tui")
def guard_tui(mode: str = typer.Option("secure", help="TUI mode: dev|secure|ops")) -> None:
    """Launch the Textual cockpit."""

    loop = _ensure_event_loop()
    loop.run_until_complete(dashboard.run_dashboard(mode=mode))


@app.command("legacy")
def legacy_passthrough(args: Optional[list[str]] = typer.Argument(None)) -> None:
    """Pass through to the legacy CLI for compatibility."""

    if legacy_cli is None:
        raise typer.Exit(code=1)
    legacy_cli.app(args=args or [])


@dev_app.command("init")
def dev_init(path: pathlib.Path = typer.Argument(pathlib.Path.cwd(), help="Project root")) -> None:
    """Initialise a secure workspace."""

    loop = _ensure_event_loop()
    loop.run_until_complete(devsuite.initialise_workspace(path))
    typer.echo(f"Workspace initialised at {path}")


@dev_app.command("shell")
def dev_shell() -> None:
    """Launch an interactive sandboxed shell."""

    loop = _ensure_event_loop()
    loop.run_until_complete(sandbox.launch_interactive_shell())


@dev_app.command("build")
def dev_build() -> None:
    """Execute a guarded build pipeline."""

    loop = _ensure_event_loop()
    loop.run_until_complete(devsuite.run_build())


@dev_app.command("scan")
def dev_scan(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Run secure scanning workflows."""

    loop = _ensure_event_loop()
    loop.run_until_complete(devsuite.run_scan(target))


@dev_app.command("deploy")
def dev_deploy(safe: bool = typer.Option(True, "--safe/--force")) -> None:
    """Perform a guarded deployment."""

    loop = _ensure_event_loop()
    loop.run_until_complete(devsuite.run_deploy(safe=safe))


@dev_app.command("doctrine")
def dev_doctrine(check: bool = typer.Option(True, "--check/--skip")) -> None:
    """Run doctrine alignment checks."""

    loop = _ensure_event_loop()
    loop.run_until_complete(devsuite.run_doctrine_check(check=check))


app.add_typer(guard_app, name="guard")
app.add_typer(dev_app, name="dev")


if __name__ == "__main__":
    app()
