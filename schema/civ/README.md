# CIV Schema Specs (CIV0+)

Status: draft
Version: 1

This directory contains canonical CIV0+ schema specifications for settlements,
infrastructure, institutions, organizations, governance, and legitimacy. These
documents define authoritative data formats and invariants only; no runtime
logic is introduced here.

Scope: CIV data formats for settlements, infrastructure, institutions, and governance.

## Invariants
- No settlement or infrastructure exists without construction contracts.
- Governance is institution-backed and law-gated.
- Schemas do not encode runtime logic.

## Forbidden assumptions
- Schemas may define authoritative behavior.
- Free settlements or governance are allowed.

## Dependencies
- `docs/architecture/CIVILIZATION_MODEL.md`
- `schema/economy/README.md`

## Canonical CIV0+ index
- `schema/civ/SPEC_SETTLEMENTS.md`
- `schema/civ/SPEC_INFRASTRUCTURE.md`
- `schema/civ/SPEC_INSTITUTIONS.md`
- `schema/civ/SPEC_ORGANIZATIONS.md`
- `schema/civ/SPEC_GOVERNANCE.md`
- `schema/civ/SPEC_LEGITIMACY.md`

## Related economy specs (CIV0+)
- `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- `schema/economy/SPEC_MARKETS_AND_EXCHANGE.md`
- `schema/economy/SPEC_LOGISTICS.md`
- `schema/economy/SPEC_RESOURCE_CONSERVATION.md`

## Legacy CIV1/Phase references (supplemental)
The following documents remain for reference and historical context. They are
non-authoritative when conflicts exist with CIV0+:
- `schema/civ/SPEC_CITIES.md`
- `schema/civ/SPEC_BUILDINGS_MACHINES.md`
- `schema/civ/SPEC_LOGISTICS_FLOWS.md`
- `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- `schema/civ/SPEC_POPULATION_COHORTS.md`
- `schema/civ/SPEC_COHORTS_MINIMAL.md`
- `schema/civ/SPEC_HOUSEHOLDS.md`
- `schema/civ/SPEC_MIGRATION.md`
- `schema/civ/SPEC_NEEDS_MINIMAL.md`

## Versioning policy
All CIV schemas follow `schema/SCHEMA_VERSIONING.md` and
`schema/SCHEMA_MIGRATION.md`:
- Every schema has `schema_id`, semantic version, and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

Schemas in this directory are authoritative for data formats and validation
rules. Runtime behavior lives in `game/` and must not be encoded here.

Reality and life integration:
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/LIFE_AND_POPULATION.md`
