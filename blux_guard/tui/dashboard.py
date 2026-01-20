"""Textual dashboard for the Developer Security Cockpit."""

from __future__ import annotations

from typing import Any

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.widgets import Footer, Header, Static

from ..core import security_cockpit, telemetry
from .audit_integrity_panel import AuditIntegrityPanel
from .audit_panel import AuditPanel
from .bq_panel import BqGuardPanel
from .credentials_panel import CredentialsPanel
from .metrics_panel import MetricsPanel
from .process_panel import ProcessPanel
from .yara_panel import YaraPanel


class DashboardApp(App[Any]):
    CSS_PATH = "cockpit.css"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("p", "refresh_process", "Processes"),
        Binding("y", "scan_yara", "YARA Scan"),
        Binding("c", "audit_credentials", "Credential Audit"),
        Binding("a", "verify_audit", "Audit Chain"),
        Binding("b", "invoke_bq", "bq Hooks"),
        Binding("e", "export_diagnostics", "Export"),
    ]

    def __init__(self, mode: str = "secure") -> None:
        super().__init__()
        self.mode = mode

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield Static(f"BLUX Guard Security Cockpit — Mode: {self.mode}", id="title")
            with Grid(id="grid"):
                yield MetricsPanel(classes="panel")
                yield ProcessPanel(classes="panel")
                yield AuditPanel(classes="panel")
                yield YaraPanel(classes="panel")
                yield CredentialsPanel(classes="panel")
                yield AuditIntegrityPanel(classes="panel")
                yield BqGuardPanel(classes="panel")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(MetricsPanel).refresh_metrics()
        self.query_one(AuditPanel).refresh_audit()
        self.query_one(ProcessPanel).refresh_processes()
        self.query_one(AuditIntegrityPanel).refresh_integrity()
        self.query_one(BqGuardPanel).refresh_status()

    def action_refresh_process(self) -> None:
        self.query_one(ProcessPanel).refresh_processes()

    async def action_scan_yara(self) -> None:
        panel = self.query_one(YaraPanel)
        await panel.run_scan()

    async def action_audit_credentials(self) -> None:
        panel = self.query_one(CredentialsPanel)
        await panel.run_audit()

    async def action_verify_audit(self) -> None:
        panel = self.query_one(AuditIntegrityPanel)
        await panel.async_refresh()

    async def action_invoke_bq(self) -> None:
        panel = self.query_one(BqGuardPanel)
        await panel.invoke()

    async def action_export_diagnostics(self) -> None:
        process_snapshot = self.query_one(ProcessPanel).snapshot
        yara_panel = self.query_one(YaraPanel)
        credential_panel = self.query_one(CredentialsPanel)
        yara_report = yara_panel.report or await asyncio.to_thread(security_cockpit.run_yara_scan)
        credential_report = credential_panel.report or await asyncio.to_thread(
            security_cockpit.argon2_credential_audit
        )
        audit_report = self.query_one(AuditIntegrityPanel).report or security_cockpit.verify_audit_chain(
            Path(telemetry.collect_status_sync()["audit_log"])  # type: ignore[arg-type]
        )
        bq_status = self.query_one(BqGuardPanel).refresh_status()
        exports = await asyncio.to_thread(
            security_cockpit.export_diagnostics,
            process_snapshot,
            yara_report,
            credential_report,
            audit_report,
            bq_status,
        )
        message = "Diagnostics exported:\n" + "\n".join(f"{name}: {path}" for name, path in exports.items())
        self.notify(message, severity="information")

async def run_dashboard(mode: str = "secure") -> None:
    telemetry.record_event(
        "tui.launch",
        actor="tui",
        payload={"mode": mode},
    )
    app = DashboardApp(mode=mode)
    await app.run_async()
