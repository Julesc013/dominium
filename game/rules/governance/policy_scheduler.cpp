/*
FILE: game/rules/governance/policy_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements event-driven policy scheduler and hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Policy scheduling is deterministic.
*/
#include "dominium/rules/governance/policy_scheduler.h"

#include <string.h>

static dom_act_time_t policy_due_next_tick(void* user, dom_act_time_t now_tick)
{
    policy_due_user* due = (policy_due_user*)user;
    if (!due || !due->policy) {
        return DG_DUE_TICK_NONE;
    }
    return policy_next_due(due->policy, now_tick);
}

static int policy_due_process_until(void* user, dom_act_time_t target_tick)
{
    policy_due_user* due = (policy_due_user*)user;
    policy_scheduler* sched;
    policy_record* policy;
    jurisdiction_record* juris;
    legitimacy_state* legitimacy;
    enforcement_capacity* capacity;
    dom_act_time_t next_tick;

    if (!due || !due->scheduler || !due->policy) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    policy = due->policy;
    next_tick = policy_next_due(policy, sched->due.current_tick);
    if (next_tick == DG_DUE_TICK_NONE || next_tick > target_tick) {
        return DG_DUE_OK;
    }
    juris = jurisdiction_find(sched->jurisdictions, policy->jurisdiction_id);
    if (!juris) {
        policy->next_due_tick = DG_DUE_TICK_NONE;
        return DG_DUE_OK;
    }
    legitimacy = legitimacy_find(sched->legitimacies, juris->legitimacy_ref);
    capacity = enforcement_capacity_find(sched->enforcement, juris->enforcement_capacity_ref);
    if (legitimacy && legitimacy->value < policy->legitimacy_min) {
        policy->next_due_tick = next_tick + policy->schedule.interval_act;
        return DG_DUE_OK;
    }
    if (capacity && capacity->available_enforcers < policy->capacity_min) {
        policy->next_due_tick = next_tick + policy->schedule.interval_act;
        return DG_DUE_OK;
    }
    if (sched->hook.apply) {
        (void)sched->hook.apply(sched->hook.user, juris, policy, next_tick);
    }
    policy->next_due_tick = next_tick + policy->schedule.interval_act;
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    return DG_DUE_OK;
}

static dg_due_vtable g_policy_due_vtable = {
    policy_due_next_tick,
    policy_due_process_until
};

int policy_scheduler_init(policy_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          policy_due_user* user_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick,
                          policy_registry* policies,
                          jurisdiction_registry* jurisdictions,
                          legitimacy_registry* legitimacies,
                          enforcement_capacity_registry* enforcement)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !policies || !jurisdictions || !legitimacies || !enforcement) {
        return -1;
    }
    rc = dg_due_scheduler_init(&sched->due,
                               event_storage,
                               event_capacity,
                               entry_storage,
                               entry_capacity,
                               start_tick);
    if (rc != DG_DUE_OK) {
        return -2;
    }
    sched->due_events = event_storage;
    sched->due_entries = entry_storage;
    sched->due_users = user_storage;
    sched->policies = policies;
    sched->jurisdictions = jurisdictions;
    sched->legitimacies = legitimacies;
    sched->enforcement = enforcement;
    sched->hook.apply = 0;
    sched->hook.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(policy_due_user) * (size_t)entry_capacity);
    return 0;
}

void policy_scheduler_set_hook(policy_scheduler* sched, const policy_event_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->hook = *hook;
    } else {
        sched->hook.apply = 0;
        sched->hook.user = 0;
    }
}

static int policy_scheduler_alloc_handle(policy_scheduler* sched, u32* out_handle)
{
    u32 i;
    if (!sched || !sched->due.entries || !out_handle) {
        return -1;
    }
    for (i = 0u; i < sched->due.entry_capacity; ++i) {
        if (!sched->due.entries[i].in_use) {
            *out_handle = i;
            return 0;
        }
    }
    return -2;
}

int policy_scheduler_register(policy_scheduler* sched,
                              policy_record* policy)
{
    u32 handle;
    policy_due_user* due;
    if (!sched || !policy) {
        return -1;
    }
    if (policy_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->policy = policy;
    if (dg_due_scheduler_register(&sched->due, &g_policy_due_vtable, due,
                                  policy->policy_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int policy_scheduler_advance(policy_scheduler* sched,
                             dom_act_time_t target_tick)
{
    if (!sched) {
        return -1;
    }
    sched->processed_last = 0u;
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        return -2;
    }
    return 0;
}

dom_act_time_t policy_scheduler_next_due(const policy_scheduler* sched)
{
    dom_time_event ev;
    if (!sched) {
        return DG_DUE_TICK_NONE;
    }
    if (dom_time_event_peek(&sched->due.queue, &ev) != DOM_TIME_OK) {
        return DG_DUE_TICK_NONE;
    }
    return ev.trigger_time;
}
