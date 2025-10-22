"""Textual dashboard for the Developer Suite cockpit."""

from __future__ import annotations

from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from ..core import doctrine_integration
from ..core import telemetry
from .audit_panel import AuditPanel
from .metrics_panel import MetricsPanel
from .shell_panel import ShellPanel


class DoctrinePanel(Static):
    """Display doctrine alignment information."""

    DEFAULT_CSS = """DoctrinePanel { padding: 1; }"""

    def on_mount(self) -> None:  # type: ignore[override]
        self.update_doctrine()

    def update_doctrine(self) -> None:
        score = doctrine_integration.doctrine_score() * 100
        doctrine = doctrine_integration.ensure_doctrine_loaded()
        summary = f"Doctrine score: {score:.1f}%\nPolicies loaded: {len(doctrine)}"
        self.update(summary)


class DashboardApp(App[Any]):
    CSS_PATH = None
    BINDINGS = [Binding("ctrl+c", "quit", "Quit"), Binding("r", "refresh", "Refresh")]

    def __init__(self, mode: str = "secure") -> None:
        super().__init__()
        self.mode = mode

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header(show_clock=True)
        with Vertical():
            yield Static(f"BLUX Guard Developer Suite — Mode: {self.mode}", id="title")
            with Horizontal():
                yield MetricsPanel()
                yield DoctrinePanel()
                yield AuditPanel()
            yield ShellPanel()
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(DoctrinePanel).update_doctrine()
        self.query_one(MetricsPanel).refresh_metrics()
        self.query_one(AuditPanel).refresh_audit()


async def run_dashboard(mode: str = "secure") -> None:
    telemetry.record_event("tui.launch", {"mode": mode})
    app = DashboardApp(mode=mode)
    await app.run_async()
