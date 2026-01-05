/*
FILE: source/domino/core/spacetime.c
MODULE: Domino
RESPONSIBILITY: Canonical spacetime types and deterministic conversions.
*/
#include "domino/core/spacetime.h"

#define DOM_U64_MAX ((u64)~(u64)0)

static int dom_mul_div_u64(u64 a, u64 mul, u64 div, u64 *out_val) {
    u64 result;
    if (!out_val || div == 0ull) {
        return DOM_SPACETIME_INVALID;
    }
    if (mul != 0ull && a > (DOM_U64_MAX / mul)) {
        *out_val = DOM_U64_MAX;
        return DOM_SPACETIME_OVERFLOW;
    }
    result = (a * mul) / div;
    *out_val = result;
    return DOM_SPACETIME_OK;
}

int dom_timebase_validate(const dom_timebase *tb) {
    if (!tb || tb->ups == 0u) {
        return DOM_SPACETIME_INVALID;
    }
    return DOM_SPACETIME_OK;
}

int dom_ticks_to_us(dom_tick ticks, dom_ups ups, u64 *out_us) {
    if (ups == 0u) {
        if (out_us) {
            *out_us = 0ull;
        }
        return DOM_SPACETIME_INVALID;
    }
    return dom_mul_div_u64((u64)ticks, 1000000ull, (u64)ups, out_us);
}

int dom_ticks_to_ns(dom_tick ticks, dom_ups ups, u64 *out_ns) {
    if (ups == 0u) {
        if (out_ns) {
            *out_ns = 0ull;
        }
        return DOM_SPACETIME_INVALID;
    }
    return dom_mul_div_u64((u64)ticks, 1000000000ull, (u64)ups, out_ns);
}

int dom_id_hash64(const char *bytes, u32 len, u64 *out_hash) {
    u64 hash;
    u32 i;

    if (!out_hash || (!bytes && len > 0u)) {
        return DOM_SPACETIME_INVALID;
    }

    hash = 14695981039346656037ull;
    for (i = 0u; i < len; ++i) {
        hash ^= (u64)(unsigned char)bytes[i];
        hash *= 1099511628211ull;
    }

    *out_hash = hash;
    return DOM_SPACETIME_OK;
}
