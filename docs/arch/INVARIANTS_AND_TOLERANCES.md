# Invariants and Tolerances (SCALE0)

Status: binding.
Scope: what MUST match exactly vs what MAY vary within declared bounds.

## Purpose
Scaling is only valid if invariants are preserved exactly and sufficient
statistics remain within declared tolerances.

## A) Invariants (must match exactly)
These invariants MUST match exactly across collapse/expand and across tiers.

| ID | Invariant | Notes |
| --- | --- | --- |
| SCALE0-PROJECTION-001 | Macro state is a semantics-preserving projection of micro ground truth. | Expansion must not change outcomes beyond declared tolerances. |
| SCALE0-CONSERVE-002 | Conservation invariants match exactly. | Includes resource totals, energy balances, population counts, inventory conservation, network topology/capacities, committed contracts, authority state. |
| SCALE0-COMMIT-003 | Collapse/expand occurs only at commit boundaries. | No mid-commit fidelity changes. |
| SCALE0-DETERMINISM-004 | Collapse/expand and macro stepping are deterministic. | Cross-thread results are stable; no wall-clock dependence. |
| SCALE0-NO-EXNIHILO-007 | Expansion does not introduce entities/resources ex nihilo. | Reconstruction must use deterministic seeds. |
| SCALE0-REPLAY-008 | Replay equivalence holds across collapse/expand. | Same inputs yield identical macro capsules and event ordering. |

## B) Sufficient statistics (match within tolerance)
These statistics MAY vary within declared tolerances but MUST respect
monotonicity constraints and error-compounding rules.

| Stat ID | Description | Error bounds | Monotonicity | Error compounding |
| --- | --- | --- | --- | --- |
| STAT-SCALE-PROD-DIST | Production capacity distribution (by sector/site). | L1 distance <= 1% of total capacity; per-bin abs error <= 1 unit or <= 5% relative. | Total capacity must not increase on collapse; bins non-negative. | Errors do not compound across commit boundaries; repeated collapse/expand remains within bound vs capsule. |
| STAT-SCALE-CONS-DIST | Consumption distribution (by cohort/sector). | L1 distance <= 2% of total consumption; per-bin abs error <= 1 unit or <= 5% relative. | Totals non-negative; demand bins cannot exceed supply invariants. | Same as above. |
| STAT-SCALE-FAIL-RATE | Failure rate estimates (hazard/MTBF). | Absolute error <= 0.5% or relative error <= 10% (whichever is larger). | If tagged monotonic, hazard must not decrease without explicit repair events. | Same as above. |
| STAT-SCALE-BELIEF-DIST | Belief/knowledge distributions. | L1 distance <= 0.02; total mass within 1e-6 of 1.0. | If tagged observed, probability mass cannot decrease. | Same as above. |
| STAT-SCALE-WEAR-DIST | Wear/fatigue distributions. | Mean and 95th percentile within 1% or 1 unit (whichever larger). | Wear cannot decrease absent explicit repair events. | Same as above. |

## C) Tolerance declaration rules
For each sufficient statistic:
- Acceptable error bounds MUST be explicit.
- Monotonicity constraints MUST be explicit.
- Error compounding behavior MUST be explicit.

Global rules:
- If no tolerance is declared, the statistic is treated as an invariant.
- Errors do not accumulate across commit boundaries; each capsule is a new
  bound for subsequent collapse/expand cycles.
- Violations of tolerance bounds are refusals, not silent adjustments.

## See also
- `docs/arch/INVARIANTS.md`
- `docs/arch/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/arch/SCALING_MODEL.md`
