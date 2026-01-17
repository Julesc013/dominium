/*
FILE: game/core/life/inheritance_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements deterministic inheritance scheduling over ACT.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic by due tick and stable key.
*/
#include "dominium/life/inheritance_scheduler.h"

#include <string.h>

static dom_act_time_t life_estate_next_due_tick(void* user, dom_act_time_t now_tick)
{
    life_inheritance_due_user* due = (life_inheritance_due_user*)user;
    (void)now_tick;
    if (!due || !due->estate) {
        return DG_DUE_TICK_NONE;
    }
    return due->estate->next_due_tick;
}

static int life_estate_process_until(void* user, dom_act_time_t target_tick)
{
    life_inheritance_due_user* due = (life_inheritance_due_user*)user;
    life_estate* estate;
    life_inheritance_action action;

    if (!due || !due->scheduler || !due->estate) {
        return DG_DUE_ERR;
    }
    estate = due->estate;
    if (estate->status != LIFE_ESTATE_OPEN) {
        estate->next_due_tick = DG_DUE_TICK_NONE;
        return DG_DUE_OK;
    }
    if (estate->claim_end_tick > target_tick) {
        return DG_DUE_OK;
    }

    memset(&action, 0, sizeof(action));
    action.estate_id = estate->estate_id;
    action.trigger_act = estate->claim_end_tick;
    action.policy_id = estate->policy_id;
    action.target_person_id = 0u;
    if (!estate->has_executor_authority) {
        action.refusal_code = LIFE_DEATH_REFUSAL_NO_EXECUTOR_AUTHORITY;
    } else {
        action.refusal_code = LIFE_DEATH_REFUSAL_NONE;
    }

    if (life_inheritance_action_append(due->scheduler->action_list, &action, &action.action_id) != 0) {
        return DG_DUE_ERR;
    }

    estate->status = LIFE_ESTATE_RESOLVING;
    estate->next_due_tick = DG_DUE_TICK_NONE;
    return DG_DUE_OK;
}

static dg_due_vtable g_life_estate_vtable = {
    life_estate_next_due_tick,
    life_estate_process_until
};

void life_inheritance_action_list_init(life_inheritance_action_list* list,
                                       life_inheritance_action* storage,
                                       u32 capacity,
                                       u64 start_id)
{
    if (!list) {
        return;
    }
    list->actions = storage;
    list->count = 0u;
    list->capacity = capacity;
    list->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_inheritance_action) * (size_t)capacity);
    }
}

int life_inheritance_action_append(life_inheritance_action_list* list,
                                   const life_inheritance_action* action,
                                   u64* out_id)
{
    life_inheritance_action* slot;
    if (!list || !action || !list->actions) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    slot = &list->actions[list->count++];
    *slot = *action;
    slot->action_id = list->next_id++;
    if (out_id) {
        *out_id = slot->action_id;
    }
    return 0;
}

int life_inheritance_scheduler_init(life_inheritance_scheduler* sched,
                                    dom_time_event* event_storage,
                                    u32 event_capacity,
                                    dg_due_entry* entry_storage,
                                    life_inheritance_due_user* user_storage,
                                    u32 entry_capacity,
                                    dom_act_time_t start_tick,
                                    dom_act_time_t claim_period_ticks,
                                    life_estate_registry* estates,
                                    life_inheritance_action_list* actions)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !estates || !actions) {
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
    sched->action_list = actions;
    sched->estates = estates;
    sched->claim_period_ticks = claim_period_ticks;
    memset(user_storage, 0, sizeof(life_inheritance_due_user) * (size_t)entry_capacity);
    return 0;
}

int life_inheritance_scheduler_register_estate(life_inheritance_scheduler* sched,
                                               life_estate* estate)
{
    u32 handle = 0u;
    life_inheritance_due_user* due;
    if (!sched || !estate) {
        return -1;
    }
    if (estate->act_created == 0) {
        return -2;
    }
    estate->claim_end_tick = estate->act_created + sched->claim_period_ticks;
    if (estate->claim_end_tick < estate->act_created) {
        return -3;
    }
    estate->next_due_tick = estate->claim_end_tick;
    if (sched->due.entry_count >= sched->due.entry_capacity) {
        return -4;
    }

    due = &sched->due_users[sched->due.entry_count];
    due->scheduler = sched;
    due->estate = estate;

    if (dg_due_scheduler_register(&sched->due, &g_life_estate_vtable, due,
                                  estate->estate_id, &handle) != DG_DUE_OK) {
        return -5;
    }
    estate->due_handle = handle;
    return 0;
}

int life_inheritance_scheduler_advance(life_inheritance_scheduler* sched,
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
