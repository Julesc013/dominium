Status: DERIVED
Last Reviewed: 2026-03-02
Supersedes: none
Superseded By: none
Scope: MOB-7 micro free motion
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MICRO_FREE_MOTION Baseline

## Constitutional and Contract Coverage
- Invariants upheld:
- `A1` deterministic updates, stable ordering by `subject_id`.
- `A2` process-only mutation through `process.mobility_free_tick`.
- `A4` no mode-flag branching introduced.
- `A10` explicit downgrade and incident signaling, no silent fallback.
- Contracts/schemas impacted:
- Added `schema/mobility/free_motion_state.schema`.
- Added `schema/mobility/free_motion_policy.schema`.
- Added compiled schemas:
- `schemas/free_motion_state.schema.json`
- `schemas/free_motion_policy.schema.json`
- Added CompatX version registration:
- `tools/xstack/compatx/version_registry.json` entries for `free_motion_state`, `free_motion_policy`.

## Solver Behavior
- Authoritative free-motion tick path: `process.mobility_free_tick`.
- Deterministic order: `subject_ids` and ROI lists are token-sorted before updates.
- Inputs used per subject:
- free-motion state row (`subject_id` / `body_id` / velocity / acceleration)
- control input (throttle, brake, vector controls)
- field snapshot (friction, wind, visibility)
- active effects (speed cap, traction, drift, visibility)
- free-motion policy + traction/wind model rows
- Integration:
- deterministic kinematic step through `src/mobility/micro/free_motion_solver.py::step_free_motion`
- EB collision resolution through process runtime collision path (`_resolve_body_collisions`)
- state persistence via `_persist_mobility_free_state` and `_persist_vehicle_state`.

## Corridor and Volume Constraints
- Constraints supported for free-motion subjects:
- `constraint.follow_corridor`
- `constraint.follow_volume`
- Runtime integrates constraint presence checks against `mobility_constraint_type_registry`.
- Corridor enforcement policy is deterministic:
- `clamp`: projected/clamped back inside bounds
- `refuse`: movement canceled, velocity reset to zero
- `warn`: movement allowed with explicit incident signaling.

## Field and Effect Integration
- FieldLayer sampling is done through `field_modifier_snapshot`; no ad-hoc weather flags.
- Deterministic field influences:
- friction/traction modifies effective acceleration
- wind vector adds drift acceleration
- visibility drives warning and auto speed-cap effects.
- Auto effects emitted by process:
- `effect.visibility_reduction`
- `effect.speed_cap`
- Decision/fidelity entries include field influence metadata.

## Spec and Safety Hooks
- Spec hooks active in free-motion tick:
- max speed enforcement from spec params (`max_speed_mm_per_tick` or `max_speed_kph`)
- visibility floor hook from spec params (`min_visibility_permille`) with incident logging.
- Safety violations emit explicit travel incidents (no silent correction only).

## UX and Diegetic Instrumentation
- Runtime instrument rows emitted under `state.mobility_free_instruments`:
- speed estimate
- wind vector
- visibility
- corridor/volume status
- Incidents captured under `state.mobility_free_incidents`:
- off-corridor/off-volume
- collision
- drift
- visibility warning.

## Multiplayer and Reenactment Hooks
- ROI-only authoritative execution enforced via required `roi_subject_ids`.
- Budget gating:
- `max_subject_updates_per_tick`
- deterministic deferred set + optional downgrade to meso tier
- fidelity decision entries with `degrade.mob.free_budget`.
- lockstep metadata:
- per-tick `lockstep_anchor` hash persisted in `state.mobility_free_runtime_state`
- deterministic `reenactment_event_ids` index persisted for same-tick incident replay lookup.
- Reenactment hooks:
- incident details persisted in deterministic travel-event stream (`incident_stub` records)
- per-tick incident summaries in `mobility_free_incidents`.

## Enforcement
- RepoX invariants added:
- `INV-FREE-MOTION-ROI-ONLY`
- `INV-NO-ADHOC-FRICTION-WIND`
- `INV-POSITION-UPDATES-PROCESS-ONLY`
- AuditX analyzer added:
- `E155_DIRECT_VELOCITY_MUTATION_SMELL` (`DirectVelocityMutationSmell`)

## TestX Coverage
- `testx.mobility.free_motion_deterministic`
- `testx.mobility.corridor_clamp_deterministic`
- `testx.mobility.friction_affects_accel`
- `testx.mobility.wind_drift_effect`
- `testx.mobility.free.budget_downgrade_logged`
- `testx.mobility.free.collision_resolution_integration`

## Validation Summary (This Baseline)
- RepoX:
- `python tools/xstack/repox/check.py --repo-root . --profile FAST` => `status=pass` (warnings present in existing workspace baseline).
- AuditX:
- `python tools/xstack/auditx/check.py --repo-root . --profile FAST` => `status=pass` (warnings from existing run-meta/baseline artifacts).
- TestX (MOB-7 subset):
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset ...` => `status=pass` for all six MOB-7 tests.
- Strict pipeline:
- `python tools/xstack/run.py strict --cache on` => `result=refusal` in this workspace baseline:
- `compatx` findings, `repox` findings, global `testx` failures, and `packagingx` lab build refusal.
- MOB-7 subset tests passed independently under FAST profile.

## Extension Points
- Aerodynamics domain:
- replace/augment `wind.basic_drift` with domain-specific lift/drag models while retaining deterministic process wrapper.
- Buoyancy domain:
- add water/surface coupling policy rows without changing free-motion state contract.
- Orbital dynamics:
- map `free.default_space_stub` to advanced solver handoff behind same process and policy gates.
