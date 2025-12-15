"""Quantum integration surface for BLUX Guard."""

from __future__ import annotations

import typer

from .cli import bluxq


def register(app: typer.Typer) -> None:
    """Register Guard commands into an existing Typer app."""

    app.add_typer(bluxq.guard_app, name="guard")
