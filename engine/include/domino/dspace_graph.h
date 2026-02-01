/*
FILE: include/domino/dspace_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dspace_graph
RESPONSIBILITY: Defines the public contract for `dspace_graph` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DSPACE_GRAPH_H
#define DOMINO_DSPACE_GRAPH_H

#include "dnumeric.h"
#include "dorbit.h"
#include "dbody.h"

#ifdef __cplusplus
extern "C" {
#endif

/* SpaceRouteId: Identifier type for Space Route objects in `dspace_graph`. */
typedef uint32_t SpaceRouteId;

/* SpaceRoute: Public type used by `dspace_graph`. */
typedef struct {
    SpaceRouteId id;
    SpaceSiteId  a;
    SpaceSiteId  b;
    Q16_16       base_travel_time_s;
    EnergyJ      energy_cost;
    Q16_16       hazard_0_1;   /* radiation/other risk */
    uint32_t     flags;        /* reserved */
} SpaceRoute;

/* Purpose: Register route.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
SpaceRouteId  dspace_route_register(const SpaceRoute *def);
/* Purpose: Get route.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
const SpaceRoute *dspace_route_get(SpaceRouteId id);
/* Purpose: Find route.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Id value (0 is commonly used as the invalid/failure sentinel for `*Id` typedefs).
 */
SpaceRouteId  dspace_route_find(SpaceSiteId a, SpaceSiteId b);
/* Purpose: Neighbors dspace route.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
U32           dspace_route_neighbors(SpaceSiteId site, SpaceRouteId *out_ids, U32 max_out);

/* Stub for future pathfinding */
SpaceRouteId  dspace_route_pathfind_stub(SpaceSiteId start, SpaceSiteId goal);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DSPACE_GRAPH_H */
