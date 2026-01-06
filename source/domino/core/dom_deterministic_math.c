/*
FILE: source/domino/core/dom_deterministic_math.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_deterministic_math
RESPONSIBILITY: Canonical deterministic math wrappers for authoritative code paths.
*/
#include "domino/core/dom_deterministic_math.h"

#include "domino/core/fixed_math.h"

static u64 dom_isqrt_u64(u64 n) {
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
    return res;
}

q16_16 dom_sin_q16(q16_16 angle_turns) {
    return d_fixed_sin_turn(angle_turns);
}

q16_16 dom_cos_q16(q16_16 angle_turns) {
    return d_fixed_cos_turn(angle_turns);
}

u64 dom_sqrt_u64(u64 value) {
    return dom_isqrt_u64(value);
}

u64 dom_div_u64(u64 num, u64 den) {
    if (den == 0u) {
        return ~0ull;
    }
    return num / den;
}

q16_16 dom_angle_normalize_q16(q16_16 angle_turns) {
    return (q16_16)(((u32)angle_turns) & 0xFFFFu);
}
