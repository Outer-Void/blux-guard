# Troubleshooting

## Common Issues

### Permission Denied for Telemetry
- **Symptom**: Errors writing to `~/.config/blux-guard/logs`.
- **Fix**: Create the directory manually (`mkdir -p ~/.config/blux-guard/logs`) or set
  `BLUX_GUARD_TELEMETRY=off`.

### SQLite Locked
- **Symptom**: Warning indicating the telemetry database is locked.
- **Fix**: The application continues; optionally vacuum or delete `telemetry.db`. Warnings appear only once when
  `BLUX_GUARD_TELEMETRY_WARN=once`.

### Unsupported Python Version
- **Symptom**: Startup exits with a message requiring Python 3.9+.
- **Fix**: Upgrade Python to at least 3.9 or use the provided installers for your platform.

## Getting Help

See `SUPPORT.md` for escalation paths and contact channels.
