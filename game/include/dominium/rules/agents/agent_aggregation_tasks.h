/*
FILE: include/dominium/rules/agents/agent_aggregation_tasks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Work IR task helpers for agent aggregation/refinement.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation and refinement are deterministic.
*/
#ifndef DOMINIUM_RULES_AGENTS_AGENT_AGGREGATION_TASKS_H
#define DOMINIUM_RULES_AGENTS_AGENT_AGGREGATION_TASKS_H

#include "dominium/rules/agents/agent_planning_tasks.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_agent_population_status {
    DOM_AGENT_POP_COHORT = 0,
    DOM_AGENT_POP_INDIVIDUAL = 1
} dom_agent_population_status;

typedef struct dom_agent_population_item {
    u64 agent_id;
    u64 cohort_id;
    u32 interest_level;
    u32 status;
} dom_agent_population_item;

typedef struct dom_agent_cohort_item {
    u64 cohort_id;
    u32 member_count;
} dom_agent_cohort_item;

typedef struct dom_agent_cohort_buffer {
    dom_agent_cohort_item* entries;
    u32 count;
    u32 capacity;
} dom_agent_cohort_buffer;

typedef struct dom_agent_aggregation_policy {
    u32 refine_threshold;
    u32 collapse_threshold;
    u32 cohort_limit;
} dom_agent_aggregation_policy;

void dom_agent_cohort_buffer_init(dom_agent_cohort_buffer* buffer,
                                  dom_agent_cohort_item* storage,
                                  u32 capacity);
void dom_agent_cohort_buffer_reset(dom_agent_cohort_buffer* buffer);

u32 dom_agent_aggregate_cohorts_slice(dom_agent_population_item* population,
                                      u32 population_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_agent_cohort_buffer* cohorts,
                                      dom_agent_audit_log* audit);

u32 dom_agent_refine_individuals_slice(dom_agent_population_item* population,
                                       u32 population_count,
                                       u32 start_index,
                                       u32 max_count,
                                       const dom_agent_aggregation_policy* policy,
                                       dom_agent_audit_log* audit);

u32 dom_agent_collapse_individuals_slice(dom_agent_population_item* population,
                                         u32 population_count,
                                         u32 start_index,
                                         u32 max_count,
                                         const dom_agent_aggregation_policy* policy,
                                         dom_agent_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_AGENTS_AGENT_AGGREGATION_TASKS_H */
