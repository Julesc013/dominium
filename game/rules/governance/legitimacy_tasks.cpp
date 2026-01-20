/*
FILE: game/rules/governance/legitimacy_tasks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance rules
RESPONSIBILITY: Implements governance task helpers for Work IR tasks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Governance ordering and updates are deterministic.
*/
#include "dominium/rules/governance/legitimacy_tasks.h"

#include <string.h>

extern "C" {

void dom_governance_audit_init(dom_governance_audit_log* log,
                               dom_governance_audit_entry* storage,
                               u32 capacity,
                               u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_governance_audit_entry) * (size_t)capacity);
    }
}

int dom_governance_audit_record(dom_governance_audit_log* log,
                                u32 kind,
                                u64 primary_id,
                                i64 amount)
{
    dom_governance_audit_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->event_id = log->next_event_id++;
    entry->kind = kind;
    entry->primary_id = primary_id;
    entry->amount = amount;
    return 0;
}

void dom_governance_runtime_reset(dom_governance_runtime_state* state)
{
    if (!state) {
        return;
    }
    state->policy_cursor = 0u;
    state->legitimacy_cursor = 0u;
    state->authority_cursor = 0u;
    state->lifecycle_cursor = 0u;
}

void dom_governance_law_registry_init(dom_governance_law_registry* reg,
                                      dom_governance_law_state* storage,
                                      u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_governance_law_state) * (size_t)capacity);
    }
}

static dom_governance_law_state* dom_governance_law_find(dom_governance_law_registry* reg,
                                                        u64 law_id,
                                                        u32* out_index)
{
    u32 i;
    if (out_index) {
        *out_index = 0u;
    }
    if (!reg || !reg->states) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->states[i].law_id == law_id) {
            if (out_index) {
                *out_index = i;
            }
            return &reg->states[i];
        }
        if (reg->states[i].law_id > law_id) {
            if (out_index) {
                *out_index = i;
            }
            return 0;
        }
    }
    if (out_index) {
        *out_index = reg->count;
    }
    return 0;
}

static dom_act_time_t dom_governance_policy_due(policy_record* policy, dom_act_time_t now_tick)
{
    dom_act_time_t next_due = policy_next_due(policy, now_tick);
    if (next_due == DG_DUE_TICK_NONE) {
        return DG_DUE_TICK_NONE;
    }
    return next_due;
}

u32 dom_governance_policy_apply_slice(policy_registry* policies,
                                      jurisdiction_registry* jurisdictions,
                                      legitimacy_registry* legitimacies,
                                      enforcement_capacity_registry* enforcement,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_act_time_t now_tick,
                                      dom_governance_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!policies || !policies->policies || max_count == 0u) {
        return 0u;
    }
    if (start_index >= policies->count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < policies->count; ++i) {
        policy_record* policy = &policies->policies[start_index + i];
        dom_act_time_t next_due = dom_governance_policy_due(policy, now_tick);
        legitimacy_state* legitimacy;
        enforcement_capacity* capacity;
        jurisdiction_record* juris;
        if (next_due == DG_DUE_TICK_NONE || next_due > now_tick) {
            continue;
        }
        juris = jurisdictions ? jurisdiction_find(jurisdictions, policy->jurisdiction_id) : 0;
        if (!juris) {
            policy->next_due_tick = DG_DUE_TICK_NONE;
            continue;
        }
        legitimacy = legitimacies ? legitimacy_find(legitimacies, juris->legitimacy_ref) : 0;
        capacity = enforcement ? enforcement_capacity_find(enforcement, juris->enforcement_capacity_ref) : 0;
        if (legitimacy && legitimacy->value < policy->legitimacy_min) {
            policy->next_due_tick = next_due + policy->schedule.interval_act;
            continue;
        }
        if (capacity && capacity->available_enforcers < policy->capacity_min) {
            policy->next_due_tick = next_due + policy->schedule.interval_act;
            continue;
        }
        if (audit) {
            (void)dom_governance_audit_record(audit, DOM_GOV_AUDIT_POLICY_APPLY, policy->policy_id, 0);
        }
        policy->next_due_tick = next_due + policy->schedule.interval_act;
        processed += 1u;
    }
    return processed;
}

u32 dom_governance_legitimacy_apply_slice(legitimacy_registry* registry,
                                          const dom_governance_legitimacy_event* events,
                                          u32 event_count,
                                          u32 start_index,
                                          u32 max_count,
                                          dom_act_time_t now_tick,
                                          dom_governance_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!registry || !events || max_count == 0u) {
        return 0u;
    }
    if (start_index >= event_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < event_count; ++i) {
        const dom_governance_legitimacy_event* ev = &events[start_index + i];
        legitimacy_state* state;
        if (ev->trigger_act > now_tick) {
            continue;
        }
        state = legitimacy_find(registry, ev->legitimacy_id);
        if (!state) {
            continue;
        }
        (void)legitimacy_apply_delta(state, ev->delta);
        if (audit) {
            (void)dom_governance_audit_record(audit, DOM_GOV_AUDIT_LEGITIMACY_UPDATE, ev->event_id, (i64)ev->delta);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_governance_authority_enforce_slice(const dom_governance_authority_action* actions,
                                           u32 action_count,
                                           u32 start_index,
                                           u32 max_count,
                                           dom_act_time_t now_tick,
                                           dom_governance_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!actions || max_count == 0u) {
        return 0u;
    }
    if (start_index >= action_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < action_count; ++i) {
        const dom_governance_authority_action* action = &actions[start_index + i];
        if (action->trigger_act > now_tick) {
            continue;
        }
        if (audit) {
            (void)dom_governance_audit_record(audit, DOM_GOV_AUDIT_AUTHORITY_ENFORCE,
                                              action->action_id, (i64)action->enforcer_cost);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_governance_law_lifecycle_slice(dom_governance_law_registry* registry,
                                       const dom_governance_law_lifecycle_event* events,
                                       u32 event_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_act_time_t now_tick,
                                       dom_governance_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!registry || !registry->states || !events || max_count == 0u) {
        return 0u;
    }
    if (start_index >= event_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < event_count; ++i) {
        const dom_governance_law_lifecycle_event* ev = &events[start_index + i];
        dom_governance_law_state* state;
        u32 insert_at = 0u;
        u32 j;
        if (ev->trigger_act > now_tick) {
            continue;
        }
        state = dom_governance_law_find(registry, ev->law_id, &insert_at);
        if (!state) {
            if (registry->count >= registry->capacity) {
                continue;
            }
            for (j = registry->count; j > insert_at; --j) {
                registry->states[j] = registry->states[j - 1u];
            }
            registry->states[insert_at].law_id = ev->law_id;
            registry->states[insert_at].state = ev->next_state;
            registry->count += 1u;
        } else {
            state->state = ev->next_state;
        }
        if (audit) {
            (void)dom_governance_audit_record(audit, DOM_GOV_AUDIT_LAW_LIFECYCLE, ev->law_id, (i64)ev->next_state);
        }
        processed += 1u;
    }
    return processed;
}

} /* extern "C" */
