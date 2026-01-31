/*
FILE: source/domino/world/energy_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/energy_fields
RESPONSIBILITY: Implements deterministic energy stores, flows, and event-driven resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/energy_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>

#define DOM_ENERGY_RNG_MAX 0xFFFFFFFFu
#define DOM_ENERGY_CASCADE_DIVISOR 2u
#define DOM_ENERGY_RESOLVE_COST_BASE 1u

static q48_16 dom_energy_min_q48(q48_16 a, q48_16 b)
{
    return (a < b) ? a : b;
}


static q16_16 dom_energy_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_ENERGY_RATIO_ONE_Q16) {
        return DOM_ENERGY_RATIO_ONE_Q16;
    }
    return value;
}

static void dom_energy_store_init(dom_energy_store* store)
{
    if (!store) {
        return;
    }
    memset(store, 0, sizeof(*store));
    store->energy_type = DOM_ENERGY_TYPE_UNSET;
}

static void dom_energy_flow_init(dom_energy_flow* flow)
{
    if (!flow) {
        return;
    }
    memset(flow, 0, sizeof(*flow));
    flow->efficiency = DOM_ENERGY_RATIO_ONE_Q16;
}

static int dom_energy_find_store_index(const dom_energy_domain* domain, u32 store_id)
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

static int dom_energy_find_flow_index(const dom_energy_domain* domain, u32 flow_id)
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

static d_bool dom_energy_domain_is_active(const dom_energy_domain* domain)
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

static d_bool dom_energy_network_collapsed(const dom_energy_domain* domain, u32 network_id)
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

static const dom_energy_macro_capsule* dom_energy_find_capsule(const dom_energy_domain* domain, u32 network_id)
{
    if (!domain) {
        return (const dom_energy_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].network_id == network_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_energy_macro_capsule*)0;
}

static void dom_energy_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_energy_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_energy_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_ENERGY_RESOLVE_COST_BASE : cost_units;
}

static q48_16 dom_energy_ratio_mul_q48(q48_16 value, q16_16 ratio)
{
    q16_16 clamped = dom_energy_clamp_ratio(ratio);
    return d_q48_16_mul(value, d_q48_16_from_q16_16(clamped));
}

static u32 dom_energy_ratio_to_u32(q16_16 ratio)
{
    q16_16 clamped = dom_energy_clamp_ratio(ratio);
    if (clamped <= 0) {
        return 0u;
    }
    if (clamped >= DOM_ENERGY_RATIO_ONE_Q16) {
        return DOM_ENERGY_RNG_MAX;
    }
    return (u32)(((u64)(u32)clamped * (u64)DOM_ENERGY_RNG_MAX) >> Q16_16_FRAC_BITS);
}

static d_bool dom_energy_flow_failure_roll(const dom_energy_domain* domain,
                                           const dom_energy_flow* flow,
                                           u64 tick)
{
    d_rng_state rng;
    const char* stream_name = "noise.stream.energy.flow.failure";
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
    threshold = dom_energy_ratio_to_u32(flow->failure_chance);
    return (d_rng_next_u32(&rng) <= threshold) ? D_TRUE : D_FALSE;
}

static d_bool dom_energy_store_apply_leakage(dom_energy_store* store,
                                             u64 tick_delta,
                                             q48_16* io_loss_total)
{
    q48_16 leak;
    if (!store || tick_delta == 0u || store->leakage_rate <= 0) {
        return D_FALSE;
    }
    leak = dom_energy_ratio_mul_q48(store->amount, store->leakage_rate);
    if (tick_delta > 1u) {
        leak = d_q48_16_mul(leak, d_q48_16_from_int((i64)tick_delta));
    }
    if (leak <= 0) {
        return D_FALSE;
    }
    if (leak > store->amount) {
        leak = store->amount;
    }
    store->amount = d_q48_16_sub(store->amount, leak);
    if (io_loss_total) {
        *io_loss_total = d_q48_16_add(*io_loss_total, leak);
    }
    return D_TRUE;
}

static q16_16 dom_energy_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_energy_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_energy_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_ENERGY_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_ENERGY_HIST_BINS) {
        scaled = DOM_ENERGY_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_energy_surface_desc_init(dom_energy_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->loss.dissipation_fraction = 0;
    desc->loss.destination_type = DOM_ENERGY_TYPE_THERMAL;
    desc->store_count = 0u;
    desc->flow_count = 0u;
    for (u32 i = 0u; i < DOM_ENERGY_MAX_STORES; ++i) {
        desc->stores[i].store_id = 0u;
        desc->stores[i].energy_type = DOM_ENERGY_TYPE_UNSET;
    }
    for (u32 i = 0u; i < DOM_ENERGY_MAX_FLOWS; ++i) {
        desc->flows[i].flow_id = 0u;
        desc->flows[i].efficiency = DOM_ENERGY_RATIO_ONE_Q16;
    }
}

void dom_energy_domain_init(dom_energy_domain* domain,
                            const dom_energy_surface_desc* desc)
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
    domain->store_count = (desc->store_count > DOM_ENERGY_MAX_STORES)
                            ? DOM_ENERGY_MAX_STORES
                            : desc->store_count;
    domain->flow_count = (desc->flow_count > DOM_ENERGY_MAX_FLOWS)
                            ? DOM_ENERGY_MAX_FLOWS
                            : desc->flow_count;
    for (u32 i = 0u; i < domain->store_count; ++i) {
        dom_energy_store_init(&domain->stores[i]);
        domain->stores[i].store_id = desc->stores[i].store_id;
        domain->stores[i].energy_type = desc->stores[i].energy_type;
        domain->stores[i].amount = desc->stores[i].amount;
        domain->stores[i].capacity = desc->stores[i].capacity;
        domain->stores[i].leakage_rate = desc->stores[i].leakage_rate;
        domain->stores[i].network_id = desc->stores[i].network_id;
        domain->stores[i].location = desc->stores[i].location;
    }
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        dom_energy_flow_init(&domain->flows[i]);
        domain->flows[i].flow_id = desc->flows[i].flow_id;
        domain->flows[i].network_id = desc->flows[i].network_id;
        domain->flows[i].source_store_id = desc->flows[i].source_store_id;
        domain->flows[i].sink_store_id = desc->flows[i].sink_store_id;
        domain->flows[i].max_transfer_rate = desc->flows[i].max_transfer_rate;
        domain->flows[i].efficiency = desc->flows[i].efficiency;
        domain->flows[i].latency_ticks = desc->flows[i].latency_ticks;
        domain->flows[i].failure_mode_mask = desc->flows[i].failure_mode_mask;
        domain->flows[i].failure_chance = desc->flows[i].failure_chance;
    }
    domain->capsule_count = 0u;
}

void dom_energy_domain_free(dom_energy_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->store_count = 0u;
    domain->flow_count = 0u;
    domain->capsule_count = 0u;
}

void dom_energy_domain_set_state(dom_energy_domain* domain,
                                 u32 existence_state,
                                 u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_energy_domain_set_policy(dom_energy_domain* domain,
                                  const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_energy_store_query(const dom_energy_domain* domain,
                           u32 store_id,
                           dom_domain_budget* budget,
                           dom_energy_store_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ENERGY_STORE_UNKNOWN;

    if (!dom_energy_domain_is_active(domain)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_energy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_energy_find_store_index(domain, store_id);
    if (index < 0) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_energy_network_collapsed(domain, domain->stores[index].network_id)) {
        out_sample->flags = DOM_ENERGY_STORE_COLLAPSED;
        dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        out_sample->store_id = domain->stores[index].store_id;
        out_sample->energy_type = domain->stores[index].energy_type;
        out_sample->network_id = domain->stores[index].network_id;
        return 0;
    }

    out_sample->store_id = domain->stores[index].store_id;
    out_sample->energy_type = domain->stores[index].energy_type;
    out_sample->amount = domain->stores[index].amount;
    out_sample->capacity = domain->stores[index].capacity;
    out_sample->leakage_rate = domain->stores[index].leakage_rate;
    out_sample->network_id = domain->stores[index].network_id;
    out_sample->flags = 0u;
    dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_energy_flow_query(const dom_energy_domain* domain,
                          u32 flow_id,
                          dom_domain_budget* budget,
                          dom_energy_flow_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_ENERGY_FLOW_UNKNOWN;

    if (!dom_energy_domain_is_active(domain)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_energy_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_energy_find_flow_index(domain, flow_id);
    if (index < 0) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_energy_network_collapsed(domain, domain->flows[index].network_id)) {
        out_sample->flags = DOM_ENERGY_FLOW_COLLAPSED;
        dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
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
    out_sample->flags = 0u;
    dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_energy_network_query(const dom_energy_domain* domain,
                             u32 network_id,
                             dom_domain_budget* budget,
                             dom_energy_network_sample* out_sample)
{
    u32 cost_base;
    u32 cost_store;
    u32 cost_flow;
    q48_16 loss_total = 0;
    q48_16 energy_total = 0;
    q48_16 capacity_total = 0;
    u32 stores_seen = 0u;
    u32 flows_seen = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_energy_domain_is_active(domain)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_energy_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_energy_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (dom_energy_network_collapsed(domain, network_id)) {
        const dom_energy_macro_capsule* capsule = dom_energy_find_capsule(domain, network_id);
        if (capsule) {
            out_sample->network_id = capsule->network_id;
            out_sample->store_count = capsule->store_count;
            out_sample->flow_count = capsule->flow_count;
            out_sample->energy_total = capsule->energy_total;
            out_sample->capacity_total = capsule->capacity_total;
        }
        out_sample->flags = DOM_ENERGY_RESOLVE_PARTIAL;
        dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                 DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_store = dom_energy_budget_cost(domain->policy.cost_coarse);
    cost_flow = dom_energy_budget_cost(domain->policy.cost_medium);

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_energy_network_collapsed(domain, store_network)) {
            out_sample->flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_store)) {
            out_sample->flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            break;
        }
        energy_total = d_q48_16_add(energy_total, domain->stores[i].amount);
        capacity_total = d_q48_16_add(capacity_total, domain->stores[i].capacity);
        stores_seen += 1u;
    }

    for (u32 i = 0u; i < domain->flow_count; ++i) {
        u32 flow_network = domain->flows[i].network_id;
        if (network_id != 0u && flow_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_energy_network_collapsed(domain, flow_network)) {
            out_sample->flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_flow)) {
            out_sample->flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            break;
        }
        flows_seen += 1u;
    }

    out_sample->network_id = network_id;
    out_sample->store_count = stores_seen;
    out_sample->flow_count = flows_seen;
    out_sample->energy_total = energy_total;
    out_sample->capacity_total = capacity_total;
    out_sample->loss_total = loss_total;
    dom_energy_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                             DOM_DOMAIN_CONFIDENCE_EXACT, cost_base, budget);
    return 0;
}

int dom_energy_resolve(dom_energy_domain* domain,
                       u32 network_id,
                       u64 tick,
                       u64 tick_delta,
                       dom_domain_budget* budget,
                       dom_energy_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_flow;
    q48_16 energy_lost = 0;
    q48_16 energy_transferred = 0;
    q48_16 energy_remaining = 0;
    u32 stores_seen = 0u;
    u32 flows_seen = 0u;
    u32 flags = 0u;
    d_bool cascade_active = D_FALSE;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_energy_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_ENERGY_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_energy_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_ENERGY_REFUSE_BUDGET;
        return 0;
    }

    if (dom_energy_network_collapsed(domain, network_id)) {
        const dom_energy_macro_capsule* capsule = dom_energy_find_capsule(domain, network_id);
        if (capsule) {
            out_result->store_count = capsule->store_count;
            out_result->flow_count = capsule->flow_count;
            out_result->energy_remaining = capsule->energy_total;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_ENERGY_RESOLVE_PARTIAL;
        return 0;
    }

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_energy_network_collapsed(domain, store_network)) {
            flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            continue;
        }
        if (dom_energy_store_apply_leakage(&domain->stores[i], tick_delta, &energy_lost)) {
            flags |= DOM_ENERGY_RESOLVE_LEAKAGE;
        }
    }

    cost_flow = dom_energy_budget_cost(domain->policy.cost_medium);
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        dom_energy_flow* flow;
        dom_energy_store* source;
        dom_energy_store* sink;
        q48_16 available;
        q48_16 sink_space;
        q48_16 max_rate;
        q48_16 transfer;
        q48_16 delivered;
        q48_16 loss;
        d_bool fail_random;
        u32 flow_network = domain->flows[i].network_id;
        if (network_id != 0u && flow_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_energy_network_collapsed(domain, flow_network)) {
            flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_flow)) {
            flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_ENERGY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_ENERGY_REFUSE_BUDGET;
            }
            break;
        }
        flow = &domain->flows[i];
        flow->flags = 0u;
        {
            int source_index = dom_energy_find_store_index(domain, flow->source_store_id);
            int sink_index = dom_energy_find_store_index(domain, flow->sink_store_id);
            if (source_index < 0 || sink_index < 0) {
                flow->flags |= DOM_ENERGY_FLOW_UNKNOWN;
                flags |= DOM_ENERGY_RESOLVE_PARTIAL;
                continue;
            }
            source = &domain->stores[source_index];
            sink = &domain->stores[sink_index];
        }

        max_rate = flow->max_transfer_rate;
        if (cascade_active && max_rate > 0) {
            max_rate = (q48_16)(max_rate / DOM_ENERGY_CASCADE_DIVISOR);
        }
        available = source->amount;
        sink_space = d_q48_16_sub(sink->capacity, sink->amount);
        if (sink_space < 0) {
            sink_space = 0;
        }
        transfer = dom_energy_min_q48(max_rate, available);
        transfer = dom_energy_min_q48(transfer, sink_space);

        if (available <= 0) {
            if (flow->failure_mode_mask & DOM_ENERGY_FAILURE_BLACKOUT) {
                flow->flags |= DOM_ENERGY_FLOW_BLACKOUT;
                flags |= DOM_ENERGY_RESOLVE_BLACKOUT;
            }
        } else if (available < max_rate) {
            if (flow->failure_mode_mask & DOM_ENERGY_FAILURE_BROWNOUT) {
                flow->flags |= DOM_ENERGY_FLOW_BROWNOUT;
                flags |= DOM_ENERGY_RESOLVE_BROWNOUT;
            }
        }
        if (sink_space <= 0) {
            if (flow->failure_mode_mask & DOM_ENERGY_FAILURE_OVERLOAD) {
                flow->flags |= DOM_ENERGY_FLOW_OVERLOAD;
                flags |= DOM_ENERGY_RESOLVE_OVERLOAD;
            }
        }

        fail_random = dom_energy_flow_failure_roll(domain, flow, tick);
        if (fail_random) {
            if (flow->failure_mode_mask & DOM_ENERGY_FAILURE_BLACKOUT) {
                flow->flags |= DOM_ENERGY_FLOW_BLACKOUT;
                flags |= DOM_ENERGY_RESOLVE_BLACKOUT;
            }
            transfer = 0;
        }

        if (transfer > 0) {
            delivered = dom_energy_ratio_mul_q48(transfer, flow->efficiency);
            loss = d_q48_16_sub(transfer, delivered);
            if (domain->surface.loss.dissipation_fraction > 0) {
                q48_16 extra_loss = dom_energy_ratio_mul_q48(delivered, domain->surface.loss.dissipation_fraction);
                delivered = d_q48_16_sub(delivered, extra_loss);
                loss = d_q48_16_add(loss, extra_loss);
            }
            source->amount = d_q48_16_sub(source->amount, transfer);
            sink->amount = d_q48_16_add(sink->amount, delivered);
            energy_transferred = d_q48_16_add(energy_transferred, delivered);
            if (loss > 0) {
                energy_lost = d_q48_16_add(energy_lost, loss);
                flags |= DOM_ENERGY_RESOLVE_LEAKAGE;
            }
        }

        if ((flow->flags & DOM_ENERGY_FLOW_BLACKOUT) ||
            (flow->flags & DOM_ENERGY_FLOW_BROWNOUT) ||
            (flow->flags & DOM_ENERGY_FLOW_OVERLOAD)) {
            if (flow->failure_mode_mask & DOM_ENERGY_FAILURE_CASCADE) {
                cascade_active = D_TRUE;
                flow->flags |= DOM_ENERGY_FLOW_CASCADE;
                flags |= DOM_ENERGY_RESOLVE_CASCADE;
            }
        }

        flows_seen += 1u;
    }

    for (u32 i = 0u; i < domain->store_count; ++i) {
        u32 store_network = domain->stores[i].network_id;
        if (network_id != 0u && store_network != network_id) {
            continue;
        }
        if (network_id == 0u && dom_energy_network_collapsed(domain, store_network)) {
            flags |= DOM_ENERGY_RESOLVE_PARTIAL;
            continue;
        }
        energy_remaining = d_q48_16_add(energy_remaining, domain->stores[i].amount);
        stores_seen += 1u;
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->store_count = stores_seen;
    out_result->flow_count = flows_seen;
    out_result->energy_transferred = energy_transferred;
    out_result->energy_lost = energy_lost;
    out_result->energy_remaining = energy_remaining;
    return 0;
}

int dom_energy_domain_collapse_network(dom_energy_domain* domain, u32 network_id)
{
    dom_energy_macro_capsule capsule;
    u32 hist_bins[DOM_ENERGY_HIST_BINS];
    if (!domain) {
        return -1;
    }
    if (dom_energy_network_collapsed(domain, network_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_ENERGY_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)network_id;
    capsule.network_id = network_id;
    for (u32 i = 0u; i < domain->store_count; ++i) {
        q16_16 ratio;
        if (network_id != 0u && domain->stores[i].network_id != network_id) {
            continue;
        }
        capsule.store_count += 1u;
        capsule.energy_total = d_q48_16_add(capsule.energy_total, domain->stores[i].amount);
        capsule.capacity_total = d_q48_16_add(capsule.capacity_total, domain->stores[i].capacity);
        ratio = 0;
        if (domain->stores[i].capacity > 0) {
            q48_16 r48 = d_q48_16_div(domain->stores[i].amount, domain->stores[i].capacity);
            ratio = dom_energy_clamp_ratio(d_q16_16_from_q48_16(r48));
        }
        hist_bins[dom_energy_hist_bin(ratio)] += 1u;
    }
    for (u32 i = 0u; i < domain->flow_count; ++i) {
        if (network_id != 0u && domain->flows[i].network_id != network_id) {
            continue;
        }
        capsule.flow_count += 1u;
        capsule.transfer_rate_total = d_q48_16_add(capsule.transfer_rate_total,
                                                   domain->flows[i].max_transfer_rate);
    }
    for (u32 b = 0u; b < DOM_ENERGY_HIST_BINS; ++b) {
        capsule.energy_ratio_hist[b] = dom_energy_hist_bin_ratio(hist_bins[b], capsule.store_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_energy_domain_expand_network(dom_energy_domain* domain, u32 network_id)
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

u32 dom_energy_domain_capsule_count(const dom_energy_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_energy_macro_capsule* dom_energy_domain_capsule_at(const dom_energy_domain* domain,
                                                             u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_energy_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
