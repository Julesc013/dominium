#ifndef DOMINO_DSPACE_GRAPH_H
#define DOMINO_DSPACE_GRAPH_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dbody.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t SpaceRouteId;

typedef struct {
    SpaceRouteId id;
    SpaceSiteId  a;
    SpaceSiteId  b;
    Q16_16       base_travel_time_s;
    EnergyJ      energy_cost;
    Q16_16       hazard_0_1;   /* radiation/other risk */
    uint32_t     flags;        /* reserved */
} SpaceRoute;

SpaceRouteId  dspace_route_register(const SpaceRoute *def);
const SpaceRoute *dspace_route_get(SpaceRouteId id);
SpaceRouteId  dspace_route_find(SpaceSiteId a, SpaceSiteId b);
U32           dspace_route_neighbors(SpaceSiteId site, SpaceRouteId *out_ids, U32 max_out);

/* Stub for future pathfinding */
SpaceRouteId  dspace_route_pathfind_stub(SpaceSiteId start, SpaceSiteId goal);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DSPACE_GRAPH_H */
