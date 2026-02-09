Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Client Flow

## Scope

This document defines client-side orchestration flow only.
It does not define or alter simulation semantics.

## Canonical States

The client state machine declares:

- `BootProgress`
- `MainMenu`
- `SingleplayerWorldManager`
- `MultiplayerServerBrowser`
- `Options`
- `About`
- `SessionLaunching`
- `SessionRunning`
- `RefusalError`

State transitions are command-driven only.
UI code (CLI/TUI/GUI) dispatches commands and renders snapshots.

## Flow Summary

1. `client.boot.start`
2. `client.boot.progress_poll`
3. `client.menu.open`
4. one of:
   - `client.menu.select.singleplayer`
   - `client.menu.select.multiplayer`
   - `client.menu.select.options`
   - `client.menu.select.about`
5. session launch commands:
   - `client.world.play`
   - `client.server.connect`
6. runtime/replay/diagnostics commands while session is active

## Refusal Behavior

When command preconditions are not met:

- return deterministic refusal code
- include command id in output/log
- do not mutate authoritative state

Current bridge-level refusal codes:

- `REFUSE_CAPABILITY_MISSING`
- `REFUSE_INVALID_STATE`
- `REFUSE_UNAVAILABLE`

