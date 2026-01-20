# Guard Role: Enforcement Layer (Userland Only)

## Responsibilities (Allowed)
- Enforce request receipts by applying userland constraints to Guard actions.
- Emit receipts with ALLOW/WARN/REQUIRE_CONFIRM/BLOCK outcomes and explicit constraints.
- Operate without elevated privileges; all checks and mitigations stay in user space.
- Keep enforcement deterministic, auditable, and protocol-scoped.
- Report violations and constraint mismatches without attempting escalation.

## Explicit Non-Goals
- No root requirement or privileged escalation mechanisms of any kind.
- No kernel hooks, kernel-level modules, or privileged network/OS controls.
- No token issuance, minting, or authentication logic.
- No policy or ethics reasoning; doctrine and cA decisions live elsewhere.
- No changes to blux-ecosystem contracts.
