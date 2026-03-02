# Mobility Constitution

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-0 unified movement substrate contract.

## 1) Purpose

This constitution defines one deterministic mobility substrate for all movement domains:

- walking and embodied motion
- rail and guideway motion
- road traffic
- sea and subsurface
- air and high-atmo
- orbital and space movement
- tethered and constrained megastructure movement

All mobility behavior must remain process-driven, profile-driven, and pack-driven.

## 2) Tiered Mobility Model

Mobility is always tiered and budget-arbitrated:

- Macro:
  - commitments, ETA bands, route assignments, and schedule intents only
  - no micro kinematic stepping at global scope
- Meso:
  - network occupancy, signals, timetable state, congestion arbitration
  - deterministic routing and tie-breaks over NetworkGraph
- Micro (ROI-only):
  - kinematic and constraint simulation, contact/collision resolution, local control response
  - activated only in ROI and under RS-5 quotas

Global always-on micro mobility is forbidden.

## 3) Movement Constraint Classes

Mobility constraints are data-declared classes, not hardcoded vehicle branches:

- `constrained_1D` (spline/track-like guide)
- `constrained_2D` (corridor/surface-lane movement)
- `constrained_3D` (volume navigation)
- `orbital_path` (analytic orbital trajectories)
- `field_following` (field lane following, maglev/warp-like lanes)
- `free_motion` (embodied/free movement under law/profile constraints)

## 4) Formalization Lifecycle

Mobility infrastructure follows FORM-1 lifecycle:

- `RAW`:
  - physical assemblies/material works exist only
  - no canonical movement guide geometry yet
- `INFERRED`:
  - candidate guide geometry can be derived and inspected
  - confirmation remains explicit
- `FORMAL`:
  - guide geometry, constraints, and policy bindings are authored
- `NETWORKED`:
  - connected graph with rules/signals/schedules and deterministic routing semantics

Promotion across states must occur through control intents and deterministic process commits.

## 5) Engineering Spec Contract

Mobility engineering semantics are SpecSheet-driven:

- examples:
  - gauge
  - width and clearances
  - curvature limits
  - load rating
  - max-speed policy references
- compliance:
  - deterministic checks
  - inspectable evidence inputs/outputs
  - explicit refusal on non-compliance

No hardcoded per-vehicle literal policy constants are allowed in runtime branches.

## 6) Control Plane Integration

All mobility control must flow through CTRL intent/IR:

- driving, dispatching, planning, and scheduling are `ControlIntent`/IR-mediated
- seat/console possession via PoseSlots and ControlBinding governs who can drive
- direct input-to-truth bypass is forbidden
- fidelity arbitration outcomes must be logged in decision logs

## 7) Mechanics and Field Integration

Mobility consumes MECH and FIELD outputs:

- MECH influences:
  - track/guide integrity
  - bridge/load path limits
  - structural degradation and failure consequences
- FIELD influences:
  - traction and slip
  - visibility and operator limits
  - icing and adhesion loss
  - wind drift and lateral perturbation
- temporary modifiers:
  - represented as explicit Effects
  - never as silent hidden multipliers

## 8) Epistemics and Diegetics

Mobility observability is role- and lens-bounded:

- drivers:
  - instrument-based local readings and warnings
- dispatchers:
  - schedule/signal/network state, policy bounded
- default players:
  - coarse diegetic states only

No omniscient mobility view without explicit entitlements/lens authority.

## 9) Performance Constitution

Mobility execution must satisfy deterministic budget law:

- no global micro simulation
- micro runs only in ROI
- deterministic degradation when budget/fidelity pressure occurs
- degradation/refusal must be explicit and logged

## 10) Proof, Eventing, and Reenactment

Mobility outcomes are event-sourced:

- trips, control decisions, incidents, and degradations are logged
- reenactment can reconstruct macro/meso and authorized micro slices
- replay equivalence and partition-hash invariants apply

Nothing "just happens" outside commitment/event causality.

## 11) Modding and Compatibility

Mobility must remain moddable and compatibility-safe:

- vehicle/constraint/signal/speed semantics are registry-driven
- optional packs remain optional
- missing mobility packs degrade/refuse deterministically
- schema/version transitions require explicit migration or refusal

## 12) Non-Goals for MOB-0

- No mobility solver implementation (MOB-1+ scope).
- No hardcoded vehicle-type simulation branches.
- No wall-clock or nondeterministic runtime behavior.
- No process-layer bypass.
