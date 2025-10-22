"""Entry point for the BLUX Guard Developer Suite CLI."""

from __future__ import annotations

import asyncio
import json
import pathlib
import traceback
from typing import Optional

import typer

try:
    from blux_cli import blux as legacy_cli
except Exception:  # pragma: no cover - defensive import guard
    legacy_cli = None

from blux_guard.core import devsuite, runtime, sandbox, telemetry
from blux_guard.core import selfcheck as core_selfcheck
from blux_guard.tui import dashboard

app = typer.Typer(help="BLUX Guard Developer Suite (Quantum namespace)")

guard_app = typer.Typer(help="Guard management commands")

dev_app = typer.Typer(help="Developer workflow commands")


def _configure_runtime(debug: bool, verbose: bool) -> None:
    runtime.set_debug(debug)
    runtime.set_verbose(verbose)
    telemetry.set_debug(debug)
    telemetry.set_verbose(verbose)


@app.callback()
def main(
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debugging output."),
    verbose: bool = typer.Option(False, "--verbose", help="Print verbose telemetry output."),
) -> None:
    """Root CLI callback.

    The callback is intentionally empty so Typer can manage sub-commands.
    """

    _configure_runtime(debug, verbose)
    runtime.ensure_supported_python("bluxq")
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


def _handle_exception(exc: Exception, *, context: str) -> None:
    telemetry.record_event(
        "cli.error",
        level="error",
        actor="cli",
        payload={"context": context, "error": str(exc)},
    )
    if runtime.debug_enabled():
        traceback.print_exc()
    else:
        typer.echo(f"Error during {context}: {exc}", err=True)


def _run_async(description: str, awaitable_factory) -> Optional[object]:
    loop = _ensure_event_loop()
    try:
        return loop.run_until_complete(awaitable_factory())
    except Exception as exc:  # pragma: no cover - defensive
        _handle_exception(exc, context=description)
        raise typer.Exit(code=1)


@guard_app.command("status")
def guard_status() -> None:
    """Print a high level status report for the guard runtime."""

    status = _run_async("guard status", telemetry.collect_status)
    typer.echo(json.dumps(status, indent=2, sort_keys=True))


@guard_app.command("tui")
def guard_tui(mode: str = typer.Option("secure", help="TUI mode: dev|secure|ops")) -> None:
    """Launch the Textual cockpit."""

    _run_async("guard tui", lambda: dashboard.run_dashboard(mode=mode))


@guard_app.command("self-check")
def guard_self_check() -> None:
    """Run environment validation checks and print the results."""

    results = _run_async("guard self-check", core_selfcheck.run_self_check)
    if not results:
        return

    typer.echo("Self-check summary:")
    for item in results["checks"]:
        typer.echo(
            f"- {item['name']}: {item['status'].upper()} -- {item['detail']}"
        )
    typer.echo(f"Overall status: {results['overall'].upper()}")


@app.command("legacy")
def legacy_passthrough(args: Optional[list[str]] = typer.Argument(None)) -> None:
    """Pass through to the legacy CLI for compatibility."""

    if legacy_cli is None:
        raise typer.Exit(code=1)
    legacy_cli.app(args=args or [])


@dev_app.command("init")
def dev_init(path: pathlib.Path = typer.Argument(pathlib.Path.cwd(), help="Project root")) -> None:
    """Initialise a secure workspace."""

    _run_async("dev init", lambda: devsuite.initialise_workspace(path))
    typer.echo(f"Workspace initialised at {path}")


@dev_app.command("shell")
def dev_shell() -> None:
    """Launch an interactive sandboxed shell."""

    _run_async("dev shell", sandbox.launch_interactive_shell)


@dev_app.command("build")
def dev_build() -> None:
    """Execute a guarded build pipeline."""

    _run_async("dev build", devsuite.run_build)


@dev_app.command("scan")
def dev_scan(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Run secure scanning workflows."""

    _run_async("dev scan", lambda: devsuite.run_scan(target))


@dev_app.command("deploy")
def dev_deploy(safe: bool = typer.Option(True, "--safe/--force")) -> None:
    """Perform a guarded deployment."""

    _run_async("dev deploy", lambda: devsuite.run_deploy(safe=safe))


@dev_app.command("doctrine")
def dev_doctrine(check: bool = typer.Option(True, "--check/--skip")) -> None:
    """Run doctrine alignment checks."""

    _run_async("dev doctrine", lambda: devsuite.run_doctrine_check(check=check))


app.add_typer(guard_app, name="guard")
app.add_typer(dev_app, name="dev")


if __name__ == "__main__":
    app()
