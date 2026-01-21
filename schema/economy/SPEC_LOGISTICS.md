--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic scheduling primitives.
GAME:
- Logistics rules, routing policy, loss handling.
SCHEMA:
- Logistics record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No teleportation of goods.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LOGISTICS — Logistics Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define logistics as scheduled movement of goods along Travel edges with
capacity, cost, and latency. Logistics is never instantaneous.

## Shipment (canonical)
Required fields:
- shipment_id (stable, unique within a timeline)
- origin_ref (actor or settlement)
- destination_ref (actor or settlement)
- cargo_manifest (resources and quantities)
- travel_edge_ref (TRAVEL edge)
- schedule_policy (ACT-based timing)
- capacity_constraints (edge or carrier limits)
- provenance_refs (origin and causal chain)

Optional fields:
- loss_policy (spoilage, theft, damage)
- transfer_points (intermediate routing)
- authority_ref (inspection or interdiction)

## Rules (absolute)
- Goods move only via Travel edges; no instant transfer.
- Capacity and cost must be declared for every shipment.
- Delays and losses are explicit and deterministic.

## Integration points
- Travel graph: `schema/travel/README.md`
- Economic actors: `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- Production chains: `schema/economy/SPEC_PRODUCTION_CHAINS.md`
- Settlements: `schema/civ/SPEC_SETTLEMENTS.md`
- Domains: `schema/domain/README.md`

## See also
- `docs/arch/ECONOMY_AND_LOGISTICS.md`
