"""Integration layer for BLUX Doctrine and registry files."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Dict

from . import telemetry

_DOCTRINE_ROOT = pathlib.Path("/blux-doctrine")
_CACHE: Dict[str, Any] | None = None


def _load_doctrine() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    doctrine = {}
    if _DOCTRINE_ROOT.exists():
        for path in sorted(_DOCTRINE_ROOT.glob("**/*.json")):
            try:
                doctrine[path.stem] = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                doctrine[path.stem] = {"error": "invalid-json"}
    _CACHE = doctrine
    return doctrine


def ensure_doctrine_loaded() -> Dict[str, Any]:
    doctrine = _load_doctrine()
    telemetry.record_event("doctrine.load", {"items": len(doctrine)})
    return doctrine


def doctrine_score() -> float:
    doctrine = ensure_doctrine_loaded()
    if not doctrine:
        return 0.0
    return min(1.0, len(doctrine) / 10.0)
