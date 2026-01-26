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
#include "domino/process.h"

#ifdef __cplusplus
extern "C" {
#endif

#define AGENT_PLAN_MAX_STEPS 8u

typedef enum agent_process_kind {
    AGENT_PROCESS_KIND_MOVE = 1,
    AGENT_PROCESS_KIND_ACQUIRE = 2,
    AGENT_PROCESS_KIND_DEFEND = 3,
    AGENT_PROCESS_KIND_RESEARCH = 4,
    AGENT_PROCESS_KIND_TRADE = 5,
    AGENT_PROCESS_KIND_OBSERVE = 6,
    AGENT_PROCESS_KIND_SURVEY = 7,
    AGENT_PROCESS_KIND_MAINTAIN = 8,
    AGENT_PROCESS_KIND_TRANSFER = 9
} agent_process_kind;

#define AGENT_PROCESS_KIND_BIT(kind) (1u << ((kind) - 1u))

typedef enum agent_process_step_flags {
    AGENT_PLAN_STEP_NONE = 0u,
    AGENT_PLAN_STEP_EPISTEMIC_GAP = (1u << 0u),
    AGENT_PLAN_STEP_FAILURE_POINT = (1u << 1u)
} agent_process_step_flags;

typedef struct agent_process_step {
    dom_process_id process_id;
    u32 process_kind;
    u64 target_ref;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 expected_cost_units;
    u32 epistemic_gap_mask;
    u32 confidence_q16;
    u32 failure_mode_id;
    u32 flags;
} agent_process_step;

typedef struct agent_plan {
    u64 plan_id;
    u64 agent_id;
    u64 goal_id;
    agent_process_step steps[AGENT_PLAN_MAX_STEPS];
    u32 step_count;
    u32 step_cursor;
    u32 estimated_cost;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 expected_epistemic_gap_mask;
    u32 confidence_q16;
    u32 failure_point_mask;
    u32 compute_budget_used;
    dom_act_time_t estimated_duration_act;
    dom_act_time_t next_due_tick;
    dom_act_time_t created_act;
    dom_act_time_t expiry_act;
    dom_act_time_t horizon_act;
} agent_plan;

typedef struct agent_plan_options {
    u32 max_steps;
    u32 max_depth;
    u32 compute_budget;
    u32 resume_step;
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
