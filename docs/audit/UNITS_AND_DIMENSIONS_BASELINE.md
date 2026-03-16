Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-1 units and dimensional system baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Units And Dimensions Baseline

## 1) Baseline Scope
MAT-1 establishes a deterministic, extensible, fixed-point dimensional system for authoritative quantities.

Primary references:
- `docs/materials/UNITS_AND_DIMENSIONS.md`
- `docs/reality/CONSERVATION_AND_EXCEPTIONS.md` (RS-2)
- `docs/reality/TIER_TAXONOMY_AND_TRANSITIONS.md` (RS-4)

## 2) Base Dimension Baseline
Canonical base dimensions in `data/registries/base_dimension_registry.json`:
- `M` mass
- `L` length
- `T` time
- `Q` charge
- `THETA` temperature
- `I` ledger balance/currency

Base dimensions are registry-declared and pack-extendable; engine logic does not hardcode SI-only behavior.

## 3) Derived Dimension Baseline
Canonical derived dimensions in `data/registries/dimension_registry.json`:
- `dim.mass`
- `dim.length`
- `dim.time`
- `dim.charge`
- `dim.temperature`
- `dim.velocity`
- `dim.acceleration`
- `dim.force`
- `dim.energy`
- `dim.power`
- `dim.pressure`
- `dim.density`
- `dim.momentum`
- `dim.angular_momentum`
- `dim.currency`
- `dim.energy_per_temperature` (entropy stub support)

Representative vectors:
- `dim.energy = M L^2 T^-2`
- `dim.force = M L T^-2`
- `dim.power = M L^2 T^-3`

## 4) Unit Registry Baseline
Canonical units in `data/registries/unit_registry.json` include:
- `unit.kg`, `unit.m`, `unit.s`, `unit.C`, `unit.K`
- `unit.N`, `unit.J`, `unit.W`, `unit.Pa`
- `unit.m_per_s`, `unit.m_per_s2`
- `unit.currency_unit`
- `unit.J_per_K` (entropy stub channel)

Unit scale factors are fixed-point integers (`scale_factor_to_canonical`), and quantity type default units must match quantity dimensions.

## 5) Quantity Type + Fixed-Point Policy
Canonical quantity types in `data/registries/quantity_type_registry.json` include:
- `quantity.mass_energy_total`
- `quantity.mass`
- `quantity.energy`
- `quantity.charge_total`
- `quantity.entropy_metric` (stub)
- `quantity.ledger_balance`

Authoritative numeric policy:
- invariant channels require fixed-point (`invariant_numeric_type = fixed_point`)
- canonical policy integrated into `numeric_precision_policy_registry`:
  - 64-bit signed storage
  - deterministic quantization by fractional bits
  - overflow behavior `refuse`
  - error budget tracked for deterministic exception emission (`exception.numeric_error_budget`)

Runtime implementation:
- `src/materials/dimension_engine.py`
  - `dimension_add`, `dimension_mul`, `dimension_div`, `dimension_equals`
  - `quantity_add`, `quantity_convert`
  - deterministic fixed-point ops (`fixed_point_add`, `fixed_point_mul`, `fixed_point_div`)

## 6) Ledger Enforcement Integration
RS-2 integration enforces quantity and dimension compatibility:
- ledger APIs consume `quantity_id` channels bound by `quantity_type_registry`
- mismatched/missing dimensions are refused before finalize
- refusal codes:
  - `refusal.dimension.mismatch`
  - `refusal.unit.invalid_conversion`
  - `refusal.numeric.fixed_point_overflow` (fixed-point invariant path)

Integration points:
- `src/reality/ledger/ledger_engine.py`
- `tools/xstack/sessionx/process_runtime.py`

## 7) Guardrails And Test Baseline
RepoX invariants:
- `INV-NO-RAW-FLOAT-IN-INVARIANT-MATH`
- `INV-QUANTITY-TYPE-DECLARED`
- `INV-DIMENSION-COMPATIBILITY-ENFORCED`

AuditX analyzers:
- `RawFloatInInvariantSmell` (`E56_RAW_FLOAT_IN_INVARIANT_SMELL`)
- `DimensionDriftSmell` (`E57_DIMENSION_DRIFT_SMELL`)

TestX coverage:
- `testx.materials.dimension_add_valid`
- `testx.materials.dimension_add_invalid_refusal`
- `testx.materials.unit_conversion_deterministic`
- `testx.materials.fixed_point_overflow_handling`
- `testx.materials.ledger_dimension_mismatch_refusal`

## 8) Extension Guidance (Fictional Quantities)
To add fictional channels (example: mana):
1. Add base or derived dimensions via registries (base dimensions only when strictly necessary).
2. Add units with deterministic fixed-point scale factors.
3. Add quantity types with fixed-point invariant numeric type and dimension-matching default units.
4. Bind conservation behavior through RS-2 contract sets by `quantity_id`.
5. Keep process-only mutation and replay determinism intact.

## 9) MAT-2..MAT-10 Extension Points
1. MAT-2: quantity graph arithmetic kernels and deterministic expression evaluation.
2. MAT-3: material process IO typing against quantity dimensions.
3. MAT-4: assembly/material interfaces with typed quantity channels.
4. MAT-5: collapse/expand dimensional consistency proofs across tiers.
5. MAT-6: provenance compaction retaining dimensional auditability.
6. MAT-7: failure/maintenance dimensional channels (wear, stress, thermal budgets).
7. MAT-8: multiplayer/SRZ deterministic dimensional reconciliation.
8. MAT-9: pack/mod evolution migrations for dimension/unit registry semver.
9. MAT-10: domain solver boundaries using deterministic-float internals with fixed-point boundary contracts.

## 10) Gate Execution Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=968 (warn-level findings present)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.dimension_add_valid,testx.materials.dimension_add_invalid_refusal,testx.materials.unit_conversion_deterministic,testx.materials.fixed_point_overflow_handling,testx.materials.ledger_dimension_mismatch_refusal`
   - result: `status=pass`, selected_tests=5
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.mat1 --cache on --format json`
   - result: `result=complete`
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
