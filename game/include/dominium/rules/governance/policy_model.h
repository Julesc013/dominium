/*
FILE: include/dominium/rules/governance/policy_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines policy records, schedules, and standards resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Policy ordering is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_POLICY_MODEL_H
#define DOMINIUM_RULES_GOVERNANCE_POLICY_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum policy_type {
    POLICY_TAXATION = 1,
    POLICY_CURFEW = 2,
    POLICY_PROPERTY_ENFORCEMENT = 3,
    POLICY_ELECTION_SCHEDULE = 4
} policy_type;

typedef struct policy_schedule {
    dom_act_time_t start_act;
    dom_act_time_t interval_act;
} policy_schedule;

typedef struct policy_record {
    u64 policy_id;
    u64 jurisdiction_id;
    policy_type type;
    policy_schedule schedule;
    u32 legitimacy_min;
    u32 capacity_min;
    dom_act_time_t next_due_tick;
} policy_record;

typedef struct policy_registry {
    policy_record* policies;
    u32 count;
    u32 capacity;
} policy_registry;

void policy_registry_init(policy_registry* reg,
                          policy_record* storage,
                          u32 capacity);
int policy_register(policy_registry* reg,
                    const policy_record* policy);
policy_record* policy_find(policy_registry* reg, u64 policy_id);
dom_act_time_t policy_next_due(const policy_record* policy, dom_act_time_t now_tick);

typedef struct governance_epistemic_set {
    const u64* known_policy_ids;
    u32 count;
} governance_epistemic_set;

int policy_epistemic_knows(const governance_epistemic_set* set, u64 policy_id);

typedef struct standard_resolution_context {
    u64 explicit_standard_id;
    u64 org_standard_id;
    u64 jurisdiction_standard_id;
    u64 personal_standard_id;
    u64 fallback_standard_id;
} standard_resolution_context;

u64 governance_resolve_standard(const standard_resolution_context* ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_POLICY_MODEL_H */
