/*
FILE: include/dominium/agents/agent_aggregate.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines aggregate agents and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Registry ordering is deterministic by aggregate_agent_id.
*/
#ifndef DOMINIUM_AGENTS_AGENT_AGGREGATE_H
#define DOMINIUM_AGENTS_AGENT_AGGREGATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/agents/aggregate_beliefs.h"
#include "dominium/agents/aggregate_goals.h"
#include "dominium/agents/agent_evaluator.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct aggregate_agent {
    u64 aggregate_agent_id;
    u64 cohort_ref;
    u64 doctrine_ref;
    aggregate_belief_summary belief_summary;
    aggregate_goal_summary goal_summary;
    u32 cohort_count;
    u32 refined_count;
    dom_act_time_t next_think_act;
    u64 active_goal_ref;
    u64 active_plan_ref;
    u64 provenance_ref;
} aggregate_agent;

typedef struct agent_aggregate_registry {
    aggregate_agent* agents;
    u32 count;
    u32 capacity;
    u64 next_aggregate_id;
} agent_aggregate_registry;

void agent_aggregate_registry_init(agent_aggregate_registry* reg,
                                   aggregate_agent* storage,
                                   u32 capacity,
                                   u64 start_id);
aggregate_agent* agent_aggregate_find(agent_aggregate_registry* reg,
                                      u64 aggregate_agent_id);
int agent_aggregate_register(agent_aggregate_registry* reg,
                             u64 aggregate_agent_id,
                             u64 cohort_ref,
                             u64 doctrine_ref,
                             u32 cohort_count,
                             u64 provenance_ref);
int agent_aggregate_set_counts(aggregate_agent* agg,
                               u32 cohort_count,
                               u32 refined_count,
                               agent_refusal_code* out_refusal);
int agent_aggregate_refresh_from_individuals(aggregate_agent* agg,
                                             const agent_belief_state* beliefs,
                                             u32 belief_count,
                                             const agent_goal_status* goals,
                                             u32 goal_count);
int agent_aggregate_make_context(const aggregate_agent* agg,
                                 agent_context* out_ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_AGGREGATE_H */
