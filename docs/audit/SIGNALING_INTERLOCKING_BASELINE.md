Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MOB-8 Signaling and Interlocking Baseline

Status: Baseline implemented for MOB-8 (signals, right-of-way, deterministic interlocking).
Date: 2026-03-03

## Constitutional and Invariant Alignment

- Determinism preserved:
  - Signal evaluation order is stable (`signal_id` sort).
  - Interlocking/refusal outcomes use deterministic ordering and fingerprints.
  - Budget degradation is explicit and deterministic.
- Process-only mutation preserved:
  - Signal aspects change only through `process.signal_set_aspect` / `process.signal_tick`.
  - Switch lock state changes only through `process.switch_lock` / `process.switch_unlock` or deterministic `signal_tick` interlocking evaluation.
  - Block reservations created only through `process.route_reserve_blocks`.
- No wall-clock dependence:
  - All updates are tick-driven.

## Signal Engine Behavior

Implemented in:
- `src/mobility/signals/signal_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

Core behavior:
- Signals are canonical rows (`mobility_signals`) bound to state machines.
- Rule policy resolution is registry-driven (`signal_rule_policy_registry`).
- Aspect evaluation uses:
  - edge occupancy (MOB-5),
  - switch state (MOB-2),
  - block reservations,
  - hazard state.
- Aspects supported in baseline:
  - `stop`
  - `caution`
  - `clear`
- Deterministic transition selection prefers transitions valid from current machine state.

## Interlocking Rules

Implemented controls:
- Switch lock while occupied/reserved:
  - `process.signal_tick` can set/clear switch locks deterministically.
- Manual/intent switch throws are refused when unsafe:
  - `process.switch_set_state` refuses with `refusal.mob.signal_violation` if lock/occupancy/reservation blocks the transition.
- Block reservation process:
  - `process.route_reserve_blocks` creates deterministic reservation windows over itinerary edges.
  - Reservation conflict resolution is deterministic.

## Micro Solver Integration (MOB-6)

Integration point:
- `process.mobility_micro_tick` in `tools/xstack/sessionx/process_runtime.py`

Behavior:
- Before edge/junction progression, controlling signal aspect is sampled.
- `stop`:
  - speed cap forced to zero,
  - deterministic braking/hold behavior applied.
- `caution`:
  - deterministic speed cap reduction applied.
- Decision influence is recorded (`DecisionLog` rows and `mobility_signal_control_decisions`).

## Failure and Maintenance Hooks

Implemented hooks:
- `process.signal_hazard_set` for hazard activation/deactivation.
- `process.signal_maintenance_tick` for deterministic schedule-driven maintenance events.
- Failure/maintenance events are recorded for replay and inspection.

## Registries, Schemas, and CompatX

Schemas:
- `schema/mobility/signal.schema`
- `schema/mobility/signal_rule_policy.schema`
- `schema/mobility/block_reservation.schema`

Registries:
- `data/registries/signal_type_registry.json`
- `data/registries/signal_rule_policy_registry.json`

Registry compile integration:
- `tools/xstack/registry_compile/{compiler.py,constants.py,lockfile.py}`
- `tools/xstack/sessionx/runner.py`
- `tools/xstack/compatx/version_registry.json`
- compiled schemas:
  - `schemas/signal_type_registry.schema.json`
  - `schemas/signal_rule_policy_registry.schema.json`

## Enforcement and Audit Coverage

RepoX invariants added:
- `INV-SIGNALS-STATE-MACHINE-ONLY`
- `INV-NO-ADHOC-STOP-LOGIC`
- `INV-INTERLOCKING-POLICY-DRIVEN`

AuditX analyzers added:
- `SignalBypassSmell` (`E156_SIGNAL_BYPASS_SMELL`)
- `AdHocInterlockingSmell` (`E157_ADHOC_INTERLOCKING_SMELL`)

## TestX Coverage

Added tests:
- `test_signal_aspect_deterministic`
- `test_switch_lock_refusal`
- `test_route_reservation_conflict_deterministic`
- `test_micro_solver_respects_stop`
- `test_budget_degrade_signal_processing_deterministic`

## Gate Run Summary

Executed:
- RepoX FAST: pass (with baseline warnings).
- AuditX FAST: pass (with baseline warnings).
- TestX MOB-8 subset: pass.
- Strict build: registry compile passes; strict aggregate still reports refusal due unrelated global baseline gates in repository.
- Topology map generation executed.

## Extension Points (SIG series road/air)

- Additional signal types can be added by registry only (`signal_type_registry`) without engine refactor.
- Additional policy tables can be added by registry only (`signal_rule_policy_registry`) for road lights, air waypoint clearance, and future interlocking packs.
- Signal networking/communications (SIG series) can layer on top of the existing process/state-machine and reservation model without violating process-only mutation.
