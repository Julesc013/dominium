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

static dom_process_id agent_process_id_from_key(const char* key)
{
    const unsigned char* bytes = (const unsigned char*)(key ? key : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash ? hash : 1u;
}

static dom_process_id agent_process_id_for_kind(u32 kind)
{
    switch (kind) {
        case AGENT_PROCESS_KIND_MOVE: return agent_process_id_from_key("PROC.MOVE");
        case AGENT_PROCESS_KIND_ACQUIRE: return agent_process_id_from_key("PROC.ACQUIRE");
        case AGENT_PROCESS_KIND_DEFEND: return agent_process_id_from_key("PROC.DEFEND");
        case AGENT_PROCESS_KIND_RESEARCH: return agent_process_id_from_key("PROC.RESEARCH");
        case AGENT_PROCESS_KIND_TRADE: return agent_process_id_from_key("PROC.TRADE");
        case AGENT_PROCESS_KIND_OBSERVE: return agent_process_id_from_key("PROC.OBSERVE");
        case AGENT_PROCESS_KIND_SURVEY: return agent_process_id_from_key("PROC.SURVEY");
        case AGENT_PROCESS_KIND_MAINTAIN: return agent_process_id_from_key("PROC.MAINTAIN");
        case AGENT_PROCESS_KIND_TRANSFER: return agent_process_id_from_key("PROC.TRANSFER");
        default: break;
    }
    return agent_process_id_from_key("PROC.UNKNOWN");
}

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
    if ((ctx->knowledge_mask & goal->preconditions.required_knowledge) !=
        goal->preconditions.required_knowledge) {
        if (goal->flags & AGENT_GOAL_FLAG_ALLOW_UNKNOWN) {
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_NONE;
            }
        } else {
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
            }
            return 0;
        }
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
        if (options->compute_budget > 0u && options->compute_budget < max_steps) {
            max_steps = options->compute_budget;
        }
    }
    if (max_depth > 0u && max_depth < max_steps) {
        return max_depth;
    }
    return max_steps;
}

static u32 agent_plan_step_confidence(const agent_goal* goal,
                                      const agent_context* ctx)
{
    u32 confidence_q16 = AGENT_CONFIDENCE_MAX;
    if (goal && goal->epistemic_confidence_q16 > 0u) {
        confidence_q16 = goal->epistemic_confidence_q16;
    }
    if (ctx && ctx->epistemic_confidence_q16 > 0u &&
        ctx->epistemic_confidence_q16 < confidence_q16) {
        confidence_q16 = ctx->epistemic_confidence_q16;
    }
    return confidence_q16;
}

static int agent_plan_add_step(agent_plan* plan,
                               u32 limit,
                               dom_process_id process_id,
                               u32 process_kind,
                               u64 target_ref,
                               u32 required_caps,
                               u32 required_auth,
                               u32 expected_cost,
                               u32 epistemic_gap_mask,
                               u32 confidence_q16,
                               u32 failure_mode_id)
{
    agent_process_step* step;
    u32 step_index;
    if (!plan || limit == 0u) {
        return -1;
    }
    if (plan->step_count >= limit || plan->step_count >= AGENT_PLAN_MAX_STEPS) {
        return -2;
    }
    step_index = plan->step_count;
    step = &plan->steps[step_index];
    memset(step, 0, sizeof(*step));
    step->process_id = process_id;
    step->process_kind = process_kind;
    step->target_ref = target_ref;
    step->required_capability_mask = required_caps;
    step->required_authority_mask = required_auth;
    step->expected_cost_units = expected_cost;
    step->epistemic_gap_mask = epistemic_gap_mask;
    step->confidence_q16 = confidence_q16;
    step->failure_mode_id = failure_mode_id;
    step->flags = AGENT_PLAN_STEP_NONE;
    if (epistemic_gap_mask != 0u) {
        step->flags |= AGENT_PLAN_STEP_EPISTEMIC_GAP;
    }
    if (failure_mode_id != 0u) {
        step->flags |= AGENT_PLAN_STEP_FAILURE_POINT;
        plan->failure_point_mask |= (1u << step_index);
    }
    plan->required_capability_mask |= required_caps;
    plan->required_authority_mask |= required_auth;
    plan->expected_epistemic_gap_mask |= epistemic_gap_mask;
    if (plan->step_count == 0u) {
        plan->confidence_q16 = confidence_q16;
    } else if (confidence_q16 < plan->confidence_q16) {
        plan->confidence_q16 = confidence_q16;
    }
    plan->estimated_cost += expected_cost;
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
    u32 missing_knowledge = 0u;
    u32 confidence_q16;
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
    out_plan->agent_id = goal->agent_id ? goal->agent_id : (ctx ? ctx->agent_id : 0u);
    out_plan->goal_id = goal->goal_id;
    out_plan->created_act = now_act;
    out_plan->expiry_act = (options && options->expiry_act) ? options->expiry_act : goal->expiry_act;
    out_plan->horizon_act = goal->horizon_act;
    out_plan->confidence_q16 = AGENT_CONFIDENCE_MAX;
    out_plan->required_capability_mask = 0u;
    out_plan->required_authority_mask = 0u;
    out_plan->expected_epistemic_gap_mask = 0u;
    out_plan->failure_point_mask = 0u;

    limit = agent_plan_step_limit(options);
    step_duration = agent_plan_step_duration(options);
    confidence_q16 = agent_plan_step_confidence(goal, ctx);
    if (ctx) {
        missing_knowledge = goal->preconditions.required_knowledge & ~ctx->knowledge_mask;
    }

    switch (goal->type) {
        case AGENT_GOAL_SURVIVE:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_MOVE),
                                    AGENT_PROCESS_KIND_MOVE,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0 ||
                agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_ACQUIRE),
                                    AGENT_PROCESS_KIND_ACQUIRE,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_ACQUIRE:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_ACQUIRE),
                                    AGENT_PROCESS_KIND_ACQUIRE,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_DEFEND:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_DEFEND),
                                    AGENT_PROCESS_KIND_DEFEND,
                                    ctx ? ctx->known_threat_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_MIGRATE:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_MOVE),
                                    AGENT_PROCESS_KIND_MOVE,
                                    ctx ? ctx->known_destination_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_RESEARCH:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_RESEARCH),
                                    AGENT_PROCESS_KIND_RESEARCH,
                                    0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    0u,
                                    confidence_q16,
                                    0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_TRADE:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_TRADE),
                                    AGENT_PROCESS_KIND_TRADE,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_SURVEY:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_SURVEY),
                                    AGENT_PROCESS_KIND_SURVEY,
                                    ctx ? ctx->known_destination_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_MAINTAIN:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_SURVEY),
                                    AGENT_PROCESS_KIND_SURVEY,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0 ||
                agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_MAINTAIN),
                                    AGENT_PROCESS_KIND_MAINTAIN,
                                    ctx ? ctx->known_resource_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
                if (out_refusal) {
                    *out_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
                }
                return -5;
            }
            break;
        case AGENT_GOAL_STABILIZE:
            if (agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_SURVEY),
                                    AGENT_PROCESS_KIND_SURVEY,
                                    ctx ? ctx->known_destination_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0 ||
                agent_plan_add_step(out_plan, limit, agent_process_id_for_kind(AGENT_PROCESS_KIND_TRANSFER),
                                    AGENT_PROCESS_KIND_TRANSFER,
                                    ctx ? ctx->known_destination_ref : 0u,
                                    goal->preconditions.required_capabilities,
                                    goal->preconditions.required_authority,
                                    1u,
                                    missing_knowledge,
                                    confidence_q16,
                                    (missing_knowledge && (goal->flags & AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE))
                                        ? AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE : 0u) != 0) {
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

    out_plan->compute_budget_used = out_plan->step_count;
    out_plan->estimated_duration_act = (dom_act_time_t)(step_duration * out_plan->step_count);
    out_plan->next_due_tick = now_act + out_plan->estimated_duration_act;
    if (options && options->resume_step > 0u && options->resume_step < out_plan->step_count) {
        out_plan->step_cursor = options->resume_step;
    }
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_NONE;
    }
    return 0;
}
