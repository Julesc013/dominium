# Transport Networks

- Node/edge registries (stub) live in `include/domino/dtransport.h` / `source/domino/dtransport.c`. Types: `TransportNodeId`, `RoadEdgeId`, `RailEdgeId`, `SeaLaneEdgeId`, `AirRouteEdgeId`.
- Nodes carry a `WPosTile` anchor. Edges connect two nodes and optionally hold an attached `VehicleId` (for trains/convoys/ships/aircraft following network routes).
- APIs:
  - `dtransport_register_node(tile)` → node id
  - `dtransport_register_{road,rail,sea_lane,air_route}(a,b)` → edge id
  - `dtransport_attach_vehicle_to_{road,rail,sea_lane,air_route}(edge, vehicle)` to bind a vehicle to a segment
  - `dtransport_query_*_path` stubs pathfinding; currently return false and zero-length.
- Implementation is deterministic and fixed-point-friendly; graph storage is simple arrays sized for early prototypes. Replace with full routing and scheduling later.
