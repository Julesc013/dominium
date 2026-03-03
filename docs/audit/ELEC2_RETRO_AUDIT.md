# ELEC2 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-03
Scope: ELEC-2 `Protection, Faults, Grounding, and Coordination`

## Findings

1. Breaker overload handling already routes through SAFETY patterns in `process.elec.network_tick`:
- Overload context emits `safety.breaker_trip` instances.
- `_apply_safety_actions` applies `flow_disconnect` deterministically.

2. Fault state is not yet a first-class electrical artifact:
- No canonical `fault_state` rows exist.
- No electrical fault hash chain is emitted for proofs/replay.

3. Current breaker/manual operation path is channel-oriented, not device-oriented:
- `process.elec.flip_breaker` and `process.elec.lockout_tagout` operate on `channel_id`.
- No separate `protection_device` rows or settings profile currently exist.

4. Lockout exists, but policy/state-machine gating is partial:
- `state["safety_lockouts"]` is populated.
- Reclose behavior is not consistently refused through explicit LOTO processes.

5. Grounding behavior is not modeled:
- No grounding policy registry or deterministic ground-fault proxy in E1 solve loop.

6. Ad-hoc fault checks do not appear outside electrical runtime path:
- No hidden breaker/fault admin bypass was found in `src/electric/` or session runtime.

## Migration Plan

1. Add canonical schemas and registries for:
- `fault_state`
- `protection_device`
- `protection_settings`
- `grounding_policy`

2. Introduce deterministic engines:
- `src/electric/fault/fault_engine.py`
- `src/electric/protection/protection_engine.py`

3. Integrate faults and trips in `process.elec.network_tick`:
- detect faults from E1 edge status + policies
- run deterministic coordination ordering
- apply trips through SAFETY pattern action path only

4. Introduce explicit LOTO processes:
- `process.elec_apply_loto`
- `process.elec_remove_loto`
- ensure reclose refusal while locked

5. Extend proof surface with:
- `fault_state_hash_chain`
- `trip_event_hash_chain`

6. Add RepoX/AuditX/TestX coverage for:
- no ad-hoc fault trip logic
- safety-only protection path
- deterministic co-ordination and budget degradation.
