--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_TRANSPORT_NETWORKS — Tile-Anchored Transport Networks (Legacy `dtransport`)

This spec defines the legacy tile-anchored transport network registry used for
early prototypes (`dtransport_*`). It is separate from the refactor TRANS
transform/topology system (`docs/SPEC_TRANS.md`).

## Scope
Applies to:
- node/edge registries for roads/rails/sea lanes/air routes
- stable ID allocation and deterministic ordering rules
- (stub) path query API surface

## Ownership
Transport networks own:
- a node table keyed by `TransportNodeId`
- per-network edge tables keyed by `{Road,Rail,SeaLane,AirRoute}EdgeId`

Nodes carry a `WPosTile` anchor (tile/chunk lattice addressing). This lattice is
domain-specific and MUST NOT be treated as a universal placement grid for other
subsystems (`docs/SPEC_DETERMINISM.md`).

## Determinism + ordering
- IDs are stable integers allocated monotonically (no pointer-derived IDs).
- All tables are fixed-size arrays (bounded; no unbounded growth per tick).
- Any iteration over nodes/edges MUST use ascending ID order.
- Any future routing/pathfinding MUST obey canonical ordering rules from
  `docs/SPEC_GRAPH_TOOLKIT.md` (no unordered traversal; explicit tie-breaks).

## API surface
Implemented plumbing (`include/domino/dtransport.h`, `source/domino/dtransport.c`):
- `dtransport_register_node(tile)` → `TransportNodeId`
- `dtransport_register_road_edge(a,b)` → `RoadEdgeId`
- `dtransport_register_rail_edge(a,b)` → `RailEdgeId`
- `dtransport_register_sea_lane(a,b)` → `SeaLaneEdgeId`
- `dtransport_register_air_route(a,b)` → `AirRouteEdgeId`
- `dtransport_attach_vehicle_to_{road,rail,sea_lane,air_route}(edge, vehicle)`
- `dtransport_query_*_path` currently returns `false` (no pathfinding in this revision)

## Forbidden behaviors
- Treating UI snapping/grids as authoritative network topology.
- Unordered iteration (hash maps, pointer identity ordering) in determinism paths.
- Platform-dependent inputs (wall-clock time, filesystem/network IO).

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_GRAPH_TOOLKIT.md`
- `docs/SPEC_PACKETS.md`
