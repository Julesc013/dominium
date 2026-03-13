Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/SUPERVISOR_MODEL.md`, `docs/appshell/IPC_DISCOVERY.md`, and `docs/appshell/IPC_ATTACH_CONSOLES.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Supervisor Surface Map

## Inventory

| Surface | Path | Class | Purpose | Readiness | Attach | Log Merge | Crash Policy | Wallclock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| process_spawn | src/runtime/process_spawn.py | canonical | deterministic process spawn abstraction | none | none | none | none | none |
| args_canonicalizer | src/appshell/supervisor/args_canonicalizer.py | canonical | stable flag ordering, quoting, and arg hashing | none | none | none | none | none |
| supervisor_engine | src/appshell/supervisor/supervisor_engine.py | canonical | spawn, readiness, attach, log merge, restart, and diag capture | bounded negotiated readiness | attach_ipc_endpoint + query_ipc_status | stable sort by source_product_id/channel_id/seq_no | bounded restarts with iteration backoff and diag capture | none |
| launcher_commands | src/appshell/commands/command_engine.py | canonical | launcher command entrypoints for start/status/stop/attach | delegated to supervisor_engine | delegated to supervisor_engine | status payload only | delegated to supervisor_engine | none |
| supervisor_service | tools/appshell/supervisor_service.py | canonical | persistent launcher-owned supervisor host | engine.start + endpoint server readiness | AppShellIPCEndpointServer | delegated to supervisor_engine | delegated to supervisor_engine | none |
| runtime_probe | tools/appshell/appshell6_probe.py | canonical | deterministic supervisor replay probe | launcher start/status/stop replay | attach_supervisor_children | aggregated log snapshot hash | probe only | none |

## Notes

- Process spawning is centralized in `src/runtime/process_spawn.py`.
- Readiness is driven by child ready handshakes plus bounded negotiated IPC attach/status verification.
- Log aggregation is stable by `(source_product_id, channel_id, seq_no, endpoint_id, event_id)`.
- Crash handling captures a diag bundle before restart decisions are evaluated.
