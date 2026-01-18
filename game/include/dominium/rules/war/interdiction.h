/*
FILE: include/dominium/rules/war/interdiction.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic interdiction operations and scheduling hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interdiction scheduling is deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_INTERDICTION_H
#define DOMINIUM_RULES_WAR_INTERDICTION_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/war/engagement.h"
#include "dominium/rules/war/engagement_scheduler.h"
#include "dominium/rules/war/security_force.h"
#include "dominium/rules/war/route_control.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum interdiction_status {
    INTERDICTION_STATUS_SCHEDULED = 0,
    INTERDICTION_STATUS_RESOLVED = 1,
    INTERDICTION_STATUS_FAILED = 2
} interdiction_status;

typedef enum interdiction_refusal_code {
    INTERDICTION_REFUSAL_NONE = 0,
    INTERDICTION_REFUSAL_INSUFFICIENT_FORCES = 1,
    INTERDICTION_REFUSAL_ROUTE_NOT_FOUND = 2,
    INTERDICTION_REFUSAL_OUT_OF_AUTHORITY = 3
} interdiction_refusal_code;

const char* interdiction_refusal_to_string(interdiction_refusal_code code);

typedef struct interdiction_operation {
    u64 interdiction_id;
    u64 route_id;
    u64 attacker_force_ref;
    u64 defender_force_ref;
    u32 domain_scope;
    u32 target_policy_mask;
    dom_act_time_t schedule_act;
    dom_act_time_t resolution_delay;
    dom_act_time_t next_due_tick;
    u32 status;
    u64 engagement_id;
    u64 authority_ref;
    u32 require_authority;
    u32 repeat_interval;
    u64 provenance_ref;
} interdiction_operation;

typedef struct interdiction_registry {
    interdiction_operation* operations;
    u32 count;
    u32 capacity;
    u64 next_id;
} interdiction_registry;

typedef struct interdiction_context {
    route_control_registry* routes;
    security_force_registry* forces;
    engagement_registry* engagements;
    engagement_scheduler* scheduler;
} interdiction_context;

void interdiction_registry_init(interdiction_registry* reg,
                                interdiction_operation* storage,
                                u32 capacity,
                                u64 start_id);
interdiction_operation* interdiction_find(interdiction_registry* reg,
                                          u64 interdiction_id);
int interdiction_register(interdiction_registry* reg,
                          const interdiction_operation* input,
                          u64* out_id);

int interdiction_apply(interdiction_operation* op,
                       interdiction_context* ctx,
                       interdiction_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_INTERDICTION_H */
