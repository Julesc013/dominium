/*
FILE: game/agents/agent_schedule.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic agent scheduling using due scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Due ordering is stable by (due_tick, agent_id).
*/
#include "dominium/agents/agent_schedule.h"

#include <string.h>

static dom_act_time_t agent_schedule_due_next_tick(void* user, dom_act_time_t now_tick)
{
    agent_schedule_due_user* due = (agent_schedule_due_user*)user;
    (void)now_tick;
    if (!due || !due->entry || !due->entry->in_use) {
        return DG_DUE_TICK_NONE;
    }
    return due->entry->next_think_act;
}

static int agent_schedule_due_process_until(void* user, dom_act_time_t target_tick)
{
    agent_schedule_due_user* due = (agent_schedule_due_user*)user;
    agent_schedule* sched;
    agent_schedule_entry* entry;
    dom_act_time_t current;
    if (!due || !due->scheduler || !due->entry) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    entry = due->entry;
    if (!entry->in_use) {
        return DG_DUE_OK;
    }
    current = entry->next_think_act;
    if (current == DG_DUE_TICK_NONE || current > target_tick) {
        return DG_DUE_OK;
    }
    if (sched->callbacks.on_think) {
        (void)sched->callbacks.on_think(sched->callbacks.user, entry, current);
    }
    if (entry->next_think_act == current) {
        if (entry->think_interval_act > 0u) {
            entry->next_think_act = current + entry->think_interval_act;
        } else {
            entry->next_think_act = DG_DUE_TICK_NONE;
        }
    }
    sched->processed_last += 1u;
    sched->processed_total += 1u;
    return DG_DUE_OK;
}

static dg_due_vtable g_agent_schedule_due_vtable = {
    agent_schedule_due_next_tick,
    agent_schedule_due_process_until
};

int agent_schedule_init(agent_schedule* sched,
                        dom_time_event* event_storage,
                        u32 event_capacity,
                        dg_due_entry* entry_storage,
                        agent_schedule_due_user* user_storage,
                        u32 due_capacity,
                        dom_act_time_t start_tick,
                        agent_schedule_entry* schedule_storage,
                        u32 schedule_capacity)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage ||
        !schedule_storage || schedule_capacity == 0u || due_capacity == 0u) {
        return -1;
    }
    rc = dg_due_scheduler_init(&sched->due,
                               event_storage,
                               event_capacity,
                               entry_storage,
                               due_capacity,
                               start_tick);
    if (rc != DG_DUE_OK) {
        return -2;
    }
    sched->due_events = event_storage;
    sched->due_entries = entry_storage;
    sched->due_users = user_storage;
    sched->entries = schedule_storage;
    sched->entry_capacity = schedule_capacity;
    sched->entry_count = 0u;
    sched->callbacks.on_think = 0;
    sched->callbacks.user = 0;
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(schedule_storage, 0, sizeof(agent_schedule_entry) * (size_t)schedule_capacity);
    memset(user_storage, 0, sizeof(agent_schedule_due_user) * (size_t)due_capacity);
    return 0;
}

static int agent_schedule_alloc_handle(agent_schedule* sched, u32* out_handle)
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

static agent_schedule_entry* agent_schedule_alloc_entry(agent_schedule* sched)
{
    u32 i;
    if (!sched || !sched->entries) {
        return 0;
    }
    if (sched->entry_count >= sched->entry_capacity) {
        return 0;
    }
    for (i = 0u; i < sched->entry_capacity; ++i) {
        if (!sched->entries[i].in_use) {
            return &sched->entries[i];
        }
    }
    return 0;
}

agent_schedule_entry* agent_schedule_find(agent_schedule* sched,
                                          u64 agent_id)
{
    u32 i;
    if (!sched || !sched->entries) {
        return 0;
    }
    for (i = 0u; i < sched->entry_capacity; ++i) {
        if (sched->entries[i].in_use && sched->entries[i].agent_id == agent_id) {
            return &sched->entries[i];
        }
    }
    return 0;
}

int agent_schedule_register(agent_schedule* sched,
                            u64 agent_id,
                            dom_act_time_t first_think_act,
                            dom_act_time_t think_interval_act)
{
    u32 handle;
    agent_schedule_entry* entry;
    agent_schedule_due_user* due;
    if (!sched || agent_id == 0u) {
        return -1;
    }
    if (agent_schedule_find(sched, agent_id)) {
        return -2;
    }
    entry = agent_schedule_alloc_entry(sched);
    if (!entry) {
        return -3;
    }
    if (agent_schedule_alloc_handle(sched, &handle) != 0) {
        return -4;
    }
    entry->agent_id = agent_id;
    entry->next_think_act = first_think_act;
    entry->think_interval_act = think_interval_act;
    entry->active_goal_ref = 0u;
    entry->active_plan_ref = 0u;
    entry->in_use = 1;
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->entry = entry;
    if (dg_due_scheduler_register(&sched->due, &g_agent_schedule_due_vtable, due,
                                  agent_id, &handle) != DG_DUE_OK) {
        memset(entry, 0, sizeof(*entry));
        return -5;
    }
    entry->due_handle = handle;
    sched->entry_count += 1u;
    return 0;
}

int agent_schedule_set_next(agent_schedule* sched,
                            u64 agent_id,
                            dom_act_time_t next_think_act)
{
    agent_schedule_entry* entry;
    if (!sched) {
        return -1;
    }
    entry = agent_schedule_find(sched, agent_id);
    if (!entry) {
        return -2;
    }
    entry->next_think_act = next_think_act;
    if (dg_due_scheduler_refresh(&sched->due, entry->due_handle) != DG_DUE_OK) {
        return -3;
    }
    return 0;
}

int agent_schedule_set_active(agent_schedule* sched,
                              u64 agent_id,
                              u64 goal_ref,
                              u64 plan_ref)
{
    agent_schedule_entry* entry;
    if (!sched) {
        return -1;
    }
    entry = agent_schedule_find(sched, agent_id);
    if (!entry) {
        return -2;
    }
    entry->active_goal_ref = goal_ref;
    entry->active_plan_ref = plan_ref;
    return 0;
}

void agent_schedule_set_callbacks(agent_schedule* sched,
                                  const agent_schedule_callbacks* callbacks)
{
    if (!sched) {
        return;
    }
    if (callbacks) {
        sched->callbacks = *callbacks;
    } else {
        sched->callbacks.on_think = 0;
        sched->callbacks.user = 0;
    }
}

int agent_schedule_advance(agent_schedule* sched,
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

dom_act_time_t agent_schedule_next_due(const agent_schedule* sched)
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
