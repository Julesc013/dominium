/*
FILE: include/dominium/rules/war/siege_effects.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic siege effects and deprivation updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Siege updates are deterministic and event-driven.
*/
#ifndef DOMINIUM_RULES_WAR_SIEGE_EFFECTS_H
#define DOMINIUM_RULES_WAR_SIEGE_EFFECTS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define SIEGE_PRESSURE_SCALE 1000u

typedef enum siege_status {
    SIEGE_STATUS_ACTIVE = 0,
    SIEGE_STATUS_ENDED = 1
} siege_status;

typedef struct siege_state {
    u64 siege_id;
    u64 target_domain_ref;
    u64 population_cohort_id;
    u64 legitimacy_id;
    u32 deprivation_pressure;
    u32 deprivation_threshold;
    u32 pressure_gain_base;
    u32 pressure_decay;
    i32 legitimacy_delta;
    u32 update_interval;
    dom_act_time_t next_due_tick;
    u32 status;
    u64 provenance_ref;
} siege_state;

typedef struct siege_registry {
    siege_state* states;
    u32 count;
    u32 capacity;
    u64 next_id;
} siege_registry;

typedef struct siege_update_context {
    legitimacy_registry* legitimacy;
    survival_needs_registry* needs;
    survival_cohort_registry* cohorts;
    survival_needs_params needs_params;
    dom_act_time_t now_act;
} siege_update_context;

void siege_registry_init(siege_registry* reg,
                         siege_state* storage,
                         u32 capacity,
                         u64 start_id);
siege_state* siege_find(siege_registry* reg,
                        u64 siege_id);
int siege_register(siege_registry* reg,
                   const siege_state* input,
                   u64* out_id);
int siege_apply_update(siege_state* state,
                       siege_update_context* ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_SIEGE_EFFECTS_H */
