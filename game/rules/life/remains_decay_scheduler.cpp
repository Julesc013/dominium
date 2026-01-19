/*
FILE: game/core/life/remains_decay_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements event-driven remains decay scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#include "dominium/life/remains_decay_scheduler.h"

#include <string.h>

static dom_act_time_t life_remains_next_due(void* user, dom_act_time_t now_tick)
{
    life_remains_decay_user* due = (life_remains_decay_user*)user;
    (void)now_tick;
    if (!due || !due->remains) {
        return DG_DUE_TICK_NONE;
    }
    if (due->remains->state == LIFE_REMAINS_COLLAPSED) {
        return DG_DUE_TICK_NONE;
    }
    return due->remains->next_due_tick;
}

static int life_remains_advance_state(life_remains_decay_scheduler* sched,
                                      life_remains* remains)
{
    if (!sched || !remains) {
        return DG_DUE_ERR;
    }
    if (remains->state == LIFE_REMAINS_FRESH) {
        remains->state = LIFE_REMAINS_DECAYED;
        remains->next_due_tick += sched->rules.decayed_to_skeletal;
        return DG_DUE_OK;
    }
    if (remains->state == LIFE_REMAINS_DECAYED) {
        remains->state = LIFE_REMAINS_SKELETAL;
        remains->next_due_tick += sched->rules.skeletal_to_unknown;
        return DG_DUE_OK;
    }
    if (remains->state == LIFE_REMAINS_SKELETAL) {
        remains->state = LIFE_REMAINS_UNKNOWN;
        remains->next_due_tick = DG_DUE_TICK_NONE;
        return DG_DUE_OK;
    }
    remains->next_due_tick = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static int life_remains_process_until(void* user, dom_act_time_t target_tick)
{
    life_remains_decay_user* due = (life_remains_decay_user*)user;
    life_remains* remains;
    if (!due || !due->scheduler || !due->remains) {
        return DG_DUE_ERR;
    }
    remains = due->remains;
    if (remains->next_due_tick == DG_DUE_TICK_NONE) {
        return DG_DUE_OK;
    }
    if (remains->next_due_tick > target_tick) {
        return DG_DUE_OK;
    }
    return life_remains_advance_state(due->scheduler, remains);
}

static dg_due_vtable g_remains_decay_vtable = {
    life_remains_next_due,
    life_remains_process_until
};

int life_remains_decay_scheduler_init(life_remains_decay_scheduler* sched,
                                      dom_time_event* event_storage,
                                      u32 event_capacity,
                                      dg_due_entry* entry_storage,
                                      life_remains_decay_user* user_storage,
                                      u32 entry_capacity,
                                      dom_act_time_t start_tick,
                                      life_remains_registry* remains,
                                      const life_remains_decay_rules* rules)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !remains || !rules) {
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
    sched->remains = remains;
    sched->rules = *rules;
    memset(user_storage, 0, sizeof(life_remains_decay_user) * (size_t)entry_capacity);
    return 0;
}

int life_remains_decay_register(life_remains_decay_scheduler* sched,
                                life_remains* remains)
{
    u32 handle = 0u;
    u32 i;
    life_remains_decay_user* due;
    if (!sched || !remains) {
        return -1;
    }
    if (!sched->due.entries || !sched->due_users) {
        return -2;
    }
    handle = sched->due.entry_capacity;
    for (i = 0u; i < sched->due.entry_capacity; ++i) {
        if (!sched->due.entries[i].in_use) {
            handle = i;
            break;
        }
    }
    if (handle >= sched->due.entry_capacity) {
        return -2;
    }
    if (remains->next_due_tick == DOM_TIME_ACT_MAX) {
        remains->next_due_tick = remains->created_act + sched->rules.fresh_to_decayed;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->remains = remains;
    if (dg_due_scheduler_register(&sched->due, &g_remains_decay_vtable, due,
                                  remains->remains_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int life_remains_decay_advance(life_remains_decay_scheduler* sched,
                               dom_act_time_t target_tick)
{
    if (!sched) {
        return -1;
    }
    if (dg_due_scheduler_advance(&sched->due, target_tick) != DG_DUE_OK) {
        return -2;
    }
    return 0;
}
