Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# SERVER-MVP1 Retro Audit

## Existing Client Start Surface

- `tools/mvp/runtime_entry.py` provided deterministic bootstrap argument parsing only.
- `tools/mvp/runtime_bundle.py` already pinned:
  - `profile_bundle`
  - `pack_lock`
  - `SessionSpec` defaults
- no local server supervisor existed in the client path.

## Existing Server Start Surface

- `src/server/server_boot.py` already supported:
  - deterministic session materialization
  - contract bundle enforcement
  - pack lock validation
  - mod policy validation
  - overlay conflict policy validation
- `src/server/server_main.py` already exposed CLI-only status/list/snapshot/diag stubs.

## Transport Constraint

- `src/net/transport/loopback.py` is deterministic but process-local.
- consequence:
  - true subprocess client/server loopback cannot handshake yet
  - an in-proc authoritative stub is required for SERVER-MVP-1 connectivity
  - subprocess spawning can still be prepared as a deterministic abstraction for future APPSHELL/IPC work

## Existing Log Handling

- server runtime already recorded `server_mvp_console_log` rows in runtime state, but no client-facing stream existed.
- proof anchors were already emitted from `src/server/runtime/tick_loop.py`.

## Integration Points Chosen

- local orchestration enters through a new client-side controller instead of the viewer shell render path.
- server console actions are factored into a shared command module so:
  - headless CLI
  - local loopback control channel
  use the same governed command surface.

## Risks Found

- no subprocess-safe transport yet
- no attachable control channel yet
- no local authority profile gate in the client boot path yet

## Resolution Direction

- add deterministic process spawn abstraction now
- keep active local singleplayer authority path in-proc until IPC replaces process-local loopback
- gate local authority to `server.profile.private_relaxed`
- expose minimal control messages:
  - `status`
  - `save_snapshot`
