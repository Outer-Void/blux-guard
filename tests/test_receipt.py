"""Tests for guard receipt issuance."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard.core import receipt as receipt_engine


def _base_envelope() -> dict:
    return {
        "trace_id": "trace-123",
        "working_dir": "/tmp/workdir",
    }


def test_mechanical_receipt_includes_constraints() -> None:
    receipt = receipt_engine.issue_guard_receipt(_base_envelope())
    payload = receipt.to_dict()
    assert receipt.constraints.get("allowed_paths")
    assert payload["$schema"] == receipt_engine.GUARD_RECEIPT_SCHEMA_ID


def test_bindings_include_trace_id() -> None:
    receipt = receipt_engine.issue_guard_receipt(_base_envelope())
    assert receipt.bindings["trace_id"] == "trace-123"
