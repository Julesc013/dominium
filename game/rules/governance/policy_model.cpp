/*
FILE: game/rules/governance/policy_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements policy records, schedules, and standards resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Policy ordering is stable and deterministic.
*/
#include "dominium/rules/governance/policy_model.h"

#include <string.h>

void policy_registry_init(policy_registry* reg,
                          policy_record* storage,
                          u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->policies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(policy_record) * (size_t)capacity);
    }
}

static u32 policy_find_index(const policy_registry* reg,
                             u64 policy_id,
                             int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->policies) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->policies[i].policy_id == policy_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->policies[i].policy_id > policy_id) {
            break;
        }
    }
    return i;
}

int policy_register(policy_registry* reg,
                    const policy_record* policy)
{
    int found = 0;
    u32 idx;
    u32 i;
    policy_record* entry;
    if (!reg || !reg->policies || !policy) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = policy_find_index(reg, policy->policy_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->policies[i] = reg->policies[i - 1u];
    }
    entry = &reg->policies[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *policy;
    if (entry->next_due_tick == 0 && entry->schedule.start_act != 0) {
        entry->next_due_tick = DG_DUE_TICK_NONE;
    }
    reg->count += 1u;
    return 0;
}

policy_record* policy_find(policy_registry* reg, u64 policy_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->policies) {
        return 0;
    }
    idx = policy_find_index(reg, policy_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->policies[idx];
}

dom_act_time_t policy_next_due(const policy_record* policy, dom_act_time_t now_tick)
{
    if (!policy) {
        return DG_DUE_TICK_NONE;
    }
    if (policy->schedule.start_act == DG_DUE_TICK_NONE) {
        return DG_DUE_TICK_NONE;
    }
    if (policy->next_due_tick != DG_DUE_TICK_NONE) {
        if (policy->next_due_tick != 0 || policy->schedule.start_act == 0) {
            return policy->next_due_tick;
        }
    }
    if (now_tick <= policy->schedule.start_act) {
        return policy->schedule.start_act;
    }
    if (policy->schedule.interval_act == 0) {
        return policy->schedule.start_act;
    }
    {
        dom_act_time_t delta = now_tick - policy->schedule.start_act;
        dom_act_time_t steps = delta / policy->schedule.interval_act;
        return policy->schedule.start_act + (steps + 1u) * policy->schedule.interval_act;
    }
}

int policy_epistemic_knows(const governance_epistemic_set* set, u64 policy_id)
{
    u32 i;
    if (!set) {
        return 1;
    }
    if (!set->known_policy_ids || set->count == 0u) {
        return 0;
    }
    for (i = 0u; i < set->count; ++i) {
        if (set->known_policy_ids[i] == policy_id) {
            return 1;
        }
    }
    return 0;
}

u64 governance_resolve_standard(const standard_resolution_context* ctx)
{
    if (!ctx) {
        return 0u;
    }
    if (ctx->explicit_standard_id != 0u) {
        return ctx->explicit_standard_id;
    }
    if (ctx->org_standard_id != 0u) {
        return ctx->org_standard_id;
    }
    if (ctx->jurisdiction_standard_id != 0u) {
        return ctx->jurisdiction_standard_id;
    }
    if (ctx->personal_standard_id != 0u) {
        return ctx->personal_standard_id;
    }
    return ctx->fallback_standard_id;
}
