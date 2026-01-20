"""Guard receipt evaluation and verification utilities."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from hashlib import sha256
from hmac import new as hmac_new
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from jsonschema import Draft202012Validator

from blux_guard import audit
from blux_guard.integrations import reg as reg_integration
from blux_guard.contracts import phase0 as phase0_contracts

_DEFAULT_SECRET = "blux-guard-dev-secret"
_SIGNATURE_ALG = "HMAC-SHA256"
GUARD_RECEIPT_SCHEMA_ID = "blux://contracts/guard_receipt.schema.json"


def _receipt_secret() -> str:
    return os.environ.get("BLUX_GUARD_RECEIPT_SECRET", _DEFAULT_SECRET)


def _canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sign_payload(payload: Dict[str, Any], secret: str) -> str:
    digest = hmac_new(secret.encode("utf-8"), _canonical_json(payload).encode("utf-8"), sha256)
    return digest.hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = Path(phase0_contracts.__file__).with_name(schema_name)
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate_schema(payload: Dict[str, Any], schema_name: str) -> None:
    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.path)
    if errors:
        messages = "; ".join(
            f"{schema_name}:{'/'.join([str(p) for p in err.path])}:{err.message}"
            for err in errors
        )
        raise ValueError(f"Schema validation failed: {messages}")


def _parse_risk_level(discernment: Optional[Dict[str, Any]]) -> Optional[str]:
    if not discernment:
        return None
    level = discernment.get("risk_level")
    if isinstance(level, str):
        return level.lower()
    return None


def _collect_reason_codes() -> List[str]:
    return []


def _default_env_allowlist() -> Iterable[str]:
    return ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "HOME")


def _default_env_denylist() -> Iterable[str]:
    return ("AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN")


@dataclass(frozen=True)
class GuardReceipt:
    receipt_id: str
    issued_at: float
    decision: str
    trace_id: str
    capability_token_ref: str
    constraints: Dict[str, Any]
    token_status: str
    reason_codes: List[str]
    discernment: Dict[str, Any]
    signature: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "$schema": GUARD_RECEIPT_SCHEMA_ID,
            "receipt_id": self.receipt_id,
            "issued_at": self.issued_at,
            "decision": self.decision,
            "trace_id": self.trace_id,
            "capability_token_ref": self.capability_token_ref,
            "token_status": self.token_status,
            "reason_codes": self.reason_codes,
            "constraints": self.constraints,
            "discernment": self.discernment,
            "signature": self.signature,
        }


def evaluate_receipt(
    envelope: Dict[str, Any],
    *,
    discernment: Optional[Dict[str, Any]] = None,
    capability_tokens: Optional[Sequence[str]] = None,
    revocations: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    _validate_schema(envelope, "request_envelope.schema.json")
    if discernment is not None:
        _validate_schema(discernment, "discernment_report.schema.json")

    trace_id = envelope.get("trace_id", str(uuid.uuid4()))
    token_ref = envelope.get("capability_token_ref", "unknown")
    provided_tokens = list(capability_tokens or envelope.get("capability_tokens") or [])
    if not provided_tokens:
        single = envelope.get("capability_token")
        if isinstance(single, str):
            provided_tokens = [single]

    reason_codes = _collect_reason_codes()
    token_status = "missing"
    token_valid = False
    if provided_tokens:
        verification = reg_integration.verify_tokens(
            provided_tokens, revocations=set(revocations or [])
        )
        token_valid = all(result.valid for result in verification)
        token_status = "valid" if token_valid else "invalid"
        if verification and verification[0].token_ref:
            token_ref = verification[0].token_ref
        for result in verification:
            reason_codes.extend(result.reason_codes)
    else:
        reason_codes.append("token.missing")

    decision = "ALLOW"
    risk_level = _parse_risk_level(discernment)
    posture = (discernment or {}).get("posture")
    requires_confirmation = (discernment or {}).get("requires_confirmation") is True
    if not token_valid:
        decision = "BLOCK"
        if "token.invalid" not in reason_codes:
            reason_codes.append("token.invalid")
    elif risk_level in {"critical"}:
        decision = "BLOCK"
        reason_codes.append("risk.critical")
    elif risk_level in {"high"}:
        decision = "REQUIRE_CONFIRM"
        reason_codes.append("risk.high")
    elif risk_level in {"medium"} and posture in {"low", "degraded"}:
        decision = "REQUIRE_CONFIRM"
        reason_codes.append("posture.low")
    elif risk_level in {"medium"}:
        decision = "WARN"
        reason_codes.append("risk.medium")
    elif requires_confirmation:
        decision = "REQUIRE_CONFIRM"
        reason_codes.append("discernment.confirmation")
    else:
        reason_codes.append("risk.low")

    working_dir = str(Path(envelope.get("working_dir", Path.cwd())))
    allowed_commands = envelope.get("allowed_commands")
    if allowed_commands is None:
        command = envelope.get("command")
        allowed_commands = [command] if command else []
    allowed_paths = envelope.get("allowed_paths")
    if not allowed_commands and not allowed_paths and decision == "ALLOW":
        allowed_paths = [working_dir]

    constraints = {
        "receipt_required": True,
        "allowlist_execution": True,
        "working_dir": working_dir,
        "sandbox_profile": envelope.get("sandbox_profile", "userland"),
        "timeout_s": envelope.get("timeout_s", 300),
        "resource_limits": envelope.get(
            "resource_limits",
            {"cpu_seconds": 120, "memory_mb": 512, "processes": 64},
        ),
        "allowed_commands": allowed_commands or None,
        "allowed_paths": allowed_paths or None,
        "network": envelope.get("network", {"egress": "restricted"}),
        "environment": {
            "allowlist": list(envelope.get("env_allowlist", _default_env_allowlist())),
            "denylist": list(envelope.get("env_denylist", _default_env_denylist())),
        },
        "confirmation_required": decision == "REQUIRE_CONFIRM",
    }
    constraints = {key: value for key, value in constraints.items() if value is not None}

    receipt_payload = {
        "$schema": GUARD_RECEIPT_SCHEMA_ID,
        "receipt_id": str(uuid.uuid4()),
        "issued_at": time.time(),
        "decision": decision,
        "trace_id": trace_id,
        "capability_token_ref": token_ref,
        "token_status": token_status,
        "reason_codes": reason_codes or ["unspecified"],
        "constraints": constraints,
        "discernment": {
            "risk_level": risk_level,
            "posture": posture,
            "summary": (discernment or {}).get("summary"),
        },
    }
    secret = _receipt_secret()
    signature_value = _sign_payload(receipt_payload, secret)
    receipt_payload["signature"] = {"alg": _SIGNATURE_ALG, "value": signature_value}

    _validate_schema(receipt_payload, "guard_receipt.schema.json")

    audit.record(
        "guard.receipt.issued",
        actor="guard",
        payload={
            "decision": decision,
            "trace_id": trace_id,
            "capability_token_ref": token_ref,
            "constraints_hash": sha256(_canonical_json(constraints).encode("utf-8")).hexdigest(),
        },
    )

    return GuardReceipt(
        receipt_id=receipt_payload["receipt_id"],
        issued_at=receipt_payload["issued_at"],
        decision=decision,
        trace_id=trace_id,
        capability_token_ref=token_ref,
        token_status=token_status,
        reason_codes=receipt_payload["reason_codes"],
        constraints=constraints,
        discernment=receipt_payload["discernment"],
        signature=receipt_payload["signature"],
    )


def verify_receipt(receipt: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        _validate_schema(receipt, "guard_receipt.schema.json")
    except ValueError as exc:
        return False, str(exc)

    signature = receipt.get("signature") or {}
    if signature.get("alg") != _SIGNATURE_ALG or "value" not in signature:
        return False, "invalid_signature_metadata"

    payload = dict(receipt)
    payload.pop("signature", None)
    expected = _sign_payload(payload, _receipt_secret())
    if expected != signature.get("value"):
        return False, "signature_mismatch"

    return True, "ok"


def evaluate_from_files(
    envelope_path: Path,
    discernment_path: Optional[Path] = None,
    tokens: Optional[Sequence[str]] = None,
    revocations_path: Optional[Path] = None,
) -> GuardReceipt:
    envelope = _load_json(envelope_path)
    discernment = _load_json(discernment_path) if discernment_path else None
    revocations: Optional[Sequence[str]] = None
    if revocations_path:
        payload = _load_json(revocations_path)
        if isinstance(payload, list):
            revocations = [str(item) for item in payload]
        elif isinstance(payload, dict):
            revocations = [str(item) for item in payload.get("revoked_tokens", [])]
    return evaluate_receipt(
        envelope,
        discernment=discernment,
        capability_tokens=tokens,
        revocations=revocations,
    )
