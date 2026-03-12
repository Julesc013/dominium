Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Batching And Substepping Policy

Status: CANONICAL  
Last Updated: 2026-03-04  
Scope: deterministic tick batching/substepping under TEMP-0.

## 1) Allowed Policies

Deterministic policies are declared in `data/registries/substep_policy_registry.json`.

Baseline policy IDs:
- `substep.none`
- `substep.fixed_4`
- `substep.fixed_8`
- `substep.closed_form_only`

## 2) Allowed Batching

- Advance canonical time in fixed tick buckets of size `N`.
- Bucket size must be declared by policy or process inputs.
- Bucket processing order remains canonical tick order.

## 3) Allowed Substepping

- Fixed `K` substeps per bucket (`K` is registry declared).
- Closed-form deterministic integration path (`substep.closed_form_only`).
- Substep policy must be deterministic and must not consult wall-clock time.

## 4) Forbidden Behavior

- Adaptive step-size changes based on floating-point error.
- Runtime-tuned substep count from real-time performance variance.
- Hidden per-platform stepping differences in authoritative outcomes.

## 5) Degradation Rules

When budget pressure occurs:
- degrade by deterministic policy order
- log deterministic downgrade decision
- do not reorder canonical ticks

## 6) Governance

RepoX and TestX enforce:
- deterministic substep policy declaration
- no adaptive-step tokens in authoritative temporal paths
- wall-clock prohibition in authoritative tick/step logic
