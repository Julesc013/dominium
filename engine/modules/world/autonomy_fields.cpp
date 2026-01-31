/*
FILE: source/domino/world/autonomy_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/autonomy_fields
RESPONSIBILITY: Implements deterministic AI autonomy, delegation, and planning resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/autonomy_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_AUTONOMY_RESOLVE_COST_BASE 1u

static q16_16 dom_autonomy_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_AUTONOMY_RATIO_ONE_Q16) {
        return DOM_AUTONOMY_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_autonomy_adjust_clamped(q16_16 base, q16_16 delta)
{
    q16_16 sum = d_q16_16_add(base, delta);
    return dom_autonomy_clamp_ratio(sum);
}

static void dom_autonomy_goal_init(dom_autonomy_goal* goal)
{
    if (!goal) {
        return;
    }
    memset(goal, 0, sizeof(*goal));
}

static void dom_autonomy_delegation_init(dom_autonomy_delegation* delegation)
{
    if (!delegation) {
        return;
    }
    memset(delegation, 0, sizeof(*delegation));
}

static void dom_autonomy_budget_init(dom_autonomy_budget* budget)
{
    if (!budget) {
        return;
    }
    memset(budget, 0, sizeof(*budget));
}

static void dom_autonomy_plan_init(dom_autonomy_plan* plan)
{
    if (!plan) {
        return;
    }
    memset(plan, 0, sizeof(*plan));
    plan->status = DOM_AUTONOMY_PLAN_UNSET;
}

static void dom_autonomy_event_init(dom_autonomy_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->process_type = DOM_AUTONOMY_PROCESS_UNSET;
}

static int dom_autonomy_find_goal_index(const dom_autonomy_domain* domain, u32 goal_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->goal_count; ++i) {
        if (domain->goals[i].goal_id == goal_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_delegation_index(const dom_autonomy_domain* domain, u32 delegation_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->delegation_count; ++i) {
        if (domain->delegations[i].delegation_id == delegation_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_budget_index(const dom_autonomy_domain* domain, u32 budget_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->budget_count; ++i) {
        if (domain->budgets[i].budget_id == budget_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_budget_for_delegation(const dom_autonomy_domain* domain, u32 delegation_id)
{
    if (!domain || delegation_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->budget_count; ++i) {
        if (domain->budgets[i].delegation_id == delegation_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_plan_index(const dom_autonomy_domain* domain, u32 plan_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->plan_count; ++i) {
        if (domain->plans[i].plan_id == plan_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_plan_for_goal(const dom_autonomy_domain* domain, u32 goal_id)
{
    if (!domain || goal_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->plan_count; ++i) {
        if (domain->plans[i].goal_id == goal_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_plan_for_delegation(const dom_autonomy_domain* domain, u32 delegation_id)
{
    if (!domain || delegation_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->plan_count; ++i) {
        if (domain->plans[i].delegation_id == delegation_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_autonomy_find_event_index(const dom_autonomy_domain* domain, u32 event_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].event_id == event_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_autonomy_domain_is_active(const dom_autonomy_domain* domain)
{
    if (!domain) {
        return D_FALSE;
    }
    if (domain->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        domain->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool dom_autonomy_region_collapsed(const dom_autonomy_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static const dom_autonomy_macro_capsule* dom_autonomy_find_capsule(const dom_autonomy_domain* domain,
                                                                   u32 region_id)
{
    if (!domain) {
        return (const dom_autonomy_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_autonomy_macro_capsule*)0;
}

static void dom_autonomy_query_meta_refused(dom_domain_query_meta* meta,
                                            u32 reason,
                                            const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_REFUSED;
    meta->resolution = DOM_DOMAIN_RES_REFUSED;
    meta->confidence = DOM_DOMAIN_CONFIDENCE_UNKNOWN;
    meta->refusal_reason = reason;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static void dom_autonomy_query_meta_ok(dom_domain_query_meta* meta,
                                       u32 resolution,
                                       u32 confidence,
                                       u32 cost_units,
                                       const dom_domain_budget* budget)
{
    if (!meta) {
        return;
    }
    memset(meta, 0, sizeof(*meta));
    meta->status = DOM_DOMAIN_QUERY_OK;
    meta->resolution = resolution;
    meta->confidence = confidence;
    meta->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
    meta->cost_units = cost_units;
    if (budget) {
        meta->budget_used = budget->used_units;
        meta->budget_max = budget->max_units;
    }
}

static u32 dom_autonomy_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_AUTONOMY_RESOLVE_COST_BASE : cost_units;
}

static u32 dom_autonomy_event_bin(u32 process_type)
{
    switch (process_type) {
        case DOM_AUTONOMY_PROCESS_PLAN: return 0u;
        case DOM_AUTONOMY_PROCESS_EXECUTE: return 1u;
        case DOM_AUTONOMY_PROCESS_REVISE: return 2u;
        case DOM_AUTONOMY_PROCESS_REVOKE: return 3u;
        case DOM_AUTONOMY_PROCESS_EXPIRE: return 4u;
        case DOM_AUTONOMY_PROCESS_FAIL: return 5u;
        case DOM_AUTONOMY_PROCESS_COMPLETE: return 6u;
        default: return 0u;
    }
}

static void dom_autonomy_update_goal_flags(dom_autonomy_goal* goal, u64 tick)
{
    if (!goal) {
        return;
    }
    if (goal->flags & DOM_AUTONOMY_GOAL_EXPIRED) {
        return;
    }
    if (goal->expiry_tick > 0u && tick >= goal->expiry_tick) {
        goal->flags |= DOM_AUTONOMY_GOAL_EXPIRED;
    }
}

static void dom_autonomy_update_budget_flags(dom_autonomy_budget* budget)
{
    if (!budget) {
        return;
    }
    budget->flags &= ~DOM_AUTONOMY_BUDGET_EXHAUSTED;
    if (budget->time_budget_ticks > 0u && budget->time_used_ticks >= budget->time_budget_ticks) {
        budget->flags |= DOM_AUTONOMY_BUDGET_EXHAUSTED;
    }
    if (budget->energy_budget > 0 && budget->energy_used >= budget->energy_budget) {
        budget->flags |= DOM_AUTONOMY_BUDGET_EXHAUSTED;
    }
    if (budget->risk_budget > 0 && budget->risk_used >= budget->risk_budget) {
        budget->flags |= DOM_AUTONOMY_BUDGET_EXHAUSTED;
    }
    if (budget->planning_budget > 0u && budget->planning_used >= budget->planning_budget) {
        budget->flags |= DOM_AUTONOMY_BUDGET_EXHAUSTED;
    }
}

static void dom_autonomy_update_plan_flags(dom_autonomy_plan* plan)
{
    if (!plan) {
        return;
    }
    plan->flags &= ~(DOM_AUTONOMY_PLAN_FAILED_FLAG |
                     DOM_AUTONOMY_PLAN_COMPLETED_FLAG |
                     DOM_AUTONOMY_PLAN_REVOKED_FLAG);
    if (plan->status == DOM_AUTONOMY_PLAN_FAILED) {
        plan->flags |= DOM_AUTONOMY_PLAN_FAILED_FLAG;
    } else if (plan->status == DOM_AUTONOMY_PLAN_COMPLETED) {
        plan->flags |= DOM_AUTONOMY_PLAN_COMPLETED_FLAG;
    } else if (plan->status == DOM_AUTONOMY_PLAN_REVOKED) {
        plan->flags |= DOM_AUTONOMY_PLAN_REVOKED_FLAG;
    }
}

static q16_16 dom_autonomy_plan_utilization(const dom_autonomy_budget* budget)
{
    if (!budget || budget->planning_budget == 0u) {
        return 0;
    }
    return dom_autonomy_clamp_ratio(
        (q16_16)(((u64)budget->planning_used << Q16_16_FRAC_BITS) / budget->planning_budget));
}

static d_bool dom_autonomy_apply_event(dom_autonomy_domain* domain,
                                       dom_autonomy_event* event,
                                       u64 tick,
                                       u32* out_flags)
{
    int goal_index = -1;
    int delegation_index = -1;
    int budget_index = -1;
    int plan_index = -1;
    dom_autonomy_goal* goal = 0;
    dom_autonomy_delegation* delegation = 0;
    dom_autonomy_budget* budget = 0;
    dom_autonomy_plan* plan = 0;
    if (!domain || !event) {
        return D_FALSE;
    }
    if (event->flags & DOM_AUTONOMY_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (event->event_tick > tick) {
        return D_FALSE;
    }

    if (event->plan_id != 0u) {
        plan_index = dom_autonomy_find_plan_index(domain, event->plan_id);
    } else if (event->goal_id != 0u) {
        plan_index = dom_autonomy_find_plan_for_goal(domain, event->goal_id);
    } else if (event->delegation_id != 0u) {
        plan_index = dom_autonomy_find_plan_for_delegation(domain, event->delegation_id);
    }
    if (plan_index >= 0) {
        plan = &domain->plans[plan_index];
    }

    if (event->budget_id != 0u) {
        budget_index = dom_autonomy_find_budget_index(domain, event->budget_id);
    } else if (event->delegation_id != 0u) {
        budget_index = dom_autonomy_find_budget_for_delegation(domain, event->delegation_id);
    } else if (plan) {
        budget_index = dom_autonomy_find_budget_for_delegation(domain, plan->delegation_id);
    }
    if (budget_index >= 0) {
        budget = &domain->budgets[budget_index];
    }

    if (event->goal_id != 0u) {
        goal_index = dom_autonomy_find_goal_index(domain, event->goal_id);
    } else if (plan) {
        goal_index = dom_autonomy_find_goal_index(domain, plan->goal_id);
    }
    if (goal_index >= 0) {
        goal = &domain->goals[goal_index];
    }

    if (event->delegation_id != 0u) {
        delegation_index = dom_autonomy_find_delegation_index(domain, event->delegation_id);
    } else if (plan) {
        delegation_index = dom_autonomy_find_delegation_index(domain, plan->delegation_id);
    } else if (budget) {
        delegation_index = dom_autonomy_find_delegation_index(domain, budget->delegation_id);
    }
    if (delegation_index >= 0) {
        delegation = &domain->delegations[delegation_index];
    }

    switch (event->process_type) {
        case DOM_AUTONOMY_PROCESS_PLAN:
            if (!plan) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            if (plan->status == DOM_AUTONOMY_PLAN_UNSET ||
                plan->status == DOM_AUTONOMY_PLAN_PROPOSED) {
                plan->status = DOM_AUTONOMY_PLAN_ACTIVE;
            }
            if (budget && event->delta_planning_used > 0u) {
                budget->planning_used += event->delta_planning_used;
                dom_autonomy_update_budget_flags(budget);
                if ((budget->flags & DOM_AUTONOMY_BUDGET_EXHAUSTED) && out_flags) {
                    *out_flags |= DOM_AUTONOMY_RESOLVE_BUDGET_EXHAUSTED;
                }
            }
            plan->last_update_tick = tick;
            break;
        case DOM_AUTONOMY_PROCESS_EXECUTE:
            if (!plan) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            if (budget) {
                if (event->delta_time_used > 0u) {
                    budget->time_used_ticks += event->delta_time_used;
                }
                if (event->delta_energy_used != 0) {
                    budget->energy_used = d_q48_16_add(budget->energy_used, event->delta_energy_used);
                }
                if (event->delta_risk_used != 0) {
                    budget->risk_used = d_q16_16_add(budget->risk_used, event->delta_risk_used);
                }
                dom_autonomy_update_budget_flags(budget);
                if ((budget->flags & DOM_AUTONOMY_BUDGET_EXHAUSTED) && out_flags) {
                    *out_flags |= DOM_AUTONOMY_RESOLVE_BUDGET_EXHAUSTED;
                }
            }
            plan->last_update_tick = tick;
            break;
        case DOM_AUTONOMY_PROCESS_REVISE:
            if (goal && event->delta_priority != 0) {
                goal->priority = dom_autonomy_adjust_clamped(goal->priority, event->delta_priority);
            }
            if (plan && event->delta_priority != 0) {
                plan->success_score = dom_autonomy_adjust_clamped(plan->success_score,
                                                                 event->delta_priority);
            }
            if (plan) {
                plan->last_update_tick = tick;
            }
            break;
        case DOM_AUTONOMY_PROCESS_REVOKE:
            if (!delegation) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            delegation->flags |= DOM_AUTONOMY_DELEGATION_REVOKED;
            if (plan) {
                plan->status = DOM_AUTONOMY_PLAN_REVOKED;
            }
            if (out_flags) {
                *out_flags |= DOM_AUTONOMY_RESOLVE_DELEGATION_REVOKED;
            }
            break;
        case DOM_AUTONOMY_PROCESS_EXPIRE:
            if (!goal) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            goal->flags |= DOM_AUTONOMY_GOAL_EXPIRED;
            if (out_flags) {
                *out_flags |= DOM_AUTONOMY_RESOLVE_GOAL_EXPIRED;
            }
            break;
        case DOM_AUTONOMY_PROCESS_FAIL:
            if (!plan) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            plan->status = DOM_AUTONOMY_PLAN_FAILED;
            if (out_flags) {
                *out_flags |= DOM_AUTONOMY_RESOLVE_PLAN_FAILED;
            }
            break;
        case DOM_AUTONOMY_PROCESS_COMPLETE:
            if (!plan) {
                event->flags |= DOM_AUTONOMY_EVENT_FAILED;
                return D_FALSE;
            }
            plan->status = DOM_AUTONOMY_PLAN_COMPLETED;
            if (out_flags) {
                *out_flags |= DOM_AUTONOMY_RESOLVE_PLAN_COMPLETED;
            }
            break;
        default:
            event->flags |= DOM_AUTONOMY_EVENT_FAILED;
            return D_FALSE;
    }

    if (plan) {
        dom_autonomy_update_plan_flags(plan);
    }
    event->flags |= DOM_AUTONOMY_EVENT_APPLIED;
    return D_TRUE;
}

static q16_16 dom_autonomy_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_autonomy_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_autonomy_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_AUTONOMY_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_AUTONOMY_HIST_BINS) {
        scaled = DOM_AUTONOMY_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_autonomy_surface_desc_init(dom_autonomy_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->goal_count = 0u;
    desc->delegation_count = 0u;
    desc->budget_count = 0u;
    desc->plan_count = 0u;
    desc->event_count = 0u;
    for (u32 i = 0u; i < DOM_AUTONOMY_MAX_GOALS; ++i) {
        desc->goals[i].goal_id = 0u;
    }
    for (u32 i = 0u; i < DOM_AUTONOMY_MAX_DELEGATIONS; ++i) {
        desc->delegations[i].delegation_id = 0u;
    }
    for (u32 i = 0u; i < DOM_AUTONOMY_MAX_BUDGETS; ++i) {
        desc->budgets[i].budget_id = 0u;
    }
    for (u32 i = 0u; i < DOM_AUTONOMY_MAX_PLANS; ++i) {
        desc->plans[i].plan_id = 0u;
    }
    for (u32 i = 0u; i < DOM_AUTONOMY_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
    }
}

void dom_autonomy_domain_init(dom_autonomy_domain* domain,
                              const dom_autonomy_surface_desc* desc)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    domain->surface = *desc;
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;

    domain->goal_count = (desc->goal_count > DOM_AUTONOMY_MAX_GOALS)
                           ? DOM_AUTONOMY_MAX_GOALS
                           : desc->goal_count;
    domain->delegation_count = (desc->delegation_count > DOM_AUTONOMY_MAX_DELEGATIONS)
                                 ? DOM_AUTONOMY_MAX_DELEGATIONS
                                 : desc->delegation_count;
    domain->budget_count = (desc->budget_count > DOM_AUTONOMY_MAX_BUDGETS)
                             ? DOM_AUTONOMY_MAX_BUDGETS
                             : desc->budget_count;
    domain->plan_count = (desc->plan_count > DOM_AUTONOMY_MAX_PLANS)
                           ? DOM_AUTONOMY_MAX_PLANS
                           : desc->plan_count;
    domain->event_count = (desc->event_count > DOM_AUTONOMY_MAX_EVENTS)
                            ? DOM_AUTONOMY_MAX_EVENTS
                            : desc->event_count;

    for (u32 i = 0u; i < domain->goal_count; ++i) {
        dom_autonomy_goal_init(&domain->goals[i]);
        domain->goals[i].goal_id = desc->goals[i].goal_id;
        domain->goals[i].objective_id = desc->goals[i].objective_id;
        domain->goals[i].success_condition_id = desc->goals[i].success_condition_id;
        domain->goals[i].constraint_id = desc->goals[i].constraint_id;
        domain->goals[i].priority = desc->goals[i].priority;
        domain->goals[i].expiry_tick = desc->goals[i].expiry_tick;
        domain->goals[i].delegator_id = desc->goals[i].delegator_id;
        domain->goals[i].provenance_id = desc->goals[i].provenance_id;
        domain->goals[i].region_id = desc->goals[i].region_id;
        domain->goals[i].flags = desc->goals[i].flags;
    }

    for (u32 i = 0u; i < domain->delegation_count; ++i) {
        dom_autonomy_delegation_init(&domain->delegations[i]);
        domain->delegations[i].delegation_id = desc->delegations[i].delegation_id;
        domain->delegations[i].delegator_id = desc->delegations[i].delegator_id;
        domain->delegations[i].delegate_agent_id = desc->delegations[i].delegate_agent_id;
        domain->delegations[i].allowed_process_count = desc->delegations[i].allowed_process_count;
        for (u32 p = 0u; p < DOM_AUTONOMY_MAX_PROCESS_REFS; ++p) {
            domain->delegations[i].allowed_process_ids[p] = desc->delegations[i].allowed_process_ids[p];
        }
        domain->delegations[i].time_budget_ticks = desc->delegations[i].time_budget_ticks;
        domain->delegations[i].energy_budget = desc->delegations[i].energy_budget;
        domain->delegations[i].risk_budget = desc->delegations[i].risk_budget;
        domain->delegations[i].oversight_policy_id = desc->delegations[i].oversight_policy_id;
        domain->delegations[i].revocation_policy_id = desc->delegations[i].revocation_policy_id;
        domain->delegations[i].provenance_id = desc->delegations[i].provenance_id;
        domain->delegations[i].region_id = desc->delegations[i].region_id;
        domain->delegations[i].flags = desc->delegations[i].flags;
    }

    for (u32 i = 0u; i < domain->budget_count; ++i) {
        dom_autonomy_budget_init(&domain->budgets[i]);
        domain->budgets[i].budget_id = desc->budgets[i].budget_id;
        domain->budgets[i].delegation_id = desc->budgets[i].delegation_id;
        domain->budgets[i].time_budget_ticks = desc->budgets[i].time_budget_ticks;
        domain->budgets[i].time_used_ticks = desc->budgets[i].time_used_ticks;
        domain->budgets[i].energy_budget = desc->budgets[i].energy_budget;
        domain->budgets[i].energy_used = desc->budgets[i].energy_used;
        domain->budgets[i].risk_budget = desc->budgets[i].risk_budget;
        domain->budgets[i].risk_used = desc->budgets[i].risk_used;
        domain->budgets[i].planning_budget = desc->budgets[i].planning_budget;
        domain->budgets[i].planning_used = desc->budgets[i].planning_used;
        domain->budgets[i].provenance_id = desc->budgets[i].provenance_id;
        domain->budgets[i].region_id = desc->budgets[i].region_id;
        domain->budgets[i].flags = desc->budgets[i].flags;
    }

    for (u32 i = 0u; i < domain->plan_count; ++i) {
        dom_autonomy_plan_init(&domain->plans[i]);
        domain->plans[i].plan_id = desc->plans[i].plan_id;
        domain->plans[i].goal_id = desc->plans[i].goal_id;
        domain->plans[i].delegation_id = desc->plans[i].delegation_id;
        domain->plans[i].step_count = desc->plans[i].step_count;
        for (u32 s = 0u; s < DOM_AUTONOMY_MAX_PLAN_STEPS; ++s) {
            domain->plans[i].step_process_ids[s] = desc->plans[i].step_process_ids[s];
        }
        domain->plans[i].success_score = desc->plans[i].success_score;
        domain->plans[i].estimated_cost = desc->plans[i].estimated_cost;
        domain->plans[i].created_tick = desc->plans[i].created_tick;
        domain->plans[i].last_update_tick = desc->plans[i].last_update_tick;
        domain->plans[i].status = desc->plans[i].status;
        domain->plans[i].provenance_id = desc->plans[i].provenance_id;
        domain->plans[i].region_id = desc->plans[i].region_id;
        domain->plans[i].flags = desc->plans[i].flags;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_autonomy_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].process_type = desc->events[i].process_type;
        domain->events[i].goal_id = desc->events[i].goal_id;
        domain->events[i].delegation_id = desc->events[i].delegation_id;
        domain->events[i].plan_id = desc->events[i].plan_id;
        domain->events[i].budget_id = desc->events[i].budget_id;
        domain->events[i].delta_priority = desc->events[i].delta_priority;
        domain->events[i].delta_energy_used = desc->events[i].delta_energy_used;
        domain->events[i].delta_risk_used = desc->events[i].delta_risk_used;
        domain->events[i].delta_time_used = desc->events[i].delta_time_used;
        domain->events[i].delta_planning_used = desc->events[i].delta_planning_used;
        domain->events[i].event_tick = desc->events[i].event_tick;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_autonomy_domain_free(dom_autonomy_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->goal_count = 0u;
    domain->delegation_count = 0u;
    domain->budget_count = 0u;
    domain->plan_count = 0u;
    domain->event_count = 0u;
    domain->capsule_count = 0u;
}

void dom_autonomy_domain_set_state(dom_autonomy_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_autonomy_domain_set_policy(dom_autonomy_domain* domain,
                                    const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_autonomy_goal_query(const dom_autonomy_domain* domain,
                            u32 goal_id,
                            dom_domain_budget* budget,
                            dom_autonomy_goal_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_GOAL_UNRESOLVED;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_autonomy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_autonomy_find_goal_index(domain, goal_id);
    if (index < 0) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_autonomy_region_collapsed(domain, domain->goals[index].region_id)) {
        out_sample->goal_id = domain->goals[index].goal_id;
        out_sample->region_id = domain->goals[index].region_id;
        out_sample->flags = DOM_AUTONOMY_GOAL_COLLAPSED;
        dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->goal_id = domain->goals[index].goal_id;
    out_sample->objective_id = domain->goals[index].objective_id;
    out_sample->success_condition_id = domain->goals[index].success_condition_id;
    out_sample->constraint_id = domain->goals[index].constraint_id;
    out_sample->priority = domain->goals[index].priority;
    out_sample->expiry_tick = domain->goals[index].expiry_tick;
    out_sample->delegator_id = domain->goals[index].delegator_id;
    out_sample->provenance_id = domain->goals[index].provenance_id;
    out_sample->region_id = domain->goals[index].region_id;
    out_sample->flags = domain->goals[index].flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_autonomy_delegation_query(const dom_autonomy_domain* domain,
                                  u32 delegation_id,
                                  dom_domain_budget* budget,
                                  dom_autonomy_delegation_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_DELEGATION_UNRESOLVED;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_autonomy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_autonomy_find_delegation_index(domain, delegation_id);
    if (index < 0) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_autonomy_region_collapsed(domain, domain->delegations[index].region_id)) {
        out_sample->delegation_id = domain->delegations[index].delegation_id;
        out_sample->region_id = domain->delegations[index].region_id;
        out_sample->flags = DOM_AUTONOMY_DELEGATION_COLLAPSED;
        dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->delegation_id = domain->delegations[index].delegation_id;
    out_sample->delegator_id = domain->delegations[index].delegator_id;
    out_sample->delegate_agent_id = domain->delegations[index].delegate_agent_id;
    out_sample->allowed_process_count = domain->delegations[index].allowed_process_count;
    out_sample->time_budget_ticks = domain->delegations[index].time_budget_ticks;
    out_sample->energy_budget = domain->delegations[index].energy_budget;
    out_sample->risk_budget = domain->delegations[index].risk_budget;
    out_sample->oversight_policy_id = domain->delegations[index].oversight_policy_id;
    out_sample->revocation_policy_id = domain->delegations[index].revocation_policy_id;
    out_sample->provenance_id = domain->delegations[index].provenance_id;
    out_sample->region_id = domain->delegations[index].region_id;
    out_sample->flags = domain->delegations[index].flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_autonomy_budget_query(const dom_autonomy_domain* domain,
                              u32 budget_id,
                              dom_domain_budget* budget,
                              dom_autonomy_budget_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_BUDGET_UNRESOLVED;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_autonomy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_autonomy_find_budget_index(domain, budget_id);
    if (index < 0) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_autonomy_region_collapsed(domain, domain->budgets[index].region_id)) {
        out_sample->budget_id = domain->budgets[index].budget_id;
        out_sample->region_id = domain->budgets[index].region_id;
        out_sample->flags = DOM_AUTONOMY_BUDGET_COLLAPSED;
        dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->budget_id = domain->budgets[index].budget_id;
    out_sample->delegation_id = domain->budgets[index].delegation_id;
    out_sample->time_budget_ticks = domain->budgets[index].time_budget_ticks;
    out_sample->time_used_ticks = domain->budgets[index].time_used_ticks;
    out_sample->energy_budget = domain->budgets[index].energy_budget;
    out_sample->energy_used = domain->budgets[index].energy_used;
    out_sample->risk_budget = domain->budgets[index].risk_budget;
    out_sample->risk_used = domain->budgets[index].risk_used;
    out_sample->planning_budget = domain->budgets[index].planning_budget;
    out_sample->planning_used = domain->budgets[index].planning_used;
    out_sample->provenance_id = domain->budgets[index].provenance_id;
    out_sample->region_id = domain->budgets[index].region_id;
    out_sample->flags = domain->budgets[index].flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_autonomy_plan_query(const dom_autonomy_domain* domain,
                            u32 plan_id,
                            dom_domain_budget* budget,
                            dom_autonomy_plan_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_PLAN_UNRESOLVED;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_autonomy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_autonomy_find_plan_index(domain, plan_id);
    if (index < 0) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_autonomy_region_collapsed(domain, domain->plans[index].region_id)) {
        out_sample->plan_id = domain->plans[index].plan_id;
        out_sample->region_id = domain->plans[index].region_id;
        out_sample->flags = DOM_AUTONOMY_PLAN_COLLAPSED;
        dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->plan_id = domain->plans[index].plan_id;
    out_sample->goal_id = domain->plans[index].goal_id;
    out_sample->delegation_id = domain->plans[index].delegation_id;
    out_sample->step_count = domain->plans[index].step_count;
    out_sample->success_score = domain->plans[index].success_score;
    out_sample->estimated_cost = domain->plans[index].estimated_cost;
    out_sample->created_tick = domain->plans[index].created_tick;
    out_sample->last_update_tick = domain->plans[index].last_update_tick;
    out_sample->status = domain->plans[index].status;
    out_sample->provenance_id = domain->plans[index].provenance_id;
    out_sample->region_id = domain->plans[index].region_id;
    out_sample->flags = domain->plans[index].flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_autonomy_event_query(const dom_autonomy_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_autonomy_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_EVENT_UNRESOLVED;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_autonomy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_autonomy_find_event_index(domain, event_id);
    if (index < 0) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_autonomy_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_AUTONOMY_EVENT_UNRESOLVED;
        dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->process_type = domain->events[index].process_type;
    out_sample->goal_id = domain->events[index].goal_id;
    out_sample->delegation_id = domain->events[index].delegation_id;
    out_sample->plan_id = domain->events[index].plan_id;
    out_sample->budget_id = domain->events[index].budget_id;
    out_sample->delta_priority = domain->events[index].delta_priority;
    out_sample->delta_energy_used = domain->events[index].delta_energy_used;
    out_sample->delta_risk_used = domain->events[index].delta_risk_used;
    out_sample->delta_time_used = domain->events[index].delta_time_used;
    out_sample->delta_planning_used = domain->events[index].delta_planning_used;
    out_sample->event_tick = domain->events[index].event_tick;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->flags = domain->events[index].flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_autonomy_region_query(const dom_autonomy_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_autonomy_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_goal;
    u32 cost_delegation;
    u32 cost_budget;
    u32 cost_plan;
    u32 cost_event;
    q48_16 priority_total = 0;
    q48_16 success_total = 0;
    q48_16 utilization_total = 0;
    u32 utilization_count = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_AUTONOMY_RESOLVE_PARTIAL;

    if (!dom_autonomy_domain_is_active(domain)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_autonomy_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_autonomy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    cost_goal = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_delegation = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_budget = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_plan = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_event = dom_autonomy_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->goal_count; ++i) {
        u32 goal_region = domain->goals[i].region_id;
        if (region_id != 0u && goal_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, goal_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_goal)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            break;
        }
        priority_total = d_q48_16_add(priority_total,
                                      d_q48_16_from_q16_16(domain->goals[i].priority));
        out_sample->goal_count += 1u;
    }

    for (u32 i = 0u; i < domain->delegation_count; ++i) {
        u32 delegation_region = domain->delegations[i].region_id;
        if (region_id != 0u && delegation_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, delegation_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_delegation)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            break;
        }
        out_sample->delegation_count += 1u;
    }

    for (u32 i = 0u; i < domain->budget_count; ++i) {
        u32 budget_region = domain->budgets[i].region_id;
        if (region_id != 0u && budget_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, budget_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_budget)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            break;
        }
        utilization_total = d_q48_16_add(utilization_total,
                                         d_q48_16_from_q16_16(dom_autonomy_plan_utilization(
                                             &domain->budgets[i])));
        utilization_count += 1u;
        out_sample->budget_count += 1u;
    }

    for (u32 i = 0u; i < domain->plan_count; ++i) {
        u32 plan_region = domain->plans[i].region_id;
        if (region_id != 0u && plan_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, plan_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_plan)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            break;
        }
        success_total = d_q48_16_add(success_total,
                                     d_q48_16_from_q16_16(domain->plans[i].success_score));
        out_sample->plan_count += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        u32 event_region = domain->events[i].region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, event_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            break;
        }
        out_sample->event_count += 1u;
        out_sample->event_type_counts[dom_autonomy_event_bin(domain->events[i].process_type)] += 1u;
    }

    out_sample->region_id = region_id;
    if (out_sample->goal_count > 0u) {
        out_sample->priority_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(priority_total,
                                             d_q48_16_from_int((i64)out_sample->goal_count))));
    }
    if (out_sample->plan_count > 0u) {
        out_sample->success_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(success_total,
                                             d_q48_16_from_int((i64)out_sample->plan_count))));
    }
    if (utilization_count > 0u) {
        out_sample->budget_utilization_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(utilization_total,
                                             d_q48_16_from_int((i64)utilization_count))));
    }
    out_sample->flags = flags;
    dom_autonomy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                               cost_base, budget);
    return 0;
}

int dom_autonomy_resolve(dom_autonomy_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_autonomy_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_goal;
    u32 cost_delegation;
    u32 cost_budget;
    u32 cost_plan;
    u32 cost_event;
    q48_16 priority_total = 0;
    q48_16 success_total = 0;
    q48_16 utilization_total = 0;
    u32 utilization_count = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_autonomy_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_AUTONOMY_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_autonomy_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_autonomy_region_collapsed(domain, region_id)) {
        const dom_autonomy_macro_capsule* capsule = dom_autonomy_find_capsule(domain, region_id);
        if (capsule) {
            out_result->goal_count = capsule->goal_count;
            out_result->delegation_count = capsule->delegation_count;
            out_result->budget_count = capsule->budget_count;
            out_result->plan_count = capsule->plan_count;
            out_result->priority_avg = capsule->priority_avg;
            out_result->success_avg = capsule->success_avg;
            out_result->budget_utilization_avg = capsule->budget_utilization_avg;
            for (u32 i = 0u; i < DOM_AUTONOMY_EVENT_BINS; ++i) {
                out_result->event_type_counts[i] = capsule->event_type_counts[i];
            }
        }
        out_result->ok = 1u;
        out_result->flags = DOM_AUTONOMY_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_goal = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_delegation = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_budget = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_plan = dom_autonomy_budget_cost(domain->policy.cost_medium);
    cost_event = dom_autonomy_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->goal_count; ++i) {
        u32 goal_region = domain->goals[i].region_id;
        if (region_id != 0u && goal_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, goal_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_goal)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_AUTONOMY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
            }
            break;
        }
        dom_autonomy_update_goal_flags(&domain->goals[i], tick);
        if (domain->goals[i].flags & DOM_AUTONOMY_GOAL_EXPIRED) {
            flags |= DOM_AUTONOMY_RESOLVE_GOAL_EXPIRED;
        }
        priority_total = d_q48_16_add(priority_total,
                                      d_q48_16_from_q16_16(domain->goals[i].priority));
        out_result->goal_count += 1u;
    }

    for (u32 i = 0u; i < domain->delegation_count; ++i) {
        u32 delegation_region = domain->delegations[i].region_id;
        if (region_id != 0u && delegation_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, delegation_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_delegation)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_AUTONOMY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
            }
            break;
        }
        if (domain->delegations[i].flags & DOM_AUTONOMY_DELEGATION_REVOKED) {
            flags |= DOM_AUTONOMY_RESOLVE_DELEGATION_REVOKED;
        }
        out_result->delegation_count += 1u;
    }

    for (u32 i = 0u; i < domain->budget_count; ++i) {
        u32 budget_region = domain->budgets[i].region_id;
        if (region_id != 0u && budget_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, budget_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_budget)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_AUTONOMY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
            }
            break;
        }
        dom_autonomy_update_budget_flags(&domain->budgets[i]);
        if (domain->budgets[i].flags & DOM_AUTONOMY_BUDGET_EXHAUSTED) {
            flags |= DOM_AUTONOMY_RESOLVE_BUDGET_EXHAUSTED;
        }
        utilization_total = d_q48_16_add(utilization_total,
                                         d_q48_16_from_q16_16(dom_autonomy_plan_utilization(
                                             &domain->budgets[i])));
        utilization_count += 1u;
        out_result->budget_count += 1u;
    }

    for (u32 i = 0u; i < domain->plan_count; ++i) {
        u32 plan_region = domain->plans[i].region_id;
        if (region_id != 0u && plan_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, plan_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_plan)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_AUTONOMY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
            }
            break;
        }
        dom_autonomy_update_plan_flags(&domain->plans[i]);
        if (domain->plans[i].status == DOM_AUTONOMY_PLAN_FAILED) {
            flags |= DOM_AUTONOMY_RESOLVE_PLAN_FAILED;
        } else if (domain->plans[i].status == DOM_AUTONOMY_PLAN_COMPLETED) {
            flags |= DOM_AUTONOMY_RESOLVE_PLAN_COMPLETED;
        } else if (domain->plans[i].status == DOM_AUTONOMY_PLAN_REVOKED) {
            flags |= DOM_AUTONOMY_RESOLVE_DELEGATION_REVOKED;
        }
        success_total = d_q48_16_add(success_total,
                                     d_q48_16_from_q16_16(domain->plans[i].success_score));
        out_result->plan_count += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_autonomy_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_autonomy_region_collapsed(domain, event_region)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_AUTONOMY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_AUTONOMY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_AUTONOMY_REFUSE_BUDGET;
            }
            break;
        }
        out_result->event_count += 1u;
        if (dom_autonomy_apply_event(domain, event, tick, &flags)) {
            out_result->event_applied_count += 1u;
            out_result->event_type_counts[dom_autonomy_event_bin(event->process_type)] += 1u;
        }
    }

    out_result->ok = 1u;
    if (out_result->event_applied_count > 0u) {
        flags |= DOM_AUTONOMY_RESOLVE_EVENTS_APPLIED;
    }
    out_result->flags = flags;

    if (out_result->goal_count > 0u) {
        out_result->priority_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(priority_total,
                                             d_q48_16_from_int((i64)out_result->goal_count))));
    }
    if (out_result->plan_count > 0u) {
        out_result->success_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(success_total,
                                             d_q48_16_from_int((i64)out_result->plan_count))));
    }
    if (utilization_count > 0u) {
        out_result->budget_utilization_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(utilization_total,
                                             d_q48_16_from_int((i64)utilization_count))));
    }
    return 0;
}

int dom_autonomy_domain_collapse_region(dom_autonomy_domain* domain, u32 region_id)
{
    dom_autonomy_macro_capsule capsule;
    u32 priority_bins[DOM_AUTONOMY_HIST_BINS];
    u32 success_bins[DOM_AUTONOMY_HIST_BINS];
    q48_16 priority_total = 0;
    q48_16 success_total = 0;
    q48_16 utilization_total = 0;
    u32 utilization_count = 0u;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_autonomy_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_AUTONOMY_MAX_CAPSULES) {
        return -2;
    }
    memset(priority_bins, 0, sizeof(priority_bins));
    memset(success_bins, 0, sizeof(success_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->goal_count; ++i) {
        if (domain->goals[i].region_id != region_id) {
            continue;
        }
        capsule.goal_count += 1u;
        priority_total = d_q48_16_add(priority_total,
                                      d_q48_16_from_q16_16(domain->goals[i].priority));
        priority_bins[dom_autonomy_hist_bin(domain->goals[i].priority)] += 1u;
    }
    for (u32 i = 0u; i < domain->delegation_count; ++i) {
        if (domain->delegations[i].region_id != region_id) {
            continue;
        }
        capsule.delegation_count += 1u;
    }
    for (u32 i = 0u; i < domain->budget_count; ++i) {
        if (domain->budgets[i].region_id != region_id) {
            continue;
        }
        capsule.budget_count += 1u;
        utilization_total = d_q48_16_add(utilization_total,
                                         d_q48_16_from_q16_16(dom_autonomy_plan_utilization(
                                             &domain->budgets[i])));
        utilization_count += 1u;
    }
    for (u32 i = 0u; i < domain->plan_count; ++i) {
        if (domain->plans[i].region_id != region_id) {
            continue;
        }
        capsule.plan_count += 1u;
        success_total = d_q48_16_add(success_total,
                                     d_q48_16_from_q16_16(domain->plans[i].success_score));
        success_bins[dom_autonomy_hist_bin(domain->plans[i].success_score)] += 1u;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].region_id != region_id) {
            continue;
        }
        capsule.event_type_counts[dom_autonomy_event_bin(domain->events[i].process_type)] += 1u;
    }

    if (capsule.goal_count > 0u) {
        capsule.priority_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(priority_total,
                                             d_q48_16_from_int((i64)capsule.goal_count))));
    }
    if (capsule.plan_count > 0u) {
        capsule.success_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(success_total,
                                             d_q48_16_from_int((i64)capsule.plan_count))));
    }
    if (utilization_count > 0u) {
        capsule.budget_utilization_avg = dom_autonomy_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(utilization_total,
                                             d_q48_16_from_int((i64)utilization_count))));
    }
    for (u32 b = 0u; b < DOM_AUTONOMY_HIST_BINS; ++b) {
        capsule.priority_hist[b] = dom_autonomy_hist_bin_ratio(priority_bins[b], capsule.goal_count);
        capsule.success_hist[b] = dom_autonomy_hist_bin_ratio(success_bins[b], capsule.plan_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_autonomy_domain_expand_region(dom_autonomy_domain* domain, u32 region_id)
{
    if (!domain || region_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_autonomy_domain_capsule_count(const dom_autonomy_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_autonomy_macro_capsule* dom_autonomy_domain_capsule_at(const dom_autonomy_domain* domain,
                                                                 u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_autonomy_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
