/*
FILE: game/agents/agent_collapse.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic collapse logic for aggregate agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Collapse aggregation is order-independent and deterministic.
*/
#include "dominium/agents/agent_collapse.h"

#include <string.h>

int agent_collapse_check_interest(const dom_interest_set* set,
                                  u32 target_kind,
                                  u64 target_id,
                                  dom_act_time_t now_act,
                                  u32 block_threshold,
                                  agent_refusal_code* out_refusal)
{
    u32 strength = 0u;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!set || block_threshold == 0u) {
        return 0;
    }
    strength = dom_interest_set_strength(set, target_kind, target_id, now_act, 0);
    if (strength >= block_threshold) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_COLLAPSE_BLOCKED_BY_INTEREST;
        }
        return -1;
    }
    return 0;
}

int agent_collapse_apply(aggregate_agent* agg,
                         dom_act_time_t now_act,
                         agent_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!agg) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -1;
    }
    agg->refined_count = 0u;
    agg->next_think_act = now_act;
    return 0;
}

int agent_collapse_from_individuals(aggregate_agent* agg,
                                    const agent_belief_state* beliefs,
                                    u32 belief_count,
                                    const agent_goal_status_entry* goals,
                                    u32 goal_count,
                                    dom_act_time_t now_act,
                                    agent_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!agg) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -1;
    }
    if (goal_count != 0u && belief_count != 0u && goal_count != belief_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -2;
    }
    (void)aggregate_beliefs_from_states(beliefs, belief_count, &agg->belief_summary);
    (void)aggregate_goals_from_status(goals, goal_count, &agg->goal_summary);
    agg->cohort_count = belief_count;
    agg->refined_count = 0u;
    agg->next_think_act = now_act;
    return 0;
}
