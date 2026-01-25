/*
FILE: include/dominium/agents/agent_conflict.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines conflict records between agents/institutions.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Conflicts ordered by conflict_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_CONFLICT_H
#define DOMINIUM_AGENTS_AGENT_CONFLICT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_conflict_status {
    AGENT_CONFLICT_ACTIVE = 0,
    AGENT_CONFLICT_RESOLVED = 1
} agent_conflict_status;

typedef struct agent_conflict {
    u64 conflict_id;
    u64 party_a_id;
    u64 party_b_id;
    u64 subject_id;
    u32 status;
    dom_act_time_t started_act;
    dom_act_time_t resolved_act;
    dom_provenance_id provenance_id;
    u32 flags;
} agent_conflict;

typedef struct agent_conflict_registry {
    agent_conflict* entries;
    u32 count;
    u32 capacity;
} agent_conflict_registry;

void agent_conflict_registry_init(agent_conflict_registry* reg,
                                  agent_conflict* storage,
                                  u32 capacity);
agent_conflict* agent_conflict_find(agent_conflict_registry* reg,
                                    u64 conflict_id);
int agent_conflict_register(agent_conflict_registry* reg,
                            u64 conflict_id,
                            u64 party_a_id,
                            u64 party_b_id,
                            u64 subject_id,
                            dom_act_time_t started_act,
                            dom_provenance_id provenance_id);
int agent_conflict_resolve(agent_conflict* conflict,
                           dom_act_time_t resolved_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_CONFLICT_H */
