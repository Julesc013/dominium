/*
FILE: include/dominium/rules/knowledge/secrecy_controls.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / knowledge
RESPONSIBILITY: Defines secrecy policies for knowledge diffusion.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Secrecy decisions are deterministic.
*/
#ifndef DOMINIUM_RULES_KNOWLEDGE_SECRECY_CONTROLS_H
#define DOMINIUM_RULES_KNOWLEDGE_SECRECY_CONTROLS_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct knowledge_secrecy_policy {
    u64 policy_id;
    u32 allow_diffusion;
    u32 min_fidelity;
} knowledge_secrecy_policy;

typedef struct knowledge_secrecy_registry {
    knowledge_secrecy_policy* policies;
    u32 count;
    u32 capacity;
} knowledge_secrecy_registry;

void knowledge_secrecy_registry_init(knowledge_secrecy_registry* reg,
                                     knowledge_secrecy_policy* storage,
                                     u32 capacity);
int knowledge_secrecy_register(knowledge_secrecy_registry* reg,
                               u64 policy_id,
                               u32 allow_diffusion,
                               u32 min_fidelity);
knowledge_secrecy_policy* knowledge_secrecy_find(knowledge_secrecy_registry* reg,
                                                 u64 policy_id);
int knowledge_secrecy_allows(const knowledge_secrecy_policy* policy,
                             u32 fidelity);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_KNOWLEDGE_SECRECY_CONTROLS_H */
