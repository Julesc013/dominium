Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-MODEL-1 Retro Consistency Audit

Date: 2026-03-03
Scope: Constitutive model migration candidates

## Existing policy functions that should migrate to constitutive models

1. `src/signals/transport/channel_executor.py`
- Current behavior: attenuation/loss functions combine policy, hop, and optional RNG decisions inline.
- Migration target: `model_type.signal_attenuation_stub` with explicit input/output signatures and cache policy.

2. `src/mobility/micro/constrained_motion_solver.py`
- Current behavior: derailment threshold and lateral-accel checks encoded in solver logic.
- Migration target: `model_type.mech_fatigue_rate_stub` plus future derail-specific constitutive model types.

3. `src/mobility/maintenance/wear_engine.py`
- Current behavior: wear accumulation uses inline scaling (load/environment/tick).
- Migration target: `model_type.mech_fatigue_rate_stub` and future wear domain model types.

## Duplicated response logic candidates

1. Field-scaled modifiers in mobility and signal engines
- Similar patterns exist in field friction/wind integration and signal attenuation quality scoring.
- Migration strategy: route both through model bindings with tier-specific evaluation.

2. Threshold-to-effect transitions
- Multiple domains currently map threshold crossings to effects/hazards directly.
- Migration strategy: use model `output_signature` with process-only output adapters (`effect`, `hazard_increment`, `flow_adjustment`).

## Migration plan

1. Introduce canonical model schemas + registries (`schema/models/*`, `data/registries/*`).
2. Add deterministic model evaluation runtime (`src/models/model_engine.py`) with cache and budget handling.
3. Bridge process runtime via `process.model_evaluate_tick` and output process families.
4. Migrate existing inline response curves incrementally behind registered model IDs.
5. Keep current behavior deterministic during migration; no semantic changes without explicit series upgrade.

## Invariants and constraints

- `A1` Determinism is primary.
- `A2` Process-only mutation.
- `A10` Explicit degradation and refusal.
- `INV-REALISM-DETAIL-MUST-BE-MODEL` (warn phase currently).
