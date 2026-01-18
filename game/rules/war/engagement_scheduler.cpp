/*
FILE: game/rules/war/engagement_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements engagement due scheduling and resolution hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduling and resolution ordering are deterministic.
*/
#include "dominium/rules/war/engagement_scheduler.h"

#include <string.h>

static dom_act_time_t engagement_due_next_tick(void* user, dom_act_time_t now_tick)
{
    engagement_due_user* due = (engagement_due_user*)user;
    (void)now_tick;
    if (!due || !due->engagement) {
        return DG_DUE_TICK_NONE;
    }
    if (due->engagement->status != ENGAGEMENT_STATUS_SCHEDULED) {
        return DG_DUE_TICK_NONE;
    }
    return due->engagement->resolution_act;
}

static int engagement_due_process_until(void* user, dom_act_time_t target_tick)
{
    engagement_due_user* due = (engagement_due_user*)user;
    engagement_scheduler* sched;
    engagement_outcome outcome;
    engagement_refusal_code refusal;
    if (!due || !due->scheduler || !due->engagement) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    if (due->engagement->status != ENGAGEMENT_STATUS_SCHEDULED) {
        return DG_DUE_OK;
    }
    if (due->engagement->resolution_act == DG_DUE_TICK_NONE ||
        due->engagement->resolution_act > target_tick) {
        return DG_DUE_OK;
    }
    memset(&outcome, 0, sizeof(outcome));
    if (engagement_resolve(due->engagement, sched->resolution, &outcome, &refusal) != 0) {
        return DG_DUE_ERR;
    }
    due->engagement->status = ENGAGEMENT_STATUS_RESOLVED;
    due->engagement->next_due_tick = DOM_TIME_ACT_MAX;
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    return DG_DUE_OK;
}

static dg_due_vtable g_engagement_due_vtable = {
    engagement_due_next_tick,
    engagement_due_process_until
};

int engagement_scheduler_init(engagement_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              engagement_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              engagement_registry* engagements,
                              engagement_outcome_list* outcomes,
                              engagement_resolution_context* resolution)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !engagements || !resolution) {
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
    sched->engagements = engagements;
    sched->outcomes = outcomes;
    sched->resolution = resolution;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(engagement_due_user) * (size_t)entry_capacity);
    return 0;
}

static int engagement_scheduler_alloc_handle(engagement_scheduler* sched, u32* out_handle)
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

int engagement_scheduler_register(engagement_scheduler* sched,
                                  engagement* engagement)
{
    u32 handle;
    engagement_due_user* due;
    if (!sched || !engagement) {
        return -1;
    }
    if (engagement_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->engagement = engagement;
    if (dg_due_scheduler_register(&sched->due, &g_engagement_due_vtable, due,
                                  engagement->engagement_id, &handle) != DG_DUE_OK) {
        return -3;
    }
    engagement->next_due_tick = engagement->resolution_act;
    return 0;
}

int engagement_scheduler_advance(engagement_scheduler* sched,
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

dom_act_time_t engagement_scheduler_next_due(const engagement_scheduler* sched)
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
