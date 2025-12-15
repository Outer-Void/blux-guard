"""Unified cockpit wrapper for Textual TUI."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult

from .. import audit
from . import dashboard


class CockpitApp(dashboard.DashboardApp):
    """Extend the dashboard with audit/correlation plumbing."""

    def __init__(self, mode: str = "secure", correlation_id: Optional[str] = None) -> None:
        super().__init__(mode=mode)
        self.correlation_id = correlation_id or audit.generate_correlation_id()

    def compose(self) -> ComposeResult:  # type: ignore[override]
        audit.record(
            "tui.screen.enter",
            actor="tui",
            payload={"screen": "home", "mode": self.mode},
            correlation_id=self.correlation_id,
        )
        for node in super().compose():
            yield node

    def on_unmount(self) -> None:  # type: ignore[override]
        audit.record(
            "tui.screen.exit",
            actor="tui",
            payload={"screen": "home", "mode": self.mode},
            correlation_id=self.correlation_id,
        )


async def run_cockpit(mode: str = "secure", *, correlation_id: Optional[str] = None) -> None:
    """Launch the cockpit with audit tracking."""

    cid = correlation_id or audit.generate_correlation_id()
    audit.record("tui.launch", actor="tui", payload={"mode": mode}, correlation_id=cid)
    app = CockpitApp(mode=mode, correlation_id=cid)
    await app.run_async()
