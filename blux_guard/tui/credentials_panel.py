"""Argon2 credential verification panel."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from textual.widgets import Static

from ..core import security_cockpit


class CredentialsPanel(Static):
    """Audit credential hashes using Argon2 metadata."""

    _report: security_cockpit.CredentialAuditReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.update("Press C to audit credentials")

    async def run_audit(self, credentials_path: Optional[str] = None) -> security_cockpit.CredentialAuditReport:
        self.update("Auditing Argon2 credentials…")
        await asyncio.sleep(0)
        report = await asyncio.to_thread(
            security_cockpit.argon2_credential_audit,
            Path(credentials_path).expanduser() if credentials_path else None,
        )
        self._report = report
        self.render_report(report)
        return report

    def render_report(self, report: security_cockpit.CredentialAuditReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.findings:
            lines.append("")
            for finding in report.findings[:5]:
                marker = "OK" if finding.valid else "ALERT"
                if not finding.valid:
                    self.set_class(True, "alert")
                lines.append(f"[{marker}] {finding.subject}: {finding.detail}")
            if len(report.findings) > 5:
                lines.append(f"… {len(report.findings) - 5} more")
        else:
            self.set_class(False, "alert")
        if report.status == "clean":
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.CredentialAuditReport | None:
        return self._report

