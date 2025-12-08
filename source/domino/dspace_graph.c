#include "domino/dspace_graph.h"

#include <string.h>

#define DSPACE_ROUTE_MAX 512

static SpaceRoute g_routes[DSPACE_ROUTE_MAX];
static SpaceRouteId g_route_count = 0;

SpaceRouteId dspace_route_register(const SpaceRoute *def)
{
    SpaceRoute copy;
    if (!def) return 0;
    if (g_route_count >= (SpaceRouteId)DSPACE_ROUTE_MAX) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = g_route_count + 1;
    }
    g_routes[g_route_count] = copy;
    g_route_count++;
    return copy.id;
}

const SpaceRoute *dspace_route_get(SpaceRouteId id)
{
    if (id == 0) return 0;
    if (id > g_route_count) return 0;
    return &g_routes[id - 1];
}

SpaceRouteId dspace_route_find(SpaceSiteId a, SpaceSiteId b)
{
    SpaceRouteId i;
    for (i = 0; i < g_route_count; ++i) {
        if ((g_routes[i].a == a && g_routes[i].b == b) ||
            (g_routes[i].a == b && g_routes[i].b == a)) {
            return g_routes[i].id;
        }
    }
    return 0;
}

U32 dspace_route_neighbors(SpaceSiteId site, SpaceRouteId *out_ids, U32 max_out)
{
    U32 count = 0;
    SpaceRouteId i;
    if (!out_ids && max_out > 0) return 0;
    for (i = 0; i < g_route_count && count < max_out; ++i) {
        if (g_routes[i].a == site || g_routes[i].b == site) {
            out_ids[count++] = g_routes[i].id;
        }
    }
    return count;
}

SpaceRouteId dspace_route_pathfind_stub(SpaceSiteId start, SpaceSiteId goal)
{
    SpaceRouteId direct = dspace_route_find(start, goal);
    if (direct != 0) return direct;
    /* TODO: implement Dijkstra/A* */
    return 0;
}
