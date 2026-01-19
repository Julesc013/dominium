/*
FILE: game/agents/doctrine_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements doctrine update scheduling and application.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Events are applied in stable ACT order.
*/
#include "dominium/agents/doctrine_scheduler.h"

#include <string.h>

static void doctrine_recompute_next_due(doctrine_scheduler* sched,
                                        agent_doctrine* doctrine)
{
    u32 i;
    dom_act_time_t next = DOM_TIME_ACT_MAX;
    if (!sched || !doctrine || !sched->events) {
        return;
    }
    for (i = 0u; i < sched->event_capacity; ++i) {
        doctrine_event* ev = &sched->events[i];
        if (ev->event_id == 0u) {
            continue;
        }
        if (ev->doctrine_id != doctrine->doctrine_id) {
            continue;
        }
        if (ev->trigger_act == DG_DUE_TICK_NONE) {
            continue;
        }
        if (ev->trigger_act < next) {
            next = ev->trigger_act;
        }
    }
    doctrine->next_due_tick = next;
}

static dom_act_time_t doctrine_due_next_tick(void* user, dom_act_time_t now_tick)
{
    doctrine_due_user* due = (doctrine_due_user*)user;
    (void)now_tick;
    if (!due || !due->event) {
        return DG_DUE_TICK_NONE;
    }
    return due->event->trigger_act;
}

static int doctrine_due_process_until(void* user, dom_act_time_t target_tick)
{
    doctrine_due_user* due = (doctrine_due_user*)user;
    doctrine_scheduler* sched;
    agent_doctrine* doctrine;
    if (!due || !due->scheduler || !due->event) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->event->trigger_act == DG_DUE_TICK_NONE ||
        due->event->trigger_act > target_tick) {
        return DG_DUE_OK;
    }
    if (due->event->type == DOCTRINE_EVENT_CLEAR) {
        (void)agent_doctrine_remove(sched->doctrines, due->event->doctrine_id);
    } else {
        (void)agent_doctrine_update(sched->doctrines, &due->event->doctrine);
    }
    doctrine = agent_doctrine_find(sched->doctrines, due->event->doctrine_id);
    if (doctrine) {
        doctrine_recompute_next_due(sched, doctrine);
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    due->event->trigger_act = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static dg_due_vtable g_doctrine_due_vtable = {
    doctrine_due_next_tick,
    doctrine_due_process_until
};

int doctrine_scheduler_init(doctrine_scheduler* sched,
                            dom_time_event* event_storage,
                            u32 event_capacity,
                            dg_due_entry* entry_storage,
                            doctrine_due_user* user_storage,
                            u32 entry_capacity,
                            dom_act_time_t start_tick,
                            doctrine_event* events,
                            u32 events_capacity,
                            agent_doctrine_registry* doctrines,
                            u64 start_event_id)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !events || !doctrines) {
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
    sched->doctrines = doctrines;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(events, 0, sizeof(doctrine_event) * (size_t)events_capacity);
    memset(user_storage, 0, sizeof(doctrine_due_user) * (size_t)entry_capacity);
    return 0;
}

static int doctrine_scheduler_alloc_handle(doctrine_scheduler* sched, u32* out_handle)
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

static doctrine_event* doctrine_event_alloc(doctrine_scheduler* sched)
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

static int doctrine_schedule_event_internal(doctrine_scheduler* sched,
                                            doctrine_event* ev)
{
    u32 handle;
    doctrine_due_user* due;
    agent_doctrine* doctrine;
    if (!sched || !ev) {
        return -1;
    }
    if (doctrine_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->event = ev;
    if (dg_due_scheduler_register(&sched->due, &g_doctrine_due_vtable, due,
                                  ev->event_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    sched->event_count += 1u;
    doctrine = agent_doctrine_find(sched->doctrines, ev->doctrine_id);
    if (doctrine) {
        doctrine_recompute_next_due(sched, doctrine);
    }
    return 0;
}

int doctrine_schedule_apply(doctrine_scheduler* sched,
                            const agent_doctrine* doctrine,
                            dom_act_time_t trigger_act)
{
    doctrine_event* ev;
    if (!sched || !doctrine || doctrine->doctrine_id == 0u) {
        return -1;
    }
    ev = doctrine_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->doctrine_id = doctrine->doctrine_id;
    ev->trigger_act = trigger_act;
    ev->type = DOCTRINE_EVENT_APPLY;
    ev->doctrine = *doctrine;
    ev->provenance_ref = doctrine->provenance_ref ? doctrine->provenance_ref : ev->event_id;
    if (doctrine_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int doctrine_schedule_clear(doctrine_scheduler* sched,
                            u64 doctrine_id,
                            dom_act_time_t trigger_act)
{
    doctrine_event* ev;
    if (!sched || doctrine_id == 0u) {
        return -1;
    }
    ev = doctrine_event_alloc(sched);
    if (!ev) {
        return -2;
    }
    memset(ev, 0, sizeof(*ev));
    ev->event_id = sched->next_event_id++;
    ev->doctrine_id = doctrine_id;
    ev->trigger_act = trigger_act;
    ev->type = DOCTRINE_EVENT_CLEAR;
    ev->provenance_ref = ev->event_id;
    if (doctrine_schedule_event_internal(sched, ev) != 0) {
        ev->event_id = 0u;
        return -3;
    }
    return 0;
}

int doctrine_scheduler_advance(doctrine_scheduler* sched,
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

dom_act_time_t doctrine_scheduler_next_due(const doctrine_scheduler* sched)
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
