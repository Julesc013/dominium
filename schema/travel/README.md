--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None (policy docs only).
GAME:
- Uses travel schema for reachability, visitability, and scheduling effects.
SCHEMA:
- Canonical travel graph, edges, scheduling, and denial semantics.
TOOLS:
- Validation and inspection tooling for travel graphs.
FORBIDDEN:
- No runtime logic in schema docs.
DEPENDENCIES:
- Engine -> none (schema only).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# Travel Schema (TRAVEL0)

This folder defines the canonical travel graph model used to schedule all
movement and reachability across scales.

Scope: travel graph edges, scheduling, capacity, cost, and denial semantics.

## Invariants
- Movement occurs only along explicit travel edges.
- Travel is scheduled on ACT and law-gated.
- Reachability does not imply visitability.

## Forbidden assumptions
- Teleportation is allowed without an edge.
- Travel can bypass capacity or cost declarations.

## Dependencies
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/TRAVEL_AND_MOVEMENT.md`

See:
- `SPEC_TRAVEL_GRAPH.md`
- `SPEC_TRAVEL_EDGES.md`
- `SPEC_TRAVEL_SCHEDULING.md`
- `SPEC_TRAVEL_DENIAL.md`
- `SPEC_TRAVEL_CAPACITY.md`
- `SPEC_TRAVEL_COST.md`
- `SPEC_TRAVEL_LATENCY.md`
- `SPEC_TRAVEL_QUEUEING.md`
- `SPEC_EXOTIC_TRAVEL.md`
- `SPEC_PORTALS.md`
- `SPEC_WORMHOLES.md`
- `SPEC_HYPERSPACE.md`

Reality layer:
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
