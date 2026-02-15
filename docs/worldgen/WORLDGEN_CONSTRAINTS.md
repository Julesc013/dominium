Status: CANONICAL
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# WorldGen Constraints

This document defines the deterministic, data-driven contract for goal-driven world generation constraints.

## Purpose

Constraint solving is a structural selection layer over worldgen plans.
It does not change simulation primitives and does not mutate runtime state directly.

## Constraint Categories

1. Hard constraints
- Must be satisfied for a candidate seed to remain eligible.
- Any hard-constraint failure removes the candidate from selection.

2. Soft constraints
- Produce weighted score contributions for eligible candidates.
- Do not by themselves disqualify candidates.

3. Scoring functions
- Deterministic functions over preview metrics.
- Must use stable numeric operations and explicit weight values.

## Deterministic Tie-Break Rules

1. Compare total score (higher score wins).
2. If score ties, compare hard-constraint pass count (higher wins).
3. If still tied, apply configured tie break policy:
- `lexicographic`: lowest canonical seed token wins.
- `seed_order`: earliest `candidate_seeds` order wins.
- `explicit_field`: compare configured metric field lexicographically/numerically.
4. If still tied after configured policy, fall back to canonical seed lexicographic order.

## Multi-Seed Search Discipline

1. Seed expansion must be deterministic from `base_seed` and candidate index.
2. Candidate generation order is fixed and stable.
3. Candidate evaluation order is fixed and stable.
4. Search output must include all evaluated candidates and deterministic refusal states.

## Artifact Lifecycle

1. Constraint specification artifact:
- Authored in pack data or local artifact.
- Validated by `worldgen_constraints.schema`.

2. Search plan artifact:
- Derived output from deterministic search.
- Validated by `worldgen_search_plan.schema`.
- Contains candidate seeds, score summary, selected seed, and deterministic hash.

3. Commit artifact:
- Uses selected seed to drive downstream world artifact compilation.
- No hidden fallback to unconstrained seed once constraints are selected.

## Separation of Responsibilities

1. Constraint specification:
- Declares hard/soft constraints and scoring policies.
- No imperative solver behavior.

2. Plan selection:
- Deterministic candidate evaluation and ranking.
- Produces selection record only.

3. Artifact generation:
- Uses selected seed from search plan.
- Remains a separate stage from search.

## Refusal Semantics

1. `refusal.constraints_unsatisfiable`
- Returned when no candidate satisfies all hard constraints.

2. `refusal.search_exhausted`
- Returned when candidate_count is exhausted without a satisfiable candidate.

3. Refusals must be deterministic and include remediation guidance:
- adjust constraints
- increase candidate_count
- change base_seed

## Invariants

1. No hidden defaults for constraints, scoring, tie-breaking, or candidate_count.
2. No nondeterministic clocks or random sources in selection logic.
3. Candidate ordering and scoring output must be canonical-serializable.
4. Constraint solving remains non-semantic governance over generation inputs.

## Cross-References

- `docs/worldgen/WORLDGEN_PIPELINE.md`
- `schema/worldgen/worldgen_constraints.schema`
- `schema/worldgen/worldgen_search_plan.schema`
- `schemas/worldgen_constraints.schema.json`
- `schemas/worldgen_search_plan.schema.json`
- `docs/contracts/refusal_contract.md`
