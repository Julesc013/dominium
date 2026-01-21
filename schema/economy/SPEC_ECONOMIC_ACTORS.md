--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Economic actor behavior, production/consumption rules.
SCHEMA:
- Economic actor record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit creation of goods or actors.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_ECONOMIC_ACTORS — Economic Actor Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define the canonical economic actors that own resources, schedule production,
and participate in exchange. Actors cannot conjure value.

## Actor types (canonical)
- INDIVIDUAL
- ORGANIZATION
- INSTITUTION
- SETTLEMENT
- COHORT

## Required fields
- actor_id (stable, unique within a timeline)
- actor_type (one of the canonical types)
- existence_state (EXIST0 state)
- ownership_refs (resources, infrastructure, accounts)
- production_contract_refs (authorized production)
- consumption_contract_refs (authorized consumption)
- provenance_refs (origin and causal chain)

Optional fields:
- market_access_refs (markets or exchange venues)
- logistics_interface_refs (shipment endpoints)
- governance_ref (when actor participates in governance)

## Rules (absolute)
- Actors may only produce via explicit production contracts.
- Actors may only consume via explicit consumption effects.
- Resource ownership must be explicit and auditable.

## Integration points
- Settlements: `schema/civ/SPEC_SETTLEMENTS.md`
- Institutions: `schema/civ/SPEC_INSTITUTIONS.md`
- Organizations: `schema/civ/SPEC_ORGANIZATIONS.md`
- Production chains: `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- Resource conservation: `schema/economy/SPEC_RESOURCE_CONSERVATION.md`
- Life entities: `schema/life/SPEC_LIFE_ENTITIES.md`

## See also
- `docs/arch/ECONOMY_AND_LOGISTICS.md`
