"""Metrics panel sourcing data from telemetry."""

from __future__ import annotations

from textual.widgets import Static

from ..core import doctrine_integration, telemetry


class MetricsPanel(Static):
    """Display runtime metrics for the cockpit."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_metrics()

    def refresh_metrics(self) -> None:
        status = telemetry.collect_status_sync()
        score = doctrine_integration.doctrine_score() * 100
        message = (
            f"Doctrine score: {score:.1f}%\n"
            f"Log dir: {status['log_dir']}\n"
            f"Audit log entries -> {status['audit_log']}"
        )
        self.update(message)
