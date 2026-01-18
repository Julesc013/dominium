/*
FILE: game/rules/war/readiness_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements readiness state and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Readiness updates and scheduling are deterministic.
*/
#include "dominium/rules/war/readiness_state.h"

#include <string.h>

void readiness_registry_init(readiness_registry* reg,
                             readiness_state* storage,
                             u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(readiness_state) * (size_t)capacity);
    }
}

static u32 readiness_find_index(const readiness_registry* reg,
                                u64 readiness_id,
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
        if (reg->states[i].readiness_id == readiness_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].readiness_id > readiness_id) {
            break;
        }
    }
    return i;
}

int readiness_register(readiness_registry* reg,
                       u64 readiness_id,
                       u32 readiness_level,
                       u32 degradation_rate,
                       u32 recovery_rate)
{
    int found = 0;
    u32 idx;
    u32 i;
    readiness_state* entry;
    if (!reg || !reg->states || readiness_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = readiness_find_index(reg, readiness_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    entry->readiness_id = readiness_id;
    entry->readiness_level = (readiness_level > READINESS_SCALE) ? READINESS_SCALE : readiness_level;
    entry->degradation_rate = degradation_rate;
    entry->recovery_rate = recovery_rate;
    entry->last_update_act = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

readiness_state* readiness_find(readiness_registry* reg,
                                u64 readiness_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = readiness_find_index(reg, readiness_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

int readiness_apply_delta(readiness_state* state,
                          i32 delta,
                          dom_act_time_t update_act)
{
    i32 next;
    if (!state) {
        return -1;
    }
    next = (i32)state->readiness_level + delta;
    if (next < 0) {
        next = 0;
    }
    if ((u32)next > READINESS_SCALE) {
        next = (i32)READINESS_SCALE;
    }
    state->readiness_level = (u32)next;
    state->last_update_act = update_act;
    return 0;
}

static void readiness_recompute_next_due(readiness_scheduler* sched,
                                         readiness_state* state)
{
    u32 i;
    dom_act_time_t next = DOM_TIME_ACT_MAX;
    if (!sched || !state || !sched->events) {
        return;
    }
    for (i = 0u; i < sched->event_capacity; ++i) {
        readiness_event* ev = &sched->events[i];
        if (ev->event_id == 0u) {
            continue;
        }
        if (ev->readiness_id != state->readiness_id) {
            continue;
        }
        if (ev->trigger_act == DG_DUE_TICK_NONE) {
            continue;
        }
        if (ev->trigger_act < next) {
            next = ev->trigger_act;
        }
    }
    state->next_due_tick = next;
}

static dom_act_time_t readiness_due_next_tick(void* user, dom_act_time_t now_tick)
{
    readiness_due_user* due = (readiness_due_user*)user;
    (void)now_tick;
    if (!due || !due->event) {
        return DG_DUE_TICK_NONE;
    }
    return due->event->trigger_act;
}

static int readiness_due_process_until(void* user, dom_act_time_t target_tick)
{
    readiness_due_user* due = (readiness_due_user*)user;
    readiness_scheduler* sched;
    readiness_state* state;
    int supply_ok = 0;
    if (!due || !due->scheduler || !due->event) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->event->trigger_act == DG_DUE_TICK_NONE ||
        due->event->trigger_act > target_tick) {
        return DG_DUE_OK;
    }
    state = readiness_find(sched->registry, due->event->readiness_id);
    if (state) {
        if (due->event->type == READINESS_EVENT_SUPPLY_CHECK) {
            if (sched->stores &&
                due->event->supply_store_ref != 0u &&
                due->event->supply_asset_id != 0u &&
                due->event->supply_qty > 0u) {
                if (infra_store_consume(sched->stores,
                                        due->event->supply_store_ref,
                                        due->event->supply_asset_id,
                                        due->event->supply_qty) == 0) {
                    supply_ok = 1;
                }
            }
            if (!supply_ok && due->event->delta != 0) {
                (void)readiness_apply_delta(state, due->event->delta, due->event->trigger_act);
            }
        } else {
            (void)readiness_apply_delta(state, due->event->delta, due->event->trigger_act);
        }
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    due->event->trigger_act = DG_DUE_TICK_NONE;
    if (state) {
        readiness_recompute_next_due(sched, state);
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_readiness_due_vtable = {
    readiness_due_next_tick,
    readiness_due_process_until
};

int readiness_scheduler_init(readiness_scheduler* sched,
                             dom_time_event* event_storage,
                             u32 event_capacity,
                             dg_due_entry* entry_storage,
                             readiness_due_user* user_storage,
                             u32 entry_capacity,
                             dom_act_time_t start_tick,
                             readiness_event* events,
                             u32 events_capacity,
                             readiness_registry* registry,
                             infra_store_registry* stores,
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
    sched->stores = stores;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(events, 0, sizeof(readiness_event) * (size_t)events_capacity);
    memset(user_storage, 0, sizeof(readiness_due_user) * (size_t)entry_capacity);
    return 0;
}

static int readiness_scheduler_alloc_handle(readiness_scheduler* sched, u32* out_handle)
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

static readiness_event* readiness_event_alloc(readiness_scheduler* sched)
{
    u32 i;
    if (!sched || !sched->events) {
        return 0;
    }
    if (sched->event_count >= sched->event_capacity) {
        return 0;
    }
    for (i = 0u; i < sched->event_capacity; ++i) {
        if (sched->events[i].event_id == 0u) {
            return &sched->events[i];
        }
    }
    return 0;
}

static int readiness_schedule_event_internal(readiness_scheduler* sched,
                                             readiness_event* ev)
{
    u32 handle;
    readiness_due_user* due;
    readiness_state* state;
    if (!sched || !ev) {
        return -1;
    }
    if (readiness_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->event = ev;
    if (dg_due_scheduler_register(&sched->due, &g_readiness_due_vtable, due,
                                  ev->event_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    sched->event_count += 1u;
    state = readiness_find(sched->registry, ev->readiness_id);
    if (state) {
        readiness_recompute_next_due(sched, state);
    }
    return 0;
}

int readiness_schedule_event(readiness_scheduler* sched,
                             u64 readiness_id,
                             i32 delta,
                             dom_act_time_t trigger_act)
{
    readiness_event* ev;
    if (!sched || readiness_id == 0u) {
        return -1;
    }
    ev = readiness_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->readiness_id = readiness_id;
    ev->delta = delta;
    ev->trigger_act = trigger_act;
    ev->type = READINESS_EVENT_DELTA;
    ev->provenance_ref = ev->event_id;
    if (readiness_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int readiness_schedule_supply_check(readiness_scheduler* sched,
                                    u64 readiness_id,
                                    dom_act_time_t trigger_act,
                                    u64 supply_store_ref,
                                    u64 supply_asset_id,
                                    u32 supply_qty,
                                    i32 shortage_delta)
{
    readiness_event* ev;
    if (!sched || readiness_id == 0u) {
        return -1;
    }
    ev = readiness_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->readiness_id = readiness_id;
    ev->delta = shortage_delta;
    ev->trigger_act = trigger_act;
    ev->type = READINESS_EVENT_SUPPLY_CHECK;
    ev->supply_store_ref = supply_store_ref;
    ev->supply_asset_id = supply_asset_id;
    ev->supply_qty = supply_qty;
    ev->provenance_ref = ev->event_id;
    if (readiness_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int readiness_scheduler_advance(readiness_scheduler* sched,
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

dom_act_time_t readiness_scheduler_next_due(const readiness_scheduler* sched)
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
