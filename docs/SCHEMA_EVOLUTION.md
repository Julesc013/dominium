Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# Schema Evolution (Operational Rules)

This document restates the repository’s **implemented** schema evolution rules.
If any conflict exists, the authoritative sources are:
- `schema/SCHEMA_VERSIONING.md`
- `schema/SCHEMA_MIGRATION.md`
- `docs/architecture/SCHEMA_STABILITY.md`

## Canonical layout

- Schemas are **flat** files under `schema/*.schema`.
- Each schema declares:
  - `schema_id` (stable identifier)
  - `schema_version` (semantic: MAJOR.MINOR.PATCH)
  - `stability` (core | extension | experimental)
- Migration routes are declared in:
  - `schema/SCHEMA_MIGRATION.md` (human-auditable)
  - `schema/SCHEMA_MIGRATION_REGISTRY.json` (machine-auditable)

## Versioning rules (summary)

- PATCH: bugfix only; no semantic change.
- MINOR: backward-compatible additions; skip-unknown safe.
- MAJOR: breaking change; requires migration or refusal.
- Version numbers are monotonic per `schema_id`.

## Migration and refusal

- Migrate or refuse; never silently coerce.
- MAJOR changes require an explicit migration plan in
  `schema/SCHEMA_MIGRATION.md`.
- Migration routes require explicit process IDs in
  `data/registries/process_registry.json`.
- Migration invocation is explicit only; no automatic background migration.
- Refuse when migration is missing, lossy, or nondeterministic.
- Unknown fields must round-trip unchanged.

## Enforcement (implemented)

TestX contracts:
- `tests/schema/schema_version_immutability_tests.py`
- `tests/schema/schema_unknown_field_tests.py`
- `tests/schema/schema_migration_tests.py`
- `tests/contract/schema_change_notes_required.py`

Tooling checks:
- `tools/ci/validate_world_definition.py`
- `tools/worldgen_offline/world_definition_lib.py`

These enforce explicit versioning, skip-unknown preservation, and refusal on
unsupported versions.

RepoX checks:
- `INV-SCHEMA-VERSION-BUMP` (version bump required when schema changes)
- `INV-SCHEMA-MIGRATION-ROUTES` (migration registry validity and process linkage)
