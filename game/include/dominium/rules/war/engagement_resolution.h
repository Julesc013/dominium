/*
FILE: include/dominium/rules/war/engagement_resolution.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic engagement resolution interfaces.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resolution outcomes are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_ENGAGEMENT_RESOLUTION_H
#define DOMINIUM_RULES_WAR_ENGAGEMENT_RESOLUTION_H

#include "dominium/epistemic.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/war/casualty_generator.h"
#include "dominium/rules/war/engagement.h"
#include "dominium/rules/war/military_cohort.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"
#include "dominium/rules/war/loss_accounting.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct engagement_casualty_config {
    u32 cause_code;
    u32 policy_id;
    dom_account_id_t remains_inventory_account_id;
    u64 jurisdiction_id;
    u8 has_contract;
    u8 allow_finder;
    u8 jurisdiction_allows;
    u8 estate_locked;
    u8 collapse_remains;
    u64 location_ref;
} engagement_casualty_config;

typedef struct engagement_casualty_source {
    u64 force_id;
    casualty_source source;
} engagement_casualty_source;

typedef struct engagement_resolution_context {
    security_force_registry* forces;
    military_cohort_registry* military;
    readiness_registry* readiness;
    morale_registry* morale;
    legitimacy_registry* legitimacy;
    infra_store_registry* stores;
    casualty_generator* casualty_gen;
    engagement_casualty_source* casualty_sources;
    u32 casualty_source_count;
    engagement_outcome_list* outcomes;
    engagement_casualty_config casualty_config;
} engagement_resolution_context;

int engagement_resolve(const engagement* engagement,
                       engagement_resolution_context* ctx,
                       engagement_outcome* out_outcome,
                       engagement_refusal_code* out_refusal);

typedef struct engagement_outcome_summary {
    u32 casualty_count;
    u32 equipment_loss_count;
    i32 morale_delta;
    i32 legitimacy_delta;
    u32 uncertainty_q16;
    int is_exact;
} engagement_outcome_summary;

int engagement_outcome_estimate_from_view(const dom_epistemic_view* view,
                                          const engagement_outcome* outcome,
                                          engagement_outcome_summary* out_summary);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_ENGAGEMENT_RESOLUTION_H */
