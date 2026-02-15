Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none

# Client Lifecycle Pipeline

Client session entry is command-driven, registry-declared, and deterministic.

Authoritative contracts:
- `schema/session/session_stage.schema`
- `schema/session/session_pipeline.schema`
- `schema/session/session_artifacts.schema`
- `data/registries/session_stage_registry.json`
- `data/registries/session_pipeline_registry.json`

## Canonical Stage Order

1. `stage.resolve_session`
2. `stage.acquire_world`
3. `stage.verify_world`
4. `stage.warmup_simulation`
5. `stage.warmup_presentation`
6. `stage.session_ready`
7. `stage.session_running`
8. `stage.suspend_session`
9. `stage.resume_session`
10. `stage.teardown_session`

## Transition Rules

- Stage transitions happen only through canonical commands declared in registry-backed transition rules.
- Direct stage jumps are refused with `refusal.stage_invalid_transition`.
- Server-side transition checks refuse with `refusal.server_stage_mismatch` when client stage transitions skip declared order.
- Server-side authority checks refuse with `refusal.server_authority_violation` when authority binding differs from SessionSpec.
- `client.session.begin` is the explicit transition from `stage.session_ready` to `stage.session_running`.
- Re-entry starts at `stage.resolve_session` and re-validates artifacts before returning to `stage.session_ready` or `stage.session_running`.

## Determinism Contract

- Transition order is stable and validated against `allowed_next_stage_ids`.
- Refusals are stable and contract-bound:
  - `refusal.stage_invalid_transition`
  - `refusal.resume_incompatible`
  - `refusal.resume_hash_mismatch`
  - `refusal.resume_identity_violation`
- Lifecycle transitions do not execute simulation ticks.

## Warm-Up Contract

- Simulation warm-up is deterministic and explicit:
  `rng_streams_initialized>macro_capsules_seeded>fields_initialized>agent_shells_initialized>authority_policies_bound`.
- Presentation warm-up is deterministic and explicit:
  `layout_loaded>renderer_backend_loaded>input_mappings_loaded>camera_defaults_prepared`.
- `session.simulation.time_advanced` stays `0` through warm-up and `SessionReady`.

## SessionReady Contract

- `stage.session_ready` requires:
  - `session_spec`
  - `universe_identity`
  - `universe_state`
  - `registry_bundle`
  - `lockfile`
  - `authority_context`
- `simulation_time.tick` MUST equal `0` and no tick may execute before `client.session.begin`.
- `client.session.inspect`, `client.session.map.open`, `client.session.stats`, and `client.session.replay.toggle`
  are allowed only in `stage.session_ready`.
- `client.session.begin` is the only command that transitions to `stage.session_running`.
- Re-entry triggers (`network_drop`, `client_restart`, `authority_change`) route through
  `stage.resolve_session -> stage.acquire_world -> stage.verify_world -> stage.warmup_simulation -> stage.warmup_presentation -> stage.session_ready`.
