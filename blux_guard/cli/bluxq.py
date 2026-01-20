"""Entry point for the BLUX Guard Developer Suite CLI."""

from __future__ import annotations

import asyncio
import json
import pathlib
import traceback
from typing import Optional

import typer

from blux_guard import audit, doctor
from blux_guard.core import devsuite, receipt as receipt_engine, runtime, telemetry
from blux_guard.core import selfcheck as core_selfcheck
from blux_guard.tui import app as cockpit_app

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
    """Main CLI callback.

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


@guard_app.command("scan")
def guard_scan(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Run a guard scan via dev suite."""

    _run_async("guard scan", lambda: devsuite.run_scan(target))


@guard_app.command("watch")
def guard_watch(target: pathlib.Path = typer.Argument(pathlib.Path("."))) -> None:
    """Continuously scan a target (placeholder watch mode)."""

    audit.record("cli.watch", actor="cli", payload={"target": str(target)})
    _run_async("guard watch", lambda: devsuite.run_scan(target))


@guard_app.command("tui")
def guard_tui(
    mode: str = typer.Option("secure", help="TUI mode: dev|secure|ops"),
    correlation_id: str = typer.Option(None, help="Correlation id to propagate."),
) -> None:
    """Launch the Textual cockpit."""

    cid = correlation_id or audit.generate_correlation_id()
    _run_async("guard tui", lambda: cockpit_app.run_cockpit(mode=mode, correlation_id=cid))


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


@guard_app.command("doctor")
def guard_doctor() -> None:
    """Run environment diagnostics."""

    report = doctor.run_doctor()
    typer.echo(json.dumps(report, indent=2))


@guard_app.command("verify")
def guard_verify() -> None:
    """Verify configuration and audit log paths."""

    report = doctor.run_verify()
    typer.echo(json.dumps(report, indent=2))


@guard_app.command("incidents")
def guard_incidents(limit: int = typer.Option(10, help="Number of entries")) -> None:
    """Print recent warning/error audit entries."""

    path = audit.audit_log_path()
    if not path.exists():
        typer.echo("No audit log present", err=True)
        return
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    for line in lines:
        typer.echo(line)


@guard_app.command("export")
def guard_export() -> None:
    """Export diagnostic bundle using cockpit helpers."""

    status = telemetry.collect_status_sync()
    audit.record("cli.export", actor="cli", payload=status)
    typer.echo(json.dumps(status, indent=2))


@guard_app.command("evaluate")
def guard_evaluate(
    request_envelope: pathlib.Path = typer.Option(
        ..., "--request-envelope", help="Envelope JSON payload."
    ),
    capability_ref: Optional[list[str]] = typer.Option(
        None, "--capability-ref", help="Capability reference (repeatable)."
    ),
    discernment: Optional[pathlib.Path] = typer.Option(
        None, "--discernment", help="Optional discernment report JSON."
    ),
) -> None:
    """Evaluate an envelope and emit a guard receipt."""

    receipt = receipt_engine.evaluate_from_files(
        request_envelope,
        discernment,
        capability_refs=capability_ref or None,
    )
    typer.echo(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))


@guard_app.command("install")
def guard_install(target: str = typer.Option("linux", help="linux|termux")) -> None:
    """Hint the operator to platform installer documentation."""

    typer.echo(f"See INSTALL.md for {target} instructions.")
    audit.record("cli.install", actor="cli", payload={"target": target})


@dev_app.command("init")
def dev_init(path: pathlib.Path = typer.Argument(pathlib.Path.cwd(), help="Project directory")) -> None:
    """Initialise a secure workspace."""

    _run_async("dev init", lambda: devsuite.initialise_workspace(path))
    typer.echo(f"Workspace initialised at {path}")


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


app.add_typer(guard_app, name="guard")
app.add_typer(dev_app, name="dev")


if __name__ == "__main__":
    app()
