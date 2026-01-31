/*
FILE: source/domino/world/fluid_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/fluid_fields
RESPONSIBILITY: Implements deterministic fluid stores, flows, pressure, and containment resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/fluid_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>

#define DOM_FLUID_RNG_MAX 0xFFFFFFFFu
#define DOM_FLUID_CASCADE_DIVISOR 2u
#define DOM_FLUID_RESOLVE_COST_BASE 1u
#define DOM_FLUID_DEFAULT_RUPTURE_RELEASE_Q16 ((q16_16)0x00004000)

static q48_16 dom_fluid_min_q48(q48_16 a, q48_16 b)
{
    return (a < b) ? a : b;
}

static q16_16 dom_fluid_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_FLUID_RATIO_ONE_Q16) {
        return DOM_FLUID_RATIO_ONE_Q16;
    }
    return value;
}

static void dom_fluid_store_init(dom_fluid_store* store)
{
    if (!store) {
        return;
    }
    memset(store, 0, sizeof(*store));
}

static void dom_fluid_flow_init(dom_fluid_flow* flow)
{
    if (!flow) {
        return;
    }
    memset(flow, 0, sizeof(*flow));
    flow->efficiency = DOM_FLUID_RATIO_ONE_Q16;
}

static void dom_fluid_pressure_init(dom_fluid_pressure* pressure)
{
    if (!pressure) {
        return;
    }
    memset(pressure, 0, sizeof(*pressure));
    pressure->release_ratio = DOM_FLUID_DEFAULT_RUPTURE_RELEASE_Q16;
}

static void dom_fluid_property_init(dom_fluid_property* property)
{
    if (!property) {
        return;
    }
    memset(property, 0, sizeof(*property));
}

static int dom_fluid_find_store_index(const dom_fluid_domain* domain, u32 store_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->store_count; ++i) {
        if (domain->stores[i].store_id == store_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_fluid_find_flow_index(const dom_fluid_domain* domain, u32 flow_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        if (domain->flows[i].flow_id == flow_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_fluid_find_pressure_index(const dom_fluid_domain* domain, u32 pressure_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        if (domain->pressures[i].pressure_id == pressure_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_fluid_find_pressure_store_index(const dom_fluid_domain* domain, u32 store_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        if (domain->pressures[i].store_id == store_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_fluid_find_property_index(const dom_fluid_domain* domain, u32 property_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->property_count; ++i) {
        if (domain->properties[i].property_id == property_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_fluid_domain_is_active(const dom_fluid_domain* domain)
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

static d_bool dom_fluid_network_collapsed(const dom_fluid_domain* domain, u32 network_id)
{
    if (!domain) {
        return D_FALSE;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].network_id == network_id) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

static const dom_fluid_macro_capsule* dom_fluid_find_capsule(const dom_fluid_domain* domain,
                                                             u32 network_id)
{
    if (!domain) {
        return (const dom_fluid_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].network_id == network_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_fluid_macro_capsule*)0;
}

static void dom_fluid_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_fluid_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_fluid_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_FLUID_RESOLVE_COST_BASE : cost_units;
}

static q48_16 dom_fluid_ratio_mul_q48(q48_16 value, q16_16 ratio)
{
    q16_16 clamped = dom_fluid_clamp_ratio(ratio);
    return d_q48_16_mul(value, d_q48_16_from_q16_16(clamped));
}

static u32 dom_fluid_ratio_to_u32(q16_16 ratio)
{
    q16_16 clamped = dom_fluid_clamp_ratio(ratio);
    if (clamped <= 0) {
        return 0u;
    }
    if (clamped >= DOM_FLUID_RATIO_ONE_Q16) {
        return DOM_FLUID_RNG_MAX;
    }
    return (u32)(((u64)(u32)clamped * (u64)DOM_FLUID_RNG_MAX) >> Q16_16_FRAC_BITS);
}

static d_bool dom_fluid_flow_failure_roll(const dom_fluid_domain* domain,
                                          const dom_fluid_flow* flow,
                                          u64 tick)
{
    d_rng_state rng;
    const char* stream_name = "noise.stream.fluid.flow.failure";
    u32 threshold;
    if (!domain || !flow) {
        return D_FALSE;
    }
    if (flow->failure_chance <= 0) {
        return D_FALSE;
    }
    D_DET_GUARD_RNG_STREAM_NAME(stream_name);
    d_rng_state_from_context(&rng,
                             domain->surface.world_seed,
                             domain->surface.domain_id,
                             (u64)flow->flow_id,
                             tick,
                             stream_name,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
    threshold = dom_fluid_ratio_to_u32(flow->failure_chance);
    return (d_rng_next_u32(&rng) <= threshold) ? D_TRUE : D_FALSE;
}

static d_bool dom_fluid_store_apply_leakage(dom_fluid_store* store,
                                            u64 tick_delta,
                                            q48_16* io_leak_total)
{
    q48_16 leak;
    if (!store || tick_delta == 0u || store->leakage_rate <= 0) {
        return D_FALSE;
    }
    leak = dom_fluid_ratio_mul_q48(store->volume, store->leakage_rate);
    if (tick_delta > 1u) {
        leak = d_q48_16_mul(leak, d_q48_16_from_int((i64)tick_delta));
    }
    if (leak <= 0) {
        return D_FALSE;
    }
    if (leak > store->volume) {
        leak = store->volume;
    }
    store->volume = d_q48_16_sub(store->volume, leak);
    if (io_leak_total) {
        *io_leak_total = d_q48_16_add(*io_leak_total, leak);
    }
    return D_TRUE;
}

static q16_16 dom_fluid_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_fluid_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_fluid_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_FLUID_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_FLUID_HIST_BINS) {
        scaled = DOM_FLUID_HIST_BINS - 1u;
    }
    return scaled;
}

static q48_16 dom_fluid_mix_q48(q48_16 base_value,
                                q48_16 base_volume,
                                q48_16 incoming_value,
                                q48_16 incoming_volume)
{
    q48_16 total = d_q48_16_add(base_volume, incoming_volume);
    if (total <= 0) {
        return base_value;
    }
    return d_q48_16_add(
        d_q48_16_mul(base_value, d_q48_16_div(base_volume, total)),
        d_q48_16_mul(incoming_value, d_q48_16_div(incoming_volume, total)));
}

static q16_16 dom_fluid_mix_q16(q16_16 base_value,
                                q48_16 base_volume,
                                q16_16 incoming_value,
                                q48_16 incoming_volume)
{
    q48_16 mixed = dom_fluid_mix_q48(d_q48_16_from_q16_16(base_value),
                                    base_volume,
                                    d_q48_16_from_q16_16(incoming_value),
                                    incoming_volume);
    return dom_fluid_clamp_ratio(d_q16_16_from_q48_16(mixed));
}

static q48_16 dom_fluid_pressure_amount(const dom_fluid_domain* domain,
                                        const dom_fluid_store* store,
                                        const dom_fluid_pressure* pressure)
{
    q48_16 base;
    q48_16 ratio;
    if (!domain || !store || !pressure) {
        return 0;
    }
    base = (pressure->pressure_limit > 0) ? pressure->pressure_limit : domain->surface.pressure_scale;
    if (base <= 0 || store->max_volume <= 0) {
        return 0;
    }
    ratio = d_q48_16_div(store->volume, store->max_volume);
    if (ratio < 0) {
        ratio = 0;
    }
    return d_q48_16_mul(ratio, base);
}

void dom_fluid_surface_desc_init(dom_fluid_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->pressure_scale = d_q48_16_from_int(1);
    for (u32 i = 0u; i < DOM_FLUID_MAX_STORES; ++i) {
        desc->stores[i].store_id = 0u;
    }
    for (u32 i = 0u; i < DOM_FLUID_MAX_FLOWS; ++i) {
        desc->flows[i].flow_id = 0u;
        desc->flows[i].efficiency = DOM_FLUID_RATIO_ONE_Q16;
    }
    for (u32 i = 0u; i < DOM_FLUID_MAX_PRESSURES; ++i) {
        desc->pressures[i].pressure_id = 0u;
        desc->pressures[i].release_ratio = DOM_FLUID_DEFAULT_RUPTURE_RELEASE_Q16;
    }
    for (u32 i = 0u; i < DOM_FLUID_MAX_PROPERTIES; ++i) {
        desc->properties[i].property_id = 0u;
    }
}

void dom_fluid_domain_init(dom_fluid_domain* domain,
                           const dom_fluid_surface_desc* desc)
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
    domain->store_count = (desc->store_count > DOM_FLUID_MAX_STORES)
                            ? DOM_FLUID_MAX_STORES
                            : desc->store_count;
    domain->flow_count = (desc->flow_count > DOM_FLUID_MAX_FLOWS)
                            ? DOM_FLUID_MAX_FLOWS
                            : desc->flow_count;
    domain->pressure_count = (desc->pressure_count > DOM_FLUID_MAX_PRESSURES)
                            ? DOM_FLUID_MAX_PRESSURES
                            : desc->pressure_count;
    domain->property_count = (desc->property_count > DOM_FLUID_MAX_PROPERTIES)
                            ? DOM_FLUID_MAX_PROPERTIES
                            : desc->property_count;

    for (u32 i = 0u; i < domain->store_count; ++i) {
        dom_fluid_store_init(&domain->stores[i]);
        domain->stores[i].store_id = desc->stores[i].store_id;
        domain->stores[i].fluid_type = desc->stores[i].fluid_type;
        domain->stores[i].volume = desc->stores[i].volume;
        domain->stores[i].max_volume = desc->stores[i].max_volume;
        domain->stores[i].temperature = desc->stores[i].temperature;
        domain->stores[i].contamination = desc->stores[i].contamination;
        domain->stores[i].leakage_rate = desc->stores[i].leakage_rate;
        domain->stores[i].network_id = desc->stores[i].network_id;
        domain->stores[i].location = desc->stores[i].location;
    }

    for (u32 i = 0u; i < domain->flow_count; ++i) {
        dom_fluid_flow_init(&domain->flows[i]);
        domain->flows[i].flow_id = desc->flows[i].flow_id;
        domain->flows[i].network_id = desc->flows[i].network_id;
        domain->flows[i].source_store_id = desc->flows[i].source_store_id;
        domain->flows[i].sink_store_id = desc->flows[i].sink_store_id;
        domain->flows[i].max_transfer_rate = desc->flows[i].max_transfer_rate;
        domain->flows[i].efficiency = desc->flows[i].efficiency;
        domain->flows[i].latency_ticks = desc->flows[i].latency_ticks;
        domain->flows[i].failure_mode_mask = desc->flows[i].failure_mode_mask;
        domain->flows[i].failure_chance = desc->flows[i].failure_chance;
        domain->flows[i].energy_per_volume = desc->flows[i].energy_per_volume;
    }

    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        dom_fluid_pressure_init(&domain->pressures[i]);
        domain->pressures[i].pressure_id = desc->pressures[i].pressure_id;
        domain->pressures[i].store_id = desc->pressures[i].store_id;
        domain->pressures[i].pressure_limit = desc->pressures[i].pressure_limit;
        domain->pressures[i].rupture_threshold = desc->pressures[i].rupture_threshold;
        domain->pressures[i].release_ratio = desc->pressures[i].release_ratio;
        if (domain->pressures[i].release_ratio <= 0) {
            domain->pressures[i].release_ratio = DOM_FLUID_DEFAULT_RUPTURE_RELEASE_Q16;
        }
    }

    for (u32 i = 0u; i < domain->property_count; ++i) {
        dom_fluid_property_init(&domain->properties[i]);
        domain->properties[i].property_id = desc->properties[i].property_id;
        domain->properties[i].fluid_type = desc->properties[i].fluid_type;
        domain->properties[i].density = desc->properties[i].density;
        domain->properties[i].viscosity_class = desc->properties[i].viscosity_class;
        domain->properties[i].compressibility_class = desc->properties[i].compressibility_class;
        domain->properties[i].hazard_profile = desc->properties[i].hazard_profile;
    }

    domain->capsule_count = 0u;
}

void dom_fluid_domain_free(dom_fluid_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->store_count = 0u;
    domain->flow_count = 0u;
    domain->pressure_count = 0u;
    domain->property_count = 0u;
    domain->capsule_count = 0u;
}

void dom_fluid_domain_set_state(dom_fluid_domain* domain,
                                u32 existence_state,
                                u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_fluid_domain_set_policy(dom_fluid_domain* domain,
                                 const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_fluid_store_query(const dom_fluid_domain* domain,
                          u32 store_id,
                          dom_domain_budget* budget,
                          dom_fluid_store_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_FLUID_STORE_UNRESOLVED;

    if (!dom_fluid_domain_is_active(domain)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_fluid_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_fluid_find_store_index(domain, store_id);
    if (index < 0) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_fluid_network_collapsed(domain, domain->stores[index].network_id)) {
        out_sample->flags = DOM_FLUID_STORE_COLLAPSED;
        dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        out_sample->store_id = domain->stores[index].store_id;
        out_sample->network_id = domain->stores[index].network_id;
        return 0;
    }

    out_sample->store_id = domain->stores[index].store_id;
    out_sample->fluid_type = domain->stores[index].fluid_type;
    out_sample->volume = domain->stores[index].volume;
    out_sample->max_volume = domain->stores[index].max_volume;
    out_sample->temperature = domain->stores[index].temperature;
    out_sample->contamination = domain->stores[index].contamination;
    out_sample->leakage_rate = domain->stores[index].leakage_rate;
    out_sample->network_id = domain->stores[index].network_id;
    out_sample->flags = domain->stores[index].flags;
    dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_fluid_flow_query(const dom_fluid_domain* domain,
                         u32 flow_id,
                         dom_domain_budget* budget,
                         dom_fluid_flow_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_FLUID_FLOW_UNRESOLVED;

    if (!dom_fluid_domain_is_active(domain)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_fluid_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_fluid_find_flow_index(domain, flow_id);
    if (index < 0) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_fluid_network_collapsed(domain, domain->flows[index].network_id)) {
        out_sample->flags = DOM_FLUID_FLOW_COLLAPSED;
        dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        out_sample->flow_id = domain->flows[index].flow_id;
        out_sample->network_id = domain->flows[index].network_id;
        return 0;
    }

    out_sample->flow_id = domain->flows[index].flow_id;
    out_sample->network_id = domain->flows[index].network_id;
    out_sample->source_store_id = domain->flows[index].source_store_id;
    out_sample->sink_store_id = domain->flows[index].sink_store_id;
    out_sample->max_transfer_rate = domain->flows[index].max_transfer_rate;
    out_sample->efficiency = domain->flows[index].efficiency;
    out_sample->latency_ticks = domain->flows[index].latency_ticks;
    out_sample->failure_mode_mask = domain->flows[index].failure_mode_mask;
    out_sample->failure_chance = domain->flows[index].failure_chance;
    out_sample->energy_per_volume = domain->flows[index].energy_per_volume;
    out_sample->flags = domain->flows[index].flags;
    dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_fluid_pressure_query(const dom_fluid_domain* domain,
                             u32 pressure_id,
                             dom_domain_budget* budget,
                             dom_fluid_pressure_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_FLUID_PRESSURE_UNRESOLVED;

    if (!dom_fluid_domain_is_active(domain)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_fluid_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_fluid_find_pressure_index(domain, pressure_id);
    if (index < 0) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    {
        int store_index = dom_fluid_find_store_index(domain, domain->pressures[index].store_id);
        if (store_index < 0) {
            dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
            return 0;
        }
        if (dom_fluid_network_collapsed(domain, domain->stores[store_index].network_id)) {
            out_sample->flags = DOM_FLUID_PRESSURE_UNRESOLVED;
            dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                    DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
            out_sample->pressure_id = domain->pressures[index].pressure_id;
            out_sample->store_id = domain->pressures[index].store_id;
            return 0;
        }
        out_sample->amount = dom_fluid_pressure_amount(domain,
                                                       &domain->stores[store_index],
                                                       &domain->pressures[index]);
        out_sample->pressure_limit = domain->pressures[index].pressure_limit;
        out_sample->rupture_threshold = domain->pressures[index].rupture_threshold;
        out_sample->release_ratio = domain->pressures[index].release_ratio;
        out_sample->flags = 0u;
        if (out_sample->pressure_limit > 0 && out_sample->amount > out_sample->pressure_limit) {
            out_sample->flags |= DOM_FLUID_PRESSURE_OVER_LIMIT;
        }
        if (out_sample->rupture_threshold > 0 && out_sample->amount > out_sample->rupture_threshold) {
            out_sample->flags |= DOM_FLUID_PRESSURE_RUPTURED;
        }
    }

    out_sample->pressure_id = domain->pressures[index].pressure_id;
    out_sample->store_id = domain->pressures[index].store_id;
    dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_fluid_property_query(const dom_fluid_domain* domain,
                             u32 property_id,
                             dom_domain_budget* budget,
                             dom_fluid_property_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_FLUID_PROPERTY_UNRESOLVED;

    if (!dom_fluid_domain_is_active(domain)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_fluid_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_fluid_find_property_index(domain, property_id);
    if (index < 0) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->property_id = domain->properties[index].property_id;
    out_sample->fluid_type = domain->properties[index].fluid_type;
    out_sample->density = domain->properties[index].density;
    out_sample->viscosity_class = domain->properties[index].viscosity_class;
    out_sample->compressibility_class = domain->properties[index].compressibility_class;
    out_sample->hazard_profile = domain->properties[index].hazard_profile;
    out_sample->flags = 0u;
    dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_fluid_network_query(const dom_fluid_domain* domain,
                            u32 network_id,
                            dom_domain_budget* budget,
                            dom_fluid_network_sample* out_sample)
{
    u32 cost_base;
    u32 cost_store;
    u32 cost_flow;
    u32 cost_pressure;
    q48_16 volume_total = 0;
    q48_16 capacity_total = 0;
    q48_16 pressure_total = 0;
    q48_16 contamination_total = 0;
    u32 stores_seen = 0u;
    u32 flows_seen = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_fluid_domain_is_active(domain)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_fluid_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_fluid_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (dom_fluid_network_collapsed(domain, network_id)) {
        const dom_fluid_macro_capsule* capsule = dom_fluid_find_capsule(domain, network_id);
        if (capsule) {
            out_sample->network_id = capsule->network_id;
            out_sample->store_count = capsule->store_count;
            out_sample->flow_count = capsule->flow_count;
            out_sample->volume_total = capsule->volume_total;
            out_sample->capacity_total = capsule->capacity_total;
        }
        out_sample->flags = DOM_FLUID_RESOLVE_PARTIAL;
        dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_store = dom_fluid_budget_cost(domain->policy.cost_coarse);
    cost_flow = dom_fluid_budget_cost(domain->policy.cost_medium);
    cost_pressure = dom_fluid_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, store_network)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_store)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            break;
        }
        volume_total = d_q48_16_add(volume_total, domain->stores[i].volume);
        capacity_total = d_q48_16_add(capacity_total, domain->stores[i].max_volume);
        if (domain->stores[i].volume > 0) {
            contamination_total = d_q48_16_add(contamination_total,
                                               d_q48_16_mul(domain->stores[i].volume,
                                                            d_q48_16_from_q16_16(domain->stores[i].contamination)));
        }
        stores_seen += 1u;
    }

    for (u32 i = 0u; i < domain->flow_count; ++i) {
        u32 flow_network = domain->flows[i].network_id;
        if (network_id != 0u && flow_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, flow_network)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_flow)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            break;
        }
        flows_seen += 1u;
    }

    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        const dom_fluid_pressure* pressure = &domain->pressures[i];
        int store_index = dom_fluid_find_store_index(domain, pressure->store_id);
        u32 store_network;
        if (store_index < 0) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        store_network = domain->stores[store_index].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, store_network)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_pressure)) {
            out_sample->flags |= DOM_FLUID_RESOLVE_PARTIAL;
            break;
        }
        pressure_total = d_q48_16_add(pressure_total,
                                      dom_fluid_pressure_amount(domain,
                                                                &domain->stores[store_index],
                                                                pressure));
    }

    out_sample->network_id = network_id;
    out_sample->store_count = stores_seen;
    out_sample->flow_count = flows_seen;
    out_sample->volume_total = volume_total;
    out_sample->capacity_total = capacity_total;
    out_sample->pressure_total = pressure_total;
    if (volume_total > 0) {
        out_sample->contamination_avg = dom_fluid_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(contamination_total, volume_total)));
    } else {
        out_sample->contamination_avg = 0;
    }
    dom_fluid_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                            DOM_DOMAIN_CONFIDENCE_EXACT, cost_base, budget);
    return 0;
}

int dom_fluid_resolve(dom_fluid_domain* domain,
                      u32 network_id,
                      u64 tick,
                      u64 tick_delta,
                      dom_domain_budget* budget,
                      dom_fluid_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_flow;
    u32 cost_pressure;
    q48_16 volume_leaked = 0;
    q48_16 volume_transferred = 0;
    q48_16 volume_remaining = 0;
    q48_16 energy_required = 0;
    u32 stores_seen = 0u;
    u32 flows_seen = 0u;
    u32 pressures_seen = 0u;
    u32 flags = 0u;
    d_bool cascade_active = D_FALSE;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_fluid_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_FLUID_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_fluid_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_FLUID_REFUSE_BUDGET;
        return 0;
    }

    if (dom_fluid_network_collapsed(domain, network_id)) {
        const dom_fluid_macro_capsule* capsule = dom_fluid_find_capsule(domain, network_id);
        if (capsule) {
            out_result->store_count = capsule->store_count;
            out_result->flow_count = capsule->flow_count;
            out_result->volume_remaining = capsule->volume_total;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_FLUID_RESOLVE_PARTIAL;
        return 0;
    }

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, store_network)) {
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        domain->stores[i].flags = 0u;
        if (dom_fluid_store_apply_leakage(&domain->stores[i], tick_delta, &volume_leaked)) {
            flags |= DOM_FLUID_RESOLVE_LEAKAGE;
        }
    }

    cost_flow = dom_fluid_budget_cost(domain->policy.cost_medium);
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        dom_fluid_flow* flow;
        dom_fluid_store* source;
        dom_fluid_store* sink;
        q48_16 available;
        q48_16 sink_space;
        q48_16 max_rate;
        q48_16 transfer;
        q48_16 delivered;
        q48_16 loss;
        d_bool fail_random;
        d_bool force_leak = D_FALSE;
        u32 flow_network = domain->flows[i].network_id;
        if (network_id != 0u && flow_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, flow_network)) {
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_flow)) {
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_FLUID_REFUSE_NONE) {
                out_result->refusal_reason = DOM_FLUID_REFUSE_BUDGET;
            }
            break;
        }
        flow = &domain->flows[i];
        flow->flags = 0u;
        {
            int source_index = dom_fluid_find_store_index(domain, flow->source_store_id);
            int sink_index = dom_fluid_find_store_index(domain, flow->sink_store_id);
            if (source_index < 0 || sink_index < 0) {
                flow->flags |= DOM_FLUID_FLOW_UNRESOLVED;
                flags |= DOM_FLUID_RESOLVE_PARTIAL;
                continue;
            }
            source = &domain->stores[source_index];
            sink = &domain->stores[sink_index];
        }

        max_rate = flow->max_transfer_rate;
        if (cascade_active && max_rate > 0) {
            max_rate = (q48_16)(max_rate / DOM_FLUID_CASCADE_DIVISOR);
        }
        available = source->volume;
        sink_space = d_q48_16_sub(sink->max_volume, sink->volume);
        if (sink_space < 0) {
            sink_space = 0;
        }
        transfer = dom_fluid_min_q48(max_rate, available);
        transfer = dom_fluid_min_q48(transfer, sink_space);

        if (available <= 0) {
            if (flow->failure_mode_mask & DOM_FLUID_FAILURE_BLOCKED) {
                flow->flags |= DOM_FLUID_FLOW_BLOCKED;
                flags |= DOM_FLUID_RESOLVE_BLOCKED;
            }
        }
        if (sink_space <= 0) {
            if (flow->failure_mode_mask & DOM_FLUID_FAILURE_OVERLOAD) {
                flow->flags |= DOM_FLUID_FLOW_OVERLOAD;
                flags |= DOM_FLUID_RESOLVE_OVERLOAD;
            }
        }

        {
            q48_16 source_pressure = 0;
            q48_16 sink_pressure = 0;
            int source_pressure_index = dom_fluid_find_pressure_store_index(domain, flow->source_store_id);
            int sink_pressure_index = dom_fluid_find_pressure_store_index(domain, flow->sink_store_id);
            if (source_pressure_index >= 0) {
                source_pressure = dom_fluid_pressure_amount(domain, source,
                                                            &domain->pressures[source_pressure_index]);
            }
            if (sink_pressure_index >= 0) {
                sink_pressure = dom_fluid_pressure_amount(domain, sink,
                                                          &domain->pressures[sink_pressure_index]);
            }
            if (source_pressure > 0 && sink_pressure > 0 && source_pressure < sink_pressure) {
                transfer = 0;
                flow->flags |= DOM_FLUID_FLOW_BLOCKED;
                flags |= DOM_FLUID_RESOLVE_BLOCKED;
            }
        }

        fail_random = dom_fluid_flow_failure_roll(domain, flow, tick);
        if (fail_random) {
            if (flow->failure_mode_mask & DOM_FLUID_FAILURE_BLOCKED) {
                flow->flags |= DOM_FLUID_FLOW_BLOCKED;
                flags |= DOM_FLUID_RESOLVE_BLOCKED;
                transfer = 0;
            } else if (flow->failure_mode_mask & DOM_FLUID_FAILURE_LEAKAGE) {
                flow->flags |= DOM_FLUID_FLOW_LEAKAGE;
                flags |= DOM_FLUID_RESOLVE_LEAKAGE;
                force_leak = D_TRUE;
            }
        }

        if (transfer > 0) {
            if (force_leak) {
                delivered = 0;
                loss = transfer;
            } else {
                delivered = dom_fluid_ratio_mul_q48(transfer, flow->efficiency);
                loss = d_q48_16_sub(transfer, delivered);
            }
            source->volume = d_q48_16_sub(source->volume, transfer);
            if (delivered > 0) {
                q48_16 sink_prev = sink->volume;
                sink->volume = d_q48_16_add(sink->volume, delivered);
                sink->temperature = dom_fluid_mix_q48(sink->temperature,
                                                      sink_prev,
                                                      source->temperature,
                                                      delivered);
                sink->contamination = dom_fluid_mix_q16(sink->contamination,
                                                        sink_prev,
                                                        source->contamination,
                                                        delivered);
            }
            volume_transferred = d_q48_16_add(volume_transferred, delivered);
            if (loss > 0) {
                volume_leaked = d_q48_16_add(volume_leaked, loss);
                flow->flags |= DOM_FLUID_FLOW_LEAKAGE;
                flags |= DOM_FLUID_RESOLVE_LEAKAGE;
            }
            if (flow->energy_per_volume > 0) {
                energy_required = d_q48_16_add(energy_required,
                                               d_q48_16_mul(flow->energy_per_volume, transfer));
            }
        }

        if ((flow->flags & DOM_FLUID_FLOW_BLOCKED) ||
            (flow->flags & DOM_FLUID_FLOW_OVERLOAD)) {
            if (flow->failure_mode_mask & DOM_FLUID_FAILURE_CASCADE) {
                cascade_active = D_TRUE;
                flow->flags |= DOM_FLUID_FLOW_CASCADE;
                flags |= DOM_FLUID_RESOLVE_CASCADE;
            }
        }

        flows_seen += 1u;
    }

    cost_pressure = dom_fluid_budget_cost(domain->policy.cost_coarse);
    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        dom_fluid_pressure* pressure = &domain->pressures[i];
        int store_index = dom_fluid_find_store_index(domain, pressure->store_id);
        q48_16 amount;
        q16_16 release_ratio;

        if (store_index < 0) {
            pressure->flags = DOM_FLUID_PRESSURE_UNRESOLVED;
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        {
            u32 store_network = domain->stores[store_index].network_id;
            if (network_id != 0u && store_network != network_id) {
                continue;
            }
            if (network_id == 0u && dom_fluid_network_collapsed(domain, store_network)) {
                pressure->flags = DOM_FLUID_PRESSURE_UNRESOLVED;
                flags |= DOM_FLUID_RESOLVE_PARTIAL;
                continue;
            }
        }
        if (!dom_domain_budget_consume(budget, cost_pressure)) {
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_FLUID_REFUSE_NONE) {
                out_result->refusal_reason = DOM_FLUID_REFUSE_BUDGET;
            }
            break;
        }

        pressure->flags = 0u;
        amount = dom_fluid_pressure_amount(domain, &domain->stores[store_index], pressure);
        if (pressure->pressure_limit > 0 && amount > pressure->pressure_limit) {
            pressure->flags |= DOM_FLUID_PRESSURE_OVER_LIMIT;
            out_result->pressure_over_limit_count += 1u;
            flags |= DOM_FLUID_RESOLVE_PRESSURE_OVER;
        }
        if (pressure->rupture_threshold > 0 && amount > pressure->rupture_threshold) {
            pressure->flags |= DOM_FLUID_PRESSURE_RUPTURED;
            out_result->pressure_rupture_count += 1u;
            flags |= DOM_FLUID_RESOLVE_RUPTURE;
            domain->stores[store_index].flags |= DOM_FLUID_STORE_RUPTURED;
            release_ratio = pressure->release_ratio;
            if (release_ratio <= 0) {
                release_ratio = DOM_FLUID_DEFAULT_RUPTURE_RELEASE_Q16;
            }
            {
                q48_16 leak = dom_fluid_ratio_mul_q48(domain->stores[store_index].volume, release_ratio);
                if (leak > 0) {
                    domain->stores[store_index].volume = d_q48_16_sub(domain->stores[store_index].volume,
                                                                     leak);
                    volume_leaked = d_q48_16_add(volume_leaked, leak);
                    amount = dom_fluid_pressure_amount(domain, &domain->stores[store_index], pressure);
                }
            }
        }
        pressure->amount = amount;
        pressures_seen += 1u;
    }

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_fluid_network_collapsed(domain, store_network)) {
            flags |= DOM_FLUID_RESOLVE_PARTIAL;
            continue;
        }
        volume_remaining = d_q48_16_add(volume_remaining, domain->stores[i].volume);
        stores_seen += 1u;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->store_count = stores_seen;
    out_result->flow_count = flows_seen;
    out_result->pressure_count = pressures_seen;
    out_result->volume_transferred = volume_transferred;
    out_result->volume_leaked = volume_leaked;
    out_result->volume_remaining = volume_remaining;
    out_result->energy_required = energy_required;
    return 0;
}

int dom_fluid_domain_collapse_network(dom_fluid_domain* domain, u32 network_id)
{
    dom_fluid_macro_capsule capsule;
    u32 pressure_bins[DOM_FLUID_HIST_BINS];
    u32 contamination_bins[DOM_FLUID_HIST_BINS];
    u32 pressure_seen = 0u;
    if (!domain) {
        return -1;
    }
    if (dom_fluid_network_collapsed(domain, network_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_FLUID_MAX_CAPSULES) {
        return -2;
    }
    memset(pressure_bins, 0, sizeof(pressure_bins));
    memset(contamination_bins, 0, sizeof(contamination_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)network_id;
    capsule.network_id = network_id;
    for (u32 i = 0u; i < domain->store_count; ++i) {
        q16_16 contamination = domain->stores[i].contamination;
        q48_16 leakage_rate;
        if (network_id != 0u && domain->stores[i].network_id != network_id) {
            continue;
        }
        capsule.store_count += 1u;
        capsule.volume_total = d_q48_16_add(capsule.volume_total, domain->stores[i].volume);
        capsule.capacity_total = d_q48_16_add(capsule.capacity_total, domain->stores[i].max_volume);
        contamination_bins[dom_fluid_hist_bin(contamination)] += 1u;
        leakage_rate = dom_fluid_ratio_mul_q48(domain->stores[i].max_volume,
                                               domain->stores[i].leakage_rate);
        capsule.leakage_rate_total = d_q48_16_add(capsule.leakage_rate_total, leakage_rate);
    }
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        if (network_id != 0u && domain->flows[i].network_id != network_id) {
            continue;
        }
        capsule.flow_count += 1u;
        capsule.transfer_rate_total = d_q48_16_add(capsule.transfer_rate_total,
                                                   domain->flows[i].max_transfer_rate);
    }
    for (u32 i = 0u; i < domain->pressure_count; ++i) {
        dom_fluid_pressure* pressure = &domain->pressures[i];
        int store_index = dom_fluid_find_store_index(domain, pressure->store_id);
        q48_16 amount;
        q48_16 ratio;
        if (store_index < 0) {
            continue;
        }
        if (network_id != 0u && domain->stores[store_index].network_id != network_id) {
            continue;
        }
        amount = dom_fluid_pressure_amount(domain, &domain->stores[store_index], pressure);
        if (pressure->pressure_limit > 0) {
            ratio = d_q48_16_div(amount, pressure->pressure_limit);
        } else {
            ratio = 0;
        }
        pressure_bins[dom_fluid_hist_bin(dom_fluid_clamp_ratio(d_q16_16_from_q48_16(ratio)))] += 1u;
        pressure_seen += 1u;
    }
    for (u32 b = 0u; b < DOM_FLUID_HIST_BINS; ++b) {
        capsule.pressure_ratio_hist[b] = dom_fluid_hist_bin_ratio(pressure_bins[b], pressure_seen);
        capsule.contamination_ratio_hist[b] = dom_fluid_hist_bin_ratio(contamination_bins[b],
                                                                       capsule.store_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_fluid_domain_expand_network(dom_fluid_domain* domain, u32 network_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].network_id == network_id) {
            domain->capsules[i] = domain->capsules[domain->capsule_count - 1u];
            domain->capsule_count -= 1u;
            return 0;
        }
    }
    return -2;
}

u32 dom_fluid_domain_capsule_count(const dom_fluid_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_fluid_macro_capsule* dom_fluid_domain_capsule_at(const dom_fluid_domain* domain,
                                                           u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_fluid_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
