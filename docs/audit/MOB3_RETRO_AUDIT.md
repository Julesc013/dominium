Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB3 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-02
Scope: MOB-3 vehicle assembly + motion state unification pre-implementation review.

## 1) Existing Vehicle-Like Components

Findings:
- No canonical vehicle aggregate currently exists in runtime state (`vehicles`, `motion_states`) as first-class collections.
- Mobility currently includes GuideGeometry and MobilityNetwork artifacts:
  - `guide_geometries`, `mobility_junctions`, `geometry_derived_metrics` in [tools/xstack/sessionx/process_runtime.py](tools/xstack/sessionx/process_runtime.py)
  - `mobility_network_bindings`, `mobility_switch_state_machines`, `mobility_route_results` in [tools/xstack/sessionx/process_runtime.py](tools/xstack/sessionx/process_runtime.py)
- Vehicle appears as a target kind in spec/fidelity/planning contracts but without a unified assembly model:
  - `_VALID_TARGET_KINDS` includes `vehicle` in [src/specs/spec_engine.py](src/specs/spec_engine.py)
  - `_PLAN_TYPES` includes `vehicle` in [src/control/planning/plan_engine.py](src/control/planning/plan_engine.py)
  - fidelity target kinds include `vehicle` in [src/control/fidelity/fidelity_engine.py](src/control/fidelity/fidelity_engine.py)

Assessment:
- Vehicle semantics are partially declared in interfaces/registries but not yet represented as one deterministic authoritative assembly record.

## 2) Existing Motion State Storage

Findings:
- Authoritative movement is currently body-centric (`process.agent_move`, `process.body_move_attempt`) with transforms stored on body assemblies in [tools/xstack/sessionx/process_runtime.py](tools/xstack/sessionx/process_runtime.py).
- Meso mobility state exists as route/network artifacts (`mobility_route_results`, active switch state machines), but no vehicle-tier state partition (`macro|meso|micro`) is present.
- No `motion_state` schema/collection currently exists under `schema/mobility` or `src/mobility`.

Assessment:
- Motion state is fragmented between embodied body motion and mobility network artifacts; vehicle-tier motion state needs explicit canonicalization.

## 3) Passenger/Cargo Special-Case Logic

Findings:
- No obvious hardcoded passenger branch was identified in authoritative Python runtime.
- Cargo/fuel-like handling routes through machine ports and logistics primitives:
  - port extraction/insertion and connection logic in [src/machines/port_engine.py](src/machines/port_engine.py)
  - machine/port process handling in [tools/xstack/sessionx/process_runtime.py](tools/xstack/sessionx/process_runtime.py)
- Existing process/pack content includes vehicle chassis assemblies (`assembly.on_planet.vehicle.chassis.basic`) but not a unified vehicle runtime aggregate.

Assessment:
- Current code is closer to generic machine/port flows than explicit passenger/cargo special-casing, but this must be normalized under vehicle assemblies to avoid future drift.

## 4) Direct Position Mutation Outside Processes

Findings:
- Authoritative motion mutation appears process-mediated in runtime (`execute_intent` branches), with movement handled by process handlers in [tools/xstack/sessionx/process_runtime.py](tools/xstack/sessionx/process_runtime.py).
- AuditX already contains mobility mutation smells (`e143_direct_position_mutation_smell.py`) to catch bypass risk.

Assessment:
- Existing mutation path is mostly aligned with process-only invariant; MOB-3 should preserve this by adding vehicle mutation only through dedicated processes.

## 5) Migration Plan to Unified Vehicle Assembly Model

1. Add canonical vehicle data contracts:
- Introduce `vehicle`, `motion_state`, and `vehicle_class` schemas under `schema/mobility`.
- Add a dedicated vehicle class registry (`data/registries/vehicle_class_registry.json`) with placeholder classes only.

2. Introduce deterministic vehicle engine:
- Add `src/mobility/vehicle/vehicle_engine.py` with:
  - normalization/builders for vehicles and motion states
  - deterministic registration from structure instances
  - reference validation for ports/interior/pose/mount/spec bindings
  - compatibility checks against edge/geometry specs

3. Process-only authoritative integration:
- Add process handlers:
  - `process.vehicle_register_from_structure`
  - `process.vehicle_check_compatibility`
- Keep movement simulation out of scope (no micro driving physics in MOB-3).

4. Inspection and reenactment hooks:
- Add inspection sections for vehicle summary/specs/ports/pose/wear risk.
- Preserve stable deterministic IDs/fingerprints for downstream reenactment descriptors.

5. Enforcement:
- Add RepoX mobility vehicle invariants:
  - `INV-NO-VEHICLE-SPECIALCASE`
  - `INV-VEHICLES-AS-ASSEMBLIES`
  - `INV-SPEC-COMPATIBILITY-REQUIRED`
- Add AuditX analyzer:
  - `VehicleHardcodeSmell`
