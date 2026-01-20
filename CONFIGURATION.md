# Configuration Reference

BLUX Guard ships with defaults under `blux_guard/config/default.yaml` and optional local overrides in
`blux_guard/config/local.yaml`.

## YAML Schema

```yaml
telemetry:
  log_dir: ~/.config/blux-guard/logs
  enabled: true
  warn_once: true
api:
  host: 0.0.0.0
  port: 8000
```

## Override Mechanics

1. The project reads `config/default.yaml` first.
2. If `config/local.yaml` exists, keys merge over defaults without altering the tracked file.
3. Environment variables take precedence when provided (e.g., `BLUX_GUARD_LOG_DIR`).

## Examples

See the `examples/` directory for sample configuration snippets.
