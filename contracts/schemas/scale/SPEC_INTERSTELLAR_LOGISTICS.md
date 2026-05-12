--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Interstellar logistics flows and transition timing.
SCHEMA:
- Interstellar logistics record formats and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No fabricated arrivals.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_INTERSTELLAR_LOGISTICS - Interstellar Flows (CIV4)

Status: draft  
Version: 1

## Purpose
Define deterministic interstellar logistics and travel as scheduled flows.

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
- Travel time is deterministic and tech-level bound.
- Ordering uses (arrival_act, flow_id).

## Determinism requirements
- Batch vs step equivalence MUST hold.
- No per-tick scanning of all flows.

## Integration points
- Scale domains: `schema/scale/SPEC_SCALE_DOMAINS.md`
- Time warp: `schema/scale/SPEC_SCALE_TIME_WARP.md`
- Cross-shard messages: `docs/SPEC_CROSS_SHARD_MESSAGES.md`

## Prohibitions
- No physical interstellar simulation.
- No global knowledge of transit status.
