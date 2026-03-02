# Micro Constrained Motion (MOB-6)

Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-02

## Purpose

Define deterministic micro constrained motion in ROI for guide-following mobility (rails/conveyors/tethers) without introducing full wheel-rail contact or suspension simulation.

## Scope

This doctrine defines:
- micro motion state representation
- constrained follow-spline updates
- derailment threshold model and incident logging
- coupling/consist baseline
- basic junction handoff behavior
- EB collision handoff for post-derail free motion

Out of scope for MOB-6:
- full contact mechanics
- full suspension dynamics
- global micro simulation
- wall-clock driven updates

## Micro Motion State

Canonical vehicle micro state is represented with deterministic integer/fixed-point fields:
- `geometry_id`: active guide geometry id
- `s_param`: guide-progress value
- `velocity`: signed motion scalar per tick
- `acceleration`: signed scalar per tick^2
- `direction`: `forward|back`
- `last_update_tick`

Heading/orientation derives from guide tangent at current `s_param` and is stored as derived/state convenience only.

## Constraint Model

Primary constraint type:
- `constraint.follow_spline`

Behavior:
- vehicle remains constrained to active guide geometry while constraint is active
- micro update step advances `s_param` by deterministic velocity integration
- endpoint clamping is deterministic
- no implicit truth mutation outside process handlers

## Derailment Model

Baseline deterministic criterion:
- `lateral_accel = v^2 / radius`
- compare to allowed threshold

Threshold envelope:
- `threshold = base(spec) * modifier(track_wear, friction, maintenance)`

Data sources:
- curvature radius from MOB-1 geometry derived metrics
- vehicle/edge spec limits from SPEC-1 bindings
- wear/maintenance modifiers from MECH/MAT state
- friction/moisture modifiers from FIELD-1/effect stack

If threshold exceeded:
- execute `process.mob_derail(vehicle_id)`
- remove constrained-follow behavior
- emit incident event with at minimum:
  - `geometry_id`
  - `vehicle_id`
  - `speed`
  - `radius`
  - `track_condition`

Derailment transition process contract:
- authoritative transition path is `process.mob_derail` only
- updates both vehicle motion rows and micro constrained rows in one deterministic process application
- disables active coupling constraints touching the derailed vehicle
- creates/updates an EB body reference for post-derail collision participation

### Optional stochastic policy

Stochastic derail path is optional and only lawful when policy explicitly allows it.

Requirements:
- named RNG stream only
- deterministic seed derived from stable inputs (vehicle, geometry, tick)
- stochastic path must remain replay-deterministic for identical inputs

## Coupling/Consist

Coupling baseline uses mount/constraint integration:
- `process.coupler_attach` validates mount compatibility
- creates coupling constraint rows
- consist ordering is deterministic (`vehicle_id` ordering)
- optional mount-point ids must resolve and pass mount compatibility before coupling activation
- coupling rows persist deterministic offset metadata for trailing consist propagation

Consist propagation model (MOB-6 baseline):
- lead vehicle drives trailing `s_param` with fixed offsets
- slack and dynamic coupler physics deferred

## Junction Handoff (Basic)

At guide endpoints:
- choose outgoing geometry by switch state machine (MOB-2)
- itinerary hint may filter candidates
- deterministic tie-break uses sorted edge/geometry ids

No valid outgoing path:
- vehicle is deterministically stopped (`velocity -> 0`)
- emit blocked event

## EB Collision Handoff

After derailment/off-guide:
- vehicle transitions to free micro body participation for collision
- collision handling uses existing EB collision substrate
- constrained solver no longer applies follow-spline updates to that vehicle until reattached

## Fidelity and Budget

- Micro solver execution is ROI-only and fidelity-gated.
- Global micro simulation is forbidden.
- If budget is insufficient, solver degrades deterministically to meso/macro-compatible handling and logs downgrade decisions.

## Control and Epistemics

- Driver controls are routed through control plane inputs/IR.
- No direct input bypass to truth mutation.
- Instruments expose speed and derail-risk as diegetic readouts with entitlement-aware detail.

## Reenactment/Provenance

Derailment and constrained-motion incidents must log enough deterministic context to reconstruct:
- speed
- curvature/radius context
- wear/friction modifiers
- active policy identifiers

## Invariants

- Process-only mutation (A2)
- Deterministic ordering and outcomes (A1)
- No mode flags (A4)
- Event/audit-visible degradation/refusal (A10)
