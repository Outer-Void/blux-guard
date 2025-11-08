# Configuration Reference

BLUX Guard ships with defaults under `blux_guard/config/default.yaml` and optional local overrides in
`blux_guard/config/local.yaml`.

## YAML Schema

```yaml
sandbox:
  shell: /bin/bash       # Override per-platform shell
  network: restricted    # or "open"
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

## Platform-Specific Tips

- **Termux** — set `sandbox.shell` to `/data/data/com.termux/files/usr/bin/bash` if needed.
- **Windows** — use `sandbox.shell: powershell` and ensure `pyyaml` handles Windows paths with double backslashes.
- **macOS** — add `sandbox.shell: /bin/zsh` for Zsh environments.

## Doctrine Integration

`core/doctrine_integration.py` reads doctrine manifests from `/blux-doctrine`. Provide environment-specific
paths with `BLUX_GUARD_DOCTRINE_ROOT` if the directory is elsewhere.

## Examples

See the `examples/` directory for sample configuration snippets and doctrine templates.
