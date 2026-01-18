/*
FILE: game/rules/population/population_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements due scheduler for cohort and migration events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Due processing order is deterministic.
*/
#include "dominium/rules/population/population_scheduler.h"

#include <string.h>

static dom_act_time_t population_due_next_tick(void* user, dom_act_time_t now_tick)
{
    population_due_user* due = (population_due_user*)user;
    (void)now_tick;
    if (!due || !due->scheduler) {
        return DG_DUE_TICK_NONE;
    }
    if (due->kind == POP_DUE_COHORT) {
        if (!due->cohort || due->cohort->count == 0u) {
            return DG_DUE_TICK_NONE;
        }
        return due->cohort->next_due_tick;
    }
    if (!due->flow || due->flow->status != POP_MIGRATION_ACTIVE) {
        return DG_DUE_TICK_NONE;
    }
    return due->flow->arrival_act;
}

static int population_due_process_until(void* user, dom_act_time_t target_tick)
{
    population_due_user* due = (population_due_user*)user;
    population_scheduler* sched;
    dom_act_time_t next_tick;

    if (!due || !due->scheduler) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->kind == POP_DUE_COHORT) {
        if (!due->cohort || due->cohort->count == 0u) {
            return DG_DUE_OK;
        }
        next_tick = due->cohort->next_due_tick;
        if (next_tick == DG_DUE_TICK_NONE || next_tick > target_tick) {
            return DG_DUE_OK;
        }
        while (next_tick != DG_DUE_TICK_NONE && next_tick <= target_tick) {
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            if (sched->cohort_hook.process) {
                next_tick = sched->cohort_hook.process(sched->cohort_hook.user,
                                                       due->cohort,
                                                       next_tick);
            } else {
                next_tick = DG_DUE_TICK_NONE;
            }
            due->cohort->next_due_tick = next_tick;
        }
        return DG_DUE_OK;
    }
    if (!due->flow || due->flow->status != POP_MIGRATION_ACTIVE) {
        return DG_DUE_OK;
    }
    if (due->flow->arrival_act == DG_DUE_TICK_NONE ||
        due->flow->arrival_act > target_tick) {
        return DG_DUE_OK;
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    if (sched->migration_hook.apply) {
        (void)sched->migration_hook.apply(sched->migration_hook.user, due->flow);
    } else if (sched->cohorts) {
        (void)population_migration_apply(due->flow, sched->cohorts, 0);
    }
    due->flow->arrival_act = DG_DUE_TICK_NONE;
    due->flow->status = POP_MIGRATION_COMPLETED;
    return DG_DUE_OK;
}

static dg_due_vtable g_population_due_vtable = {
    population_due_next_tick,
    population_due_process_until
};

int population_scheduler_init(population_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              population_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              population_cohort_registry* cohorts,
                              population_migration_registry* migrations)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !cohorts || !migrations) {
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
    sched->migrations = migrations;
    sched->cohort_hook.process = 0;
    sched->cohort_hook.user = 0;
    sched->migration_hook.apply = 0;
    sched->migration_hook.user = 0;
    sched->start_tick = start_tick;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(population_due_user) * (size_t)entry_capacity);
    return 0;
}

void population_scheduler_set_cohort_hook(population_scheduler* sched,
                                          const population_cohort_due_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->cohort_hook = *hook;
    } else {
        sched->cohort_hook.process = 0;
        sched->cohort_hook.user = 0;
    }
}

void population_scheduler_set_migration_hook(population_scheduler* sched,
                                             const population_migration_hook* hook)
{
    if (!sched) {
        return;
    }
    if (hook) {
        sched->migration_hook = *hook;
    } else {
        sched->migration_hook.apply = 0;
        sched->migration_hook.user = 0;
    }
}

static int population_scheduler_alloc_handle(population_scheduler* sched, u32* out_handle)
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

int population_scheduler_register_cohort(population_scheduler* sched,
                                         population_cohort_state* cohort)
{
    u32 handle;
    population_due_user* due;
    if (!sched || !cohort) {
        return -1;
    }
    if (population_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    if (cohort->next_due_tick == DOM_TIME_ACT_MAX) {
        cohort->next_due_tick = sched->start_tick;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->kind = POP_DUE_COHORT;
    due->cohort = cohort;
    due->flow = 0;
    if (dg_due_scheduler_register(&sched->due, &g_population_due_vtable, due,
                                  cohort->cohort_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int population_scheduler_register_migration(population_scheduler* sched,
                                            population_migration_flow* flow)
{
    u32 handle;
    population_due_user* due;
    if (!sched || !flow) {
        return -1;
    }
    if (population_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->kind = POP_DUE_MIGRATION;
    due->cohort = 0;
    due->flow = flow;
    if (dg_due_scheduler_register(&sched->due, &g_population_due_vtable, due,
                                  flow->flow_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int population_scheduler_advance(population_scheduler* sched,
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

dom_act_time_t population_scheduler_next_due(const population_scheduler* sched)
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
