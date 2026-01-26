/*
FILE: source/domino/compat/fixed_debug.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / compat/fixed_debug
RESPONSIBILITY: Implements `fixed_debug`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/core/fixed.h"

#define Q4_12_MAX_RAW   0x7FFF
#define Q4_12_MIN_RAW   0x8000
#define Q16_16_MAX_RAW  0x7FFFFFFF
#define Q16_16_MIN_RAW  0x80000000
#define Q24_8_MAX_RAW   0x7FFFFFFF
#define Q24_8_MIN_RAW   0x80000000
#define Q48_16_MAX_RAW  0x7FFFFFFFFFFFFFFFLL
#define Q48_16_MIN_RAW  0x8000000000000000LL

double d_q4_12_to_double(q4_12 value) {
    return ((double)value) / (double)(1 << Q4_12_FRAC_BITS);
}

q4_12 d_q4_12_from_double(double value) {
    double scaled = value * (double)(1 << Q4_12_FRAC_BITS);
    if (scaled > (double)Q4_12_MAX_RAW) {
        return (q4_12)Q4_12_MAX_RAW;
    }
    if (scaled < (double)Q4_12_MIN_RAW) {
        return (q4_12)Q4_12_MIN_RAW;
    }
    return (q4_12)(scaled);
}

double d_q16_16_to_double(q16_16 value) {
    return ((double)value) / (double)(1 << Q16_16_FRAC_BITS);
}

q16_16 d_q16_16_from_double(double value) {
    double scaled = value * (double)(1 << Q16_16_FRAC_BITS);
    if (scaled > (double)Q16_16_MAX_RAW) {
        return (q16_16)Q16_16_MAX_RAW;
    }
    if (scaled < (double)Q16_16_MIN_RAW) {
        return (q16_16)Q16_16_MIN_RAW;
    }
    return (q16_16)(scaled);
}

double d_q24_8_to_double(q24_8 value) {
    return ((double)value) / (double)(1 << Q24_8_FRAC_BITS);
}

q24_8 d_q24_8_from_double(double value) {
    double scaled = value * (double)(1 << Q24_8_FRAC_BITS);
    if (scaled > (double)Q24_8_MAX_RAW) {
        return (q24_8)Q24_8_MAX_RAW;
    }
    if (scaled < (double)Q24_8_MIN_RAW) {
        return (q24_8)Q24_8_MIN_RAW;
    }
    return (q24_8)(scaled);
}

double d_q48_16_to_double(q48_16 value) {
    return ((double)value) / (double)(1 << Q48_16_FRAC_BITS);
}

q48_16 d_q48_16_from_double(double value) {
    double scaled = value * (double)(1 << Q48_16_FRAC_BITS);
    if (scaled > (double)Q48_16_MAX_RAW) {
        return (q48_16)Q48_16_MAX_RAW;
    }
    if (scaled < (double)Q48_16_MIN_RAW) {
        return (q48_16)Q48_16_MIN_RAW;
    }
    return (q48_16)(scaled);
}
