/*
FILE: include/domino/dtransport.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dtransport
RESPONSIBILITY: Defines the public contract for `dtransport` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DTRANSPORT_H
#define DOMINO_DTRANSPORT_H

#include "dworld.h"
#include "dvehicle.h"

#ifdef __cplusplus
extern "C" {
#endif

/* TransportNodeId: Identifier type for Transport Node objects in `dtransport`. */
typedef uint32_t TransportNodeId;
/* RoadEdgeId: Identifier type for Road Edge objects in `dtransport`. */
typedef uint32_t RoadEdgeId;
/* RailEdgeId: Identifier type for Rail Edge objects in `dtransport`. */
typedef uint32_t RailEdgeId;
/* SeaLaneEdgeId: Identifier type for Sea Lane Edge objects in `dtransport`. */
typedef uint32_t SeaLaneEdgeId;
/* AirRouteEdgeId: Identifier type for Air Route Edge objects in `dtransport`. */
typedef uint32_t AirRouteEdgeId;

/* TransportNode: Public type used by `dtransport`. */
typedef struct {
    TransportNodeId id;
    WPosTile        tile;
} TransportNode;

/* RoadEdge: Public type used by `dtransport`. */
typedef struct {
    RoadEdgeId      id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} RoadEdge;

/* RailEdge: Public type used by `dtransport`. */
typedef struct {
    RailEdgeId      id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} RailEdge;

/* SeaLaneEdge: Public type used by `dtransport`. */
typedef struct {
    SeaLaneEdgeId   id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} SeaLaneEdge;

/* AirRouteEdge: Public type used by `dtransport`. */
typedef struct {
    AirRouteEdgeId  id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} AirRouteEdge;

/* Purpose: Register node.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
TransportNodeId dtransport_register_node(const WPosTile *tile);

/* Purpose: Register road edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
RoadEdgeId     dtransport_register_road_edge(TransportNodeId a, TransportNodeId b);
/* Purpose: Register rail edge.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
RailEdgeId     dtransport_register_rail_edge(TransportNodeId a, TransportNodeId b);
/* Purpose: Register sea lane.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
SeaLaneEdgeId  dtransport_register_sea_lane(TransportNodeId a, TransportNodeId b);
/* Purpose: Register air route.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
AirRouteEdgeId dtransport_register_air_route(TransportNodeId a, TransportNodeId b);

/* Purpose: Attach vehicle to road.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_attach_vehicle_to_road(RoadEdgeId edge, VehicleId vehicle);
/* Purpose: Attach vehicle to rail.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_attach_vehicle_to_rail(RailEdgeId edge, VehicleId vehicle);
/* Purpose: Attach vehicle to sea lane.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_attach_vehicle_to_sea_lane(SeaLaneEdgeId edge, VehicleId vehicle);
/* Purpose: Attach vehicle to air route.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_attach_vehicle_to_air_route(AirRouteEdgeId edge, VehicleId vehicle);

/* Path queries are stubbed: return false if not found or unimplemented */
bool dtransport_query_road_path(TransportNodeId from, TransportNodeId to, RoadEdgeId *out_edges, U32 max_edges, U32 *out_count);
/* Purpose: Query rail path.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_query_rail_path(TransportNodeId from, TransportNodeId to, RailEdgeId *out_edges, U32 max_edges, U32 *out_count);
/* Purpose: Query sea lane path.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_query_sea_lane_path(TransportNodeId from, TransportNodeId to, SeaLaneEdgeId *out_edges, U32 max_edges, U32 *out_count);
/* Purpose: Query air route path.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dtransport_query_air_route_path(TransportNodeId from, TransportNodeId to, AirRouteEdgeId *out_edges, U32 max_edges, U32 *out_count);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DTRANSPORT_H */
