Status: DERIVED
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-0 constitution audit, deterministic/process-only scope.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SYS0 Retro Audit

## Scope
Retro-consistency audit for introducing formal System composition/collapse without changing domain semantics.

## 1) Existing Complex Assemblies Inventory
Current complex assembly-like surfaces are data/process composed, not hidden subsystem classes:

- Machine aggregates and industrial stubs:
  - `data/registries/machine_type_registry.json`
  - includes `machine.pump.basic`, `machine.heat_exchanger.stub`, and other multi-port machine types.
- Vehicle/powertrain classes:
  - `data/registries/vehicle_class_registry.json`
  - `data/registries/mobility_vehicle_class_registry.json`
  - includes locomotive and vehicle stubs (`veh.rail_locomotive_stub`, `vehicle.rail_loco`, etc.).
- Macro region capsules and transitions:
  - `tools/xstack/sessionx/process_runtime.py`
  - `process.region_management_tick`, `process.region_expand`, `process.region_collapse`.
- Materialization collapse/expand behavior:
  - `src/materials/materialization/materialization_engine.py`
  - deterministic micro part collapse to aggregate and expand back.
- Cohort macro/micro refinement:
  - `tools/xstack/sessionx/process_runtime.py`
  - `process.cohort_expand_to_micro`, `process.cohort_collapse_from_micro`.

## 2) Hidden Subsystem Class Check
No dedicated hidden `System` runtime class found under `src/`.

- `src/system/` did not exist at audit start.
- Existing abstraction behavior is implemented via registries + deterministic process handlers + state rows.

Result: passes constitutional direction (assemblies/models/processes), but lacks explicit SYS layer contracts/artifacts.

## 3) Existing Implicit Abstractions
Deterministic abstractions already in use:

- Region macro capsules (`state.macro_capsules`) during region management tick.
- Macro travel abstraction for mobility (`src/mobility/travel/travel_engine.py`).
- Materialization ROI collapse/expand path.
- Cohort refinement macro/micro path.

These are explicit process flows, but not unified under a formal SYS composition/collapse contract.

## 4) Implicit Collapse Without Artifact Check
No silent collapse path was found in the audited runtime paths.

- Region transition emits transition artifacts/events.
- Materialization collapse emits deterministic transition/event traces.
- Cohort collapse emits deterministic state/event outputs.

Gap: no generic `system_collapse`/`system_expand` artifacts or unified capsule contract for composed subsystem graphs.

## 5) Candidate Systems for SYS Collapse Abstraction
Priority candidates for SYS-0 formalization:

- Engine/power module (fuel/air/power/heat/exhaust boundary)
- Generator module
- Pump/compressor module
- Heat exchanger module
- Vehicle propulsion module
- Factory processing module
- Plant-level nested system (multiple machine networks)

## 6) Migration Direction
Required SYS-0 migration path:

- Introduce explicit `InterfaceSignature`, `BoundaryInvariant`, `SystemStateVector`, and `MacroCapsule` records.
- Route collapse/expand only through canonical processes:
  - `process.system_collapse`
  - `process.system_expand`
- Require deterministic provenance anchor validation and explicit refusal on mismatch.
- Keep current region/capsule mechanisms unchanged; SYS-0 is additive at system composition layer.
