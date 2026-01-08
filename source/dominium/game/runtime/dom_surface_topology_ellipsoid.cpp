/*
FILE: source/dominium/game/runtime/dom_surface_topology_ellipsoid.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Ellipsoid topology provider stub (deterministic).
*/
#include "runtime/dom_surface_topology.h"

int dom_surface_topology_ellipsoid_altitude(const dom_topology_binding *binding,
                                            const dom_posseg_q16 *pos_body_fixed,
                                            q48_16 *out_altitude_m) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_altitude_m;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_ellipsoid_latlong(const dom_topology_binding *binding,
                                           const dom_posseg_q16 *pos_body_fixed,
                                           dom_topo_latlong_q16 *out_latlong) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_latlong;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_ellipsoid_pos_from_latlong(const dom_topology_binding *binding,
                                                    const dom_topo_latlong_q16 *latlong,
                                                    q48_16 altitude_m,
                                                    dom_posseg_q16 *out_pos) {
    (void)binding;
    (void)latlong;
    (void)altitude_m;
    (void)out_pos;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_ellipsoid_normal(const dom_topology_binding *binding,
                                          const dom_posseg_q16 *pos_body_fixed,
                                          dom_topo_vec3_q16 *out_normal) {
    (void)binding;
    (void)pos_body_fixed;
    (void)out_normal;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}

int dom_surface_topology_ellipsoid_tangent_frame(const dom_topology_binding *binding,
                                                 const dom_topo_latlong_q16 *latlong,
                                                 dom_topo_tangent_frame_q16 *out_frame) {
    (void)binding;
    (void)latlong;
    (void)out_frame;
    return DOM_TOPOLOGY_NOT_IMPLEMENTED;
}
