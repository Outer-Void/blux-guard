# Troubleshooting

## Common Issues

### Missing Typer Dependency
- **Symptom**: `ModuleNotFoundError: typer` when running `bluxq`.
- **Fix**: Reinstall with `pip install -e .` to ensure the declared dependencies are installed.

### Permission Denied for Telemetry
- **Symptom**: Errors writing to `~/.config/blux-guard/logs`.
- **Fix**: Create the directory manually (`mkdir -p ~/.config/blux-guard/logs`) or set
  `BLUX_GUARD_TELEMETRY=off`.
- **Validate**: Run `bluxq guard self-check` to confirm the log directory is writable after fixes.

### SQLite Locked
- **Symptom**: Warning indicating the telemetry database is locked.
- **Fix**: The application continues; optionally vacuum or delete `telemetry.db`. Warnings appear only once when
  `BLUX_GUARD_TELEMETRY_WARN=once`.
- **Validate**: `bluxq guard self-check` reports the SQLite status in the summary output.

### Termux Storage Prompts
- **Symptom**: Termux denies storage access when launching the cockpit.
- **Fix**: Run `termux-setup-storage` and restart `bluxq`.

### Unsupported Python Version
- **Symptom**: Startup exits with a message requiring Python 3.9+.
- **Fix**: Upgrade Python to at least 3.9 or use the provided installers for your platform.

### Daemon Port Conflicts
- **Symptom**: `Address already in use` when starting `bluxqd`.
- **Fix**: Stop other processes on port 8000 or adjust the port in `config/local.yaml`.
- **Validate**: Start with `bluxqd --port 9000` and rerun `bluxq guard self-check` to confirm API reachability.

### Enabling Debug Output
- **Symptom**: Need deeper insight into CLI behaviour.
- **Fix**: Run commands with `bluxq --debug ...` or `bluxq --verbose ...` to mirror telemetry events to stderr.

## Getting Help

See `SUPPORT.md` for escalation paths and contact channels.
