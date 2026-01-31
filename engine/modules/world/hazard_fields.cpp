/*
FILE: source/domino/world/hazard_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/hazard_fields
RESPONSIBILITY: Implements deterministic hazard field sampling and exposure updates.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/hazard_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_HAZARD_RESOLVE_COST_BASE 1u

static q16_16 dom_hazard_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_HAZARD_RATIO_ONE_Q16) {
        return DOM_HAZARD_RATIO_ONE_Q16;
    }
    return value;
}

static q48_16 dom_hazard_q48_from_q16(q16_16 value)
{
    return d_q48_16_from_q16_16(value);
}

static void dom_hazard_type_init(dom_hazard_type* type)
{
    if (!type) {
        return;
    }
    memset(type, 0, sizeof(*type));
    type->hazard_class = DOM_HAZARD_CLASS_UNSET;
}

static void dom_hazard_field_init(dom_hazard_field* field)
{
    if (!field) {
        return;
    }
    memset(field, 0, sizeof(*field));
}

static void dom_hazard_exposure_init(dom_hazard_exposure* exposure)
{
    if (!exposure) {
        return;
    }
    memset(exposure, 0, sizeof(*exposure));
}

static int dom_hazard_find_type_index(const dom_hazard_domain* domain, u32 type_id)
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

static int dom_hazard_find_field_index(const dom_hazard_domain* domain, u32 hazard_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->field_count; ++i) {
        if (domain->fields[i].hazard_id == hazard_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_hazard_find_exposure_index(const dom_hazard_domain* domain, u32 exposure_id)
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

static d_bool dom_hazard_domain_is_active(const dom_hazard_domain* domain)
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

static d_bool dom_hazard_region_collapsed(const dom_hazard_domain* domain, u32 region_id)
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

static const dom_hazard_macro_capsule* dom_hazard_find_capsule(const dom_hazard_domain* domain,
                                                               u32 region_id)
{
    if (!domain) {
        return (const dom_hazard_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_hazard_macro_capsule*)0;
}

static void dom_hazard_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_hazard_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_hazard_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_HAZARD_RESOLVE_COST_BASE : cost_units;
}

static q16_16 dom_hazard_distance_q16(const dom_domain_point* a, const dom_domain_point* b)
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

static q16_16 dom_hazard_falloff(const dom_hazard_field* field, const dom_domain_point* point)
{
    q16_16 distance;
    q16_16 radius;
    q16_16 remaining;
    if (!field || !point) {
        return 0;
    }
    radius = field->radius;
    distance = dom_hazard_distance_q16(&field->center, point);
    if (radius <= 0) {
        return (distance <= 0) ? DOM_HAZARD_RATIO_ONE_Q16 : 0;
    }
    if (distance >= radius) {
        return 0;
    }
    remaining = d_q16_16_sub(radius, distance);
    return dom_hazard_clamp_ratio(d_fixed_div_q16_16(remaining, radius));
}

static d_bool dom_hazard_apply_decay(dom_hazard_field* field, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    if (!field || tick_delta == 0u) {
        return D_FALSE;
    }
    if (field->decay_rate <= 0 || field->intensity <= 0) {
        return D_FALSE;
    }
    decay_per_tick = d_q16_16_mul(field->intensity, field->decay_rate);
    if (decay_per_tick <= 0) {
        return D_FALSE;
    }
    decay_total = dom_hazard_q48_from_q16(decay_per_tick);
    if (tick_delta > 1u) {
        decay_total = d_q48_16_mul(decay_total, d_q48_16_from_int((i64)tick_delta));
    }
    decay_q16 = d_q16_16_from_q48_16(decay_total);
    if (decay_q16 <= 0) {
        return D_FALSE;
    }
    if (decay_q16 >= field->intensity) {
        field->intensity = 0;
    } else {
        field->intensity = d_q16_16_sub(field->intensity, decay_q16);
    }
    return D_TRUE;
}

static q16_16 dom_hazard_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_hazard_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_hazard_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_HAZARD_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_HAZARD_HIST_BINS) {
        scaled = DOM_HAZARD_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_hazard_surface_desc_init(dom_hazard_surface_desc* desc)
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
    for (u32 i = 0u; i < DOM_HAZARD_MAX_TYPES; ++i) {
        desc->types[i].type_id = 0u;
        desc->types[i].hazard_class = DOM_HAZARD_CLASS_UNSET;
    }
    for (u32 i = 0u; i < DOM_HAZARD_MAX_FIELDS; ++i) {
        desc->fields[i].hazard_id = 0u;
        desc->fields[i].hazard_type_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HAZARD_MAX_EXPOSURES; ++i) {
        desc->exposures[i].exposure_id = 0u;
        desc->exposures[i].hazard_type_id = 0u;
    }
}

void dom_hazard_domain_init(dom_hazard_domain* domain,
                            const dom_hazard_surface_desc* desc)
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
    domain->type_count = (desc->type_count > DOM_HAZARD_MAX_TYPES)
                           ? DOM_HAZARD_MAX_TYPES
                           : desc->type_count;
    domain->field_count = (desc->field_count > DOM_HAZARD_MAX_FIELDS)
                            ? DOM_HAZARD_MAX_FIELDS
                            : desc->field_count;
    domain->exposure_count = (desc->exposure_count > DOM_HAZARD_MAX_EXPOSURES)
                               ? DOM_HAZARD_MAX_EXPOSURES
                               : desc->exposure_count;
    for (u32 i = 0u; i < domain->type_count; ++i) {
        dom_hazard_type_init(&domain->types[i]);
        domain->types[i].type_id = desc->types[i].type_id;
        domain->types[i].hazard_class = desc->types[i].hazard_class;
        domain->types[i].default_intensity = desc->types[i].default_intensity;
        domain->types[i].default_exposure_rate = desc->types[i].default_exposure_rate;
        domain->types[i].default_decay_rate = desc->types[i].default_decay_rate;
        domain->types[i].default_uncertainty = desc->types[i].default_uncertainty;
    }
    for (u32 i = 0u; i < domain->field_count; ++i) {
        dom_hazard_field_init(&domain->fields[i]);
        domain->fields[i].hazard_id = desc->fields[i].hazard_id;
        domain->fields[i].hazard_type_id = desc->fields[i].hazard_type_id;
        domain->fields[i].intensity = desc->fields[i].intensity;
        domain->fields[i].exposure_rate = desc->fields[i].exposure_rate;
        domain->fields[i].decay_rate = desc->fields[i].decay_rate;
        domain->fields[i].uncertainty = desc->fields[i].uncertainty;
        domain->fields[i].provenance_id = desc->fields[i].provenance_id;
        domain->fields[i].region_id = desc->fields[i].region_id;
        domain->fields[i].radius = desc->fields[i].radius;
        domain->fields[i].center = desc->fields[i].center;
    }
    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        dom_hazard_exposure_init(&domain->exposures[i]);
        domain->exposures[i].exposure_id = desc->exposures[i].exposure_id;
        domain->exposures[i].hazard_type_id = desc->exposures[i].hazard_type_id;
        domain->exposures[i].exposure_limit = desc->exposures[i].exposure_limit;
        domain->exposures[i].sensitivity = desc->exposures[i].sensitivity;
        domain->exposures[i].uncertainty = desc->exposures[i].uncertainty;
        domain->exposures[i].provenance_id = desc->exposures[i].provenance_id;
        domain->exposures[i].region_id = desc->exposures[i].region_id;
        domain->exposures[i].location = desc->exposures[i].location;
        domain->exposures[i].exposure_accumulated = desc->exposures[i].exposure_accumulated;
    }
    domain->capsule_count = 0u;
}

void dom_hazard_domain_free(dom_hazard_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->type_count = 0u;
    domain->field_count = 0u;
    domain->exposure_count = 0u;
    domain->capsule_count = 0u;
}

void dom_hazard_domain_set_state(dom_hazard_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_hazard_domain_set_policy(dom_hazard_domain* domain,
                                  const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_hazard_type_query(const dom_hazard_domain* domain,
                          u32 type_id,
                          dom_domain_budget* budget,
                          dom_hazard_type_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HAZARD_TYPE_UNRESOLVED;

    if (!dom_hazard_domain_is_active(domain)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_hazard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_hazard_find_type_index(domain, type_id);
    if (index < 0) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->type_id = domain->types[index].type_id;
    out_sample->hazard_class = domain->types[index].hazard_class;
    out_sample->default_intensity = domain->types[index].default_intensity;
    out_sample->default_exposure_rate = domain->types[index].default_exposure_rate;
    out_sample->default_decay_rate = domain->types[index].default_decay_rate;
    out_sample->default_uncertainty = domain->types[index].default_uncertainty;
    out_sample->flags = 0u;
    dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_hazard_field_query(const dom_hazard_domain* domain,
                           u32 field_id,
                           dom_domain_budget* budget,
                           dom_hazard_field_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HAZARD_FIELD_UNRESOLVED;

    if (!dom_hazard_domain_is_active(domain)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_hazard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_hazard_find_field_index(domain, field_id);
    if (index < 0) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_hazard_region_collapsed(domain, domain->fields[index].region_id)) {
        out_sample->hazard_id = domain->fields[index].hazard_id;
        out_sample->hazard_type_id = domain->fields[index].hazard_type_id;
        out_sample->region_id = domain->fields[index].region_id;
        out_sample->flags = DOM_HAZARD_FIELD_COLLAPSED;
        dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->hazard_id = domain->fields[index].hazard_id;
    out_sample->hazard_type_id = domain->fields[index].hazard_type_id;
    out_sample->intensity = domain->fields[index].intensity;
    out_sample->exposure_rate = domain->fields[index].exposure_rate;
    out_sample->decay_rate = domain->fields[index].decay_rate;
    out_sample->uncertainty = domain->fields[index].uncertainty;
    out_sample->provenance_id = domain->fields[index].provenance_id;
    out_sample->region_id = domain->fields[index].region_id;
    out_sample->radius = domain->fields[index].radius;
    out_sample->flags = 0u;
    dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_hazard_exposure_query(const dom_hazard_domain* domain,
                              u32 exposure_id,
                              dom_domain_budget* budget,
                              dom_hazard_exposure_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HAZARD_EXPOSURE_UNRESOLVED;

    if (!dom_hazard_domain_is_active(domain)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_hazard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_hazard_find_exposure_index(domain, exposure_id);
    if (index < 0) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_hazard_region_collapsed(domain, domain->exposures[index].region_id)) {
        out_sample->exposure_id = domain->exposures[index].exposure_id;
        out_sample->hazard_type_id = domain->exposures[index].hazard_type_id;
        out_sample->region_id = domain->exposures[index].region_id;
        out_sample->flags = DOM_HAZARD_EXPOSURE_COLLAPSED;
        dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->exposure_id = domain->exposures[index].exposure_id;
    out_sample->hazard_type_id = domain->exposures[index].hazard_type_id;
    out_sample->exposure_limit = domain->exposures[index].exposure_limit;
    out_sample->sensitivity = domain->exposures[index].sensitivity;
    out_sample->uncertainty = domain->exposures[index].uncertainty;
    out_sample->provenance_id = domain->exposures[index].provenance_id;
    out_sample->region_id = domain->exposures[index].region_id;
    out_sample->exposure_accumulated = domain->exposures[index].exposure_accumulated;
    out_sample->flags = 0u;
    if (out_sample->exposure_limit > 0 &&
        out_sample->exposure_accumulated >= out_sample->exposure_limit) {
        out_sample->flags |= DOM_HAZARD_EXPOSURE_OVER_LIMIT;
    }
    dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_hazard_region_query(const dom_hazard_domain* domain,
                            u32 region_id,
                            dom_domain_budget* budget,
                            dom_hazard_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_exposure;
    q48_16 hazard_total = 0;
    q48_16 exposure_total = 0;
    u32 fields_seen = 0u;
    u32 exposures_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_hazard_domain_is_active(domain)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_hazard_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_hazard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_hazard_region_collapsed(domain, region_id)) {
        const dom_hazard_macro_capsule* capsule = dom_hazard_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->field_count = capsule->field_count;
            out_sample->exposure_count = capsule->exposure_count;
            out_sample->hazard_energy_total = capsule->hazard_energy_total;
        }
        out_sample->flags = DOM_HAZARD_RESOLVE_PARTIAL;
        dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_field = dom_hazard_budget_cost(domain->policy.cost_medium);
    cost_exposure = dom_hazard_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_hazard_region_collapsed(domain, field_region)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            break;
        }
        hazard_total = d_q48_16_add(hazard_total, dom_hazard_q48_from_q16(domain->fields[i].intensity));
        fields_seen += 1u;
    }

    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        u32 exposure_region = domain->exposures[i].region_id;
        if (region_id != 0u && exposure_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_hazard_region_collapsed(domain, exposure_region)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_exposure)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            break;
        }
        exposure_total = d_q48_16_add(exposure_total, domain->exposures[i].exposure_accumulated);
        exposures_seen += 1u;
    }

    out_sample->region_id = region_id;
    out_sample->field_count = fields_seen;
    out_sample->exposure_count = exposures_seen;
    out_sample->hazard_energy_total = hazard_total;
    out_sample->exposure_total = exposure_total;
    out_sample->flags = flags;
    dom_hazard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                             cost_base, budget);
    return 0;
}

int dom_hazard_resolve(dom_hazard_domain* domain,
                       u32 region_id,
                       u64 tick,
                       u64 tick_delta,
                       dom_domain_budget* budget,
                       dom_hazard_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_field;
    u32 cost_exposure;
    q48_16 hazard_total = 0;
    q48_16 exposure_total = 0;
    u32 fields_seen = 0u;
    u32 exposures_seen = 0u;
    u32 flags = 0u;
    u32 over_limit_count = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    (void)tick;
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_hazard_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_HAZARD_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_hazard_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_HAZARD_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_hazard_region_collapsed(domain, region_id)) {
        const dom_hazard_macro_capsule* capsule = dom_hazard_find_capsule(domain, region_id);
        if (capsule) {
            out_result->field_count = capsule->field_count;
            out_result->exposure_count = capsule->exposure_count;
            out_result->hazard_energy_total = capsule->hazard_energy_total;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_HAZARD_RESOLVE_PARTIAL;
        return 0;
    }

    cost_field = dom_hazard_budget_cost(domain->policy.cost_medium);
    cost_exposure = dom_hazard_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->field_count; ++i) {
        u32 field_region = domain->fields[i].region_id;
        if (region_id != 0u && field_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_hazard_region_collapsed(domain, field_region)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_field)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HAZARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HAZARD_REFUSE_BUDGET;
            }
            break;
        }
        if (dom_hazard_apply_decay(&domain->fields[i], tick_delta)) {
            domain->fields[i].flags |= DOM_HAZARD_FIELD_DECAYING;
            flags |= DOM_HAZARD_RESOLVE_DECAYED;
        }
        hazard_total = d_q48_16_add(hazard_total, dom_hazard_q48_from_q16(domain->fields[i].intensity));
        fields_seen += 1u;
    }

    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        dom_hazard_exposure* exposure = &domain->exposures[i];
        q48_16 exposure_delta_total = 0;
        u32 exposure_region = exposure->region_id;
        if (region_id != 0u && exposure_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_hazard_region_collapsed(domain, exposure_region)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_exposure)) {
            flags |= DOM_HAZARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HAZARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HAZARD_REFUSE_BUDGET;
            }
            break;
        }
        for (u32 f = 0u; f < domain->field_count; ++f) {
            const dom_hazard_field* field = &domain->fields[f];
            q16_16 falloff;
            q16_16 contribution;
            if (region_id != 0u && field->region_id != region_id) {
                continue;
            }
            if (region_id == 0u && dom_hazard_region_collapsed(domain, field->region_id)) {
                flags |= DOM_HAZARD_RESOLVE_PARTIAL;
                continue;
            }
            if (exposure->hazard_type_id != 0u &&
                exposure->hazard_type_id != field->hazard_type_id) {
                continue;
            }
            if (!dom_domain_budget_consume(budget, cost_field)) {
                flags |= DOM_HAZARD_RESOLVE_PARTIAL;
                if (out_result->refusal_reason == DOM_HAZARD_REFUSE_NONE) {
                    out_result->refusal_reason = DOM_HAZARD_REFUSE_BUDGET;
                }
                break;
            }
            if (field->intensity <= 0 || field->exposure_rate <= 0) {
                continue;
            }
            falloff = dom_hazard_falloff(field, &exposure->location);
            if (falloff <= 0) {
                continue;
            }
            contribution = d_q16_16_mul(field->intensity, falloff);
            contribution = d_q16_16_mul(contribution, field->exposure_rate);
            if (exposure->sensitivity > 0) {
                contribution = d_q16_16_mul(contribution, exposure->sensitivity);
            }
            if (contribution > 0) {
                q48_16 delta = dom_hazard_q48_from_q16(contribution);
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
            exposure->flags |= DOM_HAZARD_EXPOSURE_OVER_LIMIT;
            flags |= DOM_HAZARD_RESOLVE_OVER_LIMIT;
            over_limit_count += 1u;
        }
        exposure_total = d_q48_16_add(exposure_total, exposure->exposure_accumulated);
        exposures_seen += 1u;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->field_count = fields_seen;
    out_result->exposure_count = exposures_seen;
    out_result->exposure_over_limit_count = over_limit_count;
    out_result->hazard_energy_total = hazard_total;
    out_result->exposure_total = exposure_total;
    return 0;
}

int dom_hazard_domain_collapse_region(dom_hazard_domain* domain, u32 region_id)
{
    dom_hazard_macro_capsule capsule;
    u32 hist_bins[DOM_HAZARD_HIST_BINS];
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_hazard_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_HAZARD_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;
    for (u32 i = 0u; i < domain->field_count; ++i) {
        int type_index;
        u32 hazard_class;
        if (domain->fields[i].region_id != region_id) {
            continue;
        }
        capsule.field_count += 1u;
        capsule.hazard_energy_total = d_q48_16_add(
            capsule.hazard_energy_total,
            dom_hazard_q48_from_q16(domain->fields[i].intensity));
        type_index = dom_hazard_find_type_index(domain, domain->fields[i].hazard_type_id);
        if (type_index >= 0) {
            hazard_class = domain->types[type_index].hazard_class;
            if (hazard_class > 0u && hazard_class <= DOM_HAZARD_CLASS_COUNT) {
                capsule.hazard_type_counts[hazard_class - 1u] += 1u;
            }
        }
    }
    for (u32 i = 0u; i < domain->exposure_count; ++i) {
        q16_16 ratio = 0;
        if (domain->exposures[i].region_id != region_id) {
            continue;
        }
        capsule.exposure_count += 1u;
        if (domain->exposures[i].exposure_limit > 0) {
            q48_16 div = d_q48_16_div(domain->exposures[i].exposure_accumulated,
                                      domain->exposures[i].exposure_limit);
            ratio = dom_hazard_clamp_ratio(d_q16_16_from_q48_16(div));
        }
        hist_bins[dom_hazard_hist_bin(ratio)] += 1u;
    }
    for (u32 b = 0u; b < DOM_HAZARD_HIST_BINS; ++b) {
        capsule.exposure_hist[b] = dom_hazard_hist_bin_ratio(hist_bins[b], capsule.exposure_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_hazard_domain_expand_region(dom_hazard_domain* domain, u32 region_id)
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

u32 dom_hazard_domain_capsule_count(const dom_hazard_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_hazard_macro_capsule* dom_hazard_domain_capsule_at(const dom_hazard_domain* domain,
                                                             u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_hazard_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
