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

GUARD_RECEIPT_SCHEMA_ID = "blux://contracts/guard_receipt.schema.json"
_CONTRACTS_ROOT = Path(__file__).resolve().parents[2] / "contracts" / "phase0"


def _load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = _CONTRACTS_ROOT / schema_name
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


def _resolve_constraints(envelope: Dict[str, Any]) -> Dict[str, Any]:
    working_dir = str(Path(envelope.get("working_dir", Path.cwd())))
    allowed_commands = envelope.get("allowed_commands")
    if allowed_commands is None:
        command = envelope.get("command")
        allowed_commands = [command] if command else []
    allowed_paths = envelope.get("allowed_paths") or []
    if not allowed_commands and not allowed_paths:
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
    }
    return {key: value for key, value in constraints.items() if value is not None}


@dataclass(frozen=True)
class GuardReceipt:
    receipt_id: str
    issued_at: float
    trace_id: str
    constraints: Dict[str, Any]
    bindings: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "$schema": GUARD_RECEIPT_SCHEMA_ID,
            "receipt_id": self.receipt_id,
            "issued_at": self.issued_at,
            "trace_id": self.trace_id,
            "constraints": self.constraints,
            "bindings": self.bindings,
        }


def issue_guard_receipt(
    input_envelope: Dict[str, Any],
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    _validate_schema(input_envelope, "request_envelope.schema.json")

    trace_id = str(input_envelope.get("trace_id", str(uuid.uuid4())))
    constraints = _resolve_constraints(input_envelope)

    envelope_hash = input_envelope.get("envelope_hash")
    capability_refs_list = list(capability_refs or input_envelope.get("capability_refs") or [])
    bindings: Dict[str, Any] = {"trace_id": trace_id}
    if envelope_hash:
        bindings["envelope_hash"] = envelope_hash
    if capability_refs_list:
        bindings["capability_refs"] = capability_refs_list

    receipt_payload = {
        "$schema": GUARD_RECEIPT_SCHEMA_ID,
        "receipt_id": str(uuid.uuid4()),
        "issued_at": time.time(),
        "trace_id": trace_id,
        "constraints": constraints,
        "bindings": bindings,
    }

    _validate_schema(receipt_payload, "guard_receipt.schema.json")

    audit.record(
        "guard.receipt.issued",
        actor="guard",
        payload={
            "receipt_id": receipt_payload["receipt_id"],
            "trace_id": trace_id,
            "constraints": constraints,
            "issued_at": receipt_payload["issued_at"],
        },
    )

    return GuardReceipt(
        receipt_id=receipt_payload["receipt_id"],
        issued_at=receipt_payload["issued_at"],
        trace_id=trace_id,
        constraints=constraints,
        bindings=bindings,
    )


def evaluate_receipt(
    envelope: Dict[str, Any],
    *,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    return issue_guard_receipt(
        envelope,
        capability_refs=capability_refs,
    )


def evaluate_from_files(
    envelope_path: Path,
    capability_refs: Optional[Sequence[str]] = None,
) -> GuardReceipt:
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    return issue_guard_receipt(envelope, capability_refs=capability_refs)
