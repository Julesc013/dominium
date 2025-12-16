/*
FILE: source/domino/core/dg_pose.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dg_pose
RESPONSIBILITY: Implements `dg_pose`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Canonical fixed-point pose model (C89). */
#include "core/dg_pose.h"

#include <string.h>

#include "core/det_invariants.h"

#define DG_Q_FRAC_BITS 16u
#define DG_Q_ONE       ((dg_q)((i64)1 << DG_Q_FRAC_BITS))

/* q48_16 limits (same numeric domain as signed i64). */
#define DG_Q_MAX ((dg_q)0x7FFFFFFFFFFFFFFFLL)
#define DG_Q_MIN ((dg_q)0x8000000000000000LL)

typedef struct dg_u128 {
    u64 hi;
    u64 lo;
} dg_u128;

static u64 dg_abs_i64_u64(i64 v) {
    if (v < 0) {
        if (v == (i64)DG_Q_MIN) {
            return ((u64)1) << 63;
        }
        return (u64)(-v);
    }
    return (u64)v;
}

static dg_u128 dg_mul_u64(u64 a, u64 b) {
    u32 a0 = (u32)(a & 0xFFFFFFFFUL);
    u32 a1 = (u32)(a >> 32);
    u32 b0 = (u32)(b & 0xFFFFFFFFUL);
    u32 b1 = (u32)(b >> 32);

    u64 p0 = (u64)a0 * (u64)b0;
    u64 p1 = (u64)a0 * (u64)b1;
    u64 p2 = (u64)a1 * (u64)b0;
    u64 p3 = (u64)a1 * (u64)b1;

    u64 lo = p0;
    u64 carry = 0u;

    u64 t = lo + (p1 << 32);
    if (t < lo) carry += 1u;
    lo = t;

    t = lo + (p2 << 32);
    if (t < lo) carry += 1u;
    lo = t;

    {
        dg_u128 r;
        r.hi = p3 + (p1 >> 32) + (p2 >> 32) + carry;
        r.lo = lo;
        return r;
    }
}

static void dg_u128_add_u64(dg_u128 *v, u64 add) {
    u64 lo0;
    if (!v) return;
    lo0 = v->lo;
    v->lo += add;
    if (v->lo < lo0) {
        v->hi += 1u;
    }
}

static dg_u128 dg_u128_shr16(dg_u128 v) {
    dg_u128 out;
    out.hi = v.hi >> 16;
    out.lo = (v.hi << 48) | (v.lo >> 16);
    return out;
}

static dg_q dg_compose_signed_from_u128(u64 hi, u64 lo, d_bool negative) {
    if (!negative) {
        if (hi != 0u) return DG_Q_MAX;
        if (lo > (u64)DG_Q_MAX) return DG_Q_MAX;
        return (dg_q)lo;
    }

    if (hi != 0u) return DG_Q_MIN;
    if (lo > (((u64)1) << 63)) return DG_Q_MIN;
    if (lo == (((u64)1) << 63)) return DG_Q_MIN;
    return (dg_q)(-((i64)lo));
}

static dg_q dg_q_add(dg_q a, dg_q b) { return (dg_q)d_q48_16_add((q48_16)a, (q48_16)b); }
static dg_q dg_q_sub(dg_q a, dg_q b) { return (dg_q)d_q48_16_sub((q48_16)a, (q48_16)b); }

static dg_q dg_q_neg(dg_q v) {
    if (v == DG_Q_MIN) return DG_Q_MAX; /* saturate */
    return (dg_q)(-v);
}

static dg_q dg_q_mul(dg_q a, dg_q b, dg_round_mode round_mode) {
    d_bool negative = ((a < 0) != (b < 0)) ? D_TRUE : D_FALSE;
    u64 ua = dg_abs_i64_u64((i64)a);
    u64 ub = dg_abs_i64_u64((i64)b);
    dg_u128 prod = dg_mul_u64(ua, ub);
    u64 remainder = prod.lo & 0xFFFFu;

    if (round_mode == DG_ROUND_NEAR) {
        dg_u128_add_u64(&prod, 0x8000u);
    }

    {
        dg_u128 scaled = dg_u128_shr16(prod);
        if (round_mode == DG_ROUND_FLOOR && negative && remainder != 0u) {
            /* floor(-x) = -ceil(x) => bump magnitude if any remainder existed. */
            dg_u128_add_u64(&scaled, 1u);
        }
        return dg_compose_signed_from_u128(scaled.hi, scaled.lo, negative);
    }
}

static dg_vec3_q dg_vec3_add(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q out;
    out.x = dg_q_add(a.x, b.x);
    out.y = dg_q_add(a.y, b.y);
    out.z = dg_q_add(a.z, b.z);
    return out;
}

static dg_vec3_q dg_vec3_sub(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q out;
    out.x = dg_q_sub(a.x, b.x);
    out.y = dg_q_sub(a.y, b.y);
    out.z = dg_q_sub(a.z, b.z);
    return out;
}

static dg_vec3_q dg_vec3_neg(dg_vec3_q v) {
    dg_vec3_q out;
    out.x = dg_q_neg(v.x);
    out.y = dg_q_neg(v.y);
    out.z = dg_q_neg(v.z);
    return out;
}

static dg_vec3_q dg_vec3_cross(dg_vec3_q a, dg_vec3_q b, dg_round_mode round_mode) {
    dg_vec3_q out;
    out.x = dg_q_sub(dg_q_mul(a.y, b.z, round_mode), dg_q_mul(a.z, b.y, round_mode));
    out.y = dg_q_sub(dg_q_mul(a.z, b.x, round_mode), dg_q_mul(a.x, b.z, round_mode));
    out.z = dg_q_sub(dg_q_mul(a.x, b.y, round_mode), dg_q_mul(a.y, b.x, round_mode));
    return out;
}

static dg_vec3_q dg_vec3_scale2(dg_vec3_q v) {
    dg_vec3_q out;
    out.x = dg_q_add(v.x, v.x);
    out.y = dg_q_add(v.y, v.y);
    out.z = dg_q_add(v.z, v.z);
    return out;
}

static dg_rot_q dg_rot_conjugate(dg_rot_q q) {
    dg_rot_q out;
    out.x = dg_q_neg(q.x);
    out.y = dg_q_neg(q.y);
    out.z = dg_q_neg(q.z);
    out.w = q.w;
    return out;
}

static dg_rot_q dg_rot_mul(dg_rot_q a, dg_rot_q b, dg_round_mode round_mode) {
    dg_rot_q out;

    /* Hamilton product. */
    dg_q ax = a.x, ay = a.y, az = a.z, aw = a.w;
    dg_q bx = b.x, by = b.y, bz = b.z, bw = b.w;

    out.x = dg_q_add(
        dg_q_add(dg_q_mul(aw, bx, round_mode), dg_q_mul(ax, bw, round_mode)),
        dg_q_sub(dg_q_mul(ay, bz, round_mode), dg_q_mul(az, by, round_mode))
    );

    out.y = dg_q_add(
        dg_q_add(dg_q_mul(aw, by, round_mode), dg_q_mul(ay, bw, round_mode)),
        dg_q_sub(dg_q_mul(az, bx, round_mode), dg_q_mul(ax, bz, round_mode))
    );

    out.z = dg_q_add(
        dg_q_add(dg_q_mul(aw, bz, round_mode), dg_q_mul(az, bw, round_mode)),
        dg_q_sub(dg_q_mul(ax, by, round_mode), dg_q_mul(ay, bx, round_mode))
    );

    out.w = dg_q_sub(
        dg_q_sub(dg_q_sub(dg_q_mul(aw, bw, round_mode), dg_q_mul(ax, bx, round_mode)), dg_q_mul(ay, by, round_mode)),
        dg_q_mul(az, bz, round_mode)
    );

    return out;
}

static dg_vec3_q dg_rot_rotate_vec3(dg_rot_q q, dg_vec3_q v, dg_round_mode round_mode) {
    /* v' = v + w*t + cross(q.xyz, t), where t = 2*cross(q.xyz, v). */
    dg_vec3_q qv;
    dg_vec3_q t;
    dg_vec3_q w_t;
    dg_vec3_q c;

    qv.x = q.x;
    qv.y = q.y;
    qv.z = q.z;

    t = dg_vec3_scale2(dg_vec3_cross(qv, v, round_mode));

    w_t.x = dg_q_mul(q.w, t.x, round_mode);
    w_t.y = dg_q_mul(q.w, t.y, round_mode);
    w_t.z = dg_q_mul(q.w, t.z, round_mode);

    c = dg_vec3_cross(qv, t, round_mode);
    return dg_vec3_add(dg_vec3_add(v, w_t), c);
}

dg_vec3_q dg_vec3_zero(void) {
    dg_vec3_q v;
    v.x = 0;
    v.y = 0;
    v.z = 0;
    return v;
}

dg_rot_q dg_rot_identity(void) {
    dg_rot_q q;
    q.x = 0;
    q.y = 0;
    q.z = 0;
    q.w = DG_Q_ONE;
    return q;
}

dg_pose dg_pose_identity(void) {
    dg_pose p;
    p.pos = dg_vec3_zero();
    p.rot = dg_rot_identity();
    p.incline = 0;
    p.roll = 0;
    return p;
}

dg_vec3_q dg_pose_transform_point(const dg_pose *p, dg_vec3_q local_point, dg_round_mode round_mode) {
    dg_vec3_q r;
    if (!p) return local_point;
    r = dg_rot_rotate_vec3(p->rot, local_point, round_mode);
    return dg_vec3_add(r, p->pos);
}

dg_vec3_q dg_pose_transform_dir(const dg_pose *p, dg_vec3_q local_dir, dg_round_mode round_mode) {
    if (!p) return local_dir;
    return dg_rot_rotate_vec3(p->rot, local_dir, round_mode);
}

dg_pose dg_pose_compose(const dg_pose *a, const dg_pose *b, dg_round_mode round_mode) {
    dg_pose out;
    dg_vec3_q bpos_rot;

    if (!a && !b) return dg_pose_identity();
    if (!a) return *b;
    if (!b) return *a;

    bpos_rot = dg_rot_rotate_vec3(a->rot, b->pos, round_mode);
    out.pos = dg_vec3_add(a->pos, bpos_rot);
    out.rot = dg_rot_mul(a->rot, b->rot, round_mode);
    out.incline = dg_q_add(a->incline, b->incline);
    out.roll = dg_q_add(a->roll, b->roll);
    return out;
}

dg_pose dg_pose_invert(const dg_pose *p, dg_round_mode round_mode) {
    dg_pose out;
    dg_rot_q inv;
    dg_vec3_q neg_pos;

    if (!p) return dg_pose_identity();

    /* For unit quaternions, inverse is conjugate. */
    inv = dg_rot_conjugate(p->rot);

    neg_pos = dg_vec3_neg(p->pos);
    out.pos = dg_rot_rotate_vec3(inv, neg_pos, round_mode);
    out.rot = inv;
    out.incline = dg_q_neg(p->incline);
    out.roll = dg_q_neg(p->roll);
    return out;
}

