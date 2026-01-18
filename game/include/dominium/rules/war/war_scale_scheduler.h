/*
FILE: include/dominium/rules/war/war_scale_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic scheduling for blockade, interdiction, and siege events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_WAR_SCALE_SCHEDULER_H
#define DOMINIUM_RULES_WAR_WAR_SCALE_SCHEDULER_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/war/blockade.h"
#include "dominium/rules/war/interdiction.h"
#include "dominium/rules/war/siege_effects.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum war_scale_due_type {
    WAR_SCALE_DUE_BLOCKADE = 0,
    WAR_SCALE_DUE_INTERDICTION = 1,
    WAR_SCALE_DUE_SIEGE = 2
} war_scale_due_type;

typedef struct war_scale_scheduler war_scale_scheduler;

typedef struct war_scale_due_user {
    war_scale_scheduler* scheduler;
    u32 type;
    void* target;
    u32 handle;
} war_scale_due_user;

struct war_scale_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    war_scale_due_user* due_users;
    u32 entry_capacity;

    blockade_registry* blockades;
    interdiction_registry* interdictions;
    siege_registry* sieges;

    blockade_update_context blockade_ctx;
    interdiction_context interdiction_ctx;
    siege_update_context siege_ctx;

    u32 processed_last;
    u32 processed_total;
};

int war_scale_scheduler_init(war_scale_scheduler* sched,
                             dom_time_event* event_storage,
                             u32 event_capacity,
                             dg_due_entry* entry_storage,
                             war_scale_due_user* user_storage,
                             u32 entry_capacity,
                             dom_act_time_t start_tick,
                             blockade_registry* blockades,
                             interdiction_registry* interdictions,
                             siege_registry* sieges,
                             const blockade_update_context* blockade_ctx,
                             const interdiction_context* interdiction_ctx,
                             const siege_update_context* siege_ctx);

int war_scale_scheduler_register_blockade(war_scale_scheduler* sched,
                                          blockade_state* state);
int war_scale_scheduler_register_interdiction(war_scale_scheduler* sched,
                                              interdiction_operation* op);
int war_scale_scheduler_register_siege(war_scale_scheduler* sched,
                                       siege_state* state);

int war_scale_scheduler_advance(war_scale_scheduler* sched,
                                dom_act_time_t target_tick);
dom_act_time_t war_scale_scheduler_next_due(const war_scale_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_WAR_SCALE_SCHEDULER_H */
