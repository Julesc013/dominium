# ELEC3 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-03
Scope: ELEC-3 `Advanced Device Models via ConstitutiveModels`

## Findings

1. Device behavior is still partly hardcoded in ELEC-1 solve paths.
- `src/electric/power_network_engine.py` computes resistive/motor load behavior via `_evaluate_load_from_binding`.
- E1 line losses are computed inline with resistance/capacity arithmetic in `solve_power_network_e1`.
- E0 loss fallback is computed inline in `solve_power_network_e0`.

2. Power-factor behavior is mixed between helper math and per-binding inline model branching.
- `compute_pf_permille` is deterministic and reusable.
- Motor PF contribution currently relies on hardcoded branch logic (`model.elec_load_motor_stub`) instead of central model evaluation.

3. Heat-loss representation exists but is duplicated and not fully model-sourced.
- `heat_loss_stub` appears in E0 and E1 edge status rows.
- Fault hooks in ELEC-2 also emit thermal effects (`effect.temperature_increase_local`).
- No unified convention yet for model-originated loss-to-heat outputs.

4. Storage behavior is not yet first-class electrical node state.
- `node_kind=storage` exists in payload registries.
- No canonical `storage_state` schema or deterministic charge/discharge process rows are present.

5. Runtime orchestration is process-driven and deterministic already.
- `process.elec.network_tick` orchestrates solve/fault/protection pathways.
- Safety and protection paths are integrated (`safety.breaker_trip`, LOTO workflows).

## Migration Plan

1. Introduce model-driven device behaviors in constitutive model registries and evaluator dispatch:
- PF correction
- transformer stub
- storage battery
- device loss

2. Add canonical storage state schema and process-only mutation paths:
- `process.storage_charge`
- `process.storage_discharge`

3. Refactor E1 solve usage to apply model outputs for:
- Q compensation
- transformer/device loss
- storage contribution limits
- heat-loss hooks/artifacts

4. Preserve E0 fallback behavior and deterministic downgrade semantics.

5. Extend enforcement:
- no inline device behavior outside model engine/electrical model application surface
- explicit loss-to-heat declaration requirement
