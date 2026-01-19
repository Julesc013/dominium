/*
FILE: game/agents/doctrine.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements doctrine registries and selection logic.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Selection and priority modifiers are deterministic.
*/
#include "dominium/agents/doctrine.h"

#include <string.h>

void agent_doctrine_registry_init(agent_doctrine_registry* reg,
                                  agent_doctrine* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->doctrines = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_doctrine) * (size_t)capacity);
    }
}

static u32 agent_doctrine_find_index(const agent_doctrine_registry* reg,
                                     u64 doctrine_id,
                                     int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->doctrines) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->doctrines[i].doctrine_id == doctrine_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->doctrines[i].doctrine_id > doctrine_id) {
            break;
        }
    }
    return i;
}

agent_doctrine* agent_doctrine_find(agent_doctrine_registry* reg,
                                    u64 doctrine_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->doctrines) {
        return 0;
    }
    idx = agent_doctrine_find_index(reg, doctrine_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->doctrines[idx];
}

static void agent_doctrine_copy(agent_doctrine* dst, const agent_doctrine* src)
{
    if (!dst || !src) {
        return;
    }
    *dst = *src;
    if (dst->next_due_tick == 0u) {
        dst->next_due_tick = DOM_TIME_ACT_MAX;
    }
    if (dst->provenance_ref == 0u) {
        dst->provenance_ref = dst->doctrine_id;
    }
}

int agent_doctrine_register(agent_doctrine_registry* reg,
                            const agent_doctrine* doctrine)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_doctrine* entry;
    if (!reg || !reg->doctrines || !doctrine || doctrine->doctrine_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_doctrine_find_index(reg, doctrine->doctrine_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->doctrines[i] = reg->doctrines[i - 1u];
    }
    entry = &reg->doctrines[idx];
    memset(entry, 0, sizeof(*entry));
    agent_doctrine_copy(entry, doctrine);
    reg->count += 1u;
    return 0;
}

int agent_doctrine_update(agent_doctrine_registry* reg,
                          const agent_doctrine* doctrine)
{
    agent_doctrine* entry;
    if (!reg || !doctrine || doctrine->doctrine_id == 0u) {
        return -1;
    }
    entry = agent_doctrine_find(reg, doctrine->doctrine_id);
    if (!entry) {
        return agent_doctrine_register(reg, doctrine);
    }
    agent_doctrine_copy(entry, doctrine);
    return 0;
}

int agent_doctrine_remove(agent_doctrine_registry* reg,
                          u64 doctrine_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->doctrines) {
        return -1;
    }
    idx = agent_doctrine_find_index(reg, doctrine_id, &found);
    if (!found) {
        return -2;
    }
    for (i = idx; i + 1u < reg->count; ++i) {
        reg->doctrines[i] = reg->doctrines[i + 1u];
    }
    reg->count -= 1u;
    if (reg->count < reg->capacity) {
        memset(&reg->doctrines[reg->count], 0, sizeof(agent_doctrine));
    }
    return 0;
}

int agent_doctrine_is_authorized(const agent_doctrine* doctrine,
                                 const agent_doctrine_binding* binding,
                                 agent_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!doctrine || !binding) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
        }
        return 0;
    }
    if ((binding->authority_mask & doctrine->authority_required_mask) !=
        doctrine->authority_required_mask) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
        }
        return 0;
    }
    if (doctrine->legitimacy_min > 0u &&
        binding->legitimacy_value < doctrine->legitimacy_min) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
        }
        return 0;
    }
    return 1;
}

int agent_doctrine_allows_goal(const agent_doctrine* doctrine,
                               u32 goal_type)
{
    u32 bit;
    if (!doctrine) {
        return 1;
    }
    if (goal_type >= AGENT_GOAL_TYPE_COUNT) {
        return 0;
    }
    bit = AGENT_GOAL_BIT(goal_type);
    if (doctrine->forbidden_goal_types & bit) {
        return 0;
    }
    if (doctrine->allowed_goal_types != 0u &&
        (doctrine->allowed_goal_types & bit) == 0u) {
        return 0;
    }
    return 1;
}

u32 agent_doctrine_apply_priority(const agent_doctrine* doctrine,
                                  u32 goal_type,
                                  u32 base_priority)
{
    i32 modifier = 0;
    i32 next;
    if (goal_type >= AGENT_GOAL_TYPE_COUNT) {
        return base_priority;
    }
    if (doctrine) {
        modifier = doctrine->priority_modifiers[goal_type];
    }
    next = (i32)base_priority + modifier;
    if (next < 0) {
        next = 0;
    }
    if (next > (i32)AGENT_PRIORITY_SCALE) {
        next = (i32)AGENT_PRIORITY_SCALE;
    }
    return (u32)next;
}

dom_act_time_t agent_doctrine_next_think_act(const agent_doctrine* doctrine,
                                             dom_act_time_t last_act,
                                             dom_act_time_t desired_act)
{
    dom_act_time_t next = desired_act;
    if (!doctrine) {
        return desired_act;
    }
    if ((doctrine->scheduling_policy & DOCTRINE_SCHED_INTERVAL) != 0 &&
        doctrine->min_think_interval_act > 0u) {
        dom_act_time_t min_next = last_act + doctrine->min_think_interval_act;
        if (next < min_next) {
            next = min_next;
        }
    }
    if ((doctrine->scheduling_policy & DOCTRINE_SCHED_WINDOW) != 0 &&
        doctrine->window_start_act > 0u && doctrine->window_end_act > 0u) {
        if (next < doctrine->window_start_act) {
            next = doctrine->window_start_act;
        } else if (next > doctrine->window_end_act) {
            next = doctrine->window_end_act;
        }
    }
    return next;
}

const agent_doctrine* agent_doctrine_select(const agent_doctrine_registry* reg,
                                            const agent_doctrine_binding* binding,
                                            dom_act_time_t now_act,
                                            agent_refusal_code* out_refusal)
{
    const u64 candidates[5] = {
        binding ? binding->explicit_doctrine_ref : 0u,
        binding ? binding->role_doctrine_ref : 0u,
        binding ? binding->org_doctrine_ref : 0u,
        binding ? binding->jurisdiction_doctrine_ref : 0u,
        binding ? binding->personal_doctrine_ref : 0u
    };
    u32 i;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
    }
    if (!reg || !binding) {
        return 0;
    }
    for (i = 0u; i < 5u; ++i) {
        u64 ref = candidates[i];
        const agent_doctrine* doctrine;
        if (ref == 0u) {
            continue;
        }
        doctrine = agent_doctrine_find((agent_doctrine_registry*)reg, ref);
        if (!doctrine) {
            continue;
        }
        if (doctrine->expiry_act != 0u && doctrine->expiry_act <= now_act) {
            continue;
        }
        if (!agent_doctrine_is_authorized(doctrine, binding, out_refusal)) {
            return 0;
        }
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_NONE;
        }
        return doctrine;
    }
    return 0;
}
