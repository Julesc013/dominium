/*
FILE: include/domino/dspace_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dspace_graph
RESPONSIBILITY: Defines the public contract for `dspace_graph` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
