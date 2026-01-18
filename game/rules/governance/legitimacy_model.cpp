/*
FILE: game/rules/governance/legitimacy_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements legitimacy state and deterministic event scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Legitimacy updates are deterministic.
*/
#include "dominium/rules/governance/legitimacy_model.h"

#include <string.h>

void legitimacy_registry_init(legitimacy_registry* reg,
                              legitimacy_state* storage,
                              u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(legitimacy_state) * (size_t)capacity);
    }
}

static u32 legitimacy_find_index(const legitimacy_registry* reg,
                                 u64 legitimacy_id,
                                 int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->states) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->states[i].legitimacy_id == legitimacy_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].legitimacy_id > legitimacy_id) {
            break;
        }
    }
    return i;
}

int legitimacy_register(legitimacy_registry* reg,
                        u64 legitimacy_id,
                        u32 start_value,
                        u32 max_value,
                        u32 stable_threshold,
                        u32 contested_threshold,
                        u32 failed_threshold)
{
    int found = 0;
    u32 idx;
    u32 i;
    legitimacy_state* entry;
    if (!reg || !reg->states) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = legitimacy_find_index(reg, legitimacy_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    entry->legitimacy_id = legitimacy_id;
    entry->max_value = (max_value == 0u) ? LEGITIMACY_SCALE : max_value;
    entry->value = start_value;
    if (entry->value > entry->max_value) {
        entry->value = entry->max_value;
    }
    entry->stable_threshold = stable_threshold;
    entry->contested_threshold = contested_threshold;
    entry->failed_threshold = failed_threshold;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

legitimacy_state* legitimacy_find(legitimacy_registry* reg, u64 legitimacy_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = legitimacy_find_index(reg, legitimacy_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

int legitimacy_apply_delta(legitimacy_state* state, i32 delta)
{
    i32 next;
    if (!state) {
        return -1;
    }
    next = (i32)state->value + delta;
    if (next < 0) {
        next = 0;
    }
    if ((u32)next > state->max_value) {
        next = (i32)state->max_value;
    }
    state->value = (u32)next;
    return 0;
}

int legitimacy_is_failed(const legitimacy_state* state)
{
    if (!state) {
        return 1;
    }
    return (state->value <= state->failed_threshold);
}

static dom_act_time_t legitimacy_due_next_tick(void* user, dom_act_time_t now_tick)
{
    legitimacy_due_user* due = (legitimacy_due_user*)user;
    (void)now_tick;
    if (!due || !due->event) {
        return DG_DUE_TICK_NONE;
    }
    return due->event->trigger_act;
}

static int legitimacy_due_process_until(void* user, dom_act_time_t target_tick)
{
    legitimacy_due_user* due = (legitimacy_due_user*)user;
    legitimacy_scheduler* sched;
    legitimacy_state* state;
    if (!due || !due->scheduler || !due->event) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->event->trigger_act == DG_DUE_TICK_NONE ||
        due->event->trigger_act > target_tick) {
        return DG_DUE_OK;
    }
    state = legitimacy_find(sched->registry, due->event->legitimacy_id);
    if (state) {
        (void)legitimacy_apply_delta(state, due->event->delta);
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    due->event->trigger_act = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static dg_due_vtable g_legitimacy_due_vtable = {
    legitimacy_due_next_tick,
    legitimacy_due_process_until
};

int legitimacy_scheduler_init(legitimacy_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              legitimacy_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              legitimacy_event* events,
                              u32 events_capacity,
                              legitimacy_registry* registry,
                              u64 start_event_id)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !events || !registry) {
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
    sched->events = events;
    sched->event_capacity = events_capacity;
    sched->event_count = 0u;
    sched->next_event_id = start_event_id ? start_event_id : 1u;
    sched->registry = registry;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(events, 0, sizeof(legitimacy_event) * (size_t)events_capacity);
    memset(user_storage, 0, sizeof(legitimacy_due_user) * (size_t)entry_capacity);
    return 0;
}

static int legitimacy_scheduler_alloc_handle(legitimacy_scheduler* sched, u32* out_handle)
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

int legitimacy_schedule_event(legitimacy_scheduler* sched,
                              u64 legitimacy_id,
                              i32 delta,
                              dom_act_time_t trigger_act)
{
    u32 i;
    u32 handle;
    legitimacy_event* ev;
    legitimacy_due_user* due;
    if (!sched || !sched->events) {
        return -1;
    }
    if (sched->event_count >= sched->event_capacity) {
        return -2;
    }
    for (i = 0u; i < sched->event_capacity; ++i) {
        if (sched->events[i].event_id == 0u) {
            ev = &sched->events[i];
            ev->event_id = sched->next_event_id++;
            ev->legitimacy_id = legitimacy_id;
            ev->delta = delta;
            ev->trigger_act = trigger_act;
            break;
        }
    }
    if (i >= sched->event_capacity) {
        return -3;
    }
    if (legitimacy_scheduler_alloc_handle(sched, &handle) != 0) {
        ev->event_id = 0u;
        return -4;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->event = ev;
    if (dg_due_scheduler_register(&sched->due, &g_legitimacy_due_vtable, due,
                                  ev->event_id, &handle) != DG_DUE_OK) {
        ev->event_id = 0u;
        return -5;
    }
    sched->event_count += 1u;
    return 0;
}

int legitimacy_scheduler_advance(legitimacy_scheduler* sched,
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

dom_act_time_t legitimacy_scheduler_next_due(const legitimacy_scheduler* sched)
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
