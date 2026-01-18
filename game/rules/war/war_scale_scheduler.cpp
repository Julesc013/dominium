/*
FILE: game/rules/war/war_scale_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic scheduling for blockade, interdiction, and siege events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering and processing are deterministic.
*/
#include "dominium/rules/war/war_scale_scheduler.h"

#include <string.h>

static dom_act_time_t war_scale_due_next_tick(void* user, dom_act_time_t now_tick)
{
    war_scale_due_user* due = (war_scale_due_user*)user;
    (void)now_tick;
    if (!due || !due->target) {
        return DG_DUE_TICK_NONE;
    }
    switch (due->type) {
        case WAR_SCALE_DUE_BLOCKADE: {
            blockade_state* state = (blockade_state*)due->target;
            if (state->status != BLOCKADE_STATUS_ACTIVE) {
                return DG_DUE_TICK_NONE;
            }
            return state->next_due_tick;
        }
        case WAR_SCALE_DUE_INTERDICTION: {
            interdiction_operation* op = (interdiction_operation*)due->target;
            if (op->status != INTERDICTION_STATUS_SCHEDULED) {
                return DG_DUE_TICK_NONE;
            }
            return op->next_due_tick;
        }
        case WAR_SCALE_DUE_SIEGE: {
            siege_state* state = (siege_state*)due->target;
            if (state->status != SIEGE_STATUS_ACTIVE) {
                return DG_DUE_TICK_NONE;
            }
            return state->next_due_tick;
        }
        default:
            break;
    }
    return DG_DUE_TICK_NONE;
}

static int war_scale_due_process_until(void* user, dom_act_time_t target_tick)
{
    war_scale_due_user* due = (war_scale_due_user*)user;
    war_scale_scheduler* sched;
    if (!due || !due->scheduler) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    switch (due->type) {
        case WAR_SCALE_DUE_BLOCKADE: {
            blockade_state* state = (blockade_state*)due->target;
            blockade_refusal_code refusal;
            if (!state || state->status != BLOCKADE_STATUS_ACTIVE) {
                return DG_DUE_OK;
            }
            if (state->next_due_tick == DG_DUE_TICK_NONE ||
                state->next_due_tick > target_tick) {
                return DG_DUE_OK;
            }
            sched->blockade_ctx.now_act = state->next_due_tick;
            (void)blockade_apply_maintenance(state, &sched->blockade_ctx, &refusal);
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        case WAR_SCALE_DUE_INTERDICTION: {
            interdiction_operation* op = (interdiction_operation*)due->target;
            interdiction_refusal_code refusal;
            if (!op || op->status != INTERDICTION_STATUS_SCHEDULED) {
                return DG_DUE_OK;
            }
            if (op->next_due_tick == DG_DUE_TICK_NONE ||
                op->next_due_tick > target_tick) {
                return DG_DUE_OK;
            }
            (void)interdiction_apply(op, &sched->interdiction_ctx, &refusal);
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        case WAR_SCALE_DUE_SIEGE: {
            siege_state* state = (siege_state*)due->target;
            if (!state || state->status != SIEGE_STATUS_ACTIVE) {
                return DG_DUE_OK;
            }
            if (state->next_due_tick == DG_DUE_TICK_NONE ||
                state->next_due_tick > target_tick) {
                return DG_DUE_OK;
            }
            sched->siege_ctx.now_act = state->next_due_tick;
            (void)siege_apply_update(state, &sched->siege_ctx);
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        default:
            break;
    }
    return DG_DUE_OK;
}

static dg_due_vtable g_war_scale_due_vtable = {
    war_scale_due_next_tick,
    war_scale_due_process_until
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
                             const siege_update_context* siege_ctx)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage) {
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
    sched->entry_capacity = entry_capacity;
    sched->blockades = blockades;
    sched->interdictions = interdictions;
    sched->sieges = sieges;
    if (blockade_ctx) {
        sched->blockade_ctx = *blockade_ctx;
    } else {
        memset(&sched->blockade_ctx, 0, sizeof(sched->blockade_ctx));
    }
    if (interdiction_ctx) {
        sched->interdiction_ctx = *interdiction_ctx;
    } else {
        memset(&sched->interdiction_ctx, 0, sizeof(sched->interdiction_ctx));
    }
    if (siege_ctx) {
        sched->siege_ctx = *siege_ctx;
    } else {
        memset(&sched->siege_ctx, 0, sizeof(sched->siege_ctx));
    }
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(war_scale_due_user) * (size_t)entry_capacity);
    return 0;
}

static int war_scale_scheduler_alloc_handle(war_scale_scheduler* sched,
                                            u32* out_handle)
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

static int war_scale_scheduler_register_internal(war_scale_scheduler* sched,
                                                 void* target,
                                                 u32 type,
                                                 u64 stable_key)
{
    u32 handle;
    war_scale_due_user* due;
    if (!sched || !target) {
        return -1;
    }
    if (war_scale_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->type = type;
    due->target = target;
    if (dg_due_scheduler_register(&sched->due, &g_war_scale_due_vtable, due,
                                  stable_key, &handle) != DG_DUE_OK) {
        return -3;
    }
    due->handle = handle;
    return 0;
}

int war_scale_scheduler_register_blockade(war_scale_scheduler* sched,
                                          blockade_state* state)
{
    if (!sched || !state) {
        return -1;
    }
    return war_scale_scheduler_register_internal(sched, state,
                                                 WAR_SCALE_DUE_BLOCKADE,
                                                 state->blockade_id);
}

int war_scale_scheduler_register_interdiction(war_scale_scheduler* sched,
                                              interdiction_operation* op)
{
    if (!sched || !op) {
        return -1;
    }
    return war_scale_scheduler_register_internal(sched, op,
                                                 WAR_SCALE_DUE_INTERDICTION,
                                                 op->interdiction_id);
}

int war_scale_scheduler_register_siege(war_scale_scheduler* sched,
                                       siege_state* state)
{
    if (!sched || !state) {
        return -1;
    }
    return war_scale_scheduler_register_internal(sched, state,
                                                 WAR_SCALE_DUE_SIEGE,
                                                 state->siege_id);
}

int war_scale_scheduler_advance(war_scale_scheduler* sched,
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

dom_act_time_t war_scale_scheduler_next_due(const war_scale_scheduler* sched)
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
