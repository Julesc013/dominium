/*
FILE: source/dominium/game/runtime/dom_surface_topology_torus.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Torus topology provider stub (deterministic).
*/
#include "runtime/dom_surface_topology.h"

int dom_surface_topology_torus_altitude(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        q48_16 *out_altitude_m) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_altitude_m;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_torus_latlong(const dom_topology_binding *binding,
                                       const dom_posseg_q16 *pos_body_fixed,
                                       dom_topo_latlong_q16 *out_latlong) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_latlong;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_torus_normal(const dom_topology_binding *binding,
                                      const dom_posseg_q16 *pos_body_fixed,
                                      dom_topo_vec3_q16 *out_normal) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_normal;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}
