/*
FILE: game/agents/agent_evaluator.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic goal evaluation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Goal selection uses stable ordering and fixed-point scoring.
*/
#include "dominium/agents/agent_evaluator.h"
#include "dominium/agents/agent_role.h"
#include "dominium/agents/doctrine.h"

#include <string.h>

static u32 agent_goal_priority_score(const agent_goal* goal,
                                     const agent_context* ctx)
{
    u64 total = 0u;
    if (!goal) {
        return 0u;
    }
    total = (u64)goal->base_priority;
    if (ctx) {
        switch (goal->type) {
            case AGENT_GOAL_SURVIVE:
                total += (u64)ctx->hunger_level;
                break;
            case AGENT_GOAL_DEFEND:
                total += (u64)ctx->threat_level;
                break;
            default:
                break;
        }
    }
    if (total > (u64)AGENT_PRIORITY_SCALE) {
        total = (u64)AGENT_PRIORITY_SCALE;
    }
    return (u32)total;
}

static int agent_goal_is_expired(const agent_goal* goal,
                                 dom_act_time_t now_act)
{
    if (!goal) {
        return 1;
    }
    if (goal->expiry_act == 0u) {
        return 0;
    }
    return (goal->expiry_act <= now_act) ? 1 : 0;
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

static const agent_doctrine* agent_evaluator_select_doctrine(const agent_doctrine_registry* doctrines,
                                                             const agent_role_registry* roles,
                                                             const agent_context* ctx,
                                                             dom_act_time_t now_act,
                                                             agent_refusal_code* out_refusal,
                                                             u64* out_role_ref)
{
    agent_doctrine_binding binding;
    const agent_role* role = 0;
    if (out_refusal) {
        *out_refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
    }
    if (out_role_ref) {
        *out_role_ref = 0u;
    }
    if (!doctrines || !ctx) {
        return 0;
    }
    if (ctx->role_id != 0u) {
        role = agent_role_find((agent_role_registry*)roles, ctx->role_id);
        if (!role) {
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_ROLE_MISMATCH;
            }
            return 0;
        }
        if (!agent_role_requirements_ok(role, ctx->authority_mask, ctx->capability_mask)) {
            if (out_refusal) {
                *out_refusal = AGENT_REFUSAL_ROLE_MISMATCH;
            }
            return 0;
        }
        if (out_role_ref) {
            *out_role_ref = role->role_id;
        }
    }
    memset(&binding, 0, sizeof(binding));
    binding.explicit_doctrine_ref = ctx->explicit_doctrine_ref;
    binding.role_doctrine_ref = role ? role->default_doctrine_ref : 0u;
    binding.org_doctrine_ref = ctx->org_doctrine_ref;
    binding.jurisdiction_doctrine_ref = ctx->jurisdiction_doctrine_ref;
    binding.personal_doctrine_ref = ctx->personal_doctrine_ref;
    binding.authority_mask = ctx->authority_mask;
    binding.legitimacy_value = ctx->legitimacy_value;
    return agent_doctrine_select(doctrines, &binding, now_act, out_refusal);
}

static int agent_evaluator_choose_goal_internal(const agent_goal_registry* reg,
                                                const agent_context* ctx,
                                                dom_act_time_t now_act,
                                                const agent_doctrine* doctrine,
                                                int require_doctrine,
                                                u64 applied_role_ref,
                                                agent_goal_eval_result* out)
{
    u32 i;
    const agent_goal* best = 0;
    const agent_goal* best_feasible = 0;
    u32 best_priority = 0u;
    u32 best_feasible_priority = 0u;
    agent_refusal_code best_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
    int filtered_by_doctrine = 0;
    if (!out) {
        return -1;
    }
    out->goal = 0;
    out->computed_priority = 0u;
    out->refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
    out->applied_doctrine_ref = doctrine ? doctrine->doctrine_id : 0u;
    out->applied_role_ref = applied_role_ref;
    if (!reg || !reg->goals || reg->count == 0u) {
        return -2;
    }
    if (require_doctrine && !doctrine) {
        out->refusal = AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED;
        return -3;
    }
    for (i = 0u; i < reg->count; ++i) {
        const agent_goal* goal = &reg->goals[i];
        u32 priority;
        if (doctrine && !agent_doctrine_allows_goal(doctrine, goal->type)) {
            filtered_by_doctrine = 1;
            continue;
        }
        priority = agent_goal_priority_score(goal, ctx);
        if (doctrine) {
            priority = agent_doctrine_apply_priority(doctrine, goal->type, priority);
        }
        if (!best || priority > best_priority ||
            (priority == best_priority && goal->goal_id < best->goal_id)) {
            best = goal;
            best_priority = priority;
        }
        if (agent_goal_is_expired(goal, now_act)) {
            continue;
        }
        if (agent_goal_preconditions_ok(goal, ctx, 0)) {
            if (!best_feasible || priority > best_feasible_priority ||
                (priority == best_feasible_priority && goal->goal_id < best_feasible->goal_id)) {
                best_feasible = goal;
                best_feasible_priority = priority;
            }
        }
    }
    if (best_feasible) {
        out->goal = best_feasible;
        out->computed_priority = best_feasible_priority;
        out->refusal = AGENT_REFUSAL_NONE;
        return 0;
    }
    if (!best) {
        if (filtered_by_doctrine) {
            out->refusal = AGENT_REFUSAL_GOAL_FORBIDDEN_BY_DOCTRINE;
            return -4;
        }
        return -5;
    }
    if (agent_goal_is_expired(best, now_act)) {
        best_refusal = AGENT_REFUSAL_PLAN_EXPIRED;
    } else {
        (void)agent_goal_preconditions_ok(best, ctx, &best_refusal);
        if (best_refusal == AGENT_REFUSAL_NONE) {
            best_refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
        }
    }
    out->goal = best;
    out->computed_priority = best_priority;
    out->refusal = best_refusal;
    return -6;
}

int agent_evaluator_choose_goal(const agent_goal_registry* reg,
                                const agent_context* ctx,
                                dom_act_time_t now_act,
                                agent_goal_eval_result* out)
{
    return agent_evaluator_choose_goal_internal(reg, ctx, now_act, 0, 0, 0u, out);
}

int agent_evaluator_choose_goal_with_doctrine(const agent_goal_registry* goals,
                                              const agent_doctrine_registry* doctrines,
                                              const agent_role_registry* roles,
                                              const agent_context* ctx,
                                              dom_act_time_t now_act,
                                              agent_goal_eval_result* out)
{
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;
    const agent_doctrine* doctrine;
    u64 role_ref = 0u;
    if (!out) {
        return -1;
    }
    doctrine = agent_evaluator_select_doctrine(doctrines, roles, ctx, now_act, &refusal, &role_ref);
    if (!doctrine) {
        out->goal = 0;
        out->computed_priority = 0u;
        out->refusal = refusal;
        out->applied_doctrine_ref = 0u;
        out->applied_role_ref = role_ref;
        return -2;
    }
    return agent_evaluator_choose_goal_internal(goals, ctx, now_act, doctrine, 1, role_ref, out);
}
