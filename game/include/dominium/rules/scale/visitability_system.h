/*
FILE: include/dominium/rules/scale/visitability_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Deterministic visitability evaluation and enforcement helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: All outcomes are pure functions of inputs; no wall-clock use.
*/
#ifndef DOMINIUM_RULES_SCALE_VISITABILITY_SYSTEM_H
#define DOMINIUM_RULES_SCALE_VISITABILITY_SYSTEM_H

#include "domino/world/domain_volume.h"
#include "dominium/fidelity.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_visitability_outcome {
    DOM_VISIT_ACCEPT = 0,
    DOM_VISIT_DEFER = 1,
    DOM_VISIT_REFUSE = 2
} dom_visitability_outcome;

typedef enum dom_visitability_refusal_reason {
    DOM_VISIT_REFUSE_NONE = 0,
    DOM_VISIT_REFUSE_UNREACHABLE = 1,
    DOM_VISIT_REFUSE_DOMAIN_FORBIDDEN = 2,
    DOM_VISIT_REFUSE_LAW_FORBIDDEN = 3,
    DOM_VISIT_REFUSE_EXISTENCE_INVALID = 4,
    DOM_VISIT_REFUSE_NO_CONTRACT = 5,
    DOM_VISIT_REFUSE_ARCHIVAL_BLOCKED = 6,
    DOM_VISIT_REFUSE_BUDGET_INSUFFICIENT = 7,
    DOM_VISIT_REFUSE_INTERNAL = 8
} dom_visitability_refusal_reason;

enum dom_visitability_flags {
    DOM_VISIT_FLAG_NONE = 0u,
    DOM_VISIT_FLAG_REFINEMENT_REQUIRED = 1u << 0u,
    DOM_VISIT_FLAG_DEGRADED = 1u << 1u,
    DOM_VISIT_FLAG_ADMIN_OVERRIDE = 1u << 2u,
    DOM_VISIT_FLAG_FORK_REQUIRED = 1u << 3u,
    DOM_VISIT_FLAG_AUDIT_REQUIRED = 1u << 4u
};

typedef struct dom_visitability_budget_gate {
    u32 required_units;
    u32 available_units;
    u32 allow_defer;
    u32 allow_degrade;
    dom_fidelity_tier degrade_tier;
    dom_act_time_t defer_ticks;
} dom_visitability_budget_gate;

typedef struct dom_visitability_request {
    dom_domain_id domain_id;
    u32 existence_state; /* dom_domain_existence_state */
    u32 archival_state;  /* dom_domain_archival_state */
    d_bool travel_allowed;
    d_bool domain_allowed;
    d_bool law_allowed;
    d_bool has_refinement_contract;
    d_bool allow_archival_fork;
    d_bool admin_override;
    dom_fidelity_tier required_tier;
    dom_act_time_t now_tick;
    dom_visitability_budget_gate budget;
} dom_visitability_request;

typedef struct dom_visitability_result {
    u32 outcome; /* dom_visitability_outcome */
    u32 refusal_reason; /* dom_visitability_refusal_reason */
    u32 flags;
    dom_fidelity_tier required_tier;
    dom_fidelity_tier resolved_tier;
    dom_act_time_t defer_until_tick;
} dom_visitability_result;

void dom_visitability_request_init(dom_visitability_request* request);
void dom_visitability_result_init(dom_visitability_result* result);
int dom_visitability_evaluate(const dom_visitability_request* request,
                              dom_visitability_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_VISITABILITY_SYSTEM_H */
