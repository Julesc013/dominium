--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Settlement construction, maintenance, and upgrade rules.
SCHEMA:
- Settlement record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit settlement creation.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_SETTLEMENTS — Settlement Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define the canonical settlement model for constructed aggregations of
infrastructure (camps, villages, cities, orbitals, and mobile fleets).

## Settlement types (canonical)
- CAMP
- VILLAGE
- CITY
- MEGASTRUCTURE
- ORBITAL
- MOBILE

## Required fields
- settlement_id (stable, unique within a timeline)
- settlement_type (one of the canonical types)
- existence_state (EXIST0 state)
- domain_ref (primary spatial domain or anchor)
- construction_contract_refs (explicit provenance)
- infrastructure_refs (bounded list)
- maintenance_state (explicit, schedulable)
- provenance_refs (origin and causal chain)

Optional fields:
- population_refs (cohorts or abstract populations)
- governance_ref (governance context or institution)
- mobility_ref (for MOBILE settlements)
- archive_state (LIVE | FROZEN | ARCHIVED | FORKED)

## Rules (absolute)
- No settlement exists without a construction contract effect.
- Settlements consume resources for maintenance; neglect triggers decay.
- Settlement membership and ordering are deterministic and bounded.
- Settlements may exist without population (ruins or abandoned sites).

## Integration points
- Infrastructure: `schema/civ/SPEC_INFRASTRUCTURE.md`
- Economy actors: `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- Production chains: `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- Domain volumes: `schema/domain/README.md`
- Travel and logistics: `schema/travel/README.md`
- Life populations: `schema/life/SPEC_POPULATION_MODELS.md`

## See also
- `docs/architecture/CIVILIZATION_MODEL.md`
- `docs/architecture/COLLAPSE_AND_DECAY.md`
