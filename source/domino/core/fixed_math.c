/*
FILE: source/domino/core/fixed_math.c
MODULE: Domino
PURPOSE: Deterministic fixed-point trig/sqrt/div helpers (no floating-point).
*/
#include "domino/core/fixed_math.h"

#include <limits.h>

enum {
    TURN_QUARTER = 0x4000u,
    TURN_MASK = 0xFFFFu,
    TURN_QUARTER_SHIFT = 14,
    SIN_LUT_SIZE = 64u
};

static const q16_16 k_sin_quarter_lut[SIN_LUT_SIZE + 1u] = {
    0, 1608, 3216, 4821, 6424, 8022, 9616, 11204,
    12785, 14359, 15924, 17479, 19024, 20557, 22078, 23586,
    25080, 26558, 28020, 29466, 30893, 32303, 33692, 35062,
    36410, 37736, 39040, 40320, 41576, 42806, 44011, 45190,
    46341, 47464, 48559, 49624, 50660, 51665, 52639, 53581,
    54491, 55368, 56212, 57022, 57798, 58538, 59244, 59914,
    60547, 61145, 61705, 62228, 62714, 63162, 63572, 63944,
    64277, 64571, 64827, 65043, 65220, 65358, 65457, 65516,
    65536
};

static q16_16 sin_quarter_interp(u32 offset) {
    const u32 scaled = offset * SIN_LUT_SIZE;
    const u32 idx = (scaled >> TURN_QUARTER_SHIFT);
    const u32 frac = (scaled & (TURN_QUARTER - 1u));
    if (idx >= SIN_LUT_SIZE) {
        return k_sin_quarter_lut[SIN_LUT_SIZE];
    }
    {
        const q16_16 v0 = k_sin_quarter_lut[idx];
        const q16_16 v1 = k_sin_quarter_lut[idx + 1u];
        const i32 diff = (i32)(v1 - v0);
        const i32 interp = (i32)((i64)diff * (i64)frac >> TURN_QUARTER_SHIFT);
        return (q16_16)(v0 + interp);
    }
}

static u32 isqrt_u64(u64 n) {
    u64 res = 0u;
    u64 bit = 1ull << 62;
    while (bit > n) {
        bit >>= 2u;
    }
    while (bit != 0u) {
        if (n >= res + bit) {
            n -= res + bit;
            res = (res >> 1u) + bit;
        } else {
            res >>= 1u;
        }
        bit >>= 2u;
    }
    return (u32)res;
}

q16_16 d_fixed_sin_turn(q16_16 turn) {
    const u32 norm = ((u32)turn) & TURN_MASK;
    const u32 quadrant = (norm >> TURN_QUARTER_SHIFT) & 0x3u;
    u32 offset = (norm & (TURN_QUARTER - 1u));
    q16_16 val;

    if (quadrant & 1u) {
        offset = TURN_QUARTER - offset;
    }
    val = sin_quarter_interp(offset);
    if (quadrant >= 2u) {
        val = (q16_16)(-val);
    }
    return val;
}

q16_16 d_fixed_cos_turn(q16_16 turn) {
    return d_fixed_sin_turn((q16_16)(turn + (q16_16)TURN_QUARTER));
}

q16_16 d_fixed_sqrt_q16_16(q16_16 value) {
    if (value <= 0) {
        return 0;
    }
    {
        const u64 n = ((u64)(u32)value) << 16u;
        const u32 root = isqrt_u64(n);
        return (q16_16)root;
    }
}

q16_16 d_fixed_div_q16_16(q16_16 numer, q16_16 denom) {
    if (denom == 0) {
        return (numer >= 0) ? (q16_16)INT32_MAX : (q16_16)INT32_MIN;
    }
    {
        const i64 num = ((i64)numer) << 16u;
        i64 q = num / (i64)denom;
        if (q > (i64)INT32_MAX) q = (i64)INT32_MAX;
        if (q < (i64)INT32_MIN) q = (i64)INT32_MIN;
        return (q16_16)q;
    }
}
