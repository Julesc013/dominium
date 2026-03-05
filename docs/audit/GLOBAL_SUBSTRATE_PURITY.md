# GLOBAL Substrate Purity Sweep

Date: 2026-03-05
Phase: `GLOBAL-REVIEW-2`

## Scope
Targeted refactor-only sweep for promoted substrate purity blocker:
- `E179_INLINE_RESPONSE_CURVE_SMELL` (STRICT promoted)

No gameplay feature additions and no new solver introduction.

## Before/After Delta
- Baseline (previous tracked `docs/audit/auditx/SUMMARY.md`):
  - `architecture.inline_response_curve_smell: 7`
- Current strict audit (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - `architecture.inline_response_curve_smell: 0`
  - `promoted_blockers: 0`

## Refactors Applied
Moved inline response-curve math into model-layer helper functions (`src/models/model_engine.py`) and switched call sites to consume those deterministic helpers:

- `evaluate_field_modifier_curve`
  - caller: `src/fields/field_engine.py`
- `aggregate_structural_edge_metrics`
  - caller: `src/mechanics/structural_graph_engine.py`
- `compute_wear_ratio_permille`
  - caller: `src/mobility/maintenance/wear_engine.py`
- `compute_lateral_accel_units`
- `compute_derailment_threshold_units`
  - caller: `src/mobility/micro/constrained_motion_solver.py`
- `compute_congestion_ratio_permille`
- `compute_congestion_multiplier_permille`
  - caller: `src/mobility/traffic/traffic_engine.py`
- `resolve_speed_multiplier_permille`
  - caller: `src/mobility/travel/travel_engine.py`
- `evaluate_receipt_acceptance_curve`
  - caller: `src/signals/trust/trust_engine.py`

## Correctness Notes
- Fixed an integration recursion bug introduced during refactor in `src/mobility/traffic/traffic_engine.py` by aliasing model-helper imports.
- Verified that `testx.mobility.wear.influences_derail_threshold` fails on clean `HEAD` and current branch (pre-existing baseline failure; not introduced by this patch).

## Validation
- `python -m py_compile src/models/model_engine.py src/fields/field_engine.py src/mechanics/structural_graph_engine.py src/mobility/maintenance/wear_engine.py src/mobility/micro/constrained_motion_solver.py src/mobility/traffic/traffic_engine.py src/mobility/travel/travel_engine.py src/signals/trust/trust_engine.py` -> pass
- `python tools/xstack/auditx/check.py --repo-root . --profile STRICT` -> pass (`promoted_blockers=0`)
- `python tools/xstack/testx_all.py --repo-root . --profile FAST --cache off --subset test_field_sampling_deterministic,testx.mechanics.stress_ratio_calculation,testx.mobility.wear.accumulation_deterministic,test_velocity_derived_from_momentum,testx.mobility.travel.tick_progress_deterministic,testx.signals.acceptance_threshold` -> pass

## Contracts/Schema Impact
- Runtime contracts/schemas: unchanged.
- Behavior shape: preserved; implementation location moved from domain inline curves to model-layer helpers.
