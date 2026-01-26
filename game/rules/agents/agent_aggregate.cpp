/*
FILE: game/agents/agent_aggregate.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements aggregate agent registries and helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Registry ordering is deterministic by aggregate_agent_id.
*/
#include "dominium/agents/agent_aggregate.h"

#include <string.h>

void agent_aggregate_registry_init(agent_aggregate_registry* reg,
                                   aggregate_agent* storage,
                                   u32 capacity,
                                   u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->agents = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_aggregate_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(aggregate_agent) * (size_t)capacity);
    }
}

static u32 agent_aggregate_find_index(const agent_aggregate_registry* reg,
                                      u64 aggregate_agent_id,
                                      int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->agents) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->agents[i].aggregate_agent_id == aggregate_agent_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->agents[i].aggregate_agent_id > aggregate_agent_id) {
            break;
        }
    }
    return i;
}

aggregate_agent* agent_aggregate_find(agent_aggregate_registry* reg,
                                      u64 aggregate_agent_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->agents) {
        return 0;
    }
    idx = agent_aggregate_find_index(reg, aggregate_agent_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->agents[idx];
}

int agent_aggregate_register(agent_aggregate_registry* reg,
                             u64 aggregate_agent_id,
                             u64 cohort_ref,
                             u64 doctrine_ref,
                             u32 cohort_count,
                             u64 provenance_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    aggregate_agent* entry;
    if (!reg || !reg->agents) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    if (aggregate_agent_id == 0u) {
        aggregate_agent_id = reg->next_aggregate_id++;
        if (aggregate_agent_id == 0u) {
            aggregate_agent_id = reg->next_aggregate_id++;
        }
    }
    idx = agent_aggregate_find_index(reg, aggregate_agent_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->agents[i] = reg->agents[i - 1u];
    }
    entry = &reg->agents[idx];
    memset(entry, 0, sizeof(*entry));
    entry->aggregate_agent_id = aggregate_agent_id;
    entry->cohort_ref = cohort_ref;
    entry->doctrine_ref = doctrine_ref;
    entry->cohort_count = cohort_count;
    entry->refined_count = 0u;
    entry->next_think_act = DOM_TIME_ACT_MAX;
    entry->provenance_ref = provenance_ref ? provenance_ref : aggregate_agent_id;
    reg->count += 1u;
    return 0;
}

int agent_aggregate_set_counts(aggregate_agent* agg,
                               u32 cohort_count,
                               u32 refined_count,
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
    if (refined_count > cohort_count) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_REFINEMENT_LIMIT_REACHED;
        }
        return -2;
    }
    agg->cohort_count = cohort_count;
    agg->refined_count = refined_count;
    return 0;
}

int agent_aggregate_refresh_from_individuals(aggregate_agent* agg,
                                             const agent_belief_state* beliefs,
                                             u32 belief_count,
                                             const agent_goal_status_entry* goals,
                                             u32 goal_count)
{
    if (!agg) {
        return -1;
    }
    (void)aggregate_beliefs_from_states(beliefs, belief_count, &agg->belief_summary);
    (void)aggregate_goals_from_status(goals, goal_count, &agg->goal_summary);
    agg->cohort_count = belief_count;
    if (agg->refined_count > belief_count) {
        agg->refined_count = belief_count;
    }
    return 0;
}

int agent_aggregate_make_context(const aggregate_agent* agg,
                                 agent_context* out_ctx)
{
    if (!agg || !out_ctx) {
        return -1;
    }
    memset(out_ctx, 0, sizeof(*out_ctx));
    out_ctx->agent_id = agg->aggregate_agent_id;
    out_ctx->knowledge_mask = agg->belief_summary.knowledge_mask;
    out_ctx->hunger_level = agg->belief_summary.hunger_avg;
    out_ctx->threat_level = agg->belief_summary.threat_avg;
    out_ctx->explicit_doctrine_ref = agg->doctrine_ref;
    return 0;
}
