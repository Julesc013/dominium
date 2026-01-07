/*
FILE: source/dominium/game/runtime/dom_surface_topology.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Surface topology provider selection and dispatch.
*/
#include "runtime/dom_surface_topology.h"

extern "C" {
#include "domino/core/spacetime.h"
}

int dom_surface_topology_sphere_altitude(const dom_topology_binding *binding,
                                         const dom_posseg_q16 *pos_body_fixed,
                                         q48_16 *out_altitude_m);
int dom_surface_topology_sphere_latlong(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        dom_topo_latlong_q16 *out_latlong);
int dom_surface_topology_sphere_normal(const dom_topology_binding *binding,
                                       const dom_posseg_q16 *pos_body_fixed,
                                       dom_topo_vec3_q16 *out_normal);

int dom_surface_topology_ellipsoid_altitude(const dom_topology_binding *binding,
                                            const dom_posseg_q16 *pos_body_fixed,
                                            q48_16 *out_altitude_m);
int dom_surface_topology_ellipsoid_latlong(const dom_topology_binding *binding,
                                           const dom_posseg_q16 *pos_body_fixed,
                                           dom_topo_latlong_q16 *out_latlong);
int dom_surface_topology_ellipsoid_normal(const dom_topology_binding *binding,
                                          const dom_posseg_q16 *pos_body_fixed,
                                          dom_topo_vec3_q16 *out_normal);

int dom_surface_topology_torus_altitude(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        q48_16 *out_altitude_m);
int dom_surface_topology_torus_latlong(const dom_topology_binding *binding,
                                       const dom_posseg_q16 *pos_body_fixed,
                                       dom_topo_latlong_q16 *out_latlong);
int dom_surface_topology_torus_normal(const dom_topology_binding *binding,
                                      const dom_posseg_q16 *pos_body_fixed,
                                      dom_topo_vec3_q16 *out_normal);

static dom_body_id earth_body_id(void) {
    dom_body_id id = 0ull;
    (void)dom_id_hash64("earth", 5u, &id);
    return id;
}

int dom_surface_topology_select(const dom_body_registry *bodies,
                                dom_body_id body_id,
                                u32 select_flags,
                                dom_topology_binding *out_binding) {
    dom_body_info info;
    dom_body_id earth_id;
    int rc;

    if (!bodies || !out_binding) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    rc = dom_body_registry_get(bodies, body_id, &info);
    if (rc != DOM_BODY_REGISTRY_OK) {
        return DOM_TOPOLOGY_NOT_FOUND;
    }

    earth_id = earth_body_id();
    out_binding->body_id = info.id;
    out_binding->flags = 0u;
    out_binding->param_a_m = info.radius_m;
    out_binding->param_b_m = 0;
    out_binding->param_c_m = 0;

    if ((select_flags & DOM_TOPOLOGY_SELECT_FORCE_TORUS) != 0u &&
        info.id != earth_id) {
        out_binding->kind = DOM_TOPOLOGY_KIND_TORUS;
        return DOM_TOPOLOGY_OK;
    }

    if ((select_flags & DOM_TOPOLOGY_SELECT_ALLOW_TORUS) != 0u &&
        info.id != earth_id) {
        out_binding->kind = DOM_TOPOLOGY_KIND_TORUS;
        return DOM_TOPOLOGY_OK;
    }

    out_binding->kind = DOM_TOPOLOGY_KIND_SPHERE;
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_altitude(const dom_topology_binding *binding,
                                  const dom_posseg_q16 *pos_body_fixed,
                                  q48_16 *out_altitude_m) {
    if (!binding || !pos_body_fixed || !out_altitude_m) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    switch (binding->kind) {
        case DOM_TOPOLOGY_KIND_SPHERE:
            return dom_surface_topology_sphere_altitude(binding, pos_body_fixed, out_altitude_m);
        case DOM_TOPOLOGY_KIND_ELLIPSOID:
            return dom_surface_topology_ellipsoid_altitude(binding, pos_body_fixed, out_altitude_m);
        case DOM_TOPOLOGY_KIND_TORUS:
            return dom_surface_topology_torus_altitude(binding, pos_body_fixed, out_altitude_m);
        default:
            break;
    }
    return DOM_TOPOLOGY_INVALID_DATA;
}

int dom_surface_topology_latlong(const dom_topology_binding *binding,
                                 const dom_posseg_q16 *pos_body_fixed,
                                 dom_topo_latlong_q16 *out_latlong) {
    if (!binding || !pos_body_fixed || !out_latlong) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    switch (binding->kind) {
        case DOM_TOPOLOGY_KIND_SPHERE:
            return dom_surface_topology_sphere_latlong(binding, pos_body_fixed, out_latlong);
        case DOM_TOPOLOGY_KIND_ELLIPSOID:
            return dom_surface_topology_ellipsoid_latlong(binding, pos_body_fixed, out_latlong);
        case DOM_TOPOLOGY_KIND_TORUS:
            return dom_surface_topology_torus_latlong(binding, pos_body_fixed, out_latlong);
        default:
            break;
    }
    return DOM_TOPOLOGY_INVALID_DATA;
}

int dom_surface_topology_surface_normal(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        dom_topo_vec3_q16 *out_normal) {
    if (!binding || !pos_body_fixed || !out_normal) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    switch (binding->kind) {
        case DOM_TOPOLOGY_KIND_SPHERE:
            return dom_surface_topology_sphere_normal(binding, pos_body_fixed, out_normal);
        case DOM_TOPOLOGY_KIND_ELLIPSOID:
            return dom_surface_topology_ellipsoid_normal(binding, pos_body_fixed, out_normal);
        case DOM_TOPOLOGY_KIND_TORUS:
            return dom_surface_topology_torus_normal(binding, pos_body_fixed, out_normal);
        default:
            break;
    }
    return DOM_TOPOLOGY_INVALID_DATA;
}
