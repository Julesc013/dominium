/*
FILE: include/dominium/rules/scale/relevance_transitions.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Interest relevance transitions and request generation helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: All transitions and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_RELEVANCE_TRANSITIONS_H
#define DOMINIUM_RULES_SCALE_RELEVANCE_TRANSITIONS_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/interest_set.h"
#include "dominium/interest_sources.h"
#include "dominium/fidelity.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_interest_source_kind {
    DOM_INTEREST_SOURCE_PLAYER_FOCUS = 0,
    DOM_INTEREST_SOURCE_COMMAND_INTENT = 1,
    DOM_INTEREST_SOURCE_LOGISTICS = 2,
    DOM_INTEREST_SOURCE_SENSOR_COMMS = 3,
    DOM_INTEREST_SOURCE_HAZARD_CONFLICT = 4,
    DOM_INTEREST_SOURCE_GOVERNANCE_SCOPE = 5,
    DOM_INTEREST_SOURCE_COUNT = 6
} dom_interest_source_kind;

typedef struct dom_interest_runtime_state {
    dom_interest_set*         scratch_set;
    dom_interest_set*         merged_set;
    dom_interest_state*       relevance_states;
    u32                       relevance_count;
    dom_interest_transition*  transitions;
    u32                       transition_count;
    u32                       transition_capacity;
    dom_fidelity_request*     fidelity_requests;
    u32                       request_count;
    u32                       request_capacity;
    u32                       source_cursor[DOM_INTEREST_SOURCE_COUNT];
} dom_interest_runtime_state;

void dom_interest_runtime_reset(dom_interest_runtime_state* state);
void dom_interest_runtime_advance_cursor(dom_interest_runtime_state* state,
                                         dom_interest_source_kind source_kind,
                                         u32 count);

int dom_interest_collect_slice(dom_interest_runtime_state* state,
                               const dom_interest_source_list* list,
                               dom_interest_reason reason,
                               u32 start_index,
                               u32 count,
                               dom_act_time_t now_tick);

int dom_interest_merge_sets(dom_interest_runtime_state* state);

u32 dom_interest_apply_hysteresis(dom_interest_runtime_state* state,
                                  const dom_interest_policy* policy,
                                  dom_act_time_t now_tick);

u32 dom_interest_build_fidelity_requests(dom_interest_runtime_state* state,
                                         dom_fidelity_tier refine_tier,
                                         dom_fidelity_tier collapse_tier,
                                         u32 reason);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_RELEVANCE_TRANSITIONS_H */
