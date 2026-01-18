/*
FILE: include/dominium/rules/governance/org_governance_binding.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / governance
RESPONSIBILITY: Defines organization to jurisdiction bindings.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Binding order is stable and deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_ORG_BINDING_H
#define DOMINIUM_RULES_GOVERNANCE_ORG_BINDING_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct org_governance_binding {
    u64 org_id;
    u64 jurisdiction_id;
    u64 legitimacy_ref;
    u64 enforcement_capacity_ref;
} org_governance_binding;

typedef struct org_governance_registry {
    org_governance_binding* bindings;
    u32 count;
    u32 capacity;
} org_governance_registry;

void org_governance_registry_init(org_governance_registry* reg,
                                  org_governance_binding* storage,
                                  u32 capacity);
int org_governance_register(org_governance_registry* reg,
                            u64 org_id,
                            u64 jurisdiction_id,
                            u64 legitimacy_ref,
                            u64 enforcement_ref);
org_governance_binding* org_governance_find(org_governance_registry* reg,
                                            u64 org_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_GOVERNANCE_ORG_BINDING_H */
