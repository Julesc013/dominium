# Project Governance (FUTURE0)

Status: binding.
Scope: how architectural decisions are made and enforced.

Governance protects invariants and prevents simplification drift. This file
summarizes the decision process; it does not replace ARCH0 or CHANGE_PROTOCOL.

## Invariants
- ARCH0 and canon docs are binding.
- Invariant changes require architectural review.
- Determinism and law gates are mandatory.

## Decision hierarchy
1) ARCH0 constitution and canonical docs are binding.
2) Change protocol governs all sim-affecting changes.
3) CI enforcement IDs encode non-negotiable checks.

## Required review
- Invariant changes require architectural review and canon updates.
- Schema changes require versioning and migration/refusal plans.
- Mod policy violations are refused.

## Enforcement baseline
- Law and capability gates are mandatory.
- Determinism is required for authoritative logic.
- Absence and refusal are valid outcomes.

## Forbidden assumptions
- Invariants are optional or negotiable.
- Review can be bypassed for "small" changes.

## Dependencies
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/CHANGE_PROTOCOL.md`

## See also
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/CHANGE_PROTOCOL.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
