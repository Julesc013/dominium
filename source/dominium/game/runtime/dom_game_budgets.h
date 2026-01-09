/*
FILE: source/dominium/game/runtime/dom_game_budgets.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_budgets
RESPONSIBILITY: Defines non-authoritative budget profiles for runtime subsystems.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_GAME_BUDGETS_H
#define DOM_GAME_BUDGETS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_GAME_BUDGET_OK = 0,
    DOM_GAME_BUDGET_INVALID_ARGUMENT = -1
};

enum {
    DOM_GAME_BUDGET_PROFILE_VERSION = 1u
};

typedef struct dom_game_budget_profile {
    u32 struct_size;
    u32 struct_version;
    u32 perf_tier;
    u32 derived_budget_ms;
    u32 derived_budget_io_bytes;
    u32 derived_budget_jobs;
    u32 ai_max_ops_per_tick;
    u32 ai_max_factions_per_tick;
} dom_game_budget_profile;

int dom_game_budget_profile_for_tier(u32 perf_tier,
                                     dom_game_budget_profile *out_profile);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_GAME_BUDGETS_H */
