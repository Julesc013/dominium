/*
FILE: tools/observability/agent_inspector.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Implements read-only inspection of agent state, goals, beliefs, plans, and failures.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and iteration.
*/
#include "agent_inspector.h"

#include <string.h>

static void tool_agent_access_default(tool_access_context* access)
{
    if (!access) {
        return;
    }
    access->mode = TOOL_ACCESS_EPISTEMIC;
    access->knowledge_mask = 0u;
}

int tool_agent_inspector_init(tool_agent_inspector* insp,
                              const tool_observation_store* store,
                              const tool_access_context* access,
                              u64 agent_id)
{
    if (!insp || !store) {
        return TOOL_OBSERVE_INVALID;
    }
    memset(insp, 0, sizeof(*insp));
    insp->store = store;
    insp->agent_id = agent_id;
    if (access) {
        insp->access = *access;
    } else {
        tool_agent_access_default(&insp->access);
    }
    return TOOL_OBSERVE_OK;
}

int tool_agent_inspector_reset(tool_agent_inspector* insp)
{
    if (!insp) {
        return TOOL_OBSERVE_INVALID;
    }
    insp->goal_cursor = 0u;
    insp->belief_cursor = 0u;
    insp->memory_cursor = 0u;
    insp->plan_cursor = 0u;
    insp->failure_cursor = 0u;
    return TOOL_OBSERVE_OK;
}

int tool_agent_inspector_state(const tool_agent_inspector* insp,
                               tool_agent_state* out_state)
{
    u32 i;
    if (!insp || !out_state || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agents || insp->store->agent_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    for (i = 0u; i < insp->store->agent_count; ++i) {
        const tool_agent_state* state = &insp->store->agents[i];
        if (insp->agent_id != 0u && state->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, state->knowledge_mask)) {
            return TOOL_OBSERVE_REFUSED;
        }
        *out_state = *state;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_agent_inspector_next_goal(tool_agent_inspector* insp,
                                   tool_agent_goal_record* out_goal)
{
    if (!insp || !out_goal || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agent_goals || insp->store->agent_goal_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->goal_cursor < insp->store->agent_goal_count) {
        const tool_agent_goal_record* goal = &insp->store->agent_goals[insp->goal_cursor++];
        if (insp->agent_id != 0u && goal->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, goal->required_knowledge)) {
            continue;
        }
        *out_goal = *goal;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_agent_inspector_next_belief(tool_agent_inspector* insp,
                                     tool_agent_belief_record* out_belief)
{
    if (!insp || !out_belief || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agent_beliefs || insp->store->agent_belief_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->belief_cursor < insp->store->agent_belief_count) {
        const tool_agent_belief_record* belief = &insp->store->agent_beliefs[insp->belief_cursor++];
        if (insp->agent_id != 0u && belief->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, belief->required_knowledge)) {
            continue;
        }
        *out_belief = *belief;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_agent_inspector_next_memory(tool_agent_inspector* insp,
                                     tool_agent_memory_record* out_memory)
{
    if (!insp || !out_memory || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agent_memory || insp->store->agent_memory_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->memory_cursor < insp->store->agent_memory_count) {
        const tool_agent_memory_record* mem = &insp->store->agent_memory[insp->memory_cursor++];
        if (insp->agent_id != 0u && mem->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, mem->required_knowledge)) {
            continue;
        }
        *out_memory = *mem;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_agent_inspector_next_plan_step(tool_agent_inspector* insp,
                                        tool_agent_plan_step_record* out_step)
{
    if (!insp || !out_step || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agent_plan_steps || insp->store->agent_plan_step_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->plan_cursor < insp->store->agent_plan_step_count) {
        const tool_agent_plan_step_record* step = &insp->store->agent_plan_steps[insp->plan_cursor++];
        if (insp->agent_id != 0u && step->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, step->required_knowledge)) {
            continue;
        }
        *out_step = *step;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}

int tool_agent_inspector_next_failure(tool_agent_inspector* insp,
                                      tool_agent_failure_record* out_failure)
{
    if (!insp || !out_failure || !insp->store) {
        return TOOL_OBSERVE_INVALID;
    }
    if (!insp->store->agent_failures || insp->store->agent_failure_count == 0u) {
        return TOOL_OBSERVE_NO_DATA;
    }
    while (insp->failure_cursor < insp->store->agent_failure_count) {
        const tool_agent_failure_record* fail = &insp->store->agent_failures[insp->failure_cursor++];
        if (insp->agent_id != 0u && fail->agent_id != insp->agent_id) {
            continue;
        }
        if (!tool_inspect_access_allows(&insp->access, fail->required_knowledge)) {
            continue;
        }
        *out_failure = *fail;
        return TOOL_OBSERVE_OK;
    }
    return TOOL_OBSERVE_NO_DATA;
}
