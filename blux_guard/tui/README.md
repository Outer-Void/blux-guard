# BLUX Guard Developer Suite TUI

The Textual cockpit extends the legacy guard interface with developer-focused panels while remaining fully compatible with `initiate_cockpit.py`.

## Panels

- **Metrics** – summarizes log locations, telemetry enablement, and Prometheus heartbeat values.
- **Doctrine** – displays BLUX Doctrine alignment and policy counts using `doctrine_integration`.
- **Audit** – tails the JSONL audit stream with best-effort degradation if storage is unavailable.
- **Shell** – launches a sandboxed PTY (`sandbox.launch_interactive_shell`) capable of running editors and build tools.
- **Footer/Header** – Textual status chrome with clock and refresh hotkeys.

## Key Bindings

- `Ctrl+C` – exit the cockpit.
- `r` – refresh doctrine, metrics, and audit panels.
- `Enter` inside the shell panel – start a sandboxed shell session.

## Telemetry Awareness

Shell launches and PTY commands record to the `devshell.jsonl` stream. When the telemetry directory cannot be created the panels continue operating, emit a single degrade warning on stderr when `BLUX_GUARD_TELEMETRY_WARN=once`, and avoid raising exceptions.

## Launching

```bash
bluxq guard tui --mode dev
```

The legacy entry point remains available:

```bash
python initiate_cockpit.py
```
