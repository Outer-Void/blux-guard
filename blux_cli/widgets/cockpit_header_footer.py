#!/usr/bin/env python3
"""
cockpit_header_footer.py — Reusable Header and Footer widgets for BLUX Guard Cockpit
Textual 0.25+ compatible, full-width layouts, import-safe.
"""

from textual.widgets import Header, Footer
from textual.reactive import reactive
from rich.text import Text
from datetime import datetime


class CockpitHeader(Header):
    """
    Custom cockpit header with live timestamp and dynamic title.
    """

    title_text = reactive("BLUX Guard Cockpit")

    def __init__(self, title: str = None, **kwargs):
        super().__init__(**kwargs)
        if title:
            self.title_text = title

    def render(self) -> Text:
        """
        Render header with dynamic title and UTC clock.
        """
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        header_text = f"{self.title_text} | {ts}"
        text = Text(header_text, style="bold cyan")
        # Center the text in the header area
        text = text.center(self.size.width) if self.size.width else text
        return text

    def update_title(self, new_title: str):
        """
        Update the header title dynamically.
        """
        self.title_text = new_title
        self.refresh()


class CockpitFooter(Footer):
    """
    Custom cockpit footer with instructions and dynamic status.
    """

    status_text = reactive("Ready")

    def update_status(self, message: str):
        """
        Update the footer status dynamically.
        """
        self.status_text = message
        self.refresh()

    def render(self) -> Text:
        """
        Render footer content with status and quit hint.
        """
        footer_text = f"{self.status_text} | Press 'q' to quit"
        text = Text(footer_text, style="bold green")
        # Center the text in the footer area
        text = text.center(self.size.width) if self.size.width else text
        return text
