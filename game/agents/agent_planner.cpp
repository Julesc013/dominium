/*
FILE: game/agents/agent_planner.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements bounded deterministic agent planning.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Planning uses fixed ordering and bounded step counts.
*/
#include "dominium/agents/agent_planner.h"

#include <string.h>

static int agent_goal_expired_at(const agent_goal* goal,
                                 const agent_plan_options* options,
                                 dom_act_time_t now_act)
{
    dom_act_time_t expiry = 0u;
    if (options && options->expiry_act != 0u) {
        expiry = options->expiry_act;
    }
    if (goal && goal->expiry_act != 0u) {
        if (expiry == 0u || goal->expiry_act < expiry) {
            expiry = goal->expiry_act;
        }
    }
    if (expiry != 0u && expiry <= now_act) {
        return 1;
    }
    return 0;
}

static int agent_goal_preconditions_ok(const agent_goal* goal,
                                       const agent_context* ctx,
                                       agent_refusal_code* out_refusal)
{
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!goal || !ctx) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
        }
        return 0;
    }
    if ((ctx->capability_mask & goal->preconditions.required_capabilities) !=
        goal->preconditions.required_capabilities) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_CAPABILITY;
        }
        return 0;
    }
    if ((ctx->authority_mask & goal->preconditions.required_authority) !=
        goal->preconditions.required_authority) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
        }
        return 0;
    }
    if ((ctx->knowledge_mask & goal->preconditions.required_knowledge) !=
        goal->preconditions.required_knowledge) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
        }
        return 0;
    }
    return 1;
}

static u32 agent_plan_step_limit(const agent_plan_options* options)
{
    u32 max_steps = AGENT_PLAN_MAX_STEPS;
    u32 max_depth = 0u;
    if (options) {
        if (options->max_steps > 0u) {
            max_steps = options->max_steps;
        }
        max_depth = options->max_depth;
    }
    if (max_depth > 0u && max_depth < max_steps) {
        return max_depth;
    }
    return max_steps;
}

static int agent_plan_add_step(agent_plan* plan,
                               u32 limit,
                               u32 type,
                               u64 target_ref,
                               u32 quantity)
{
    agent_command_intent* cmd;
    if (!plan || limit == 0u) {
        return -1;
    }
    if (plan->step_count >= limit || plan->step_count >= AGENT_PLAN_MAX_STEPS) {
        return -2;
    }
    cmd = &plan->steps[plan->step_count];
    memset(cmd, 0, sizeof(*cmd));
    cmd->type = type;
    cmd->target_ref = target_ref;
    cmd->quantity = quantity;
    cmd->provenance_ref = plan->plan_id;
    plan->step_count += 1u;
    return 0;
}

static dom_act_time_t agent_plan_step_duration(const agent_plan_options* options)
{
    if (options && options->step_duration_act > 0u) {
        return options->step_duration_act;
    }
    return 1u;
}

int agent_planner_build(const agent_goal* goal,
                        const agent_context* ctx,
                        const agent_plan_options* options,
                        dom_act_time_t now_act,
                        agent_plan* out_plan,
                        agent_refusal_code* out_refusal)
{
    u32 limit;
    dom_act_time_t step_duration;
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    if (!goal || !ctx || !out_plan) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
        }
        return -1;
    }
    if (agent_goal_expired_at(goal, options, now_act)) {
        if (out_refusal) {
            *out_refusal = AGENT_REFUSAL_PLAN_EXPIRED;
        }
        return -2;
    }
    if (!agent_goal_preconditions_ok(goal, ctx, &refusal)) {
        if (out_refusal) {
            *out_refusal = refusal;
        }
        return -3;
    }
    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->plan_id = (options && options->plan_id) ? options->plan_id : goal->goal_id;
    out_plan->goal_id = goal->goal_id;
    out_plan->created_act = now_act;
    out_plan->expiry_act = (options && options->expiry_act) ? options->expiry_act : goal->expiry_act;

    limit = agent_plan_step_limit(options);
    step_duration = agent_plan_step_duration(options);

    switch (goal->type) {
        case AGENT_GOAL_SURVIVE:
            if (!(ctx->knowledge_mask & AGENT_KNOW_RESOURCE) || ctx->known_resource_ref == 0u) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
                }
                return -4;
            }
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_MOVE,
                                    ctx->known_resource_ref, 0u) != 0 ||
                agent_plan_add_step(out_plan, limit, AGENT_CMD_ACQUIRE,
                                    ctx->known_resource_ref, 1u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_ACQUIRE:
            if (!(ctx->knowledge_mask & AGENT_KNOW_RESOURCE) || ctx->known_resource_ref == 0u) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
                }
                return -4;
            }
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_ACQUIRE,
                                    ctx->known_resource_ref, 1u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_DEFEND:
            if (!(ctx->knowledge_mask & AGENT_KNOW_THREAT) || ctx->known_threat_ref == 0u) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
                }
                return -4;
            }
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_DEFEND,
                                    ctx->known_threat_ref, 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_MIGRATE:
            if (!(ctx->knowledge_mask & AGENT_KNOW_SAFE_ROUTE) ||
                ctx->known_destination_ref == 0u) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
                }
                return -4;
            }
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_MOVE,
                                    ctx->known_destination_ref, 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_RESEARCH:
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_RESEARCH,
                                    0u, 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_TRADE:
            if (!(ctx->knowledge_mask & AGENT_KNOW_RESOURCE) || ctx->known_resource_ref == 0u) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
                }
                return -4;
            }
            if (agent_plan_add_step(out_plan, limit, AGENT_CMD_TRADE,
                                    ctx->known_resource_ref, 1u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        default:
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
            }
            return -6;
    }

    out_plan->estimated_cost = out_plan->step_count;
    out_plan->estimated_duration_act = (dom_act_time_t)(step_duration * out_plan->step_count);
    out_plan->next_due_tick = now_act + out_plan->estimated_duration_act;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    return 0;
}
