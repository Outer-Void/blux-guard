# Guard Role: Mechanical Enforcement Layer

## Responsibilities (Allowed)
- Emit guard receipts from validated envelopes and include deterministic constraints.
- Operate without elevated privileges; all checks and mitigations stay in user space.
- Keep enforcement deterministic, auditable, and protocol-scoped.
- Report constraint mismatches without attempting escalation.

## Explicit Non-Goals
- No privilege elevation mechanisms of any kind.
- No kernel hooks, kernel-level modules, or privileged network/OS controls.
- No token issuance or verification logic.
- No policy or ethics reasoning.
- No control-plane services, daemons, servers, or orchestration.
- Guard does not run tools or spawn shells.
