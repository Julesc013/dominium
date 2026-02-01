/*
FILE: source/domino/world/srz_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/srz_fields
RESPONSIBILITY: Implements deterministic SRZ verification and sampling.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/srz_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_SRZ_RESOLVE_COST_BASE 1u

static q16_16 dom_srz_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_SRZ_RATIO_ONE_Q16) {
        return DOM_SRZ_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_srz_ratio_from_counts(u32 numerator, u32 denominator)
{
    if (denominator == 0u) {
        return 0;
    }
    return (q16_16)(((u64)numerator << Q16_16_FRAC_BITS) / denominator);
}

static void dom_srz_threshold_init(dom_srz_threshold_desc* threshold)
{
    if (!threshold) {
        return;
    }
    threshold->metric_id = DOM_SRZ_METRIC_UNSET;
    threshold->value = 0;
}

static void dom_srz_zone_init(dom_srz_zone* zone)
{
    if (!zone) {
        return;
    }
    memset(zone, 0, sizeof(*zone));
    zone->mode = DOM_SRZ_MODE_UNSET;
    zone->verification_policy = DOM_SRZ_VERIFY_UNSET;
    for (u32 i = 0u; i < DOM_SRZ_MAX_THRESHOLDS; ++i) {
        dom_srz_threshold_init(&zone->escalation[i]);
        dom_srz_threshold_init(&zone->deescalation[i]);
    }
}

static void dom_srz_assignment_init(dom_srz_assignment* assignment)
{
    if (!assignment) {
        return;
    }
    memset(assignment, 0, sizeof(*assignment));
}

static void dom_srz_policy_init(dom_srz_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->verification_policy = DOM_SRZ_VERIFY_UNSET;
}

static void dom_srz_log_init(dom_srz_log* log)
{
    if (!log) {
        return;
    }
    memset(log, 0, sizeof(*log));
}

static void dom_srz_hash_link_init(dom_srz_hash_link* link)
{
    if (!link) {
        return;
    }
    memset(link, 0, sizeof(*link));
}

static void dom_srz_state_delta_init(dom_srz_state_delta* delta)
{
    if (!delta) {
        return;
    }
    memset(delta, 0, sizeof(*delta));
}

static int dom_srz_find_zone_index(const dom_srz_domain* domain, u32 srz_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->zone_count; ++i) {
        if (domain->zones[i].srz_id == srz_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_srz_find_assignment_index(const dom_srz_domain* domain, u32 assignment_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->assignment_count; ++i) {
        if (domain->assignments[i].assignment_id == assignment_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_srz_find_policy_index(const dom_srz_domain* domain, u32 policy_id)
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

static int dom_srz_find_log_index(const dom_srz_domain* domain, u32 log_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->log_count; ++i) {
        if (domain->logs[i].log_id == log_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_srz_find_hash_link_index(const dom_srz_domain* domain, u32 link_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        if (domain->hash_links[i].link_id == link_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_srz_find_delta_index(const dom_srz_domain* domain, u32 delta_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->delta_count; ++i) {
        if (domain->deltas[i].delta_id == delta_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_srz_domain_is_active(const dom_srz_domain* domain)
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

static d_bool dom_srz_region_collapsed(const dom_srz_domain* domain, u32 region_id)
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

static const dom_srz_macro_capsule* dom_srz_find_capsule(const dom_srz_domain* domain, u32 region_id)
{
    if (!domain) {
        return (const dom_srz_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_srz_macro_capsule*)0;
}

static void dom_srz_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_srz_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_srz_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_SRZ_RESOLVE_COST_BASE : cost_units;
}

static q16_16 dom_srz_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_srz_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_srz_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_SRZ_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_SRZ_HIST_BINS) {
        scaled = DOM_SRZ_HIST_BINS - 1u;
    }
    return scaled;
}

static u32 dom_srz_chain_link_count(const dom_srz_domain* domain, u32 chain_id)
{
    u32 count = 0u;
    if (!domain || chain_id == 0u) {
        return 0u;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        if (domain->hash_links[i].chain_id == chain_id) {
            count += 1u;
        }
    }
    return count;
}

static const dom_srz_hash_link* dom_srz_chain_first(const dom_srz_domain* domain, u32 chain_id)
{
    const dom_srz_hash_link* first = 0;
    if (!domain || chain_id == 0u) {
        return (const dom_srz_hash_link*)0;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        const dom_srz_hash_link* link = &domain->hash_links[i];
        if (link->chain_id != chain_id) {
            continue;
        }
        if (link->prev_hash == 0u) {
            if (first) {
                return (const dom_srz_hash_link*)0;
            }
            first = link;
        }
    }
    return first;
}

static const dom_srz_hash_link* dom_srz_chain_next(const dom_srz_domain* domain,
                                                   u32 chain_id,
                                                   u64 prev_hash)
{
    if (!domain || chain_id == 0u) {
        return (const dom_srz_hash_link*)0;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        const dom_srz_hash_link* link = &domain->hash_links[i];
        if (link->chain_id != chain_id) {
            continue;
        }
        if (link->prev_hash == prev_hash) {
            return link;
        }
    }
    return (const dom_srz_hash_link*)0;
}

static d_bool dom_srz_chain_verify_strict(const dom_srz_domain* domain,
                                          const dom_srz_log* log,
                                          u32* out_seen,
                                          u32* out_process_total,
                                          u32* out_rng_total)
{
    const dom_srz_hash_link* link;
    const dom_srz_hash_link* first;
    u32 total_links;
    u32 seen = 0u;
    u32 process_total = 0u;
    u32 rng_total = 0u;
    u64 guard = 0u;
    if (!domain || !log || log->chain_id == 0u) {
        return D_FALSE;
    }
    total_links = dom_srz_chain_link_count(domain, log->chain_id);
    if (total_links == 0u) {
        return D_FALSE;
    }
    first = dom_srz_chain_first(domain, log->chain_id);
    if (!first) {
        return D_FALSE;
    }
    link = first;
    while (link) {
        seen += 1u;
        process_total += link->process_count;
        rng_total += link->rng_stream_count;
        if (link->hash == 0u) {
            return D_FALSE;
        }
        guard += 1u;
        if (guard > total_links + 1u) {
            return D_FALSE;
        }
        link = dom_srz_chain_next(domain, log->chain_id, link->hash);
    }
    if (seen != total_links) {
        return D_FALSE;
    }
    if (out_seen) {
        *out_seen = seen;
    }
    if (out_process_total) {
        *out_process_total = process_total;
    }
    if (out_rng_total) {
        *out_rng_total = rng_total;
    }
    return D_TRUE;
}

static d_bool dom_srz_chain_verify_spot(const dom_srz_domain* domain,
                                        const dom_srz_log* log,
                                        u32* out_process_total,
                                        u32* out_rng_total)
{
    const dom_srz_hash_link* first;
    const dom_srz_hash_link* last = 0;
    u32 process_total = 0u;
    u32 rng_total = 0u;
    if (!domain || !log || log->chain_id == 0u) {
        return D_FALSE;
    }
    first = dom_srz_chain_first(domain, log->chain_id);
    if (!first) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        const dom_srz_hash_link* link = &domain->hash_links[i];
        if (link->chain_id != log->chain_id) {
            continue;
        }
        process_total += link->process_count;
        rng_total += link->rng_stream_count;
        if (!last || link->segment_index > last->segment_index) {
            last = link;
        }
    }
    if (!last || last->hash == 0u) {
        return D_FALSE;
    }
    if (out_process_total) {
        *out_process_total = process_total;
    }
    if (out_rng_total) {
        *out_rng_total = rng_total;
    }
    return D_TRUE;
}

static d_bool dom_srz_delta_verify(const dom_srz_domain* domain,
                                   const dom_srz_log* log)
{
    int index;
    if (!domain || !log || log->delta_id == 0u) {
        return D_FALSE;
    }
    index = dom_srz_find_delta_index(domain, log->delta_id);
    if (index < 0) {
        return D_FALSE;
    }
    const dom_srz_state_delta* delta = &domain->deltas[index];
    if ((delta->flags & DOM_SRZ_DELTA_INVARIANTS_OK) == 0u) {
        return D_FALSE;
    }
    if (delta->process_count != log->process_count) {
        return D_FALSE;
    }
    if (delta->rng_stream_count != log->rng_stream_count) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool dom_srz_log_epistemic_ok(const dom_srz_zone* zone,
                                       const dom_srz_log* log)
{
    if (!zone || !log) {
        return D_FALSE;
    }
    if (zone->epistemic_scope_id == 0u || log->epistemic_scope_id == 0u) {
        return D_TRUE;
    }
    return (zone->epistemic_scope_id == log->epistemic_scope_id) ? D_TRUE : D_FALSE;
}

void dom_srz_surface_desc_init(dom_srz_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
}

void dom_srz_domain_init(dom_srz_domain* domain, const dom_srz_surface_desc* desc)
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

    domain->zone_count = (desc->zone_count > DOM_SRZ_MAX_ZONES) ? DOM_SRZ_MAX_ZONES : desc->zone_count;
    domain->assignment_count = (desc->assignment_count > DOM_SRZ_MAX_ASSIGNMENTS)
                                   ? DOM_SRZ_MAX_ASSIGNMENTS
                                   : desc->assignment_count;
    domain->policy_count = (desc->policy_count > DOM_SRZ_MAX_POLICIES)
                               ? DOM_SRZ_MAX_POLICIES
                               : desc->policy_count;
    domain->log_count = (desc->log_count > DOM_SRZ_MAX_LOGS) ? DOM_SRZ_MAX_LOGS : desc->log_count;
    domain->hash_link_count = (desc->hash_link_count > DOM_SRZ_MAX_HASH_LINKS)
                                  ? DOM_SRZ_MAX_HASH_LINKS
                                  : desc->hash_link_count;
    domain->delta_count = (desc->delta_count > DOM_SRZ_MAX_DELTAS) ? DOM_SRZ_MAX_DELTAS : desc->delta_count;

    for (u32 i = 0u; i < domain->zone_count; ++i) {
        dom_srz_zone_init(&domain->zones[i]);
        domain->zones[i].srz_id = desc->zones[i].srz_id;
        domain->zones[i].domain_count = desc->zones[i].domain_count;
        memcpy(domain->zones[i].domain_ids, desc->zones[i].domain_ids,
               sizeof(domain->zones[i].domain_ids));
        domain->zones[i].mode = desc->zones[i].mode;
        domain->zones[i].verification_policy = desc->zones[i].verification_policy;
        domain->zones[i].escalation_count = desc->zones[i].escalation_count;
        memcpy(domain->zones[i].escalation, desc->zones[i].escalation,
               sizeof(domain->zones[i].escalation));
        domain->zones[i].deescalation_count = desc->zones[i].deescalation_count;
        memcpy(domain->zones[i].deescalation, desc->zones[i].deescalation,
               sizeof(domain->zones[i].deescalation));
        domain->zones[i].epistemic_scope_id = desc->zones[i].epistemic_scope_id;
        domain->zones[i].policy_id = desc->zones[i].policy_id;
        domain->zones[i].provenance_id = desc->zones[i].provenance_id;
        domain->zones[i].region_id = desc->zones[i].region_id;
        domain->zones[i].flags = desc->zones[i].flags;
    }

    for (u32 i = 0u; i < domain->assignment_count; ++i) {
        dom_srz_assignment_init(&domain->assignments[i]);
        domain->assignments[i].assignment_id = desc->assignments[i].assignment_id;
        domain->assignments[i].srz_id = desc->assignments[i].srz_id;
        domain->assignments[i].executor_id = desc->assignments[i].executor_id;
        domain->assignments[i].authority_token_id = desc->assignments[i].authority_token_id;
        domain->assignments[i].capability_baseline_id = desc->assignments[i].capability_baseline_id;
        domain->assignments[i].start_tick = desc->assignments[i].start_tick;
        domain->assignments[i].expiry_tick = desc->assignments[i].expiry_tick;
        domain->assignments[i].provenance_id = desc->assignments[i].provenance_id;
        domain->assignments[i].region_id = desc->assignments[i].region_id;
        domain->assignments[i].flags = desc->assignments[i].flags;
    }

    for (u32 i = 0u; i < domain->policy_count; ++i) {
        dom_srz_policy_init(&domain->policies[i]);
        domain->policies[i].policy_id = desc->policies[i].policy_id;
        domain->policies[i].verification_policy = desc->policies[i].verification_policy;
        domain->policies[i].spot_check_rate = desc->policies[i].spot_check_rate;
        domain->policies[i].strict_replay_interval = desc->policies[i].strict_replay_interval;
        domain->policies[i].max_segment_ticks = desc->policies[i].max_segment_ticks;
        domain->policies[i].provenance_id = desc->policies[i].provenance_id;
        domain->policies[i].region_id = desc->policies[i].region_id;
        domain->policies[i].flags = desc->policies[i].flags;
    }

    for (u32 i = 0u; i < domain->log_count; ++i) {
        dom_srz_log_init(&domain->logs[i]);
        domain->logs[i].log_id = desc->logs[i].log_id;
        domain->logs[i].srz_id = desc->logs[i].srz_id;
        domain->logs[i].assignment_id = desc->logs[i].assignment_id;
        domain->logs[i].policy_id = desc->logs[i].policy_id;
        domain->logs[i].chain_id = desc->logs[i].chain_id;
        domain->logs[i].delta_id = desc->logs[i].delta_id;
        domain->logs[i].start_tick = desc->logs[i].start_tick;
        domain->logs[i].end_tick = desc->logs[i].end_tick;
        domain->logs[i].process_count = desc->logs[i].process_count;
        domain->logs[i].rng_stream_count = desc->logs[i].rng_stream_count;
        domain->logs[i].epistemic_scope_id = desc->logs[i].epistemic_scope_id;
        domain->logs[i].provenance_id = desc->logs[i].provenance_id;
        domain->logs[i].region_id = desc->logs[i].region_id;
        domain->logs[i].flags = desc->logs[i].flags;
    }

    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        dom_srz_hash_link_init(&domain->hash_links[i]);
        domain->hash_links[i].link_id = desc->hash_links[i].link_id;
        domain->hash_links[i].chain_id = desc->hash_links[i].chain_id;
        domain->hash_links[i].segment_index = desc->hash_links[i].segment_index;
        domain->hash_links[i].prev_hash = desc->hash_links[i].prev_hash;
        domain->hash_links[i].hash = desc->hash_links[i].hash;
        domain->hash_links[i].start_tick = desc->hash_links[i].start_tick;
        domain->hash_links[i].end_tick = desc->hash_links[i].end_tick;
        domain->hash_links[i].process_count = desc->hash_links[i].process_count;
        domain->hash_links[i].rng_stream_count = desc->hash_links[i].rng_stream_count;
        domain->hash_links[i].provenance_id = desc->hash_links[i].provenance_id;
        domain->hash_links[i].region_id = desc->hash_links[i].region_id;
        domain->hash_links[i].flags = desc->hash_links[i].flags;
    }

    for (u32 i = 0u; i < domain->delta_count; ++i) {
        dom_srz_state_delta_init(&domain->deltas[i]);
        domain->deltas[i].delta_id = desc->deltas[i].delta_id;
        domain->deltas[i].srz_id = desc->deltas[i].srz_id;
        domain->deltas[i].log_id = desc->deltas[i].log_id;
        domain->deltas[i].process_count = desc->deltas[i].process_count;
        domain->deltas[i].rng_stream_count = desc->deltas[i].rng_stream_count;
        domain->deltas[i].provenance_id = desc->deltas[i].provenance_id;
        domain->deltas[i].region_id = desc->deltas[i].region_id;
        domain->deltas[i].flags = desc->deltas[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_srz_domain_free(dom_srz_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->zone_count = 0u;
    domain->assignment_count = 0u;
    domain->policy_count = 0u;
    domain->log_count = 0u;
    domain->hash_link_count = 0u;
    domain->delta_count = 0u;
    domain->capsule_count = 0u;
}

void dom_srz_domain_set_state(dom_srz_domain* domain, u32 existence_state, u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_srz_domain_set_policy(dom_srz_domain* domain, const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_srz_zone_query(const dom_srz_domain* domain,
                       u32 srz_id,
                       dom_domain_budget* budget,
                       dom_srz_zone_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_ZONE_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_zone_index(domain, srz_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->zones[index].region_id)) {
        out_sample->srz_id = domain->zones[index].srz_id;
        out_sample->region_id = domain->zones[index].region_id;
        out_sample->flags = DOM_SRZ_ZONE_COLLAPSED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->srz_id = domain->zones[index].srz_id;
    out_sample->domain_count = domain->zones[index].domain_count;
    out_sample->mode = domain->zones[index].mode;
    out_sample->verification_policy = domain->zones[index].verification_policy;
    out_sample->escalation_count = domain->zones[index].escalation_count;
    out_sample->deescalation_count = domain->zones[index].deescalation_count;
    out_sample->epistemic_scope_id = domain->zones[index].epistemic_scope_id;
    out_sample->policy_id = domain->zones[index].policy_id;
    out_sample->provenance_id = domain->zones[index].provenance_id;
    out_sample->region_id = domain->zones[index].region_id;
    out_sample->flags = 0u;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_assignment_query(const dom_srz_domain* domain,
                             u32 assignment_id,
                             dom_domain_budget* budget,
                             dom_srz_assignment_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_ASSIGNMENT_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_assignment_index(domain, assignment_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->assignments[index].region_id)) {
        out_sample->assignment_id = domain->assignments[index].assignment_id;
        out_sample->region_id = domain->assignments[index].region_id;
        out_sample->flags = DOM_SRZ_ASSIGNMENT_COLLAPSED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->assignment_id = domain->assignments[index].assignment_id;
    out_sample->srz_id = domain->assignments[index].srz_id;
    out_sample->executor_id = domain->assignments[index].executor_id;
    out_sample->authority_token_id = domain->assignments[index].authority_token_id;
    out_sample->capability_baseline_id = domain->assignments[index].capability_baseline_id;
    out_sample->start_tick = domain->assignments[index].start_tick;
    out_sample->expiry_tick = domain->assignments[index].expiry_tick;
    out_sample->provenance_id = domain->assignments[index].provenance_id;
    out_sample->region_id = domain->assignments[index].region_id;
    out_sample->flags = 0u;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_policy_query(const dom_srz_domain* domain,
                         u32 policy_id,
                         dom_domain_budget* budget,
                         dom_srz_policy_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_POLICY_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_policy_index(domain, policy_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->policies[index].region_id)) {
        out_sample->policy_id = domain->policies[index].policy_id;
        out_sample->region_id = domain->policies[index].region_id;
        out_sample->flags = DOM_SRZ_POLICY_UNRESOLVED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->policy_id = domain->policies[index].policy_id;
    out_sample->verification_policy = domain->policies[index].verification_policy;
    out_sample->spot_check_rate = domain->policies[index].spot_check_rate;
    out_sample->strict_replay_interval = domain->policies[index].strict_replay_interval;
    out_sample->max_segment_ticks = domain->policies[index].max_segment_ticks;
    out_sample->provenance_id = domain->policies[index].provenance_id;
    out_sample->region_id = domain->policies[index].region_id;
    out_sample->flags = 0u;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_log_query(const dom_srz_domain* domain,
                      u32 log_id,
                      dom_domain_budget* budget,
                      dom_srz_log_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_LOG_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_log_index(domain, log_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->logs[index].region_id)) {
        out_sample->log_id = domain->logs[index].log_id;
        out_sample->region_id = domain->logs[index].region_id;
        out_sample->flags = DOM_SRZ_LOG_UNRESOLVED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->log_id = domain->logs[index].log_id;
    out_sample->srz_id = domain->logs[index].srz_id;
    out_sample->assignment_id = domain->logs[index].assignment_id;
    out_sample->policy_id = domain->logs[index].policy_id;
    out_sample->chain_id = domain->logs[index].chain_id;
    out_sample->delta_id = domain->logs[index].delta_id;
    out_sample->start_tick = domain->logs[index].start_tick;
    out_sample->end_tick = domain->logs[index].end_tick;
    out_sample->process_count = domain->logs[index].process_count;
    out_sample->rng_stream_count = domain->logs[index].rng_stream_count;
    out_sample->epistemic_scope_id = domain->logs[index].epistemic_scope_id;
    out_sample->provenance_id = domain->logs[index].provenance_id;
    out_sample->region_id = domain->logs[index].region_id;
    out_sample->flags = domain->logs[index].flags;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_hash_link_query(const dom_srz_domain* domain,
                            u32 link_id,
                            dom_domain_budget* budget,
                            dom_srz_hash_link_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_HASH_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_hash_link_index(domain, link_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->hash_links[index].region_id)) {
        out_sample->link_id = domain->hash_links[index].link_id;
        out_sample->region_id = domain->hash_links[index].region_id;
        out_sample->flags = DOM_SRZ_HASH_UNRESOLVED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->link_id = domain->hash_links[index].link_id;
    out_sample->chain_id = domain->hash_links[index].chain_id;
    out_sample->segment_index = domain->hash_links[index].segment_index;
    out_sample->prev_hash = domain->hash_links[index].prev_hash;
    out_sample->hash = domain->hash_links[index].hash;
    out_sample->start_tick = domain->hash_links[index].start_tick;
    out_sample->end_tick = domain->hash_links[index].end_tick;
    out_sample->process_count = domain->hash_links[index].process_count;
    out_sample->rng_stream_count = domain->hash_links[index].rng_stream_count;
    out_sample->provenance_id = domain->hash_links[index].provenance_id;
    out_sample->region_id = domain->hash_links[index].region_id;
    out_sample->flags = domain->hash_links[index].flags;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_state_delta_query(const dom_srz_domain* domain,
                              u32 delta_id,
                              dom_domain_budget* budget,
                              dom_srz_state_delta_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_SRZ_DELTA_UNRESOLVED;

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }
    index = dom_srz_find_delta_index(domain, delta_id);
    if (index < 0) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }
    if (dom_srz_region_collapsed(domain, domain->deltas[index].region_id)) {
        out_sample->delta_id = domain->deltas[index].delta_id;
        out_sample->region_id = domain->deltas[index].region_id;
        out_sample->flags = DOM_SRZ_DELTA_UNRESOLVED;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }
    out_sample->delta_id = domain->deltas[index].delta_id;
    out_sample->srz_id = domain->deltas[index].srz_id;
    out_sample->log_id = domain->deltas[index].log_id;
    out_sample->process_count = domain->deltas[index].process_count;
    out_sample->rng_stream_count = domain->deltas[index].rng_stream_count;
    out_sample->provenance_id = domain->deltas[index].provenance_id;
    out_sample->region_id = domain->deltas[index].region_id;
    out_sample->flags = domain->deltas[index].flags;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_region_query(const dom_srz_domain* domain,
                         u32 region_id,
                         dom_domain_budget* budget,
                         dom_srz_region_sample* out_sample)
{
    u32 cost;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_srz_domain_is_active(domain)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }
    cost = dom_srz_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_srz_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_srz_region_collapsed(domain, region_id)) {
        const dom_srz_macro_capsule* capsule = dom_srz_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->zone_count = capsule->zone_count;
            out_sample->assignment_count = capsule->assignment_count;
            out_sample->policy_count = capsule->policy_count;
            out_sample->log_count = capsule->log_count;
            out_sample->hash_link_count = capsule->hash_link_count;
            out_sample->delta_count = capsule->delta_count;
            out_sample->verification_ok_count = capsule->verification_ok_count;
            out_sample->verification_fail_count = capsule->verification_fail_count;
        }
        out_sample->flags = DOM_SRZ_RESOLVE_PARTIAL;
        dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    for (u32 i = 0u; i < domain->zone_count; ++i) {
        if (region_id != 0u && domain->zones[i].region_id != region_id) {
            continue;
        }
        out_sample->zone_count += 1u;
        if (domain->zones[i].mode == DOM_SRZ_MODE_SERVER) {
            out_sample->server_mode_count += 1u;
        } else if (domain->zones[i].mode == DOM_SRZ_MODE_DELEGATED) {
            out_sample->delegated_mode_count += 1u;
        } else if (domain->zones[i].mode == DOM_SRZ_MODE_DORMANT) {
            out_sample->dormant_mode_count += 1u;
        }
    }
    for (u32 i = 0u; i < domain->assignment_count; ++i) {
        if (region_id != 0u && domain->assignments[i].region_id != region_id) {
            continue;
        }
        out_sample->assignment_count += 1u;
    }
    for (u32 i = 0u; i < domain->policy_count; ++i) {
        if (region_id != 0u && domain->policies[i].region_id != region_id) {
            continue;
        }
        out_sample->policy_count += 1u;
    }
    for (u32 i = 0u; i < domain->log_count; ++i) {
        if (region_id != 0u && domain->logs[i].region_id != region_id) {
            continue;
        }
        out_sample->log_count += 1u;
        if (domain->logs[i].flags & DOM_SRZ_LOG_VERIFIED) {
            out_sample->verification_ok_count += 1u;
        }
        if (domain->logs[i].flags & DOM_SRZ_LOG_FAILED) {
            out_sample->verification_fail_count += 1u;
        }
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        if (region_id != 0u && domain->hash_links[i].region_id != region_id) {
            continue;
        }
        out_sample->hash_link_count += 1u;
    }
    for (u32 i = 0u; i < domain->delta_count; ++i) {
        if (region_id != 0u && domain->deltas[i].region_id != region_id) {
            continue;
        }
        out_sample->delta_count += 1u;
    }
    out_sample->region_id = region_id;
    out_sample->failure_rate = dom_srz_ratio_from_counts(out_sample->verification_fail_count,
                                                         out_sample->verification_ok_count +
                                                         out_sample->verification_fail_count);
    out_sample->flags = 0u;
    dom_srz_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                          DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_srz_resolve(dom_srz_domain* domain,
                    u32 region_id,
                    u64 tick,
                    u64 tick_delta,
                    dom_domain_budget* budget,
                    dom_srz_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_full;
    q16_16 failure_rate;
    u32 flags = 0u;
    u32 ok_count = 0u;
    u32 fail_count = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    (void)tick;
    (void)tick_delta;
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_srz_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_SRZ_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_srz_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_SRZ_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_srz_region_collapsed(domain, region_id)) {
        const dom_srz_macro_capsule* capsule = dom_srz_find_capsule(domain, region_id);
        if (capsule) {
            out_result->zone_count = capsule->zone_count;
            out_result->assignment_count = capsule->assignment_count;
            out_result->policy_count = capsule->policy_count;
            out_result->log_count = capsule->log_count;
            out_result->hash_link_count = capsule->hash_link_count;
            out_result->delta_count = capsule->delta_count;
            out_result->verification_ok_count = capsule->verification_ok_count;
            out_result->verification_fail_count = capsule->verification_fail_count;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_SRZ_RESOLVE_PARTIAL;
        return 0;
    }

    cost_full = dom_srz_budget_cost(domain->policy.cost_full);

    for (u32 i = 0u; i < domain->zone_count; ++i) {
        if (region_id != 0u && domain->zones[i].region_id != region_id) {
            continue;
        }
        out_result->zone_count += 1u;
        if (domain->zones[i].mode == DOM_SRZ_MODE_SERVER) {
            out_result->server_mode_count += 1u;
        } else if (domain->zones[i].mode == DOM_SRZ_MODE_DELEGATED) {
            out_result->delegated_mode_count += 1u;
        } else if (domain->zones[i].mode == DOM_SRZ_MODE_DORMANT) {
            out_result->dormant_mode_count += 1u;
        }
    }
    for (u32 i = 0u; i < domain->assignment_count; ++i) {
        if (region_id != 0u && domain->assignments[i].region_id != region_id) {
            continue;
        }
        out_result->assignment_count += 1u;
    }
    for (u32 i = 0u; i < domain->policy_count; ++i) {
        if (region_id != 0u && domain->policies[i].region_id != region_id) {
            continue;
        }
        out_result->policy_count += 1u;
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        if (region_id != 0u && domain->hash_links[i].region_id != region_id) {
            continue;
        }
        out_result->hash_link_count += 1u;
    }
    for (u32 i = 0u; i < domain->delta_count; ++i) {
        if (region_id != 0u && domain->deltas[i].region_id != region_id) {
            continue;
        }
        out_result->delta_count += 1u;
    }

    for (u32 i = 0u; i < domain->log_count; ++i) {
        dom_srz_log* log = &domain->logs[i];
        int zone_index;
        int policy_index;
        const dom_srz_zone* zone;
        const dom_srz_policy* policy = 0;
        u32 process_total = 0u;
        u32 rng_total = 0u;
        d_bool verified = D_FALSE;
        d_bool epistemic_ok = D_TRUE;

        if (region_id != 0u && log->region_id != region_id) {
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_full)) {
            flags |= DOM_SRZ_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_SRZ_REFUSE_NONE) {
                out_result->refusal_reason = DOM_SRZ_REFUSE_BUDGET;
            }
            break;
        }
        out_result->log_count += 1u;
        log->flags &= ~(DOM_SRZ_LOG_VERIFIED | DOM_SRZ_LOG_FAILED | DOM_SRZ_LOG_EPISTEMIC_MISMATCH);

        zone_index = dom_srz_find_zone_index(domain, log->srz_id);
        if (zone_index < 0) {
            log->flags |= DOM_SRZ_LOG_FAILED;
            fail_count += 1u;
            out_result->refusal_reason = DOM_SRZ_REFUSE_ZONE_MISSING;
            flags |= DOM_SRZ_RESOLVE_VERIFICATION_FAILED;
            continue;
        }
        zone = &domain->zones[zone_index];
        epistemic_ok = dom_srz_log_epistemic_ok(zone, log);
        if (!epistemic_ok) {
            log->flags |= DOM_SRZ_LOG_FAILED | DOM_SRZ_LOG_EPISTEMIC_MISMATCH;
            fail_count += 1u;
            flags |= DOM_SRZ_RESOLVE_EPISTEMIC_REFUSED | DOM_SRZ_RESOLVE_VERIFICATION_FAILED;
            out_result->refusal_reason = DOM_SRZ_REFUSE_EPISTEMIC;
            continue;
        }

        if (zone->mode == DOM_SRZ_MODE_DORMANT) {
            flags |= DOM_SRZ_RESOLVE_PARTIAL;
            continue;
        }

        policy_index = dom_srz_find_policy_index(domain,
                                                 log->policy_id ? log->policy_id : zone->policy_id);
        if (policy_index >= 0) {
            policy = &domain->policies[policy_index];
        }

        if (zone->mode == DOM_SRZ_MODE_SERVER) {
            verified = D_TRUE;
        } else if (zone->mode == DOM_SRZ_MODE_DELEGATED) {
            u32 policy_mode = zone->verification_policy;
            if (policy && policy->verification_policy != DOM_SRZ_VERIFY_UNSET) {
                policy_mode = policy->verification_policy;
            }
            if (policy_mode == DOM_SRZ_VERIFY_STRICT) {
                flags |= DOM_SRZ_RESOLVE_STRICT_APPLIED;
                verified = dom_srz_chain_verify_strict(domain, log, 0, &process_total, &rng_total);
            } else if (policy_mode == DOM_SRZ_VERIFY_SPOT) {
                flags |= DOM_SRZ_RESOLVE_SPOT_APPLIED;
                verified = dom_srz_chain_verify_spot(domain, log, &process_total, &rng_total);
            } else if (policy_mode == DOM_SRZ_VERIFY_INVARIANT_ONLY) {
                flags |= DOM_SRZ_RESOLVE_INVARIANT_ONLY_APPLIED;
                verified = dom_srz_delta_verify(domain, log);
            } else {
                verified = D_FALSE;
            }
        }

        if (verified) {
            if (log->process_count > 0u && process_total > 0u && process_total != log->process_count) {
                verified = D_FALSE;
            }
            if (log->rng_stream_count > 0u && rng_total > 0u && rng_total != log->rng_stream_count) {
                verified = D_FALSE;
            }
        }

        if (verified) {
            log->flags |= DOM_SRZ_LOG_VERIFIED;
            ok_count += 1u;
            flags |= DOM_SRZ_RESOLVE_VERIFIED;
        } else {
            log->flags |= DOM_SRZ_LOG_FAILED;
            fail_count += 1u;
            flags |= DOM_SRZ_RESOLVE_VERIFICATION_FAILED;
            if (out_result->refusal_reason == DOM_SRZ_REFUSE_NONE) {
                out_result->refusal_reason = DOM_SRZ_REFUSE_PROOF_INVALID;
            }
        }
    }

    failure_rate = dom_srz_ratio_from_counts(fail_count, ok_count + fail_count);
    out_result->verification_ok_count = ok_count;
    out_result->verification_fail_count = fail_count;
    out_result->failure_rate = failure_rate;

    for (u32 i = 0u; i < domain->zone_count; ++i) {
        dom_srz_zone* zone = &domain->zones[i];
        if (region_id != 0u && zone->region_id != region_id) {
            continue;
        }
        for (u32 t = 0u; t < zone->escalation_count; ++t) {
            if (zone->escalation[t].metric_id == DOM_SRZ_METRIC_FAIL_RATE &&
                failure_rate >= zone->escalation[t].value) {
                zone->flags |= DOM_SRZ_ZONE_ESCALATED;
                flags |= DOM_SRZ_RESOLVE_ESCALATED;
            }
        }
        for (u32 t = 0u; t < zone->deescalation_count; ++t) {
            if (zone->deescalation[t].metric_id == DOM_SRZ_METRIC_FAIL_RATE &&
                failure_rate <= zone->deescalation[t].value) {
                zone->flags |= DOM_SRZ_ZONE_DEESCALATED;
                flags |= DOM_SRZ_RESOLVE_DEESCALATED;
            }
        }
    }

    out_result->flags = flags;
    out_result->ok = (fail_count == 0u) ? 1u : 0u;
    if (fail_count == 0u) {
        out_result->refusal_reason = DOM_SRZ_REFUSE_NONE;
    }
    return 0;
}

int dom_srz_domain_collapse_region(dom_srz_domain* domain, u32 region_id)
{
    dom_srz_macro_capsule capsule;
    u32 failure_bins[DOM_SRZ_HIST_BINS];
    u32 total_zones = 0u;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_srz_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_SRZ_MAX_CAPSULES) {
        return -2;
    }
    memset(failure_bins, 0, sizeof(failure_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;
    for (u32 i = 0u; i < domain->zone_count; ++i) {
        if (domain->zones[i].region_id != region_id) {
            continue;
        }
        capsule.zone_count += 1u;
        total_zones += 1u;
    }
    for (u32 i = 0u; i < domain->assignment_count; ++i) {
        if (domain->assignments[i].region_id != region_id) {
            continue;
        }
        capsule.assignment_count += 1u;
    }
    for (u32 i = 0u; i < domain->policy_count; ++i) {
        if (domain->policies[i].region_id != region_id) {
            continue;
        }
        capsule.policy_count += 1u;
    }
    for (u32 i = 0u; i < domain->log_count; ++i) {
        if (domain->logs[i].region_id != region_id) {
            continue;
        }
        capsule.log_count += 1u;
        if (domain->logs[i].flags & DOM_SRZ_LOG_VERIFIED) {
            capsule.verification_ok_count += 1u;
        }
        if (domain->logs[i].flags & DOM_SRZ_LOG_FAILED) {
            capsule.verification_fail_count += 1u;
        }
    }
    for (u32 i = 0u; i < domain->hash_link_count; ++i) {
        if (domain->hash_links[i].region_id != region_id) {
            continue;
        }
        capsule.hash_link_count += 1u;
    }
    for (u32 i = 0u; i < domain->delta_count; ++i) {
        if (domain->deltas[i].region_id != region_id) {
            continue;
        }
        capsule.delta_count += 1u;
    }

    if (total_zones > 0u) {
        q16_16 rate = dom_srz_ratio_from_counts(capsule.verification_fail_count,
                                                capsule.verification_ok_count +
                                                capsule.verification_fail_count);
        failure_bins[dom_srz_hist_bin(rate)] += total_zones;
    }
    for (u32 b = 0u; b < DOM_SRZ_HIST_BINS; ++b) {
        capsule.failure_hist[b] = dom_srz_hist_bin_ratio(failure_bins[b], total_zones);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_srz_domain_expand_region(dom_srz_domain* domain, u32 region_id)
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

u32 dom_srz_domain_capsule_count(const dom_srz_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_srz_macro_capsule* dom_srz_domain_capsule_at(const dom_srz_domain* domain, u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_srz_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
