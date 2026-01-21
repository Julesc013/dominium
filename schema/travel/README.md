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

See:
- `SPEC_TRAVEL_GRAPH.md`
- `SPEC_TRAVEL_EDGES.md`
- `SPEC_TRAVEL_SCHEDULING.md`
- `SPEC_TRAVEL_DENIAL.md`
