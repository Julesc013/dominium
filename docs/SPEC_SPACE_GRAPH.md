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
