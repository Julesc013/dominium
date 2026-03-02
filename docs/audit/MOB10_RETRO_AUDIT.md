# MOB10 Retro-Consistency Audit

Date: 2026-03-03
Scope: Vehicle interior integration with mobility (INT/POSE/MOB/FIELD/MECH/CTRL).

## Existing Interior + Vehicle Integration Surface

- `process.vehicle_register_from_structure` already accepts and validates `interior_graph_id` plus `pose_slot_ids`.
- `process.compartment_flow_tick` already runs deterministic compartment flow, including boundary sampling from FieldLayer and diegetic interior instruments.
- `process.pose_enter` already enforces access path reachability through interior portals via `_pose_slot_accessible_by_path`.
- `process.portal_seal_breach` already reduces portal sealing coefficients.
- MECH fracture flow already supports linking a structural fracture edge to a portal and creating leak hazards.

## Ad-hoc / Gap Findings

- Vehicle world-position sampling for field boundary exchange is partially ad-hoc:
  - `_target_spatial_position` relies primarily on direct row position/extensions/cell hints.
  - Vehicle movement state (`macro/meso/micro` tiers) is not consistently used as fallback world anchor.
- Vehicle-interior specific dashboard/instrument projections are not explicitly modeled as vehicle dashboard payloads.
- Mobility-layer incident reason coverage exists for derail/collision/visibility/wind, but not explicit vehicle-interior breach/decompression/flood-start incident rows in mobility event streams.
- Vehicle-targeted inspection sections exist (`section.vehicle.summary/specs/ports/pose_slots/wear_risk`) but no explicit vehicle-interior summary/portal/pressure sections.

## Frame-Consistency Risk

- Interior volume transforms are parented to `parent_spatial_id` and resolved through spatial composition.
- Risk: for vehicle interiors this parent link may drift unless vehicle registration/runtime keeps interior volume parent spatial linkage synchronized with vehicle `spatial_id`.

## Epistemic Risk

- Interior instruments are diegetic and coarse in baseline flow tick.
- Risk: adding vehicle dashboard instrumentation could leak raw interior state unless quantized and routed through perceived instrument channels only.

## Migration Plan

1. Add explicit MOB10 doctrine (`docs/mobility/VEHICLE_INTERIORS.md`) defining frame, boundary exchange, and incident semantics.
2. Add deterministic runtime linkage for vehicle spatial frame:
   - synchronize vehicle interior volume parent spatial linkage,
   - extend vehicle position sampling fallback from motion/body state for field boundary exchange.
3. Integrate compartment boundary sampling with moving vehicle context:
   - optional deterministic ram-air pressure term from wind + vehicle velocity (micro).
4. Emit explicit breach/leak/flooding incident events through process paths and provenance metadata.
5. Add moving-access policy hook for compartment transitions through `process.pose_enter`.
6. Add vehicle dashboard diegetic instrument rows (pressure/oxygen/smoke/flood) with coarse quantized outputs only.
7. Extend inspection sections for vehicle interior summary, portal states, pressure map.
8. Add enforcement rules (RepoX + AuditX) for no ad-hoc vehicle-cabin logic and no instrument truth leaks.
9. Add deterministic TestX coverage for motion attachment, boundary exchange, breach hazard creation, portal-path access, and instrument redaction.
