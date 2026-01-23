/*
FILE: source/domino/compat/capability_set.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / compat/capability_set
RESPONSIBILITY: Implements capability set membership helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic set membership for sorted inputs.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/capability.h"

d_bool dom_capability_set_contains(const dom_capability_set_view* set,
                                   dom_capability_id id)
{
    u32 lo;
    u32 hi;
    if (!set || !set->ids || set->count == 0u) {
        return D_FALSE;
    }
    lo = 0u;
    hi = set->count;
    while (lo < hi) {
        u32 mid = lo + (hi - lo) / 2u;
        dom_capability_id v = set->ids[mid];
        if (v == id) {
            return D_TRUE;
        }
        if (v < id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return D_FALSE;
}

d_bool dom_capability_set_is_subset(const dom_capability_set_view* required,
                                    const dom_capability_set_view* provided)
{
    u32 i;
    if (!required || required->count == 0u) {
        return D_TRUE;
    }
    if (!provided || !provided->ids || provided->count == 0u) {
        return D_FALSE;
    }
    for (i = 0u; i < required->count; ++i) {
        if (!dom_capability_set_contains(provided, required->ids[i])) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}
