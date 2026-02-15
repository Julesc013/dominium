Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none

# Session Ready And Running

`stage.session_ready` is a deterministic stop-state before simulation time advances.

Reference contracts:
- `schema/session/session_stage.schema`
- `schema/session/session_pipeline.schema`
- `data/registries/session_stage_registry.json`
- `data/registries/session_pipeline_registry.json`

## stage.session_ready Contract

- `world_ready=1` and `camera_placed=1` are required.
- `session.simulation.time_advanced` is always `0`.
- `universe_state.simulation_time.tick` MUST equal `0`.
- `agent_actions_executed` is always `0`.
- Allowed commands in this state:
  - `client.session.stage`
  - `client.session.inspect`
  - `client.session.map.open`
  - `client.session.stats`
  - `client.session.replay.toggle`
  - `client.session.begin`
  - `client.session.abort`

## stage.session_running Contract

- Entered only by explicit `client.session.begin`.
- `client.session.begin` is refused unless the pipeline stage is `stage.session_ready`.
- Direct `ready -> running` bypasses are forbidden; transitions must satisfy `allowed_next_stage_ids`.
- Abort/resume/re-entry are validated against lockfile + registry hashes + universe identity invariants.
- Re-entry commands:
  - `client.session.reentry.network_drop`
  - `client.session.reentry.client_restart`
  - `client.session.reentry.authority_change`
- Re-entry returns through lifecycle stages and re-establishes `stage.session_ready` before running.
