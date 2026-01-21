# Schema Policy (FUTURE0)

Status: binding.
Scope: global schema extension and compatibility rules.

Schemas define authoritative data formats. They must evolve without breaking
determinism or introducing silent behavior changes.

## Compatibility rules
- Every schema has a `schema_id`, semantic version, and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

## Unknown fields and fallbacks
- Unknown fields must be preserved or refused deterministically.
- Silent fallback is forbidden.
- Compatibility decisions must be auditable.

## Determinism and invariants
- Schema changes must not introduce nondeterminism.
- Invariant changes require architectural review and canon updates.

## Mod constraints
- Mods may only extend schemas via documented extension points.
- Mods may not redefine or remove canonical fields.
- Mods must declare schema versions and compatibility targets.

## See also
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`
- `schema/mod_extension_policy.md`
