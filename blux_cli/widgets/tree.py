"""
BLUX Ecosystem Tree Widget
Interactive tree visualization for BLUX Guard ecosystem
Cross-platform compatible with security integration
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root to Python path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Tree, Header, Footer, Static, Label
    from textual.containers import Horizontal, Vertical
    from textual import events
    from textual.reactive import reactive
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    print("Textual not available - tree widget requires: pip install textual")

# Security integration
try:
    from blux_modules.security.privilege_manager import PrivilegeManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Detect dev mode
try:
    import textual_dev  # type: ignore
    DEV_MODE = True
except ImportError:
    DEV_MODE = False


class FallbackPrivilege:
    def get_privilege_info(self):
        is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        return {"is_root": is_root, "fallback": True, "platform": {"system": os.name, "architecture": platform.machine()}}


# Load node data from a JSON file
try:
    with open(Path(__file__).parent / "node_data.json", "r") as f:
        NODE_DATA = json.load(f)
except FileNotFoundError:
    NODE_DATA = {}
    print("Warning: node_data.json not found. Node details will be limited.")

class SecurityStatus(Static):
    """
    Security status indicator for tree nodes
    """

    def __init__(self, privilege_mgr=None):
        super().__init__()
        self.privilege_mgr = privilege_mgr if privilege_mgr else FallbackPrivilege()

    def compose(self) -> ComposeResult:
        yield Label("🔒 Security Status", classes="security-header")
        yield Label("Loading...", classes="security-content")

    def on_mount(self) -> None:
        self.update_security_status()

    def update_security_status(self):
        """Update security status display"""
        if not self.privilege_mgr:
            self.query_one(".security-content").update("❌ Security unavailable")
            return

        try:
            priv_info = self.privilege_mgr.get_privilege_info()
            status = "🔴 ROOT" if priv_info['is_root'] else "🟢 USER"
            mode = self.privilege_mgr.get_operational_mode() if hasattr(self.privilege_mgr, 'get_operational_mode') else "UNKNOWN"

            content = f"""
{status} • {mode}

Platform: {priv_info['platform']['system']}
Arch: {priv_info['platform']['architecture']}

{'⚠️  Running with full system access' if priv_info['is_root'] else '🔐 User-space security mode'}
"""
            self.query_one(".security-content").update(content)
        except Exception as e:
            self.query_one(".security-content").update(f"❌ Error: {str(e)}")


class NodeDetails(Static):
    """
    Enhanced node details panel with security context
    """

    current_node = reactive("")

    def __init__(self, privilege_mgr=None):
        super().__init__()
        self.privilege_mgr = privilege_mgr if privilege_mgr else FallbackPrivilege()

    def compose(self) -> ComposeResult:
        yield Label("📋 Node Details", classes="details-header")
        yield Label("Select a node to view details", classes="details-content")

    def watch_current_node(self, node_label: str) -> None:
        """Update details when node changes"""
        if not node_label:
            self.query_one(".details-content").update("Select a node to view details")
            return

        # Get node-specific information
        node_info = self._get_node_info(node_label)
        self.query_one(".details-content").update(node_info)

    def _get_node_info(self, node_label: str) -> str:
        """Get detailed information for a specific node"""
        info = NODE_DATA.get(node_label, {
            "description": "BLUX Ecosystem Component",
            "security_level": "STANDARD",
            "capabilities": ["Security operations", "System integration"]
        })

        # Build details content
        content = f"[bold]{node_label}[/bold]\n\n"
        content += f"Description: {info['description']}\n"
        content += f"Security Level: {info['security_level']}\n\n"

        # Add security context
        if self.privilege_mgr:
            priv_info = self.privilege_mgr.get_privilege_info()
            if info.get('requires_root') and not priv_info['is_root']:
                content += "⚠️ [yellow]Requires root privileges[/yellow]\n"
                content += "   Some features may be limited\n\n"

        content += "Capabilities:\n"
        for capability in info['capabilities']:
            content += f"  • {capability}\n"

        content += "\nNavigation:\n"
        content += "  ↑↓ - Navigate • → - Expand • ← - Collapse\n"
        content += "  Enter - Select • q - Quit"

        return content


class BLUXTree(Tree):
    """
    Enhanced BLUX Ecosystem Tree with security integration
    """

    def __init__(self, privilege_mgr=None):
        super().__init__("The Outer Void")
        self.privilege_mgr = privilege_mgr if privilege_mgr else FallbackPrivilege()

    def on_mount(self) -> None:
        """Build the tree structure on mount"""
        self.root.expand()

        # Main ecosystem structure
        blux = self.root.add("BLUX_Ecosystem", expand=True)

        # Core components with security context
        self._add_component(blux, "BLUX-cA — AI-Conscious_Agent", requires_root=False)
        self._add_component(blux, "BLUX_Lite-(GOLD) — AI-Orchestrator", requires_root=False)
        self._add_component(blux, "BLUX_Quantum — bluxq-cli", requires_root=True)
        self._add_component(blux, "BLUX_Commander — Web_Interface", requires_root=False)
        self._add_component(blux, "BLUX_Guard_Ultra — BLUX_Term_Cockpit", requires_root=False)
        self._add_component(blux, "BLUX_Reg — BLUX_Auth_Sys", requires_root=False)

        # BLUX Guard Ultra subtree
        guard = blux.add("BLUX_Guard_Ultra — Terminal Cockpit", expand=True)
        self._add_component(guard, "Defender — Intrusion Detector", requires_root=True)
        self._add_component(guard, "Network Monitor — Conn Watch", requires_root=True)
        self._add_component(guard, "TUI Cockpit — Session Manager", requires_root=False)
        self._add_component(guard, "Security Dashboard", requires_root=False)
        self._add_component(guard, "Anti-Tamper Engine", requires_root=True)

        # BLUX Lite subtree
        lite = blux.add("BLUX_Lite-(GOLD) — Orchestrator", expand=True)
        self._add_component(lite, "Coordinator — Task Broker", requires_root=False)
        self._add_component(lite, "LibF Hub — Routing / plugins", requires_root=False)
        self._add_component(lite, "Memory — History Store", requires_root=False)
        self._add_component(lite, "AI Decision Engine", requires_root=False)

        # BLUX-cA subtree
        ca = blux.add("BLUX-cA — Conscious Agent (v0.1)", expand=True)
        self._add_component(ca, "Policy Engine", requires_root=False)
        self._add_component(ca, "Intervention Library", requires_root=False)
        self._add_component(ca, "Audit Trail", requires_root=False)
        self._add_component(ca, "Threat Intelligence", requires_root=False)

        # Security modules subtree
        security = blux.add("Security Modules", expand=True)
        self._add_component(security, "Authentication System", requires_root=False)
        self._add_component(security, "Privilege Manager", requires_root=False)
        self._add_component(security, "Sensor Framework", requires_root=True)
        self._add_component(security, "Containment Engine", requires_root=True)

    def _add_component(self, parent, label: str, requires_root: bool = False):
        """Add a component with security context"""
        node = parent.add(label)

        # Add security indicator if root is required but not available
        if requires_root and self.privilege_mgr:
            priv_info = self.privilege_mgr.get_privilege_info()
            if not priv_info['is_root']:
                node.label = f"{label} ⚠️"

        return node


class TreeApp(App):
    """
    BLUX Ecosystem Tree Visualization
    Cross-platform compatible with security integration
    """

    CSS_PATH = "blux_cockpit.css"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f1", "help", "Help"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.title = "BLUX Ecosystem — The Outer Void"
        if DEV_MODE:
            self.title = f"{self.title} — DEV MODE ACTIVE"

        # Create a single instance of PrivilegeManager
        if SECURITY_AVAILABLE:
            try:
                self.privilege_mgr = PrivilegeManager()
            except Exception:
                self.privilege_mgr = FallbackPrivilege()
        else:
            self.privilege_mgr = FallbackPrivilege()

    def compose(self) -> ComposeResult:
        """Compose the application layout"""
        yield Header(show_clock=True)

        with Horizontal():
            # Left panel - Tree
            with Vertical(classes="tree-panel"):
                yield BLUXTree(self.privilege_mgr)

            # Right panel - Details and Security
            with Vertical(classes="details-panel"):
                yield NodeDetails(self.privilege_mgr)
                yield SecurityStatus(self.privilege_mgr)

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        tree = self.query_one(BLUXTree)
        tree.focus()

        # Update title with security context
        if self.privilege_mgr:
            try:
                priv_info = self.privilege_mgr.get_privilege_info()
                mode = "ROOT" if priv_info['is_root'] else "USER"
                self.sub_title = f"Security Mode: {mode} • Platform: {priv_info['platform']['system']}"
            except Exception:
                self.sub_title = "Security: Basic Mode"

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection"""
        node_details = self.query_one(NodeDetails)
        node_details.current_node = str(event.node.label)

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    def action_help(self) -> None:
        """Show help information"""
        self.notify(
            "↑↓: Navigate • →: Expand • ←: Collapse • Enter: Select • q: Quit",
            title="Navigation Help"
        )

    def action_refresh(self) -> None:
        """Refresh security status"""
        security_status = self.query_one(SecurityStatus)
        security_status.update_security_status()
        self.notify("Security status refreshed")


# Fallback implementation for when Textual is not available
class BasicTreeView:
    """
    Basic fallback tree view for environments without Textual
    """

    def __init__(self, privilege_mgr=None):
        self.privilege_mgr = privilege_mgr if privilege_mgr else FallbackPrivilege()

    def display(self):
        """Display basic tree view"""
        print("BLUX Ecosystem Tree - The Outer Void")
        print("=" * 50)

        tree_structure = """
The Outer Void
└── BLUX_Ecosystem
    ├── BLUX-cA — AI-Conscious_Agent
    ├── BLUX_Lite-(GOLD) — AI-Orchestrator
    ├── BLUX_Quantum — bluxq-cli
    ├── BLUX_Commander — Web_Interface
    ├── BLUX_Guard_Ultra — BLUX_Term_Cockpit
    │   ├── Defender — Intrusion Detector
    │   ├── Network Monitor — Conn Watch
    │   ├── TUI Cockpit — Session Manager
    │   └── Security Dashboard
    ├── BLUX_Reg — BLUX_Auth_Sys
    └── Security Modules
        ├── Authentication System
        ├── Privilege Manager
        └── Sensor Framework
"""
        print(tree_structure)

        # Show security status
        if self.privilege_mgr:
            try:
                priv_info = self.privilege_mgr.get_privilege_info()
                print(f"\nSecurity Status:")
                print(f"  Mode: {'ROOT' if priv_info['is_root'] else 'USER'}")
                print(f"  Platform: {priv_info['platform']['system']}")
                if not priv_info['is_root']:
                    print(f"  Note: Some features require root privileges")
            except Exception as e:
                print(f"  Security status unavailable: {e}")


def main():
    """Main entry point"""
    if not TEXTUAL_AVAILABLE:
        print("Textual not available - using basic tree view")
        view = BasicTreeView()
        view.display()
        return

    try:
        if SECURITY_AVAILABLE:
            try:
                privilege_mgr = PrivilegeManager()
            except Exception:
                privilege_mgr = FallbackPrivilege()
        else:
            privilege_mgr = FallbackPrivilege()
        app = TreeApp(privilege_mgr=privilege_mgr)
        app.run()
    except Exception as e:
        print(f"Failed to start tree application: {e}")
        print("Falling back to basic view...")
        view = BasicTreeView()
        view.display()


if __name__ == "__main__":
    main()
