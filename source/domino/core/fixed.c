/*
FILE: source/domino/core/fixed.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/fixed
RESPONSIBILITY: Implements `fixed`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-critical fixed-point math; relies on `source/domino/core/det_invariants.h` (two's complement, arithmetic right shift).
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/core/fixed.h"

/* Fixed-point arithmetic is part of the deterministic core. This implementation:
 * - uses saturating semantics for bounded Q formats
 * - avoids non-portable 128-bit compiler extensions by emulating u128 multiply
 */
#define Q4_12_MAX  ((q4_12)0x7FFF)
#define Q4_12_MIN  ((q4_12)0x8000)

#define Q32_MAX    ((i64)0x7FFFFFFF)
#define Q32_MIN    ((i64)0x80000000)

#define Q64_MAX    ((q48_16)0x7FFFFFFFFFFFFFFFLL)
#define Q64_MIN    ((q48_16)0x8000000000000000LL)

typedef struct d_u128 {
    u64 hi;
    u64 lo;
} d_u128;

static q4_12 d_q4_12_saturate_i32(i32 v) {
    if (v > (i32)Q4_12_MAX) {
        return Q4_12_MAX;
    }
    if (v < (i32)Q4_12_MIN) {
        return Q4_12_MIN;
    }
    return (q4_12)v;
}

static q16_16 d_q32_saturate_i64(i64 v) {
    if (v > Q32_MAX) {
        return (q16_16)Q32_MAX;
    }
    if (v < Q32_MIN) {
        return (q16_16)Q32_MIN;
    }
    return (q16_16)v;
}

static q48_16 d_q64_saturate_i64(i64 v) {
    if (v > Q64_MAX) {
        return Q64_MAX;
    }
    if (v < Q64_MIN) {
        return Q64_MIN;
    }
    return v;
}

static u64 d_abs_i64_u64(i64 v) {
    if (v < 0) {
        if (v == Q64_MIN) {
            return ((u64)1) << 63;
        }
        return (u64)(-v);
    }
    return (u64)v;
}

static d_u128 d_mul_u64(u64 a, u64 b) {
    /* Portable 64x64->128 multiply using 32-bit partial products (C89/C90 has no u128). */
    u32 a0 = (u32)(a & 0xFFFFFFFFUL);
    u32 a1 = (u32)(a >> 32);
    u32 b0 = (u32)(b & 0xFFFFFFFFUL);
    u32 b1 = (u32)(b >> 32);

    u64 p0 = (u64)a0 * (u64)b0;
    u64 p1 = (u64)a0 * (u64)b1;
    u64 p2 = (u64)a1 * (u64)b0;
    u64 p3 = (u64)a1 * (u64)b1;

    u64 lo = p0;
    u64 carry = 0;

    u64 t = lo + (p1 << 32);
    if (t < lo) {
        carry++;
    }
    lo = t;

    t = lo + (p2 << 32);
    if (t < lo) {
        carry++;
    }
    lo = t;

    u64 hi = p3 + (p1 >> 32) + (p2 >> 32) + carry;

    d_u128 result;
    result.hi = hi;
    result.lo = lo;
    return result;
}

static void d_shift_right_u128(const d_u128* value, unsigned int shift, d_u128* out_value) {
    /* Assumes 0 < shift < 64 for current usage. */
    out_value->hi = value->hi >> shift;
    out_value->lo = (value->hi << (64 - shift)) | (value->lo >> shift);
}

static q48_16 d_compose_signed_from_u128(u64 hi, u64 lo, d_bool negative) {
    if (!negative) {
        if (hi != 0) {
            return Q64_MAX;
        }
        if (lo > (u64)Q64_MAX) {
            return Q64_MAX;
        }
        return (q48_16)lo;
    }
    if (hi != 0) {
        return Q64_MIN;
    }
    if (lo > (((u64)1) << 63)) {
        return Q64_MIN;
    }
    if (lo == (((u64)1) << 63)) {
        return Q64_MIN;
    }
    return (q48_16)(-((i64)lo));
}

static q48_16 d_shift_left_i64_saturate(i64 v, unsigned int shift) {
    /* NOTE: Uses signed shifts; ISO C90 leaves some signed-shift behavior undefined/implementation-defined.
     * The determinism baseline assumes two's complement toolchains (see source/domino/core/det_invariants.h).
     */
    if (shift >= 63) {
        return (v >= 0) ? Q64_MAX : Q64_MIN;
    }
    if (v > (Q64_MAX >> shift)) {
        return Q64_MAX;
    }
    if (v < (Q64_MIN >> shift)) {
        return Q64_MIN;
    }
    return (q48_16)(v << shift);
}

/* Integer conversions */
q4_12 d_q4_12_from_int(i32 value) {
    return d_q4_12_saturate_i32(value << Q4_12_FRAC_BITS);
}

i32 d_q4_12_to_int(q4_12 value) {
    return (i32)(value >> Q4_12_FRAC_BITS);
}

q16_16 d_q16_16_from_int(i32 value) {
    return (q16_16)(value << Q16_16_FRAC_BITS);
}

i32 d_q16_16_to_int(q16_16 value) {
    return (i32)(value >> Q16_16_FRAC_BITS);
}

q24_8 d_q24_8_from_int(i32 value) {
    return (q24_8)(value << Q24_8_FRAC_BITS);
}

i32 d_q24_8_to_int(q24_8 value) {
    return (i32)(value >> Q24_8_FRAC_BITS);
}

q48_16 d_q48_16_from_int(i64 value) {
    return d_shift_left_i64_saturate(value, Q48_16_FRAC_BITS);
}

i64 d_q48_16_to_int(q48_16 value) {
    return (i64)(value >> Q48_16_FRAC_BITS);
}

/* Arithmetic helpers */
q4_12 d_q4_12_add(q4_12 a, q4_12 b) {
    i32 sum = (i32)a + (i32)b;
    return d_q4_12_saturate_i32(sum);
}

q4_12 d_q4_12_sub(q4_12 a, q4_12 b) {
    i32 diff = (i32)a - (i32)b;
    return d_q4_12_saturate_i32(diff);
}

q4_12 d_q4_12_mul(q4_12 a, q4_12 b) {
    i32 prod = (i32)a * (i32)b;
    i32 shifted = prod >> Q4_12_FRAC_BITS;
    return d_q4_12_saturate_i32(shifted);
}

q4_12 d_q4_12_div(q4_12 a, q4_12 b) {
    if (b == 0) {
        return (a >= 0) ? Q4_12_MAX : Q4_12_MIN;
    }
    i32 num = ((i32)a << Q4_12_FRAC_BITS);
    i32 div = num / (i32)b;
    return d_q4_12_saturate_i32(div);
}

q16_16 d_q16_16_add(q16_16 a, q16_16 b) {
    i64 sum = (i64)a + (i64)b;
    return d_q32_saturate_i64(sum);
}

q16_16 d_q16_16_sub(q16_16 a, q16_16 b) {
    i64 diff = (i64)a - (i64)b;
    return d_q32_saturate_i64(diff);
}

q16_16 d_q16_16_mul(q16_16 a, q16_16 b) {
    i64 prod = (i64)a * (i64)b;
    i64 shifted = prod >> Q16_16_FRAC_BITS;
    return d_q32_saturate_i64(shifted);
}

q16_16 d_q16_16_div(q16_16 a, q16_16 b) {
    if (b == 0) {
        return (a >= 0) ? (q16_16)Q32_MAX : (q16_16)Q32_MIN;
    }
    i64 num = ((i64)a << Q16_16_FRAC_BITS);
    i64 div = num / (i64)b;
    return d_q32_saturate_i64(div);
}

q24_8 d_q24_8_add(q24_8 a, q24_8 b) {
    i64 sum = (i64)a + (i64)b;
    return (q24_8)d_q32_saturate_i64(sum);
}

q24_8 d_q24_8_sub(q24_8 a, q24_8 b) {
    i64 diff = (i64)a - (i64)b;
    return (q24_8)d_q32_saturate_i64(diff);
}

q24_8 d_q24_8_mul(q24_8 a, q24_8 b) {
    i64 prod = (i64)a * (i64)b;
    i64 shifted = prod >> Q24_8_FRAC_BITS;
    return (q24_8)d_q32_saturate_i64(shifted);
}

q24_8 d_q24_8_div(q24_8 a, q24_8 b) {
    if (b == 0) {
        return (a >= 0) ? (q24_8)Q32_MAX : (q24_8)Q32_MIN;
    }
    i64 num = ((i64)a << Q24_8_FRAC_BITS);
    i64 div = num / (i64)b;
    return (q24_8)d_q32_saturate_i64(div);
}

q48_16 d_q48_16_add(q48_16 a, q48_16 b) {
    if (b > 0 && a > (Q64_MAX - b)) {
        return Q64_MAX;
    }
    if (b < 0 && a < (Q64_MIN - b)) {
        return Q64_MIN;
    }
    return a + b;
}

q48_16 d_q48_16_sub(q48_16 a, q48_16 b) {
    if (b < 0 && a > (Q64_MAX + b)) {
        return Q64_MAX;
    }
    if (b > 0 && a < (Q64_MIN + b)) {
        return Q64_MIN;
    }
    return a - b;
}

q48_16 d_q48_16_mul(q48_16 a, q48_16 b) {
    d_bool negative = ((a < 0) != (b < 0)) ? D_TRUE : D_FALSE;
    u64 ua = d_abs_i64_u64(a);
    u64 ub = d_abs_i64_u64(b);

    d_u128 prod = d_mul_u64(ua, ub);
    d_u128 scaled;
    d_shift_right_u128(&prod, Q48_16_FRAC_BITS, &scaled);

    return d_compose_signed_from_u128(scaled.hi, scaled.lo, negative);
}

q48_16 d_q48_16_div(q48_16 a, q48_16 b) {
    if (b == 0) {
        return (a >= 0) ? Q64_MAX : Q64_MIN;
    }

    /* Saturating shift of numerator. */
    q48_16 shifted = d_shift_left_i64_saturate(a, Q48_16_FRAC_BITS);
    if (shifted == Q64_MAX || shifted == Q64_MIN) {
        return shifted;
    }

    return d_q64_saturate_i64(shifted / b);
}

/* Cross-format helpers */
q16_16 d_q16_16_from_q4_12(q4_12 v) {
    return (q16_16)((i32)v << (Q16_16_FRAC_BITS - Q4_12_FRAC_BITS));
}

q4_12 d_q4_12_from_q16_16(q16_16 v) {
    i32 tmp = (i32)(v >> (Q16_16_FRAC_BITS - Q4_12_FRAC_BITS));
    return d_q4_12_saturate_i32(tmp);
}

q24_8 d_q24_8_from_q16_16(q16_16 v) {
    i32 tmp = (i32)(v >> (Q16_16_FRAC_BITS - Q24_8_FRAC_BITS));
    return (q24_8)d_q32_saturate_i64(tmp);
}

q16_16 d_q16_16_from_q24_8(q24_8 v) {
    i64 tmp = ((i64)v) << (Q16_16_FRAC_BITS - Q24_8_FRAC_BITS);
    return d_q32_saturate_i64(tmp);
}

q48_16 d_q48_16_from_q16_16(q16_16 v) {
    return (q48_16)(i64)v;
}

q16_16 d_q16_16_from_q48_16(q48_16 v) {
    return d_q32_saturate_i64((i64)v);
}
