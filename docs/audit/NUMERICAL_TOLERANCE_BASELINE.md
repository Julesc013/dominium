# NUMERICAL_TOLERANCE_BASELINE

## Scope
- Series: `TOL-0`
- Objective: global deterministic tolerance + rounding discipline without changing quantity semantics or introducing float-based authority paths.
- Canon alignment: `docs/canon/constitution_v1.md` A1/A2/E2/E3/E6 and `AGENTS.md` process-only mutation + determinism constraints.

## Registry Summary
- Added canonical tolerance contract schemas:
  - `schema/meta/quantity_tolerance.schema`
  - `schema/meta/model_residual_policy.schema`
  - `schemas/quantity_tolerance.schema.json`
  - `schemas/model_residual_policy.schema.json`
- Added canonical registries:
  - `data/registries/quantity_tolerance_registry.json`
  - `data/registries/model_residual_policy_registry.json`
- CompatX schema registry updated for both tolerance/residual schema IDs.

## Rounding Rules
- Deterministic numeric helper substrate added at `src/meta/numeric.py`.
- Authoritative helpers:
  - `deterministic_divide`
  - `deterministic_mul_div`
  - `deterministic_round`
  - `normalize_rounding_mode`
- Allowed rounding modes:
  - `round_half_to_even`
  - `floor`
  - `ceiling`
  - `truncate`
- Core numeric paths migrated to deterministic helpers:
  - `src/time/time_mapping_engine.py` drift multiplier path (permille fixed-point, no float-round path).
  - `src/physics/momentum_engine.py` velocity derivation from momentum.
  - `src/mobility/micro/free_motion_solver.py` momentum-to-velocity path.

## Conservation Tolerance Settings
- Energy transform enforcement now supports tolerance fallback from registry:
  - `src/physics/energy/energy_ledger_engine.py`
- Ledger runtime now consumes quantity tolerance policy rows and emits residual diagnostics:
  - `src/reality/ledger/ledger_engine.py`
  - `extensions.residual_exceeded` rows are attached when configured mode/tolerance is exceeded.

## Overflow and Residual Policies
- Overflow behavior is explicit and policy-driven (`fail|saturate`) via:
  - `src/meta/numeric.py` + runtime wiring in `tools/xstack/sessionx/process_runtime.py`.
- Energy total and related quantity mutations route through `_apply_quantity_overflow_policy` in authoritative process runtime pathways.
- No wrap-around policy is introduced.

## Proof and Replay Coverage
- Proof surfaces now include:
  - `quantity_tolerance_registry_hash`
  - `rounding_mode_policy_hash`
- Integrated in:
  - `tools/xstack/sessionx/process_runtime.py`
  - `src/net/policies/policy_server_authoritative.py`
  - `src/control/proof/control_proof_bundle.py`
  - `schemas/control_proof_bundle.schema.json`
- Added numeric verification tool:
  - `tools/meta/tool_verify_numeric_stability.py` (+ shell/cmd wrappers).

## Enforcement Readiness
- RepoX strict invariants added:
  - `INV-QUANTITY-TOLERANCE-DECLARED`
  - `INV-DETERMINISTIC-ROUND-ONLY`
  - `INV-NO-IMPLICIT-FLOAT`
  - `INV-NO-IMPLICIT-OVERFLOW`
- AuditX strict-promoted analyzers added:
  - `E236_IMPLICIT_FLOAT_USAGE_SMELL`
  - `E237_MISSING_TOLERANCE_SMELL`
  - `E238_DIRECT_DIVISION_WITHOUT_ROUND_SMELL`

## Test Coverage
- Added TestX:
  - `test_all_quantities_have_tolerance`
  - `test_rounding_deterministic`
  - `test_energy_conservation_within_tolerance`
  - `test_no_float_usage`
  - `test_cross_platform_hash_stability_under_load`

## Readiness for PROV-0
- Numeric policy is now explicit, registry-driven, hashable, and enforceable in strict governance lanes.
- Residual and overflow behavior are no longer implicit in core energy/momentum/time substrate paths.
- Substrate is ready for provenance-level numeric trace requirements in `PROV-0`.

## Gate Snapshot (2026-03-05)
- `RepoX STRICT`: `pass` (warnings only; no refusal/fail findings).
- `AuditX STRICT`: `fail` (pre-existing strict-promoted `E179_INLINE_RESPONSE_CURVE_SMELL` findings outside TOL touch set).
- `TestX STRICT`: `fail` (large pre-existing baseline failures unrelated to TOL delta; TOL-specific tests pass).
- Numeric stability stress harness:
  - `python tools/meta/tool_verify_numeric_stability.py --window-ticks 8192 --drift-scale 64`
  - Result: `complete` with deterministic replay match.
- Strict build gate:
  - `python tools/ci/validate_all.py --strict` returned refusal because executable is missing in local environment (`validate_all executable not found`).
