/*
FILE: include/dominium/interest_macro.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / interest_macro
RESPONSIBILITY: Macro update hooks that require InterestSet input.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic iteration required.
*/
#ifndef DOMINIUM_INTEREST_MACRO_H
#define DOMINIUM_INTEREST_MACRO_H

#include "dominium/interest_set.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_macro_stats {
    u32 processed;
    u64 strength_sum;
} dom_macro_stats;

/* Purpose: Macro update hook that only processes InterestSet entries. */
int dom_macro_step(const dom_interest_set* set, dom_macro_stats* out_stats);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_INTEREST_MACRO_H */
