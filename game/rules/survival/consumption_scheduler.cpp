/*
FILE: game/rules/survival/consumption_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / survival rules
RESPONSIBILITY: Implements event-driven cohort consumption scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#include "dominium/rules/survival/consumption_scheduler.h"

#include <string.h>

static u32 survival_clamp_add(u32 base, u64 add, u32 max_value)
{
    u64 sum = (u64)base + add;
    if (sum > (u64)max_value) {
        return max_value;
    }
    return (u32)sum;
}

static dom_act_time_t survival_consumption_next_due_tick(void* user, dom_act_time_t now_tick)
{
    survival_consumption_due_user* due = (survival_consumption_due_user*)user;
    (void)now_tick;
    if (!due || !due->cohort) {
        return DG_DUE_TICK_NONE;
    }
    if (due->cohort->count == 0u) {
        return DG_DUE_TICK_NONE;
    }
    return due->cohort->next_due_tick;
}

static void survival_emit_death(survival_consumption_scheduler* sched,
                                survival_cohort* cohort,
                                dom_act_time_t act_time,
                                u32 cause_code)
{
    if (!sched || !cohort) {
        return;
    }
    if (cohort->count == 0u) {
        return;
    }
    (void)survival_cohort_adjust_count(sched->cohorts, cohort->cohort_id, -1, 0);
    if (sched->death_hook.emit) {
        (void)sched->death_hook.emit(sched->death_hook.user, cohort->cohort_id, 1u, act_time, cause_code);
    }
}

static void survival_apply_consumption(survival_consumption_scheduler* sched,
                                       survival_cohort* cohort,
                                       survival_needs_state* needs,
                                       dom_act_time_t due_tick)
{
    u64 food_need;
    u64 water_need;
    u64 deficit;

    if (!sched || !cohort || !needs) {
        return;
    }
    if (cohort->count == 0u) {
        return;
    }


    food_need = (u64)sched->params.food_per_person * (u64)cohort->count;
    if (needs->food_store >= food_need) {
        needs->food_store -= (u32)food_need;
        needs->hunger_level = 0u;
    } else {
        deficit = food_need - needs->food_store;
        needs->food_store = 0u;
        needs->hunger_level = survival_clamp_add(needs->hunger_level, deficit, sched->params.hunger_max);
    }

    water_need = (u64)sched->params.water_per_person * (u64)cohort->count;
    if (needs->water_store >= water_need) {
        needs->water_store -= (u32)water_need;
        needs->thirst_level = 0u;
    } else {
        deficit = water_need - needs->water_store;
        needs->water_store = 0u;
        needs->thirst_level = survival_clamp_add(needs->thirst_level, deficit, sched->params.thirst_max);
    }

    if (needs->thirst_level >= sched->params.thirst_max) {
        survival_emit_death(sched, cohort, due_tick, SURVIVAL_DEATH_CAUSE_DEHYDRATION);
        needs->thirst_level -= sched->params.thirst_max;
    } else if (needs->hunger_level >= sched->params.hunger_max) {
        survival_emit_death(sched, cohort, due_tick, SURVIVAL_DEATH_CAUSE_STARVATION);
        needs->hunger_level -= sched->params.hunger_max;
    }

    needs->last_consumption_tick = due_tick;
}

static int survival_consumption_process_until(void* user, dom_act_time_t target_tick)
{
    survival_consumption_due_user* due = (survival_consumption_due_user*)user;
    survival_consumption_scheduler* sched;
    survival_cohort* cohort;
    survival_needs_state* needs;
    dom_act_time_t next_tick;

    if (!due || !due->scheduler || !due->cohort) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    cohort = due->cohort;
    if (cohort->count == 0u) {
        cohort->next_due_tick = DG_DUE_TICK_NONE;
        return DG_DUE_OK;
    }
    needs = survival_needs_get(sched->needs, cohort->cohort_id);
    if (!needs) {
        return DG_DUE_ERR;
    }
    next_tick = cohort->next_due_tick;
    if (next_tick == DG_DUE_TICK_NONE || next_tick > target_tick) {
        return DG_DUE_OK;
    }
    while (next_tick != DG_DUE_TICK_NONE && next_tick <= target_tick) {
        survival_apply_consumption(sched, cohort, needs, next_tick);
        sched->processed_last += 1u;
        sched->processed_total += 1u;
        if (cohort->count == 0u) {
            cohort->next_due_tick = DG_DUE_TICK_NONE;
            needs->next_consumption_tick = DG_DUE_TICK_NONE;
            return DG_DUE_OK;
        }
        next_tick = next_tick + sched->params.consumption_interval;
        cohort->next_due_tick = next_tick;
        needs->next_consumption_tick = next_tick;
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_consumption_vtable = {
    survival_consumption_next_due_tick,
    survival_consumption_process_until
};

int survival_consumption_scheduler_init(survival_consumption_scheduler* sched,
                                        dom_time_event* event_storage,
                                        u32 event_capacity,
                                        dg_due_entry* entry_storage,
                                        survival_consumption_due_user* user_storage,
                                        u32 entry_capacity,
                                        dom_act_time_t start_tick,
                                        survival_cohort_registry* cohorts,
                                        survival_needs_registry* needs,
                                        const survival_needs_params* params)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !cohorts || !needs || !params) {
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
    sched->cohorts = cohorts;
    sched->needs = needs;
    sched->params = *params;
    sched->death_hook.emit = 0;
    sched->death_hook.user = 0;
    sched->start_tick = start_tick;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(survival_consumption_due_user) * (size_t)entry_capacity);
    return 0;
}

void survival_consumption_set_death_hook(survival_consumption_scheduler* sched,
                                         const survival_death_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->death_hook = *hook;
    } else {
        sched->death_hook.emit = 0;
        sched->death_hook.user = 0;
    }
}

int survival_consumption_register_cohort(survival_consumption_scheduler* sched,
                                         survival_cohort* cohort)
{
    u32 handle;
    u32 i;
    survival_needs_state* needs;
    survival_consumption_due_user* due;

    if (!sched || !cohort) {
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
        return -3;
    }
    needs = survival_needs_get(sched->needs, cohort->cohort_id);
    if (!needs) {
        if (survival_needs_register(sched->needs, cohort->cohort_id, 0) != 0) {
            return -4;
        }
        needs = survival_needs_get(sched->needs, cohort->cohort_id);
        if (!needs) {
            return -5;
        }
    }
    if (cohort->next_due_tick == DOM_TIME_ACT_MAX) {
        cohort->next_due_tick = sched->start_tick + sched->params.consumption_interval;
    }
    needs->next_consumption_tick = cohort->next_due_tick;
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->cohort = cohort;
    if (dg_due_scheduler_register(&sched->due, &g_consumption_vtable, due,
                                  cohort->cohort_id, &handle) != DG_DUE_OK) {
        return -6;
    }
    return 0;
}

int survival_consumption_advance(survival_consumption_scheduler* sched,
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

dom_act_time_t survival_consumption_next_due(const survival_consumption_scheduler* sched)
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
