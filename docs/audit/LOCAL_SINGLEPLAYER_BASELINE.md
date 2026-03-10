Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# Local Singleplayer Baseline

## Orchestration Flow

SERVER-MVP-1 now provides a deterministic local singleplayer controller that:

- materializes a pinned `SessionSpec`
- builds deterministic server spawn arguments
- boots a local authoritative server
- completes a bounded loopback ready handshake
- attaches a local client transport

The current connection-capable path is:

- process-preferred
- in-proc loopback active

This is explicit and documented, not a silent fallback.

## Control Channel Summary

The MVP control stub supports:

- `status`
- `save_snapshot`

Responses travel through deterministic loopback protocol messages:

- `server.control.request.stub.v1`
- `server.control.response.stub.v1`
- `server.console.log.stub.v1`

Server log events are tick-tagged and streamed through the same loopback connection.

## Crash / Diag Stub

On boot failure or supervised spawned-process exit:

- a local diag stub is emitted
- the diag includes:
  - seed
  - `pack_lock_hash`
  - `contract_bundle_hash`
  - `semantic_contract_registry_hash`
  - last captured log lines

## Readiness for Next Work

SERVER-MVP-1 is ready for:

- APPSHELL-0..4 command hosting and supervision work
- SERVER-MVP-1 successor work that swaps in real IPC/socket transport
- DIAG-0 richer diagnostic bundles

Known intentional limitations:

- no cross-process transport yet
- no full console attach shell yet
- no remote authority discovery
