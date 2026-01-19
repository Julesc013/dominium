/*
FILE: game/agents/agent_refinement.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic refinement selection and events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Selection order is stable by (role_rank desc, agent_id asc).
*/
#include "dominium/agents/agent_refinement.h"
#include "dominium/agents/agent_collapse.h"

#include <string.h>

static int agent_refinement_is_selected(const u64* selected, u32 count, u64 agent_id)
{
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (selected[i] == agent_id) {
            return 1;
        }
    }
    return 0;
}

int agent_refinement_select(const agent_refine_candidate* candidates,
                            u32 candidate_count,
                            u32 max_select,
                            u64* out_ids,
                            u32* in_out_count)
{
    u32 capacity;
    u32 selected = 0u;
    u32 i;
    if (!out_ids || !in_out_count) {
        return -1;
    }
    capacity = *in_out_count;
    *in_out_count = 0u;
    if (!candidates || candidate_count == 0u || max_select == 0u || capacity == 0u) {
        return 0;
    }
    if (max_select > capacity) {
        max_select = capacity;
    }
    for (i = 0u; i < max_select; ++i) {
        u32 j;
        u64 best_id = 0u;
        u32 best_rank = 0u;
        int found = 0;
        for (j = 0u; j < candidate_count; ++j) {
            const agent_refine_candidate* cand = &candidates[j];
            if (agent_refinement_is_selected(out_ids, selected, cand->agent_id)) {
                continue;
            }
            if (!found || cand->role_rank > best_rank ||
                (cand->role_rank == best_rank && cand->agent_id < best_id)) {
                best_id = cand->agent_id;
                best_rank = cand->role_rank;
                found = 1;
            }
        }
        if (!found) {
            break;
        }
        out_ids[selected] = best_id;
        selected += 1u;
    }
    *in_out_count = selected;
    return 0;
}

static u32 agent_refinement_spread_value(u64 agent_id, u32 min_value, u32 max_value)
{
    u32 span;
    if (max_value <= min_value) {
        return min_value;
    }
    span = max_value - min_value;
    return min_value + (u32)(agent_id % (u64)(span + 1u));
}

int agent_refinement_apply(const aggregate_belief_summary* summary,
                           const agent_refine_candidate* candidates,
                           u32 candidate_count,
                           u32 desired_count,
                           agent_belief_state* out_states,
                           u64* out_ids,
                           u32* in_out_count,
                           dom_act_time_t now_act,
                           agent_refusal_code* out_refusal)
{
    u32 capacity;
    u32 selected = 0u;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!summary || !out_states || !out_ids || !in_out_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -1;
    }
    capacity = *in_out_count;
    *in_out_count = 0u;
    if (desired_count == 0u) {
        return 0;
    }
    if (capacity < desired_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_REFINEMENT_LIMIT_REACHED;
        }
        return -2;
    }
    if (!candidates || candidate_count == 0u) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -3;
    }
    selected = capacity;
    if (selected > desired_count) {
        selected = desired_count;
    }
    if (agent_refinement_select(candidates, candidate_count, desired_count,
                                out_ids, &selected) != 0) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -4;
    }
    if (selected < desired_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_REFINEMENT_LIMIT_REACHED;
        }
        return -5;
    }
    for (capacity = 0u; capacity < selected; ++capacity) {
        u64 agent_id = out_ids[capacity];
        u32 hunger = agent_refinement_spread_value(agent_id,
                                                   summary->hunger_min,
                                                   summary->hunger_max);
        u32 threat = agent_refinement_spread_value(agent_id,
                                                   summary->threat_min,
                                                   summary->threat_max);
        agent_belief_init(&out_states[capacity],
                          agent_id,
                          summary->knowledge_any_mask,
                          hunger,
                          threat,
                          now_act);
    }
    *in_out_count = selected;
    return 0;
}

int agent_refinement_apply_to_aggregate(aggregate_agent* agg,
                                        u32 desired_count,
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
    if (desired_count > agg->cohort_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_REFINEMENT_LIMIT_REACHED;
        }
        return -2;
    }
    agg->refined_count = desired_count;
    return 0;
}

int agent_refinement_process_events(agent_aggregate_registry* aggregates,
                                    agent_refinement_event* events,
                                    u32 event_count,
                                    dom_act_time_t target_tick,
                                    agent_refusal_code* out_refusal)
{
    u32 i;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!aggregates || !events) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
        }
        return -1;
    }
    for (;;) {
        agent_refinement_event* next_event = 0;
        for (i = 0u; i < event_count; ++i) {
            agent_refinement_event* ev = &events[i];
            if (ev->trigger_act == DG_DUE_TICK_NONE || ev->trigger_act > target_tick) {
                continue;
            }
            if (!next_event ||
                ev->trigger_act < next_event->trigger_act ||
                (ev->trigger_act == next_event->trigger_act &&
                 ev->event_id < next_event->event_id)) {
                next_event = ev;
            }
        }
        if (!next_event) {
            break;
        }
        aggregate_agent* agg = agent_aggregate_find(aggregates, next_event->aggregate_agent_id);
        if (!agg) {
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_AGENT_STATE_INCONSISTENT;
            }
            return -2;
        }
        if (next_event->type == AGENT_REFINE_EVENT_REFINE) {
            if (agent_refinement_apply_to_aggregate(agg, next_event->desired_count, out_refusal) != 0) {
                return -3;
            }
        } else {
            if (agent_collapse_apply(agg, next_event->trigger_act, out_refusal) != 0) {
                return -4;
            }
        }
        next_event->trigger_act = DG_DUE_TICK_NONE;
    }
    return 0;
}
