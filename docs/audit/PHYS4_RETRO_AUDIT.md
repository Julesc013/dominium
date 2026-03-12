Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# PHYS-4 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-04
Scope: PHYS-4 entropy/degradation preflight over existing PHYS/ELEC/THERM/MECH runtime pathways.

## 1) Existing Wear / Efficiency-loss Logic

Observed pre-PHYS4 degradation pathways:

- `tools/xstack/sessionx/process_runtime.py`:
  - `process.decay_tick` computed `machine_output_permille` with inline backlog/wear penalty math.
  - generated `effect.machine_degraded` directly from those inline calculations.
- `process.vehicle_environment_tick` emits stress-driven `effect.machine_degraded` from structural summaries.
- `process.drill_hole` and `process.mechanics_fracture` mutate structural strain/failure without explicit entropy accounting.

## 2) Ad-hoc Degradation Multipliers

Inline formulas identified:

- maintenance backlog penalty + wear penalty -> output reduction
- stress ratio threshold -> direct output reduction

These are deterministic but partially bypass a unified entropy policy substrate.

## 3) Silent Loss-of-quality Patterns

No silent state mutation bypassing process boundaries was found.

However, degradation meaning was not centrally classified as entropy-driven, which makes cross-domain irreversibility audits harder.

## 4) Migration Notes

PHYS-4 migration applied:

- Introduced deterministic entropy engine hooks in process runtime:
  - contribution recording
  - reset recording
  - effect evaluation snapshots
  - entropy hash chains
- Replaced maintenance inline degradation in `process.decay_tick` with entropy-policy-derived multipliers.
- Added contribution hooks for:
  - ELEC loss transform (`transform.electrical_to_thermal`)
  - THERM phase transition (`transform.phase_change_stub`)
  - MECH plastic/fracture updates (`transform.plastic_deformation_stub`)
- Added maintenance reset hook in `process.maintenance_perform` (alias `process.perform_maintenance`).

## 5) Deprecation Notes

Transitional legacy channel:

- `quantity.entropy_metric` remains present for compatibility reads.
- Canonical PHYS-4 target channel is `quantity.entropy_index`.
- New PHYS-4 logging and exception pathways now prefer `quantity.entropy_index`.
