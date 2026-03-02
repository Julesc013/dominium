Status: AUDIT
Scope: MOB-9 maintenance/wear retrofit
Date: 2026-03-03

# MOB9 Retro Audit

## Audit Method
- Scanned mobility runtime/process paths:
  - `process.travel_tick`
  - `process.mobility_micro_tick`
  - `process.signal_tick`
- Scanned mobility modules for wear/degradation logic:
  - `src/mobility/travel/*`
  - `src/mobility/traffic/*`
  - `src/mobility/micro/*`
  - `src/mobility/signals/*`
- Scanned generic maintenance substrate:
  - `src/materials/maintenance/decay_engine.py`
  - `process.decay_tick`, `process.inspection_perform`, `process.maintenance_perform`

## Findings

### F1 - Mobility wear is partially ad-hoc in derailment path
- Existing:
  - `process.mobility_micro_tick` reads `track_wear_permille` from geometry metric extensions.
  - `process.mobility_micro_tick` reads `maintenance_permille` from vehicle extensions.
- Gap:
  - No unified canonical wear rows for mobility targets.
  - Derailment threshold modifiers are not sourced from a dedicated wear state model.

### F2 - No explicit per-target mobility wear state rows
- Existing:
  - MAT-6 tracks generic `asset_health_states.accumulated_wear`.
  - Mobility has occupancy, travel, micro motion, signal state, but no canonical wear table.
- Gap:
  - Missing deterministic wear records for edge/node/vehicle mobility targets.

### F3 - Maintenance flow exists but mobility service tasks are not explicit
- Existing:
  - Generic maintenance scheduling/inspection/service processes exist in MAT-6.
- Gap:
  - No mobility-scoped process wrappers for track/vehicle inspect/service affordances.
  - No deterministic mobility wear reduction process surfaced as mobility tasks.

### F4 - Hazard coupling to mobility incidents is incomplete
- Existing:
  - Derailment reason codes include `incident.derailment.track_wear`.
  - Signal hazards are present in MOB-8.
- Gap:
  - No canonical mobility wear threshold evaluation that triggers `process.mob_failure` / `process.mob_track_failure`.

### F5 - Inspection surfaces do not consume mobility wear rows
- Existing:
  - `section.vehicle.wear_risk` exists.
  - Maintenance and mechanics summaries augment inspection payloads.
- Gap:
  - No direct mobility wear summary augmentation from mobility wear state rows.

## Migration Plan
1. Introduce canonical mobility wear schemas/registries (`wear_state`, `wear_type`, wear accumulation policy IDs).
2. Implement deterministic mobility wear engine under `src/mobility/maintenance/wear_engine.py`.
3. Add process-layer canonical wear updates:
   - travel edge traversal
   - micro braking
   - environmental exposure hooks from FieldLayer
4. Replace ad-hoc derailment wear modifiers with wear-state-derived values.
5. Add mobility failure processes and threshold triggers via hazard semantics.
6. Add mobility inspection/service process wrappers for track/vehicle.
7. Add RepoX/AuditX rules to prevent ad-hoc wear mutations.
