Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Phase: APPSHELL-6

# Supervisor Baseline

## Orchestration Flows

- `launcher start` validates packs/contracts, spawns the launcher supervisor service, and emits a deterministic run manifest.
- The supervisor service spawns persistent child product hosts in deterministic order.
- `launcher status` reports process state, aggregated logs, and attach status.
- `launcher stop` performs graceful shutdown in client then server order.

## Manifest Format

The run manifest records:

- seed
- session template id
- profile bundle hash
- pack lock hash
- contract bundle hash
- ordered process rows with binary hash and args hash

## Crash Handling

- crash state is detected on deterministic supervisor refresh boundaries
- diag snapshot bundles are emitted per crashed child
- restart is only applied when the active supervisor policy permits it

## Current Scope

- portable local-only orchestration
- negotiated IPC attach for logs, console, and status
- deterministic aggregated log file at `dist/runtime/supervisor/aggregated_logs.jsonl`

## Next Phase Readiness

This baseline is ready for:

- DIAG-0 full repro bundles
- richer launcher/session supervisor commands
- future APPSHELL supervisor panels and process groups
