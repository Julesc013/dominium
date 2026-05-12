# Schema Migration Law (DATA0)

Migrations are mandatory governance for breaking schema changes.
All migrations MUST be explicit, deterministic, and auditable.

## Core Rule

Migrate or refuse; never silently coerce.

## Migration Requirements

- Migrations MUST be version-to-version (e.g., 2.1.0 -> 3.0.0).
- Migrations MUST be deterministic and repeatable.
- Migrations MUST preserve unknown fields (skip-unknown).
- Migrations SHOULD be reversible where possible.
- Migrations MUST emit an audit trail of actions taken.

## When Migration is Mandatory

- MAJOR version bump of any schema used at runtime or in saves.
- Any change that alters simulation semantics.
- Any change that alters identifier or ordering semantics.

## When Refusal is Mandatory

- No migration exists for a MAJOR bump.
- Migration would require non-deterministic guessing.
- Migration would drop unknown or sim-affecting fields.
- Migration would violate determinism or performance rules.

## Audit Trail Requirements

Every migration MUST record:
- source schema_id and version
- target schema_id and version
- deterministic summary of applied changes
- refusal reason when migration fails

Audit logs MUST be stored with the migrated artifact (save, replay, or export).

## Forbidden Behaviors

- Best-effort guessing of missing data.
- Dropping unknown fields.
- Implicit defaulting for sim-affecting values.
- In-place mutation without provenance or audit trail.

## Migration Plans (Registry)

- dominium.schema.pack_manifest 1.0.0 -> 2.0.0
  - Map required_engine_version -> requires_engine.
  - Map dependencies -> depends.
  - Preserve unknown fields and extensions.
  - Refuse if both old and new forms are present but conflict.
  - Process ID: process.schema.migrate.pack_manifest.v1_to_v2
  - Deterministic function:
    tools/schema_migration/schema_migration_runner.py::migrate_pack_manifest_1_0_0_to_2_0_0

## Machine-readable migration registry

- File: `schema/SCHEMA_MIGRATION_REGISTRY.json`
- Purpose: deterministic, explicit migration route table.
- Required fields per route:
  - `schema_id`
  - `source_version`
  - `target_version`
  - `migration_process_id`
  - `migration_function`
  - `data_loss`
  - `invocation` (`explicit` only)

## Explicit invocation contract

- Migrations are invoked explicitly via tooling or tests.
- No background or implicit migration is permitted.
- Example invocation:
  - `python tools/schema_migration/schema_migration_runner.py --schema-id dominium.schema.pack_manifest --source-version 1.0.0 --target-version 2.0.0 --input in.json --output out.json`
