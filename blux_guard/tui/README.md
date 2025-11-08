# BLUX Guard Developer Security Cockpit

The Textual cockpit now focuses on secure developer operations. It extends the legacy guard interface with new security instrumentation while remaining fully compatible with `initiate_cockpit.py`.

## Panels

- **Metrics** – summarizes log locations, telemetry enablement, and Prometheus heartbeat values.
- **Processes** – surfaces the top processes by CPU/memory to spot runaway builds.
- **Doctrine** – displays BLUX Doctrine alignment and policy counts using `doctrine_integration`.
- **Audit Tail** – tails the JSONL audit stream with best-effort degradation if storage is unavailable.
- **YARA Scanner** – runs local rule packs against configurable paths (no network usage).
- **Credentials** – performs Argon2 metadata validation for stored credential files.
- **Audit Chain** – replays the audit log hash chain to confirm integrity.
- **bq Guard Hooks** – reports quantum orchestration hooks registered via `security_cockpit.bq_guard_registry`.
- **Shell** – launches a sandboxed PTY (`sandbox.launch_interactive_shell`) capable of running editors and build tools.
- **Footer/Header** – Textual status chrome with clock and refresh hotkeys.

## Key Bindings

- `Ctrl+C` – exit the cockpit.
- `r` – refresh all passive panels.
- `p` – refresh process metrics immediately.
- `y` – run a YARA scan against the configured targets.
- `c` – audit Argon2 credential hashes.
- `a` – recompute the audit hash chain digest.
- `b` – invoke registered bq guard hooks.
- `e` – export diagnostics to JSON and plaintext under `~/.config/blux-guard/diagnostics`.
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
