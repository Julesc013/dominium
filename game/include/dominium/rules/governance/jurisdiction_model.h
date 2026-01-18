/*
FILE: include/dominium/rules/governance/jurisdiction_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines jurisdiction records and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Jurisdiction ordering is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_JURISDICTION_MODEL_H
#define DOMINIUM_RULES_GOVERNANCE_JURISDICTION_MODEL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct jurisdiction_record {
    u64 jurisdiction_id;
    u64 boundary_ref;
    u64 default_time_standard_id;
    u64 default_money_standard_id;
    u64 policy_set_id;
    u64 enforcement_capacity_ref;
    u64 legitimacy_ref;
    dom_act_time_t next_due_tick;
} jurisdiction_record;

typedef struct jurisdiction_registry {
    jurisdiction_record* records;
    u32 count;
    u32 capacity;
} jurisdiction_registry;

void jurisdiction_registry_init(jurisdiction_registry* reg,
                                jurisdiction_record* storage,
                                u32 capacity);
int jurisdiction_register(jurisdiction_registry* reg,
                          u64 jurisdiction_id,
                          u64 boundary_ref,
                          u64 time_standard_id,
                          u64 money_standard_id);
jurisdiction_record* jurisdiction_find(jurisdiction_registry* reg,
                                       u64 jurisdiction_id);
int jurisdiction_set_policy(jurisdiction_registry* reg,
                            u64 jurisdiction_id,
                            u64 policy_set_id);
int jurisdiction_set_refs(jurisdiction_registry* reg,
                          u64 jurisdiction_id,
                          u64 legitimacy_ref,
                          u64 enforcement_ref);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_JURISDICTION_MODEL_H */
