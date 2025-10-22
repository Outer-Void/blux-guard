"""Audit log panel."""

from __future__ import annotations

import pathlib

from textual.widgets import Static

from ..core import telemetry


class AuditPanel(Static):
    """Render the most recent audit log lines."""

    _max_lines = 5

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_audit()

    def refresh_audit(self) -> None:
        status = telemetry.collect_status_sync()
        path = pathlib.Path(status["audit_log"])
        if not path.exists():
            self.update("No audit events yet")
            return
        lines = path.read_text(encoding="utf-8").strip().splitlines()[-self._max_lines :]
        rendered = "\n".join(lines) if lines else "No audit events yet"
        self.update(rendered)
