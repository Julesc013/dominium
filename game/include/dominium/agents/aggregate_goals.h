/*
FILE: include/dominium/agents/aggregate_goals.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines aggregate goal summaries for cohort agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is order-independent and deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGGREGATE_GOALS_H
#define DOMINIUM_AGENTS_AGGREGATE_GOALS_H

#include "domino/core/types.h"
#include "dominium/agents/agent_evaluator.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_goal_status_entry {
    u32 goal_type;
    u32 is_satisfied;
} agent_goal_status_entry;

typedef struct aggregate_goal_summary {
    u32 count;
    u32 goal_counts[AGENT_GOAL_TYPE_COUNT];
    u32 satisfied_counts[AGENT_GOAL_TYPE_COUNT];
} aggregate_goal_summary;

void aggregate_goals_init(aggregate_goal_summary* summary);
int aggregate_goals_from_status(const agent_goal_status_entry* statuses,
                                u32 count,
                                aggregate_goal_summary* out_summary);
int aggregate_goals_from_results(const agent_goal_eval_result* results,
                                 u32 count,
                                 aggregate_goal_summary* out_summary);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGGREGATE_GOALS_H */
