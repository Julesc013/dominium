# LIFE Schema Specs (LIFE0+)

Status: draft
Version: 2

This directory contains canonical LIFE0+ schema specifications for life
entities, population models, birth/death contracts, identity, and continuity.
These are documentation-only and define authoritative formats and constraints.

Scope: life entity, population, birth/death, and identity formats.

## Invariants
- No life appears without birth contracts.
- No life disappears without death contracts.
- Schemas do not encode runtime logic.

## Forbidden assumptions
- Life entities can be fabricated for convenience.
- Identity can be overwritten by refinement details.

## Dependencies
- `docs/arch/LIFE_AND_POPULATION.md`
- `docs/arch/REALITY_LAYER.md`

## Canonical LIFE0+ index
- `schema/life/SPEC_LIFE_ENTITIES.md`
- `schema/life/SPEC_POPULATION_MODELS.md`
- `schema/life/SPEC_BIRTH_CONTRACTS.md`
- `schema/life/SPEC_DEATH_CONTRACTS.md`
- `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
- `schema/life/SPEC_REINCARNATION.md`

## Legacy LIFE0/Phase 6 references (supplemental)
The following documents describe prior phase plans or implementation guides.
They remain useful but are subordinate to LIFE0+ in case of conflict:
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

Reality layer:
- `docs/arch/REALITY_LAYER.md`
- `docs/arch/LIFE_AND_POPULATION.md`
