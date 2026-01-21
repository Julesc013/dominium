# FUTURE0 Enforcement Notes

Status: binding.
Scope: how FUTURE0 rules are enforced in CI and review.

This document describes enforcement expectations for FUTURE0 guardrails. It
does not introduce new runtime logic; it defines compliance expectations.

## Enforcement IDs (canonical)
- FUTURE0-INVARIANT-001: changes touching invariants require arch review.
- FUTURE0-MOD-002: mods violating schema policy are refused.
- FUTURE0-NODEBT-003: no silent fallback for unknown data.

## Enforcement mechanisms
- Documentation lint for invariant and canon updates.
- Schema lint for versioning, unknown-field behavior, and mod policy.
- Manual audit when invariants or execution semantics are touched.

## See also
- `docs/ci/CI_ENFORCEMENT_MATRIX.md`
- `schema/schema_policy.md`
- `schema/mod_extension_policy.md`
