/*
FILE: include/dominium/agents/agent_planner.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines bounded agent planning and command intents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Planning produces identical steps for identical inputs.
*/
#ifndef DOMINIUM_AGENTS_AGENT_PLANNER_H
#define DOMINIUM_AGENTS_AGENT_PLANNER_H

#include "dominium/agents/agent_evaluator.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AGENT_PLAN_MAX_STEPS 8u

typedef enum agent_command_type {
    AGENT_CMD_NONE = 0,
    AGENT_CMD_MOVE = 1,
    AGENT_CMD_ACQUIRE = 2,
    AGENT_CMD_DEFEND = 3,
    AGENT_CMD_RESEARCH = 4,
    AGENT_CMD_TRADE = 5
} agent_command_type;

#define AGENT_COMMAND_TYPE_COUNT 6u

typedef struct agent_command_intent {
    u32 type;
    u64 target_ref;
    u32 quantity;
    u32 flags;
    u64 provenance_ref;
} agent_command_intent;

typedef struct agent_plan {
    u64 plan_id;
    u64 goal_id;
    agent_command_intent steps[AGENT_PLAN_MAX_STEPS];
    u32 step_count;
    u32 estimated_cost;
    dom_act_time_t estimated_duration_act;
    dom_act_time_t next_due_tick;
    dom_act_time_t created_act;
    dom_act_time_t expiry_act;
} agent_plan;

typedef struct agent_plan_options {
    u32 max_steps;
    u32 max_depth;
    u64 plan_id;
    dom_act_time_t expiry_act;
    dom_act_time_t step_duration_act;
} agent_plan_options;

int agent_planner_build(const agent_goal* goal,
                        const agent_context* ctx,
                        const agent_plan_options* options,
                        dom_act_time_t now_act,
                        agent_plan* out_plan,
                        agent_refusal_code* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_PLANNER_H */
