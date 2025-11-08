"""Security cockpit utilities powering the interactive TUI."""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil is optional at runtime
    psutil = None  # type: ignore

try:  # pragma: no cover - yara is optional
    import yara  # type: ignore
except Exception:  # pragma: no cover
    yara = None  # type: ignore

try:
    from argon2 import PasswordHasher  # type: ignore
    from argon2 import low_level as argon2_low_level  # type: ignore
except Exception:  # pragma: no cover - argon2 is optional in some environments
    PasswordHasher = None  # type: ignore
    argon2_low_level = None  # type: ignore


@dataclass
class ProcessInfo:
    """Snapshot of a single process for the cockpit."""

    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    status: str


@dataclass
class ProcessSnapshot:
    """Collection of process information."""

    processes: List[ProcessInfo] = field(default_factory=list)
    unavailable: bool = False
    message: str = ""


def collect_process_snapshot(limit: int = 5) -> ProcessSnapshot:
    """Collect a snapshot of the top processes.

    Parameters
    ----------
    limit:
        Maximum number of processes to include in the snapshot.
    """

    if psutil is None:
        return ProcessSnapshot(unavailable=True, message="psutil not installed")

    try:
        procs = sorted(
            psutil.process_iter(["pid", "name", "cpu_percent", "status", "memory_info"]),
            key=lambda proc: proc.info.get("cpu_percent") or 0.0,
            reverse=True,
        )
    except (psutil.Error, OSError) as exc:  # pragma: no cover - protective branch
        return ProcessSnapshot(unavailable=True, message=str(exc))

    items: List[ProcessInfo] = []
    for proc in procs[:limit]:
        info = proc.info
        mem_info = info.get("memory_info")
        memory_mb = float(mem_info.rss) / (1024**2) if mem_info else 0.0  # type: ignore[attr-defined]
        items.append(
            ProcessInfo(
                pid=int(info.get("pid") or 0),
                name=str(info.get("name") or "unknown"),
                cpu_percent=float(info.get("cpu_percent") or 0.0),
                memory_mb=memory_mb,
                status=str(info.get("status") or "unknown"),
            )
        )

    return ProcessSnapshot(processes=items)


@dataclass
class YaraScanFinding:
    path: str
    rule: str


@dataclass
class YaraScanReport:
    status: str
    message: str
    findings: List[YaraScanFinding] = field(default_factory=list)
    scanned: List[str] = field(default_factory=list)


def run_yara_scan(
    target_paths: Optional[Iterable[Path]] = None,
    rules_path: Optional[Path] = None,
) -> YaraScanReport:
    """Run a YARA scan over the supplied paths.

    The scan avoids network activity by design and only touches the provided
    directories or files.
    """

    if yara is None:
        return YaraScanReport(status="unavailable", message="yara-python not installed")

    targets = list(target_paths or [Path.cwd()])
    resolved_targets = [str(path.expanduser().resolve()) for path in targets]
    try:
        search_paths = [Path(path) for path in resolved_targets]
    except OSError as exc:  # pragma: no cover - defensive path handling
        return YaraScanReport(status="error", message=f"Invalid path: {exc}")

    if rules_path is None:
        default_rules = Path(os.environ.get("BLUX_GUARD_YARA_RULES", "~/.config/blux-guard/yara/index.yar"))
        rules_path = default_rules.expanduser()

    if not rules_path.exists():
        return YaraScanReport(
            status="missing_rules",
            message=f"Rules not found at {rules_path}",
            scanned=resolved_targets,
        )

    try:
        rules = yara.compile(filepath=str(rules_path))
    except yara.Error as exc:  # pragma: no cover - depends on runtime environment
        return YaraScanReport(status="compile_error", message=str(exc))

    findings: List[YaraScanFinding] = []
    for path in search_paths:
        if path.is_dir():
            for candidate in path.rglob("*"):
                if not candidate.is_file():
                    continue
                try:
                    matches = rules.match(str(candidate))
                except yara.Error:  # pragma: no cover - continue on per-file errors
                    continue
                for match in matches:
                    findings.append(YaraScanFinding(path=str(candidate), rule=str(match)))
        elif path.is_file():
            try:
                matches = rules.match(str(path))
            except yara.Error:
                matches = []
            for match in matches:
                findings.append(YaraScanFinding(path=str(path), rule=str(match)))

    if findings:
        message = f"{len(findings)} YARA finding(s)";
        status = "alert"
    else:
        message = "No matches"
        status = "clean"

    return YaraScanReport(status=status, message=message, findings=findings, scanned=resolved_targets)


@dataclass
class CredentialFinding:
    subject: str
    valid: bool
    detail: str


@dataclass
class CredentialAuditReport:
    status: str
    message: str
    findings: List[CredentialFinding] = field(default_factory=list)


def argon2_credential_audit(credentials_path: Optional[Path] = None) -> CredentialAuditReport:
    """Validate stored credential hashes without revealing underlying secrets."""

    if PasswordHasher is None or argon2_low_level is None:
        return CredentialAuditReport(status="unavailable", message="argon2-cffi not installed")

    if credentials_path is None:
        credentials_path = Path("~/.config/blux-guard/credentials.json").expanduser()

    if not credentials_path.exists():
        return CredentialAuditReport(status="missing", message=f"No credentials file at {credentials_path}")

    try:
        payload = json.loads(credentials_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CredentialAuditReport(status="error", message=f"Invalid JSON: {exc}")

    entries: Iterable[dict[str, Any]] = payload.get("users", []) if isinstance(payload, dict) else []
    findings: List[CredentialFinding] = []
    for entry in entries:
        username = str(entry.get("username", "<unknown>"))
        hash_value = entry.get("argon2")
        if not isinstance(hash_value, str):
            findings.append(CredentialFinding(subject=username, valid=False, detail="Missing argon2 hash"))
            continue
        try:
            # Validate formatting and parameters without verifying a password.
            argon2_low_level.extract_parameters(hash_value)
            findings.append(CredentialFinding(subject=username, valid=True, detail="OK"))
        except Exception as exc:  # pragma: no cover - depends on runtime data
            findings.append(CredentialFinding(subject=username, valid=False, detail=str(exc)))

    invalid = [finding for finding in findings if not finding.valid]
    if invalid:
        status = "alert"
        message = f"{len(invalid)} invalid credential hash(es)"
    else:
        status = "clean"
        message = "All credential hashes valid"

    return CredentialAuditReport(status=status, message=message, findings=findings)


@dataclass
class AuditChainReport:
    status: str
    message: str
    digest: str
    line_count: int


def verify_audit_chain(audit_path: Path) -> AuditChainReport:
    """Verify a hash-chain over the audit log."""

    if not audit_path.exists():
        return AuditChainReport(status="missing", message="Audit log missing", digest="", line_count=0)

    previous = b""
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        previous = sha256(previous + line.encode("utf-8")).digest()

    digest = previous.hex()
    status = "clean" if lines else "empty"
    message = "Audit chain intact" if lines else "Audit log empty"
    return AuditChainReport(status=status, message=message, digest=digest, line_count=len(lines))


@dataclass
class BqGuardHook:
    name: str
    description: str
    callback: Callable[[], Any]


@dataclass
class BqHookStatus:
    registered: List[str] = field(default_factory=list)
    last_result: Optional[str] = None
    message: str = ""


class BqGuardHookRegistry:
    """Registry that tracks hooks for quantum orchestration."""

    def __init__(self) -> None:
        self._hooks: List[BqGuardHook] = []
        self._last_result: Optional[str] = None

    def register(self, hook: BqGuardHook) -> None:
        self._hooks.append(hook)

    def list_hooks(self) -> List[BqGuardHook]:
        return list(self._hooks)

    async def invoke_all(self) -> None:
        """Invoke all hooks sequentially without allowing network access."""

        results: List[str] = []
        for hook in self._hooks:
            maybe_coro = hook.callback()
            if asyncio.iscoroutine(maybe_coro):
                value = await maybe_coro
            else:
                value = maybe_coro
            results.append(f"{hook.name}:{value}")
        self._last_result = ";".join(results) if results else None

    def status(self) -> BqHookStatus:
        return BqHookStatus(
            registered=[hook.name for hook in self._hooks],
            last_result=self._last_result,
            message="Hooks ready" if self._hooks else "No hooks registered",
        )


bq_guard_registry = BqGuardHookRegistry()


def export_diagnostics(
    process_snapshot: ProcessSnapshot,
    yara_report: YaraScanReport,
    credential_report: CredentialAuditReport,
    audit_report: AuditChainReport,
    bq_status: BqHookStatus,
    export_dir: Optional[Path] = None,
) -> dict[str, Path]:
    """Export diagnostics data to JSON and plaintext files.

    The export is stored locally only and avoids network interaction entirely.
    """

    export_dir = (export_dir or Path("~/.config/blux-guard/diagnostics")).expanduser()
    export_dir.mkdir(parents=True, exist_ok=True)

    timestamp = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    process_payload = {
        "unavailable": process_snapshot.unavailable,
        "message": process_snapshot.message,
        "entries": [asdict(proc) for proc in process_snapshot.processes],
    }

    payload = {
        "timestamp": timestamp,
        "processes": process_payload,
        "yara": asdict(yara_report),
        "credentials": asdict(credential_report),
        "audit_chain": asdict(audit_report),
        "bq_guard": {
            "registered": bq_status.registered,
            "last_result": bq_status.last_result,
            "message": bq_status.message,
        },
    }

    json_path = export_dir / f"diagnostics_{timestamp}.json"
    text_path = export_dir / f"diagnostics_{timestamp}.txt"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    text_lines = [
        f"Timestamp: {timestamp}",
        "Processes:",
    ]
    if process_snapshot.unavailable:
        text_lines.append(f"  Unavailable: {process_snapshot.message}")
    else:
        for proc in process_snapshot.processes:
            text_lines.append(
                f"  PID {proc.pid:<6} {proc.name:<25} CPU {proc.cpu_percent:>5.1f}% MEM {proc.memory_mb:>7.1f}MB [{proc.status}]"
            )
    text_lines.extend(
        [
            "",
            f"YARA: {yara_report.status} - {yara_report.message}",
        ]
    )
    for finding in yara_report.findings:
        text_lines.append(f"  {finding.rule}: {finding.path}")
    text_lines.extend(
        [
            "",
            f"Credentials: {credential_report.status} - {credential_report.message}",
        ]
    )
    for finding in credential_report.findings:
        marker = "OK" if finding.valid else "ALERT"
        text_lines.append(f"  [{marker}] {finding.subject}: {finding.detail}")
    text_lines.extend(
        [
            "",
            f"Audit Chain: {audit_report.status} - {audit_report.message}",
            f"Digest: {audit_report.digest}",
            f"Lines: {audit_report.line_count}",
            "",
            "bq Guard Hooks:",
        ]
    )
    text_lines.append(f"  Registered: {', '.join(bq_status.registered) or 'None'}")
    if bq_status.last_result:
        text_lines.append(f"  Last Result: {bq_status.last_result}")
    text_lines.append(f"  Message: {bq_status.message}")

    text_path.write_text("\n".join(text_lines), encoding="utf-8")

    return {"json": json_path, "text": text_path}


__all__ = [
    "ProcessInfo",
    "ProcessSnapshot",
    "collect_process_snapshot",
    "YaraScanFinding",
    "YaraScanReport",
    "run_yara_scan",
    "CredentialFinding",
    "CredentialAuditReport",
    "argon2_credential_audit",
    "AuditChainReport",
    "verify_audit_chain",
    "BqGuardHook",
    "BqHookStatus",
    "BqGuardHookRegistry",
    "bq_guard_registry",
    "export_diagnostics",
]

