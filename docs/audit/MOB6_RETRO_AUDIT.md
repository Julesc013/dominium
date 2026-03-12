Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB6 Retro-Consistency Audit

Date: 2026-03-02
Scope: MOB-6 micro constrained motion enablement
Canonical refs: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md, docs/mobility/MOBILITY_CONSTITUTION.md

## Findings

### Existing micro movement constraints
- No dedicated constrained rail/guide micro solver module exists under `src/mobility/`.
- Existing authoritative movement primitives are:
  - macro/meso mobility updates in `src/mobility/travel/travel_engine.py` and `src/mobility/traffic/traffic_engine.py`
  - free-body movement and collision handling in `tools/xstack/sessionx/process_runtime.py` (`_apply_body_move_attempt`, `_resolve_body_collisions`)
- Vehicle `micro_state` fields are present in `src/mobility/vehicle/vehicle_engine.py` but are currently a carrier only.

### Direct position changes for vehicles
- Vehicle motion truth is currently mutated via process handlers in `tools/xstack/sessionx/process_runtime.py`.
- No separate mobility micro process exists yet; vehicle micro position/velocity updates are not currently handled by a dedicated deterministic mobility solver.
- Body-level transform updates are process-gated in `_apply_body_move_attempt`; this is lawful for EB bodies but not yet tied to MOB constrained rail motion.

### Derailment logic hidden in effects
- No explicit mobility derailment process was found.
- Mechanics provides risk signals (for example `derailment_risk_permille` style summaries in mechanics output paths), but there is no process-mediated `process.mob_derail` pathway yet.
- Effects are used for modifiers (speed cap, traction, wind drift), but derailment state transitions are not yet wired as a first-class incident process.

## Migration Plan to MOB-6 Substrate

1. Introduce canonical micro entities:
- `micro_motion_states`
- `coupling_constraints`
- optional derail policy rows referenced from policy/registries

2. Introduce deterministic micro process handlers (process-only mutation):
- `process.mobility_micro_tick`
- `process.mob_derail`
- `process.coupler_attach`

3. Implement constrained solver module:
- deterministic per-vehicle order by `vehicle_id`
- spline `s` advancement with fixed-point/integer state
- speed-cap/effect application via existing effect stack
- ROI-only execution with deterministic budget downgrade to meso and DecisionLog/fidelity entry

4. Derailment pipeline:
- derive curvature radius from GuideGeometry metrics
- threshold compare using spec/track/friction modifiers
- optional stochastic path only via named RNG stream and deterministic seed hash
- emit `incident.derailment.*` event payloads and provenance-facing metadata

5. Coupling pathway:
- validate mount compatibility
- create canonical coupling constraint rows
- deterministic consist ordering and fixed offset propagation

6. Junction handoff (basic):
- choose outgoing edge via switch state machine + itinerary hint
- deterministic tie-break by edge_id
- emit blocked event and brake-to-stop when no valid outgoing edge

7. EB handoff after derail:
- remove follow-spline coupling for derailed vehicle
- materialize/activate EB body row and route through existing collision substrate

8. Enforcement:
- add MOB-6 RepoX invariants and derailment bypass checks
- add AuditX derailment bypass smell analyzer

9. TestX:
- add deterministic solver, derail trigger, speed cap, coupling order, switch handoff, budget downgrade tests.

## Canon/Invariant Notes
- Upholds A1 determinism and A2 process-only mutation.
- No mode flags; all behavior remains profile/policy/registry driven.
- No wall-clock usage; tick-based only.
