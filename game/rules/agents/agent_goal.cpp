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
        case AGENT_REFUSAL_CONSTRAINT_DENIED: return "constraint_denied";
        case AGENT_REFUSAL_CONTRACT_VIOLATION: return "contract_violation";
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
                                 u64 agent_id,
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
        const agent_goal* g = &reg->goals[i];
        if (g->agent_id == agent_id && g->goal_id == goal_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (g->agent_id > agent_id ||
            (g->agent_id == agent_id && g->goal_id > goal_id)) {
            break;
        }
    }
    return i;
}

agent_goal* agent_goal_find(agent_goal_registry* reg,
                            u64 goal_id)
{
    u32 i;
    if (!reg || !reg->goals) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->goals[i].goal_id == goal_id) {
            return &reg->goals[i];
        }
    }
    return 0;
}

int agent_goal_register(agent_goal_registry* reg,
                        const agent_goal_desc* desc,
                        u64* out_goal_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_goal* entry;
    u64 goal_id;
    u64 agent_id;
    if (out_goal_id) {
        *out_goal_id = 0u;
    }
    if (!reg || !reg->goals || !desc) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    agent_id = desc->agent_id;
    goal_id = desc->goal_id;
    if (agent_id == 0u) {
        return -3;
    }
    if (goal_id == 0u) {
        goal_id = reg->next_goal_id++;
        if (goal_id == 0u) {
            goal_id = reg->next_goal_id++;
        }
    }
    idx = agent_goal_find_index(reg, agent_id, goal_id, &found);
    if (found) {
        return -4;
    }
    for (i = reg->count; i > idx; --i) {
        reg->goals[i] = reg->goals[i - 1u];
    }
    entry = &reg->goals[idx];
    memset(entry, 0, sizeof(*entry));
    entry->goal_id = goal_id;
    entry->agent_id = agent_id;
    entry->type = desc->type;
    entry->base_priority = (desc->base_priority > AGENT_PRIORITY_SCALE) ? AGENT_PRIORITY_SCALE : desc->base_priority;
    entry->urgency = (desc->urgency > AGENT_PRIORITY_SCALE) ? AGENT_PRIORITY_SCALE : desc->urgency;
    entry->acceptable_risk_q16 = desc->acceptable_risk_q16;
    entry->horizon_act = desc->horizon_act;
    entry->epistemic_confidence_q16 = (desc->epistemic_confidence_q16 > AGENT_CONFIDENCE_MAX)
        ? AGENT_CONFIDENCE_MAX : desc->epistemic_confidence_q16;
    entry->condition_count = 0u;
    if (desc->conditions && desc->condition_count > 0u) {
        u32 count = desc->condition_count;
        if (count > AGENT_GOAL_MAX_CONDITIONS) {
            count = AGENT_GOAL_MAX_CONDITIONS;
        }
        memcpy(entry->conditions, desc->conditions, sizeof(agent_goal_condition) * (size_t)count);
        entry->condition_count = count;
    }
    entry->preconditions = desc->preconditions;
    entry->satisfaction_flags = desc->satisfaction_flags;
    entry->expiry_act = desc->expiry_act;
    entry->status = AGENT_GOAL_ACTIVE;
    entry->failure_count = 0u;
    entry->oscillation_count = 0u;
    entry->abandon_after_failures = desc->abandon_after_failures;
    entry->abandon_after_act = desc->abandon_after_act;
    entry->defer_until_act = 0u;
    entry->conflict_group = desc->conflict_group;
    entry->flags = desc->flags;
    entry->last_update_act = 0u;
    reg->count += 1u;
    if (out_goal_id) {
        *out_goal_id = goal_id;
    }
    return 0;
}

int agent_goal_set_status(agent_goal* goal,
                          u32 status,
                          dom_act_time_t now_act)
{
    if (!goal) {
        return -1;
    }
    goal->status = status;
    goal->last_update_act = now_act;
    return 0;
}

int agent_goal_record_failure(agent_goal* goal,
                              dom_act_time_t now_act)
{
    if (!goal) {
        return -1;
    }
    if (goal->status == AGENT_GOAL_ABANDONED || goal->status == AGENT_GOAL_SATISFIED) {
        return 0;
    }
    goal->failure_count += 1u;
    goal->last_update_act = now_act;
    if (goal->abandon_after_failures > 0u &&
        goal->failure_count >= goal->abandon_after_failures) {
        goal->status = AGENT_GOAL_ABANDONED;
    } else {
        goal->status = AGENT_GOAL_DEFERRED;
        goal->defer_until_act = (now_act == DOM_TIME_ACT_MAX) ? now_act : (now_act + 1u);
    }
    return 0;
}

int agent_goal_record_oscillation(agent_goal* goal,
                                  dom_act_time_t now_act)
{
    if (!goal) {
        return -1;
    }
    goal->oscillation_count += 1u;
    goal->last_update_act = now_act;
    return 0;
}
