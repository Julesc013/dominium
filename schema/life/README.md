# LIFE Schema Specs (Phase 6)

Status: draft
Version: 1

This directory contains schema specifications for LIFE0 (person/body/controller,
death/estate, control authority, continuation policies, and lineage overview).
These are documentation-only and define authoritative formats and constraints.

## Index
- `schema/life/SPEC_LIFE_CONTINUITY.md`
- `schema/life/SPEC_DEATH_AND_ESTATE.md`
- `schema/life/SPEC_CONTROL_AUTHORITY.md`
- `schema/life/SPEC_CONTINUATION_POLICIES.md`
- `schema/life/SPEC_BIRTH_LINEAGE_OVERVIEW.md`

## Versioning policy
All LIFE schemas follow `schema/SCHEMA_VERSIONING.md` and `schema/SCHEMA_MIGRATION.md`:
- Every schema has `schema_id`, semantic version, and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

Schemas in this directory are authoritative for data formats and validation rules.
Runtime logic and gameplay behavior live in `game/` and must not be encoded here.
