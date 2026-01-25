/*
FILE: game/agents/delegation.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements delegation checks and cohort plan collapse.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Delegation ordering is deterministic by delegation_id.
*/
#include "dominium/agents/delegation.h"

#include <string.h>

void agent_delegation_registry_init(agent_delegation_registry* reg,
                                    agent_delegation* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->delegations = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_delegation) * (size_t)capacity);
    }
}

static u32 agent_delegation_find_index(const agent_delegation_registry* reg,
                                       u64 delegation_id,
                                       int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->delegations) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->delegations[i].delegation_id == delegation_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->delegations[i].delegation_id > delegation_id) {
            break;
        }
    }
    return i;
}

agent_delegation* agent_delegation_find(agent_delegation_registry* reg,
                                        u64 delegation_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->delegations) {
        return 0;
    }
    idx = agent_delegation_find_index(reg, delegation_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->delegations[idx];
}

agent_delegation* agent_delegation_find_for_delegatee(agent_delegation_registry* reg,
                                                      u64 delegatee_ref,
                                                      dom_act_time_t now_act)
{
    u32 i;
    if (!reg || !reg->delegations || delegatee_ref == 0u) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        agent_delegation* del = &reg->delegations[i];
        if (del->delegatee_ref != delegatee_ref) {
            continue;
        }
        if (del->expiry_act != 0u && del->expiry_act <= now_act) {
            continue;
        }
        return del;
    }
    return 0;
}

int agent_delegation_register(agent_delegation_registry* reg,
                              u64 delegation_id,
                              u64 delegator_ref,
                              u64 delegatee_ref,
                              u32 delegation_kind,
                              u32 allowed_process_mask,
                              u32 authority_mask,
                              dom_act_time_t expiry_act,
                              u64 provenance_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_delegation* entry;
    if (!reg || !reg->delegations || delegation_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_delegation_find_index(reg, delegation_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->delegations[i] = reg->delegations[i - 1u];
    }
    entry = &reg->delegations[idx];
    memset(entry, 0, sizeof(*entry));
    entry->delegation_id = delegation_id;
    entry->delegator_ref = delegator_ref;
    entry->delegatee_ref = delegatee_ref;
    entry->delegation_kind = delegation_kind;
    entry->allowed_process_mask = allowed_process_mask;
    entry->authority_mask = authority_mask;
    entry->expiry_act = expiry_act;
    entry->provenance_ref = provenance_ref ? provenance_ref : delegation_id;
    entry->revoked = 0u;
    reg->count += 1u;
    return 0;
}

int agent_delegation_revoke(agent_delegation_registry* reg,
                            u64 delegation_id)
{
    agent_delegation* entry = agent_delegation_find(reg, delegation_id);
    if (!entry) {
        return -1;
    }
    entry->revoked = 1u;
    return 0;
}

int agent_delegation_allows_process(const agent_delegation* delegation,
                                    u32 process_kind,
                                    dom_act_time_t now_act,
                                    agent_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!delegation) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return 0;
    }
    if (delegation->revoked) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return 0;
    }
    if (delegation->expiry_act != 0u && delegation->expiry_act <= now_act) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_DELEGATION_EXPIRED;
        }
        return 0;
    }
    if (process_kind == 0u || delegation->allowed_process_mask == 0u) {
        return 1;
    }
    if ((delegation->allowed_process_mask & AGENT_PROCESS_KIND_BIT(process_kind)) == 0u) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return 0;
    }
    return 1;
}

int agent_delegation_check_plan(const agent_delegation_registry* reg,
                                u64 delegatee_ref,
                                const agent_plan* plan,
                                dom_act_time_t now_act,
                                agent_refusal_code* out_refusal)
{
    u32 i;
    agent_delegation* delegation;
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!reg || !plan || delegatee_ref == 0u) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return -1;
    }
    delegation = agent_delegation_find_for_delegatee((agent_delegation_registry*)reg,
                                                     delegatee_ref, now_act);
    if (!delegation) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return -2;
    }
    for (i = 0u; i < plan->step_count; ++i) {
        if (!agent_delegation_allows_process(delegation, plan->steps[i].process_kind,
                                             now_act, &refusal)) {
            if (out_refusal) {
                *out_refusal = refusal;
            }
            return -3;
        }
    }
    return 0;
}

int agent_cohort_plan_collapse(const agent_plan* plan,
                               u32 cohort_size,
                               agent_plan* out_plan)
{
    u32 i;
    if (!plan || !out_plan || cohort_size == 0u) {
        return -1;
    }
    *out_plan = *plan;
    if (plan->estimated_cost > 0u) {
        u64 cost = (u64)plan->estimated_cost * (u64)cohort_size;
        if (cost > 0xFFFFFFFFu) {
            cost = 0xFFFFFFFFu;
        }
        out_plan->estimated_cost = (u32)cost;
    }
    for (i = 0u; i < out_plan->step_count; ++i) {
        if (out_plan->steps[i].expected_cost_units > 0u) {
            u64 cost = (u64)out_plan->steps[i].expected_cost_units * (u64)cohort_size;
            if (cost > 0xFFFFFFFFu) {
                cost = 0xFFFFFFFFu;
            }
            out_plan->steps[i].expected_cost_units = (u32)cost;
        }
    }
    return 0;
}
