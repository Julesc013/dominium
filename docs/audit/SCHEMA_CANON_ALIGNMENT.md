Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# Schema Canon Alignment Note (BR-0)

## Why the integer ladder layout is not applicable

The repository canonical schema mechanism uses **flat `.schema` files** with
semantic `schema_version` and explicit migration/refusal rules. There is no
`schema/<name>/vN/` ladder in the current canon, and enforcing one would be a
structural change, not a hardening pass.

Authoritative references:
- `schema/SCHEMA_VERSIONING.md` (semantic versioning rules)
- `schema/SCHEMA_MIGRATION.md` (migration/refusal requirements)
- `docs/architecture/SCHEMA_STABILITY.md` (FROZEN/EVOLVING policy)
- `docs/architecture/SCHEMA_CHANGE_NOTES.md` (change note requirements)

## Canonical versioning and migration mechanism (as implemented)

- Each schema is a **single flat file** under `schema/*.schema`.
- Required fields: `schema_id`, `schema_version` (semantic), `stability`.
- **MAJOR** bumps require explicit migration or refusal.
- **Unknown fields must round-trip** unchanged (skip-unknown).
- No silent coercion; migrate or refuse.

Enforcement and implementation surfaces:
- `tests/schema/schema_version_immutability_tests.py`
- `tests/contract/schema_change_notes_required.py`
- `tests/schema/schema_unknown_field_tests.py`
- `tools/ci/validate_world_definition.py`
- `tools/worldgen_offline/world_definition_lib.py`

These checks and validators enforce:
- Schema version immutability expectations.
- Explicit change notes for schema changes.
- Refusal on unknown or unsupported schema versions in tooling.

## Explicit migration invocation (how it is satisfied)

Migrations are **invoked explicitly** by tools or pipelines that handle
schema-bearing artifacts (packs, world definitions, saves, replays). There is
no automatic background migration. When a migration is absent or unsafe, the
tools refuse with a deterministic error.

Examples of explicit refusal behavior on unsupported versions:
- `tools/worldgen_offline/world_definition_lib.py` (refuses unknown schema_version)
- `tools/ci/validate_world_definition.py` (validates and refuses incompatible versions)

## Authoritative procedure to add schema versions and migrations

1) Update the `.schema` file **with a semver bump** matching the change type.
2) Add a migration plan entry to `schema/SCHEMA_MIGRATION.md` (for MAJOR bumps).
3) Update `docs/architecture/SCHEMA_CHANGE_NOTES.md` with INV-SCHEMA-* notes.
4) Ensure tests continue to pass:
   - schema version immutability
   - unknown-field round-trip
   - schema change notes required

This alignment removes the L2 conflict without changing canon.
