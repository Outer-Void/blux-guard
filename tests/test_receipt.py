"""Tests for guard receipt evaluation and verification."""

from __future__ import annotations

import tempfile
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blux_guard.core import receipt as receipt_engine
from blux_guard.integrations import reg as reg_integration


def _base_envelope() -> dict:
    return {
        "trace_id": "trace-123",
        "capability_token_ref": "cap-token-abc",
    }


def _stub_verifications(valid: bool) -> list[reg_integration.TokenVerification]:
    return [
        reg_integration.TokenVerification(
            token="token-1",
            valid=valid,
            token_ref="token-ref-1",
            reason_codes=["token.valid" if valid else "token.invalid"],
            metadata={},
        )
    ]


def test_invalid_token_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        monkeypatch.setattr(reg_integration, "verify_tokens", lambda *args, **kwargs: _stub_verifications(False))
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            capability_tokens=["token-1"],
        )
        assert receipt.decision == "BLOCK"
        assert receipt.token_status == "invalid"
        assert "token.invalid" in receipt.reason_codes


def test_high_risk_requires_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        monkeypatch.setattr(reg_integration, "verify_tokens", lambda *args, **kwargs: _stub_verifications(True))
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            discernment={"risk_level": "high"},
            capability_tokens=["token-1"],
        )
        assert receipt.decision == "REQUIRE_CONFIRM"


def test_valid_token_allows(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        monkeypatch.setattr(reg_integration, "verify_tokens", lambda *args, **kwargs: _stub_verifications(True))
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            capability_tokens=["token-1"],
        )
        payload = receipt.to_dict()
        assert receipt.decision == "ALLOW"
        assert "sandbox_profile" in receipt.constraints
        assert "network" in receipt.constraints
        assert receipt.constraints.get("allowed_commands") or receipt.constraints.get("allowed_paths")
        assert payload["$schema"] == receipt_engine.GUARD_RECEIPT_SCHEMA_ID


def test_receipt_tamper_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        monkeypatch.setattr(reg_integration, "verify_tokens", lambda *args, **kwargs: _stub_verifications(True))
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            capability_tokens=["token-1"],
        )
        payload = receipt.to_dict()
        payload["constraints"]["timeout_s"] = 999
        ok, reason = receipt_engine.verify_receipt(payload)
        assert not ok
        assert reason == "signature_mismatch"


def test_low_posture_medium_risk_requires_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("BLUX_GUARD_LOG_DIR", tmpdir)
        monkeypatch.setenv("BLUX_GUARD_RECEIPT_SECRET", "test-secret")
        monkeypatch.setattr(reg_integration, "verify_tokens", lambda *args, **kwargs: _stub_verifications(True))
        envelope = _base_envelope()
        receipt = receipt_engine.evaluate_receipt(
            envelope,
            discernment={"risk_level": "medium", "posture": "low"},
            capability_tokens=["token-1"],
        )
        assert receipt.decision == "REQUIRE_CONFIRM"
