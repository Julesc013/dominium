/*
FILE: include/dominium/rules/war/mobilization_pipeline.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic mobilization pipeline for security forces.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Mobilization ordering and results are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_MOBILIZATION_PIPELINE_H
#define DOMINIUM_RULES_WAR_MOBILIZATION_PIPELINE_H

#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/war/military_cohort.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct mobilization_request {
    u64 force_id;
    u64 owning_org_or_jurisdiction;
    u32 domain_scope;
    u64 population_cohort_id;
    u32 population_count;
    u64 equipment_store_ref;
    u64 equipment_asset_ids[SECURITY_FORCE_MAX_EQUIPMENT];
    u32 equipment_qtys[SECURITY_FORCE_MAX_EQUIPMENT];
    u32 equipment_count;
    u64 logistics_dependency_refs[SECURITY_FORCE_MAX_LOGISTICS];
    u32 logistics_dependency_count;
    u64 readiness_id;
    u32 readiness_start;
    u32 readiness_target;
    u32 readiness_degradation_rate;
    u32 readiness_recovery_rate;
    dom_act_time_t readiness_ramp_act;
    u64 morale_id;
    u32 morale_start;
    i32 morale_legitimacy_delta;
    u64 legitimacy_id;
    u32 legitimacy_min;
    u64 enforcement_capacity_id;
    u64 provenance_ref;
    dom_act_time_t now_act;
    dom_act_time_t supply_check_act;
    u64 supply_asset_id;
    u32 supply_qty;
} mobilization_request;

typedef struct mobilization_result {
    u64 force_id;
    u64 military_cohort_id;
    u64 readiness_id;
    u64 morale_id;
} mobilization_result;

typedef struct mobilization_context {
    security_force_registry* forces;
    military_cohort_registry* military_cohorts;
    population_cohort_registry* population;
    readiness_registry* readiness;
    readiness_scheduler* readiness_sched;
    morale_registry* morale;
    morale_scheduler* morale_sched;
    infra_store_registry* stores;
    legitimacy_registry* legitimacy;
    enforcement_capacity_registry* enforcement;
} mobilization_context;

int war_mobilization_apply(const mobilization_request* req,
                           mobilization_context* ctx,
                           war_refusal_code* out_refusal,
                           mobilization_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_MOBILIZATION_PIPELINE_H */
