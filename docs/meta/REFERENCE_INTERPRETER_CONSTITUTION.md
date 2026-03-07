# Reference Interpreter Constitution

Status: CANONICAL
Last Updated: 2026-03-07
Scope: META-REF-0

## 1) Purpose
Reference interpreters provide slow, simple, deterministic correctness checks against fast runtime implementations for critical subsystems.

They are verification surfaces only and do not alter runtime semantics.

## 2) Definition
A reference interpreter is a pure evaluator that:
- consumes canonical subsystem inputs,
- recomputes expected outputs with straightforward deterministic logic,
- emits a stable output hash and comparison payload.

Requirements:
- deterministic ordering,
- portable behavior (no OS-dependent branching),
- no wall-clock dependency,
- no production-path coupling.

## 3) Runtime vs Reference Pairing
Each covered subsystem must expose:
- runtime evaluator (authoritative fast path), and
- reference evaluator (derived verification path).

META-REF-0 initial pairings:
- `phys.energy_ledger` <-> `ref.energy_ledger`
- `meta.coupling_scheduler` <-> `ref.coupling_scheduler`
- `sys.boundary_invariant_check` <-> `ref.system_invariant_check`
- `meta.compiled_model_verify` <-> `ref.compiled_model_verify`

Reserved stubs:
- `ref.proc_quality_baseline`
- `ref.logic_eval_engine`

## 4) Equivalence Criteria
Exact equivalence required for:
- discrete decision sets and orderings,
- invariant booleans (`pass`/`fail`),
- proof ids/hash references where exact policy applies.

Tolerance-bounded equivalence required for:
- numeric residuals and aggregates under declared TOL policy.

## 5) Execution Profiles
- FAST:
  - reference suite disabled by default,
  - no heavy dual-evaluation cost.
- STRICT:
  - targeted reference checks allowed (curated fixtures/windows).
- FULL:
  - curated deterministic reference windows required,
  - mismatch is a failure.

## 6) Discrepancy Contract
On mismatch, report must include:
- seed,
- tick window,
- subsystem id,
- runtime hash,
- reference hash,
- divergence signature,
- minimal deterministic reproduction payload.

Reports are written as derived artifacts and may be compacted.

## 7) Governance
- Reference evaluators are required for critical subsystems under RepoX/AuditX rules.
- Missing evaluator coverage is warning in STRICT and failing in FULL.
- Any detected semantic drift must be fixed before baseline promotion.
