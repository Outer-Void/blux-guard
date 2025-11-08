"""Panel representing bq guard quantum orchestration hooks."""

from __future__ import annotations

import asyncio

from textual.widgets import Static

from ..core import security_cockpit


class BqGuardPanel(Static):
    """Show registered quantum orchestration hooks and allow invocation."""

    def on_mount(self) -> None:  # type: ignore[override]
        self.refresh_status()

    def refresh_status(self) -> security_cockpit.BqHookStatus:
        status = security_cockpit.bq_guard_registry.status()
        lines = ["bq Guard Hooks", f"Registered: {len(status.registered)}"]
        if status.registered:
            lines.append(", ".join(status.registered))
        if status.last_result:
            lines.append(f"Last: {status.last_result}")
        lines.append(status.message)
        self.update("\n".join(lines))
        return status

    async def invoke(self) -> security_cockpit.BqHookStatus:
        await asyncio.sleep(0)
        await security_cockpit.bq_guard_registry.invoke_all()
        return self.refresh_status()

