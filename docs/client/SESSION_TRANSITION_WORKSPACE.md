Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Session Transition Workspace

The session transition workspace replaces loading-screen behavior with a stage-aware command workspace.

## Required Panels (NOW)

- `Progress`: semantic stage timeline, never percentage-only.
- `Progress` also reports warm-up execution steps for simulation and presentation.
- `Details`: lock hash, world hash, pack set hash, capability set, schema refs.
- `Details` includes `session.simulation.time_advanced` and must remain `0` during warm-up.
- `Details` also surfaces `world_ready`, `camera_placed`, `agent_actions_executed`,
  `map_open`, `stats_visible`, and `replay_recording_enabled`.
- `Messages`: warnings/refusals in deterministic order.
- `Actions`: `Cancel`, `Back`, `Fix`, `Continue` command surfaces.

## Stub Panels (SOON)

- `Preview Minimap`
- `Network Diagnostics`

Both are represented as explicit stubs and report deterministic refusal when unavailable.

## Deferred Panels (AAA)

- Cinematic transition overlays are deferred and documented only.

## Mode Parity

- CLI renders structured progress/events from the same stage stream.
- TUI and GUI map the same panel model from UI IR workspace data.
- Workspace definition lives in `client/ui/workspaces/session_transition/session_transition.default.json`.
