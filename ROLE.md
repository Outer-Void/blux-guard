# BLUX Guard Role

BLUX Guard provides enforcement-only receipt issuance with deterministic, userland constraints.

## Explicit Non-Capabilities
- Does not run tools or execute commands.
- Does not sandbox-run commands or spawn shells.
- Does not issue or verify tokens.
- Does not interpret doctrine, policy, or ethics.
- Can be bypassed by design, but emits audit logs when a bypass signal is provided.
