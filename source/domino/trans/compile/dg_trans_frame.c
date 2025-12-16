/*
FILE: source/domino/trans/compile/dg_trans_frame.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/dg_trans_frame
RESPONSIBILITY: Implements `dg_trans_frame`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic local frame construction for TRANS (C89). */
#include "trans/compile/dg_trans_frame.h"

#include <string.h>

#include "core/det_invariants.h"
#include "domino/core/fixed.h"

#define DG_TRANS_Q_ONE        ((dg_q)((i64)1 << 16))
#define DG_TRANS_Q_HALF_TURN  ((dg_q)((i64)1 << 15)) /* 0.5 turn */
#define DG_TRANS_Q_QUART_TURN ((dg_q)((i64)1 << 14)) /* 0.25 turn */

/* CORDIC parameters for Q48.16 turns.
 * NOTE: At this resolution, atan(2^-i) becomes zero at i>=15, so we stop at 15.
 */
#define DG_TRANS_CORDIC_ITERS 15u
#define DG_TRANS_CORDIC_K_Q16 ((dg_q)39797) /* ~0.607252935 * 65536 */

static const dg_q dg_trans_atan_turns_q16[DG_TRANS_CORDIC_ITERS] = {
    (dg_q)8192, (dg_q)4836, (dg_q)2555, (dg_q)1297, (dg_q)651,
    (dg_q)326,  (dg_q)163,  (dg_q)81,   (dg_q)41,   (dg_q)20,
    (dg_q)10,   (dg_q)5,    (dg_q)3,    (dg_q)1,    (dg_q)1
};

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

static dg_vec3_q dg_trans_vec3_cross(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q out;
    out.x = (dg_q)d_q48_16_sub(d_q48_16_mul((q48_16)a.y, (q48_16)b.z), d_q48_16_mul((q48_16)a.z, (q48_16)b.y));
    out.y = (dg_q)d_q48_16_sub(d_q48_16_mul((q48_16)a.z, (q48_16)b.x), d_q48_16_mul((q48_16)a.x, (q48_16)b.z));
    out.z = (dg_q)d_q48_16_sub(d_q48_16_mul((q48_16)a.x, (q48_16)b.y), d_q48_16_mul((q48_16)a.y, (q48_16)b.x));
    return out;
}

static dg_vec3_q dg_trans_vec3_add(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q out;
    out.x = (dg_q)d_q48_16_add((q48_16)a.x, (q48_16)b.x);
    out.y = (dg_q)d_q48_16_add((q48_16)a.y, (q48_16)b.y);
    out.z = (dg_q)d_q48_16_add((q48_16)a.z, (q48_16)b.z);
    return out;
}

static dg_vec3_q dg_trans_vec3_sub(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q out;
    out.x = (dg_q)d_q48_16_sub((q48_16)a.x, (q48_16)b.x);
    out.y = (dg_q)d_q48_16_sub((q48_16)a.y, (q48_16)b.y);
    out.z = (dg_q)d_q48_16_sub((q48_16)a.z, (q48_16)b.z);
    return out;
}

static dg_vec3_q dg_trans_vec3_scale(dg_vec3_q v, dg_q s) {
    dg_vec3_q out;
    out.x = (dg_q)d_q48_16_mul((q48_16)v.x, (q48_16)s);
    out.y = (dg_q)d_q48_16_mul((q48_16)v.y, (q48_16)s);
    out.z = (dg_q)d_q48_16_mul((q48_16)v.z, (q48_16)s);
    return out;
}

static int dg_trans_vec3_is_zero(dg_vec3_q v) {
    return (v.x == 0 && v.y == 0 && v.z == 0) ? 1 : 0;
}

static dg_vec3_q dg_trans_vec3_normalize_unit(dg_vec3_q v, int *out_is_zero) {
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
        if (out_is_zero) *out_is_zero = 1;
        out.x = 0; out.y = 0; out.z = 0;
        return out;
    }

    while (max_abs > 0x3FFFFFFFULL) {
        max_abs >>= 1;
        shift += 1u;
    }

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
        if (out_is_zero) *out_is_zero = 1;
        out.x = 0; out.y = 0; out.z = 0;
        return out;
    }

    if (out_is_zero) *out_is_zero = 0;
    out.x = (dg_q)(((i64)sx << 16) / (i64)len);
    out.y = (dg_q)(((i64)sy << 16) / (i64)len);
    out.z = (dg_q)(((i64)sz << 16) / (i64)len);
    return out;
}

static dg_q dg_trans_wrap_turns_half(dg_q turns) {
    dg_q one = DG_TRANS_Q_ONE;
    dg_q half = DG_TRANS_Q_HALF_TURN;
    dg_q r = (dg_q)((i64)turns % (i64)one);
    if (r < (dg_q)(-half)) {
        r = (dg_q)d_q48_16_add((q48_16)r, (q48_16)one);
    }
    if (r >= half) {
        r = (dg_q)d_q48_16_sub((q48_16)r, (q48_16)one);
    }
    return r;
}

int dg_trans_sincos_turns(dg_q turns, dg_q *out_cos, dg_q *out_sin) {
    dg_q a;
    dg_q half = DG_TRANS_Q_HALF_TURN;
    dg_q quart = DG_TRANS_Q_QUART_TURN;
    int flip = 0;
    i64 x;
    i64 y;
    i64 z;
    u32 i;

    if (!out_cos || !out_sin) return -1;
    *out_cos = DG_TRANS_Q_ONE;
    *out_sin = 0;

    a = dg_trans_wrap_turns_half(turns);
    if (a > quart) {
        a = (dg_q)d_q48_16_sub((q48_16)a, (q48_16)half);
        flip = 1;
    } else if (a < (dg_q)(-quart)) {
        a = (dg_q)d_q48_16_add((q48_16)a, (q48_16)half);
        flip = 1;
    }

    /* CORDIC rotation mode: start with (K,0). */
    x = (i64)DG_TRANS_CORDIC_K_Q16;
    y = 0;
    z = (i64)a;

    for (i = 0u; i < DG_TRANS_CORDIC_ITERS; ++i) {
        i64 x_new;
        i64 y_new;
        i64 x_shift = x >> i;
        i64 y_shift = y >> i;
        dg_q atan_i = dg_trans_atan_turns_q16[i];

        if (z >= 0) {
            x_new = x - y_shift;
            y_new = y + x_shift;
            z -= (i64)atan_i;
        } else {
            x_new = x + y_shift;
            y_new = y - x_shift;
            z += (i64)atan_i;
        }
        x = x_new;
        y = y_new;
    }

    if (flip) {
        x = -x;
        y = -y;
    }

    *out_cos = (dg_q)x;
    *out_sin = (dg_q)y;
    return 0;
}

int dg_trans_frame_build(dg_vec3_q origin, dg_vec3_q forward_dir, dg_q roll_turns, dg_trans_frame *out_frame) {
    dg_vec3_q fwd;
    dg_vec3_q up_ref;
    dg_vec3_q right;
    dg_vec3_q up;
    dg_q c;
    dg_q s;
    dg_vec3_q right2;
    dg_vec3_q up2;
    int is_zero;

    if (!out_frame) return -1;
    memset(out_frame, 0, sizeof(*out_frame));

    fwd = dg_trans_vec3_normalize_unit(forward_dir, &is_zero);
    if (is_zero) return -2;

    up_ref.x = 0;
    up_ref.y = 0;
    up_ref.z = DG_TRANS_Q_ONE;

    right = dg_trans_vec3_cross(up_ref, fwd);
    if (dg_trans_vec3_is_zero(right)) {
        /* forward parallel to world up: use world +Y as reference. */
        up_ref.x = 0;
        up_ref.y = DG_TRANS_Q_ONE;
        up_ref.z = 0;
        right = dg_trans_vec3_cross(up_ref, fwd);
    }

    right = dg_trans_vec3_normalize_unit(right, &is_zero);
    if (is_zero) return -3;

    up = dg_trans_vec3_cross(fwd, right);
    up = dg_trans_vec3_normalize_unit(up, &is_zero);
    if (is_zero) return -4;

    if (dg_trans_sincos_turns(roll_turns, &c, &s) != 0) {
        return -5;
    }

    /* Apply roll about forward axis: right' = right*c + up*s; up' = up*c - right*s. */
    right2 = dg_trans_vec3_add(dg_trans_vec3_scale(right, c), dg_trans_vec3_scale(up, s));
    up2 = dg_trans_vec3_sub(dg_trans_vec3_scale(up, c), dg_trans_vec3_scale(right, s));

    right2 = dg_trans_vec3_normalize_unit(right2, &is_zero);
    if (is_zero) return -6;
    up2 = dg_trans_vec3_normalize_unit(up2, &is_zero);
    if (is_zero) return -7;

    out_frame->origin = origin;
    out_frame->forward = fwd;
    out_frame->right = right2;
    out_frame->up = up2;
    return 0;
}

