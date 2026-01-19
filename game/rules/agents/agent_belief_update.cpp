/*
FILE: game/agents/agent_belief_update.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic belief updates for agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Belief deltas clamp to fixed bounds and apply in-order.
*/
#include "dominium/agents/agent_belief_update.h"

static u32 agent_clamp_need(i32 value)
{
    if (value < 0) {
        return 0u;
    }
    if ((u32)value > AGENT_NEED_SCALE) {
        return AGENT_NEED_SCALE;
    }
    return (u32)value;
}

void agent_belief_init(agent_belief_state* state,
                       u64 agent_id,
                       u32 knowledge_mask,
                       u32 hunger_level,
                       u32 threat_level,
                       dom_act_time_t now_act)
{
    if (!state) {
        return;
    }
    state->agent_id = agent_id;
    state->knowledge_mask = knowledge_mask;
    state->hunger_level = (hunger_level > AGENT_NEED_SCALE) ? AGENT_NEED_SCALE : hunger_level;
    state->threat_level = (threat_level > AGENT_NEED_SCALE) ? AGENT_NEED_SCALE : threat_level;
    state->last_update_act = now_act;
}

int agent_belief_apply_observation(agent_belief_state* state,
                                   const agent_observation_event* obs,
                                   dom_act_time_t now_act)
{
    i32 next;
    if (!state || !obs) {
        return -1;
    }
    state->knowledge_mask |= obs->knowledge_grant_mask;
    state->knowledge_mask &= ~obs->knowledge_clear_mask;

    next = (i32)state->hunger_level + obs->hunger_delta;
    state->hunger_level = agent_clamp_need(next);

    next = (i32)state->threat_level + obs->threat_delta;
    state->threat_level = agent_clamp_need(next);

    state->last_update_act = now_act;
    return 0;
}

int agent_belief_apply_command_outcome(agent_belief_state* state,
                                       const agent_command_outcome* outcome,
                                       dom_act_time_t now_act)
{
    i32 next;
    if (!state || !outcome) {
        return -1;
    }
    state->knowledge_mask &= ~outcome->knowledge_clear_mask;
    if (!outcome->success && outcome->refusal == AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE &&
        outcome->knowledge_clear_mask == 0u) {
        state->knowledge_mask &= ~AGENT_KNOW_RESOURCE;
    }

    next = (i32)state->hunger_level + outcome->hunger_delta;
    state->hunger_level = agent_clamp_need(next);

    next = (i32)state->threat_level + outcome->threat_delta;
    state->threat_level = agent_clamp_need(next);

    state->last_update_act = now_act;
    return 0;
}
