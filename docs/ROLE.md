# Guard Role: Enforcement Layer (Userland Only)

## Responsibilities (Allowed)
- Enforce request receipts by applying userland constraints to Guard actions.
- Emit receipts with ALLOW/WARN/REQUIRE_CONFIRM/BLOCK outcomes and explicit constraints.
- Operate without elevated privileges; all checks and mitigations stay in user space.
- Keep enforcement deterministic, auditable, and protocol-scoped.
- Report violations and constraint mismatches without attempting escalation.

## Explicit Non-Goals
- No privilege elevation mechanisms of any kind.
- No kernel hooks, kernel-level modules, or privileged network/OS controls.
- No token issuance or verification logic.
- No policy or ethics reasoning.
- No changes to blux-ecosystem contracts.
- Guard does not run tools or spawn shells.
- Guard can be bypassed by design but emits an audit log entry when a bypass signal is provided.
