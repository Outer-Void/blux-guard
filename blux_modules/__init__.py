"""
BLUX Guard Swarm Simulator Package

This package provides a nano-swarm simulator for defensive purposes,
allowing you to simulate and test responses to security events.

Version: 1.0.0
Author: Outer Void Team
"""

from .swarm_sim import main, Agent, ApkWatchHandler  # Import what you want to expose
from .swarm_sim import INC_DIR, OUTBOX, QUARANTINE_SCRIPT, NUM_AGENTS, WATCH_DIRECTORIES, ALERT_COOLDOWN
from .swarm_sim import sign_and_append, do_quarantine, emit_alert_file

__all__ = [
    "main",
    "Agent",
    "ApkWatchHandler",
    "INC_DIR",
    "OUTBOX",
    "QUARANTINE_SCRIPT",
    "NUM_AGENTS",
    "WATCH_DIRECTORIES",
    "ALERT_COOLDOWN",
    "sign_and_append",
    "do_quarantine",
    "emit_alert_file",
]
