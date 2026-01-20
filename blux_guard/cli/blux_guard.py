"""BLUX Guard receipt CLI."""

from __future__ import annotations

import json
import pathlib
from typing import Optional

import typer

from blux_guard.core import receipt as receipt_engine

app = typer.Typer(help="BLUX Guard receipt tooling")


@app.command("evaluate")
def evaluate(
    request_envelope: pathlib.Path = typer.Option(
        ..., "--request-envelope", help="Envelope JSON payload."
    ),
    token: Optional[list[str]] = typer.Option(
        None, "--token", help="Capability token (repeatable)."
    ),
    discernment: Optional[pathlib.Path] = typer.Option(
        None, "--discernment", help="Optional discernment report JSON."
    ),
    revocations: Optional[pathlib.Path] = typer.Option(
        None, "--revocations", help="Optional revocation list JSON."
    ),
) -> None:
    """Evaluate an envelope and emit a guard receipt."""

    receipt = receipt_engine.evaluate_from_files(
        request_envelope,
        discernment,
        tokens=token or None,
        revocations_path=revocations,
    )
    typer.echo(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))


@app.command("verify-receipt")
def verify_receipt(
    receipt_path: pathlib.Path = typer.Option(
        ..., "--receipt", help="Guard receipt JSON payload."
    )
) -> None:
    """Verify a guard receipt for integrity."""

    receipt_payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    ok, reason = receipt_engine.verify_receipt(receipt_payload)
    payload = {"ok": ok, "reason": reason}
    if not ok:
        typer.echo(json.dumps(payload), err=True)
        raise typer.Exit(code=2)
    typer.echo(json.dumps(payload))
