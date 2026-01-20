"""Tests for guard receipt evaluation and verification."""

from __future__ import annotations

import tempfile
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard.core import receipt as receipt_engine


def _base_envelope() -> dict:
    return {
        "trace_id": "trace-123",
        "capability_token_ref": "cap-token-abc",
    }


def test_invalid_token_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            capability_token={"status": "invalid"},
        )
        assert receipt.decision == "BLOCK"
        assert receipt.token_status == "invalid_token"


def test_high_risk_requires_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            discernment={"risk_level": "high"},
            capability_token={"valid": True},
        )
        assert receipt.decision == "REQUIRE_CONFIRM"


def test_receipt_tamper_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            capability_token={"valid": True},
        )
        payload = receipt.to_dict()
        payload["constraints"]["timeout_s"] = 999
        ok, reason = receipt_engine.verify_receipt(payload)
        assert not ok
        assert reason == "signature_mismatch"
