/*
FILE: source/dominium/game/runtime/dom_surface_topology_sphere.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Sphere topology provider (deterministic fixed-point).
*/
#include "runtime/dom_surface_topology.h"

#include "domino/core/dom_deterministic_math.h"

namespace {

static int ensure_flat_pos(const dom_posseg_q16 *pos) {
    if (!pos) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (pos->seg[0] != 0 || pos->seg[1] != 0 || pos->seg[2] != 0) {
        return DOM_TOPOLOGY_NOT_IMPLEMENTED;
    }
    return DOM_TOPOLOGY_OK;
}

static u64 vec_length_q16(const dom_posseg_q16 *pos) {
    i64 x = (i64)pos->loc[0];
    i64 y = (i64)pos->loc[1];
    i64 z = (i64)pos->loc[2];
    u64 x2 = (u64)(x * x);
    u64 y2 = (u64)(y * y);
    u64 z2 = (u64)(z * z);
    return dom_sqrt_u64(x2 + y2 + z2);
}

static u64 vec_length_xy_q16(const dom_posseg_q16 *pos) {
    i64 x = (i64)pos->loc[0];
    i64 y = (i64)pos->loc[1];
    u64 x2 = (u64)(x * x);
    u64 y2 = (u64)(y * y);
    return dom_sqrt_u64(x2 + y2);
}

static q16_16 approx_atan_turns_q16(u32 ratio_q16) {
    u64 scaled = (u64)ratio_q16 * 0x2000ull;
    return (q16_16)(scaled >> 16);
}

static q16_16 atan2_turns_unsigned(u32 y, u32 x) {
    u32 ratio;
    q16_16 base;
    if (x == 0u && y == 0u) {
        return 0;
    }
    if (x >= y) {
        ratio = (x == 0u) ? 0u : (u32)(((u64)y << 16) / x);
        return approx_atan_turns_q16(ratio);
    }
    ratio = (y == 0u) ? 0u : (u32)(((u64)x << 16) / y);
    base = approx_atan_turns_q16(ratio);
    return (q16_16)(0x4000 - base);
}

static q16_16 atan2_turns_q16(i32 y, i32 x) {
    u32 ay = (y < 0) ? (u32)(-y) : (u32)y;
    u32 ax = (x < 0) ? (u32)(-x) : (u32)x;
    q16_16 angle = atan2_turns_unsigned(ay, ax);

    if (x >= 0 && y >= 0) {
        return dom_angle_normalize_q16(angle);
    }
    if (x < 0 && y >= 0) {
        return dom_angle_normalize_q16((q16_16)(0x8000 - angle));
    }
    if (x < 0 && y < 0) {
        return dom_angle_normalize_q16((q16_16)(0x8000 + angle));
    }
    return dom_angle_normalize_q16((q16_16)(-angle));
}

static q16_16 atan2_turns_signed_q16(i32 y, i32 x) {
    u32 ay = (y < 0) ? (u32)(-y) : (u32)y;
    u32 ax = (x < 0) ? (u32)(-x) : (u32)x;
    q16_16 angle = atan2_turns_unsigned(ay, ax);
    if (y < 0) {
        return (q16_16)(-angle);
    }
    return angle;
}

} // namespace

int dom_surface_topology_sphere_altitude(const dom_topology_binding *binding,
                                         const dom_posseg_q16 *pos_body_fixed,
                                         q48_16 *out_altitude_m) {
    u64 len_q16;
    q48_16 len_q48;
    int rc;
    if (!binding || !pos_body_fixed || !out_altitude_m) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    rc = ensure_flat_pos(pos_body_fixed);
    if (rc != DOM_TOPOLOGY_OK) {
        return rc;
    }
    len_q16 = vec_length_q16(pos_body_fixed);
    len_q48 = d_q48_16_from_q16_16((q16_16)len_q16);
    *out_altitude_m = d_q48_16_sub(len_q48, binding->param_a_m);
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_latlong(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        dom_topo_latlong_q16 *out_latlong) {
    u64 len_xy_q16;
    q16_16 lon_turns;
    q16_16 lat_turns;
    int rc;
    if (!binding || !pos_body_fixed || !out_latlong) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    rc = ensure_flat_pos(pos_body_fixed);
    if (rc != DOM_TOPOLOGY_OK) {
        return rc;
    }
    lon_turns = atan2_turns_q16(pos_body_fixed->loc[1], pos_body_fixed->loc[0]);
    len_xy_q16 = vec_length_xy_q16(pos_body_fixed);
    lat_turns = atan2_turns_signed_q16(pos_body_fixed->loc[2], (i32)len_xy_q16);
    out_latlong->lat_turns = lat_turns;
    out_latlong->lon_turns = lon_turns;
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_normal(const dom_topology_binding *binding,
                                       const dom_posseg_q16 *pos_body_fixed,
                                       dom_topo_vec3_q16 *out_normal) {
    u64 len_q16;
    q16_16 len_q16_fixed;
    int rc;
    if (!binding || !pos_body_fixed || !out_normal) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    rc = ensure_flat_pos(pos_body_fixed);
    if (rc != DOM_TOPOLOGY_OK) {
        return rc;
    }
    len_q16 = vec_length_q16(pos_body_fixed);
    len_q16_fixed = (q16_16)len_q16;
    if (len_q16_fixed == 0) {
        out_normal->v[0] = 0;
        out_normal->v[1] = 0;
        out_normal->v[2] = d_q16_16_from_int(1);
        return DOM_TOPOLOGY_OK;
    }
    out_normal->v[0] = d_q16_16_div(pos_body_fixed->loc[0], len_q16_fixed);
    out_normal->v[1] = d_q16_16_div(pos_body_fixed->loc[1], len_q16_fixed);
    out_normal->v[2] = d_q16_16_div(pos_body_fixed->loc[2], len_q16_fixed);
    return DOM_TOPOLOGY_OK;
}
