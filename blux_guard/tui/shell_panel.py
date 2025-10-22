"""Interactive shell panel powered by asyncio subprocesses."""

from __future__ import annotations

from typing import Optional

from textual.reactive import reactive
from textual.widgets import Static

from ..core import sandbox, telemetry


class ShellPanel(Static):
    """Simple wrapper that launches a sandbox shell when activated."""

    running: reactive[bool] = reactive(False)

    def on_mount(self) -> None:  # type: ignore[override]
        self.update("Press Enter to launch sandbox shell")

    async def on_key(self, event) -> None:  # type: ignore[override]
        if event.key == "enter" and not self.running:
            self.running = True
            self.update("Launching sandbox shell...")
            await sandbox.launch_interactive_shell()
            self.update("Shell session ended")
            self.running = False

    async def action_launch(self, command: Optional[str] = None) -> None:
        if self.running:
            return
        self.running = True
        telemetry.record_event("tui.shell.launch", {"command": command or "default"})
        await sandbox.launch_interactive_shell(command)
        self.running = False
        self.update("Shell session ended")
