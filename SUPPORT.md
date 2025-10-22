# Support

## Channels

- **Security Incidents**: Email security@outervoid.example (PGP key available upon request).
- **General Support**: Open an issue on GitHub with the `[support]` label.
- **Enterprise Engagements**: Contact enterprise@outervoid.example for onboarding assistance.

## Response Targets

- Critical security reports: 24 hours.
- Operational outages: 1 business day.
- Documentation or usage questions: 3 business days.

## Version Support Policy

- Active development tracks the `main` branch.
- Maintenance: latest tagged release receives backports for critical fixes.
- Older branches transition to community support only.

## Self-Service Resources

- `TROUBLESHOOTING.md` for quick fixes.
- `OPERATIONS.md` for runbook procedures.
- `CONFIGURATION.md` for customizing runtime behavior.

## Before Contacting Support

Collect the following diagnostics to accelerate triage:

- Output from `bluxq guard status` and `bluxq guard self-check`.
- Any stderr messages printed when running with `--debug` or `--verbose` flags.
- Confirmation of telemetry directory permissions or overrides (`BLUX_GUARD_LOG_DIR`).
