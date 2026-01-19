/*
FILE: include/dominium/agents/agent_collapse.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic collapse logic for aggregate agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Collapse aggregation is order-independent and deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGENT_COLLAPSE_H
#define DOMINIUM_AGENTS_AGENT_COLLAPSE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/agents/agent_aggregate.h"
#include "dominium/agents/aggregate_beliefs.h"
#include "dominium/agents/aggregate_goals.h"
#include "dominium/interest_set.h"

#ifdef __cplusplus
extern "C" {
#endif

int agent_collapse_check_interest(const dom_interest_set* set,
                                  u32 target_kind,
                                  u64 target_id,
                                  dom_act_time_t now_act,
                                  u32 block_threshold,
                                  agent_refusal_code* out_refusal);
int agent_collapse_apply(aggregate_agent* agg,
                         dom_act_time_t now_act,
                         agent_refusal_code* out_refusal);
int agent_collapse_from_individuals(aggregate_agent* agg,
                                    const agent_belief_state* beliefs,
                                    u32 belief_count,
                                    const agent_goal_status* goals,
                                    u32 goal_count,
                                    dom_act_time_t now_act,
                                    agent_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_COLLAPSE_H */
