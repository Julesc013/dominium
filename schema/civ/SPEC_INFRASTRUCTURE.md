--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Infrastructure construction, maintenance, and capacity rules.
SCHEMA:
- Infrastructure record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit infrastructure creation.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_INFRASTRUCTURE — Infrastructure Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define persistent infrastructure systems that provide capacity, not free
outputs: housing, industry, power, transport, communication, and defense.

## Infrastructure types (canonical)
- HOUSING
- INDUSTRY
- POWER
- TRANSPORT
- COMMUNICATION
- DEFENSE
- SUPPORT (shared services)

## Required fields
- infrastructure_id (stable, unique within a timeline)
- infrastructure_type (one of the canonical types)
- existence_state (EXIST0 state)
- domain_ref (spatial anchor)
- settlement_ref (optional, owning settlement)
- construction_contract_refs (explicit provenance)
- maintenance_state (explicit, schedulable)
- capacity_profile (declared limits, not outputs)
- provenance_refs (origin and causal chain)

Optional fields:
- production_chain_refs (when infrastructure hosts production)
- logistics_interface_refs (when it acts as a node)
- decay_state (explicit condition record)

## Rules (absolute)
- Infrastructure must be constructed and recorded; no implicit spawn.
- Maintenance is required; neglect degrades capacity deterministically.
- Capacity is explicit; output without inputs is forbidden.
- Infrastructure cannot produce goods without a production contract.

## Integration points
- Settlements: `schema/civ/SPEC_SETTLEMENTS.md`
- Production chains: `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- Logistics: `schema/economy/SPEC_LOGISTICS.md`
- Resource conservation: `schema/economy/SPEC_RESOURCE_CONSERVATION.md`
- Reality layer: `docs/architecture/REALITY_LAYER.md`

## See also
- `docs/architecture/CIVILIZATION_MODEL.md`
- `docs/architecture/ECONOMY_AND_LOGISTICS.md`
