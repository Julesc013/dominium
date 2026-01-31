/*
FILE: source/domino/world/trust_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/trust_fields
RESPONSIBILITY: Implements deterministic trust, reputation, and legitimacy resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/trust_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_TRUST_RESOLVE_COST_BASE 1u
#define DOM_TRUST_INCIDENT_ACCEL_Q16 ((q16_16)0x00008000)
#define DOM_TRUST_HALF_Q16 ((q16_16)0x00008000)

static q16_16 dom_trust_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_TRUST_RATIO_ONE_Q16) {
        return DOM_TRUST_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_trust_add_clamped(q16_16 a, q16_16 b)
{
    q16_16 sum = d_q16_16_add(a, b);
    return dom_trust_clamp_ratio(sum);
}

static q16_16 dom_trust_sub_clamped(q16_16 a, q16_16 b)
{
    q16_16 diff = d_q16_16_sub(a, b);
    return dom_trust_clamp_ratio(diff);
}

static q16_16 dom_trust_ratio_from_counts(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static void dom_trust_field_init(dom_trust_field* field)
{
    if (!field) {
        return;
    }
    memset(field, 0, sizeof(*field));
}

static void dom_trust_event_init(dom_trust_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->process_type = DOM_TRUST_PROCESS_UNSET;
}

static void dom_reputation_profile_init(dom_reputation_profile* profile)
{
    if (!profile) {
        return;
    }
    memset(profile, 0, sizeof(*profile));
}

static void dom_legitimacy_field_init(dom_legitimacy_field* field)
{
    if (!field) {
        return;
    }
    memset(field, 0, sizeof(*field));
}

static int dom_trust_find_field_index(const dom_trust_domain* domain, u32 trust_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->field_count; ++i) {
        if (domain->fields[i].trust_id == trust_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_trust_find_event_index(const dom_trust_domain* domain, u32 event_id)
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

static int dom_trust_find_profile_index(const dom_trust_domain* domain, u32 profile_id)
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

static int dom_trust_find_legitimacy_index(const dom_trust_domain* domain, u32 legitimacy_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->legitimacy_count; ++i) {
        if (domain->legitimacy[i].legitimacy_id == legitimacy_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_trust_find_field_for_subject(const dom_trust_domain* domain,
                                            u32 subject_ref_id,
                                            u32 context_id)
{
    if (!domain || subject_ref_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->field_count; ++i) {
        const dom_trust_field* field = &domain->fields[i];
        if (field->subject_ref_id != subject_ref_id) {
            continue;
        }
        if (context_id != 0u && field->context_id != context_id) {
            continue;
        }
        return (int)i;
    }
    return -1;
}

static d_bool dom_trust_domain_is_active(const dom_trust_domain* domain)
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

static d_bool dom_trust_region_collapsed(const dom_trust_domain* domain, u32 region_id)
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

static const dom_trust_macro_capsule* dom_trust_find_capsule(const dom_trust_domain* domain,
                                                             u32 region_id)
{
    if (!domain) {
        return (const dom_trust_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_trust_macro_capsule*)0;
}

static void dom_trust_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_trust_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_trust_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_TRUST_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_trust_apply_decay(dom_trust_field* field, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    if (!field || tick_delta == 0u) {
        return D_FALSE;
    }
    if (field->decay_rate <= 0 || field->trust_level <= 0) {
        return D_FALSE;
    }
    decay_per_tick = d_q16_16_mul(field->trust_level, field->decay_rate);
    if (decay_per_tick <= 0) {
        return D_FALSE;
    }
    decay_total = d_q48_16_from_q16_16(decay_per_tick);
    if (tick_delta > 1u) {
        decay_total = d_q48_16_mul(decay_total, d_q48_16_from_int((i64)tick_delta));
    }
    decay_q16 = d_q16_16_from_q48_16(decay_total);
    if (decay_q16 <= 0) {
        return D_FALSE;
    }
    field->trust_level = dom_trust_sub_clamped(field->trust_level, decay_q16);
    return D_TRUE;
}

static d_bool dom_trust_apply_event(dom_trust_domain* domain,
                                    dom_trust_event* event,
                                    u64 tick,
                                    u32* out_incident,
                                    u32* out_dispute)
{
    int field_index;
    dom_trust_field* field;
    q16_16 delta;
    if (!domain || !event) {
        return D_FALSE;
    }
    if (event->flags & DOM_TRUST_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (event->event_tick > tick) {
        return D_FALSE;
    }
    field_index = dom_trust_find_field_for_subject(domain, event->subject_ref_id, event->context_id);
    if (field_index < 0) {
        return D_FALSE;
    }
    field = &domain->fields[field_index];
    delta = dom_trust_clamp_ratio(event->delta_level);

    if ((event->flags & DOM_TRUST_EVENT_INCIDENT) &&
        event->process_type == DOM_TRUST_PROCESS_DECREASE) {
        delta = dom_trust_add_clamped(delta, d_q16_16_mul(delta, DOM_TRUST_INCIDENT_ACCEL_Q16));
        if (out_incident) {
            *out_incident += 1u;
        }
    }
    if ((event->flags & DOM_TRUST_EVENT_DISPUTE) && out_dispute) {
        *out_dispute += 1u;
    }

    switch (event->process_type) {
        case DOM_TRUST_PROCESS_INCREASE:
            field->trust_level = dom_trust_add_clamped(field->trust_level, delta);
            break;
        case DOM_TRUST_PROCESS_DECREASE:
            field->trust_level = dom_trust_sub_clamped(field->trust_level, delta);
            break;
        case DOM_TRUST_PROCESS_DECAY:
            field->trust_level = dom_trust_sub_clamped(field->trust_level,
                                                       d_q16_16_mul(field->trust_level, delta));
            break;
        case DOM_TRUST_PROCESS_TRANSFER: {
            int source_index = dom_trust_find_field_for_subject(domain,
                                                                event->source_ref_id,
                                                                event->context_id);
            if (source_index >= 0) {
                const dom_trust_field* source = &domain->fields[source_index];
                q16_16 transfer = d_q16_16_mul(source->trust_level, delta);
                field->trust_level = dom_trust_add_clamped(field->trust_level, transfer);
            }
            break;
        }
        default:
            return D_FALSE;
    }

    if (event->uncertainty > 0) {
        field->uncertainty = dom_trust_add_clamped(field->uncertainty, event->uncertainty);
    }
    event->flags |= DOM_TRUST_EVENT_APPLIED;
    return D_TRUE;
}

static q16_16 dom_trust_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_trust_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_trust_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_TRUST_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_TRUST_HIST_BINS) {
        scaled = DOM_TRUST_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_trust_surface_desc_init(dom_trust_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->field_count = 0u;
    desc->event_count = 0u;
    desc->profile_count = 0u;
    desc->legitimacy_count = 0u;
    for (u32 i = 0u; i < DOM_TRUST_MAX_FIELDS; ++i) {
        desc->fields[i].trust_id = 0u;
    }
    for (u32 i = 0u; i < DOM_TRUST_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
    }
    for (u32 i = 0u; i < DOM_TRUST_MAX_PROFILES; ++i) {
        desc->profiles[i].profile_id = 0u;
    }
    for (u32 i = 0u; i < DOM_TRUST_MAX_LEGITIMACY; ++i) {
        desc->legitimacy[i].legitimacy_id = 0u;
    }
}

void dom_trust_domain_init(dom_trust_domain* domain,
                           const dom_trust_surface_desc* desc)
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

    domain->field_count = (desc->field_count > DOM_TRUST_MAX_FIELDS)
                            ? DOM_TRUST_MAX_FIELDS
                            : desc->field_count;
    domain->event_count = (desc->event_count > DOM_TRUST_MAX_EVENTS)
                            ? DOM_TRUST_MAX_EVENTS
                            : desc->event_count;
    domain->profile_count = (desc->profile_count > DOM_TRUST_MAX_PROFILES)
                              ? DOM_TRUST_MAX_PROFILES
                              : desc->profile_count;
    domain->legitimacy_count = (desc->legitimacy_count > DOM_TRUST_MAX_LEGITIMACY)
                                 ? DOM_TRUST_MAX_LEGITIMACY
                                 : desc->legitimacy_count;

    for (u32 i = 0u; i < domain->field_count; ++i) {
        dom_trust_field_init(&domain->fields[i]);
        domain->fields[i].trust_id = desc->fields[i].trust_id;
        domain->fields[i].subject_ref_id = desc->fields[i].subject_ref_id;
        domain->fields[i].context_id = desc->fields[i].context_id;
        domain->fields[i].trust_level = desc->fields[i].trust_level;
        domain->fields[i].uncertainty = desc->fields[i].uncertainty;
        domain->fields[i].decay_rate = desc->fields[i].decay_rate;
        domain->fields[i].provenance_id = desc->fields[i].provenance_id;
        domain->fields[i].region_id = desc->fields[i].region_id;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_trust_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].process_type = desc->events[i].process_type;
        domain->events[i].subject_ref_id = desc->events[i].subject_ref_id;
        domain->events[i].source_ref_id = desc->events[i].source_ref_id;
        domain->events[i].context_id = desc->events[i].context_id;
        domain->events[i].delta_level = desc->events[i].delta_level;
        domain->events[i].uncertainty = desc->events[i].uncertainty;
        domain->events[i].event_tick = desc->events[i].event_tick;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        dom_reputation_profile_init(&domain->profiles[i]);
        domain->profiles[i].profile_id = desc->profiles[i].profile_id;
        domain->profiles[i].subject_ref_id = desc->profiles[i].subject_ref_id;
        domain->profiles[i].region_id = desc->profiles[i].region_id;
        domain->profiles[i].historical_performance = desc->profiles[i].historical_performance;
        domain->profiles[i].audit_results = desc->profiles[i].audit_results;
        domain->profiles[i].incident_history = desc->profiles[i].incident_history;
        domain->profiles[i].endorsements = desc->profiles[i].endorsements;
        domain->profiles[i].disputes = desc->profiles[i].disputes;
        domain->profiles[i].uncertainty = desc->profiles[i].uncertainty;
    }

    for (u32 i = 0u; i < domain->legitimacy_count; ++i) {
        dom_legitimacy_field_init(&domain->legitimacy[i]);
        domain->legitimacy[i].legitimacy_id = desc->legitimacy[i].legitimacy_id;
        domain->legitimacy[i].institution_ref_id = desc->legitimacy[i].institution_ref_id;
        domain->legitimacy[i].authority_scope_id = desc->legitimacy[i].authority_scope_id;
        domain->legitimacy[i].region_id = desc->legitimacy[i].region_id;
        domain->legitimacy[i].compliance_rate = desc->legitimacy[i].compliance_rate;
        domain->legitimacy[i].challenge_rate = desc->legitimacy[i].challenge_rate;
        domain->legitimacy[i].symbolic_support = desc->legitimacy[i].symbolic_support;
        domain->legitimacy[i].uncertainty = desc->legitimacy[i].uncertainty;
        domain->legitimacy[i].provenance_id = desc->legitimacy[i].provenance_id;
    }

    domain->capsule_count = 0u;
}

void dom_trust_domain_free(dom_trust_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->field_count = 0u;
    domain->event_count = 0u;
    domain->profile_count = 0u;
    domain->legitimacy_count = 0u;
    domain->capsule_count = 0u;
}

void dom_trust_domain_set_state(dom_trust_domain* domain,
                                u32 existence_state,
                                u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_trust_domain_set_policy(dom_trust_domain* domain,
                                 const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_trust_field_query(const dom_trust_domain* domain,
                          u32 trust_id,
                          dom_domain_budget* budget,
                          dom_trust_field_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_TRUST_FIELD_UNRESOLVED;

    if (!dom_trust_domain_is_active(domain)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_trust_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_trust_find_field_index(domain, trust_id);
    if (index < 0) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_trust_region_collapsed(domain, domain->fields[index].region_id)) {
        out_sample->trust_id = domain->fields[index].trust_id;
        out_sample->subject_ref_id = domain->fields[index].subject_ref_id;
        out_sample->context_id = domain->fields[index].context_id;
        out_sample->region_id = domain->fields[index].region_id;
        out_sample->flags = DOM_TRUST_FIELD_COLLAPSED;
        dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->trust_id = domain->fields[index].trust_id;
    out_sample->subject_ref_id = domain->fields[index].subject_ref_id;
    out_sample->context_id = domain->fields[index].context_id;
    out_sample->trust_level = domain->fields[index].trust_level;
    out_sample->uncertainty = domain->fields[index].uncertainty;
    out_sample->decay_rate = domain->fields[index].decay_rate;
    out_sample->provenance_id = domain->fields[index].provenance_id;
    out_sample->region_id = domain->fields[index].region_id;
    out_sample->flags = domain->fields[index].flags;
    dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_trust_event_query(const dom_trust_domain* domain,
                          u32 event_id,
                          dom_domain_budget* budget,
                          dom_trust_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_TRUST_EVENT_UNRESOLVED;

    if (!dom_trust_domain_is_active(domain)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_trust_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_trust_find_event_index(domain, event_id);
    if (index < 0) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_trust_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_TRUST_EVENT_COLLAPSED;
        dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->process_type = domain->events[index].process_type;
    out_sample->subject_ref_id = domain->events[index].subject_ref_id;
    out_sample->source_ref_id = domain->events[index].source_ref_id;
    out_sample->context_id = domain->events[index].context_id;
    out_sample->delta_level = domain->events[index].delta_level;
    out_sample->uncertainty = domain->events[index].uncertainty;
    out_sample->event_tick = domain->events[index].event_tick;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->flags = domain->events[index].flags;
    dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_reputation_profile_query(const dom_trust_domain* domain,
                                 u32 profile_id,
                                 dom_domain_budget* budget,
                                 dom_reputation_profile_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_REPUTATION_PROFILE_UNRESOLVED;

    if (!dom_trust_domain_is_active(domain)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_trust_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_trust_find_profile_index(domain, profile_id);
    if (index < 0) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_trust_region_collapsed(domain, domain->profiles[index].region_id)) {
        out_sample->profile_id = domain->profiles[index].profile_id;
        out_sample->subject_ref_id = domain->profiles[index].subject_ref_id;
        out_sample->region_id = domain->profiles[index].region_id;
        out_sample->flags = DOM_REPUTATION_PROFILE_COLLAPSED;
        dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->profile_id = domain->profiles[index].profile_id;
    out_sample->subject_ref_id = domain->profiles[index].subject_ref_id;
    out_sample->region_id = domain->profiles[index].region_id;
    out_sample->historical_performance = domain->profiles[index].historical_performance;
    out_sample->audit_results = domain->profiles[index].audit_results;
    out_sample->incident_history = domain->profiles[index].incident_history;
    out_sample->endorsements = domain->profiles[index].endorsements;
    out_sample->disputes = domain->profiles[index].disputes;
    out_sample->uncertainty = domain->profiles[index].uncertainty;
    out_sample->flags = domain->profiles[index].flags;
    dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_legitimacy_field_query(const dom_trust_domain* domain,
                               u32 legitimacy_id,
                               dom_domain_budget* budget,
                               dom_legitimacy_field_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_LEGITIMACY_FIELD_UNRESOLVED;

    if (!dom_trust_domain_is_active(domain)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_trust_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_trust_find_legitimacy_index(domain, legitimacy_id);
    if (index < 0) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_trust_region_collapsed(domain, domain->legitimacy[index].region_id)) {
        out_sample->legitimacy_id = domain->legitimacy[index].legitimacy_id;
        out_sample->institution_ref_id = domain->legitimacy[index].institution_ref_id;
        out_sample->region_id = domain->legitimacy[index].region_id;
        out_sample->flags = DOM_LEGITIMACY_FIELD_COLLAPSED;
        dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->legitimacy_id = domain->legitimacy[index].legitimacy_id;
    out_sample->institution_ref_id = domain->legitimacy[index].institution_ref_id;
    out_sample->authority_scope_id = domain->legitimacy[index].authority_scope_id;
    out_sample->region_id = domain->legitimacy[index].region_id;
    out_sample->compliance_rate = domain->legitimacy[index].compliance_rate;
    out_sample->challenge_rate = domain->legitimacy[index].challenge_rate;
    out_sample->symbolic_support = domain->legitimacy[index].symbolic_support;
    out_sample->uncertainty = domain->legitimacy[index].uncertainty;
    out_sample->provenance_id = domain->legitimacy[index].provenance_id;
    out_sample->flags = domain->legitimacy[index].flags;
    dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_trust_region_query(const dom_trust_domain* domain,
                           u32 region_id,
                           dom_domain_budget* budget,
                           dom_trust_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_event;
    u32 cost_profile;
    u32 cost_legitimacy;
    q48_16 trust_total = 0;
    q16_16 dispute_sum = 0;
    q16_16 compliance_sum = 0;
    u32 fields_seen = 0u;
    u32 events_seen = 0u;
    u32 profiles_seen = 0u;
    u32 legitimacy_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_trust_domain_is_active(domain)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_trust_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_trust_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_trust_region_collapsed(domain, region_id)) {
        const dom_trust_macro_capsule* capsule = dom_trust_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->field_count = capsule->field_count;
            out_sample->event_count = capsule->event_count;
            out_sample->profile_count = capsule->profile_count;
            out_sample->legitimacy_count = capsule->legitimacy_count;
            out_sample->trust_avg = capsule->trust_avg;
            out_sample->dispute_rate_avg = capsule->dispute_rate_avg;
            out_sample->compliance_rate_avg = capsule->compliance_rate_avg;
        }
        out_sample->flags = DOM_TRUST_RESOLVE_PARTIAL;
        dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_field = dom_trust_budget_cost(domain->policy.cost_medium);
    cost_event = dom_trust_budget_cost(domain->policy.cost_coarse);
    cost_profile = dom_trust_budget_cost(domain->policy.cost_coarse);
    cost_legitimacy = dom_trust_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, field_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            break;
        }
        trust_total = d_q48_16_add(trust_total, d_q48_16_from_q16_16(domain->fields[i].trust_level));
        fields_seen += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        u32 event_region = domain->events[i].region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, event_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            break;
        }
        events_seen += 1u;
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        u32 profile_region = domain->profiles[i].region_id;
        if (region_id != 0u && profile_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, profile_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_profile)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            break;
        }
        dispute_sum = d_q16_16_add(dispute_sum, domain->profiles[i].disputes);
        profiles_seen += 1u;
    }

    for (u32 i = 0u; i < domain->legitimacy_count; ++i) {
        u32 legit_region = domain->legitimacy[i].region_id;
        if (region_id != 0u && legit_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, legit_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_legitimacy)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            break;
        }
        compliance_sum = d_q16_16_add(compliance_sum, domain->legitimacy[i].compliance_rate);
        legitimacy_seen += 1u;
    }

    out_sample->region_id = region_id;
    out_sample->field_count = fields_seen;
    out_sample->event_count = events_seen;
    out_sample->profile_count = profiles_seen;
    out_sample->legitimacy_count = legitimacy_seen;
    if (fields_seen > 0u) {
        q48_16 div = d_q48_16_div(trust_total, d_q48_16_from_int((i64)fields_seen));
        out_sample->trust_avg = dom_trust_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (profiles_seen > 0u) {
        out_sample->dispute_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(dispute_sum / (i32)profiles_seen));
    }
    if (legitimacy_seen > 0u) {
        out_sample->compliance_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(compliance_sum / (i32)legitimacy_seen));
    }
    out_sample->flags = flags;
    dom_trust_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                            cost_base, budget);
    return 0;
}

int dom_trust_resolve(dom_trust_domain* domain,
                      u32 region_id,
                      u64 tick,
                      u64 tick_delta,
                      dom_domain_budget* budget,
                      dom_trust_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_event;
    u32 cost_profile;
    u32 cost_legitimacy;
    q48_16 trust_total = 0;
    q16_16 dispute_sum = 0;
    q16_16 compliance_sum = 0;
    u32 fields_seen = 0u;
    u32 events_seen = 0u;
    u32 events_applied = 0u;
    u32 profiles_seen = 0u;
    u32 legitimacy_seen = 0u;
    u32 incident_count = 0u;
    u32 dispute_count = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_trust_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_TRUST_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_trust_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_TRUST_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_trust_region_collapsed(domain, region_id)) {
        const dom_trust_macro_capsule* capsule = dom_trust_find_capsule(domain, region_id);
        if (capsule) {
            out_result->field_count = capsule->field_count;
            out_result->event_count = capsule->event_count;
            out_result->profile_count = capsule->profile_count;
            out_result->legitimacy_count = capsule->legitimacy_count;
            out_result->trust_avg = capsule->trust_avg;
            out_result->dispute_rate_avg = capsule->dispute_rate_avg;
            out_result->compliance_rate_avg = capsule->compliance_rate_avg;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_TRUST_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_field = dom_trust_budget_cost(domain->policy.cost_medium);
    cost_event = dom_trust_budget_cost(domain->policy.cost_coarse);
    cost_profile = dom_trust_budget_cost(domain->policy.cost_coarse);
    cost_legitimacy = dom_trust_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, field_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_TRUST_REFUSE_NONE) {
                out_result->refusal_reason = DOM_TRUST_REFUSE_BUDGET;
            }
            break;
        }
        if (dom_trust_apply_decay(&domain->fields[i], tick_delta)) {
            domain->fields[i].flags |= DOM_TRUST_FIELD_DECAYING;
            flags |= DOM_TRUST_RESOLVE_DECAYED;
        }
        trust_total = d_q48_16_add(trust_total, d_q48_16_from_q16_16(domain->fields[i].trust_level));
        fields_seen += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_trust_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, event_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_TRUST_REFUSE_NONE) {
                out_result->refusal_reason = DOM_TRUST_REFUSE_BUDGET;
            }
            break;
        }
        events_seen += 1u;
        if (dom_trust_apply_event(domain, event, tick, &incident_count, &dispute_count)) {
            events_applied += 1u;
        }
    }

    for (u32 i = 0u; i < domain->profile_count; ++i) {
        dom_reputation_profile* profile = &domain->profiles[i];
        q16_16 trust_sum = 0;
        q16_16 uncertainty_sum = 0;
        q16_16 audit_sum = 0;
        q16_16 incident_sum = 0;
        q16_16 endorsement_sum = 0;
        q16_16 dispute_sum_local = 0;
        u32 trust_seen = 0u;
        u32 audit_seen = 0u;
        u32 incident_seen = 0u;
        u32 endorsement_seen = 0u;
        u32 dispute_seen = 0u;
        u32 profile_region = profile->region_id;
        if (region_id != 0u && profile_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, profile_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_profile)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_TRUST_REFUSE_NONE) {
                out_result->refusal_reason = DOM_TRUST_REFUSE_BUDGET;
            }
            break;
        }
        for (u32 f = 0u; f < domain->field_count; ++f) {
            const dom_trust_field* field = &domain->fields[f];
            if (profile->subject_ref_id != 0u &&
                field->subject_ref_id != profile->subject_ref_id) {
                continue;
            }
            if (profile_region != 0u && field->region_id != profile_region) {
                continue;
            }
            trust_sum = d_q16_16_add(trust_sum, field->trust_level);
            uncertainty_sum = d_q16_16_add(uncertainty_sum, field->uncertainty);
            trust_seen += 1u;
        }
        for (u32 e = 0u; e < domain->event_count; ++e) {
            const dom_trust_event* event = &domain->events[e];
            if (!(event->flags & DOM_TRUST_EVENT_APPLIED)) {
                continue;
            }
            if (profile->subject_ref_id != 0u &&
                event->subject_ref_id != profile->subject_ref_id) {
                continue;
            }
            if (profile_region != 0u && event->region_id != profile_region) {
                continue;
            }
            if (event->process_type == DOM_TRUST_PROCESS_INCREASE ||
                event->process_type == DOM_TRUST_PROCESS_TRANSFER) {
                endorsement_sum = d_q16_16_add(endorsement_sum, event->delta_level);
                endorsement_seen += 1u;
                audit_sum = d_q16_16_add(audit_sum, event->delta_level);
                audit_seen += 1u;
            }
            if (event->process_type == DOM_TRUST_PROCESS_DECREASE &&
                (event->flags & DOM_TRUST_EVENT_INCIDENT)) {
                incident_sum = d_q16_16_add(incident_sum, event->delta_level);
                incident_seen += 1u;
            }
            if (event->flags & DOM_TRUST_EVENT_DISPUTE) {
                dispute_sum_local = d_q16_16_add(dispute_sum_local, event->delta_level);
                dispute_seen += 1u;
            }
        }
        profile->flags = 0u;
        if (trust_seen > 0u) {
            profile->historical_performance = dom_trust_clamp_ratio(
                (q16_16)(trust_sum / (i32)trust_seen));
            profile->uncertainty = dom_trust_clamp_ratio(
                (q16_16)(uncertainty_sum / (i32)trust_seen));
        }
        if (audit_seen > 0u) {
            profile->audit_results = dom_trust_clamp_ratio(
                (q16_16)(audit_sum / (i32)audit_seen));
        }
        if (incident_seen > 0u) {
            profile->incident_history = dom_trust_clamp_ratio(
                (q16_16)(incident_sum / (i32)incident_seen));
        }
        if (endorsement_seen > 0u) {
            profile->endorsements = dom_trust_clamp_ratio(
                (q16_16)(endorsement_sum / (i32)endorsement_seen));
        }
        if (dispute_seen > 0u) {
            profile->disputes = dom_trust_clamp_ratio(
                (q16_16)(dispute_sum_local / (i32)dispute_seen));
        }
        dispute_sum = d_q16_16_add(dispute_sum, profile->disputes);
        profiles_seen += 1u;
    }

    for (u32 i = 0u; i < domain->legitimacy_count; ++i) {
        u32 legit_region = domain->legitimacy[i].region_id;
        if (region_id != 0u && legit_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_trust_region_collapsed(domain, legit_region)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_legitimacy)) {
            flags |= DOM_TRUST_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_TRUST_REFUSE_NONE) {
                out_result->refusal_reason = DOM_TRUST_REFUSE_BUDGET;
            }
            break;
        }
        compliance_sum = d_q16_16_add(compliance_sum, domain->legitimacy[i].compliance_rate);
        legitimacy_seen += 1u;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->field_count = fields_seen;
    out_result->event_count = events_seen;
    out_result->event_applied_count = events_applied;
    out_result->profile_count = profiles_seen;
    out_result->legitimacy_count = legitimacy_seen;
    if (fields_seen > 0u) {
        q48_16 div = d_q48_16_div(trust_total, d_q48_16_from_int((i64)fields_seen));
        out_result->trust_avg = dom_trust_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (profiles_seen > 0u) {
        out_result->dispute_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(dispute_sum / (i32)profiles_seen));
    }
    if (legitimacy_seen > 0u) {
        out_result->compliance_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(compliance_sum / (i32)legitimacy_seen));
    }
    if (incident_count > 0u) {
        flags |= DOM_TRUST_RESOLVE_INCIDENT;
    }
    if (dispute_count > 0u) {
        flags |= DOM_TRUST_RESOLVE_DISPUTE;
    }
    out_result->flags = flags;
    return 0;
}

int dom_trust_domain_collapse_region(dom_trust_domain* domain, u32 region_id)
{
    dom_trust_macro_capsule capsule;
    u32 hist_bins[DOM_TRUST_HIST_BINS];
    q48_16 trust_total = 0;
    q16_16 dispute_sum = 0;
    q16_16 compliance_sum = 0;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_trust_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_TRUST_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;
    for (u32 i = 0u; i < domain->field_count; ++i) {
        if (domain->fields[i].region_id != region_id) {
            continue;
        }
        capsule.field_count += 1u;
        trust_total = d_q48_16_add(trust_total, d_q48_16_from_q16_16(domain->fields[i].trust_level));
        hist_bins[dom_trust_hist_bin(domain->fields[i].trust_level)] += 1u;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].region_id != region_id) {
            continue;
        }
        capsule.event_count += 1u;
    }
    for (u32 i = 0u; i < domain->profile_count; ++i) {
        if (domain->profiles[i].region_id != region_id) {
            continue;
        }
        capsule.profile_count += 1u;
        dispute_sum = d_q16_16_add(dispute_sum, domain->profiles[i].disputes);
    }
    for (u32 i = 0u; i < domain->legitimacy_count; ++i) {
        if (domain->legitimacy[i].region_id != region_id) {
            continue;
        }
        capsule.legitimacy_count += 1u;
        compliance_sum = d_q16_16_add(compliance_sum, domain->legitimacy[i].compliance_rate);
    }
    if (capsule.field_count > 0u) {
        q48_16 div = d_q48_16_div(trust_total, d_q48_16_from_int((i64)capsule.field_count));
        capsule.trust_avg = dom_trust_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (capsule.profile_count > 0u) {
        capsule.dispute_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(dispute_sum / (i32)capsule.profile_count));
    }
    if (capsule.legitimacy_count > 0u) {
        capsule.compliance_rate_avg = dom_trust_clamp_ratio(
            (q16_16)(compliance_sum / (i32)capsule.legitimacy_count));
    }
    for (u32 b = 0u; b < DOM_TRUST_HIST_BINS; ++b) {
        capsule.trust_hist[b] = dom_trust_hist_bin_ratio(hist_bins[b], capsule.field_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_trust_domain_expand_region(dom_trust_domain* domain, u32 region_id)
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

u32 dom_trust_domain_capsule_count(const dom_trust_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_trust_macro_capsule* dom_trust_domain_capsule_at(const dom_trust_domain* domain,
                                                           u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_trust_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
