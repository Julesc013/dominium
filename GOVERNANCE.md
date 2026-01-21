# Project Governance (FUTURE0)

Status: binding.
Scope: decision hierarchy, review requirements, and enforcement baseline.

Governance protects invariants and prevents simplification drift. This file
summarizes the decision process; it does not replace ARCH0 or CHANGE_PROTOCOL.

## Invariants
- ARCH0 and CANON docs are binding.
- Invariant changes require architectural review and canon updates.
- Determinism and law gates are non-negotiable.

## Decision hierarchy
1) ARCH0 constitution and canonical docs are binding.
2) Change protocol governs all sim-affecting changes.
3) CI enforcement IDs encode non-negotiable checks.

## Required review
- Invariant changes require architectural review and canon updates.
- Schema changes require versioning and migration/refusal plans.
- Mod policy violations are refused.

## Forbidden assumptions
- "Small" changes can bypass review or CI enforcement.
- Invariants are optional or negotiable.

## Dependencies
- `docs/arch/ARCH0_CONSTITUTION.md`
- `docs/arch/CHANGE_PROTOCOL.md`
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`

## See also
- `docs/GOVERNANCE.md`
