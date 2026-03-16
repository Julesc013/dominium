Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Coupling Budget And Relevance Constitution

Status: CANONICAL  
Last Updated: 2026-03-06  
Scope: COUPLE-0 deterministic coupling budgets and relevance filtering.

## 1) Purpose

Prevent coupling evaluation explosion as cross-domain coverage grows, while preserving deterministic replay and equivalence within declared error bounds.

This constitution governs only scheduling and evaluation selection. It does not authorize semantic changes to domain models.

## 2) Coupling Evaluation Categories

Every coupling contract must declare `coupling_priority_class`:

- `critical`
  - Must run each tick window when present.
  - If unavailable, trigger fail-safe escalation.
- `important`
  - Runs when relevant.
  - May be deferred under budget pressure.
- `optional`
  - Runs when relevant and budget remains.
  - Safe to skip with bounded error growth.

## 3) Relevance Definition

A coupling evaluation is relevant if any condition holds:

1. Declared input signature changed beyond tolerance (`TOL` policy).
2. Referenced hazard crossed threshold bands.
3. System entered ROI or explicit inspection was requested.
4. Certification check requested this tick/window.
5. SYS forced-expand trigger is pending.
6. Contract is explicitly forced by policy/action.

Default relevance check is hash-delta over declared inputs plus tolerance policy lookup.

## 4) Budget Rules

Each domain/system owner declares deterministic coupling budget:

- `coupling_budget_units_per_tick`
- owner id: domain id or system id

Each coupling contract declares:

- `coupling_cost_units`
- `coupling_priority_class`
- `coupling_relevance_policy_id`

Deterministic selection order under budget:

1. Select all `critical` couplings.
2. Select `relevant-important` by `(priority_weight, coupling_contract_id)`.
3. Select `relevant-optional` by `(priority_weight, coupling_contract_id)`.

Skipped relevant couplings must be logged with explicit reason.

## 5) Degradation Semantics

When coupling is skipped:

- Apply policy:
  - hold last output value, or
  - safe default output
- Record increased error estimate.
- Emit deterministic coupling evaluation record with reason:
  - `skipped_budget` or `skipped_irrelevant`

For critical couplings:

- Skip is forbidden in normal flow.
- If execution cannot proceed, trigger:
  - `safety.fail_safe_shutdown`
  - SYS forced-expand request when reliability policy requires.

## 6) Determinism, Proof, And Replay

- Coupling selection order must be stable across thread/platform.
- Selection keys are explicit and sorted.
- Every selection decision is recorded (`coupling_evaluation_record`).
- Proof bundle includes:
  - coupling evaluation hash chain
  - coupling budget registry version hash
  - coupling relevance policy registry version hash

Replay verifier must be able to recompute selection + hashes for a window.

## 7) Process Discipline

- Coupling model evaluation stays model-driven through canonical process/runtime pathways.
- Direct ad hoc cross-domain evaluation bypass is forbidden.
- Scheduler is required for coupling-bound model evaluations.

## 8) Non-Goals

- No CFD or bespoke solvers.
- No wall-clock scheduling.
- No nondeterministic coupling arbitration.
- No bypass of model engine, tolerance policy, or coupling contracts.
