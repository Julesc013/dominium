# Schema Catalog

This directory defines authoritative data-shape contracts for Dominium.

## Versioning rules
- Every schema MUST declare `schema_id` and `schema_version`.
- `schema_version` follows semantic versioning.
- Changes that remove or rename fields require a MAJOR version bump.
- Changes that add optional fields require a MINOR version bump.
- Patch bumps are limited to clarifications and non-semantic fixes.

## Backward compatibility
- Schemas are open maps; unknown fields MUST be preserved.
- Unknown fields MUST round-trip through tools without loss.
- ID meanings are stable and MUST NOT be reused with new semantics.

## Extension rules
- Every record MUST include an `extensions: map` field.
- Mods add new data via namespaced IDs and extension bags.
- Enums remain closed; open sets use IDs/registries instead.

## Unit annotations
- All numeric fields MUST carry unit tags.
- Units must exist in `docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Governance
- Schema changes require entries in `docs/architecture/SCHEMA_CHANGE_NOTES.md`.
- Schema changes require TestX validation and may trigger migration notes.
- Migration routes are explicit in `schema/SCHEMA_MIGRATION_REGISTRY.json`.
- Migration invocation must be explicit; no silent coercion.
