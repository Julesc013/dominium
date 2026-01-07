/*
FILE: source/dominium/game/runtime/dom_surface_topology.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Surface topology provider selection and queries.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_SURFACE_TOPOLOGY_H
#define DOM_SURFACE_TOPOLOGY_H

#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
#include "domino/core/types.h"
#include "runtime/dom_body_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TOPOLOGY_OK = 0,
    DOM_TOPOLOGY_ERR = -1,
    DOM_TOPOLOGY_INVALID_ARGUMENT = -2,
    DOM_TOPOLOGY_NOT_FOUND = -3,
    DOM_TOPOLOGY_NOT_IMPLEMENTED = -4,
    DOM_TOPOLOGY_INVALID_DATA = -5
};

enum {
    DOM_TOPOLOGY_KIND_SPHERE = 1u,
    DOM_TOPOLOGY_KIND_ELLIPSOID = 2u,
    DOM_TOPOLOGY_KIND_TORUS = 3u
};

enum {
    DOM_TOPOLOGY_SELECT_ALLOW_TORUS = 1u,
    DOM_TOPOLOGY_SELECT_FORCE_TORUS = 2u
};

typedef struct dom_topology_binding {
    u32 kind;
    dom_body_id body_id;
    q48_16 param_a_m;
    q48_16 param_b_m;
    q48_16 param_c_m;
    u32 flags;
} dom_topology_binding;

typedef struct dom_topo_latlong_q16 {
    q16_16 lat_turns;
    q16_16 lon_turns;
} dom_topo_latlong_q16;

typedef struct dom_topo_vec3_q16 {
    q16_16 v[3];
} dom_topo_vec3_q16;

int dom_surface_topology_select(const dom_body_registry *bodies,
                                dom_body_id body_id,
                                u32 select_flags,
                                dom_topology_binding *out_binding);

int dom_surface_topology_altitude(const dom_topology_binding *binding,
                                  const dom_posseg_q16 *pos_body_fixed,
                                  q48_16 *out_altitude_m);
int dom_surface_topology_latlong(const dom_topology_binding *binding,
                                 const dom_posseg_q16 *pos_body_fixed,
                                 dom_topo_latlong_q16 *out_latlong);
int dom_surface_topology_surface_normal(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        dom_topo_vec3_q16 *out_normal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SURFACE_TOPOLOGY_H */
