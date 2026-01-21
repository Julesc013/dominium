/*
Visitability contract tests (DOMAIN4).
*/
#include "dominium/rules/scale/visitability_system.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void test_request_base(dom_visitability_request* req)
{
    dom_visitability_request_init(req);
    req->domain_id = 1u;
    req->existence_state = DOM_DOMAIN_EXISTENCE_REFINABLE;
    req->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    req->travel_allowed = D_TRUE;
    req->domain_allowed = D_TRUE;
    req->law_allowed = D_TRUE;
    req->has_refinement_contract = D_TRUE;
    req->required_tier = DOM_FIDELITY_MICRO;
    req->now_tick = 100u;
    req->budget.required_units = 2u;
    req->budget.available_units = 2u;
}

static int test_reachable_not_refinable(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    req.existence_state = DOM_DOMAIN_EXISTENCE_LATENT;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_REFUSE, "latent should refuse");
    EXPECT(res.refusal_reason == DOM_VISIT_REFUSE_EXISTENCE_INVALID, "latent reason");
    return 0;
}

static int test_refinable_not_reachable(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    req.travel_allowed = D_FALSE;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_REFUSE, "unreachable should refuse");
    EXPECT(res.refusal_reason == DOM_VISIT_REFUSE_UNREACHABLE, "unreachable reason");
    return 0;
}

static int test_refinable_and_reachable(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_ACCEPT, "refinable should accept");
    EXPECT((res.flags & DOM_VISIT_FLAG_REFINEMENT_REQUIRED) != 0u, "refinement required flag");
    return 0;
}

static int test_budget_pressure(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    req.budget.required_units = 10u;
    req.budget.available_units = 1u;
    req.budget.allow_defer = 1u;
    req.budget.defer_ticks = 5u;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_DEFER, "budget defer");
    EXPECT(res.refusal_reason == DOM_VISIT_REFUSE_BUDGET_INSUFFICIENT, "budget reason");
    EXPECT(res.defer_until_tick == 105u, "defer tick");

    test_request_base(&req);
    req.budget.required_units = 10u;
    req.budget.available_units = 1u;
    req.budget.allow_defer = 0u;
    req.budget.allow_degrade = 1u;
    req.budget.degrade_tier = DOM_FIDELITY_MESO;
    req.required_tier = DOM_FIDELITY_MICRO;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_ACCEPT, "budget degrade accept");
    EXPECT((res.flags & DOM_VISIT_FLAG_DEGRADED) != 0u, "degraded flag");
    EXPECT(res.resolved_tier == DOM_FIDELITY_MESO, "degraded tier");
    return 0;
}

static int test_admin_override(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    req.travel_allowed = D_FALSE;
    req.domain_allowed = D_FALSE;
    req.law_allowed = D_FALSE;
    req.has_refinement_contract = D_FALSE;
    req.admin_override = D_TRUE;
    req.existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_ACCEPT, "admin override accept");
    EXPECT((res.flags & DOM_VISIT_FLAG_ADMIN_OVERRIDE) != 0u, "admin override flag");
    EXPECT((res.flags & DOM_VISIT_FLAG_AUDIT_REQUIRED) != 0u, "audit flag");
    return 0;
}

static int test_archived_unreachable(void)
{
    dom_visitability_request req;
    dom_visitability_result res;

    test_request_base(&req);
    req.existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    req.archival_state = DOM_DOMAIN_ARCHIVAL_ARCHIVED;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_REFUSE, "archived refuse");
    EXPECT(res.refusal_reason == DOM_VISIT_REFUSE_ARCHIVAL_BLOCKED, "archived reason");

    test_request_base(&req);
    req.existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    req.archival_state = DOM_DOMAIN_ARCHIVAL_ARCHIVED;
    req.admin_override = D_TRUE;
    req.allow_archival_fork = D_TRUE;

    dom_visitability_evaluate(&req, &res);
    EXPECT(res.outcome == DOM_VISIT_ACCEPT, "archived fork accept");
    EXPECT((res.flags & DOM_VISIT_FLAG_FORK_REQUIRED) != 0u, "fork required");
    return 0;
}

int main(void)
{
    if (test_reachable_not_refinable() != 0) return 1;
    if (test_refinable_not_reachable() != 0) return 1;
    if (test_refinable_and_reachable() != 0) return 1;
    if (test_budget_pressure() != 0) return 1;
    if (test_admin_override() != 0) return 1;
    if (test_archived_unreachable() != 0) return 1;
    return 0;
}
