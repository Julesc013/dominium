/*
FILE: source/domino/world/institution_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/institution_fields
RESPONSIBILITY: Implements deterministic institution, law, and governance resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/institution_fields.h"

#include <string.h>

#define DOM_INSTITUTION_RESOLVE_COST_BASE 1u

static q16_16 dom_institution_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_INSTITUTION_RATIO_ONE_Q16) {
        return DOM_INSTITUTION_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_institution_ratio_from_counts(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_institution_action_index(u32 action)
{
    switch (action) {
        case DOM_INSTITUTION_ENFORCE_PERMIT:
            return 0u;
        case DOM_INSTITUTION_ENFORCE_DENY:
            return 1u;
        case DOM_INSTITUTION_ENFORCE_PENALIZE:
            return 2u;
        case DOM_INSTITUTION_ENFORCE_LICENSE:
            return 3u;
        default:
            return 0u;
    }
}

static void dom_institution_entity_init(dom_institution_entity* entity)
{
    if (!entity) {
        return;
    }
    memset(entity, 0, sizeof(*entity));
}

static void dom_institution_scope_init(dom_institution_scope* scope)
{
    if (!scope) {
        return;
    }
    memset(scope, 0, sizeof(*scope));
}

static void dom_institution_capability_init(dom_institution_capability* capability)
{
    if (!capability) {
        return;
    }
    memset(capability, 0, sizeof(*capability));
}

static void dom_institution_rule_init(dom_institution_rule* rule)
{
    if (!rule) {
        return;
    }
    memset(rule, 0, sizeof(*rule));
    rule->action = DOM_INSTITUTION_RULE_UNSET;
}

static void dom_institution_enforcement_init(dom_institution_enforcement* enforcement)
{
    if (!enforcement) {
        return;
    }
    memset(enforcement, 0, sizeof(*enforcement));
    enforcement->action = DOM_INSTITUTION_ENFORCE_UNSET;
}

static int dom_institution_find_entity_index(const dom_institution_domain* domain,
                                             u32 institution_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->entity_count; ++i) {
        if (domain->entities[i].institution_id == institution_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_institution_find_scope_index(const dom_institution_domain* domain, u32 scope_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->scope_count; ++i) {
        if (domain->scopes[i].scope_id == scope_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_institution_find_capability_index(const dom_institution_domain* domain,
                                                 u32 capability_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capability_count; ++i) {
        if (domain->capabilities[i].capability_id == capability_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_institution_find_rule_index(const dom_institution_domain* domain, u32 rule_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->rule_count; ++i) {
        if (domain->rules[i].rule_id == rule_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_institution_find_enforcement_index(const dom_institution_domain* domain,
                                                  u32 enforcement_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->enforcement_count; ++i) {
        if (domain->enforcement[i].enforcement_id == enforcement_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_institution_domain_is_active(const dom_institution_domain* domain)
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

static d_bool dom_institution_region_collapsed(const dom_institution_domain* domain, u32 region_id)
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

static const dom_institution_macro_capsule* dom_institution_find_capsule(
    const dom_institution_domain* domain,
    u32 region_id)
{
    if (!domain) {
        return (const dom_institution_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_institution_macro_capsule*)0;
}

static void dom_institution_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_institution_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_institution_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_INSTITUTION_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_institution_apply_enforcement(dom_institution_enforcement* enforcement,
                                                u64 tick,
                                                u32* out_action_counts)
{
    if (!enforcement) {
        return D_FALSE;
    }
    if (enforcement->flags & DOM_INSTITUTION_ENFORCEMENT_APPLIED) {
        return D_FALSE;
    }
    if (enforcement->event_tick > tick) {
        return D_FALSE;
    }
    enforcement->flags |= DOM_INSTITUTION_ENFORCEMENT_APPLIED;
    if (out_action_counts) {
        u32 index = dom_institution_action_index(enforcement->action);
        if (index < DOM_INSTITUTION_ACTION_BINS) {
            out_action_counts[index] += 1u;
        }
    }
    return D_TRUE;
}

static u32 dom_institution_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_institution_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_INSTITUTION_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_INSTITUTION_HIST_BINS) {
        scaled = DOM_INSTITUTION_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_institution_surface_desc_init(dom_institution_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->entity_count = 0u;
    desc->scope_count = 0u;
    desc->capability_count = 0u;
    desc->rule_count = 0u;
    desc->enforcement_count = 0u;
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_ENTITIES; ++i) {
        desc->entities[i].institution_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_SCOPES; ++i) {
        desc->scopes[i].scope_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_CAPABILITIES; ++i) {
        desc->capabilities[i].capability_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_RULES; ++i) {
        desc->rules[i].rule_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_ENFORCEMENTS; ++i) {
        desc->enforcement[i].enforcement_id = 0u;
    }
}

void dom_institution_domain_init(dom_institution_domain* domain,
                                 const dom_institution_surface_desc* desc)
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

    domain->entity_count = (desc->entity_count > DOM_INSTITUTION_MAX_ENTITIES)
                             ? DOM_INSTITUTION_MAX_ENTITIES
                             : desc->entity_count;
    domain->scope_count = (desc->scope_count > DOM_INSTITUTION_MAX_SCOPES)
                            ? DOM_INSTITUTION_MAX_SCOPES
                            : desc->scope_count;
    domain->capability_count = (desc->capability_count > DOM_INSTITUTION_MAX_CAPABILITIES)
                                 ? DOM_INSTITUTION_MAX_CAPABILITIES
                                 : desc->capability_count;
    domain->rule_count = (desc->rule_count > DOM_INSTITUTION_MAX_RULES)
                           ? DOM_INSTITUTION_MAX_RULES
                           : desc->rule_count;
    domain->enforcement_count = (desc->enforcement_count > DOM_INSTITUTION_MAX_ENFORCEMENTS)
                                  ? DOM_INSTITUTION_MAX_ENFORCEMENTS
                                  : desc->enforcement_count;

    for (u32 i = 0u; i < domain->entity_count; ++i) {
        dom_institution_entity_init(&domain->entities[i]);
        domain->entities[i].institution_id = desc->entities[i].institution_id;
        domain->entities[i].scope_id = desc->entities[i].scope_id;
        domain->entities[i].authority_count = desc->entities[i].authority_count;
        for (u32 a = 0u; a < DOM_INSTITUTION_MAX_AUTHORITY_TYPES; ++a) {
            domain->entities[i].authority_types[a] = desc->entities[i].authority_types[a];
        }
        domain->entities[i].enforcement_capacity = desc->entities[i].enforcement_capacity;
        domain->entities[i].resource_budget = desc->entities[i].resource_budget;
        domain->entities[i].legitimacy_level = desc->entities[i].legitimacy_level;
        domain->entities[i].legitimacy_ref_id = desc->entities[i].legitimacy_ref_id;
        domain->entities[i].knowledge_base_id = desc->entities[i].knowledge_base_id;
        domain->entities[i].provenance_id = desc->entities[i].provenance_id;
        domain->entities[i].region_id = desc->entities[i].region_id;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        dom_institution_scope_init(&domain->scopes[i]);
        domain->scopes[i].scope_id = desc->scopes[i].scope_id;
        domain->scopes[i].spatial_domain_id = desc->scopes[i].spatial_domain_id;
        domain->scopes[i].subject_domain_count = desc->scopes[i].subject_domain_count;
        for (u32 s = 0u; s < DOM_INSTITUTION_MAX_SUBJECT_DOMAINS; ++s) {
            domain->scopes[i].subject_domain_ids[s] = desc->scopes[i].subject_domain_ids[s];
        }
        domain->scopes[i].overlap_policy_id = desc->scopes[i].overlap_policy_id;
        domain->scopes[i].provenance_id = desc->scopes[i].provenance_id;
        domain->scopes[i].region_id = desc->scopes[i].region_id;
    }

    for (u32 i = 0u; i < domain->capability_count; ++i) {
        dom_institution_capability_init(&domain->capabilities[i]);
        domain->capabilities[i].capability_id = desc->capabilities[i].capability_id;
        domain->capabilities[i].institution_id = desc->capabilities[i].institution_id;
        domain->capabilities[i].scope_id = desc->capabilities[i].scope_id;
        domain->capabilities[i].authority_type_id = desc->capabilities[i].authority_type_id;
        domain->capabilities[i].process_family_id = desc->capabilities[i].process_family_id;
        domain->capabilities[i].capacity_limit = desc->capabilities[i].capacity_limit;
        domain->capabilities[i].license_required_id = desc->capabilities[i].license_required_id;
        domain->capabilities[i].provenance_id = desc->capabilities[i].provenance_id;
        domain->capabilities[i].region_id = desc->capabilities[i].region_id;
        domain->capabilities[i].flags = desc->capabilities[i].flags;
    }

    for (u32 i = 0u; i < domain->rule_count; ++i) {
        dom_institution_rule_init(&domain->rules[i]);
        domain->rules[i].rule_id = desc->rules[i].rule_id;
        domain->rules[i].institution_id = desc->rules[i].institution_id;
        domain->rules[i].scope_id = desc->rules[i].scope_id;
        domain->rules[i].process_family_id = desc->rules[i].process_family_id;
        domain->rules[i].subject_domain_id = desc->rules[i].subject_domain_id;
        domain->rules[i].authority_type_id = desc->rules[i].authority_type_id;
        domain->rules[i].action = desc->rules[i].action;
        domain->rules[i].license_required_id = desc->rules[i].license_required_id;
        domain->rules[i].provenance_id = desc->rules[i].provenance_id;
        domain->rules[i].region_id = desc->rules[i].region_id;
        domain->rules[i].flags = desc->rules[i].flags;
    }

    for (u32 i = 0u; i < domain->enforcement_count; ++i) {
        dom_institution_enforcement_init(&domain->enforcement[i]);
        domain->enforcement[i].enforcement_id = desc->enforcement[i].enforcement_id;
        domain->enforcement[i].institution_id = desc->enforcement[i].institution_id;
        domain->enforcement[i].rule_id = desc->enforcement[i].rule_id;
        domain->enforcement[i].process_family_id = desc->enforcement[i].process_family_id;
        domain->enforcement[i].agent_id = desc->enforcement[i].agent_id;
        domain->enforcement[i].action = desc->enforcement[i].action;
        domain->enforcement[i].event_tick = desc->enforcement[i].event_tick;
        domain->enforcement[i].provenance_id = desc->enforcement[i].provenance_id;
        domain->enforcement[i].region_id = desc->enforcement[i].region_id;
        domain->enforcement[i].flags = desc->enforcement[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_institution_domain_free(dom_institution_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->entity_count = 0u;
    domain->scope_count = 0u;
    domain->capability_count = 0u;
    domain->rule_count = 0u;
    domain->enforcement_count = 0u;
    domain->capsule_count = 0u;
}

void dom_institution_domain_set_state(dom_institution_domain* domain,
                                      u32 existence_state,
                                      u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_institution_domain_set_policy(dom_institution_domain* domain,
                                       const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_institution_entity_query(const dom_institution_domain* domain,
                                 u32 institution_id,
                                 dom_domain_budget* budget,
                                 dom_institution_entity_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_INSTITUTION_ENTITY_UNRESOLVED;

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_institution_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_institution_find_entity_index(domain, institution_id);
    if (index < 0) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_institution_region_collapsed(domain, domain->entities[index].region_id)) {
        out_sample->institution_id = domain->entities[index].institution_id;
        out_sample->region_id = domain->entities[index].region_id;
        out_sample->flags = DOM_INSTITUTION_ENTITY_COLLAPSED;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->institution_id = domain->entities[index].institution_id;
    out_sample->scope_id = domain->entities[index].scope_id;
    out_sample->authority_count = domain->entities[index].authority_count;
    for (u32 a = 0u; a < DOM_INSTITUTION_MAX_AUTHORITY_TYPES; ++a) {
        out_sample->authority_types[a] = domain->entities[index].authority_types[a];
    }
    out_sample->enforcement_capacity = domain->entities[index].enforcement_capacity;
    out_sample->resource_budget = domain->entities[index].resource_budget;
    out_sample->legitimacy_level = domain->entities[index].legitimacy_level;
    out_sample->legitimacy_ref_id = domain->entities[index].legitimacy_ref_id;
    out_sample->knowledge_base_id = domain->entities[index].knowledge_base_id;
    out_sample->provenance_id = domain->entities[index].provenance_id;
    out_sample->region_id = domain->entities[index].region_id;
    out_sample->flags = domain->entities[index].flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_institution_scope_query(const dom_institution_domain* domain,
                                u32 scope_id,
                                dom_domain_budget* budget,
                                dom_institution_scope_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_INSTITUTION_SCOPE_UNRESOLVED;

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_institution_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_institution_find_scope_index(domain, scope_id);
    if (index < 0) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_institution_region_collapsed(domain, domain->scopes[index].region_id)) {
        out_sample->scope_id = domain->scopes[index].scope_id;
        out_sample->region_id = domain->scopes[index].region_id;
        out_sample->flags = DOM_INSTITUTION_SCOPE_COLLAPSED;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->scope_id = domain->scopes[index].scope_id;
    out_sample->spatial_domain_id = domain->scopes[index].spatial_domain_id;
    out_sample->subject_domain_count = domain->scopes[index].subject_domain_count;
    for (u32 s = 0u; s < DOM_INSTITUTION_MAX_SUBJECT_DOMAINS; ++s) {
        out_sample->subject_domain_ids[s] = domain->scopes[index].subject_domain_ids[s];
    }
    out_sample->overlap_policy_id = domain->scopes[index].overlap_policy_id;
    out_sample->provenance_id = domain->scopes[index].provenance_id;
    out_sample->region_id = domain->scopes[index].region_id;
    out_sample->flags = domain->scopes[index].flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_institution_capability_query(const dom_institution_domain* domain,
                                     u32 capability_id,
                                     dom_domain_budget* budget,
                                     dom_institution_capability_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_INSTITUTION_CAPABILITY_UNRESOLVED;

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_institution_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_institution_find_capability_index(domain, capability_id);
    if (index < 0) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_institution_region_collapsed(domain, domain->capabilities[index].region_id)) {
        out_sample->capability_id = domain->capabilities[index].capability_id;
        out_sample->region_id = domain->capabilities[index].region_id;
        out_sample->flags = DOM_INSTITUTION_CAPABILITY_COLLAPSED;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->capability_id = domain->capabilities[index].capability_id;
    out_sample->institution_id = domain->capabilities[index].institution_id;
    out_sample->scope_id = domain->capabilities[index].scope_id;
    out_sample->authority_type_id = domain->capabilities[index].authority_type_id;
    out_sample->process_family_id = domain->capabilities[index].process_family_id;
    out_sample->capacity_limit = domain->capabilities[index].capacity_limit;
    out_sample->license_required_id = domain->capabilities[index].license_required_id;
    out_sample->provenance_id = domain->capabilities[index].provenance_id;
    out_sample->region_id = domain->capabilities[index].region_id;
    out_sample->flags = domain->capabilities[index].flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_institution_rule_query(const dom_institution_domain* domain,
                               u32 rule_id,
                               dom_domain_budget* budget,
                               dom_institution_rule_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_INSTITUTION_RULE_UNRESOLVED;

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_institution_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_institution_find_rule_index(domain, rule_id);
    if (index < 0) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_institution_region_collapsed(domain, domain->rules[index].region_id)) {
        out_sample->rule_id = domain->rules[index].rule_id;
        out_sample->region_id = domain->rules[index].region_id;
        out_sample->flags = DOM_INSTITUTION_RULE_COLLAPSED;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->rule_id = domain->rules[index].rule_id;
    out_sample->institution_id = domain->rules[index].institution_id;
    out_sample->scope_id = domain->rules[index].scope_id;
    out_sample->process_family_id = domain->rules[index].process_family_id;
    out_sample->subject_domain_id = domain->rules[index].subject_domain_id;
    out_sample->authority_type_id = domain->rules[index].authority_type_id;
    out_sample->action = domain->rules[index].action;
    out_sample->license_required_id = domain->rules[index].license_required_id;
    out_sample->provenance_id = domain->rules[index].provenance_id;
    out_sample->region_id = domain->rules[index].region_id;
    out_sample->flags = domain->rules[index].flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_institution_enforcement_query(const dom_institution_domain* domain,
                                      u32 enforcement_id,
                                      dom_domain_budget* budget,
                                      dom_institution_enforcement_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_INSTITUTION_ENFORCEMENT_UNRESOLVED;

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_institution_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_institution_find_enforcement_index(domain, enforcement_id);
    if (index < 0) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_institution_region_collapsed(domain, domain->enforcement[index].region_id)) {
        out_sample->enforcement_id = domain->enforcement[index].enforcement_id;
        out_sample->region_id = domain->enforcement[index].region_id;
        out_sample->flags = DOM_INSTITUTION_ENFORCEMENT_UNRESOLVED;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->enforcement_id = domain->enforcement[index].enforcement_id;
    out_sample->institution_id = domain->enforcement[index].institution_id;
    out_sample->rule_id = domain->enforcement[index].rule_id;
    out_sample->process_family_id = domain->enforcement[index].process_family_id;
    out_sample->agent_id = domain->enforcement[index].agent_id;
    out_sample->action = domain->enforcement[index].action;
    out_sample->event_tick = domain->enforcement[index].event_tick;
    out_sample->provenance_id = domain->enforcement[index].provenance_id;
    out_sample->region_id = domain->enforcement[index].region_id;
    out_sample->flags = domain->enforcement[index].flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_institution_region_query(const dom_institution_domain* domain,
                                 u32 region_id,
                                 dom_domain_budget* budget,
                                 dom_institution_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_entity;
    u32 cost_scope;
    u32 cost_capability;
    u32 cost_rule;
    u32 cost_enforcement;
    q48_16 enforcement_total = 0;
    q48_16 budget_total = 0;
    q16_16 legitimacy_sum = 0;
    u32 entities_seen = 0u;
    u32 scopes_seen = 0u;
    u32 capabilities_seen = 0u;
    u32 rules_seen = 0u;
    u32 enforcement_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_institution_domain_is_active(domain)) {
        dom_institution_query_meta_refused(&out_sample->meta,
                                           DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_institution_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_institution_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_institution_region_collapsed(domain, region_id)) {
        const dom_institution_macro_capsule* capsule = dom_institution_find_capsule(domain,
                                                                                    region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->entity_count = capsule->entity_count;
            out_sample->scope_count = capsule->scope_count;
            out_sample->capability_count = capsule->capability_count;
            out_sample->rule_count = capsule->rule_count;
            out_sample->enforcement_count = capsule->enforcement_count;
            out_sample->enforcement_capacity_avg = capsule->enforcement_capacity_avg;
            out_sample->resource_budget_avg = capsule->resource_budget_avg;
            out_sample->legitimacy_avg = capsule->legitimacy_avg;
            for (u32 a = 0u; a < DOM_INSTITUTION_ACTION_BINS; ++a) {
                out_sample->enforcement_action_counts[a] = capsule->enforcement_action_counts[a];
            }
        }
        out_sample->flags = DOM_INSTITUTION_RESOLVE_PARTIAL;
        dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                      DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_entity = dom_institution_budget_cost(domain->policy.cost_medium);
    cost_scope = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_capability = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_rule = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_enforcement = dom_institution_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->entity_count; ++i) {
        u32 entity_region = domain->entities[i].region_id;
        if (region_id != 0u && entity_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, entity_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_entity)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            break;
        }
        enforcement_total = d_q48_16_add(enforcement_total,
                                         domain->entities[i].enforcement_capacity);
        budget_total = d_q48_16_add(budget_total, domain->entities[i].resource_budget);
        legitimacy_sum = d_q16_16_add(legitimacy_sum, domain->entities[i].legitimacy_level);
        entities_seen += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        u32 scope_region = domain->scopes[i].region_id;
        if (region_id != 0u && scope_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, scope_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_scope)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            break;
        }
        scopes_seen += 1u;
    }

    for (u32 i = 0u; i < domain->capability_count; ++i) {
        u32 cap_region = domain->capabilities[i].region_id;
        if (region_id != 0u && cap_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, cap_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_capability)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            break;
        }
        capabilities_seen += 1u;
    }

    for (u32 i = 0u; i < domain->rule_count; ++i) {
        u32 rule_region = domain->rules[i].region_id;
        if (region_id != 0u && rule_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, rule_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_rule)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            break;
        }
        rules_seen += 1u;
    }

    for (u32 i = 0u; i < domain->enforcement_count; ++i) {
        u32 enforcement_region = domain->enforcement[i].region_id;
        if (region_id != 0u && enforcement_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, enforcement_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_enforcement)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            break;
        }
        enforcement_seen += 1u;
        {
            u32 index = dom_institution_action_index(domain->enforcement[i].action);
            if (index < DOM_INSTITUTION_ACTION_BINS) {
                out_sample->enforcement_action_counts[index] += 1u;
            }
        }
    }

    out_sample->region_id = region_id;
    out_sample->entity_count = entities_seen;
    out_sample->scope_count = scopes_seen;
    out_sample->capability_count = capabilities_seen;
    out_sample->rule_count = rules_seen;
    out_sample->enforcement_count = enforcement_seen;
    if (entities_seen > 0u) {
        q48_16 div_capacity = d_q48_16_div(enforcement_total,
                                          d_q48_16_from_int((i64)entities_seen));
        q48_16 div_budget = d_q48_16_div(budget_total,
                                        d_q48_16_from_int((i64)entities_seen));
        out_sample->enforcement_capacity_avg = div_capacity;
        out_sample->resource_budget_avg = div_budget;
        out_sample->legitimacy_avg = dom_institution_clamp_ratio(
            (q16_16)(legitimacy_sum / (i32)entities_seen));
    }
    out_sample->flags = flags;
    dom_institution_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                                  cost_base, budget);
    return 0;
}

int dom_institution_resolve(dom_institution_domain* domain,
                            u32 region_id,
                            u64 tick,
                            u64 tick_delta,
                            dom_domain_budget* budget,
                            dom_institution_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_entity;
    u32 cost_scope;
    u32 cost_capability;
    u32 cost_rule;
    u32 cost_enforcement;
    q48_16 enforcement_total = 0;
    q48_16 budget_total = 0;
    q16_16 legitimacy_sum = 0;
    u32 entities_seen = 0u;
    u32 scopes_seen = 0u;
    u32 capabilities_seen = 0u;
    u32 rules_seen = 0u;
    u32 enforcement_seen = 0u;
    u32 enforcement_applied = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_institution_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_INSTITUTION_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_institution_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_institution_region_collapsed(domain, region_id)) {
        const dom_institution_macro_capsule* capsule = dom_institution_find_capsule(domain,
                                                                                    region_id);
        if (capsule) {
            out_result->entity_count = capsule->entity_count;
            out_result->scope_count = capsule->scope_count;
            out_result->capability_count = capsule->capability_count;
            out_result->rule_count = capsule->rule_count;
            out_result->enforcement_count = capsule->enforcement_count;
            out_result->enforcement_capacity_avg = capsule->enforcement_capacity_avg;
            out_result->resource_budget_avg = capsule->resource_budget_avg;
            out_result->legitimacy_avg = capsule->legitimacy_avg;
            for (u32 a = 0u; a < DOM_INSTITUTION_ACTION_BINS; ++a) {
                out_result->enforcement_action_counts[a] = capsule->enforcement_action_counts[a];
            }
        }
        out_result->ok = 1u;
        out_result->flags = DOM_INSTITUTION_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_entity = dom_institution_budget_cost(domain->policy.cost_medium);
    cost_scope = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_capability = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_rule = dom_institution_budget_cost(domain->policy.cost_coarse);
    cost_enforcement = dom_institution_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->entity_count; ++i) {
        u32 entity_region = domain->entities[i].region_id;
        if (region_id != 0u && entity_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, entity_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_entity)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_INSTITUTION_REFUSE_NONE) {
                out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
            }
            break;
        }
        enforcement_total = d_q48_16_add(enforcement_total,
                                         domain->entities[i].enforcement_capacity);
        budget_total = d_q48_16_add(budget_total, domain->entities[i].resource_budget);
        legitimacy_sum = d_q16_16_add(legitimacy_sum, domain->entities[i].legitimacy_level);
        entities_seen += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        u32 scope_region = domain->scopes[i].region_id;
        if (region_id != 0u && scope_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, scope_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_scope)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_INSTITUTION_REFUSE_NONE) {
                out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
            }
            break;
        }
        scopes_seen += 1u;
    }

    for (u32 i = 0u; i < domain->capability_count; ++i) {
        u32 cap_region = domain->capabilities[i].region_id;
        if (region_id != 0u && cap_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, cap_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_capability)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_INSTITUTION_REFUSE_NONE) {
                out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
            }
            break;
        }
        capabilities_seen += 1u;
    }

    for (u32 i = 0u; i < domain->rule_count; ++i) {
        u32 rule_region = domain->rules[i].region_id;
        if (region_id != 0u && rule_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, rule_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_rule)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_INSTITUTION_REFUSE_NONE) {
                out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
            }
            break;
        }
        rules_seen += 1u;
    }

    for (u32 i = 0u; i < domain->enforcement_count; ++i) {
        dom_institution_enforcement* enforcement = &domain->enforcement[i];
        u32 enforcement_region = enforcement->region_id;
        if (region_id != 0u && enforcement_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_institution_region_collapsed(domain, enforcement_region)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_enforcement)) {
            flags |= DOM_INSTITUTION_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_INSTITUTION_REFUSE_NONE) {
                out_result->refusal_reason = DOM_INSTITUTION_REFUSE_BUDGET;
            }
            break;
        }
        enforcement_seen += 1u;
        if (dom_institution_apply_enforcement(enforcement, tick,
                                              out_result->enforcement_action_counts)) {
            enforcement_applied += 1u;
            flags |= DOM_INSTITUTION_RESOLVE_EVENTS_APPLIED;
        }
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->entity_count = entities_seen;
    out_result->scope_count = scopes_seen;
    out_result->capability_count = capabilities_seen;
    out_result->rule_count = rules_seen;
    out_result->enforcement_count = enforcement_seen;
    out_result->enforcement_applied_count = enforcement_applied;
    if (entities_seen > 0u) {
        q48_16 div_capacity = d_q48_16_div(enforcement_total,
                                          d_q48_16_from_int((i64)entities_seen));
        q48_16 div_budget = d_q48_16_div(budget_total,
                                        d_q48_16_from_int((i64)entities_seen));
        out_result->enforcement_capacity_avg = div_capacity;
        out_result->resource_budget_avg = div_budget;
        out_result->legitimacy_avg = dom_institution_clamp_ratio(
            (q16_16)(legitimacy_sum / (i32)entities_seen));
    }
    return 0;
}

int dom_institution_domain_collapse_region(dom_institution_domain* domain, u32 region_id)
{
    dom_institution_macro_capsule capsule;
    u32 legitimacy_bins[DOM_INSTITUTION_HIST_BINS];
    q48_16 enforcement_total = 0;
    q48_16 budget_total = 0;
    q16_16 legitimacy_sum = 0;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_institution_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_INSTITUTION_MAX_CAPSULES) {
        return -2;
    }
    memset(&capsule, 0, sizeof(capsule));
    memset(legitimacy_bins, 0, sizeof(legitimacy_bins));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->entity_count; ++i) {
        if (domain->entities[i].region_id != region_id) {
            continue;
        }
        capsule.entity_count += 1u;
        enforcement_total = d_q48_16_add(enforcement_total,
                                         domain->entities[i].enforcement_capacity);
        budget_total = d_q48_16_add(budget_total, domain->entities[i].resource_budget);
        legitimacy_sum = d_q16_16_add(legitimacy_sum, domain->entities[i].legitimacy_level);
        legitimacy_bins[dom_institution_hist_bin(domain->entities[i].legitimacy_level)] += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        if (domain->scopes[i].region_id != region_id) {
            continue;
        }
        capsule.scope_count += 1u;
    }

    for (u32 i = 0u; i < domain->capability_count; ++i) {
        if (domain->capabilities[i].region_id != region_id) {
            continue;
        }
        capsule.capability_count += 1u;
    }

    for (u32 i = 0u; i < domain->rule_count; ++i) {
        if (domain->rules[i].region_id != region_id) {
            continue;
        }
        capsule.rule_count += 1u;
    }

    for (u32 i = 0u; i < domain->enforcement_count; ++i) {
        if (domain->enforcement[i].region_id != region_id) {
            continue;
        }
        capsule.enforcement_count += 1u;
        {
            u32 index = dom_institution_action_index(domain->enforcement[i].action);
            if (index < DOM_INSTITUTION_ACTION_BINS) {
                capsule.enforcement_action_counts[index] += 1u;
            }
        }
    }

    if (capsule.entity_count > 0u) {
        q48_16 div_capacity = d_q48_16_div(enforcement_total,
                                          d_q48_16_from_int((i64)capsule.entity_count));
        q48_16 div_budget = d_q48_16_div(budget_total,
                                        d_q48_16_from_int((i64)capsule.entity_count));
        capsule.enforcement_capacity_avg = div_capacity;
        capsule.resource_budget_avg = div_budget;
        capsule.legitimacy_avg = dom_institution_clamp_ratio(
            (q16_16)(legitimacy_sum / (i32)capsule.entity_count));
    }
    for (u32 b = 0u; b < DOM_INSTITUTION_HIST_BINS; ++b) {
        capsule.legitimacy_hist[b] = dom_institution_ratio_from_counts(legitimacy_bins[b],
                                                                       capsule.entity_count);
    }

    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_institution_domain_expand_region(dom_institution_domain* domain, u32 region_id)
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

u32 dom_institution_domain_capsule_count(const dom_institution_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_institution_macro_capsule* dom_institution_domain_capsule_at(
    const dom_institution_domain* domain,
    u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_institution_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
