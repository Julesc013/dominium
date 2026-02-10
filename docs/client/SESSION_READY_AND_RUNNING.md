Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Session Ready And Running

`SessionReady` is a deterministic stop-state before simulation time advances.

## SessionReady Contract

- `world_ready=1` and `camera_placed=1` are required.
- `session.simulation.time_advanced` is always `0`.
- `agent_actions_executed` is always `0`.
- Allowed commands in this state:
  - `client.session.inspect`
  - `client.session.map.open`
  - `client.session.stats`
  - `client.session.replay.toggle`
  - `client.session.begin`

## SessionRunning Contract

- Entered only by explicit `client.session.begin`.
- `client.session.begin` is refused unless the pipeline stage is `SessionReady`.
- Re-entry commands:
  - `client.session.reentry.network_drop`
  - `client.session.reentry.client_restart`
  - `client.session.reentry.authority_change`
- Re-entry returns through lifecycle stages and re-establishes `SessionReady` before running.
