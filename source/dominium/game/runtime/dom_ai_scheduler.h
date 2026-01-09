/*
FILE: source/dominium/game/runtime/dom_ai_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_scheduler
RESPONSIBILITY: Budgeted, deterministic AI scheduler for faction planners.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_AI_SCHEDULER_H
#define DOM_AI_SCHEDULER_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_AI_SCHEDULER_OK = 0,
    DOM_AI_SCHEDULER_ERR = -1,
    DOM_AI_SCHEDULER_INVALID_ARGUMENT = -2
};

enum {
    DOM_AI_SCHEDULER_CONFIG_VERSION = 1u
};

enum dom_ai_reason_code {
    DOM_AI_REASON_NONE = 0u,
    DOM_AI_REASON_ACTIONS = 1u,
    DOM_AI_REASON_BUDGET_HIT = 2u,
    DOM_AI_REASON_INVALID_INPUT = 3u
};

typedef struct dom_ai_scheduler_config {
    u32 struct_size;
    u32 struct_version;
    u32 period_ticks;
    u32 max_ops_per_tick;
    u32 max_factions_per_tick;
    u32 enable_traces;
} dom_ai_scheduler_config;

typedef struct dom_ai_faction_state {
    u64 faction_id;
    u64 next_decision_tick;
    u64 last_plan_id;
    u32 last_output_count;
    u32 last_reason_code;
    u32 last_budget_hit;
} dom_ai_faction_state;

struct dom_game_runtime;
typedef struct dom_ai_scheduler dom_ai_scheduler;

dom_ai_scheduler *dom_ai_scheduler_create(void);
void dom_ai_scheduler_destroy(dom_ai_scheduler *sched);
int dom_ai_scheduler_init(dom_ai_scheduler *sched,
                          const dom_ai_scheduler_config *cfg);
int dom_ai_scheduler_set_budget(dom_ai_scheduler *sched,
                                u32 max_ops_per_tick,
                                u32 max_factions_per_tick);
int dom_ai_scheduler_tick(dom_ai_scheduler *sched,
                          struct dom_game_runtime *runtime,
                          u64 tick);
int dom_ai_scheduler_get_config(const dom_ai_scheduler *sched,
                                dom_ai_scheduler_config *out_cfg);
int dom_ai_scheduler_load_states(dom_ai_scheduler *sched,
                                 const dom_ai_faction_state *states,
                                 u32 count);

int dom_ai_scheduler_list_states(const dom_ai_scheduler *sched,
                                 dom_ai_faction_state *out_states,
                                 u32 max_states,
                                 u32 *out_count);
int dom_ai_scheduler_get_state(const dom_ai_scheduler *sched,
                               u64 faction_id,
                               dom_ai_faction_state *out_state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_AI_SCHEDULER_H */
