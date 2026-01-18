/*
FILE: include/dominium/rules/technology/tech_activation.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / technology
RESPONSIBILITY: Defines deterministic technology activation rules.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Activation checks are deterministic.
*/
#ifndef DOMINIUM_RULES_TECH_ACTIVATION_H
#define DOMINIUM_RULES_TECH_ACTIVATION_H

#include "domino/core/dom_time_core.h"
#include "dominium/rules/technology/tech_prerequisites.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tech_activation_status {
    TECH_INACTIVE = 0,
    TECH_ACTIVE = 1,
    TECH_REFUSED = 2
} tech_activation_status;

typedef struct tech_activation {
    u64 tech_id;
    u64 actor_id;
    tech_activation_status status;
    dom_act_time_t activated_act;
} tech_activation;

typedef struct tech_activation_registry {
    tech_activation* activations;
    u32 count;
    u32 capacity;
} tech_activation_registry;

void tech_activation_registry_init(tech_activation_registry* reg,
                                   tech_activation* storage,
                                   u32 capacity);
int tech_activation_request(tech_activation_registry* reg,
                            const tech_prereq_registry* prereqs,
                            const knowledge_registry* knowledge,
                            u64 tech_id,
                            u64 actor_id,
                            dom_act_time_t act,
                            int acknowledged);
int tech_activation_is_active(const tech_activation_registry* reg,
                              u64 tech_id,
                              u64 actor_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_TECH_ACTIVATION_H */
