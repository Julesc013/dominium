# Process Capsule Model

Status: AUTHORITATIVE
Last Updated: 2026-03-06
Scope: PROC-5 deterministic process capsules for macro execution and expand-on-demand.

## 1) ProcessCapsule

A `ProcessCapsule` is a macro abstraction of a `(process_id, version)` pair that:

- preserves deterministic boundary behavior within declared error bounds
- exposes explicit internal state via STATEVEC definitions/snapshots
- declares a validity domain for safe macro execution
- optionally references a COMPILE-0 `compiled_model_id`
- remains process-governed and provenance-linked.

Required declarations:

- input/output signature references
- `error_bound_policy_id` (TOL)
- `validity_domain_ref`
- `state_vector_definition_id`
- `coupling_budget_id` (COUPLE)
- optional `compiled_model_id`.

## 2) Capsule Eligibility

Capsule generation is allowed only when:

- maturity state is `capsule_eligible`
- stability horizon is satisfied by PROC-4 policy
- QC pass envelope remains at/above policy threshold.

Generation must refuse if any gate fails.

## 3) Capsule Execution Semantics

`process.process_capsule_execute` must deterministically produce:

- output batch quantity/quality outcomes
- QC sampling outcomes (PROC-3 policy)
- energy transform records (PHYS-3 integration)
- emissions records (POLL hooks)
- canonical process/capsule execution records with provenance links.

Execution is macro-first:

- valid inputs and context: execute capsule model
- invalid domain or policy breach: forced expand to micro run or deterministic refusal.

## 4) Invalidations

A capsule is invalidated when any of the following occurs:

- input values outside declared validity ranges
- environment bounds exceeded
- tool condition drift exceeds threshold
- QC failures beyond policy tolerance
- governing spec reference changes.

Invalidation must emit a canonical invalidation record and explain artifact.

## 5) Expand-On-Demand

On invalid capsule execution request:

- request forced expand to micro process execution when policy/budget allows
- otherwise return deterministic refusal with reason code and remediation metadata.

No silent fallback and no silent mutation are permitted.

