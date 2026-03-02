# Micro Free Motion (MOB-7)

Status: AUTHORITATIVE
Version: 1.0.0
Last Updated: 2026-03-02

## Purpose

Define deterministic ROI-only micro free motion for agents and vehicles not bound to spline-only constraints, without introducing full aerodynamics, buoyancy, or orbital dynamics.

## Scope

This doctrine defines:
- canonical free-motion state rows
- deterministic per-tick free-motion integration
- optional corridor/volume constraint enforcement
- deterministic field/effect influence for friction, wind, and visibility
- process-only mutation and budgeted micro execution

Out of scope for MOB-7:
- detailed aerodynamics
- detailed buoyancy/hydrodynamics
- orbital dynamics
- global micro simulation
- wall-clock-driven updates

## Free Motion State

Canonical free-motion state binds a mobility subject to an EB body:
- `vehicle_id` or `agent_id` (one required)
- `body_id` (required EB body reference)
- `velocity` (vector integer mm/tick)
- `acceleration` (vector integer mm/tick^2)
- `corridor_geometry_id` (optional `geo.corridor2D`)
- `volume_geometry_id` (optional `geo.volume3D`)
- `last_update_tick`

The body transform/orientation remains authoritative in EB body rows; free-motion rows are the mobility-process control surface for deterministic motion updates.

## Solver Model

Per processed subject, deterministic update order is by stable subject id.

Update sequence:
1. Resolve policy caps (`max_speed`, `max_accel`).
2. Resolve control desired acceleration from control inputs.
3. Apply traction model (`traction.basic_friction`) from friction field/effects.
4. Apply wind model (`wind.basic_drift`) from field wind vector and policy scale.
5. Integrate acceleration and velocity in fixed-tick integer math.
6. Integrate body position through deterministic EB movement/collision path.
7. Apply corridor/volume enforcement mode (`clamp|refuse|warn`).

## Corridor/Volume Constraints

Supported optional constraints:
- `constraint.follow_corridor` for `geo.corridor2D`
- `constraint.follow_volume` for `geo.volume3D`

Baseline enforcement:
- corridor/volume bounds are sampled from GuideGeometry bounds/parameters
- if subject exits bounds:
  - `clamp`: project/clamp position deterministically to nearest valid point
  - `refuse`: reject movement step and keep prior position
  - `warn`: allow step and emit deterministic warning metadata

Constraint participation is expressed via deterministic constraint component hooks and validated through constraint type registry rows.

## Field and Effect Integration

Field influence must route through FIELD-1 query/snapshot paths:
- friction field reduces effective acceleration
- wind field adds drift acceleration
- visibility field contributes visibility risk and speed-cap/effect decisions

Effect integration:
- `effect.speed_cap` may cap free-motion speed
- `effect.visibility_reduction` may be auto-applied when visibility degrades
- field/effect influence is logged in deterministic decision metadata

No ad-hoc weather or friction/wind flags are allowed outside field/effect channels.

## Tier Switching and Budget

- Micro free motion is ROI-only.
- Non-ROI subjects must remain meso/macro.
- Budget gate applies deterministic maximum subject updates per tick.
- Over-budget subjects are deferred deterministically by subject id order and may be downgraded to meso with explicit decision-log entries.

## Control and Authority

- All free-motion simulation mutation is process-only (`process.mobility_free_tick`).
- Control inputs are accepted only through control-plane process inputs/IR mediation.
- Renderer and UI remain presentation-only.

## Safety and Spec Hooks

SpecSheet integration points:
- safe speed envelope for corridor/volume classes
- visibility-linked operating restrictions
- clearance compatibility hooks (stub until deeper domain solvers)

Violations produce deterministic warnings/refusals/incidents, not silent correction.

## UX and Diegetics

`process.mobility_free_tick` produces deterministic instrument payloads for diegetic presentation:
- `speed_mm_per_tick`
- `wind_vector`
- `visibility_permille`
- `corridor_status` / `volume_status`

These outputs are stored in `state.mobility_free_instruments` and can be rendered as speedometer/wind/visibility warnings without introducing a second truth path.

Planning/admin overlays use GuideGeometry and free-motion runtime metadata:
- corridor and volume boundary wireframes from `guide_geometries`
- subject-level warning state from `mobility_free_incidents`

## Multiplayer and Reenactment

Authoritative/hybrid behavior:
- free-motion mutation runs on the authoritative process path only
- clients consume redacted state and instrument channels

Lockstep behavior:
- sorted `subject_id` update order
- integer tick integration
- deterministic budget deferral order

Reenactment hooks:
- incidents are emitted to deterministic `travel_events` as `incident_stub` with reason codes
- summarized rows are persisted in `state.mobility_free_incidents`
- runtime budget/ROI outcomes are persisted in `state.mobility_free_runtime_state`

## Invariants

- A1 Determinism: stable ordering + integer integration + tick-only updates.
- A2 Process-only mutation: authoritative writes only in process runtime.
- A4 No mode flags: data/policy-driven behavior only.
- A5 Event-driven advancement: no hidden background mutation.
