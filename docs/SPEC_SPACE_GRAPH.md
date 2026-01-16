--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Space Graph (Sites + Routes)

- Graph nodes are `SpaceSiteId` (stations, Lagrange points, vessels-on-rails).
- Edges are `SpaceRoute { id, a, b, base_travel_time_s (Q16.16 seconds), energy_cost (EnergyJ), hazard_0_1 (Q16.16), flags }`.
- Registry lives in `source/domino/dspace_graph.c` with helpers:
  - `dspace_route_register`, `dspace_route_get`, `dspace_route_find`.
  - `dspace_route_neighbors(site, out_ids, max_out)` to enumerate adjacent routes.
  - `dspace_route_pathfind_stub(start, goal)` returns a direct edge if present; multi-hop pathfinding is not implemented in this pass.

## Space sites
- Defined in `dbody.h` / `dbody.c`:
  - `SpaceSite { id, name, attached_body, orbit, offset }`.
  - `dspace_site_register`, `dspace_site_get`, `dspace_site_pos`.
  - Sites can represent L1–L5 points, stations in orbit, tether anchors, or free-floating references.

## Usage
- Higher-level travel planners build on this graph for transfers, logistics, and missions.
- Hazards encode radiation/trajectory risk; flags are reserved for explicit future expansion in versioned specs.
- Pathfinding beyond direct-edge lookup is not implemented in this pass; any future algorithm must be deterministic and obey canonical ordering rules (`docs/SPEC_GRAPH_TOOLKIT.md`).
