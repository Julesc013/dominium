/*
FILE: source/domino/trans/model/dg_trans_alignment.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_alignment
RESPONSIBILITY: Implements `dg_trans_alignment`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS corridor alignment authoring model (C89). */
#include "trans/model/dg_trans_alignment.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "domino/core/fixed.h"
#include "trans/compile/dg_trans_frame.h"

#define DG_TRANS_Q_ONE ((dg_q)((i64)1 << 16))

static u64 dg_trans_abs_i64_u64(i64 v) {
    if (v < 0) {
        if (v == (i64)0x8000000000000000LL) {
            return ((u64)1) << 63;
        }
        return (u64)(-v);
    }
    return (u64)v;
}

static u64 dg_trans_isqrt_u64(u64 v) {
    u64 res = 0u;
    u64 bit = (u64)1u << 62;
    while (bit > v) {
        bit >>= 2;
    }
    while (bit != 0u) {
        if (v >= res + bit) {
            v -= res + bit;
            res = (res >> 1) + bit;
        } else {
            res >>= 1;
        }
        bit >>= 2;
    }
    return res;
}

static dg_q dg_trans_vec3_dist_q(dg_vec3_q a, dg_vec3_q b) {
    i64 dx = (i64)b.x - (i64)a.x;
    i64 dy = (i64)b.y - (i64)a.y;
    i64 dz = (i64)b.z - (i64)a.z;
    u64 adx = dg_trans_abs_i64_u64(dx);
    u64 ady = dg_trans_abs_i64_u64(dy);
    u64 adz = dg_trans_abs_i64_u64(dz);
    u64 max_abs = adx;
    u32 shift = 0u;
    u64 sdx, sdy, sdz;
    u64 sum_sq;
    u64 len_scaled;
    u64 len_raw;

    if (ady > max_abs) max_abs = ady;
    if (adz > max_abs) max_abs = adz;
    if (max_abs == 0u) return 0;

    /* Scale down to keep squares in 64-bit (<= ~2^62). */
    while (max_abs > 0x3FFFFFFFULL) {
        max_abs >>= 1;
        shift += 1u;
    }

    sdx = adx >> shift;
    sdy = ady >> shift;
    sdz = adz >> shift;

    sum_sq = sdx * sdx + sdy * sdy + sdz * sdz;
    len_scaled = dg_trans_isqrt_u64(sum_sq);
    if (shift >= 63u) {
        len_raw = ((u64)1u) << 63;
    } else {
        len_raw = len_scaled << shift;
    }

    if (len_raw > (u64)0x7FFFFFFFFFFFFFFFULL) {
        return (dg_q)0x7FFFFFFFFFFFFFFFLL;
    }
    return (dg_q)(i64)len_raw;
}

static u32 dg_trans_alignment_point_lower_bound(const dg_trans_alignment *a, u32 point_index) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!a) return 0u;
    hi = a->point_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (a->points[mid].point_index >= point_index) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 dg_trans_profile_lower_bound(const dg_trans_profile_knot *k, u32 count, dg_q s) {
    u32 lo = 0u;
    u32 hi = count;
    u32 mid;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if ((i64)k[mid].s >= (i64)s) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static dg_q dg_trans_profile_eval(const dg_trans_profile_knot *k, u32 count, dg_q s) {
    u32 idx;
    const dg_trans_profile_knot *k0;
    const dg_trans_profile_knot *k1;
    dg_q ds;
    dg_q dv;
    dg_q t;
    dg_q lerp;

    if (!k || count == 0u) return 0;
    if ((i64)s <= (i64)k[0].s) return k[0].v;
    if ((i64)s >= (i64)k[count - 1u].s) return k[count - 1u].v;

    idx = dg_trans_profile_lower_bound(k, count, s);
    if (idx == 0u) return k[0].v;
    if (idx >= count) return k[count - 1u].v;

    k0 = &k[idx - 1u];
    k1 = &k[idx];
    ds = (dg_q)((q48_16)k1->s - (q48_16)k0->s);
    dv = (dg_q)((q48_16)k1->v - (q48_16)k0->v);
    if (ds == 0) return k1->v;

    t = (dg_q)d_q48_16_div((q48_16)((q48_16)s - (q48_16)k0->s), (q48_16)ds);
    lerp = (dg_q)d_q48_16_add((q48_16)k0->v, d_q48_16_mul((q48_16)dv, (q48_16)t));
    return lerp;
}

static dg_q dg_trans_profile_slope(const dg_trans_profile_knot *k, u32 count, dg_q s) {
    u32 idx;
    const dg_trans_profile_knot *k0;
    const dg_trans_profile_knot *k1;
    dg_q ds;
    dg_q dv;
    if (!k || count < 2u) return 0;
    if ((i64)s <= (i64)k[0].s) s = k[0].s;
    if ((i64)s >= (i64)k[count - 1u].s) s = k[count - 1u].s;

    idx = dg_trans_profile_lower_bound(k, count, s);
    if (idx == 0u) idx = 1u;
    if (idx >= count) idx = count - 1u;

    k0 = &k[idx - 1u];
    k1 = &k[idx];
    ds = (dg_q)((q48_16)k1->s - (q48_16)k0->s);
    dv = (dg_q)((q48_16)k1->v - (q48_16)k0->v);
    if (ds == 0) return 0;
    return (dg_q)d_q48_16_div((q48_16)dv, (q48_16)ds);
}

static dg_vec3_q dg_trans_vec3_normalize_unit(dg_vec3_q v) {
    i64 x = (i64)v.x;
    i64 y = (i64)v.y;
    i64 z = (i64)v.z;
    u64 ax = dg_trans_abs_i64_u64(x);
    u64 ay = dg_trans_abs_i64_u64(y);
    u64 az = dg_trans_abs_i64_u64(z);
    u64 max_abs = ax;
    u32 shift = 0u;
    i64 sx, sy, sz;
    u64 sum_sq;
    u64 len;
    dg_vec3_q out;

    if (ay > max_abs) max_abs = ay;
    if (az > max_abs) max_abs = az;
    if (max_abs == 0u) {
        out.x = 0;
        out.y = 0;
        out.z = 0;
        return out;
    }

    while (max_abs > 0x3FFFFFFFULL) {
        max_abs >>= 1;
        shift += 1u;
    }

    /* Use truncating division for deterministic sign handling. */
    if (shift == 0u) {
        sx = x;
        sy = y;
        sz = z;
    } else {
        i64 denom = (i64)1 << shift;
        sx = x / denom;
        sy = y / denom;
        sz = z / denom;
    }

    sum_sq = (u64)(sx < 0 ? -sx : sx) * (u64)(sx < 0 ? -sx : sx)
           + (u64)(sy < 0 ? -sy : sy) * (u64)(sy < 0 ? -sy : sy)
           + (u64)(sz < 0 ? -sz : sz) * (u64)(sz < 0 ? -sz : sz);
    len = dg_trans_isqrt_u64(sum_sq);
    if (len == 0u) {
        out.x = 0;
        out.y = 0;
        out.z = 0;
        return out;
    }

    out.x = (dg_q)(((i64)sx << 16) / (i64)len);
    out.y = (dg_q)(((i64)sy << 16) / (i64)len);
    out.z = (dg_q)(((i64)sz << 16) / (i64)len);
    return out;
}

void dg_trans_alignment_init(dg_trans_alignment *a) {
    if (!a) return;
    memset(a, 0, sizeof(*a));
}

void dg_trans_alignment_free(dg_trans_alignment *a) {
    if (!a) return;
    if (a->points) free(a->points);
    if (a->z_profile) free(a->z_profile);
    if (a->roll_profile) free(a->roll_profile);
    dg_trans_alignment_init(a);
}

int dg_trans_alignment_reserve_points(dg_trans_alignment *a, u32 capacity) {
    dg_trans_alignment_point *p;
    u32 new_cap;
    if (!a) return -1;
    if (capacity <= a->point_capacity) return 0;
    new_cap = a->point_capacity ? a->point_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    p = (dg_trans_alignment_point *)realloc(a->points, sizeof(dg_trans_alignment_point) * (size_t)new_cap);
    if (!p) return -2;
    if (new_cap > a->point_capacity) {
        memset(&p[a->point_capacity], 0, sizeof(dg_trans_alignment_point) * (size_t)(new_cap - a->point_capacity));
    }
    a->points = p;
    a->point_capacity = new_cap;
    return 0;
}

int dg_trans_alignment_set_point(dg_trans_alignment *a, u32 point_index, dg_vec3_q pos) {
    u32 idx;
    if (!a) return -1;
    if (point_index == 0u) return -2;

    idx = dg_trans_alignment_point_lower_bound(a, point_index);
    if (idx < a->point_count && a->points[idx].point_index == point_index) {
        a->points[idx].pos = pos;
        return 1;
    }

    if (dg_trans_alignment_reserve_points(a, a->point_count + 1u) != 0) return -3;
    if (idx < a->point_count) {
        memmove(&a->points[idx + 1u], &a->points[idx], sizeof(dg_trans_alignment_point) * (size_t)(a->point_count - idx));
    }
    a->points[idx].point_index = point_index;
    a->points[idx].pos = pos;
    a->point_count += 1u;
    return 0;
}

static int dg_trans_alignment_reserve_profile(dg_trans_profile_knot **k, u32 *cap, u32 capacity) {
    dg_trans_profile_knot *p;
    u32 new_cap;
    if (!k || !cap) return -1;
    if (capacity <= *cap) return 0;
    new_cap = (*cap) ? (*cap) : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    p = (dg_trans_profile_knot *)realloc(*k, sizeof(dg_trans_profile_knot) * (size_t)new_cap);
    if (!p) return -2;
    if (new_cap > *cap) {
        memset(&p[*cap], 0, sizeof(dg_trans_profile_knot) * (size_t)(new_cap - *cap));
    }
    *k = p;
    *cap = new_cap;
    return 0;
}

static int dg_trans_alignment_set_profile_knot(
    dg_trans_profile_knot **k,
    u32 *count,
    u32 *cap,
    dg_q s,
    dg_q v
) {
    u32 idx;
    if (!k || !count || !cap) return -1;
    if (dg_trans_alignment_reserve_profile(k, cap, *count + 1u) != 0) return -2;
    idx = dg_trans_profile_lower_bound(*k, *count, s);
    if (idx < *count && (i64)(*k)[idx].s == (i64)s) {
        (*k)[idx].v = v;
        return 1;
    }
    if (idx < *count) {
        memmove(&(*k)[idx + 1u], &(*k)[idx], sizeof(dg_trans_profile_knot) * (size_t)(*count - idx));
    }
    (*k)[idx].s = s;
    (*k)[idx].v = v;
    *count += 1u;
    return 0;
}

int dg_trans_alignment_reserve_z_profile(dg_trans_alignment *a, u32 capacity) {
    if (!a) return -1;
    return dg_trans_alignment_reserve_profile(&a->z_profile, &a->z_capacity, capacity);
}

int dg_trans_alignment_set_z_knot(dg_trans_alignment *a, dg_q s, dg_q z_offset) {
    if (!a) return -1;
    return dg_trans_alignment_set_profile_knot(&a->z_profile, &a->z_count, &a->z_capacity, s, z_offset);
}

int dg_trans_alignment_reserve_roll_profile(dg_trans_alignment *a, u32 capacity) {
    if (!a) return -1;
    return dg_trans_alignment_reserve_profile(&a->roll_profile, &a->roll_capacity, capacity);
}

int dg_trans_alignment_set_roll_knot(dg_trans_alignment *a, dg_q s, dg_q roll_turns) {
    if (!a) return -1;
    return dg_trans_alignment_set_profile_knot(&a->roll_profile, &a->roll_count, &a->roll_capacity, s, roll_turns);
}

int dg_trans_alignment_length_q(const dg_trans_alignment *a, dg_q *out_len) {
    dg_q len = 0;
    u32 i;
    if (!out_len) return -1;
    *out_len = 0;
    if (!a) return -2;
    if (a->point_count < 2u) return -3;

    for (i = 0u; i + 1u < a->point_count; ++i) {
        dg_q seg = dg_trans_vec3_dist_q(a->points[i].pos, a->points[i + 1u].pos);
        len = (dg_q)d_q48_16_add((q48_16)len, (q48_16)seg);
    }
    *out_len = len;
    return 0;
}

static int dg_trans_alignment_locate_segment(
    const dg_trans_alignment *a,
    dg_q s,
    u32 *out_seg_index,
    dg_q *out_seg_s0,
    dg_q *out_seg_len
) {
    dg_q accum = 0;
    u32 i;
    if (!a || a->point_count < 2u) return -1;
    if (!out_seg_index || !out_seg_s0 || !out_seg_len) return -2;

    for (i = 0u; i + 1u < a->point_count; ++i) {
        dg_q seg_len = dg_trans_vec3_dist_q(a->points[i].pos, a->points[i + 1u].pos);
        if (seg_len <= 0) {
            continue;
        }
        if ((i64)s <= (i64)d_q48_16_add((q48_16)accum, (q48_16)seg_len)) {
            *out_seg_index = i;
            *out_seg_s0 = accum;
            *out_seg_len = seg_len;
            return 0;
        }
        accum = (dg_q)d_q48_16_add((q48_16)accum, (q48_16)seg_len);
    }

    *out_seg_index = a->point_count - 2u;
    *out_seg_s0 = accum;
    *out_seg_len = 0;
    return 1;
}

int dg_trans_alignment_eval_pos(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_pos) {
    dg_q len;
    u32 seg_idx;
    dg_q seg_s0;
    dg_q seg_len;
    dg_q u;
    dg_vec3_q p0;
    dg_vec3_q p1;
    dg_vec3_q out;
    dg_q zoff;

    if (!out_pos) return -1;
    out_pos->x = 0;
    out_pos->y = 0;
    out_pos->z = 0;
    if (!a) return -2;
    if (a->point_count < 2u) return -3;
    if (dg_trans_alignment_length_q(a, &len) != 0) return -4;

    if ((i64)s <= 0) s = 0;
    if ((i64)s >= (i64)len) s = len;

    if (dg_trans_alignment_locate_segment(a, s, &seg_idx, &seg_s0, &seg_len) != 0) {
        *out_pos = a->points[a->point_count - 1u].pos;
        return 0;
    }

    p0 = a->points[seg_idx].pos;
    p1 = a->points[seg_idx + 1u].pos;

    if (seg_len <= 0) {
        out = p0;
    } else {
        u = (dg_q)d_q48_16_div((q48_16)((q48_16)s - (q48_16)seg_s0), (q48_16)seg_len);

        out.x = (dg_q)d_q48_16_add((q48_16)p0.x, d_q48_16_mul((q48_16)((q48_16)p1.x - (q48_16)p0.x), (q48_16)u));
        out.y = (dg_q)d_q48_16_add((q48_16)p0.y, d_q48_16_mul((q48_16)((q48_16)p1.y - (q48_16)p0.y), (q48_16)u));
        out.z = (dg_q)d_q48_16_add((q48_16)p0.z, d_q48_16_mul((q48_16)((q48_16)p1.z - (q48_16)p0.z), (q48_16)u));
    }

    zoff = dg_trans_profile_eval(a->z_profile, a->z_count, s);
    out.z = (dg_q)d_q48_16_add((q48_16)out.z, (q48_16)zoff);

    *out_pos = out;
    return 0;
}

int dg_trans_alignment_eval_roll(const dg_trans_alignment *a, dg_q s, dg_q *out_roll_turns) {
    if (!out_roll_turns) return -1;
    *out_roll_turns = 0;
    if (!a) return -2;
    *out_roll_turns = dg_trans_profile_eval(a->roll_profile, a->roll_count, s);
    return 0;
}

int dg_trans_alignment_eval_tangent(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_tangent_unit) {
    dg_q len;
    u32 seg_idx;
    dg_q seg_s0;
    dg_q seg_len;
    dg_vec3_q p0;
    dg_vec3_q p1;
    dg_vec3_q d;
    dg_q z_slope;
    dg_vec3_q out;

    if (!out_tangent_unit) return -1;
    out_tangent_unit->x = DG_TRANS_Q_ONE;
    out_tangent_unit->y = 0;
    out_tangent_unit->z = 0;
    if (!a) return -2;
    if (a->point_count < 2u) return -3;
    if (dg_trans_alignment_length_q(a, &len) != 0) return -4;

    if ((i64)s <= 0) s = 0;
    if ((i64)s >= (i64)len) s = len;

    if (dg_trans_alignment_locate_segment(a, s, &seg_idx, &seg_s0, &seg_len) != 0 || seg_len <= 0) {
        return -5;
    }

    p0 = a->points[seg_idx].pos;
    p1 = a->points[seg_idx + 1u].pos;
    d.x = (dg_q)d_q48_16_div((q48_16)((q48_16)p1.x - (q48_16)p0.x), (q48_16)seg_len);
    d.y = (dg_q)d_q48_16_div((q48_16)((q48_16)p1.y - (q48_16)p0.y), (q48_16)seg_len);
    d.z = (dg_q)d_q48_16_div((q48_16)((q48_16)p1.z - (q48_16)p0.z), (q48_16)seg_len);

    z_slope = dg_trans_profile_slope(a->z_profile, a->z_count, s);
    d.z = (dg_q)d_q48_16_add((q48_16)d.z, (q48_16)z_slope);

    out = dg_trans_vec3_normalize_unit(d);
    *out_tangent_unit = out;
    return 0;
}

int dg_trans_alignment_eval_up(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_up_unit) {
    dg_vec3_q tan;
    dg_q roll;
    dg_trans_frame f;
    dg_vec3_q origin;

    if (!out_up_unit) return -1;
    out_up_unit->x = 0;
    out_up_unit->y = 0;
    out_up_unit->z = DG_TRANS_Q_ONE;
    if (!a) return -2;

    if (dg_trans_alignment_eval_tangent(a, s, &tan) != 0) return -3;
    (void)dg_trans_alignment_eval_roll(a, s, &roll);

    origin.x = 0;
    origin.y = 0;
    origin.z = 0;

    if (dg_trans_frame_build(origin, tan, roll, &f) != 0) return -4;
    *out_up_unit = f.up;
    return 0;
}
