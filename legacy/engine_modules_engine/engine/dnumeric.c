/*
FILE: source/domino/dnumeric.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / dnumeric
RESPONSIBILITY: Implements `dnumeric`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/dnumeric.h"

#include <limits.h>

/* Fixed-point conversions */

Q16_16 dnum_from_int32(I32 v)
{
    return (Q16_16)(v << 16);
}

I32 dnum_to_int32(Q16_16 v)
{
    return (I32)(v >> 16);
}

Q4_12 dnum_q16_to_q4(Q16_16 v)
{
    I32 shifted = (I32)(v >> 4);
    if (shifted > (I32)INT16_MAX) shifted = (I32)INT16_MAX;
    else if (shifted < (I32)INT16_MIN) shifted = (I32)INT16_MIN;
    return (Q4_12)shifted;
}

Q16_16 dnum_q4_to_q16(Q4_12 v)
{
    return (Q16_16)(((I32)v) << 4);
}

/* Angle helpers */

Turn dnum_turn_normalise_0_1(Turn t)
{
    const I32 full_turn = (I32)(1 << 16);
    I32 norm = (I32)(t % full_turn);
    if (norm < 0) {
        norm += full_turn;
    }
    return (Turn)norm;
}

Turn dnum_turn_normalise_neg_pos_half(Turn t)
{
    const I32 half_turn = (I32)(1 << 15);
    const I32 full_turn = (I32)(1 << 16);
    I32 norm = (I32)dnum_turn_normalise_0_1(t);
    if (norm >= half_turn) {
        norm -= full_turn;
    }
    return (Turn)norm;
}

Turn dnum_turn_add(Turn a, Turn b)
{
    return dnum_turn_normalise_0_1((Turn)((I32)a + (I32)b));
}

Turn dnum_turn_sub(Turn a, Turn b)
{
    return dnum_turn_normalise_0_1((Turn)((I32)a - (I32)b));
}

/* Time step policy */

const SecondsQ16 g_domino_dt_s = (SecondsQ16)((1 << 16) / DOMINO_DEFAULT_UPS);
