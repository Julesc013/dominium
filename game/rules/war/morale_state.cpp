/*
FILE: game/rules/war/morale_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements morale state and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Morale updates and scheduling are deterministic.
*/
#include "dominium/rules/war/morale_state.h"

#include <string.h>

void morale_registry_init(morale_registry* reg,
                          morale_state* storage,
                          u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(morale_state) * (size_t)capacity);
    }
}

static u32 morale_find_index(const morale_registry* reg,
                             u64 morale_id,
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
        if (reg->states[i].morale_id == morale_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].morale_id > morale_id) {
            break;
        }
    }
    return i;
}

int morale_register(morale_registry* reg,
                    u64 morale_id,
                    u32 morale_level,
                    const morale_modifiers* modifiers)
{
    int found = 0;
    u32 idx;
    u32 i;
    morale_state* entry;
    if (!reg || !reg->states || morale_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = morale_find_index(reg, morale_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    entry->morale_id = morale_id;
    entry->morale_level = (morale_level > MORALE_SCALE) ? MORALE_SCALE : morale_level;
    if (modifiers) {
        entry->modifiers = *modifiers;
    }
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

morale_state* morale_find(morale_registry* reg,
                          u64 morale_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = morale_find_index(reg, morale_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

int morale_apply_delta(morale_state* state,
                       i32 delta)
{
    i32 next;
    if (!state) {
        return -1;
    }
    next = (i32)state->morale_level + delta;
    if (next < 0) {
        next = 0;
    }
    if ((u32)next > MORALE_SCALE) {
        next = (i32)MORALE_SCALE;
    }
    state->morale_level = (u32)next;
    return 0;
}

int morale_set_modifiers(morale_state* state,
                         const morale_modifiers* modifiers)
{
    if (!state || !modifiers) {
        return -1;
    }
    state->modifiers = *modifiers;
    return 0;
}

static void morale_recompute_next_due(morale_scheduler* sched,
                                      morale_state* state)
{
    u32 i;
    dom_act_time_t next = DOM_TIME_ACT_MAX;
    if (!sched || !state || !sched->events) {
        return;
    }
    for (i = 0u; i < sched->event_capacity; ++i) {
        morale_event* ev = &sched->events[i];
        if (ev->event_id == 0u) {
            continue;
        }
        if (ev->morale_id != state->morale_id) {
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

static dom_act_time_t morale_due_next_tick(void* user, dom_act_time_t now_tick)
{
    morale_due_user* due = (morale_due_user*)user;
    (void)now_tick;
    if (!due || !due->event) {
        return DG_DUE_TICK_NONE;
    }
    return due->event->trigger_act;
}

static int morale_due_process_until(void* user, dom_act_time_t target_tick)
{
    morale_due_user* due = (morale_due_user*)user;
    morale_scheduler* sched;
    morale_state* state;
    if (!due || !due->scheduler || !due->event) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->event->trigger_act == DG_DUE_TICK_NONE ||
        due->event->trigger_act > target_tick) {
        return DG_DUE_OK;
    }
    state = morale_find(sched->registry, due->event->morale_id);
    if (state) {
        if (due->event->type == MORALE_EVENT_LEGITIMACY_CHECK) {
            legitimacy_state* legit = 0;
            if (sched->legitimacy) {
                legit = legitimacy_find(sched->legitimacy, due->event->legitimacy_id);
            }
            if (!legit || legit->value < due->event->legitimacy_min) {
                (void)morale_apply_delta(state, due->event->delta);
            }
        } else {
            (void)morale_apply_delta(state, due->event->delta);
        }
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    due->event->trigger_act = DG_DUE_TICK_NONE;
    if (state) {
        morale_recompute_next_due(sched, state);
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_morale_due_vtable = {
    morale_due_next_tick,
    morale_due_process_until
};

int morale_scheduler_init(morale_scheduler* sched,
                          dom_time_event* event_storage,
                          u32 event_capacity,
                          dg_due_entry* entry_storage,
                          morale_due_user* user_storage,
                          u32 entry_capacity,
                          dom_act_time_t start_tick,
                          morale_event* events,
                          u32 events_capacity,
                          morale_registry* registry,
                          legitimacy_registry* legitimacy,
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
    sched->legitimacy = legitimacy;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(events, 0, sizeof(morale_event) * (size_t)events_capacity);
    memset(user_storage, 0, sizeof(morale_due_user) * (size_t)entry_capacity);
    return 0;
}

static int morale_scheduler_alloc_handle(morale_scheduler* sched, u32* out_handle)
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

static morale_event* morale_event_alloc(morale_scheduler* sched)
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

static int morale_schedule_event_internal(morale_scheduler* sched,
                                          morale_event* ev)
{
    u32 handle;
    morale_due_user* due;
    morale_state* state;
    if (!sched || !ev) {
        return -1;
    }
    if (morale_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->event = ev;
    if (dg_due_scheduler_register(&sched->due, &g_morale_due_vtable, due,
                                  ev->event_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    sched->event_count += 1u;
    state = morale_find(sched->registry, ev->morale_id);
    if (state) {
        morale_recompute_next_due(sched, state);
    }
    return 0;
}

int morale_schedule_event(morale_scheduler* sched,
                          u64 morale_id,
                          i32 delta,
                          dom_act_time_t trigger_act)
{
    morale_event* ev;
    if (!sched || morale_id == 0u) {
        return -1;
    }
    ev = morale_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->morale_id = morale_id;
    ev->delta = delta;
    ev->trigger_act = trigger_act;
    ev->type = MORALE_EVENT_DELTA;
    ev->provenance_ref = ev->event_id;
    if (morale_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int morale_schedule_legitimacy_check(morale_scheduler* sched,
                                     u64 morale_id,
                                     dom_act_time_t trigger_act,
                                     u64 legitimacy_id,
                                     u32 legitimacy_min,
                                     i32 delta_if_below)
{
    morale_event* ev;
    if (!sched || morale_id == 0u) {
        return -1;
    }
    ev = morale_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->morale_id = morale_id;
    ev->delta = delta_if_below;
    ev->trigger_act = trigger_act;
    ev->type = MORALE_EVENT_LEGITIMACY_CHECK;
    ev->legitimacy_id = legitimacy_id;
    ev->legitimacy_min = legitimacy_min;
    ev->provenance_ref = ev->event_id;
    if (morale_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int morale_scheduler_advance(morale_scheduler* sched,
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

dom_act_time_t morale_scheduler_next_due(const morale_scheduler* sched)
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
