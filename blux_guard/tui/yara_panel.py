"""Panel that triggers local YARA scans."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Optional

from textual.widgets import Static

from ..core import security_cockpit


class YaraPanel(Static):
    """Display and run YARA scans on-demand."""

    _paths: Optional[list[str]] = None
    _report: security_cockpit.YaraScanReport | None = None

    def on_mount(self) -> None:  # type: ignore[override]
        self.update("Press Y to run YARA scan")

    async def run_scan(
        self,
        paths: Optional[Iterable[str]] = None,
        rules_path: Optional[str] = None,
    ) -> security_cockpit.YaraScanReport:
        self.update("Scanning with YARA…")
        await asyncio.sleep(0)
        path_objects = [Path(p) for p in (paths or self._paths or ["."])]
        report = await asyncio.to_thread(
            security_cockpit.run_yara_scan,
            path_objects,
            Path(rules_path) if rules_path else None,
        )
        self._report = report
        self._paths = [str(p) for p in path_objects]
        self.render_report(report)
        return report

    def render_report(self, report: security_cockpit.YaraScanReport) -> None:
        lines = [f"Status: {report.status}", report.message]
        if report.scanned:
            lines.append("Targets: " + ", ".join(report.scanned))
        if report.findings:
            self.set_class(True, "alert")
            lines.append("")
            for finding in report.findings[:5]:
                lines.append(f"{finding.rule} -> {finding.path}")
            if len(report.findings) > 5:
                lines.append(f"… {len(report.findings) - 5} more")
        else:
            self.set_class(False, "alert")
        self.update("\n".join(lines))

    @property
    def report(self) -> security_cockpit.YaraScanReport | None:
        return self._report

