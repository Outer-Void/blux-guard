"""Process monitoring panel for the cockpit."""

from __future__ import annotations

from textual.widgets import Static

from ..core import security_cockpit


class ProcessPanel(Static):
    """Render top process information using psutil."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_processes()

    def refresh_processes(self) -> None:
        snapshot = security_cockpit.collect_process_snapshot()
        if snapshot.unavailable:
            self.update(f"Process monitor unavailable\n{snapshot.message}")
            self.set_class(True, "alert")
            return

        lines = ["PID    CPU%   MEM(MB) STATUS   NAME"]
        for proc in snapshot.processes:
            lines.append(
                f"{proc.pid:<6} {proc.cpu_percent:>5.1f} {proc.memory_mb:>8.1f} {proc.status:<8} {proc.name}"
            )
        self.update("\n".join(lines))
        self.set_class(False, "alert")
        self._snapshot = snapshot

    @property
    def snapshot(self) -> security_cockpit.ProcessSnapshot:
        if not hasattr(self, "_snapshot"):
            self._snapshot = security_cockpit.collect_process_snapshot()
        return self._snapshot

