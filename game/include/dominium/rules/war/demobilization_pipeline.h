/*
FILE: include/dominium/rules/war/demobilization_pipeline.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic demobilization pipeline for security forces.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Demobilization ordering and results are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_DEMOBILIZATION_PIPELINE_H
#define DOMINIUM_RULES_WAR_DEMOBILIZATION_PIPELINE_H

#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/war/military_cohort.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct demobilization_request {
    u64 force_id;
    u64 equipment_store_ref;
    u64 population_cohort_id;
    u64 provenance_ref;
    dom_act_time_t now_act;
} demobilization_request;

typedef struct demobilization_context {
    security_force_registry* forces;
    military_cohort_registry* military_cohorts;
    population_cohort_registry* population;
    readiness_registry* readiness;
    morale_registry* morale;
    infra_store_registry* stores;
} demobilization_context;

int war_demobilization_apply(const demobilization_request* req,
                             demobilization_context* ctx,
                             war_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_DEMOBILIZATION_PIPELINE_H */
