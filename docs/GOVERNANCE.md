# Project Governance (FUTURE0)

Status: binding.
Scope: how architectural decisions are made and enforced.

Governance protects invariants and prevents simplification drift. This file
summarizes the decision process; it does not replace ARCH0 or CHANGE_PROTOCOL.

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

## See also
- `docs/arch/ARCH0_CONSTITUTION.md`
- `docs/arch/CHANGE_PROTOCOL.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
