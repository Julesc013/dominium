/*
FILE: include/dominium/agents/agent_constraint.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines constraint records imposed by institutions.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Constraints ordered by constraint_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_CONSTRAINT_H
#define DOMINIUM_AGENTS_AGENT_CONSTRAINT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_constraint_mode {
    AGENT_CONSTRAINT_DENY = 0,
    AGENT_CONSTRAINT_ALLOW = 1
} agent_constraint_mode;

typedef struct agent_constraint {
    u64 constraint_id;
    u64 institution_id;
    u64 target_agent_id;
    u32 process_kind_mask;
    u32 mode;
    dom_act_time_t expiry_act;
    dom_provenance_id provenance_id;
    u32 revoked;
} agent_constraint;

typedef struct agent_constraint_registry {
    agent_constraint* entries;
    u32 count;
    u32 capacity;
} agent_constraint_registry;

void agent_constraint_registry_init(agent_constraint_registry* reg,
                                    agent_constraint* storage,
                                    u32 capacity);
agent_constraint* agent_constraint_find(agent_constraint_registry* reg,
                                        u64 constraint_id);
int agent_constraint_register(agent_constraint_registry* reg,
                              u64 constraint_id,
                              u64 institution_id,
                              u64 target_agent_id,
                              u32 process_kind_mask,
                              u32 mode,
                              dom_act_time_t expiry_act,
                              dom_provenance_id provenance_id);
int agent_constraint_revoke(agent_constraint_registry* reg,
                            u64 constraint_id);
int agent_constraint_allows_process(const agent_constraint_registry* reg,
                                    u64 agent_id,
                                    u32 process_kind,
                                    dom_act_time_t now_act,
                                    u64* out_institution_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_CONSTRAINT_H */
