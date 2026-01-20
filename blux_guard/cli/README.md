# bluxq Command Reference

The Quantum namespace CLI provides developer-focused commands for guard operations.

## Guard Commands

```bash
bluxq guard status            # JSON status snapshot
bluxq guard tui --mode dev    # launch cockpit (dev|secure|ops)
bluxq guard evaluate --request-envelope envelope.json --capability-ref CAP_REF
```

## Developer Suite Commands

```bash
bluxq dev init                # provision secure workspace
bluxq dev build               # guarded build pipeline
bluxq dev scan .              # run security scanning
bluxq dev deploy --safe       # deployment with rollback guard
```

All commands record telemetry using best-effort logging. Set `BLUX_GUARD_TELEMETRY=off` to disable log writes or `BLUX_GUARD_TELEMETRY_WARN=once` to print a single degrade notice when storage is unavailable.
