/*
FILE: game/rules/scale/visitability_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Deterministic visitability evaluation and enforcement helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: No wall-clock or RNG use; stable ordering and saturation.
*/
#include "dominium/rules/scale/visitability_system.h"

#include <string.h>

static d_bool dom_visitability_state_valid(u32 existence_state)
{
    return (existence_state == DOM_DOMAIN_EXISTENCE_REFINABLE ||
            existence_state == DOM_DOMAIN_EXISTENCE_REALIZED) ? D_TRUE : D_FALSE;
}

static d_bool dom_visitability_state_exists(u32 existence_state)
{
    return (existence_state != DOM_DOMAIN_EXISTENCE_NONEXISTENT &&
            existence_state != DOM_DOMAIN_EXISTENCE_DECLARED) ? D_TRUE : D_FALSE;
}

static d_bool dom_visitability_archival_blocked(u32 archival_state)
{
    return (archival_state == DOM_DOMAIN_ARCHIVAL_FROZEN ||
            archival_state == DOM_DOMAIN_ARCHIVAL_ARCHIVED) ? D_TRUE : D_FALSE;
}

static dom_act_time_t dom_visitability_defer_tick(dom_act_time_t now,
                                                  dom_act_time_t defer_ticks)
{
    if (defer_ticks == 0) {
        defer_ticks = 1u;
    }
    if (now > (DOM_TIME_ACT_MAX - defer_ticks)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + defer_ticks;
}

void dom_visitability_request_init(dom_visitability_request* request)
{
    if (!request) {
        return;
    }
    memset(request, 0, sizeof(*request));
    request->existence_state = DOM_DOMAIN_EXISTENCE_NONEXISTENT;
    request->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    request->required_tier = DOM_FIDELITY_MACRO;
    request->budget.degrade_tier = DOM_FIDELITY_MACRO;
}

void dom_visitability_result_init(dom_visitability_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->outcome = DOM_VISIT_REFUSE;
    result->refusal_reason = DOM_VISIT_REFUSE_INTERNAL;
    result->flags = DOM_VISIT_FLAG_NONE;
    result->required_tier = DOM_FIDELITY_LATENT;
    result->resolved_tier = DOM_FIDELITY_LATENT;
    result->defer_until_tick = 0;
}

int dom_visitability_evaluate(const dom_visitability_request* request,
                              dom_visitability_result* out_result)
{
    dom_visitability_result result;
    d_bool admin_override;
    d_bool budget_ok;

    dom_visitability_result_init(&result);
    if (!request || !out_result) {
        return -1;
    }

    result.required_tier = request->required_tier;
    result.resolved_tier = request->required_tier;
    admin_override = request->admin_override ? D_TRUE : D_FALSE;

    if (dom_visitability_state_exists(request->existence_state) == D_FALSE) {
        result.refusal_reason = DOM_VISIT_REFUSE_EXISTENCE_INVALID;
        *out_result = result;
        return 0;
    }

    if (dom_visitability_archival_blocked(request->archival_state) == D_TRUE) {
        if (admin_override == D_TRUE && request->allow_archival_fork == D_TRUE) {
            result.flags |= DOM_VISIT_FLAG_FORK_REQUIRED;
        } else {
            result.refusal_reason = DOM_VISIT_REFUSE_ARCHIVAL_BLOCKED;
            *out_result = result;
            return 0;
        }
    }

    if (admin_override == D_FALSE) {
        if (request->travel_allowed == D_FALSE) {
            result.refusal_reason = DOM_VISIT_REFUSE_UNREACHABLE;
            *out_result = result;
            return 0;
        }
        if (request->domain_allowed == D_FALSE) {
            result.refusal_reason = DOM_VISIT_REFUSE_DOMAIN_FORBIDDEN;
            *out_result = result;
            return 0;
        }
        if (request->law_allowed == D_FALSE) {
            result.refusal_reason = DOM_VISIT_REFUSE_LAW_FORBIDDEN;
            *out_result = result;
            return 0;
        }
        if (dom_visitability_state_valid(request->existence_state) == D_FALSE) {
            result.refusal_reason = DOM_VISIT_REFUSE_EXISTENCE_INVALID;
            *out_result = result;
            return 0;
        }
        if (request->has_refinement_contract == D_FALSE) {
            result.refusal_reason = DOM_VISIT_REFUSE_NO_CONTRACT;
            *out_result = result;
            return 0;
        }
    } else {
        result.flags |= DOM_VISIT_FLAG_ADMIN_OVERRIDE | DOM_VISIT_FLAG_AUDIT_REQUIRED;
    }

    budget_ok = D_TRUE;
    if (request->budget.required_units > 0u &&
        request->budget.available_units < request->budget.required_units) {
        budget_ok = D_FALSE;
    }

    if (budget_ok == D_FALSE && admin_override == D_FALSE) {
        if (request->budget.allow_defer) {
            result.outcome = DOM_VISIT_DEFER;
            result.refusal_reason = DOM_VISIT_REFUSE_BUDGET_INSUFFICIENT;
            result.defer_until_tick = dom_visitability_defer_tick(request->now_tick,
                                                                  request->budget.defer_ticks);
            *out_result = result;
            return 0;
        }
        if (request->budget.allow_degrade &&
            request->budget.degrade_tier < request->required_tier) {
            result.flags |= DOM_VISIT_FLAG_DEGRADED;
            result.resolved_tier = request->budget.degrade_tier;
        } else {
            result.refusal_reason = DOM_VISIT_REFUSE_BUDGET_INSUFFICIENT;
            *out_result = result;
            return 0;
        }
    }

    result.outcome = DOM_VISIT_ACCEPT;
    result.refusal_reason = DOM_VISIT_REFUSE_NONE;
    if (request->existence_state == DOM_DOMAIN_EXISTENCE_REFINABLE) {
        result.flags |= DOM_VISIT_FLAG_REFINEMENT_REQUIRED;
    }
    *out_result = result;
    return 0;
}
