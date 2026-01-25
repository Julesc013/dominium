/*
FILE: include/dominium/agents/agent_evaluator.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic agent goal evaluation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Goal selection and priority scoring are deterministic.
*/
#ifndef DOMINIUM_AGENTS_AGENT_EVALUATOR_H
#define DOMINIUM_AGENTS_AGENT_EVALUATOR_H

#include "dominium/agents/agent_goal.h"

#ifdef __cplusplus
extern "C" {
#endif

struct agent_doctrine_registry;
struct agent_role_registry;

typedef struct agent_context {
    u64 agent_id;
    u32 capability_mask;
    u32 authority_mask;
    u32 knowledge_mask;
    u32 hunger_level;
    u32 threat_level;
    u32 risk_tolerance_q16;
    u32 epistemic_confidence_q16;
    u64 known_resource_ref;
    u64 known_threat_ref;
    u64 known_destination_ref;
    u64 role_id;
    u64 explicit_doctrine_ref;
    u64 org_doctrine_ref;
    u64 jurisdiction_doctrine_ref;
    u64 personal_doctrine_ref;
    u32 legitimacy_value;
} agent_context;

typedef struct agent_goal_eval_result {
    const agent_goal* goal;
    u32 computed_priority;
    u32 confidence_q16;
    agent_refusal_code refusal;
    u64 applied_doctrine_ref;
    u64 applied_role_ref;
} agent_goal_eval_result;

int agent_evaluator_choose_goal(const agent_goal_registry* reg,
                                const agent_context* ctx,
                                dom_act_time_t now_act,
                                agent_goal_eval_result* out);
int agent_evaluator_choose_goal_with_doctrine(const agent_goal_registry* goals,
                                              const struct agent_doctrine_registry* doctrines,
                                              const struct agent_role_registry* roles,
                                              const agent_context* ctx,
                                              dom_act_time_t now_act,
                                              agent_goal_eval_result* out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_EVALUATOR_H */
