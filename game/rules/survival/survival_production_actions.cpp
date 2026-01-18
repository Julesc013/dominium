/*
FILE: game/rules/survival/survival_production_actions.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / survival rules
RESPONSIBILITY: Implements deterministic production actions for CIV0a.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Action ordering is deterministic.
*/
#include "dominium/rules/survival/survival_production_actions.h"

#include <string.h>

void survival_production_action_registry_init(survival_production_action_registry* reg,
                                              survival_production_action* storage,
                                              u32 capacity,
                                              u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->actions = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(survival_production_action) * (size_t)capacity);
    }
}

survival_production_action* survival_production_action_find(
    survival_production_action_registry* reg,
    u64 action_id)
{
    u32 i;
    if (!reg || !reg->actions) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->actions[i].action_id == action_id) {
            return &reg->actions[i];
        }
    }
    return 0;
}

static dom_act_time_t survival_production_next_due_tick(void* user, dom_act_time_t now_tick)
{
    survival_production_due_user* due = (survival_production_due_user*)user;
    (void)now_tick;
    if (!due || !due->action) {
        return DG_DUE_TICK_NONE;
    }
    if (due->action->status != SURVIVAL_ACTION_PENDING) {
        return DG_DUE_TICK_NONE;
    }
    return due->action->end_tick;
}

static int survival_production_apply(survival_production_scheduler* sched,
                                     survival_production_action* action)
{
    survival_needs_state* needs;
    survival_cohort* cohort;
    if (!sched || !action) {
        return DG_DUE_ERR;
    }
    cohort = survival_cohort_find(sched->cohorts, action->cohort_id);
    if (!cohort) {
        action->status = SURVIVAL_ACTION_REFUSED;
        action->refusal_code = SURVIVAL_REFUSAL_COHORT_NOT_FOUND;
        return DG_DUE_OK;
    }
    needs = survival_needs_get(sched->needs, action->cohort_id);
    if (!needs) {
        action->status = SURVIVAL_ACTION_REFUSED;
        action->refusal_code = SURVIVAL_REFUSAL_COHORT_NOT_FOUND;
        (void)survival_cohort_set_active_action(sched->cohorts, action->cohort_id, 0u);
        return DG_DUE_OK;
    }

    if (action->type == SURVIVAL_ACTION_GATHER_FOOD) {
        needs->food_store += action->output_food;
    } else if (action->type == SURVIVAL_ACTION_COLLECT_WATER) {
        needs->water_store += action->output_water;
    } else if (action->type == SURVIVAL_ACTION_BUILD_SHELTER) {
        needs->shelter_level = survival_shelter_apply(needs->shelter_level,
                                                      action->output_shelter,
                                                      5u);
    }
    needs->last_production_provenance = action->provenance_ref;
    action->status = SURVIVAL_ACTION_COMPLETED;
    action->refusal_code = SURVIVAL_REFUSAL_NONE;
    (void)survival_cohort_set_active_action(sched->cohorts, action->cohort_id, 0u);
    return DG_DUE_OK;
}

static int survival_production_process_until(void* user, dom_act_time_t target_tick)
{
    survival_production_due_user* due = (survival_production_due_user*)user;
    survival_production_scheduler* sched;
    survival_production_action* action;

    if (!due || !due->scheduler || !due->action) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    action = due->action;
    if (action->status != SURVIVAL_ACTION_PENDING) {
        return DG_DUE_OK;
    }
    if (action->end_tick > target_tick) {
        return DG_DUE_OK;
    }
    return survival_production_apply(sched, action);
}

static dg_due_vtable g_production_vtable = {
    survival_production_next_due_tick,
    survival_production_process_until
};

int survival_production_scheduler_init(survival_production_scheduler* sched,
                                       dom_time_event* event_storage,
                                       u32 event_capacity,
                                       dg_due_entry* entry_storage,
                                       survival_production_due_user* user_storage,
                                       u32 entry_capacity,
                                       dom_act_time_t start_tick,
                                       survival_cohort_registry* cohorts,
                                       survival_needs_registry* needs,
                                       survival_production_action_registry* actions)
{
    int rc;
    if (!sched || !event_storage || !entry_storage || !user_storage || !cohorts || !needs || !actions) {
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
    sched->actions = actions;
    memset(user_storage, 0, sizeof(survival_production_due_user) * (size_t)entry_capacity);
    return 0;
}

int survival_production_schedule_action(survival_production_scheduler* sched,
                                        const survival_production_action_input* input,
                                        survival_production_refusal_code* out_refusal,
                                        u64* out_action_id)
{
    survival_cohort* cohort;
    survival_production_action* action;
    survival_production_due_user* due;
    u32 handle;
    u32 i;
    survival_production_refusal_code refusal = SURVIVAL_REFUSAL_NONE;

    if (out_refusal) {
        *out_refusal = SURVIVAL_REFUSAL_NONE;
    }
    if (!sched || !input || !sched->actions || !sched->actions->actions) {
        return -1;
    }
    cohort = survival_cohort_find(sched->cohorts, input->cohort_id);
    if (!cohort) {
        refusal = SURVIVAL_REFUSAL_COHORT_NOT_FOUND;
        goto refuse_out;
    }
    if (cohort->active_action_id != 0u) {
        refusal = SURVIVAL_REFUSAL_ACTION_ALREADY_PENDING;
        goto refuse_out;
    }
    if (sched->actions->count >= sched->actions->capacity) {
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

    action = &sched->actions->actions[sched->actions->count++];
    memset(action, 0, sizeof(*action));
    action->action_id = sched->actions->next_id++;
    action->cohort_id = input->cohort_id;
    action->type = input->type;
    action->status = SURVIVAL_ACTION_PENDING;
    action->start_tick = input->start_tick;
    action->end_tick = input->start_tick + input->duration_ticks;
    action->output_food = input->output_food;
    action->output_water = input->output_water;
    action->output_shelter = input->output_shelter;
    action->provenance_ref = input->provenance_ref;
    action->refusal_code = SURVIVAL_REFUSAL_NONE;

    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->action = action;
    if (dg_due_scheduler_register(&sched->due, &g_production_vtable, due,
                                  action->action_id, &handle) != DG_DUE_OK) {
        return -4;
    }
    (void)survival_cohort_set_active_action(sched->cohorts, input->cohort_id, action->action_id);
    if (out_action_id) {
        *out_action_id = action->action_id;
    }
    if (out_refusal) {
        *out_refusal = SURVIVAL_REFUSAL_NONE;
    }
    return 0;

refuse_out:
    if (out_refusal) {
        *out_refusal = refusal;
    }
    return 1;
}

int survival_production_advance(survival_production_scheduler* sched,
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

dom_act_time_t survival_production_next_due(const survival_production_scheduler* sched)
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
