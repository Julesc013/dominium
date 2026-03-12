Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# VEHICLE_MODEL_BASELINE

Status: BASELINE
Last Updated: 2026-03-02
Scope: MOB-3 vehicle assembly model and tiered motion-state substrate.

## 1) Constitutional Rules Implemented

- Vehicles are normalized as assembly-backed entities, not hardcoded mode classes.
- Authoritative mutation is process-only:
  - `process.vehicle_register_from_structure`
  - `process.vehicle_check_compatibility`
  - `process.vehicle_apply_environment_hooks`
- Deterministic identity and ordering are preserved through:
  - deterministic vehicle and motion-state references
  - canonical sorted normalization of vehicle/motion/event rows
  - deterministic compatibility result/event IDs
- No micro solver is introduced in MOB-3; environment hooks emit explicit effects only.

## 2) Schemas and Registries

- MOB-3 schemas integrated:
  - `schema/mobility/vehicle.schema`
  - `schema/mobility/motion_state.schema`
  - `schema/mobility/vehicle_class.schema`
  - `schema/mobility/vehicle_class_registry.schema`
  - `schemas/vehicle.schema.json`
  - `schemas/motion_state.schema.json`
  - `schemas/vehicle_class.schema.json`
  - `schemas/vehicle_class_registry.schema.json`
- Vehicle class registry integrated:
  - `data/registries/vehicle_class_registry.json`
  - baseline placeholder classes for rail/road/sea/air/space/mobile platform families

## 3) Compatibility Checks

- `process.vehicle_check_compatibility` performs deterministic vehicle-to-edge validation.
- Inputs:
  - `vehicle_id`
  - `target_edge_id`
  - optional `enforce` flag
- Validation path:
  - resolves vehicle specs + edge/geometry specs
  - checks gauge compatibility
  - checks clearance envelope compatibility (stub metric path from MOB-1 geometry metrics)
- Outcomes:
  - persisted row in `vehicle_compatibility_results`
  - event row in `vehicle_events`
  - strict refusal when enforced and incompatible:
    - `refusal.mob.spec_noncompliant`

## 4) Integration Points

- Ports/Interiors/Pose/Mount:
  - registration validates declared `port_ids`, `interior_graph_id`, `pose_slot_ids`, `mount_point_ids`
  - query surfaces:
    - `get_vehicle_capabilities`
    - `get_vehicle_ports`
    - `get_vehicle_interior`
    - `get_vehicle_driver_pose_slots`
- MECH/FIELD/EFFECT:
  - environment hooks consume field modifiers and mechanics stress summaries
  - hook process applies explicit temporary effects:
    - traction reduction
    - wind drift
    - visibility reduction and speed cap
    - stress-driven machine degradation
  - no motion transform stepping is performed
- Inspection/Reenactment:
  - vehicle sections available:
    - `section.vehicle.summary`
    - `section.vehicle.specs`
    - `section.vehicle.ports`
    - `section.vehicle.pose_slots`
    - `section.vehicle.wear_risk`
  - stable `vehicle_id` and event streams provide reenactment anchors

## 5) Readiness for MOB-4 and MOB-6/7

- MOB-4 macro itineraries:
  - `motion_state.macro_state` and compatibility rows are ready for itinerary + schedule admission checks
  - vehicle-edge compatibility hooks can be invoked during route assignment
- MOB-6/7 micro motion:
  - `motion_state.micro_state` slot fields exist but remain non-simulated in MOB-3
  - environment hooks already provide explicit effect modifiers for future micro solvers
  - no global micro-body creation path was introduced

## 6) Gate Runs (2026-03-02)

- RepoX:
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - status: `pass` (warn findings only)
- AuditX:
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
  - status: `pass` (scan executed; findings reported)
- TestX (MOB-3 subset):
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset testx.mobility.vehicle_register_deterministic,testx.mobility.spec_compatibility_refusal,testx.mobility.vehicle_ports_pose_interior_refs_valid,testx.mobility.no_motion_sim_side_effects`
  - status: `pass` (4/4)
- strict build:
  - command: `python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mob3 --cache on --format json`
  - status: `complete` (`result=complete`)
- topology map update:
  - command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - status: `complete` (`node_count=2358`, `edge_count=100046`)
  - deterministic fingerprint: `5cd1750dc478479180df213dc523b544b9246b4ac6527e3dc469bc0e05c9efcb`
