/*
FILE: source/dominium/game/runtime/dom_surface_topology_sphere.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/surface_topology
RESPONSIBILITY: Sphere topology provider (deterministic fixed-point).
*/
#include "runtime/dom_surface_topology.h"

#include "domino/core/dom_deterministic_math.h"

namespace {

static q48_16 seg_size_q48(void) {
    return d_q48_16_from_int(DOM_TOPOLOGY_POSSEG_SIZE_M);
}

static q48_16 axis_to_q48(i32 seg, q16_16 loc) {
    q48_16 seg_m = d_q48_16_from_int((i64)seg * DOM_TOPOLOGY_POSSEG_SIZE_M);
    q48_16 loc_m = d_q48_16_from_q16_16(loc);
    return d_q48_16_add(seg_m, loc_m);
}

static void posseg_to_q48(const dom_posseg_q16 *pos, q48_16 out[3]) {
    out[0] = axis_to_q48(pos->seg[0], pos->loc[0]);
    out[1] = axis_to_q48(pos->seg[1], pos->loc[1]);
    out[2] = axis_to_q48(pos->seg[2], pos->loc[2]);
}

static void q48_to_posseg(q48_16 v, i32 *out_seg, q16_16 *out_loc) {
    const q48_16 seg_size = seg_size_q48();
    i64 seg = 0;
    q48_16 rem;
    if (!out_seg || !out_loc) {
        return;
    }
    if (seg_size != 0) {
        seg = (i64)(v / seg_size);
    }
    rem = d_q48_16_sub(v, d_q48_16_mul(d_q48_16_from_int(seg), seg_size));
    if (rem < 0) {
        seg -= 1;
        rem = d_q48_16_add(rem, seg_size);
    }
    *out_seg = (i32)seg;
    *out_loc = d_q16_16_from_q48_16(rem);
}

static q16_16 clamp_lat_turns(q16_16 lat_turns) {
    const q16_16 max_lat = (q16_16)0x4000;
    if (lat_turns > max_lat) {
        return max_lat;
    }
    if (lat_turns < (q16_16)(-max_lat)) {
        return (q16_16)(-max_lat);
    }
    return lat_turns;
}

static q16_16 normalize_axis(q48_16 coord, q48_16 radius) {
    q48_16 ratio;
    if (radius == 0) {
        return 0;
    }
    ratio = d_q48_16_div(coord, radius);
    return d_q16_16_from_q48_16(ratio);
}

static u64 vec_length_q16_components(q16_16 x, q16_16 y, q16_16 z) {
    i64 xi = (i64)x;
    i64 yi = (i64)y;
    i64 zi = (i64)z;
    u64 x2 = (u64)(xi * xi);
    u64 y2 = (u64)(yi * yi);
    u64 z2 = (u64)(zi * zi);
    return dom_sqrt_u64(x2 + y2 + z2);
}

static u64 vec_length_xy_q16_components(q16_16 x, q16_16 y) {
    i64 xi = (i64)x;
    i64 yi = (i64)y;
    u64 x2 = (u64)(xi * xi);
    u64 y2 = (u64)(yi * yi);
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
    q48_16 coords[3];
    q48_16 radius;
    q16_16 nx;
    q16_16 ny;
    q16_16 nz;
    u64 len_norm_q16;
    q48_16 len_m;
    if (!binding || !pos_body_fixed || !out_altitude_m) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    radius = binding->param_a_m;
    if (radius <= 0) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    posseg_to_q48(pos_body_fixed, coords);
    nx = normalize_axis(coords[0], radius);
    ny = normalize_axis(coords[1], radius);
    nz = normalize_axis(coords[2], radius);
    len_norm_q16 = vec_length_q16_components(nx, ny, nz);
    len_m = d_q48_16_mul(radius, d_q48_16_from_q16_16((q16_16)len_norm_q16));
    *out_altitude_m = d_q48_16_sub(len_m, radius);
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_latlong(const dom_topology_binding *binding,
                                        const dom_posseg_q16 *pos_body_fixed,
                                        dom_topo_latlong_q16 *out_latlong) {
    q48_16 coords[3];
    q48_16 radius;
    q16_16 nx;
    q16_16 ny;
    q16_16 nz;
    u64 len_xy_q16;
    q16_16 lon_turns;
    q16_16 lat_turns;
    if (!binding || !pos_body_fixed || !out_latlong) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    radius = binding->param_a_m;
    if (radius <= 0) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    posseg_to_q48(pos_body_fixed, coords);
    nx = normalize_axis(coords[0], radius);
    ny = normalize_axis(coords[1], radius);
    nz = normalize_axis(coords[2], radius);
    lon_turns = atan2_turns_q16(ny, nx);
    len_xy_q16 = vec_length_xy_q16_components(nx, ny);
    lat_turns = atan2_turns_signed_q16(nz, (i32)len_xy_q16);
    out_latlong->lat_turns = lat_turns;
    out_latlong->lon_turns = lon_turns;
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_normal(const dom_topology_binding *binding,
                                       const dom_posseg_q16 *pos_body_fixed,
                                       dom_topo_vec3_q16 *out_normal) {
    q48_16 coords[3];
    q48_16 radius;
    q16_16 nx;
    q16_16 ny;
    q16_16 nz;
    u64 len_norm_q16;
    q16_16 len_norm_fixed;
    if (!binding || !pos_body_fixed || !out_normal) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    radius = binding->param_a_m;
    if (radius <= 0) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }
    posseg_to_q48(pos_body_fixed, coords);
    nx = normalize_axis(coords[0], radius);
    ny = normalize_axis(coords[1], radius);
    nz = normalize_axis(coords[2], radius);
    len_norm_q16 = vec_length_q16_components(nx, ny, nz);
    len_norm_fixed = (q16_16)len_norm_q16;
    if (len_norm_fixed == 0) {
        out_normal->v[0] = 0;
        out_normal->v[1] = 0;
        out_normal->v[2] = d_q16_16_from_int(1);
        return DOM_TOPOLOGY_OK;
    }
    out_normal->v[0] = d_q16_16_div(nx, len_norm_fixed);
    out_normal->v[1] = d_q16_16_div(ny, len_norm_fixed);
    out_normal->v[2] = d_q16_16_div(nz, len_norm_fixed);
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_pos_from_latlong(const dom_topology_binding *binding,
                                                 const dom_topo_latlong_q16 *latlong,
                                                 q48_16 altitude_m,
                                                 dom_posseg_q16 *out_pos) {
    q16_16 lat_turns;
    q16_16 lon_turns;
    q16_16 sin_lat;
    q16_16 cos_lat;
    q16_16 sin_lon;
    q16_16 cos_lon;
    q16_16 x_unit;
    q16_16 y_unit;
    q16_16 z_unit;
    q48_16 radius;
    q48_16 r;
    q48_16 x;
    q48_16 y;
    q48_16 z;

    if (!binding || !latlong || !out_pos) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }

    radius = binding->param_a_m;
    if (radius <= 0) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }

    lat_turns = clamp_lat_turns(latlong->lat_turns);
    lon_turns = dom_angle_normalize_q16(latlong->lon_turns);

    sin_lat = dom_sin_q16(lat_turns);
    cos_lat = dom_cos_q16(lat_turns);
    sin_lon = dom_sin_q16(lon_turns);
    cos_lon = dom_cos_q16(lon_turns);

    x_unit = d_q16_16_mul(cos_lat, cos_lon);
    y_unit = d_q16_16_mul(cos_lat, sin_lon);
    z_unit = sin_lat;

    r = d_q48_16_add(radius, altitude_m);
    if (r <= 0) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }

    x = d_q48_16_mul(r, d_q48_16_from_q16_16(x_unit));
    y = d_q48_16_mul(r, d_q48_16_from_q16_16(y_unit));
    z = d_q48_16_mul(r, d_q48_16_from_q16_16(z_unit));

    q48_to_posseg(x, &out_pos->seg[0], &out_pos->loc[0]);
    q48_to_posseg(y, &out_pos->seg[1], &out_pos->loc[1]);
    q48_to_posseg(z, &out_pos->seg[2], &out_pos->loc[2]);
    return DOM_TOPOLOGY_OK;
}

int dom_surface_topology_sphere_tangent_frame(const dom_topology_binding *binding,
                                              const dom_topo_latlong_q16 *latlong,
                                              dom_topo_tangent_frame_q16 *out_frame) {
    q16_16 lat_turns;
    q16_16 lon_turns;
    q16_16 sin_lat;
    q16_16 cos_lat;
    q16_16 sin_lon;
    q16_16 cos_lon;

    if (!binding || !latlong || !out_frame) {
        return DOM_TOPOLOGY_INVALID_ARGUMENT;
    }
    if (binding->kind != DOM_TOPOLOGY_KIND_SPHERE) {
        return DOM_TOPOLOGY_INVALID_DATA;
    }

    lat_turns = clamp_lat_turns(latlong->lat_turns);
    lon_turns = dom_angle_normalize_q16(latlong->lon_turns);

    sin_lat = dom_sin_q16(lat_turns);
    cos_lat = dom_cos_q16(lat_turns);
    sin_lon = dom_sin_q16(lon_turns);
    cos_lon = dom_cos_q16(lon_turns);

    out_frame->up.v[0] = d_q16_16_mul(cos_lat, cos_lon);
    out_frame->up.v[1] = d_q16_16_mul(cos_lat, sin_lon);
    out_frame->up.v[2] = sin_lat;

    out_frame->east.v[0] = (q16_16)(-sin_lon);
    out_frame->east.v[1] = cos_lon;
    out_frame->east.v[2] = 0;

    out_frame->north.v[0] = d_q16_16_mul((q16_16)(-sin_lat), cos_lon);
    out_frame->north.v[1] = d_q16_16_mul((q16_16)(-sin_lat), sin_lon);
    out_frame->north.v[2] = cos_lat;
    return DOM_TOPOLOGY_OK;
}
