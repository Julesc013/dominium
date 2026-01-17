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
