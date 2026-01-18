/*
FILE: game/rules/war/mobilization_pipeline.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic mobilization for security forces.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Mobilization ordering and results are deterministic.
*/
#include "dominium/rules/war/mobilization_pipeline.h"

#include <string.h>

static int war_check_equipment_available(const mobilization_request* req,
                                         infra_store_registry* stores)
{
    u32 i;
    u32 qty = 0u;
    if (!req || !stores) {
        return -1;
    }
    for (i = 0u; i < req->equipment_count; ++i) {
        u64 asset_id = req->equipment_asset_ids[i];
        u32 need_qty = req->equipment_qtys[i];
        if (asset_id == 0u || need_qty == 0u) {
            return -2;
        }
        if (infra_store_get_qty(stores, req->equipment_store_ref, asset_id, &qty) != 0) {
            return -3;
        }
        if (qty < need_qty) {
            return -4;
        }
    }
    return 0;
}

static int war_consume_equipment(const mobilization_request* req,
                                 infra_store_registry* stores,
                                 u32* out_consumed_count)
{
    u32 i;
    if (out_consumed_count) {
        *out_consumed_count = 0u;
    }
    if (!req || !stores) {
        return -1;
    }
    for (i = 0u; i < req->equipment_count; ++i) {
        u64 asset_id = req->equipment_asset_ids[i];
        u32 need_qty = req->equipment_qtys[i];
        if (infra_store_consume(stores, req->equipment_store_ref, asset_id, need_qty) != 0) {
            return -2;
        }
        if (out_consumed_count) {
            *out_consumed_count = i + 1u;
        }
    }
    return 0;
}

static void war_refund_equipment(const mobilization_request* req,
                                 infra_store_registry* stores,
                                 u32 consumed_count)
{
    u32 i;
    if (!req || !stores) {
        return;
    }
    for (i = 0u; i < consumed_count; ++i) {
        u64 asset_id = req->equipment_asset_ids[i];
        u32 qty = req->equipment_qtys[i];
        if (asset_id == 0u || qty == 0u) {
            continue;
        }
        (void)infra_store_add(stores, req->equipment_store_ref, asset_id, qty);
    }
}

static u64 war_assign_force_id(const mobilization_request* req,
                               const mobilization_context* ctx)
{
    u64 assigned = req ? req->force_id : 0u;
    if (assigned != 0u) {
        return assigned;
    }
    if (!ctx || !ctx->forces) {
        return 0u;
    }
    assigned = ctx->forces->next_force_id ? ctx->forces->next_force_id : 1u;
    if (assigned == 0u) {
        assigned = 1u;
    }
    return assigned;
}

int war_mobilization_apply(const mobilization_request* req,
                           mobilization_context* ctx,
                           war_refusal_code* out_refusal,
                           mobilization_result* out_result)
{
    u32 i;
    u32 consumed = 0u;
    u64 force_id;
    u64 readiness_id;
    u64 morale_id;
    security_force* force;
    readiness_state* readiness;
    morale_state* morale;
    population_cohort_state* population;
    enforcement_capacity* enforcement;
    legitimacy_state* legitimacy;
    i32 readiness_delta;

    if (out_refusal) {
        *out_refusal = WAR_REFUSAL_NONE;
    }
    if (out_result) {
        memset(out_result, 0, sizeof(*out_result));
    }
    if (!req || !ctx || !ctx->forces || !ctx->military_cohorts ||
        !ctx->population || !ctx->readiness || !ctx->morale ||
        !ctx->stores || !ctx->readiness_sched || !ctx->morale_sched) {
        return -1;
    }
    if (req->population_count == 0u || req->population_cohort_id == 0u) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_POPULATION;
        }
        return -2;
    }
    if (req->equipment_count > SECURITY_FORCE_MAX_EQUIPMENT) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_EQUIPMENT;
        }
        return -3;
    }
    if (req->logistics_dependency_count == 0u ||
        req->logistics_dependency_count > SECURITY_FORCE_MAX_LOGISTICS ||
        req->supply_asset_id == 0u || req->supply_qty == 0u) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_LOGISTICS;
        }
        return -4;
    }
    if (security_force_find(ctx->forces, req->force_id) != 0) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return -5;
    }
    if (ctx->military_cohorts &&
        military_cohort_find(ctx->military_cohorts, req->population_cohort_id) != 0) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return -6;
    }
    if (ctx->forces->count >= ctx->forces->capacity ||
        ctx->military_cohorts->count >= ctx->military_cohorts->capacity ||
        ctx->readiness->count >= ctx->readiness->capacity ||
        ctx->morale->count >= ctx->morale->capacity) {
        return -7;
    }
    population = population_cohort_find(ctx->population, req->population_cohort_id);
    if (!population || population->count < req->population_count) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_POPULATION;
        }
        return -8;
    }
    if (war_check_equipment_available(req, ctx->stores) != 0) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_EQUIPMENT;
        }
        return -9;
    }
    if (req->enforcement_capacity_id != 0u) {
        if (!ctx->enforcement) {
            if (out_refusal) {
                *out_refusal = WAR_REFUSAL_INSUFFICIENT_AUTHORITY;
            }
            return -10;
        }
        enforcement = enforcement_capacity_find(ctx->enforcement, req->enforcement_capacity_id);
        if (!enforcement || enforcement->available_enforcers < req->population_count) {
            if (out_refusal) {
                *out_refusal = WAR_REFUSAL_INSUFFICIENT_AUTHORITY;
            }
            return -10;
        }
    }
    legitimacy = 0;
    if (req->legitimacy_id != 0u) {
        if (!ctx->legitimacy) {
            if (out_refusal) {
                *out_refusal = WAR_REFUSAL_INSUFFICIENT_LEGITIMACY;
            }
            return -11;
        }
        legitimacy = legitimacy_find(ctx->legitimacy, req->legitimacy_id);
        if (!legitimacy || legitimacy->value < req->legitimacy_min) {
            if (out_refusal) {
                *out_refusal = WAR_REFUSAL_INSUFFICIENT_LEGITIMACY;
            }
            return -11;
        }
    }

    force_id = war_assign_force_id(req, ctx);
    if (force_id == 0u) {
        return -12;
    }
    readiness_id = req->readiness_id ? req->readiness_id : force_id;
    morale_id = req->morale_id ? req->morale_id : force_id;

    if (readiness_find(ctx->readiness, readiness_id) != 0 ||
        morale_find(ctx->morale, morale_id) != 0) {
        return -13;
    }

    if (security_force_register(ctx->forces,
                                req->force_id,
                                req->owning_org_or_jurisdiction,
                                req->domain_scope,
                                req->population_cohort_id,
                                req->provenance_ref) != 0) {
        return -14;
    }
    force = security_force_find(ctx->forces, force_id);
    if (!force) {
        return -15;
    }

    if (war_consume_equipment(req, ctx->stores, &consumed) != 0) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_EQUIPMENT;
        }
        return -16;
    }

    if (population_cohort_adjust_count(ctx->population,
                                       req->population_cohort_id,
                                       -(i32)req->population_count,
                                       0) != 0) {
        war_refund_equipment(req, ctx->stores, consumed);
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_POPULATION;
        }
        return -17;
    }

    if (military_cohort_register(ctx->military_cohorts,
                                 req->population_cohort_id,
                                 force_id,
                                 req->population_count,
                                 MILITARY_ROLE_INFANTRY,
                                 req->provenance_ref) != 0) {
        (void)population_cohort_adjust_count(ctx->population,
                                             req->population_cohort_id,
                                             (i32)req->population_count,
                                             0);
        war_refund_equipment(req, ctx->stores, consumed);
        return -18;
    }

    if (readiness_register(ctx->readiness,
                           readiness_id,
                           req->readiness_start,
                           req->readiness_degradation_rate,
                           req->readiness_recovery_rate) != 0) {
        return -19;
    }
    readiness = readiness_find(ctx->readiness, readiness_id);
    if (readiness) {
        readiness->last_update_act = req->now_act;
        readiness->readiness_level = (req->readiness_start > READINESS_SCALE)
            ? READINESS_SCALE : req->readiness_start;
    }

    if (morale_register(ctx->morale,
                        morale_id,
                        req->morale_start,
                        0) != 0) {
        return -20;
    }
    morale = morale_find(ctx->morale, morale_id);
    if (morale) {
        morale->morale_level = (req->morale_start > MORALE_SCALE)
            ? MORALE_SCALE : req->morale_start;
    }

    readiness_delta = (i32)req->readiness_target - (i32)req->readiness_start;
    if (readiness_delta != 0 && req->readiness_ramp_act != DG_DUE_TICK_NONE) {
        (void)readiness_schedule_event(ctx->readiness_sched,
                                       readiness_id,
                                       readiness_delta,
                                       req->readiness_ramp_act);
    }
    if (req->supply_check_act != DG_DUE_TICK_NONE) {
        (void)readiness_schedule_supply_check(ctx->readiness_sched,
                                              readiness_id,
                                              req->supply_check_act,
                                              req->logistics_dependency_refs[0],
                                              req->supply_asset_id,
                                              req->supply_qty,
                                              -(i32)req->readiness_degradation_rate);
    }
    if (req->legitimacy_id != 0u && req->morale_legitimacy_delta != 0) {
        (void)morale_schedule_legitimacy_check(ctx->morale_sched,
                                               morale_id,
                                               req->now_act,
                                               req->legitimacy_id,
                                               req->legitimacy_min,
                                               req->morale_legitimacy_delta);
    }

    for (i = 0u; i < req->equipment_count; ++i) {
        (void)security_force_add_equipment(ctx->forces,
                                           force_id,
                                           req->equipment_asset_ids[i],
                                           req->equipment_qtys[i]);
    }
    for (i = 0u; i < req->logistics_dependency_count; ++i) {
        (void)security_force_add_logistics_dependency(ctx->forces,
                                                      force_id,
                                                      req->logistics_dependency_refs[i]);
    }
    (void)security_force_set_states(ctx->forces, force_id, readiness_id, morale_id);
    (void)security_force_set_status(ctx->forces, force_id, SECURITY_FORCE_MOBILIZING);

    force->next_due_tick = DOM_TIME_ACT_MAX;
    readiness = readiness_find(ctx->readiness, readiness_id);
    if (readiness && readiness->next_due_tick < force->next_due_tick) {
        force->next_due_tick = readiness->next_due_tick;
    }
    morale = morale_find(ctx->morale, morale_id);
    if (morale && morale->next_due_tick < force->next_due_tick) {
        force->next_due_tick = morale->next_due_tick;
    }

    if (out_result) {
        out_result->force_id = force_id;
        out_result->military_cohort_id = req->population_cohort_id;
        out_result->readiness_id = readiness_id;
        out_result->morale_id = morale_id;
    }
    return 0;
}
