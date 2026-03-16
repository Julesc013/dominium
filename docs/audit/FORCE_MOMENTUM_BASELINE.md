Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FORCE & MOMENTUM BASELINE (PHYS-1)

Date: 2026-03-04  
Scope: PHYS-1 deterministic force/momentum substrate across process runtime, model coupling, proof hooks, and enforcement scaffolding.

## 1) Momentum State Model

Canonical PHYS-1 state/process schemas integrated:

- `schema/physics/momentum_state.schema`
- `schema/physics/force_application.schema`
- `schema/physics/impulse_application.schema`
- `schemas/momentum_state.schema.json`
- `schemas/force_application.schema.json`
- `schemas/impulse_application.schema.json`

Runtime substrate:

- `src/physics/momentum_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

Process mutation paths:

- `process.apply_force` (`delta_p = F * dt`)
- `process.apply_impulse` (`delta_p = J`)

Both mutation paths:

- update `momentum_states` only (authoritative substrate)
- append deterministic application rows
- refresh `momentum_hash_chain` and `impulse_event_hash_chain`
- emit deterministic decision metadata

## 2) ROI MOB Integration

`process.mobility_free_tick` now integrates ROI micro free-motion against momentum substrate:

- reads/creates `momentum_state` per ROI body
- derives velocity from momentum and mass during deterministic step solve
- integrates position in deterministic subject order
- persists updated momentum and kinetic observation artifacts
- remains budgeted and deterministic under ROI-only execution

Macro and meso tiers remain non-integrating for PHYS micro momentum, preserving tier contract discipline.

## 3) Gravity Stub via FIELD + META-MODEL

Gravity coupling is model-driven:

- model type: `model_type.phys_gravity_stub`
- constitutive model: `model.phys.gravity_stub`
- field input: `field.gravity.vector`
- output path: `process.apply_force` payload

`process.model_evaluate_tick`:

- auto-binds gravity model for target assemblies when profile enables gravity
- resolves gravity from FIELD sampling
- applies resulting force through momentum process pathway
- logs model output process events deterministically

## 4) Ledger & Observation Hooks

Momentum updates produce derived kinetic observations:

- quantity: `quantity.energy_kinetic`
- family: `OBSERVATION`
- source process: force/impulse/mobility/model pathways

Momentum-conservation enforcement by profile:

- external impulse rows are logged when declared
- unlogged external impulses emit `exception_event` (`conservation_violation`)
- exception artifacts are projected as INFO family `RECORD`

## 5) MECH/SAFETY Coupling

PHYS->MECH coupling is routed via hazard pathway:

- sudden impulse increments `hazard.structural_overload` (`model_hazard_rows`)
- coupling metadata includes `coupling_model_id = model.phys.impulse_structural_stub`
- large impulse thresholds emit safety hook events (`safety.structural_overload`)

No direct fracture mutation is introduced in PHYS-1.

## 6) Proof & Multiplayer Hooks

Control proof surfaces now include:

- `momentum_hash_chain`
- `impulse_event_hash_chain`

Server/hybrid emitters propagate both chains into proof bundle payloads:

- `src/net/policies/policy_server_authoritative.py`
- `src/net/srz/shard_coordinator.py`

Inspection exposure includes:

- `section.phys.momentum_summary`
- `section.phys.kinetic_energy`

## 7) Enforcement Readiness

RepoX rules added:

- `INV-NO-DIRECT-VELOCITY-MUTATION`
- `INV-FORCE-THROUGH-PROCESS`
- `INV-MOMENTUM-STATE-DECLARED`

AuditX analyzers added:

- `E208_DIRECT_VELOCITY_WRITE_SMELL`
- `E209_INLINE_ACCELERATION_SMELL`

STRICT promotion map updated to block direct velocity write smell.

## 8) PHYS-1 TestX Coverage

Added PHYS-1 tests:

1. `test_impulse_updates_momentum_deterministic`
2. `test_velocity_derived_from_momentum`
3. `test_gravity_force_applied`
4. `test_momentum_conservation_profile`
5. `test_cross_platform_hash_stability`

## 9) Gate Status

Gate execution summary in this branch:

- Topology regeneration:
  - command: `python tools/governance/tool_topology_generate.py --repo-root .`
  - result: PASS
  - topology fingerprint: `985ea9e92dec2a44cf8799ca9fbdea5810a94734cc7068b0c9005456c4008dae`
- RepoX (STRICT):
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - result: PASS
  - message: `repox scan passed (files=1452, findings=17)` (warnings only)
- AuditX (STRICT):
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - result: FAIL
  - message: `auditx scan complete (changed_only=false, findings=1600, promoted_blockers=7)`
  - promoted blockers include pre-existing `E179_INLINE_RESPONSE_CURVE_SMELL` in:
    - `src/fields/field_engine.py`
    - `src/mechanics/structural_graph_engine.py`
    - `src/mobility/maintenance/wear_engine.py`
    - `src/mobility/micro/constrained_motion_solver.py`
    - `src/mobility/traffic/traffic_engine.py`
    - `src/mobility/travel/travel_engine.py`
    - `src/signals/trust/trust_engine.py`
- TestX (STRICT, PHYS-1 required subset):
  - command:
    - `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset test_impulse_updates_momentum_deterministic,test_velocity_derived_from_momentum,test_gravity_force_applied,test_momentum_conservation_profile,test_cross_platform_hash_stability`
  - result: PASS (`selected_tests=5`)
- TestX (STRICT full):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT`
  - result: FAIL (`selected_tests=645`; `pass=503`, `fail=142`)
  - dominant failure cluster remains branch-preexisting (`create_session_spec refused` and packaging/session bootstrap paths)
- strict build:
  - command: `python tools/xstack/run.py --repo-root . --cache off strict`
  - result: REFUSAL
  - key blockers:
    - `compatx` refusals at step 01
    - session boot refusal at step 07
    - `auditx` promoted blockers at step 09
    - `testx` strict failures at step 10
    - packaging refusal at step 13

## 10) Readiness for PHYS-2

PHYS-1 establishes deterministic force/momentum substrate contracts required for PHYS-2 field generalization:

- force/impulse process pathways are explicit and auditable
- gravity demonstrates FIELD->MODEL->PROCESS coupling discipline
- momentum/impulse proof chains support replay verification
- MECH hazard coupling exists without bypassing model/process governance
