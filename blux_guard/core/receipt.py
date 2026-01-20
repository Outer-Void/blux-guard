"""Guard receipt issuance utilities."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from jsonschema import Draft202012Validator

from blux_guard import audit
from blux_guard.contracts import phase0 as phase0_contracts

GUARD_RECEIPT_SCHEMA_ID = "blux://contracts/guard_receipt.schema.json"
_DEFAULT_MAPPING = Path(__file__).resolve().parents[1] / "guard" / "mapping" / "default_mapping.json"
_MAPPING_CACHE: Dict[str, Any] | None = None


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


def _load_mapping(path: Optional[Path] = None) -> Dict[str, Any]:
    global _MAPPING_CACHE
    if _MAPPING_CACHE is None:
        mapping_path = path or _DEFAULT_MAPPING
        _MAPPING_CACHE = json.loads(mapping_path.read_text(encoding="utf-8"))
    return dict(_MAPPING_CACHE)


def _normalize_flag(value: Any) -> Optional[str]:
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized or None
    return None


def _resolve_decision(discernment: Optional[Dict[str, Any]], mapping: Dict[str, Any]) -> tuple[str, List[str]]:
    decision = str(mapping.get("default_decision", "ALLOW"))
    reason_codes: List[str] = []
    if not discernment:
        reason_codes.append("discernment.none")
        reason_codes.append(f"decision.{decision.lower()}")
        return decision, reason_codes

    order = mapping.get("order", ["band", "uncertainty"])
    band = _normalize_flag(discernment.get("band"))
    uncertainty = _normalize_flag(discernment.get("uncertainty"))

    for key in order:
        if key == "band" and band:
            reason_codes.append(f"band.{band}")
            decision = mapping.get("band", {}).get(band, decision)
        if key == "uncertainty" and uncertainty:
            reason_codes.append(f"uncertainty.{uncertainty}")
            decision = mapping.get("uncertainty", {}).get(uncertainty, decision)

    reason_codes.append(f"decision.{decision.lower()}")
    return decision, reason_codes


def _default_env_allowlist() -> Iterable[str]:
    return ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "HOME")


def _default_env_denylist() -> Iterable[str]:
    return ("AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN")


def _resolve_environment(envelope: Dict[str, Any]) -> Dict[str, List[str]]:
    environment = envelope.get("environment")
    allowlist: Iterable[str] = _default_env_allowlist()
    denylist: Iterable[str] = _default_env_denylist()
    if isinstance(environment, dict):
        allowlist = environment.get("allowlist", allowlist)
        denylist = environment.get("denylist", denylist)
    allowlist = envelope.get("env_allowlist", allowlist)
    denylist = envelope.get("env_denylist", denylist)
    return {"allowlist": list(allowlist), "denylist": list(denylist)}


def _resolve_constraints(envelope: Dict[str, Any], decision: str) -> Dict[str, Any]:
    working_dir = str(Path(envelope.get("working_dir", Path.cwd())))
    allowed_commands = envelope.get("allowed_commands")
    if allowed_commands is None:
        command = envelope.get("command")
        allowed_commands = [command] if command else []
    allowed_paths = envelope.get("allowed_paths") or []
    if decision == "ALLOW" and not allowed_commands and not allowed_paths:
        allowed_paths = [working_dir]

    environment = _resolve_environment(envelope)
    allowlists = {
        "commands": list(allowed_commands),
        "paths": list(allowed_paths),
        "environment": list(environment.get("allowlist", [])),
    }
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
        "allowed_commands": list(allowed_commands) or None,
        "allowed_paths": list(allowed_paths) or None,
        "network": envelope.get("network", {"egress": "restricted"}),
        "environment": environment,
        "allowlists": allowlists,
        "confirmation_required": decision == "REQUIRE_CONFIRM",
    }
    return {key: value for key, value in constraints.items() if value is not None}


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
    bindings: Dict[str, Any]

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
            "bindings": self.bindings,
        }


def issue_guard_receipt(
    input_envelope: Dict[str, Any],
    discernment_report: Optional[Dict[str, Any]] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    _validate_schema(input_envelope, "request_envelope.schema.json")
    if discernment_report is not None:
        _validate_schema(discernment_report, "discernment_report.schema.json")

    trace_id = str(input_envelope.get("trace_id", str(uuid.uuid4())))
    mapping = _load_mapping()
    decision, reason_codes = _resolve_decision(discernment_report, mapping)
    constraints = _resolve_constraints(input_envelope, decision)

    envelope_hash = input_envelope.get("envelope_hash")
    capability_refs_list = list(capability_refs or input_envelope.get("capability_refs") or [])
    bindings: Dict[str, Any] = {"trace_id": trace_id}
    if envelope_hash:
        bindings["envelope_hash"] = envelope_hash
    if capability_refs_list:
        bindings["capability_refs"] = capability_refs_list

    capability_token_ref = str(
        input_envelope.get("capability_token_ref")
        or (capability_refs_list[0] if capability_refs_list else "unbound")
    )

    receipt_payload = {
        "$schema": GUARD_RECEIPT_SCHEMA_ID,
        "receipt_id": str(uuid.uuid4()),
        "issued_at": time.time(),
        "decision": decision,
        "trace_id": trace_id,
        "capability_token_ref": capability_token_ref,
        "token_status": "unverified",
        "reason_codes": reason_codes or ["unspecified"],
        "constraints": constraints,
        "discernment": {
            "band": _normalize_flag((discernment_report or {}).get("band")),
            "uncertainty": _normalize_flag((discernment_report or {}).get("uncertainty")),
            "summary": (discernment_report or {}).get("summary"),
        },
        "signature": {"alg": "none", "value": "unsigned"},
        "bindings": bindings,
    }

    _validate_schema(receipt_payload, "guard_receipt.schema.json")

    audit.record(
        "guard.receipt.issued",
        actor="guard",
        payload={
            "receipt_id": receipt_payload["receipt_id"],
            "trace_id": trace_id,
            "decision": decision,
            "reason_codes": reason_codes or ["unspecified"],
            "constraints": constraints,
            "issued_at": receipt_payload["issued_at"],
        },
    )

    bypass_signal = input_envelope.get("guard_bypass") or input_envelope.get("bypass")
    if bypass_signal:
        audit.record(
            "guard.bypass",
            actor="guard",
            payload={"trace_id": trace_id, "signal": bypass_signal},
        )

    return GuardReceipt(
        receipt_id=receipt_payload["receipt_id"],
        issued_at=receipt_payload["issued_at"],
        decision=decision,
        trace_id=trace_id,
        capability_token_ref=capability_token_ref,
        token_status=receipt_payload["token_status"],
        reason_codes=receipt_payload["reason_codes"],
        constraints=constraints,
        discernment=receipt_payload["discernment"],
        signature=receipt_payload["signature"],
        bindings=bindings,
    )


def evaluate_receipt(
    envelope: Dict[str, Any],
    *,
    discernment: Optional[Dict[str, Any]] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    return issue_guard_receipt(
        envelope,
        discernment_report=discernment,
        capability_refs=capability_refs,
    )


def evaluate_from_files(
    envelope_path: Path,
    discernment_path: Optional[Path] = None,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    discernment = json.loads(discernment_path.read_text(encoding="utf-8")) if discernment_path else None
    return issue_guard_receipt(
        envelope,
        discernment_report=discernment,
        capability_refs=capability_refs,
    )
