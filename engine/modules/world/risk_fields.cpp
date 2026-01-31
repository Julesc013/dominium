/*
FILE: source/domino/world/risk_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/risk_fields
RESPONSIBILITY: Implements deterministic risk fields, liability, and insurance resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/risk_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_RISK_RESOLVE_COST_BASE 1u
#define DOM_RISK_AUDIT_MIN_Q16 ((q16_16)0x00008000)
#define DOM_RISK_AUDIT_PENALTY_Q16 ((q16_16)0x00008000)

static q16_16 dom_risk_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_RISK_RATIO_ONE_Q16) {
        return DOM_RISK_RATIO_ONE_Q16;
    }
    return value;
}

static q48_16 dom_risk_q48_from_q16(q16_16 value)
{
    return d_q48_16_from_q16_16(value);
}

static q48_16 dom_risk_apply_ratio_q48(q48_16 value, q16_16 ratio)
{
    q16_16 clamped = dom_risk_clamp_ratio(ratio);
    if (value == 0 || clamped <= 0) {
        return 0;
    }
    if (clamped >= DOM_RISK_RATIO_ONE_Q16) {
        return value;
    }
    return d_q48_16_mul(value, d_q48_16_from_q16_16(clamped));
}

static void dom_risk_type_init(dom_risk_type* type)
{
    if (!type) {
        return;
    }
    memset(type, 0, sizeof(*type));
    type->risk_class = DOM_RISK_CLASS_UNSET;
}

static void dom_risk_field_init(dom_risk_field* field)
{
    if (!field) {
        return;
    }
    memset(field, 0, sizeof(*field));
}

static void dom_risk_exposure_init(dom_risk_exposure* exposure)
{
    if (!exposure) {
        return;
    }
    memset(exposure, 0, sizeof(*exposure));
}

static void dom_risk_profile_init(dom_risk_profile* profile)
{
    if (!profile) {
        return;
    }
    memset(profile, 0, sizeof(*profile));
}

static void dom_risk_event_init(dom_liability_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
}

static void dom_risk_attribution_init(dom_liability_attribution* attribution)
{
    if (!attribution) {
        return;
    }
    memset(attribution, 0, sizeof(*attribution));
}

static void dom_risk_policy_init(dom_insurance_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
}

static void dom_risk_claim_init(dom_insurance_claim* claim)
{
    if (!claim) {
        return;
    }
    memset(claim, 0, sizeof(*claim));
}

static int dom_risk_find_type_index(const dom_risk_domain* domain, u32 type_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->type_count; ++i) {
        if (domain->types[i].type_id == type_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_field_index(const dom_risk_domain* domain, u32 field_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->field_count; ++i) {
        if (domain->fields[i].risk_id == field_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_exposure_index(const dom_risk_domain* domain, u32 exposure_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        if (domain->exposures[i].exposure_id == exposure_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_profile_index(const dom_risk_domain* domain, u32 profile_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->profile_count; ++i) {
        if (domain->profiles[i].profile_id == profile_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_event_index(const dom_risk_domain* domain, u32 event_id)
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

static int dom_risk_find_attribution_index(const dom_risk_domain* domain, u32 attribution_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->attribution_count; ++i) {
        if (domain->attributions[i].attribution_id == attribution_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_policy_index(const dom_risk_domain* domain, u32 policy_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->policy_count; ++i) {
        if (domain->policies[i].policy_id == policy_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_risk_find_claim_index(const dom_risk_domain* domain, u32 claim_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->claim_count; ++i) {
        if (domain->claims[i].claim_id == claim_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_risk_domain_is_active(const dom_risk_domain* domain)
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

static d_bool dom_risk_region_collapsed(const dom_risk_domain* domain, u32 region_id)
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

static const dom_risk_macro_capsule* dom_risk_find_capsule(const dom_risk_domain* domain,
                                                           u32 region_id)
{
    if (!domain) {
        return (const dom_risk_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_risk_macro_capsule*)0;
}

static void dom_risk_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_risk_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_risk_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_RISK_RESOLVE_COST_BASE : cost_units;
}

static q16_16 dom_risk_distance_q16(const dom_domain_point* a, const dom_domain_point* b)
{
    q16_16 dx;
    q16_16 dy;
    q16_16 dz;
    q16_16 sum;
    if (!a || !b) {
        return 0;
    }
    dx = d_q16_16_sub(a->x, b->x);
    dy = d_q16_16_sub(a->y, b->y);
    dz = d_q16_16_sub(a->z, b->z);
    sum = d_q16_16_add(d_q16_16_mul(dx, dx), d_q16_16_mul(dy, dy));
    sum = d_q16_16_add(sum, d_q16_16_mul(dz, dz));
    if (sum < 0) {
        sum = 0;
    }
    return d_fixed_sqrt_q16_16(sum);
}

static q16_16 dom_risk_falloff(const dom_risk_field* field, const dom_domain_point* point)
{
    q16_16 distance;
    q16_16 radius;
    q16_16 remaining;
    if (!field || !point) {
        return 0;
    }
    radius = field->radius;
    distance = dom_risk_distance_q16(&field->center, point);
    if (radius <= 0) {
        return (distance <= 0) ? DOM_RISK_RATIO_ONE_Q16 : 0;
    }
    if (distance >= radius) {
        return 0;
    }
    remaining = d_q16_16_sub(radius, distance);
    return dom_risk_clamp_ratio(d_fixed_div_q16_16(remaining, radius));
}

static q16_16 dom_risk_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_risk_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_risk_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_RISK_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_RISK_HIST_BINS) {
        scaled = DOM_RISK_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_risk_surface_desc_init(dom_risk_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->type_count = 0u;
    desc->field_count = 0u;
    desc->exposure_count = 0u;
    desc->profile_count = 0u;
    desc->event_count = 0u;
    desc->attribution_count = 0u;
    desc->policy_count = 0u;
    desc->claim_count = 0u;
    for (u32 i = 0u; i < DOM_RISK_MAX_TYPES; ++i) {
        desc->types[i].type_id = 0u;
        desc->types[i].risk_class = DOM_RISK_CLASS_UNSET;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_FIELDS; ++i) {
        desc->fields[i].risk_id = 0u;
        desc->fields[i].risk_type_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_EXPOSURES; ++i) {
        desc->exposures[i].exposure_id = 0u;
        desc->exposures[i].risk_type_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_PROFILES; ++i) {
        desc->profiles[i].profile_id = 0u;
        desc->profiles[i].subject_ref_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
        desc->events[i].risk_type_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_ATTRIBUTIONS; ++i) {
        desc->attributions[i].attribution_id = 0u;
        desc->attributions[i].event_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_POLICIES; ++i) {
        desc->policies[i].policy_id = 0u;
        desc->policies[i].holder_ref_id = 0u;
    }
    for (u32 i = 0u; i < DOM_RISK_MAX_CLAIMS; ++i) {
        desc->claims[i].claim_id = 0u;
        desc->claims[i].policy_id = 0u;
    }
}

void dom_risk_domain_init(dom_risk_domain* domain,
                          const dom_risk_surface_desc* desc)
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

    domain->type_count = (desc->type_count > DOM_RISK_MAX_TYPES)
                           ? DOM_RISK_MAX_TYPES
                           : desc->type_count;
    domain->field_count = (desc->field_count > DOM_RISK_MAX_FIELDS)
                            ? DOM_RISK_MAX_FIELDS
                            : desc->field_count;
    domain->exposure_count = (desc->exposure_count > DOM_RISK_MAX_EXPOSURES)
                               ? DOM_RISK_MAX_EXPOSURES
                               : desc->exposure_count;
    domain->profile_count = (desc->profile_count > DOM_RISK_MAX_PROFILES)
                              ? DOM_RISK_MAX_PROFILES
                              : desc->profile_count;
    domain->event_count = (desc->event_count > DOM_RISK_MAX_EVENTS)
                            ? DOM_RISK_MAX_EVENTS
                            : desc->event_count;
    domain->attribution_count = (desc->attribution_count > DOM_RISK_MAX_ATTRIBUTIONS)
                                  ? DOM_RISK_MAX_ATTRIBUTIONS
                                  : desc->attribution_count;
    domain->policy_count = (desc->policy_count > DOM_RISK_MAX_POLICIES)
                             ? DOM_RISK_MAX_POLICIES
                             : desc->policy_count;
    domain->claim_count = (desc->claim_count > DOM_RISK_MAX_CLAIMS)
                            ? DOM_RISK_MAX_CLAIMS
                            : desc->claim_count;

    for (u32 i = 0u; i < domain->type_count; ++i) {
        dom_risk_type_init(&domain->types[i]);
        domain->types[i].type_id = desc->types[i].type_id;
        domain->types[i].risk_class = desc->types[i].risk_class;
        domain->types[i].default_exposure_rate = desc->types[i].default_exposure_rate;
        domain->types[i].default_impact_mean = desc->types[i].default_impact_mean;
        domain->types[i].default_impact_spread = desc->types[i].default_impact_spread;
        domain->types[i].default_uncertainty = desc->types[i].default_uncertainty;
    }

    for (u32 i = 0u; i < domain->field_count; ++i) {
        dom_risk_field_init(&domain->fields[i]);
        domain->fields[i].risk_id = desc->fields[i].risk_id;
        domain->fields[i].risk_type_id = desc->fields[i].risk_type_id;
        domain->fields[i].exposure_rate = desc->fields[i].exposure_rate;
        domain->fields[i].impact_mean = desc->fields[i].impact_mean;
        domain->fields[i].impact_spread = desc->fields[i].impact_spread;
        domain->fields[i].uncertainty = desc->fields[i].uncertainty;
        domain->fields[i].hazard_ref_id = desc->fields[i].hazard_ref_id;
        domain->fields[i].provenance_id = desc->fields[i].provenance_id;
        domain->fields[i].region_id = desc->fields[i].region_id;
        domain->fields[i].radius = desc->fields[i].radius;
        domain->fields[i].center = desc->fields[i].center;
    }

    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        dom_risk_exposure_init(&domain->exposures[i]);
        domain->exposures[i].exposure_id = desc->exposures[i].exposure_id;
        domain->exposures[i].risk_type_id = desc->exposures[i].risk_type_id;
        domain->exposures[i].exposure_rate = desc->exposures[i].exposure_rate;
        domain->exposures[i].exposure_limit = desc->exposures[i].exposure_limit;
        domain->exposures[i].exposure_accumulated = desc->exposures[i].exposure_accumulated;
        domain->exposures[i].sensitivity = desc->exposures[i].sensitivity;
        domain->exposures[i].uncertainty = desc->exposures[i].uncertainty;
        domain->exposures[i].subject_ref_id = desc->exposures[i].subject_ref_id;
        domain->exposures[i].region_id = desc->exposures[i].region_id;
        domain->exposures[i].location = desc->exposures[i].location;
        domain->exposures[i].provenance_id = desc->exposures[i].provenance_id;
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        dom_risk_profile_init(&domain->profiles[i]);
        domain->profiles[i].profile_id = desc->profiles[i].profile_id;
        domain->profiles[i].subject_ref_id = desc->profiles[i].subject_ref_id;
        domain->profiles[i].region_id = desc->profiles[i].region_id;
        domain->profiles[i].exposure_total = desc->profiles[i].exposure_total;
        domain->profiles[i].impact_mean = desc->profiles[i].impact_mean;
        domain->profiles[i].impact_spread = desc->profiles[i].impact_spread;
        domain->profiles[i].uncertainty = desc->profiles[i].uncertainty;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_risk_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].risk_type_id = desc->events[i].risk_type_id;
        domain->events[i].hazard_ref_id = desc->events[i].hazard_ref_id;
        domain->events[i].exposure_ref_id = desc->events[i].exposure_ref_id;
        domain->events[i].loss_amount = desc->events[i].loss_amount;
        domain->events[i].event_tick = desc->events[i].event_tick;
        domain->events[i].subject_ref_id = desc->events[i].subject_ref_id;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
    }

    for (u32 i = 0u; i < domain->attribution_count; ++i) {
        dom_risk_attribution_init(&domain->attributions[i]);
        domain->attributions[i].attribution_id = desc->attributions[i].attribution_id;
        domain->attributions[i].event_id = desc->attributions[i].event_id;
        domain->attributions[i].responsible_ref_id = desc->attributions[i].responsible_ref_id;
        domain->attributions[i].role_tag = desc->attributions[i].role_tag;
        domain->attributions[i].compliance_tag = desc->attributions[i].compliance_tag;
        domain->attributions[i].negligence_score = desc->attributions[i].negligence_score;
        domain->attributions[i].share_ratio = desc->attributions[i].share_ratio;
        domain->attributions[i].uncertainty = desc->attributions[i].uncertainty;
        domain->attributions[i].provenance_id = desc->attributions[i].provenance_id;
    }

    for (u32 i = 0u; i < domain->policy_count; ++i) {
        dom_risk_policy_init(&domain->policies[i]);
        domain->policies[i].policy_id = desc->policies[i].policy_id;
        domain->policies[i].holder_ref_id = desc->policies[i].holder_ref_id;
        domain->policies[i].risk_type_id = desc->policies[i].risk_type_id;
        domain->policies[i].coverage_ratio = desc->policies[i].coverage_ratio;
        domain->policies[i].premium = desc->policies[i].premium;
        domain->policies[i].payout_limit = desc->policies[i].payout_limit;
        domain->policies[i].deductible = desc->policies[i].deductible;
        domain->policies[i].audit_tag = desc->policies[i].audit_tag;
        domain->policies[i].audit_score = desc->policies[i].audit_score;
        domain->policies[i].start_tick = desc->policies[i].start_tick;
        domain->policies[i].end_tick = desc->policies[i].end_tick;
        domain->policies[i].region_id = desc->policies[i].region_id;
    }

    for (u32 i = 0u; i < domain->claim_count; ++i) {
        dom_risk_claim_init(&domain->claims[i]);
        domain->claims[i].claim_id = desc->claims[i].claim_id;
        domain->claims[i].policy_id = desc->claims[i].policy_id;
        domain->claims[i].event_id = desc->claims[i].event_id;
        domain->claims[i].claim_amount = desc->claims[i].claim_amount;
        domain->claims[i].approved_amount = desc->claims[i].approved_amount;
        domain->claims[i].status_tag = desc->claims[i].status_tag;
        domain->claims[i].filed_tick = desc->claims[i].filed_tick;
        domain->claims[i].resolved_tick = desc->claims[i].resolved_tick;
        domain->claims[i].audit_ref_id = desc->claims[i].audit_ref_id;
    }

    domain->capsule_count = 0u;
}

void dom_risk_domain_free(dom_risk_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->type_count = 0u;
    domain->field_count = 0u;
    domain->exposure_count = 0u;
    domain->profile_count = 0u;
    domain->event_count = 0u;
    domain->attribution_count = 0u;
    domain->policy_count = 0u;
    domain->claim_count = 0u;
    domain->capsule_count = 0u;
}

void dom_risk_domain_set_state(dom_risk_domain* domain,
                               u32 existence_state,
                               u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_risk_domain_set_policy(dom_risk_domain* domain,
                                const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_risk_type_query(const dom_risk_domain* domain,
                        u32 type_id,
                        dom_domain_budget* budget,
                        dom_risk_type_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_TYPE_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_type_index(domain, type_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->type_id = domain->types[index].type_id;
    out_sample->risk_class = domain->types[index].risk_class;
    out_sample->default_exposure_rate = domain->types[index].default_exposure_rate;
    out_sample->default_impact_mean = domain->types[index].default_impact_mean;
    out_sample->default_impact_spread = domain->types[index].default_impact_spread;
    out_sample->default_uncertainty = domain->types[index].default_uncertainty;
    out_sample->flags = 0u;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_risk_field_query(const dom_risk_domain* domain,
                         u32 field_id,
                         dom_domain_budget* budget,
                         dom_risk_field_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_FIELD_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_field_index(domain, field_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_risk_region_collapsed(domain, domain->fields[index].region_id)) {
        out_sample->risk_id = domain->fields[index].risk_id;
        out_sample->risk_type_id = domain->fields[index].risk_type_id;
        out_sample->region_id = domain->fields[index].region_id;
        out_sample->flags = DOM_RISK_FIELD_COLLAPSED;
        dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->risk_id = domain->fields[index].risk_id;
    out_sample->risk_type_id = domain->fields[index].risk_type_id;
    out_sample->exposure_rate = domain->fields[index].exposure_rate;
    out_sample->impact_mean = domain->fields[index].impact_mean;
    out_sample->impact_spread = domain->fields[index].impact_spread;
    out_sample->uncertainty = domain->fields[index].uncertainty;
    out_sample->hazard_ref_id = domain->fields[index].hazard_ref_id;
    out_sample->provenance_id = domain->fields[index].provenance_id;
    out_sample->region_id = domain->fields[index].region_id;
    out_sample->radius = domain->fields[index].radius;
    out_sample->flags = 0u;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_risk_exposure_query(const dom_risk_domain* domain,
                            u32 exposure_id,
                            dom_domain_budget* budget,
                            dom_risk_exposure_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_EXPOSURE_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_exposure_index(domain, exposure_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_risk_region_collapsed(domain, domain->exposures[index].region_id)) {
        out_sample->exposure_id = domain->exposures[index].exposure_id;
        out_sample->risk_type_id = domain->exposures[index].risk_type_id;
        out_sample->region_id = domain->exposures[index].region_id;
        out_sample->flags = DOM_RISK_EXPOSURE_COLLAPSED;
        dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->exposure_id = domain->exposures[index].exposure_id;
    out_sample->risk_type_id = domain->exposures[index].risk_type_id;
    out_sample->exposure_rate = domain->exposures[index].exposure_rate;
    out_sample->exposure_limit = domain->exposures[index].exposure_limit;
    out_sample->exposure_accumulated = domain->exposures[index].exposure_accumulated;
    out_sample->sensitivity = domain->exposures[index].sensitivity;
    out_sample->uncertainty = domain->exposures[index].uncertainty;
    out_sample->subject_ref_id = domain->exposures[index].subject_ref_id;
    out_sample->region_id = domain->exposures[index].region_id;
    out_sample->provenance_id = domain->exposures[index].provenance_id;
    out_sample->flags = 0u;
    if (out_sample->exposure_limit > 0 &&
        out_sample->exposure_accumulated >= out_sample->exposure_limit) {
        out_sample->flags |= DOM_RISK_EXPOSURE_OVER_LIMIT;
    }
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_risk_profile_query(const dom_risk_domain* domain,
                           u32 profile_id,
                           dom_domain_budget* budget,
                           dom_risk_profile_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_PROFILE_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_profile_index(domain, profile_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_risk_region_collapsed(domain, domain->profiles[index].region_id)) {
        out_sample->profile_id = domain->profiles[index].profile_id;
        out_sample->subject_ref_id = domain->profiles[index].subject_ref_id;
        out_sample->region_id = domain->profiles[index].region_id;
        out_sample->flags = DOM_RISK_PROFILE_COLLAPSED;
        dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->profile_id = domain->profiles[index].profile_id;
    out_sample->subject_ref_id = domain->profiles[index].subject_ref_id;
    out_sample->region_id = domain->profiles[index].region_id;
    out_sample->exposure_total = domain->profiles[index].exposure_total;
    out_sample->impact_mean = domain->profiles[index].impact_mean;
    out_sample->impact_spread = domain->profiles[index].impact_spread;
    out_sample->uncertainty = domain->profiles[index].uncertainty;
    out_sample->flags = domain->profiles[index].flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_liability_event_query(const dom_risk_domain* domain,
                              u32 event_id,
                              dom_domain_budget* budget,
                              dom_liability_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_EVENT_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_event_index(domain, event_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_risk_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->risk_type_id = domain->events[index].risk_type_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_RISK_EVENT_UNRESOLVED;
        dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->risk_type_id = domain->events[index].risk_type_id;
    out_sample->hazard_ref_id = domain->events[index].hazard_ref_id;
    out_sample->exposure_ref_id = domain->events[index].exposure_ref_id;
    out_sample->loss_amount = domain->events[index].loss_amount;
    out_sample->event_tick = domain->events[index].event_tick;
    out_sample->subject_ref_id = domain->events[index].subject_ref_id;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->flags = domain->events[index].flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_liability_attribution_query(const dom_risk_domain* domain,
                                    u32 attribution_id,
                                    dom_domain_budget* budget,
                                    dom_liability_attribution_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_ATTR_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_attribution_index(domain, attribution_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->attribution_id = domain->attributions[index].attribution_id;
    out_sample->event_id = domain->attributions[index].event_id;
    out_sample->responsible_ref_id = domain->attributions[index].responsible_ref_id;
    out_sample->role_tag = domain->attributions[index].role_tag;
    out_sample->compliance_tag = domain->attributions[index].compliance_tag;
    out_sample->negligence_score = domain->attributions[index].negligence_score;
    out_sample->share_ratio = domain->attributions[index].share_ratio;
    out_sample->uncertainty = domain->attributions[index].uncertainty;
    out_sample->provenance_id = domain->attributions[index].provenance_id;
    out_sample->flags = domain->attributions[index].flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_insurance_policy_query(const dom_risk_domain* domain,
                               u32 policy_id,
                               dom_domain_budget* budget,
                               dom_insurance_policy_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_POLICY_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_policy_index(domain, policy_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->policy_id = domain->policies[index].policy_id;
    out_sample->holder_ref_id = domain->policies[index].holder_ref_id;
    out_sample->risk_type_id = domain->policies[index].risk_type_id;
    out_sample->coverage_ratio = domain->policies[index].coverage_ratio;
    out_sample->premium = domain->policies[index].premium;
    out_sample->payout_limit = domain->policies[index].payout_limit;
    out_sample->deductible = domain->policies[index].deductible;
    out_sample->audit_tag = domain->policies[index].audit_tag;
    out_sample->audit_score = domain->policies[index].audit_score;
    out_sample->start_tick = domain->policies[index].start_tick;
    out_sample->end_tick = domain->policies[index].end_tick;
    out_sample->region_id = domain->policies[index].region_id;
    out_sample->flags = domain->policies[index].flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_insurance_claim_query(const dom_risk_domain* domain,
                              u32 claim_id,
                              dom_domain_budget* budget,
                              dom_insurance_claim_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_RISK_CLAIM_UNRESOLVED;

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_risk_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_risk_find_claim_index(domain, claim_id);
    if (index < 0) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->claim_id = domain->claims[index].claim_id;
    out_sample->policy_id = domain->claims[index].policy_id;
    out_sample->event_id = domain->claims[index].event_id;
    out_sample->claim_amount = domain->claims[index].claim_amount;
    out_sample->approved_amount = domain->claims[index].approved_amount;
    out_sample->status_tag = domain->claims[index].status_tag;
    out_sample->filed_tick = domain->claims[index].filed_tick;
    out_sample->resolved_tick = domain->claims[index].resolved_tick;
    out_sample->audit_ref_id = domain->claims[index].audit_ref_id;
    out_sample->flags = domain->claims[index].flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_risk_region_query(const dom_risk_domain* domain,
                          u32 region_id,
                          dom_domain_budget* budget,
                          dom_risk_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_exposure;
    u32 cost_profile;
    q48_16 exposure_total = 0;
    q48_16 impact_mean_total = 0;
    q16_16 impact_spread_sum = 0;
    u32 field_seen = 0u;
    u32 exposure_seen = 0u;
    u32 profile_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_risk_domain_is_active(domain)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_risk_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_risk_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_risk_region_collapsed(domain, region_id)) {
        const dom_risk_macro_capsule* capsule = dom_risk_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->field_count = capsule->field_count;
            out_sample->exposure_count = capsule->exposure_count;
            out_sample->profile_count = capsule->profile_count;
            out_sample->exposure_total = capsule->exposure_total;
        }
        out_sample->flags = DOM_RISK_RESOLVE_PARTIAL;
        dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_field = dom_risk_budget_cost(domain->policy.cost_medium);
    cost_exposure = dom_risk_budget_cost(domain->policy.cost_coarse);
    cost_profile = dom_risk_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, field_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            break;
        }
        impact_mean_total = d_q48_16_add(impact_mean_total, domain->fields[i].impact_mean);
        impact_spread_sum = d_q16_16_add(impact_spread_sum, domain->fields[i].impact_spread);
        field_seen += 1u;
    }

    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        u32 exposure_region = domain->exposures[i].region_id;
        if (region_id != 0u && exposure_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, exposure_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_exposure)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            break;
        }
        exposure_total = d_q48_16_add(exposure_total, domain->exposures[i].exposure_accumulated);
        exposure_seen += 1u;
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        u32 profile_region = domain->profiles[i].region_id;
        if (region_id != 0u && profile_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, profile_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_profile)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            break;
        }
        profile_seen += 1u;
    }

    out_sample->region_id = region_id;
    out_sample->field_count = field_seen;
    out_sample->exposure_count = exposure_seen;
    out_sample->profile_count = profile_seen;
    out_sample->exposure_total = exposure_total;
    out_sample->impact_mean_total = impact_mean_total;
    if (field_seen > 0u) {
        out_sample->impact_spread_avg = (q16_16)(impact_spread_sum / (i32)field_seen);
    }
    out_sample->flags = flags;
    dom_risk_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                           cost_base, budget);
    return 0;
}

int dom_risk_resolve(dom_risk_domain* domain,
                     u32 region_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_risk_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_exposure;
    u32 cost_profile;
    u32 cost_claim;
    q48_16 exposure_total = 0;
    q48_16 impact_mean_total = 0;
    q48_16 claim_paid_total = 0;
    u32 fields_seen = 0u;
    u32 exposures_seen = 0u;
    u32 profiles_seen = 0u;
    u32 over_limit_count = 0u;
    u32 claim_count = 0u;
    u32 claim_approved = 0u;
    u32 claim_denied = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    (void)tick;
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_risk_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_RISK_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_risk_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_risk_region_collapsed(domain, region_id)) {
        const dom_risk_macro_capsule* capsule = dom_risk_find_capsule(domain, region_id);
        if (capsule) {
            out_result->field_count = capsule->field_count;
            out_result->exposure_count = capsule->exposure_count;
            out_result->profile_count = capsule->profile_count;
            out_result->exposure_total = capsule->exposure_total;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_RISK_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_field = dom_risk_budget_cost(domain->policy.cost_medium);
    cost_exposure = dom_risk_budget_cost(domain->policy.cost_coarse);
    cost_profile = dom_risk_budget_cost(domain->policy.cost_coarse);
    cost_claim = dom_risk_budget_cost(domain->policy.cost_medium);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, field_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_RISK_REFUSE_NONE) {
                out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
            }
            break;
        }
        fields_seen += 1u;
    }

    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        dom_risk_exposure* exposure = &domain->exposures[i];
        q48_16 exposure_delta_total = 0;
        u32 exposure_region = exposure->region_id;
        if (region_id != 0u && exposure_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, exposure_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_exposure)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_RISK_REFUSE_NONE) {
                out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
            }
            break;
        }
        for (u32 f = 0u; f < domain->field_count; ++f) {
            const dom_risk_field* field = &domain->fields[f];
            q16_16 falloff;
            q16_16 contribution;
            if (region_id != 0u && field->region_id != region_id) {
                continue;
            }
            if (region_id == 0u && dom_risk_region_collapsed(domain, field->region_id)) {
                flags |= DOM_RISK_RESOLVE_PARTIAL;
                continue;
            }
            if (exposure->risk_type_id != 0u &&
                exposure->risk_type_id != field->risk_type_id) {
                continue;
            }
            if (!dom_domain_budget_consume(budget, cost_field)) {
                flags |= DOM_RISK_RESOLVE_PARTIAL;
                if (out_result->refusal_reason == DOM_RISK_REFUSE_NONE) {
                    out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
                }
                break;
            }
            if (field->exposure_rate <= 0) {
                continue;
            }
            falloff = dom_risk_falloff(field, &exposure->location);
            if (falloff <= 0) {
                continue;
            }
            contribution = d_q16_16_mul(field->exposure_rate, falloff);
            if (exposure->exposure_rate > 0) {
                contribution = d_q16_16_mul(contribution, exposure->exposure_rate);
            }
            if (exposure->sensitivity > 0) {
                contribution = d_q16_16_mul(contribution, exposure->sensitivity);
            }
            if (contribution > 0) {
                q48_16 delta = dom_risk_q48_from_q16(contribution);
                if (tick_delta > 1u) {
                    delta = d_q48_16_mul(delta, d_q48_16_from_int((i64)tick_delta));
                }
                exposure_delta_total = d_q48_16_add(exposure_delta_total, delta);
            }
        }
        if (exposure_delta_total != 0) {
            exposure->exposure_accumulated = d_q48_16_add(exposure->exposure_accumulated,
                                                          exposure_delta_total);
        }
        if (exposure->exposure_limit > 0 &&
            exposure->exposure_accumulated >= exposure->exposure_limit) {
            exposure->flags |= DOM_RISK_EXPOSURE_OVER_LIMIT;
            flags |= DOM_RISK_RESOLVE_OVER_LIMIT;
            over_limit_count += 1u;
        }
        exposure_total = d_q48_16_add(exposure_total, exposure->exposure_accumulated);
        exposures_seen += 1u;
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        dom_risk_profile* profile = &domain->profiles[i];
        q48_16 profile_exposure_total = 0;
        q48_16 profile_impact_mean = 0;
        q16_16 profile_spread_sum = 0;
        q16_16 profile_uncertainty_sum = 0;
        u32 matched = 0u;
        u32 profile_region = profile->region_id;
        if (region_id != 0u && profile_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_risk_region_collapsed(domain, profile_region)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_profile)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_RISK_REFUSE_NONE) {
                out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
            }
            break;
        }
        for (u32 e = 0u; e < domain->exposure_count; ++e) {
            const dom_risk_exposure* exposure = &domain->exposures[e];
            int type_index;
            q16_16 ratio = DOM_RISK_RATIO_ONE_Q16;
            if (profile->subject_ref_id != 0u &&
                exposure->subject_ref_id != profile->subject_ref_id) {
                continue;
            }
            if (profile_region != 0u && exposure->region_id != profile_region) {
                continue;
            }
            profile_exposure_total = d_q48_16_add(profile_exposure_total,
                                                  exposure->exposure_accumulated);
            if (exposure->exposure_limit > 0) {
                q48_16 div = d_q48_16_div(exposure->exposure_accumulated,
                                          exposure->exposure_limit);
                ratio = dom_risk_clamp_ratio(d_q16_16_from_q48_16(div));
            }
            type_index = dom_risk_find_type_index(domain, exposure->risk_type_id);
            if (type_index >= 0) {
                profile_impact_mean = d_q48_16_add(
                    profile_impact_mean,
                    dom_risk_apply_ratio_q48(domain->types[type_index].default_impact_mean,
                                             ratio));
                profile_spread_sum = d_q16_16_add(profile_spread_sum,
                                                  domain->types[type_index].default_impact_spread);
            }
            profile_uncertainty_sum = d_q16_16_add(profile_uncertainty_sum, exposure->uncertainty);
            matched += 1u;
        }
        profile->exposure_total = profile_exposure_total;
        profile->impact_mean = profile_impact_mean;
        if (matched > 0u) {
            profile->impact_spread = (q16_16)(profile_spread_sum / (i32)matched);
            profile->uncertainty = (q16_16)(profile_uncertainty_sum / (i32)matched);
        }
        profile->flags = 0u;
        impact_mean_total = d_q48_16_add(impact_mean_total, profile_impact_mean);
        profiles_seen += 1u;
    }

    for (u32 i = 0u; i < domain->claim_count; ++i) {
        dom_insurance_claim* claim = &domain->claims[i];
        q48_16 payout = 0;
        int policy_index;
        int event_index;
        if (!dom_domain_budget_consume(budget, cost_claim)) {
            flags |= DOM_RISK_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_RISK_REFUSE_NONE) {
                out_result->refusal_reason = DOM_RISK_REFUSE_BUDGET;
            }
            break;
        }
        claim_count += 1u;
        claim->flags = 0u;
        policy_index = dom_risk_find_policy_index(domain, claim->policy_id);
        event_index = dom_risk_find_event_index(domain, claim->event_id);
        if (policy_index < 0 || event_index < 0) {
            claim->flags |= DOM_RISK_CLAIM_DENIED;
            claim_denied += 1u;
            flags |= DOM_RISK_RESOLVE_CLAIM_DENIED;
            continue;
        }
        {
            dom_insurance_policy* policy = &domain->policies[policy_index];
            dom_liability_event* event = &domain->events[event_index];
            d_bool active = D_TRUE;
            if (policy->start_tick != 0u && tick < policy->start_tick) {
                active = D_FALSE;
            }
            if (policy->end_tick != 0u && tick > policy->end_tick) {
                active = D_FALSE;
            }
            if (!active) {
                policy->flags |= DOM_RISK_POLICY_INACTIVE;
                claim->flags |= DOM_RISK_CLAIM_DENIED;
                claim_denied += 1u;
                flags |= DOM_RISK_RESOLVE_CLAIM_DENIED;
                continue;
            }
            if (policy->risk_type_id != 0u && policy->risk_type_id != event->risk_type_id) {
                claim->flags |= DOM_RISK_CLAIM_DENIED;
                claim_denied += 1u;
                flags |= DOM_RISK_RESOLVE_CLAIM_DENIED;
                continue;
            }
            if (policy->region_id != 0u && policy->region_id != event->region_id) {
                claim->flags |= DOM_RISK_CLAIM_DENIED;
                claim_denied += 1u;
                flags |= DOM_RISK_RESOLVE_CLAIM_DENIED;
                continue;
            }
            if (event->loss_amount > policy->deductible) {
                payout = d_q48_16_sub(event->loss_amount, policy->deductible);
            }
            payout = dom_risk_apply_ratio_q48(payout, policy->coverage_ratio);
            if (policy->audit_score < DOM_RISK_AUDIT_MIN_Q16) {
                q16_16 audit_ratio = d_q16_16_sub(DOM_RISK_RATIO_ONE_Q16,
                                                  DOM_RISK_AUDIT_PENALTY_Q16);
                payout = dom_risk_apply_ratio_q48(payout, audit_ratio);
            }
            if (claim->claim_amount > 0 && payout > claim->claim_amount) {
                payout = claim->claim_amount;
            }
            if (policy->payout_limit > 0 && payout > policy->payout_limit) {
                payout = policy->payout_limit;
            }
        }
        claim->approved_amount = payout;
        claim->resolved_tick = tick;
        if (payout > 0) {
            claim->flags |= DOM_RISK_CLAIM_APPROVED;
            claim_approved += 1u;
            flags |= DOM_RISK_RESOLVE_CLAIM_APPROVED;
            claim_paid_total = d_q48_16_add(claim_paid_total, payout);
        } else {
            claim->flags |= DOM_RISK_CLAIM_DENIED;
            claim_denied += 1u;
            flags |= DOM_RISK_RESOLVE_CLAIM_DENIED;
        }
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->field_count = fields_seen;
    out_result->exposure_count = exposures_seen;
    out_result->exposure_over_limit_count = over_limit_count;
    out_result->profile_count = profiles_seen;
    out_result->claim_count = claim_count;
    out_result->claim_approved_count = claim_approved;
    out_result->claim_denied_count = claim_denied;
    out_result->exposure_total = exposure_total;
    out_result->impact_mean_total = impact_mean_total;
    out_result->claim_paid_total = claim_paid_total;
    return 0;
}

int dom_risk_domain_collapse_region(dom_risk_domain* domain, u32 region_id)
{
    dom_risk_macro_capsule capsule;
    u32 hist_bins[DOM_RISK_HIST_BINS];
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_risk_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_RISK_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;
    for (u32 i = 0u; i < domain->field_count; ++i) {
        int type_index;
        u32 risk_class;
        if (domain->fields[i].region_id != region_id) {
            continue;
        }
        capsule.field_count += 1u;
        type_index = dom_risk_find_type_index(domain, domain->fields[i].risk_type_id);
        if (type_index >= 0) {
            risk_class = domain->types[type_index].risk_class;
            if (risk_class > 0u && risk_class <= DOM_RISK_CLASS_COUNT) {
                capsule.risk_type_counts[risk_class - 1u] += 1u;
            }
        }
    }
    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        q16_16 ratio = 0;
        if (domain->exposures[i].region_id != region_id) {
            continue;
        }
        capsule.exposure_count += 1u;
        capsule.exposure_total = d_q48_16_add(capsule.exposure_total,
                                              domain->exposures[i].exposure_accumulated);
        if (domain->exposures[i].exposure_limit > 0) {
            q48_16 div = d_q48_16_div(domain->exposures[i].exposure_accumulated,
                                      domain->exposures[i].exposure_limit);
            ratio = dom_risk_clamp_ratio(d_q16_16_from_q48_16(div));
        }
        hist_bins[dom_risk_hist_bin(ratio)] += 1u;
    }
    for (u32 i = 0u; i < domain->profile_count; ++i) {
        if (domain->profiles[i].region_id != region_id) {
            continue;
        }
        capsule.profile_count += 1u;
    }
    for (u32 b = 0u; b < DOM_RISK_HIST_BINS; ++b) {
        capsule.exposure_hist[b] = dom_risk_hist_bin_ratio(hist_bins[b], capsule.exposure_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_risk_domain_expand_region(dom_risk_domain* domain, u32 region_id)
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

u32 dom_risk_domain_capsule_count(const dom_risk_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_risk_macro_capsule* dom_risk_domain_capsule_at(const dom_risk_domain* domain,
                                                         u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_risk_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
