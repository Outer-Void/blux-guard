#!/usr/bin/env python3
"""
anti_tamper_controls.py

Interactive Anti-Tamper Controls panel for BLUX Guard (non-root)
- Safe, simulated actions
- Textual 0.25+ compatible
- Can run standalone or be adapted into a larger TUI
"""

import asyncio
from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Checkbox, Static
from textual.reactive import reactive
from rich.markdown import Markdown

BASE_DIR = Path(__file__).parent
CSS_PATH = str(Path(__file__).parent / "blux_cockpit.css")

# Default simulated monitor state
DEFAULT_CONTROLS = {
    "package_monitor": False,
    "selinux_monitor": False,
    "su_sentinel": False,
}


class AntiTamperControls(App):
    """
    Anti-Tamper Controls Panel — simulation only, non-root safe.
    """
    
    CSS_PATH = CSS_PATH

    controls_state = reactive(DEFAULT_CONTROLS.copy())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical():
            # Controls area: checkboxes + buttons
            with Horizontal(id="controls"):
                with Horizontal(classes="checkbox-container"):
                    self.chk_package = Checkbox("Package Monitor", id="chk_package")
                    yield self.chk_package
                with Horizontal(classes="checkbox-container"):
                    self.chk_selinux = Checkbox("SELinux Monitor", id="chk_selinux")
                    yield self.chk_selinux
                with Horizontal(classes="checkbox-container"):
                    self.chk_su = Checkbox("SU Sentinel", id="chk_su")
                    yield self.chk_su

                # Action buttons
                yield Button("Scan Packages", id="btn_scan_pkgs")
                yield Button("Check SELinux", id="btn_check_selinux")
                yield Button("Audit SU Access", id="btn_audit_su")
                yield Button("Force Lockdown", id="btn_lockdown", variant="error")

            # Log / status area
            self.log_panel = Static(self._initial_markdown(), id="log")
            yield self.log_panel

        yield Footer()

    def _initial_markdown(self) -> Markdown:
        intro = (
            "# Anti-Tamper Controls\n\n"
            "This panel **simulates** anti-tamper actions without requiring root. "
            "Toggle monitors (checkboxes) to enable/disable simulated watchers. "
            "Use buttons to run checks — results appear in the log below.\n\n"
            f"**Started:** {datetime.utcnow().isoformat()}Z\n"
        )
        return Markdown(intro)

    # -------------------------
    # Event handlers
    # -------------------------
    async def on_mount(self) -> None:
        """
        Initialize checkbox states from reactive state.
        """
        self.chk_package.value = self.controls_state["package_monitor"]
        self.chk_selinux.value = self.controls_state["selinux_monitor"]
        self.chk_su.value = self.controls_state["su_sentinel"]
        self.set_interval(5, self._periodic_monitor_heartbeat)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.
        """
        button = event.button
        btn_id = button.id
        
        if btn_id == "btn_scan_pkgs":
            await self._action_with_log("Scanning installed packages", self._simulate_package_scan)
        elif btn_id == "btn_check_selinux":
            await self._action_with_log("Checking SELinux status", self._simulate_selinux_check)
        elif btn_id == "btn_audit_su":
            await self._action_with_log("Auditing su/sudo usage", self._simulate_su_audit)
        elif btn_id == "btn_lockdown":
            await self._action_with_log("Forcing containment lockdown", self._simulate_lockdown, critical=True)
        else:
            await self._append_log(f"[yellow]Unknown button pressed:[/yellow] {button.label}")

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """
        Handle checkbox change events.
        """
        chk_id = event.checkbox.id
        val = event.value
        
        if chk_id == "chk_package":
            self.controls_state["package_monitor"] = val
            await self._append_log(f"Package Monitor {'enabled' if val else 'disabled'}")
        elif chk_id == "chk_selinux":
            self.controls_state["selinux_monitor"] = val
            await self._append_log(f"SELinux Monitor {'enabled' if val else 'disabled'}")
        elif chk_id == "chk_su":
            self.controls_state["su_sentinel"] = val
            await self._append_log(f"SU Sentinel {'enabled' if val else 'disabled'}")

    # -------------------------
    # Simulated actions
    # -------------------------
    async def _action_with_log(self, summary: str, coro_callable, *, critical: bool = False):
        """
        Execute an action and log the results.
        """
        ts = datetime.utcnow().isoformat() + "Z"
        await self._append_log(f"[bold]{summary}[/bold] — started at {ts}")
        try:
            result = await coro_callable()
            await self._append_log(f"[green]{summary} — completed[/green]: {result}")
            if critical:
                await self._append_log(f"[red]CRITICAL ACTION EXECUTED (simulated): {summary}[/red]")
        except Exception as e:
            await self._append_log(f"[red]Error during {summary}:[/red] {e}")

    async def _simulate_package_scan(self) -> str:
        """
        Simulate package scanning.
        """
        await asyncio.sleep(0.8)
        return "OK — 1 package needs update (package.foo=1.2.3 -> 1.2.4)"

    async def _simulate_selinux_check(self) -> str:
        """
        Simulate SELinux status check.
        """
        await asyncio.sleep(0.5)
        return "SELinux mode: permissive (simulated). No policy violations detected."

    async def _simulate_su_audit(self) -> str:
        """
        Simulate su/sudo audit.
        """
        await asyncio.sleep(0.6)
        return "Recent su attempts: 0; Last sudo: 2025-10-01T12:34:56Z (simulated)"

    async def _simulate_lockdown(self) -> str:
        """
        Simulate system lockdown.
        """
        await asyncio.sleep(1.2)
        # Update reactive state and checkboxes
        self.controls_state.update({
            "package_monitor": False,
            "selinux_monitor": False, 
            "su_sentinel": False
        })
        self.chk_package.value = False
        self.chk_selinux.value = False
        self.chk_su.value = False
        return "Lockdown simulated: all monitors disabled."

    # -------------------------
    # Heartbeat & Logging
    # -------------------------
    async def _periodic_monitor_heartbeat(self) -> None:
        """
        Periodic update showing active monitors.
        """
        active = [k.replace('_', ' ').title() for k, v in self.controls_state.items() if v]
        if active:
            await self._append_log(f"[cyan]Heartbeat:[/cyan] active monitors: {', '.join(active)}")

    async def _append_log(self, message: str) -> None:
        """
        Append a message to the log panel.
        """
        ts = datetime.utcnow().isoformat() + "Z"
        prev_text = str(self.log_panel.renderable) if self.log_panel.renderable else ""
        new_line = f"- {ts} — {message}\n"
        content = (prev_text + new_line)[-2000:]  # keep last ~2000 chars
        self.log_panel.update(Markdown(content))

    # -------------------------
# Runner
# -------------------------
@classmethod
def run_standalone(cls):
    """
    Run the app in standalone mode.
    """
    app = cls()
    app.run()


if __name__ == "__main__":
    AntiTamperControls.run_standalone()
