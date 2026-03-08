## GEO-6 Retro-Consistency Audit

Date: 2026-03-09
Scope: deterministic pathing, traversal cost layers, shard-safe route staging

### Canon and invariant context

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/geo/GEO_CONSTITUTION.md`
- `docs/geo/SPATIAL_INDEX_AND_IDENTITY.md`
- `docs/geo/REFERENCE_FRAMES_AND_PRECISION.md`
- `docs/geo/METRIC_QUERY_ENGINE.md`
- `docs/geo/FIELD_BINDING_TO_GEO.md`
- `docs/geo/PROJECTION_AND_LENS_MODEL.md`

### Current MOB pathfinding and movement assumptions

- `src/mobility/travel/itinerary_engine.py`
  - Current macro routing is graph-based through `src/core/graph/routing_engine.py`.
  - It is deterministic, but it operates on `node_id` and `edge_id`, not `geo_cell_key`.
  - This is an integration seam for infrastructure overlays, not a replacement for geometry-portable routing.
- `src/mobility/travel/travel_engine.py`
  - Travel commitments consume precomputed `route_edge_ids`.
  - The travel loop assumes a network itinerary already exists and does not expose a GEO-native route query layer.
- `src/mobility/micro/constrained_motion_solver.py`
  - Local segment length already routes through `geo_distance(...)`.
  - Orientation logic still derives heading from `dx` and `dy`, which is acceptable for local micro pose handling but not as a general path heuristic substrate.
- `src/mobility/network/mobility_network_engine.py`
  - Infrastructure remains represented as a deterministic overlay network.
  - GEO-6 should treat this as an optional cost/preference layer rather than a mandatory path substrate.

### Hardcoded dimensional and topology assumptions

- Existing macro mobility routing assumes a graph over authored endpoints rather than a topology/partition cell graph.
- Existing micro motion helpers still read `x/y/z` vectors directly for local body motion and spline constraints.
- No canonical path engine currently exists for:
  - torus wrap cell graphs
  - atlas tile traversal
  - portal-identified cell adjacency
  - 4D or higher-dimensional neighborhood graphs

### ROI scheduling integration point

- `src/system/roi/system_roi_scheduler.py`
  - Radius checks already route through `roi_distance_mm(...)`.
  - No path-cost or reachability substrate exists yet for deterministic travel-time or traversal-bounded ROI planning.
  - GEO-6 should add adapter surfaces here rather than reintroducing raw range loops.

### Road, rail, and portal overlay integration points

- `src/core/graph/routing_engine.py`
  - Provides the deterministic tie-break and cross-shard staged-segment pattern GEO-6 should mirror.
- `src/mobility/travel/itinerary_engine.py`
  - Existing road/rail-style travel overlays can consume GEO path results later through conversion or hybrid planning.
- `src/pollution/dispersion_engine.py`
  - Already depends on `geo_neighbors(...)`, confirming the repository now has a canonical GEO cell-graph seam for neighborhood iteration.
- GEO portal support currently exists only as topology/neighbor semantics from GEO-0/GEO-3.
  - GEO-6 must route through those neighbor surfaces rather than inventing a separate portal table.

### Required integration points

- MOB:
  - add GEO-native path requests for geometry-portable routing
  - keep existing graph-itinerary travel as an infrastructure overlay consumer
- ROI scheduling:
  - add deterministic traversal-based distance/cost helpers for future expansion policies
- road/rail overlays:
  - consume traversal infrastructure preference hooks instead of replacing GEO neighbors
- portal links:
  - remain topology-driven through `geo_neighbors(...)`
- future LOGIC/PROC/service dispatch:
  - consume canonical derived `path_result` or canonical plan artifacts rather than embedding their own heuristic search

### Migration notes

- Future spatial path queries must use `geo_cell_key` or `position_ref` endpoints and `traversal_policy_id`.
- No domain should enumerate cell neighbors ad hoc once GEO-6 lands.
- Existing network-graph route systems stay valid for explicit infrastructure graphs, but topology-portable movement and service reachability should enter through GEO-6 first.
- Cross-shard path intent should reference staged shard segments and boundary hops, not direct remote shard state reads.

### Audit conclusion

- The repository already has deterministic routing patterns and deterministic GEO neighbor/distance primitives.
- What is missing is the canonical bridge between them: a GEO-native path substrate over cell graphs with stable tie-breaking, bounded expansions, optional field/infrastructure cost layers, and shard-stage planning.
- GEO-6 should add that bridge without refactoring existing vehicle or authored graph travel into a new model.
