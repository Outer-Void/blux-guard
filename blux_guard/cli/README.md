# bluxq Command Reference

The Quantum namespace CLI wraps the legacy BLUX Guard tooling with developer-focused commands while maintaining backward compatibility.

## Guard Commands

```bash
bluxq guard status            # JSON status snapshot
bluxq guard tui --mode dev    # launch cockpit (dev|secure|ops)
```

## Developer Suite Commands

```bash
bluxq dev init                # provision secure workspace
bluxq dev shell               # enter sandboxed PTY
bluxq dev build               # guarded build pipeline
bluxq dev scan .              # run security scanning
bluxq dev deploy --safe       # deployment with rollback guard
bluxq dev doctrine --check    # enforce doctrine alignment
```

## Legacy Compatibility

```bash
bluxq legacy                  # forwards to blux_cli.blux
```

All commands record telemetry using best-effort logging. Set `BLUX_GUARD_TELEMETRY=off` to disable log writes or `BLUX_GUARD_TELEMETRY_WARN=once` to print a single degrade notice when storage is unavailable.
