/*
FILE: game/agents/agent_goal.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements agent goal registries and refusal string mapping.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Goal ordering and registration are deterministic.
*/
#include "dominium/agents/agent_goal.h"

#include <string.h>

const char* agent_refusal_to_string(agent_refusal_code code)
{
    switch (code) {
        case AGENT_REFUSAL_NONE: return "none";
        case AGENT_REFUSAL_GOAL_NOT_FEASIBLE: return "goal_not_feasible";
        case AGENT_REFUSAL_INSUFFICIENT_CAPABILITY: return "insufficient_capability";
        case AGENT_REFUSAL_INSUFFICIENT_AUTHORITY: return "insufficient_authority";
        case AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE: return "insufficient_knowledge";
        case AGENT_REFUSAL_PLAN_EXPIRED: return "plan_expired";
        case AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED: return "doctrine_not_authorized";
        case AGENT_REFUSAL_GOAL_FORBIDDEN_BY_DOCTRINE: return "goal_forbidden_by_doctrine";
        case AGENT_REFUSAL_DELEGATION_EXPIRED: return "delegation_expired";
        case AGENT_REFUSAL_ROLE_MISMATCH: return "role_mismatch";
        case AGENT_REFUSAL_AGGREGATION_NOT_ALLOWED: return "aggregation_not_allowed";
        case AGENT_REFUSAL_REFINEMENT_LIMIT_REACHED: return "refinement_limit_reached";
        case AGENT_REFUSAL_COLLAPSE_BLOCKED_BY_INTEREST: return "collapse_blocked_by_interest";
        case AGENT_REFUSAL_AGENT_STATE_INCONSISTENT: return "agent_state_inconsistent";
        default: return "unknown";
    }
}

void agent_goal_registry_init(agent_goal_registry* reg,
                              agent_goal* storage,
                              u32 capacity,
                              u64 start_goal_id)
{
    if (!reg) {
        return;
    }
    reg->goals = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_goal_id = start_goal_id ? start_goal_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_goal) * (size_t)capacity);
    }
}

static u32 agent_goal_find_index(const agent_goal_registry* reg,
                                 u64 goal_id,
                                 int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->goals) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->goals[i].goal_id == goal_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->goals[i].goal_id > goal_id) {
            break;
        }
    }
    return i;
}

agent_goal* agent_goal_find(agent_goal_registry* reg,
                            u64 goal_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->goals) {
        return 0;
    }
    idx = agent_goal_find_index(reg, goal_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->goals[idx];
}

int agent_goal_register(agent_goal_registry* reg,
                        u64 goal_id,
                        u32 type,
                        u32 base_priority,
                        const agent_goal_preconditions* preconditions,
                        u32 satisfaction_flags,
                        dom_act_time_t expiry_act)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_goal* entry;
    if (!reg || !reg->goals) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    if (goal_id == 0u) {
        goal_id = reg->next_goal_id++;
        if (goal_id == 0u) {
            goal_id = reg->next_goal_id++;
        }
    }
    idx = agent_goal_find_index(reg, goal_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->goals[i] = reg->goals[i - 1u];
    }
    entry = &reg->goals[idx];
    memset(entry, 0, sizeof(*entry));
    entry->goal_id = goal_id;
    entry->type = type;
    entry->base_priority = (base_priority > AGENT_PRIORITY_SCALE) ? AGENT_PRIORITY_SCALE : base_priority;
    if (preconditions) {
        entry->preconditions = *preconditions;
    }
    entry->satisfaction_flags = satisfaction_flags;
    entry->expiry_act = expiry_act;
    reg->count += 1u;
    return 0;
}
