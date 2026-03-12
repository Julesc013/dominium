Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Vehicle Model Doctrine

Status: CANONICAL
Last Updated: 2026-03-02
Scope: MOB-3 universal vehicle assembly and motion-state substrate.

## 1) Purpose

MOB-3 defines vehicles as deterministic assemblies rather than hardcoded mode classes.
The model unifies rail/road/sea/air/space/robot/mobile-platform carriers under one data-driven contract.

## 2) Vehicle as Assembly

A vehicle is an assembly aggregate composed of:

- structure (AG/constructed structure instance reference)
- machine ports (cargo/fuel/energy interfaces)
- interior graph reference (cabins/holds/compartments)
- pose slot references (driver seats and operator stations)
- mount point references (couplers, docking interfaces)
- motion state reference (macro/meso/micro-tier record)
- control bindings (via pose/control systems)
- hazard and maintenance references

No vehicle behavior is authorized by renderer/UI-only mutation.

## 3) Vehicle Classes Are Data-Driven

- Vehicle typing is registry-driven (`vehicle_class_id`) with capability tags and supported motion modes.
- No runtime hardcoded branch by vehicle type is permitted.
- Required interfaces and policy constraints are resolved from SpecSheets and class/spec bindings.

## 4) Motion State Tiers

Motion state is explicit and tiered:

- Macro:
  - itinerary/schedule intent and ETA references only
  - no micro transform stepping
- Meso:
  - mobility network occupancy context (edge/occupancy token)
  - schedule and routing compatibility context
- Micro:
  - reserved slot for ROI-local motion state linkage (geometry parameter/body linkage)
  - physical micro simulation is out of MOB-3 scope

Tier activation is policy/fidelity driven and must remain deterministic and budgeted.

## 5) Compatibility Contract (Spec + Network)

Compatibility checks are deterministic and inspectable:

- Vehicle-side interface specs:
  - gauge
  - interface profile
  - clearance envelope requirements
- Edge/geometry-side specs:
  - track/corridor gauge
  - clearance/min curvature constraints
- Compatibility outcome:
  - pass/warn/fail summaries
  - strict refusal path: `refusal.mob.spec_noncompliant`

No silent coercion of incompatible specs is allowed.

## 6) Ports / Interiors / Pose / Mount Integration

- Ports:
  - vehicle declares `port_ids` for cargo/fuel/energy transfer surfaces
- Interiors:
  - vehicle can bind `interior_graph_id` for cabins/holds and compartment semantics
- PoseSlots:
  - driver/operator authority is granted through pose occupancy + control binding
- MountPoints:
  - couplers/docking links are mount-point based, never vehicle-type specialcased

## 7) MECH + FIELD + EFFECT Hooks

- MECH integration:
  - vehicle structure references can consume stress and fracture summaries
  - maintenance/wear risk must be explicit and inspectable
- FIELD integration:
  - friction, wind, and visibility are consumed as field/effect hooks
  - effects are explicit modifiers; no hidden multipliers
- MOB-3 does not implement micro driving dynamics.

## 8) Control Plane + Authority

- Vehicle registration, compatibility checks, and state updates are process-only.
- Driving/scheduling authority must route via control plane intents/IR.
- Seat/pose occupancy is the authority gateway for operator control.
- Direct input bypass is forbidden.

## 9) Determinism and Provenance

- Vehicle IDs and fingerprints are deterministic.
- Motion state and compatibility evaluations are ordered and deterministic.
- Vehicle events are provenance-carrying for replay/reenactment.
- No wall-clock dependence is allowed.

## 10) Non-Goals (MOB-3)

- No micro driving physics solver.
- No aerodynamic/orbital solver.
- No congestion/signaling model.
- No hardcoded vehicle mode flags.
