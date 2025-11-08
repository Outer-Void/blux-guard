"""Panel verifying the audit hash chain."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Static

from ..core import security_cockpit, telemetry


class AuditIntegrityPanel(Static):
    """Display audit log integrity information."""

    _report: security_cockpit.AuditChainReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_integrity()

    def refresh_integrity(self) -> security_cockpit.AuditChainReport:
        status = telemetry.collect_status_sync()
        audit_path = Path(status["audit_log"]).expanduser()
        report = security_cockpit.verify_audit_chain(audit_path)
        self._report = report
        self.render_report(report)
        return report

    async def async_refresh(self) -> security_cockpit.AuditChainReport:
        await asyncio.sleep(0)
        return self.refresh_integrity()

    def render_report(self, report: security_cockpit.AuditChainReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.digest:
            lines.append(f"Digest: {report.digest[:16]}…")
        lines.append(f"Entries: {report.line_count}")
        if report.status not in {"clean", "empty"}:
            self.set_class(True, "alert")
        else:
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.AuditChainReport | None:
        return self._report

