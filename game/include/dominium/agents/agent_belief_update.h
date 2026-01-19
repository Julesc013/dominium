/*
FILE: include/dominium/agents/agent_belief_update.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Defines deterministic agent belief updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Belief updates are event-driven and ordered by ACT time.
*/
#ifndef DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H
#define DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H

#include "dominium/agents/agent_goal.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct agent_belief_state {
    u64 agent_id;
    u32 knowledge_mask;
    u32 hunger_level;
    u32 threat_level;
    dom_act_time_t last_update_act;
} agent_belief_state;

typedef struct agent_observation_event {
    u32 knowledge_grant_mask;
    u32 knowledge_clear_mask;
    i32 hunger_delta;
    i32 threat_delta;
} agent_observation_event;

typedef struct agent_command_outcome {
    u32 command_type;
    int success;
    agent_refusal_code refusal;
    u32 knowledge_clear_mask;
    i32 hunger_delta;
    i32 threat_delta;
} agent_command_outcome;

void agent_belief_init(agent_belief_state* state,
                       u64 agent_id,
                       u32 knowledge_mask,
                       u32 hunger_level,
                       u32 threat_level,
                       dom_act_time_t now_act);
int agent_belief_apply_observation(agent_belief_state* state,
                                   const agent_observation_event* obs,
                                   dom_act_time_t now_act);
int agent_belief_apply_command_outcome(agent_belief_state* state,
                                       const agent_command_outcome* outcome,
                                       dom_act_time_t now_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_AGENTS_AGENT_BELIEF_UPDATE_H */
