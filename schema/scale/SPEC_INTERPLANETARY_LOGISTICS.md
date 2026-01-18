--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Interplanetary logistics flows and transition timing.
SCHEMA:
- Interplanetary logistics record formats and versioning metadata.
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
# SPEC_INTERPLANETARY_LOGISTICS - Interplanetary Flows (CIV4)

Status: draft  
Version: 1

## Purpose
Define deterministic interplanetary logistics as scheduled flows.

## ShipmentFlow schema
Required fields:
- flow_id
- src_domain_ref
- dst_domain_ref
- asset_id
- qty
- departure_act
- arrival_act
- capacity_ref
- provenance_summary
- next_due_tick
- status (pending/arrived/blocked)

Rules:
- arrival_act is computed deterministically from domain rules and tech level.
- Ordering uses (arrival_act, flow_id).

## Determinism requirements
- Batch vs step equivalence MUST hold.
- No per-tick scanning of all flows.

## Integration points
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`
- Time warp: `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Logistics primitives: `schema/civ/SPEC_LOGISTICS_FLOWS.md`

## Prohibitions
- No physics simulation for travel.
- No global flow updates outside due scheduling.
