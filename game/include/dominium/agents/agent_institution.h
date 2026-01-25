/*
FILE: include/dominium/agents/agent_institution.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines institution records as first-class agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering by institution_id is deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGENT_INSTITUTION_H
#define DOMINIUM_AGENTS_AGENT_INSTITUTION_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum agent_institution_status {
    AGENT_INSTITUTION_ACTIVE = 0,
    AGENT_INSTITUTION_DORMANT = 1,
    AGENT_INSTITUTION_COLLAPSED = 2
} agent_institution_status;

typedef struct agent_institution {
    u64 institution_id;
    u64 agent_id;
    u32 authority_mask;
    u32 legitimacy_q16;
    u32 status;
    dom_act_time_t founded_act;
    dom_act_time_t collapsed_act;
    dom_provenance_id provenance_id;
    u32 flags;
} agent_institution;

typedef struct agent_institution_registry {
    agent_institution* entries;
    u32 count;
    u32 capacity;
} agent_institution_registry;

void agent_institution_registry_init(agent_institution_registry* reg,
                                     agent_institution* storage,
                                     u32 capacity);
agent_institution* agent_institution_find(agent_institution_registry* reg,
                                          u64 institution_id);
int agent_institution_register(agent_institution_registry* reg,
                               u64 institution_id,
                               u64 agent_id,
                               u32 authority_mask,
                               u32 legitimacy_q16,
                               dom_act_time_t founded_act,
                               dom_provenance_id provenance_id);
int agent_institution_set_legitimacy(agent_institution* inst,
                                     u32 legitimacy_q16);
int agent_institution_check_collapse(agent_institution* inst,
                                     u32 collapse_threshold_q16,
                                     dom_act_time_t now_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_INSTITUTION_H */
