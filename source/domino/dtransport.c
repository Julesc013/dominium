#include "domino/dtransport.h"

#include <string.h>

#define DTRANSPORT_MAX_NODES 1024
#define DTRANSPORT_MAX_EDGES 2048

static TransportNode g_nodes[DTRANSPORT_MAX_NODES];
static U32           g_node_count = 0;

static RoadEdge      g_roads[DTRANSPORT_MAX_EDGES];
static U32           g_road_count = 0;
static RailEdge      g_rails[DTRANSPORT_MAX_EDGES];
static U32           g_rail_count = 0;
static SeaLaneEdge   g_sea_lanes[DTRANSPORT_MAX_EDGES];
static U32           g_sea_lane_count = 0;
static AirRouteEdge  g_air_routes[DTRANSPORT_MAX_EDGES];
static U32           g_air_route_count = 0;

static TransportNodeId dtransport_alloc_node(void)
{
    if (g_node_count >= DTRANSPORT_MAX_NODES) return 0;
    return (TransportNodeId)(++g_node_count);
}

static RoadEdgeId dtransport_alloc_road(void)
{
    if (g_road_count >= DTRANSPORT_MAX_EDGES) return 0;
    return (RoadEdgeId)(++g_road_count);
}

static RailEdgeId dtransport_alloc_rail(void)
{
    if (g_rail_count >= DTRANSPORT_MAX_EDGES) return 0;
    return (RailEdgeId)(++g_rail_count);
}

static SeaLaneEdgeId dtransport_alloc_sea_lane(void)
{
    if (g_sea_lane_count >= DTRANSPORT_MAX_EDGES) return 0;
    return (SeaLaneEdgeId)(++g_sea_lane_count);
}

static AirRouteEdgeId dtransport_alloc_air_route(void)
{
    if (g_air_route_count >= DTRANSPORT_MAX_EDGES) return 0;
    return (AirRouteEdgeId)(++g_air_route_count);
}

static RoadEdge *dtransport_get_road(RoadEdgeId id)
{
    if (id == 0 || id > g_road_count) return 0;
    return &g_roads[id - 1];
}

static RailEdge *dtransport_get_rail(RailEdgeId id)
{
    if (id == 0 || id > g_rail_count) return 0;
    return &g_rails[id - 1];
}

static SeaLaneEdge *dtransport_get_sea_lane(SeaLaneEdgeId id)
{
    if (id == 0 || id > g_sea_lane_count) return 0;
    return &g_sea_lanes[id - 1];
}

static AirRouteEdge *dtransport_get_air_route(AirRouteEdgeId id)
{
    if (id == 0 || id > g_air_route_count) return 0;
    return &g_air_routes[id - 1];
}

TransportNodeId dtransport_register_node(const WPosTile *tile)
{
    TransportNodeId id = dtransport_alloc_node();
    if (id == 0) return 0;
    g_nodes[id - 1].id = id;
    if (tile) {
        g_nodes[id - 1].tile = *tile;
    } else {
        memset(&g_nodes[id - 1].tile, 0, sizeof(WPosTile));
    }
    return id;
}

RoadEdgeId dtransport_register_road_edge(TransportNodeId a, TransportNodeId b)
{
    RoadEdgeId id = dtransport_alloc_road();
    if (id == 0) return 0;
    g_roads[id - 1].id = id;
    g_roads[id - 1].a = a;
    g_roads[id - 1].b = b;
    g_roads[id - 1].attached_vehicle = 0;
    return id;
}

RailEdgeId dtransport_register_rail_edge(TransportNodeId a, TransportNodeId b)
{
    RailEdgeId id = dtransport_alloc_rail();
    if (id == 0) return 0;
    g_rails[id - 1].id = id;
    g_rails[id - 1].a = a;
    g_rails[id - 1].b = b;
    g_rails[id - 1].attached_vehicle = 0;
    return id;
}

SeaLaneEdgeId dtransport_register_sea_lane(TransportNodeId a, TransportNodeId b)
{
    SeaLaneEdgeId id = dtransport_alloc_sea_lane();
    if (id == 0) return 0;
    g_sea_lanes[id - 1].id = id;
    g_sea_lanes[id - 1].a = a;
    g_sea_lanes[id - 1].b = b;
    g_sea_lanes[id - 1].attached_vehicle = 0;
    return id;
}

AirRouteEdgeId dtransport_register_air_route(TransportNodeId a, TransportNodeId b)
{
    AirRouteEdgeId id = dtransport_alloc_air_route();
    if (id == 0) return 0;
    g_air_routes[id - 1].id = id;
    g_air_routes[id - 1].a = a;
    g_air_routes[id - 1].b = b;
    g_air_routes[id - 1].attached_vehicle = 0;
    return id;
}

bool dtransport_attach_vehicle_to_road(RoadEdgeId edge, VehicleId vehicle)
{
    RoadEdge *e = dtransport_get_road(edge);
    if (!e) return false;
    e->attached_vehicle = vehicle;
    return true;
}

bool dtransport_attach_vehicle_to_rail(RailEdgeId edge, VehicleId vehicle)
{
    RailEdge *e = dtransport_get_rail(edge);
    if (!e) return false;
    e->attached_vehicle = vehicle;
    return true;
}

bool dtransport_attach_vehicle_to_sea_lane(SeaLaneEdgeId edge, VehicleId vehicle)
{
    SeaLaneEdge *e = dtransport_get_sea_lane(edge);
    if (!e) return false;
    e->attached_vehicle = vehicle;
    return true;
}

bool dtransport_attach_vehicle_to_air_route(AirRouteEdgeId edge, VehicleId vehicle)
{
    AirRouteEdge *e = dtransport_get_air_route(edge);
    if (!e) return false;
    e->attached_vehicle = vehicle;
    return true;
}

bool dtransport_query_road_path(TransportNodeId from, TransportNodeId to, RoadEdgeId *out_edges, U32 max_edges, U32 *out_count)
{
    (void)from; (void)to; (void)out_edges; (void)max_edges;
    if (out_count) *out_count = 0;
    return false;
}

bool dtransport_query_rail_path(TransportNodeId from, TransportNodeId to, RailEdgeId *out_edges, U32 max_edges, U32 *out_count)
{
    (void)from; (void)to; (void)out_edges; (void)max_edges;
    if (out_count) *out_count = 0;
    return false;
}

bool dtransport_query_sea_lane_path(TransportNodeId from, TransportNodeId to, SeaLaneEdgeId *out_edges, U32 max_edges, U32 *out_count)
{
    (void)from; (void)to; (void)out_edges; (void)max_edges;
    if (out_count) *out_count = 0;
    return false;
}

bool dtransport_query_air_route_path(TransportNodeId from, TransportNodeId to, AirRouteEdgeId *out_edges, U32 max_edges, U32 *out_count)
{
    (void)from; (void)to; (void)out_edges; (void)max_edges;
    if (out_count) *out_count = 0;
    return false;
}
