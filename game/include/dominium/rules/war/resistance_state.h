/*
FILE: include/dominium/rules/war/resistance_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic resistance state records and updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resistance updates are deterministic and event-driven.
*/
#ifndef DOMINIUM_RULES_WAR_RESISTANCE_STATE_H
#define DOMINIUM_RULES_WAR_RESISTANCE_STATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/epistemic.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/war/occupation_state.h"

#ifdef __cplusplus
extern "C" {
#endif

#define RESISTANCE_SCALE 1000u

typedef enum resistance_status {
    RESISTANCE_STATUS_LATENT = 0,
    RESISTANCE_STATUS_ACTIVE = 1,
    RESISTANCE_STATUS_SUPPRESSED = 2
} resistance_status;

typedef struct resistance_state {
    u64 resistance_id;
    u64 territory_id;
    u64 legitimacy_id;
    u64 population_cohort_id;
    u32 resistance_pressure;
    u32 legitimacy_min;
    u32 deprivation_threshold;
    u32 coercion_threshold;
    u32 activation_threshold;
    u32 suppression_threshold;
    u32 pressure_decay;
    u32 pressure_gain_base;
    u32 coercion_level;
    u32 disruption_interval;
    u32 disruption_delay;
    dom_act_time_t next_disruption_act;
    u64 disruption_transport_capacity_id;
    u64 disruption_supply_store_ref;
    u64 disruption_supply_asset_id;
    u32 disruption_supply_qty;
    u32 update_interval;
    dom_act_time_t next_due_tick;
    u32 status;
    u64 provenance_ref;
} resistance_state;

typedef struct resistance_registry {
    resistance_state* states;
    u32 count;
    u32 capacity;
    u64 next_id;
} resistance_registry;

typedef struct resistance_update_context {
    legitimacy_registry* legitimacy;
    survival_needs_registry* needs;
    survival_cohort_registry* cohorts;
    survival_needs_params needs_params;
    dom_act_time_t now_act;
} resistance_update_context;

typedef struct resistance_estimate {
    u32 pressure;
    u32 status;
    u32 uncertainty_q16;
    int is_exact;
} resistance_estimate;

void resistance_registry_init(resistance_registry* reg,
                              resistance_state* storage,
                              u32 capacity,
                              u64 start_id);
resistance_state* resistance_find(resistance_registry* reg,
                                  u64 resistance_id);
resistance_state* resistance_find_by_territory(resistance_registry* reg,
                                               u64 territory_id);
int resistance_register(resistance_registry* reg,
                        const resistance_state* input,
                        u64* out_id);
int resistance_set_next_due(resistance_registry* reg,
                            u64 resistance_id,
                            dom_act_time_t next_due_tick);

int resistance_apply_update(resistance_state* state,
                            const occupation_state* occupation,
                            resistance_update_context* ctx);

int resistance_estimate_from_view(const dom_epistemic_view* view,
                                  const resistance_state* actual,
                                  resistance_estimate* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_RESISTANCE_STATE_H */
