"""Runtime helpers shared across CLI and daemon entry points."""

from __future__ import annotations

import sys
from typing import Iterable, Tuple


_MIN_VERSION: Tuple[int, int] = (3, 9)


def ensure_supported_python(component: str, *, minimum: Tuple[int, int] = _MIN_VERSION) -> None:
    """Exit gracefully when the interpreter is too old.

    Parameters
    ----------
    component:
        Human readable component identifier (e.g. ``"bluxq"``).
    minimum:
        Minimal accepted Python major/minor version tuple.
    """

    current = sys.version_info[:2]
    if current >= minimum:
        return

    message = (
        f"{component} requires Python {minimum[0]}.{minimum[1]} or newer. "
        f"Detected {current[0]}.{current[1]}. Please upgrade your interpreter."
    )
    print(message, file=sys.stderr)
    raise SystemExit(1)


def format_supported_versions(supported: Iterable[Tuple[int, int]] | None = None) -> str:
    """Format supported interpreter versions for help messages."""

    if not supported:
        supported = [(3, 9), (3, 10), (3, 11)]
    return ", ".join(f"{major}.{minor}" for major, minor in supported)
