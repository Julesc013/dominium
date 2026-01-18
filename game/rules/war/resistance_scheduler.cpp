/*
FILE: game/rules/war/resistance_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic scheduling for occupation, resistance, and disruptions.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Scheduler ordering and processing are deterministic.
*/
#include "dominium/rules/war/resistance_scheduler.h"

#include <string.h>

static dom_act_time_t resistance_due_next_tick(void* user, dom_act_time_t now_tick)
{
    resistance_due_user* due = (resistance_due_user*)user;
    (void)now_tick;
    if (!due || !due->target) {
        return DG_DUE_TICK_NONE;
    }
    switch (due->type) {
        case RESIST_DUE_OCCUPATION: {
            occupation_state* occ = (occupation_state*)due->target;
            if (occ->status != OCCUPATION_STATUS_ACTIVE) {
                return DG_DUE_TICK_NONE;
            }
            return occ->next_due_tick;
        }
        case RESIST_DUE_RESISTANCE: {
            resistance_state* res = (resistance_state*)due->target;
            return res->next_due_tick;
        }
        case RESIST_DUE_DISRUPTION: {
            disruption_event* ev = (disruption_event*)due->target;
            if (ev->status != DISRUPTION_STATUS_SCHEDULED) {
                return DG_DUE_TICK_NONE;
            }
            return ev->scheduled_act;
        }
        case RESIST_DUE_POLICY: {
            pacification_policy_event* ev = (pacification_policy_event*)due->target;
            if (ev->status != PACIFICATION_EVENT_SCHEDULED) {
                return DG_DUE_TICK_NONE;
            }
            return ev->scheduled_act;
        }
        default:
            break;
    }
    return DG_DUE_TICK_NONE;
}

static int resistance_schedule_disruption(resistance_scheduler* sched,
                                          resistance_state* state,
                                          dom_act_time_t now_act)
{
    disruption_event ev;
    u64 disruption_id = 0u;
    u32 delay;
    if (!sched || !state || !sched->disruptions) {
        return -1;
    }
    if (state->disruption_interval == 0u) {
        return 0;
    }
    if (state->next_disruption_act != 0u && now_act < state->next_disruption_act) {
        return 0;
    }
    if (state->disruption_transport_capacity_id == 0u &&
        state->disruption_supply_store_ref == 0u) {
        return 0;
    }
    memset(&ev, 0, sizeof(ev));
    ev.territory_id = state->territory_id;
    if (state->resistance_pressure >= 800u) {
        ev.effect_type = DISRUPTION_EFFECT_SABOTAGE;
        ev.capacity_delta = state->resistance_pressure / 20u;
    } else if (state->resistance_pressure >= 600u) {
        ev.effect_type = DISRUPTION_EFFECT_STRIKE;
        ev.capacity_delta = state->resistance_pressure / 25u;
    } else {
        ev.effect_type = DISRUPTION_EFFECT_AMBUSH;
        ev.capacity_delta = state->resistance_pressure / 30u;
    }
    ev.transport_capacity_id = state->disruption_transport_capacity_id;
    ev.supply_store_ref = state->disruption_supply_store_ref;
    ev.supply_asset_id = state->disruption_supply_asset_id;
    ev.supply_qty = state->disruption_supply_qty;
    ev.legitimacy_id = state->legitimacy_id;
    ev.legitimacy_delta = -(i32)(state->resistance_pressure / 100u);
    delay = state->disruption_delay ? state->disruption_delay : 1u;
    ev.delay_ticks = delay;
    ev.scheduled_act = now_act + delay;
    if (disruption_event_schedule(sched->disruptions, &ev, &disruption_id) != 0) {
        return -2;
    }
    if (disruption_id != 0u) {
        disruption_event* stored = disruption_event_find(sched->disruptions, disruption_id);
        if (stored) {
            (void)resistance_scheduler_register_disruption(sched, stored);
        }
    }
    state->next_disruption_act = now_act + state->disruption_interval;
    return 0;
}

static void resistance_apply_enforcement_attrition(resistance_scheduler* sched,
                                                   const occupation_state* occupation,
                                                   const resistance_state* state)
{
    enforcement_capacity* capacity;
    u32 loss;
    if (!sched || !occupation || !state || !sched->enforcement) {
        return;
    }
    if (state->status != RESISTANCE_STATUS_ACTIVE) {
        return;
    }
    if (occupation->enforcement_capacity_id == 0u) {
        return;
    }
    capacity = enforcement_capacity_find(sched->enforcement,
                                         occupation->enforcement_capacity_id);
    if (!capacity || capacity->available_enforcers == 0u) {
        return;
    }
    loss = state->resistance_pressure / 200u;
    if (loss == 0u) {
        loss = 1u;
    }
    if (loss > capacity->available_enforcers) {
        loss = capacity->available_enforcers;
    }
    capacity->available_enforcers -= loss;
}

static int resistance_due_process_until(void* user, dom_act_time_t target_tick)
{
    resistance_due_user* due = (resistance_due_user*)user;
    resistance_scheduler* sched;
    if (!due || !due->scheduler) {
        return DG_DUE_ERR;
    }
    sched = due->scheduler;
    switch (due->type) {
        case RESIST_DUE_OCCUPATION: {
            occupation_state* occ = (occupation_state*)due->target;
            occupation_update_context ctx;
            occupation_refusal_code refusal;
            if (!occ || occ->status != OCCUPATION_STATUS_ACTIVE) {
                return DG_DUE_OK;
            }
            if (occ->next_due_tick == DG_DUE_TICK_NONE ||
                occ->next_due_tick > target_tick) {
                return DG_DUE_OK;
            }
            memset(&ctx, 0, sizeof(ctx));
            ctx.territory = sched->territories;
            ctx.legitimacy = sched->legitimacy;
            ctx.enforcement = sched->enforcement;
            ctx.stores = sched->stores;
            ctx.now_act = occ->next_due_tick;
            (void)occupation_apply_maintenance(occ, &ctx, &refusal);
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        case RESIST_DUE_RESISTANCE: {
            resistance_state* res = (resistance_state*)due->target;
            resistance_update_context ctx;
            occupation_state* occ;
            if (!res) {
                return DG_DUE_OK;
            }
            if (res->next_due_tick == DG_DUE_TICK_NONE ||
                res->next_due_tick > target_tick) {
                return DG_DUE_OK;
            }
            memset(&ctx, 0, sizeof(ctx));
            ctx.legitimacy = sched->legitimacy;
            ctx.needs = sched->survival_needs;
            ctx.cohorts = sched->survival_cohorts;
            ctx.needs_params = sched->needs_params;
            ctx.now_act = res->next_due_tick;
            occ = (sched->occupations) ? occupation_find_by_territory(sched->occupations, res->territory_id) : 0;
            (void)resistance_apply_update(res, occ, &ctx);
            if (res->status == RESISTANCE_STATUS_ACTIVE) {
                (void)resistance_schedule_disruption(sched, res, ctx.now_act);
                resistance_apply_enforcement_attrition(sched, occ, res);
            }
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        case RESIST_DUE_DISRUPTION: {
            disruption_event* ev = (disruption_event*)due->target;
            disruption_effects_context ctx;
            if (!ev || ev->status != DISRUPTION_STATUS_SCHEDULED) {
                return DG_DUE_OK;
            }
            if (ev->scheduled_act == DG_DUE_TICK_NONE ||
                ev->scheduled_act > target_tick) {
                return DG_DUE_OK;
            }
            memset(&ctx, 0, sizeof(ctx));
            ctx.stores = sched->stores;
            ctx.transport = sched->transport;
            ctx.legitimacy = sched->legitimacy;
            (void)disruption_apply(ev, &ctx);
            sched->processed_last += 1u;
            sched->processed_total += 1u;
            (void)dg_due_scheduler_refresh(&sched->due, due->handle);
            return DG_DUE_OK;
        }
        case RESIST_DUE_POLICY: {
            pacification_policy_event* ev = (pacification_policy_event*)due->target;
            pacification_apply_context ctx;
            occupation_refusal_code refusal;
            if (!ev || ev->status != PACIFICATION_EVENT_SCHEDULED) {
                return DG_DUE_OK;
            }
            if (ev->scheduled_act == DG_DUE_TICK_NONE ||
                ev->scheduled_act > target_tick) {
                return DG_DUE_OK;
            }
            memset(&ctx, 0, sizeof(ctx));
            ctx.policies = sched->policies;
            ctx.stores = sched->stores;
            ctx.legitimacy = sched->legitimacy;
            ctx.territory = sched->territories;
            ctx.occupations = sched->occupations;
            ctx.resistances = sched->resistances;
            if (pacification_policy_apply(ev, &ctx, &refusal) != 0) {
                ev->status = PACIFICATION_EVENT_APPLIED;
                ev->scheduled_act = DOM_TIME_ACT_MAX;
            }
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

static dg_due_vtable g_resistance_due_vtable = {
    resistance_due_next_tick,
    resistance_due_process_until
};

int resistance_scheduler_init(resistance_scheduler* sched,
                              dom_time_event* event_storage,
                              u32 event_capacity,
                              dg_due_entry* entry_storage,
                              resistance_due_user* user_storage,
                              u32 entry_capacity,
                              dom_act_time_t start_tick,
                              occupation_registry* occupations,
                              resistance_registry* resistances,
                              territory_control_registry* territories,
                              disruption_event_list* disruptions,
                              pacification_policy_registry* policies,
                              pacification_policy_event_list* policy_events,
                              legitimacy_registry* legitimacy,
                              enforcement_capacity_registry* enforcement,
                              infra_store_registry* stores,
                              transport_capacity_registry* transport,
                              survival_cohort_registry* survival_cohorts,
                              survival_needs_registry* survival_needs,
                              const survival_needs_params* needs_params)
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
    sched->occupations = occupations;
    sched->resistances = resistances;
    sched->territories = territories;
    sched->disruptions = disruptions;
    sched->policies = policies;
    sched->policy_events = policy_events;
    sched->legitimacy = legitimacy;
    sched->enforcement = enforcement;
    sched->stores = stores;
    sched->transport = transport;
    sched->survival_cohorts = survival_cohorts;
    sched->survival_needs = survival_needs;
    if (needs_params) {
        sched->needs_params = *needs_params;
    } else {
        survival_needs_params_default(&sched->needs_params);
    }
    sched->processed_last = 0u;
    sched->processed_total = 0u;
    memset(user_storage, 0, sizeof(resistance_due_user) * (size_t)entry_capacity);
    return 0;
}

static int resistance_scheduler_alloc_handle(resistance_scheduler* sched,
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

static int resistance_scheduler_register_internal(resistance_scheduler* sched,
                                                  void* target,
                                                  u32 type,
                                                  u64 stable_key)
{
    u32 handle;
    resistance_due_user* due;
    if (!sched || !target) {
        return -1;
    }
    if (resistance_scheduler_alloc_handle(sched, &handle) != 0) {
        return -2;
    }
    due = &sched->due_users[handle];
    due->scheduler = sched;
    due->type = type;
    due->target = target;
    if (dg_due_scheduler_register(&sched->due, &g_resistance_due_vtable, due,
                                  stable_key, &handle) != DG_DUE_OK) {
        return -3;
    }
    due->handle = handle;
    return 0;
}

int resistance_scheduler_register_occupation(resistance_scheduler* sched,
                                             occupation_state* state)
{
    if (!sched || !state) {
        return -1;
    }
    return resistance_scheduler_register_internal(sched, state,
                                                  RESIST_DUE_OCCUPATION,
                                                  state->occupation_id);
}

int resistance_scheduler_register_resistance(resistance_scheduler* sched,
                                             resistance_state* state)
{
    if (!sched || !state) {
        return -1;
    }
    return resistance_scheduler_register_internal(sched, state,
                                                  RESIST_DUE_RESISTANCE,
                                                  state->resistance_id);
}

int resistance_scheduler_register_disruption(resistance_scheduler* sched,
                                             disruption_event* event)
{
    if (!sched || !event) {
        return -1;
    }
    return resistance_scheduler_register_internal(sched, event,
                                                  RESIST_DUE_DISRUPTION,
                                                  event->disruption_id);
}

int resistance_scheduler_register_policy(resistance_scheduler* sched,
                                         pacification_policy_event* event)
{
    if (!sched || !event) {
        return -1;
    }
    return resistance_scheduler_register_internal(sched, event,
                                                  RESIST_DUE_POLICY,
                                                  event->event_id);
}

int resistance_scheduler_advance(resistance_scheduler* sched,
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

dom_act_time_t resistance_scheduler_next_due(const resistance_scheduler* sched)
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
