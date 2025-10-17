#!/usr/bin/env python3
"""
BLUX Guard Shell Launcher
Simple wrapper to launch the BLUX Guard shell from anywhere
Version: 1.0.0
Author: Outer Void Team
"""

import os
import sys
from pathlib import Path

# Dynamically discover the project root
try:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from blux_guard_shell import launch_shell
    print("🚀 Launching BLUX Guard Shell...")
    launch_shell()

except ImportError as e:
    print(f"❌ Failed to launch BLUX Guard Shell: {e}")
    print("💡 Make sure you're in the BLUX Guard project directory")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n👋 BLUX Guard Shell launch cancelled")
    sys.exit(130)
