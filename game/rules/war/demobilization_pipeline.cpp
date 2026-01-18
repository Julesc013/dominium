/*
FILE: game/rules/war/demobilization_pipeline.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic demobilization for security forces.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Demobilization ordering and results are deterministic.
*/
#include "dominium/rules/war/demobilization_pipeline.h"

#include <string.h>

int war_demobilization_apply(const demobilization_request* req,
                             demobilization_context* ctx,
                             war_refusal_code* out_refusal)
{
    u32 i;
    u64 cohort_id;
    security_force* force;
    military_cohort* cohort;
    readiness_state* readiness;
    morale_state* morale;

    if (out_refusal) {
        *out_refusal = WAR_REFUSAL_NONE;
    }
    if (!req || !ctx || !ctx->forces || !ctx->military_cohorts ||
        !ctx->population || !ctx->readiness || !ctx->morale || !ctx->stores) {
        return -1;
    }
    force = security_force_find(ctx->forces, req->force_id);
    if (!force) {
        if (out_refusal) {
            *out_refusal = WAR_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return -2;
    }
    cohort_id = req->population_cohort_id ? req->population_cohort_id : force->cohort_ref;
    if (cohort_id == 0u) {
        return -3;
    }
    cohort = military_cohort_find(ctx->military_cohorts, cohort_id);
    if (!cohort) {
        return -4;
    }

    if (cohort->count > 0u) {
        (void)population_cohort_adjust_count(ctx->population,
                                             cohort_id,
                                             (i32)cohort->count,
                                             0);
    }

    for (i = 0u; i < force->equipment_count; ++i) {
        if (force->equipment_refs[i] == 0u || force->equipment_qtys[i] == 0u) {
            continue;
        }
        (void)infra_store_add(ctx->stores,
                              req->equipment_store_ref,
                              force->equipment_refs[i],
                              force->equipment_qtys[i]);
    }

    (void)military_cohort_release(ctx->military_cohorts, cohort_id);

    readiness = readiness_find(ctx->readiness, force->readiness_state_ref);
    if (readiness) {
        readiness->readiness_level = 0u;
        readiness->last_update_act = req->now_act;
        readiness->next_due_tick = DOM_TIME_ACT_MAX;
    }
    morale = morale_find(ctx->morale, force->morale_state_ref);
    if (morale) {
        morale->morale_level = 0u;
        morale->next_due_tick = DOM_TIME_ACT_MAX;
    }

    force->equipment_count = 0u;
    force->logistics_dependency_count = 0u;
    force->next_due_tick = DOM_TIME_ACT_MAX;
    force->provenance_ref = req->provenance_ref ? req->provenance_ref : force->provenance_ref;
    force->status = SECURITY_FORCE_DEMOBILIZED;
    return 0;
}
