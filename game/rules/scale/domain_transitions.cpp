/*
FILE: game/rules/scale/domain_transitions.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Implements deterministic domain transitions and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Transition ordering and processing are deterministic.
*/
#include "dominium/rules/scale/domain_transitions.h"

#include <string.h>

void scale_transition_registry_init(scale_transition_registry* reg,
                                    scale_domain_transition* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->transitions = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(scale_domain_transition) * (size_t)capacity);
    }
}

static u32 scale_transition_find_index(const scale_transition_registry* reg,
                                       u64 transition_id,
                                       int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->transitions) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->transitions[i].transition_id == transition_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->transitions[i].transition_id > transition_id) {
            break;
        }
    }
    return i;
}

int scale_transition_register(scale_transition_registry* reg,
                              u64 transition_id,
                              u64 src_domain_id,
                              u64 dst_domain_id,
                              dom_act_time_t departure_act,
                              dom_act_time_t arrival_act,
                              u32 resource_cost,
                              u64 provenance_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    scale_domain_transition* entry;
    if (!reg || !reg->transitions) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = scale_transition_find_index(reg, transition_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->transitions[i] = reg->transitions[i - 1u];
    }
    entry = &reg->transitions[idx];
    memset(entry, 0, sizeof(*entry));
    entry->transition_id = transition_id;
    entry->src_domain_id = src_domain_id;
    entry->dst_domain_id = dst_domain_id;
    entry->departure_act = departure_act;
    entry->arrival_act = arrival_act;
    entry->resource_cost = resource_cost;
    entry->provenance_ref = provenance_ref;
    entry->next_due_tick = arrival_act;
    entry->status = SCALE_TRANSITION_PENDING;
    reg->count += 1u;
    return 0;
}

scale_domain_transition* scale_transition_find(scale_transition_registry* reg,
                                               u64 transition_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->transitions) {
        return 0;
    }
    idx = scale_transition_find_index(reg, transition_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->transitions[idx];
}

static dom_act_time_t transition_due_next_tick(void* user, dom_act_time_t now_tick)
{
    scale_transition_due_user* due = (scale_transition_due_user*)user;
    (void)now_tick;
    if (!due || !due->transition) {
        return DG_DUE_TICK_NONE;
    }
    if (due->transition->status != SCALE_TRANSITION_PENDING) {
        return DG_DUE_TICK_NONE;
    }
    return due->transition->next_due_tick;
}

static int transition_due_process_until(void* user, dom_act_time_t target_tick)
{
    scale_transition_due_user* due = (scale_transition_due_user*)user;
    scale_transition_scheduler* sched;
    scale_domain_transition* transition;

    if (!due || !due->scheduler || !due->transition) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    transition = due->transition;
    if (transition->status != SCALE_TRANSITION_PENDING) {
        return DG_DUE_OK;
    }
    if (transition->next_due_tick == DG_DUE_TICK_NONE ||
        transition->next_due_tick > target_tick) {
        return DG_DUE_OK;
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    transition->status = SCALE_TRANSITION_ARRIVED;
    transition->next_due_tick = DG_DUE_TICK_NONE;
    if (sched->hook.on_arrival) {
        (void)sched->hook.on_arrival(sched->hook.user, transition);
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_transition_due_vtable = {
    transition_due_next_tick,
    transition_due_process_until
};

int scale_transition_scheduler_init(scale_transition_scheduler* sched,
                                    dom_time_event* event_storage,
                                    u32 event_capacity,
                                    dg_due_entry* entry_storage,
                                    scale_transition_due_user* user_storage,
                                    u32 entry_capacity,
                                    dom_act_time_t start_tick,
                                    scale_transition_registry* registry)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !registry) {
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
    sched->registry = registry;
    sched->hook.on_arrival = 0;
    sched->hook.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(scale_transition_due_user) * (size_t)entry_capacity);
    return 0;
}

void scale_transition_set_hook(scale_transition_scheduler* sched,
                               const scale_transition_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->hook = *hook;
    } else {
        sched->hook.on_arrival = 0;
        sched->hook.user = 0;
    }
}

static int scale_transition_alloc_handle(scale_transition_scheduler* sched,
                                         u32* out_handle)
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

int scale_transition_scheduler_register(scale_transition_scheduler* sched,
                                        scale_domain_transition* transition)
{
    u32 handle;
    scale_transition_due_user* due;
    if (!sched || !transition) {
        return -1;
    }
    if (scale_transition_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (transition->next_due_tick == DOM_TIME_ACT_MAX) {
        transition->next_due_tick = transition->arrival_act;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->transition = transition;
    if (dg_due_scheduler_register(&sched->due, &g_transition_due_vtable, due,
                                  transition->transition_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int scale_transition_scheduler_advance(scale_transition_scheduler* sched,
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

dom_act_time_t scale_transition_scheduler_next_due(const scale_transition_scheduler* sched)
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
