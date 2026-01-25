/*
FILE: include/dominium/agents/agent_authority.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines authority grants, revocations, and deterministic resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Grants ordered by grant_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_AUTHORITY_H
#define DOMINIUM_AGENTS_AGENT_AUTHORITY_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_authority_grant {
    u64 grant_id;
    u64 granter_id;
    u64 grantee_id;
    u32 authority_mask;
    dom_act_time_t expiry_act;
    u32 revoked;
    dom_provenance_id provenance_id;
} agent_authority_grant;

typedef struct agent_authority_registry {
    agent_authority_grant* entries;
    u32 count;
    u32 capacity;
} agent_authority_registry;

void agent_authority_registry_init(agent_authority_registry* reg,
                                   agent_authority_grant* storage,
                                   u32 capacity);
agent_authority_grant* agent_authority_find(agent_authority_registry* reg,
                                            u64 grant_id);
int agent_authority_grant_register(agent_authority_registry* reg,
                                   u64 grant_id,
                                   u64 granter_id,
                                   u64 grantee_id,
                                   u32 authority_mask,
                                   dom_act_time_t expiry_act,
                                   dom_provenance_id provenance_id);
int agent_authority_grant_revoke(agent_authority_registry* reg,
                                 u64 grant_id);
u32 agent_authority_effective_mask(const agent_authority_registry* reg,
                                   u64 grantee_id,
                                   u32 base_mask,
                                   dom_act_time_t now_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_AUTHORITY_H */
