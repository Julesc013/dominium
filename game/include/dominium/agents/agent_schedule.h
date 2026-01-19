/*
FILE: include/dominium/agents/agent_schedule.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic agent scheduling records and due processing.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Due ordering is stable by (next_due_tick, agent_id).
*/
#ifndef DOMINIUM_AGENTS_AGENT_SCHEDULE_H
#define DOMINIUM_AGENTS_AGENT_SCHEDULE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/sim/dg_due_sched.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_schedule_entry {
    u64 agent_id;
    dom_act_time_t next_think_act;
    dom_act_time_t think_interval_act;
    u64 active_goal_ref;
    u64 active_plan_ref;
    u32 due_handle;
    int in_use;
} agent_schedule_entry;

typedef int (*agent_schedule_think_fn)(void* user,
                                       agent_schedule_entry* entry,
                                       dom_act_time_t now_act);

typedef struct agent_schedule_callbacks {
    agent_schedule_think_fn on_think;
    void* user;
} agent_schedule_callbacks;

typedef struct agent_schedule_due_user {
    struct agent_schedule* scheduler;
    agent_schedule_entry* entry;
} agent_schedule_due_user;

typedef struct agent_schedule {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    agent_schedule_due_user* due_users;
    agent_schedule_entry* entries;
    u32 entry_capacity;
    u32 entry_count;
    agent_schedule_callbacks callbacks;
    u32 processed_last;
    u32 processed_total;
} agent_schedule;

int agent_schedule_init(agent_schedule* sched,
                        dom_time_event* event_storage,
                        u32 event_capacity,
                        dg_due_entry* entry_storage,
                        agent_schedule_due_user* user_storage,
                        u32 due_capacity,
                        dom_act_time_t start_tick,
                        agent_schedule_entry* schedule_storage,
                        u32 schedule_capacity);
int agent_schedule_register(agent_schedule* sched,
                            u64 agent_id,
                            dom_act_time_t first_think_act,
                            dom_act_time_t think_interval_act);
agent_schedule_entry* agent_schedule_find(agent_schedule* sched,
                                          u64 agent_id);
int agent_schedule_set_next(agent_schedule* sched,
                            u64 agent_id,
                            dom_act_time_t next_think_act);
int agent_schedule_set_active(agent_schedule* sched,
                              u64 agent_id,
                              u64 goal_ref,
                              u64 plan_ref);
void agent_schedule_set_callbacks(agent_schedule* sched,
                                  const agent_schedule_callbacks* callbacks);
int agent_schedule_advance(agent_schedule* sched,
                           dom_act_time_t target_tick);
dom_act_time_t agent_schedule_next_due(const agent_schedule* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_SCHEDULE_H */
