/*
FILE: source/domino/world/information_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/information_fields
RESPONSIBILITY: Implements deterministic information networks, routing, and event-driven resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/information_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>

#define DOM_INFO_RNG_MAX 0xFFFFFFFFu
#define DOM_INFO_RESOLVE_COST_BASE 1u

#define DOM_INFO_LAT_TICKS_IMMEDIATE 1u
#define DOM_INFO_LAT_TICKS_LOCAL 4u
#define DOM_INFO_LAT_TICKS_REGIONAL 16u
#define DOM_INFO_LAT_TICKS_ORBITAL 64u
#define DOM_INFO_LAT_TICKS_INTERPLANETARY 256u

static q16_16 dom_info_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_INFO_RATIO_ONE_Q16) {
        return DOM_INFO_RATIO_ONE_Q16;
    }
    return value;
}

static void dom_info_capacity_init(dom_info_capacity* capacity)
{
    if (!capacity) {
        return;
    }
    memset(capacity, 0, sizeof(*capacity));
}

static void dom_info_node_init(dom_info_node* node)
{
    if (!node) {
        return;
    }
    memset(node, 0, sizeof(*node));
    node->node_type = DOM_INFO_NODE_UNSET;
}

static void dom_info_link_init(dom_info_link* link)
{
    if (!link) {
        return;
    }
    memset(link, 0, sizeof(*link));
    link->direction = DOM_INFO_LINK_BIDIR;
}

static void dom_info_data_init(dom_info_data* data)
{
    if (!data) {
        return;
    }
    memset(data, 0, sizeof(*data));
    data->data_type = DOM_INFO_DATA_UNSET;
    data->flags = DOM_INFO_DATA_FLAG_PENDING;
}

static int dom_info_find_capacity_index(const dom_info_domain* domain, u32 capacity_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->capacity_count; ++i) {
        if (domain->capacities[i].capacity_id == capacity_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_info_find_node_index(const dom_info_domain* domain, u32 node_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->node_count; ++i) {
        if (domain->nodes[i].node_id == node_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_info_find_link_index(const dom_info_domain* domain, u32 link_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->link_count; ++i) {
        if (domain->links[i].link_id == link_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_info_find_data_index(const dom_info_domain* domain, u32 data_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->data_count; ++i) {
        if (domain->data[i].data_id == data_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_info_find_link_for_nodes(const dom_info_domain* domain,
                                        u32 source_node_id,
                                        u32 sink_node_id,
                                        u32 network_id)
{
    if (!domain || source_node_id == 0u || sink_node_id == 0u) {
        return -1;
    }
    for (u32 i = 0u; i < domain->link_count; ++i) {
        const dom_info_link* link = &domain->links[i];
        if (network_id != 0u && link->network_id != network_id) {
            continue;
        }
        if (link->direction == DOM_INFO_LINK_BIDIR) {
            if ((link->node_a_id == source_node_id && link->node_b_id == sink_node_id) ||
                (link->node_b_id == source_node_id && link->node_a_id == sink_node_id)) {
                return (int)i;
            }
        } else if (link->direction == DOM_INFO_LINK_A_TO_B) {
            if (link->node_a_id == source_node_id && link->node_b_id == sink_node_id) {
                return (int)i;
            }
        } else if (link->direction == DOM_INFO_LINK_B_TO_A) {
            if (link->node_b_id == source_node_id && link->node_a_id == sink_node_id) {
                return (int)i;
            }
        }
    }
    return -1;
}

static d_bool dom_info_domain_is_active(const dom_info_domain* domain)
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

static d_bool dom_info_network_collapsed(const dom_info_domain* domain, u32 network_id)
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

static const dom_info_macro_capsule* dom_info_find_capsule(const dom_info_domain* domain,
                                                           u32 network_id)
{
    if (!domain) {
        return (const dom_info_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].network_id == network_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_info_macro_capsule*)0;
}

static void dom_info_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_info_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_info_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_INFO_RESOLVE_COST_BASE : cost_units;
}

static u32 dom_info_ratio_to_u32(q16_16 ratio)
{
    q16_16 clamped = dom_info_clamp_ratio(ratio);
    if (clamped <= 0) {
        return 0u;
    }
    if (clamped >= DOM_INFO_RATIO_ONE_Q16) {
        return DOM_INFO_RNG_MAX;
    }
    return (u32)(((u64)(u32)clamped * (u64)DOM_INFO_RNG_MAX) >> Q16_16_FRAC_BITS);
}

static u64 dom_info_latency_ticks(u32 latency_class)
{
    switch (latency_class) {
        case DOM_INFO_LATENCY_IMMEDIATE: return DOM_INFO_LAT_TICKS_IMMEDIATE;
        case DOM_INFO_LATENCY_LOCAL: return DOM_INFO_LAT_TICKS_LOCAL;
        case DOM_INFO_LATENCY_REGIONAL: return DOM_INFO_LAT_TICKS_REGIONAL;
        case DOM_INFO_LATENCY_ORBITAL: return DOM_INFO_LAT_TICKS_ORBITAL;
        case DOM_INFO_LATENCY_INTERPLANETARY: return DOM_INFO_LAT_TICKS_INTERPLANETARY;
        default: return DOM_INFO_LAT_TICKS_LOCAL;
    }
}

static d_bool dom_info_error_roll(const dom_info_domain* domain,
                                  const dom_info_link* link,
                                  const dom_info_data* data,
                                  q16_16 error_rate,
                                  u64 tick)
{
    d_rng_state rng;
    const char* stream_name = "noise.stream.signal.data.error";
    u32 threshold;
    if (!domain || !link || !data) {
        return D_FALSE;
    }
    if (error_rate <= 0) {
        return D_FALSE;
    }
    D_DET_GUARD_RNG_STREAM_NAME(stream_name);
    d_rng_state_from_context(&rng,
                             domain->surface.world_seed,
                             domain->surface.domain_id,
                             (u64)link->link_id ^ (u64)data->data_id,
                             tick,
                             stream_name,
                             D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM);
    threshold = dom_info_ratio_to_u32(error_rate);
    return (d_rng_next_u32(&rng) <= threshold) ? D_TRUE : D_FALSE;
}

static q16_16 dom_info_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_info_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_info_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_INFO_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_INFO_HIST_BINS) {
        scaled = DOM_INFO_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_info_surface_desc_init(dom_info_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->capacity_count = 0u;
    desc->node_count = 0u;
    desc->link_count = 0u;
    desc->data_count = 0u;
    for (u32 i = 0u; i < DOM_INFO_MAX_CAPACITY_PROFILES; ++i) {
        desc->capacities[i].capacity_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INFO_MAX_NODES; ++i) {
        desc->nodes[i].node_id = 0u;
        desc->nodes[i].node_type = DOM_INFO_NODE_UNSET;
    }
    for (u32 i = 0u; i < DOM_INFO_MAX_LINKS; ++i) {
        desc->links[i].link_id = 0u;
    }
    for (u32 i = 0u; i < DOM_INFO_MAX_DATA; ++i) {
        desc->data[i].data_id = 0u;
    }
}

void dom_info_domain_init(dom_info_domain* domain,
                          const dom_info_surface_desc* desc)
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
    domain->capacity_count = (desc->capacity_count > DOM_INFO_MAX_CAPACITY_PROFILES)
                                ? DOM_INFO_MAX_CAPACITY_PROFILES
                                : desc->capacity_count;
    domain->node_count = (desc->node_count > DOM_INFO_MAX_NODES)
                                ? DOM_INFO_MAX_NODES
                                : desc->node_count;
    domain->link_count = (desc->link_count > DOM_INFO_MAX_LINKS)
                                ? DOM_INFO_MAX_LINKS
                                : desc->link_count;
    domain->data_count = (desc->data_count > DOM_INFO_MAX_DATA)
                                ? DOM_INFO_MAX_DATA
                                : desc->data_count;

    for (u32 i = 0u; i < domain->capacity_count; ++i) {
        dom_info_capacity_init(&domain->capacities[i]);
        domain->capacities[i].capacity_id = desc->capacities[i].capacity_id;
        domain->capacities[i].bandwidth_limit = desc->capacities[i].bandwidth_limit;
        domain->capacities[i].latency_class = desc->capacities[i].latency_class;
        domain->capacities[i].error_rate = desc->capacities[i].error_rate;
        domain->capacities[i].congestion_policy = desc->capacities[i].congestion_policy;
    }
    for (u32 i = 0u; i < domain->node_count; ++i) {
        dom_info_node_init(&domain->nodes[i]);
        domain->nodes[i].node_id = desc->nodes[i].node_id;
        domain->nodes[i].node_type = desc->nodes[i].node_type;
        domain->nodes[i].compute_capacity = desc->nodes[i].compute_capacity;
        domain->nodes[i].storage_capacity = desc->nodes[i].storage_capacity;
        domain->nodes[i].energy_per_unit = desc->nodes[i].energy_per_unit;
        domain->nodes[i].heat_per_unit = desc->nodes[i].heat_per_unit;
        domain->nodes[i].network_id = desc->nodes[i].network_id;
        domain->nodes[i].location = desc->nodes[i].location;
    }
    for (u32 i = 0u; i < domain->link_count; ++i) {
        dom_info_link_init(&domain->links[i]);
        domain->links[i].link_id = desc->links[i].link_id;
        domain->links[i].network_id = desc->links[i].network_id;
        domain->links[i].node_a_id = desc->links[i].node_a_id;
        domain->links[i].node_b_id = desc->links[i].node_b_id;
        domain->links[i].capacity_id = desc->links[i].capacity_id;
        domain->links[i].direction = desc->links[i].direction;
    }
    for (u32 i = 0u; i < domain->data_count; ++i) {
        dom_info_data_init(&domain->data[i]);
        domain->data[i].data_id = desc->data[i].data_id;
        domain->data[i].data_type = desc->data[i].data_type;
        domain->data[i].data_size = desc->data[i].data_size;
        domain->data[i].data_uncertainty = dom_info_clamp_ratio(desc->data[i].data_uncertainty);
        domain->data[i].source_node_id = desc->data[i].source_node_id;
        domain->data[i].sink_node_id = desc->data[i].sink_node_id;
        domain->data[i].protocol_id = desc->data[i].protocol_id;
        domain->data[i].network_id = desc->data[i].network_id;
        domain->data[i].send_tick = desc->data[i].send_tick;
    }
    domain->capsule_count = 0u;
}

void dom_info_domain_free(dom_info_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->capacity_count = 0u;
    domain->node_count = 0u;
    domain->link_count = 0u;
    domain->data_count = 0u;
    domain->capsule_count = 0u;
}

void dom_info_domain_set_state(dom_info_domain* domain,
                               u32 existence_state,
                               u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_info_domain_set_policy(dom_info_domain* domain,
                                const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_info_capacity_query(const dom_info_domain* domain,
                            u32 capacity_id,
                            dom_domain_budget* budget,
                            dom_info_capacity_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_info_domain_is_active(domain)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_info_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_info_find_capacity_index(domain, capacity_id);
    if (index < 0) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    out_sample->capacity_id = domain->capacities[index].capacity_id;
    out_sample->bandwidth_limit = domain->capacities[index].bandwidth_limit;
    out_sample->latency_class = domain->capacities[index].latency_class;
    out_sample->error_rate = domain->capacities[index].error_rate;
    out_sample->congestion_policy = domain->capacities[index].congestion_policy;
    out_sample->flags = domain->capacities[index].flags;
    dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_info_node_query(const dom_info_domain* domain,
                        u32 node_id,
                        dom_domain_budget* budget,
                        dom_info_node_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_info_domain_is_active(domain)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_info_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_info_find_node_index(domain, node_id);
    if (index < 0) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_info_network_collapsed(domain, domain->nodes[index].network_id)) {
        out_sample->flags = DOM_INFO_NODE_FLAG_COLLAPSED;
        out_sample->node_id = domain->nodes[index].node_id;
        out_sample->node_type = domain->nodes[index].node_type;
        out_sample->network_id = domain->nodes[index].network_id;
        dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->node_id = domain->nodes[index].node_id;
    out_sample->node_type = domain->nodes[index].node_type;
    out_sample->compute_capacity = domain->nodes[index].compute_capacity;
    out_sample->storage_capacity = domain->nodes[index].storage_capacity;
    out_sample->storage_used = domain->nodes[index].storage_used;
    out_sample->energy_per_unit = domain->nodes[index].energy_per_unit;
    out_sample->heat_per_unit = domain->nodes[index].heat_per_unit;
    out_sample->network_id = domain->nodes[index].network_id;
    out_sample->flags = domain->nodes[index].flags;
    dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_info_link_query(const dom_info_domain* domain,
                        u32 link_id,
                        dom_domain_budget* budget,
                        dom_info_link_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_info_domain_is_active(domain)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_info_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_info_find_link_index(domain, link_id);
    if (index < 0) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_info_network_collapsed(domain, domain->links[index].network_id)) {
        out_sample->flags = DOM_INFO_LINK_FLAG_COLLAPSED;
        out_sample->link_id = domain->links[index].link_id;
        out_sample->network_id = domain->links[index].network_id;
        dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->link_id = domain->links[index].link_id;
    out_sample->network_id = domain->links[index].network_id;
    out_sample->node_a_id = domain->links[index].node_a_id;
    out_sample->node_b_id = domain->links[index].node_b_id;
    out_sample->capacity_id = domain->links[index].capacity_id;
    out_sample->direction = domain->links[index].direction;
    out_sample->flags = domain->links[index].flags;
    dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_info_data_query(const dom_info_domain* domain,
                        u32 data_id,
                        dom_domain_budget* budget,
                        dom_info_data_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_info_domain_is_active(domain)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_info_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_info_find_data_index(domain, data_id);
    if (index < 0) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_info_network_collapsed(domain, domain->data[index].network_id)) {
        out_sample->flags = DOM_INFO_DATA_FLAG_QUEUED;
        out_sample->data_id = domain->data[index].data_id;
        out_sample->data_type = domain->data[index].data_type;
        out_sample->network_id = domain->data[index].network_id;
        dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->data_id = domain->data[index].data_id;
    out_sample->data_type = domain->data[index].data_type;
    out_sample->data_size = domain->data[index].data_size;
    out_sample->data_uncertainty = domain->data[index].data_uncertainty;
    out_sample->source_node_id = domain->data[index].source_node_id;
    out_sample->sink_node_id = domain->data[index].sink_node_id;
    out_sample->protocol_id = domain->data[index].protocol_id;
    out_sample->network_id = domain->data[index].network_id;
    out_sample->send_tick = domain->data[index].send_tick;
    out_sample->flags = domain->data[index].flags;
    dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_info_network_query(const dom_info_domain* domain,
                           u32 network_id,
                           dom_domain_budget* budget,
                           dom_info_network_sample* out_sample)
{
    u32 cost_base;
    u32 cost_node;
    u32 cost_link;
    u32 cost_data;
    u32 nodes_seen = 0u;
    u32 links_seen = 0u;
    u32 data_seen = 0u;
    u32 queued_count = 0u;
    u32 dropped_count = 0u;
    q48_16 data_total = 0;
    q16_16 error_rate_sum = 0;
    u32 error_rate_count = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_info_domain_is_active(domain)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_info_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_info_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (dom_info_network_collapsed(domain, network_id)) {
        const dom_info_macro_capsule* capsule = dom_info_find_capsule(domain, network_id);
        if (capsule) {
            out_sample->network_id = capsule->network_id;
            out_sample->node_count = capsule->node_count;
            out_sample->link_count = capsule->link_count;
            out_sample->data_count = capsule->data_count;
            out_sample->data_total = capsule->data_total;
        }
        out_sample->flags = DOM_INFO_RESOLVE_PARTIAL;
        dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_node = dom_info_budget_cost(domain->policy.cost_coarse);
    cost_link = dom_info_budget_cost(domain->policy.cost_coarse);
    cost_data = dom_info_budget_cost(domain->policy.cost_medium);

    for (u32 i = 0u; i < domain->node_count; ++i) {
        if (network_id != 0u && domain->nodes[i].network_id != network_id) {
            continue;
        }
        if (network_id == 0u && dom_info_network_collapsed(domain, domain->nodes[i].network_id)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_node)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            break;
        }
        nodes_seen += 1u;
    }

    for (u32 i = 0u; i < domain->link_count; ++i) {
        if (network_id != 0u && domain->links[i].network_id != network_id) {
            continue;
        }
        if (network_id == 0u && dom_info_network_collapsed(domain, domain->links[i].network_id)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_link)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            break;
        }
        links_seen += 1u;
        {
            int cap_index = dom_info_find_capacity_index(domain, domain->links[i].capacity_id);
            if (cap_index >= 0) {
                error_rate_sum = d_q16_16_add(error_rate_sum, domain->capacities[cap_index].error_rate);
                error_rate_count += 1u;
            }
        }
    }

    for (u32 i = 0u; i < domain->data_count; ++i) {
        const dom_info_data* data = &domain->data[i];
        if (network_id != 0u && data->network_id != network_id) {
            continue;
        }
        if (network_id == 0u && dom_info_network_collapsed(domain, data->network_id)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_data)) {
            out_sample->flags |= DOM_INFO_RESOLVE_PARTIAL;
            break;
        }
        data_seen += 1u;
        data_total = d_q48_16_add(data_total, data->data_size);
        if (data->flags & DOM_INFO_DATA_FLAG_QUEUED) {
            queued_count += 1u;
        }
        if (data->flags & DOM_INFO_DATA_FLAG_DROPPED) {
            dropped_count += 1u;
        }
    }

    out_sample->network_id = network_id;
    out_sample->node_count = nodes_seen;
    out_sample->link_count = links_seen;
    out_sample->data_count = data_seen;
    out_sample->data_total = data_total;
    out_sample->queued_count = queued_count;
    out_sample->dropped_count = dropped_count;
    if (error_rate_count > 0u) {
        out_sample->error_rate_avg = (q16_16)(error_rate_sum / (i32)error_rate_count);
    }
    dom_info_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                           DOM_DOMAIN_CONFIDENCE_EXACT, cost_base, budget);
    return 0;
}

int dom_info_resolve(dom_info_domain* domain,
                     u32 network_id,
                     u64 tick,
                     u64 tick_delta,
                     dom_domain_budget* budget,
                     dom_info_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_link;
    u32 cost_data;
    u32 flags = 0u;
    u32 delivered = 0u;
    u32 dropped = 0u;
    u32 queued = 0u;
    q48_16 energy_total = 0;
    q48_16 heat_total = 0;
    q48_16 link_bandwidth[DOM_INFO_MAX_LINKS];
    q48_16 compute_used[DOM_INFO_MAX_NODES];
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));
    memset(link_bandwidth, 0, sizeof(link_bandwidth));
    memset(compute_used, 0, sizeof(compute_used));

    if (!dom_info_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_INFO_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_info_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_INFO_REFUSE_BUDGET;
        return 0;
    }

    if (dom_info_network_collapsed(domain, network_id)) {
        const dom_info_macro_capsule* capsule = dom_info_find_capsule(domain, network_id);
        if (capsule) {
            out_result->delivered_count = capsule->data_count;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_INFO_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_link = dom_info_budget_cost(domain->policy.cost_medium);
    for (u32 i = 0u; i < domain->link_count; ++i) {
        dom_info_link* link = &domain->links[i];
        q48_16 bandwidth;
        if (network_id != 0u && link->network_id != network_id) {
            continue;
        }
        if (network_id == 0u && dom_info_network_collapsed(domain, link->network_id)) {
            flags |= DOM_INFO_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_link)) {
            flags |= DOM_INFO_RESOLVE_PARTIAL;
            out_result->refusal_reason = DOM_INFO_REFUSE_BUDGET;
            break;
        }
        link->flags = 0u;
        bandwidth = 0;
        {
            int cap_index = dom_info_find_capacity_index(domain, link->capacity_id);
            if (cap_index >= 0) {
                bandwidth = domain->capacities[cap_index].bandwidth_limit;
                if (tick_delta > 1u && bandwidth > 0) {
                    bandwidth = d_q48_16_mul(bandwidth, d_q48_16_from_int((i64)tick_delta));
                }
                if (bandwidth <= 0) {
                    link->flags |= DOM_INFO_LINK_FLAG_OUTAGE;
                    flags |= DOM_INFO_RESOLVE_OUTAGE;
                }
            } else {
                link->flags |= DOM_INFO_LINK_FLAG_OUTAGE;
                flags |= DOM_INFO_RESOLVE_OUTAGE;
            }
        }
        link_bandwidth[i] = bandwidth;
    }

    cost_data = dom_info_budget_cost(domain->policy.cost_coarse);
    for (u32 i = 0u; i < domain->data_count; ++i) {
        dom_info_data* data = &domain->data[i];
        int link_index;
        dom_info_link* link;
        dom_info_capacity* capacity;
        int cap_index;
        dom_info_node* source_node;
        dom_info_node* sink_node;
        q48_16 bandwidth_remaining;
        u64 latency_ticks;
        q48_16 compute_cap;
        q48_16 compute_next;
        d_bool corrupt = D_FALSE;

        if (network_id != 0u && data->network_id != network_id) {
            continue;
        }
        if (data->flags & (DOM_INFO_DATA_FLAG_DELIVERED | DOM_INFO_DATA_FLAG_DROPPED)) {
            continue;
        }

        if (!dom_domain_budget_consume(budget, cost_data)) {
            flags |= DOM_INFO_RESOLVE_PARTIAL;
            out_result->refusal_reason = DOM_INFO_REFUSE_BUDGET;
            break;
        }

        if (data->send_tick > tick) {
            data->flags |= DOM_INFO_DATA_FLAG_QUEUED;
            queued += 1u;
            continue;
        }

        link_index = dom_info_find_link_for_nodes(domain, data->source_node_id, data->sink_node_id,
                                                  (network_id != 0u) ? network_id : data->network_id);
        if (link_index < 0) {
            data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
            data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
            dropped += 1u;
            flags |= DOM_INFO_RESOLVE_DROPPED;
            continue;
        }
        link = &domain->links[link_index];
        cap_index = dom_info_find_capacity_index(domain, link->capacity_id);
        if (cap_index < 0) {
            data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
            data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
            dropped += 1u;
            flags |= DOM_INFO_RESOLVE_DROPPED;
            continue;
        }
        capacity = &domain->capacities[cap_index];

        latency_ticks = dom_info_latency_ticks(capacity->latency_class);
        if (tick < data->send_tick + latency_ticks) {
            data->flags |= DOM_INFO_DATA_FLAG_QUEUED;
            queued += 1u;
            continue;
        }

        {
            int source_index = dom_info_find_node_index(domain, data->source_node_id);
            int sink_index = dom_info_find_node_index(domain, data->sink_node_id);
            if (source_index < 0 || sink_index < 0) {
                data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
                data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
                dropped += 1u;
                flags |= DOM_INFO_RESOLVE_DROPPED;
                continue;
            }
            source_node = &domain->nodes[source_index];
            sink_node = &domain->nodes[sink_index];
        }

        compute_cap = sink_node->compute_capacity;
        if (compute_cap > 0) {
            compute_next = d_q48_16_add(compute_used[(u32)(sink_node - domain->nodes)], data->data_size);
            if (compute_next > compute_cap) {
                if (capacity->congestion_policy == DOM_INFO_CONGESTION_QUEUE) {
                    data->flags |= DOM_INFO_DATA_FLAG_QUEUED;
                    queued += 1u;
                    flags |= DOM_INFO_RESOLVE_CONGESTED;
                    link->flags |= DOM_INFO_LINK_FLAG_CONGESTED;
                    continue;
                }
                if (capacity->congestion_policy == DOM_INFO_CONGESTION_DEGRADE) {
                    data->flags |= DOM_INFO_DATA_FLAG_CORRUPT;
                    flags |= DOM_INFO_RESOLVE_CORRUPT;
                } else {
                    data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
                    data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
                    dropped += 1u;
                    flags |= DOM_INFO_RESOLVE_DROPPED;
                    link->flags |= DOM_INFO_LINK_FLAG_CONGESTED;
                    continue;
                }
            } else {
                compute_used[(u32)(sink_node - domain->nodes)] = compute_next;
            }
        }

        bandwidth_remaining = link_bandwidth[link_index];
        if (bandwidth_remaining < data->data_size) {
            if (capacity->congestion_policy == DOM_INFO_CONGESTION_QUEUE) {
                data->flags |= DOM_INFO_DATA_FLAG_QUEUED;
                queued += 1u;
                flags |= DOM_INFO_RESOLVE_CONGESTED;
                link->flags |= DOM_INFO_LINK_FLAG_CONGESTED;
                continue;
            }
            if (capacity->congestion_policy == DOM_INFO_CONGESTION_DEGRADE && bandwidth_remaining > 0) {
                data->flags |= DOM_INFO_DATA_FLAG_CORRUPT;
                flags |= DOM_INFO_RESOLVE_CORRUPT;
                link_bandwidth[link_index] = 0;
            } else {
                data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
                data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
                dropped += 1u;
                flags |= DOM_INFO_RESOLVE_DROPPED;
                link->flags |= DOM_INFO_LINK_FLAG_CONGESTED;
                continue;
            }
        } else {
            link_bandwidth[link_index] = d_q48_16_sub(bandwidth_remaining, data->data_size);
        }

        if (capacity->error_rate > 0) {
            corrupt = dom_info_error_roll(domain, link, data, capacity->error_rate, tick);
            if (corrupt) {
                data->flags |= DOM_INFO_DATA_FLAG_CORRUPT;
                if (capacity->error_rate > data->data_uncertainty) {
                    data->data_uncertainty = dom_info_clamp_ratio(capacity->error_rate);
                }
                flags |= DOM_INFO_RESOLVE_CORRUPT;
                link->flags |= DOM_INFO_LINK_FLAG_CORRUPT;
            }
        }

        if (data->data_type == DOM_INFO_DATA_STORAGE) {
            if (sink_node->storage_capacity > 0) {
                q48_16 storage_next = d_q48_16_add(sink_node->storage_used, data->data_size);
                if (storage_next > sink_node->storage_capacity) {
                    if (capacity->congestion_policy == DOM_INFO_CONGESTION_QUEUE) {
                        data->flags |= DOM_INFO_DATA_FLAG_QUEUED;
                        queued += 1u;
                        flags |= DOM_INFO_RESOLVE_CONGESTED;
                        continue;
                    }
                    data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
                    data->flags |= DOM_INFO_DATA_FLAG_DROPPED;
                    dropped += 1u;
                    flags |= DOM_INFO_RESOLVE_DROPPED;
                    continue;
                }
                sink_node->storage_used = storage_next;
            }
            data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
            data->flags |= DOM_INFO_DATA_FLAG_STORED;
        } else {
            data->flags &= ~DOM_INFO_DATA_FLAG_QUEUED;
            data->flags |= DOM_INFO_DATA_FLAG_DELIVERED;
        }

        delivered += 1u;
        energy_total = d_q48_16_add(energy_total,
                                    d_q48_16_mul(data->data_size, source_node->energy_per_unit));
        energy_total = d_q48_16_add(energy_total,
                                    d_q48_16_mul(data->data_size, sink_node->energy_per_unit));
        heat_total = d_q48_16_add(heat_total,
                                  d_q48_16_mul(data->data_size, source_node->heat_per_unit));
        heat_total = d_q48_16_add(heat_total,
                                  d_q48_16_mul(data->data_size, sink_node->heat_per_unit));
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->delivered_count = delivered;
    out_result->dropped_count = dropped;
    out_result->queued_count = queued;
    out_result->energy_cost_total = energy_total;
    out_result->heat_generated_total = heat_total;
    return 0;
}

int dom_info_domain_collapse_network(dom_info_domain* domain, u32 network_id)
{
    dom_info_macro_capsule capsule;
    u32 hist_bins[DOM_INFO_HIST_BINS];
    if (!domain) {
        return -1;
    }
    if (dom_info_network_collapsed(domain, network_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_INFO_MAX_CAPSULES) {
        return -2;
    }
    memset(hist_bins, 0, sizeof(hist_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)network_id;
    capsule.network_id = network_id;

    for (u32 i = 0u; i < domain->node_count; ++i) {
        if (network_id != 0u && domain->nodes[i].network_id != network_id) {
            continue;
        }
        capsule.node_count += 1u;
    }
    for (u32 i = 0u; i < domain->link_count; ++i) {
        if (network_id != 0u && domain->links[i].network_id != network_id) {
            continue;
        }
        capsule.link_count += 1u;
        {
            int cap_index = dom_info_find_capacity_index(domain, domain->links[i].capacity_id);
            if (cap_index >= 0) {
                hist_bins[dom_info_hist_bin(domain->capacities[cap_index].error_rate)] += 1u;
            }
        }
    }
    for (u32 i = 0u; i < domain->data_count; ++i) {
        if (network_id != 0u && domain->data[i].network_id != network_id) {
            continue;
        }
        capsule.data_count += 1u;
        capsule.data_total = d_q48_16_add(capsule.data_total, domain->data[i].data_size);
    }
    for (u32 b = 0u; b < DOM_INFO_HIST_BINS; ++b) {
        capsule.error_rate_hist[b] = dom_info_hist_bin_ratio(hist_bins[b], capsule.link_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_info_domain_expand_network(dom_info_domain* domain, u32 network_id)
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

u32 dom_info_domain_capsule_count(const dom_info_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_info_macro_capsule* dom_info_domain_capsule_at(const dom_info_domain* domain,
                                                         u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_info_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
