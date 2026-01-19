/*
FILE: include/dominium/agents/agent_role.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines agent roles and deterministic role registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Role ordering is deterministic by role_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_ROLE_H
#define DOMINIUM_AGENTS_AGENT_ROLE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_role {
    u64 role_id;
    u64 default_doctrine_ref;
    u32 authority_requirements;
    u32 capability_requirements;
} agent_role;

typedef struct agent_role_registry {
    agent_role* roles;
    u32 count;
    u32 capacity;
} agent_role_registry;

void agent_role_registry_init(agent_role_registry* reg,
                              agent_role* storage,
                              u32 capacity);
agent_role* agent_role_find(agent_role_registry* reg,
                            u64 role_id);
int agent_role_register(agent_role_registry* reg,
                        u64 role_id,
                        u64 default_doctrine_ref,
                        u32 authority_requirements,
                        u32 capability_requirements);
int agent_role_requirements_ok(const agent_role* role,
                               u32 authority_mask,
                               u32 capability_mask);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_ROLE_H */
