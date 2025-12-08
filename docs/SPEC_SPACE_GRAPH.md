# Space Graph (Sites + Routes)

- Graph nodes are `SpaceSiteId` (stations, Lagrange points, vessels-on-rails).
- Edges are `SpaceRoute { id, a, b, base_travel_time_s (Q16.16 seconds), energy_cost (EnergyJ), hazard_0_1 (Q16.16), flags }`.
- Registry lives in `source/domino/dspace_graph.c` with helpers:
  - `dspace_route_register`, `dspace_route_get`, `dspace_route_find`.
  - `dspace_route_neighbors(site, out_ids, max_out)` to enumerate adjacent routes.
  - `dspace_route_pathfind_stub(start, goal)` currently returns direct edge if present (TODO: Dijkstra/A*).

## Space sites
- Defined in `dbody.h` / `dbody.c`:
  - `SpaceSite { id, name, attached_body, orbit, offset }`.
  - `dspace_site_register`, `dspace_site_get`, `dspace_site_pos`.
  - Sites can represent L1–L5 points, stations in orbit, tether anchors, or free-floating references.

## Usage
- Higher-level travel planners build on this graph for transfers, logistics, and missions.
- Hazards encode radiation/trajectory risk; flags are reserved for wormholes/FTL/etc.
- Pathfinding is intentionally stubbed; deterministic algorithms will be slotted in later using this API.
