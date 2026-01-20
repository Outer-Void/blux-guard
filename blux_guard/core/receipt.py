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
from typing import Any, Dict, Iterable, Optional, Tuple

from blux_guard import audit

_DEFAULT_SECRET = "blux-guard-dev-secret"
_SIGNATURE_ALG = "HMAC-SHA256"


def _receipt_secret() -> str:
    return os.environ.get("BLUX_GUARD_RECEIPT_SECRET", _DEFAULT_SECRET)


def _canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sign_payload(payload: Dict[str, Any], secret: str) -> str:
    digest = hmac_new(secret.encode("utf-8"), _canonical_json(payload).encode("utf-8"), sha256)
    return digest.hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_risk_level(discernment: Optional[Dict[str, Any]]) -> Optional[str]:
    if not discernment:
        return None
    level = discernment.get("risk_level")
    if isinstance(level, str):
        return level.lower()
    return None


def _validate_token(token: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not token:
        return False, "missing_token"
    if token.get("valid") is True or token.get("status") == "valid" or token.get("state") == "active":
        return True, "valid"
    return False, "invalid_token"


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
    discernment: Dict[str, Any]
    signature: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "issued_at": self.issued_at,
            "decision": self.decision,
            "trace_id": self.trace_id,
            "capability_token_ref": self.capability_token_ref,
            "token_status": self.token_status,
            "constraints": self.constraints,
            "discernment": self.discernment,
            "signature": self.signature,
        }


def evaluate_receipt(
    envelope: Dict[str, Any],
    *,
    discernment: Optional[Dict[str, Any]] = None,
    capability_token: Optional[Dict[str, Any]] = None,
) -> GuardReceipt:
    trace_id = envelope.get("trace_id", str(uuid.uuid4()))
    token_ref = envelope.get("capability_token_ref", "unknown")
    token_valid, token_status = _validate_token(capability_token)

    decision = "ALLOW"
    risk_level = _parse_risk_level(discernment)
    if not token_valid:
        decision = "BLOCK"
    elif risk_level in {"critical"}:
        decision = "BLOCK"
    elif risk_level in {"high"} or (discernment or {}).get("requires_confirmation") is True:
        decision = "REQUIRE_CONFIRM"
    elif risk_level in {"medium"}:
        decision = "WARN"

    working_dir = str(Path(envelope.get("working_dir", Path.cwd())))
    allowlist = envelope.get("allowed_commands")
    if allowlist is None:
        command = envelope.get("command")
        allowlist = [command] if command else []

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
        "allowed_commands": allowlist,
        "filesystem_allowlist": envelope.get("filesystem_allowlist", [working_dir]),
        "network_policy": envelope.get("network_policy", {"egress": "restricted"}),
        "environment_scrub": {
            "allowlist": list(envelope.get("env_allowlist", _default_env_allowlist())),
            "denylist": list(envelope.get("env_denylist", _default_env_denylist())),
        },
        "confirmation_required": decision == "REQUIRE_CONFIRM",
    }

    receipt_payload = {
        "receipt_id": str(uuid.uuid4()),
        "issued_at": time.time(),
        "decision": decision,
        "trace_id": trace_id,
        "capability_token_ref": token_ref,
        "token_status": token_status,
        "constraints": constraints,
        "discernment": {
            "risk_level": risk_level,
            "summary": (discernment or {}).get("summary"),
        },
    }
    secret = _receipt_secret()
    signature_value = _sign_payload(receipt_payload, secret)
    receipt_payload["signature"] = {"alg": _SIGNATURE_ALG, "value": signature_value}

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
        constraints=constraints,
        discernment=receipt_payload["discernment"],
        signature=receipt_payload["signature"],
    )


def verify_receipt(receipt: Dict[str, Any]) -> Tuple[bool, str]:
    required = [
        "receipt_id",
        "issued_at",
        "decision",
        "trace_id",
        "capability_token_ref",
        "constraints",
        "signature",
    ]
    missing = [field for field in required if field not in receipt]
    if missing:
        return False, f"missing_fields:{','.join(missing)}"

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
) -> GuardReceipt:
    envelope = _load_json(envelope_path)
    discernment = _load_json(discernment_path) if discernment_path else None
    capability_token = envelope.get("capability_token")
    return evaluate_receipt(
        envelope,
        discernment=discernment,
        capability_token=capability_token,
    )
