# WAR Schema Specs (CIV5-WAR0)

Status: draft
Version: 1

This directory contains schema specifications for deterministic conflict,
security forces, engagements, occupation, and interplanetary war. These are
documentation-only and define authoritative formats and constraints.

## Index
- `schema/war/SPEC_CONFLICT_CANON.md`
- `schema/war/SPEC_SECURITY_FORCES.md`
- `schema/war/SPEC_ENGAGEMENTS.md`
- `schema/war/SPEC_OCCUPATION_AND_RESISTANCE.md`
- `schema/war/SPEC_INTERPLANETARY_WAR.md`

## Versioning policy
All WAR schemas follow `schema/SCHEMA_VERSIONING.md` and `schema/SCHEMA_MIGRATION.md`:
- Every schema has `schema_id`, semantic version, and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

Schemas in this directory are authoritative for data formats and validation rules.
Runtime logic and gameplay behavior live in `game/` and must not be encoded here.
