#ifndef DOMINO_DTRANSPORT_H
#define DOMINO_DTRANSPORT_H

#include "dworld.h"
#include "dvehicle.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t TransportNodeId;
typedef uint32_t RoadEdgeId;
typedef uint32_t RailEdgeId;
typedef uint32_t SeaLaneEdgeId;
typedef uint32_t AirRouteEdgeId;

typedef struct {
    TransportNodeId id;
    WPosTile        tile;
} TransportNode;

typedef struct {
    RoadEdgeId      id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} RoadEdge;

typedef struct {
    RailEdgeId      id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} RailEdge;

typedef struct {
    SeaLaneEdgeId   id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} SeaLaneEdge;

typedef struct {
    AirRouteEdgeId  id;
    TransportNodeId a;
    TransportNodeId b;
    VehicleId       attached_vehicle;
} AirRouteEdge;

TransportNodeId dtransport_register_node(const WPosTile *tile);

RoadEdgeId     dtransport_register_road_edge(TransportNodeId a, TransportNodeId b);
RailEdgeId     dtransport_register_rail_edge(TransportNodeId a, TransportNodeId b);
SeaLaneEdgeId  dtransport_register_sea_lane(TransportNodeId a, TransportNodeId b);
AirRouteEdgeId dtransport_register_air_route(TransportNodeId a, TransportNodeId b);

bool dtransport_attach_vehicle_to_road(RoadEdgeId edge, VehicleId vehicle);
bool dtransport_attach_vehicle_to_rail(RailEdgeId edge, VehicleId vehicle);
bool dtransport_attach_vehicle_to_sea_lane(SeaLaneEdgeId edge, VehicleId vehicle);
bool dtransport_attach_vehicle_to_air_route(AirRouteEdgeId edge, VehicleId vehicle);

/* Path queries are stubbed: return false if not found or unimplemented */
bool dtransport_query_road_path(TransportNodeId from, TransportNodeId to, RoadEdgeId *out_edges, U32 max_edges, U32 *out_count);
bool dtransport_query_rail_path(TransportNodeId from, TransportNodeId to, RailEdgeId *out_edges, U32 max_edges, U32 *out_count);
bool dtransport_query_sea_lane_path(TransportNodeId from, TransportNodeId to, SeaLaneEdgeId *out_edges, U32 max_edges, U32 *out_count);
bool dtransport_query_air_route_path(TransportNodeId from, TransportNodeId to, AirRouteEdgeId *out_edges, U32 max_edges, U32 *out_count);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DTRANSPORT_H */
