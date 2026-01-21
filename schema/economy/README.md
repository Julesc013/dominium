# Economy Schema Specs (CIV0+)

Status: draft
Version: 1

This directory contains canonical CIV0+ economy schema specifications for
economic actors, production chains, markets, logistics, and conservation.
These documents define authoritative data formats and invariants only; no
runtime logic is introduced here.

## Canonical CIV0+ economy index
- `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- `schema/economy/SPEC_MARKETS_AND_EXCHANGE.md`
- `schema/economy/SPEC_LOGISTICS.md`
- `schema/economy/SPEC_RESOURCE_CONSERVATION.md`

## Related civilization specs (CIV0+)
- `schema/civ/SPEC_SETTLEMENTS.md`
- `schema/civ/SPEC_INFRASTRUCTURE.md`
- `schema/civ/SPEC_INSTITUTIONS.md`
- `schema/civ/SPEC_ORGANIZATIONS.md`
- `schema/civ/SPEC_GOVERNANCE.md`
- `schema/civ/SPEC_LEGITIMACY.md`

## Versioning policy
All economy schemas follow `schema/SCHEMA_VERSIONING.md` and
`schema/SCHEMA_MIGRATION.md`:
- Every schema has `schema_id`, semantic version, and stability level.
- MAJOR bumps require explicit migration or refusal.
- MINOR bumps must be skip-unknown safe (unknown fields preserved).
- PATCH changes must not alter simulation behavior.

Schemas in this directory are authoritative for data formats and validation
rules. Runtime behavior lives in `game/` and must not be encoded here.

Reality and civilization integration:
- `docs/arch/REALITY_LAYER.md`
- `docs/arch/CIVILIZATION_MODEL.md`
