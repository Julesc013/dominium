Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Phase: APPSHELL-6

# APPSHELL6 Retro Audit

## Existing Surfaces

- `src/runtime/process_spawn.py` already provides deterministic Python process specs and portable spawn helpers.
- `src/appshell/logging/log_engine.py` already provides console, file, and ring sinks with deterministic event IDs.
- `src/appshell/ipc/ipc_transport.py`, `src/appshell/ipc/ipc_endpoint_server.py`, and `src/appshell/ipc/ipc_client.py` already provide local negotiated IPC with monotonic per-channel sequence numbers.
- `tools/launcher/launch.py` is already AppShell-backed and is the correct product surface for supervision commands.

## Required Integration Points

- Add a supervisor runtime that validates packs/contracts before spawning children.
- Reuse APPSHELL-4 IPC instead of inventing a new attach protocol.
- Aggregate child logs from structured IPC log queries, not ad hoc stdout scraping.
- Preserve deterministic boot by using bounded polling iterations and ready payloads instead of wall-clock timeouts.

## Risks Identified

- Existing child spawns had no writable stdin, so deterministic stop control would not work until fixed.
- Existing launcher command registry had no first-class `launcher start|stop|status|attach` command family.
- Existing TUI status/log panels did not surface supervised process state or aggregated logs.
