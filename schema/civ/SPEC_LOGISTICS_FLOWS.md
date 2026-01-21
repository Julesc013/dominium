--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Logistics flow rules, capacity checks, and cost policies.
SCHEMA:
- Logistics flow record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No teleportation of goods.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LOGISTICS_FLOWS — Deterministic Logistics (CIV1)

Status: draft  
Version: 1

NOTE: Legacy CIV1 spec. Superseded by CIV0+ canonical documents in
`schema/civ/README.md` and `schema/economy/README.md`. Retained for reference
and non-authoritative if conflicts exist.

## Purpose
Define deterministic logistics flows for goods movement without vehicles.

## LogisticsFlow schema
Required fields:
- flow_id
- src_store_ref
- dst_store_ref
- asset_id
- qty
- departure_act
- arrival_act
- capacity_ref
- provenance_summary

Rules:
- arrival_act uses ACT time only.
- Flow application is deterministic and ordered by flow_id.
- Capacity availability is enforced deterministically.

## Determinism requirements
- Flow arrivals are ACT-scheduled and batch-vs-step equivalent.
- Costs are deterministic functions of distance proxy and asset weight class.

## Integration points
- Production chains: `schema/civ/SPEC_PRODUCTION_CHAINS.md`
- Building machines: `schema/civ/SPEC_BUILDINGS_MACHINES.md`

## Prohibitions
- No hidden transfers or teleportation of goods.
- No stochastic routing or random delays.
