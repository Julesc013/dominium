/*
FILE: include/dominium/rules/reproduction_rules.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game rules / life reproduction
RESPONSIBILITY: Defines reproduction eligibility policies (bounded).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Eligibility evaluation must be deterministic.
*/
#ifndef DOMINIUM_RULES_REPRODUCTION_RULES_H
#define DOMINIUM_RULES_REPRODUCTION_RULES_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_reproduction_rules {
    u32 min_parents;
    u32 max_parents;
    dom_act_time_t gestation_ticks;
    u8 allow_unknown_parents;
} life_reproduction_rules;

int life_reproduction_rules_validate(const life_reproduction_rules* rules,
                                     const u64* parent_ids,
                                     u32 parent_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_REPRODUCTION_RULES_H */
