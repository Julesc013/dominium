/*
FILE: game/core/dom_interest_macro.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / interest_macro
RESPONSIBILITY: Example macro update path that requires InterestSet input.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: InterestSet ordering is deterministic.
*/
#include "dominium/interest_macro.h"

int dom_macro_step(const dom_interest_set* set, dom_macro_stats* out_stats)
{
    u32 i;
    if (!set || !out_stats) {
        return -1;
    }
    out_stats->processed = 0u;
    out_stats->strength_sum = 0u;
    for (i = 0u; i < set->count; ++i) {
        out_stats->processed += 1u;
        out_stats->strength_sum += (u64)set->entries[i].strength;
    }
    return 0;
}
