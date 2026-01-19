/*
FILE: include/dominium/agents/aggregate_beliefs.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines aggregate belief summaries for cohort agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is order-independent and deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGGREGATE_BELIEFS_H
#define DOMINIUM_AGENTS_AGGREGATE_BELIEFS_H

#include "domino/core/types.h"
#include "dominium/agents/agent_belief_update.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct aggregate_belief_summary {
    u32 count;
    u32 knowledge_mask;
    u32 knowledge_any_mask;
    u32 hunger_min;
    u32 hunger_max;
    u32 hunger_avg;
    u32 threat_min;
    u32 threat_max;
    u32 threat_avg;
} aggregate_belief_summary;

int aggregate_beliefs_from_states(const agent_belief_state* states,
                                  u32 count,
                                  aggregate_belief_summary* out_summary);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGGREGATE_BELIEFS_H */
