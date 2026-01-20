"""Registry/key verification integration for BLUX Guard."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from ..core import telemetry


@dataclass(frozen=True)
class TokenVerification:
    token: str
    valid: bool
    token_ref: str
    reason_codes: List[str]
    metadata: Dict[str, str]


def _parse_verifier_payload(payload: Dict[str, str], token: str) -> TokenVerification:
    valid = bool(payload.get("valid")) or payload.get("status") == "valid" or payload.get("state") == "active"
    token_ref = payload.get("token_ref") or payload.get("id") or payload.get("ref") or token
    reasons = payload.get("reason_codes") or []
    if isinstance(reasons, str):
        reasons = [reasons]
    if not reasons:
        reasons = ["token.valid" if valid else "token.invalid"]
    return TokenVerification(
        token=token,
        valid=valid,
        token_ref=token_ref,
        reason_codes=[str(item) for item in reasons],
        metadata={k: str(v) for k, v in payload.items() if k not in {"reason_codes"}},
    )


def verify_token(token: str, *, revocations: Optional[Iterable[str]] = None) -> TokenVerification:
    if revocations and token in set(revocations):
        return TokenVerification(
            token=token,
            valid=False,
            token_ref=token,
            reason_codes=["token.revoked"],
            metadata={"status": "revoked"},
        )
    try:
        result = subprocess.run(
            ["blux-reg", "verify", "--token", token],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        telemetry.record_event(
            "reg.verify",
            actor="integration",
            payload={"status": "unavailable", "reason": "cli_missing"},
        )
        return TokenVerification(
            token=token,
            valid=False,
            token_ref=token,
            reason_codes=["token.verifier_unavailable"],
            metadata={"status": "unavailable"},
        )

    if result.returncode != 0:
        telemetry.record_event(
            "reg.verify",
            actor="integration",
            payload={"status": "failed", "code": str(result.returncode)},
        )
        return TokenVerification(
            token=token,
            valid=False,
            token_ref=token,
            reason_codes=["token.verify_failed"],
            metadata={"status": "failed", "stderr": result.stderr.strip()},
        )

    payload: Dict[str, str] = {}
    try:
        payload = json.loads(result.stdout.strip() or "{}")
    except json.JSONDecodeError:
        payload = {"status": "unknown", "message": result.stdout.strip()}

    telemetry.record_event(
        "reg.verify",
        actor="integration",
        payload={"status": payload.get("status", "ok"), "token_ref": payload.get("token_ref")},
    )
    return _parse_verifier_payload(payload, token)


def verify_tokens(tokens: Sequence[str], *, revocations: Optional[Iterable[str]] = None) -> List[TokenVerification]:
    return [verify_token(token, revocations=revocations) for token in tokens]


def verify_operator_key() -> Dict[str, str]:
    """Legacy registry verification."""

    telemetry.record_event("reg.verify", actor="integration", payload={"status": "stub"})
    return {"status": "unknown", "message": "Registry verification stubbed"}
