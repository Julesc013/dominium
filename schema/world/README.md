# WORLD Schema Specs (CONTENT0)

Status: draft
Version: 1

This directory contains schema specifications for deterministic world and
universe data models. These are documentation-only and define authoritative
formats and constraints.

## Index
- `schema/world/SPEC_UNIVERSE_MODEL.md`
- `schema/world/SPEC_GALAXY_MODEL.md`
- `schema/world/SPEC_SYSTEM_MODEL.md`
- `schema/world/SPEC_CELESTIAL_BODY.md`
- `schema/world/SPEC_ORBITAL_RAILS.md`
- `schema/world/SPEC_SURFACE_AND_REGIONS.md`
- `schema/world/SPEC_WORLD_DATA_IMPORT.md`

## Versioning policy
All WORLD schemas follow `schema/SCHEMA_VERSIONING.md` and `schema/SCHEMA_MIGRATION.md`:
- Every schema has a semantic version and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

Schemas in this directory are authoritative for data formats and validation
rules. Runtime logic and gameplay behavior live in `game/` and must not be
encoded here.
