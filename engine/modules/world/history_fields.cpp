/*
FILE: source/domino/world/history_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/history_fields
RESPONSIBILITY: Implements deterministic history and civilization graph resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/history_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_HISTORY_RESOLVE_COST_BASE 1u
#define DOM_HISTORY_HALF_Q16 ((q16_16)0x00008000)

static q16_16 dom_history_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_HISTORY_RATIO_ONE_Q16) {
        return DOM_HISTORY_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_history_add_clamped(q16_16 a, q16_16 b)
{
    q16_16 sum = d_q16_16_add(a, b);
    return dom_history_clamp_ratio(sum);
}

static q16_16 dom_history_sub_clamped(q16_16 a, q16_16 b)
{
    q16_16 diff = d_q16_16_sub(a, b);
    return dom_history_clamp_ratio(diff);
}

static void dom_history_source_init(dom_history_source* source)
{
    if (!source) {
        return;
    }
    memset(source, 0, sizeof(*source));
    source->source_type = DOM_HISTORY_SOURCE_UNSET;
}

static void dom_history_event_init(dom_history_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->event_role = DOM_HISTORY_ROLE_UNSET;
    event->category = DOM_HISTORY_EVENT_UNSET;
    event->process_type = DOM_HISTORY_PROCESS_UNSET;
}

static void dom_history_epoch_init(dom_history_epoch* epoch)
{
    if (!epoch) {
        return;
    }
    memset(epoch, 0, sizeof(*epoch));
    epoch->epoch_type = DOM_HISTORY_EPOCH_UNSET;
}

static void dom_civilization_graph_init(dom_civilization_graph* graph)
{
    if (!graph) {
        return;
    }
    memset(graph, 0, sizeof(*graph));
}

static void dom_civilization_node_init(dom_civilization_node* node)
{
    if (!node) {
        return;
    }
    memset(node, 0, sizeof(*node));
}

static void dom_civilization_edge_init(dom_civilization_edge* edge)
{
    if (!edge) {
        return;
    }
    memset(edge, 0, sizeof(*edge));
    edge->edge_type = DOM_CIV_EDGE_UNSET;
}

static int dom_history_find_source_index(const dom_history_domain* domain, u32 source_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->source_count; ++i) {
        if (domain->sources[i].source_id == source_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_history_find_event_index(const dom_history_domain* domain, u32 event_id)
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

static int dom_history_find_epoch_index(const dom_history_domain* domain, u32 epoch_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->epoch_count; ++i) {
        if (domain->epochs[i].epoch_id == epoch_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_history_find_graph_index(const dom_history_domain* domain, u32 graph_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->graph_count; ++i) {
        if (domain->graphs[i].graph_id == graph_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_history_find_node_index(const dom_history_domain* domain, u32 node_id)
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

static int dom_history_find_edge_index(const dom_history_domain* domain, u32 edge_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->edge_count; ++i) {
        if (domain->edges[i].edge_id == edge_id) {
            return (int)i;
        }
    }
    return -1;
}

static d_bool dom_history_domain_is_active(const dom_history_domain* domain)
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

static d_bool dom_history_region_collapsed(const dom_history_domain* domain, u32 region_id)
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

static const dom_history_macro_capsule* dom_history_find_capsule(const dom_history_domain* domain,
                                                                 u32 region_id)
{
    if (!domain) {
        return (const dom_history_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_history_macro_capsule*)0;
}

static void dom_history_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_history_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_history_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_HISTORY_RESOLVE_COST_BASE : cost_units;
}

static d_bool dom_history_apply_decay(dom_history_event* event, u64 tick_delta)
{
    q16_16 decay_per_tick;
    q48_16 decay_total;
    q16_16 decay_q16;
    if (!event || tick_delta == 0u) {
        return D_FALSE;
    }
    if (event->decay_rate <= 0 || event->confidence <= 0) {
        return D_FALSE;
    }
    decay_per_tick = d_q16_16_mul(event->confidence, event->decay_rate);
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
    event->confidence = dom_history_sub_clamped(event->confidence, decay_q16);
    event->uncertainty = dom_history_add_clamped(event->uncertainty, decay_q16);
    return D_TRUE;
}

static d_bool dom_history_apply_process(dom_history_domain* domain,
                                        dom_history_event* process_event,
                                        u64 tick,
                                        q48_16* confidence_total,
                                        q48_16* uncertainty_total,
                                        q48_16* bias_total,
                                        u32* out_flags)
{
    int target_index;
    dom_history_event* target;
    q16_16 delta_confidence;
    q16_16 delta_uncertainty;
    q16_16 delta_bias;
    q16_16 confidence_before;
    q16_16 uncertainty_before;
    q16_16 bias_before;
    if (!domain || !process_event) {
        return D_FALSE;
    }
    if (process_event->event_role != DOM_HISTORY_ROLE_PROCESS) {
        return D_FALSE;
    }
    if (process_event->flags & DOM_HISTORY_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (process_event->start_tick > tick) {
        return D_FALSE;
    }
    if (process_event->target_event_id == 0u) {
        return D_FALSE;
    }
    target_index = dom_history_find_event_index(domain, process_event->target_event_id);
    if (target_index < 0) {
        return D_FALSE;
    }
    target = &domain->events[target_index];
    if (target->event_role != DOM_HISTORY_ROLE_DERIVED) {
        return D_FALSE;
    }
    if (process_event->region_id != 0u && target->region_id != process_event->region_id) {
        return D_FALSE;
    }

    delta_confidence = dom_history_clamp_ratio(process_event->delta_confidence);
    delta_uncertainty = dom_history_clamp_ratio(process_event->delta_uncertainty);
    delta_bias = dom_history_clamp_ratio(process_event->delta_bias);

    confidence_before = target->confidence;
    uncertainty_before = target->uncertainty;
    bias_before = target->bias;

    switch (process_event->process_type) {
        case DOM_HISTORY_PROCESS_RECORD:
            target->confidence = dom_history_add_clamped(target->confidence, delta_confidence);
            if (delta_uncertainty > 0) {
                target->uncertainty = dom_history_sub_clamped(target->uncertainty, delta_uncertainty);
            }
            target->flags |= DOM_HISTORY_EVENT_RECORDED;
            break;
        case DOM_HISTORY_PROCESS_FORGET:
            target->confidence = dom_history_sub_clamped(target->confidence, delta_confidence);
            target->uncertainty = dom_history_add_clamped(target->uncertainty, delta_uncertainty);
            target->flags |= DOM_HISTORY_EVENT_FORGOTTEN;
            if (out_flags) {
                *out_flags |= DOM_HISTORY_RESOLVE_FORGOTTEN;
            }
            break;
        case DOM_HISTORY_PROCESS_REVISE:
            target->bias = dom_history_add_clamped(target->bias, delta_bias);
            target->uncertainty = dom_history_add_clamped(target->uncertainty, delta_uncertainty);
            target->flags |= DOM_HISTORY_EVENT_REVISED;
            if (out_flags) {
                *out_flags |= DOM_HISTORY_RESOLVE_REVISED;
            }
            break;
        case DOM_HISTORY_PROCESS_MYTHOLOGIZE:
            target->bias = dom_history_add_clamped(target->bias, delta_bias);
            target->uncertainty = dom_history_add_clamped(target->uncertainty, delta_uncertainty);
            target->flags |= DOM_HISTORY_EVENT_MYTH;
            if (out_flags) {
                *out_flags |= DOM_HISTORY_RESOLVE_MYTH;
            }
            break;
        default:
            return D_FALSE;
    }

    if (confidence_total) {
        q16_16 diff = d_q16_16_sub(target->confidence, confidence_before);
        *confidence_total = d_q48_16_add(*confidence_total, d_q48_16_from_q16_16(diff));
    }
    if (uncertainty_total) {
        q16_16 diff = d_q16_16_sub(target->uncertainty, uncertainty_before);
        *uncertainty_total = d_q48_16_add(*uncertainty_total, d_q48_16_from_q16_16(diff));
    }
    if (bias_total) {
        q16_16 diff = d_q16_16_sub(target->bias, bias_before);
        *bias_total = d_q48_16_add(*bias_total, d_q48_16_from_q16_16(diff));
    }

    process_event->flags |= DOM_HISTORY_EVENT_APPLIED;
    return D_TRUE;
}

static q16_16 dom_history_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_history_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_history_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_HISTORY_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_HISTORY_HIST_BINS) {
        scaled = DOM_HISTORY_HIST_BINS - 1u;
    }
    return scaled;
}

static void dom_history_graph_compute_metrics(dom_history_domain* domain,
                                              dom_civilization_graph* graph)
{
    q48_16 trade_total = 0;
    q16_16 trust_sum = 0;
    q16_16 standard_sum = 0;
    u32 edges_seen = 0u;
    if (!domain || !graph) {
        return;
    }
    for (u32 i = 0u; i < graph->edge_count && i < DOM_HISTORY_MAX_EDGE_REFS; ++i) {
        u32 edge_id = graph->edge_refs[i];
        int edge_index = dom_history_find_edge_index(domain, edge_id);
        if (edge_index < 0) {
            continue;
        }
        trust_sum = d_q16_16_add(trust_sum, domain->edges[edge_index].trust_weight);
        standard_sum = d_q16_16_add(standard_sum, domain->edges[edge_index].standard_weight);
        trade_total = d_q48_16_add(trade_total, domain->edges[edge_index].trade_volume);
        edges_seen += 1u;
    }
    graph->trade_volume_total = trade_total;
    if (edges_seen > 0u) {
        graph->trust_weight_avg = dom_history_clamp_ratio((q16_16)(trust_sum / (i32)edges_seen));
        graph->standard_weight_avg = dom_history_clamp_ratio((q16_16)(standard_sum / (i32)edges_seen));
    } else {
        graph->trust_weight_avg = 0;
        graph->standard_weight_avg = 0;
    }
}

void dom_history_surface_desc_init(dom_history_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->source_count = 0u;
    desc->event_count = 0u;
    desc->epoch_count = 0u;
    desc->graph_count = 0u;
    desc->node_count = 0u;
    desc->edge_count = 0u;
    for (u32 i = 0u; i < DOM_HISTORY_MAX_SOURCES; ++i) {
        desc->sources[i].source_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HISTORY_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HISTORY_MAX_EPOCHS; ++i) {
        desc->epochs[i].epoch_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HISTORY_MAX_GRAPHS; ++i) {
        desc->graphs[i].graph_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HISTORY_MAX_NODES; ++i) {
        desc->nodes[i].node_id = 0u;
    }
    for (u32 i = 0u; i < DOM_HISTORY_MAX_EDGES; ++i) {
        desc->edges[i].edge_id = 0u;
    }
}

void dom_history_domain_init(dom_history_domain* domain,
                             const dom_history_surface_desc* desc)
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

    domain->source_count = (desc->source_count > DOM_HISTORY_MAX_SOURCES)
                             ? DOM_HISTORY_MAX_SOURCES
                             : desc->source_count;
    domain->event_count = (desc->event_count > DOM_HISTORY_MAX_EVENTS)
                            ? DOM_HISTORY_MAX_EVENTS
                            : desc->event_count;
    domain->epoch_count = (desc->epoch_count > DOM_HISTORY_MAX_EPOCHS)
                            ? DOM_HISTORY_MAX_EPOCHS
                            : desc->epoch_count;
    domain->graph_count = (desc->graph_count > DOM_HISTORY_MAX_GRAPHS)
                            ? DOM_HISTORY_MAX_GRAPHS
                            : desc->graph_count;
    domain->node_count = (desc->node_count > DOM_HISTORY_MAX_NODES)
                           ? DOM_HISTORY_MAX_NODES
                           : desc->node_count;
    domain->edge_count = (desc->edge_count > DOM_HISTORY_MAX_EDGES)
                           ? DOM_HISTORY_MAX_EDGES
                           : desc->edge_count;

    for (u32 i = 0u; i < domain->source_count; ++i) {
        dom_history_source_init(&domain->sources[i]);
        domain->sources[i].source_id = desc->sources[i].source_id;
        domain->sources[i].source_type = desc->sources[i].source_type;
        domain->sources[i].source_event_id = desc->sources[i].source_event_id;
        domain->sources[i].perspective_ref_id = desc->sources[i].perspective_ref_id;
        domain->sources[i].confidence = desc->sources[i].confidence;
        domain->sources[i].bias = desc->sources[i].bias;
        domain->sources[i].recorded_tick = desc->sources[i].recorded_tick;
        domain->sources[i].region_id = desc->sources[i].region_id;
        domain->sources[i].provenance_id = desc->sources[i].provenance_id;
        domain->sources[i].flags = desc->sources[i].flags;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_history_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].event_role = desc->events[i].event_role;
        domain->events[i].category = desc->events[i].category;
        domain->events[i].process_type = desc->events[i].process_type;
        domain->events[i].target_event_id = desc->events[i].target_event_id;
        domain->events[i].start_tick = desc->events[i].start_tick;
        domain->events[i].end_tick = desc->events[i].end_tick;
        domain->events[i].source_count = desc->events[i].source_count;
        for (u32 s = 0u; s < DOM_HISTORY_MAX_SOURCE_REFS; ++s) {
            domain->events[i].source_refs[s] = desc->events[i].source_refs[s];
        }
        domain->events[i].perspective_ref_id = desc->events[i].perspective_ref_id;
        domain->events[i].confidence = desc->events[i].confidence;
        domain->events[i].uncertainty = desc->events[i].uncertainty;
        domain->events[i].bias = desc->events[i].bias;
        domain->events[i].decay_rate = desc->events[i].decay_rate;
        domain->events[i].delta_confidence = desc->events[i].delta_confidence;
        domain->events[i].delta_uncertainty = desc->events[i].delta_uncertainty;
        domain->events[i].delta_bias = desc->events[i].delta_bias;
        domain->events[i].myth_weight = desc->events[i].myth_weight;
        domain->events[i].epoch_ref_id = desc->events[i].epoch_ref_id;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    for (u32 i = 0u; i < domain->epoch_count; ++i) {
        dom_history_epoch_init(&domain->epochs[i]);
        domain->epochs[i].epoch_id = desc->epochs[i].epoch_id;
        domain->epochs[i].epoch_type = desc->epochs[i].epoch_type;
        domain->epochs[i].start_tick = desc->epochs[i].start_tick;
        domain->epochs[i].end_tick = desc->epochs[i].end_tick;
        domain->epochs[i].confidence = desc->epochs[i].confidence;
        domain->epochs[i].uncertainty = desc->epochs[i].uncertainty;
        domain->epochs[i].bias = desc->epochs[i].bias;
        domain->epochs[i].perspective_ref_id = desc->epochs[i].perspective_ref_id;
        domain->epochs[i].region_id = desc->epochs[i].region_id;
        domain->epochs[i].provenance_id = desc->epochs[i].provenance_id;
        domain->epochs[i].flags = desc->epochs[i].flags;
    }

    for (u32 i = 0u; i < domain->node_count; ++i) {
        dom_civilization_node_init(&domain->nodes[i]);
        domain->nodes[i].node_id = desc->nodes[i].node_id;
        domain->nodes[i].institution_ref_id = desc->nodes[i].institution_ref_id;
        domain->nodes[i].region_id = desc->nodes[i].region_id;
        domain->nodes[i].flags = desc->nodes[i].flags;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        dom_civilization_edge_init(&domain->edges[i]);
        domain->edges[i].edge_id = desc->edges[i].edge_id;
        domain->edges[i].from_node_id = desc->edges[i].from_node_id;
        domain->edges[i].to_node_id = desc->edges[i].to_node_id;
        domain->edges[i].edge_type = desc->edges[i].edge_type;
        domain->edges[i].trust_weight = desc->edges[i].trust_weight;
        domain->edges[i].trade_volume = desc->edges[i].trade_volume;
        domain->edges[i].standard_weight = desc->edges[i].standard_weight;
        domain->edges[i].region_id = desc->edges[i].region_id;
        domain->edges[i].flags = desc->edges[i].flags;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        dom_civilization_graph_init(&domain->graphs[i]);
        domain->graphs[i].graph_id = desc->graphs[i].graph_id;
        domain->graphs[i].epoch_ref_id = desc->graphs[i].epoch_ref_id;
        domain->graphs[i].node_count = desc->graphs[i].node_count;
        for (u32 n = 0u; n < DOM_HISTORY_MAX_NODE_REFS; ++n) {
            domain->graphs[i].node_refs[n] = desc->graphs[i].node_refs[n];
        }
        domain->graphs[i].edge_count = desc->graphs[i].edge_count;
        for (u32 e = 0u; e < DOM_HISTORY_MAX_EDGE_REFS; ++e) {
            domain->graphs[i].edge_refs[e] = desc->graphs[i].edge_refs[e];
        }
        domain->graphs[i].region_id = desc->graphs[i].region_id;
        domain->graphs[i].provenance_id = desc->graphs[i].provenance_id;
        domain->graphs[i].flags = desc->graphs[i].flags;
        dom_history_graph_compute_metrics(domain, &domain->graphs[i]);
    }

    domain->capsule_count = 0u;
}

void dom_history_domain_free(dom_history_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->source_count = 0u;
    domain->event_count = 0u;
    domain->epoch_count = 0u;
    domain->graph_count = 0u;
    domain->node_count = 0u;
    domain->edge_count = 0u;
    domain->capsule_count = 0u;
}

void dom_history_domain_set_state(dom_history_domain* domain,
                                  u32 existence_state,
                                  u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_history_domain_set_policy(dom_history_domain* domain,
                                   const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_history_source_query(const dom_history_domain* domain,
                             u32 source_id,
                             dom_domain_budget* budget,
                             dom_history_source_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HISTORY_SOURCE_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_source_index(domain, source_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->sources[index].region_id)) {
        out_sample->source_id = domain->sources[index].source_id;
        out_sample->region_id = domain->sources[index].region_id;
        out_sample->flags = DOM_HISTORY_SOURCE_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->source_id = domain->sources[index].source_id;
    out_sample->source_type = domain->sources[index].source_type;
    out_sample->source_event_id = domain->sources[index].source_event_id;
    out_sample->perspective_ref_id = domain->sources[index].perspective_ref_id;
    out_sample->confidence = domain->sources[index].confidence;
    out_sample->bias = domain->sources[index].bias;
    out_sample->recorded_tick = domain->sources[index].recorded_tick;
    out_sample->region_id = domain->sources[index].region_id;
    out_sample->provenance_id = domain->sources[index].provenance_id;
    out_sample->flags = domain->sources[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_history_event_query(const dom_history_domain* domain,
                            u32 event_id,
                            dom_domain_budget* budget,
                            dom_history_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HISTORY_EVENT_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_event_index(domain, event_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->event_role = domain->events[index].event_role;
        out_sample->category = domain->events[index].category;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_HISTORY_EVENT_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->event_role = domain->events[index].event_role;
    out_sample->category = domain->events[index].category;
    out_sample->process_type = domain->events[index].process_type;
    out_sample->target_event_id = domain->events[index].target_event_id;
    out_sample->start_tick = domain->events[index].start_tick;
    out_sample->end_tick = domain->events[index].end_tick;
    out_sample->source_count = domain->events[index].source_count;
    out_sample->perspective_ref_id = domain->events[index].perspective_ref_id;
    out_sample->confidence = domain->events[index].confidence;
    out_sample->uncertainty = domain->events[index].uncertainty;
    out_sample->bias = domain->events[index].bias;
    out_sample->decay_rate = domain->events[index].decay_rate;
    out_sample->delta_confidence = domain->events[index].delta_confidence;
    out_sample->delta_uncertainty = domain->events[index].delta_uncertainty;
    out_sample->delta_bias = domain->events[index].delta_bias;
    out_sample->myth_weight = domain->events[index].myth_weight;
    out_sample->epoch_ref_id = domain->events[index].epoch_ref_id;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->flags = domain->events[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_history_epoch_query(const dom_history_domain* domain,
                            u32 epoch_id,
                            dom_domain_budget* budget,
                            dom_history_epoch_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_HISTORY_EPOCH_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_epoch_index(domain, epoch_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->epochs[index].region_id)) {
        out_sample->epoch_id = domain->epochs[index].epoch_id;
        out_sample->epoch_type = domain->epochs[index].epoch_type;
        out_sample->region_id = domain->epochs[index].region_id;
        out_sample->flags = DOM_HISTORY_EPOCH_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->epoch_id = domain->epochs[index].epoch_id;
    out_sample->epoch_type = domain->epochs[index].epoch_type;
    out_sample->start_tick = domain->epochs[index].start_tick;
    out_sample->end_tick = domain->epochs[index].end_tick;
    out_sample->confidence = domain->epochs[index].confidence;
    out_sample->uncertainty = domain->epochs[index].uncertainty;
    out_sample->bias = domain->epochs[index].bias;
    out_sample->perspective_ref_id = domain->epochs[index].perspective_ref_id;
    out_sample->region_id = domain->epochs[index].region_id;
    out_sample->provenance_id = domain->epochs[index].provenance_id;
    out_sample->flags = domain->epochs[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_civilization_graph_query(const dom_history_domain* domain,
                                 u32 graph_id,
                                 dom_domain_budget* budget,
                                 dom_civilization_graph_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CIV_GRAPH_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_graph_index(domain, graph_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->graphs[index].region_id)) {
        out_sample->graph_id = domain->graphs[index].graph_id;
        out_sample->epoch_ref_id = domain->graphs[index].epoch_ref_id;
        out_sample->region_id = domain->graphs[index].region_id;
        out_sample->flags = DOM_CIV_GRAPH_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->graph_id = domain->graphs[index].graph_id;
    out_sample->epoch_ref_id = domain->graphs[index].epoch_ref_id;
    out_sample->node_count = domain->graphs[index].node_count;
    out_sample->edge_count = domain->graphs[index].edge_count;
    out_sample->trust_weight_avg = domain->graphs[index].trust_weight_avg;
    out_sample->trade_volume_total = domain->graphs[index].trade_volume_total;
    out_sample->standard_weight_avg = domain->graphs[index].standard_weight_avg;
    out_sample->region_id = domain->graphs[index].region_id;
    out_sample->provenance_id = domain->graphs[index].provenance_id;
    out_sample->flags = domain->graphs[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_civilization_node_query(const dom_history_domain* domain,
                                u32 node_id,
                                dom_domain_budget* budget,
                                dom_civilization_node_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CIV_NODE_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_node_index(domain, node_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->nodes[index].region_id)) {
        out_sample->node_id = domain->nodes[index].node_id;
        out_sample->region_id = domain->nodes[index].region_id;
        out_sample->flags = DOM_CIV_NODE_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->node_id = domain->nodes[index].node_id;
    out_sample->institution_ref_id = domain->nodes[index].institution_ref_id;
    out_sample->region_id = domain->nodes[index].region_id;
    out_sample->flags = domain->nodes[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_civilization_edge_query(const dom_history_domain* domain,
                                u32 edge_id,
                                dom_domain_budget* budget,
                                dom_civilization_edge_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_CIV_EDGE_UNRESOLVED;

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_history_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_history_find_edge_index(domain, edge_id);
    if (index < 0) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_history_region_collapsed(domain, domain->edges[index].region_id)) {
        out_sample->edge_id = domain->edges[index].edge_id;
        out_sample->region_id = domain->edges[index].region_id;
        out_sample->flags = DOM_CIV_EDGE_COLLAPSED;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->edge_id = domain->edges[index].edge_id;
    out_sample->from_node_id = domain->edges[index].from_node_id;
    out_sample->to_node_id = domain->edges[index].to_node_id;
    out_sample->edge_type = domain->edges[index].edge_type;
    out_sample->trust_weight = domain->edges[index].trust_weight;
    out_sample->trade_volume = domain->edges[index].trade_volume;
    out_sample->standard_weight = domain->edges[index].standard_weight;
    out_sample->region_id = domain->edges[index].region_id;
    out_sample->flags = domain->edges[index].flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_history_region_query(const dom_history_domain* domain,
                             u32 region_id,
                             dom_domain_budget* budget,
                             dom_history_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_source;
    u32 cost_event;
    u32 cost_epoch;
    u32 cost_graph;
    u32 cost_node;
    u32 cost_edge;
    q48_16 confidence_total = 0;
    q48_16 uncertainty_total = 0;
    q48_16 bias_total = 0;
    q48_16 trade_total = 0;
    q16_16 trust_sum = 0;
    q16_16 standard_sum = 0;
    u32 sources_seen = 0u;
    u32 events_seen = 0u;
    u32 process_seen = 0u;
    u32 epochs_seen = 0u;
    u32 graphs_seen = 0u;
    u32 nodes_seen = 0u;
    u32 edges_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_history_domain_is_active(domain)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_history_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_history_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_history_region_collapsed(domain, region_id)) {
        const dom_history_macro_capsule* capsule = dom_history_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->source_count = capsule->source_count;
            out_sample->event_count = capsule->event_count;
            out_sample->epoch_count = capsule->epoch_count;
            out_sample->graph_count = capsule->graph_count;
            out_sample->node_count = capsule->node_count;
            out_sample->edge_count = capsule->edge_count;
        }
        out_sample->flags = DOM_HISTORY_RESOLVE_PARTIAL;
        dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                  DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_source = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_event = dom_history_budget_cost(domain->policy.cost_medium);
    cost_epoch = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_graph = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_node = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_edge = dom_history_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->source_count; ++i) {
        u32 src_region = domain->sources[i].region_id;
        if (region_id != 0u && src_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, src_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_source)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        sources_seen += 1u;
        if ((domain->sources[i].flags & DOM_HISTORY_SOURCE_ARCHAEOLOGY) ||
            domain->sources[i].source_type == DOM_HISTORY_SOURCE_ARTIFACT) {
            flags |= DOM_HISTORY_RESOLVE_ARCHAEOLOGY;
        }
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        const dom_history_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, event_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        if (event->event_role == DOM_HISTORY_ROLE_PROCESS) {
            process_seen += 1u;
            continue;
        }
        events_seen += 1u;
        confidence_total = d_q48_16_add(confidence_total, d_q48_16_from_q16_16(event->confidence));
        uncertainty_total = d_q48_16_add(uncertainty_total, d_q48_16_from_q16_16(event->uncertainty));
        bias_total = d_q48_16_add(bias_total, d_q48_16_from_q16_16(event->bias));
    }

    for (u32 i = 0u; i < domain->epoch_count; ++i) {
        u32 epoch_region = domain->epochs[i].region_id;
        if (region_id != 0u && epoch_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, epoch_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_epoch)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        epochs_seen += 1u;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        u32 graph_region = domain->graphs[i].region_id;
        if (region_id != 0u && graph_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, graph_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_graph)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        graphs_seen += 1u;
    }

    for (u32 i = 0u; i < domain->node_count; ++i) {
        u32 node_region = domain->nodes[i].region_id;
        if (region_id != 0u && node_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, node_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_node)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        nodes_seen += 1u;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        u32 edge_region = domain->edges[i].region_id;
        if (region_id != 0u && edge_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, edge_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_edge)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            break;
        }
        edges_seen += 1u;
        trust_sum = d_q16_16_add(trust_sum, domain->edges[i].trust_weight);
        standard_sum = d_q16_16_add(standard_sum, domain->edges[i].standard_weight);
        trade_total = d_q48_16_add(trade_total, domain->edges[i].trade_volume);
    }

    out_sample->region_id = region_id;
    out_sample->source_count = sources_seen;
    out_sample->event_count = events_seen;
    out_sample->process_count = process_seen;
    out_sample->epoch_count = epochs_seen;
    out_sample->graph_count = graphs_seen;
    out_sample->node_count = nodes_seen;
    out_sample->edge_count = edges_seen;
    if (events_seen > 0u) {
        q48_16 div = d_q48_16_div(confidence_total, d_q48_16_from_int((i64)events_seen));
        out_sample->confidence_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(uncertainty_total, d_q48_16_from_int((i64)events_seen));
        out_sample->uncertainty_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(bias_total, d_q48_16_from_int((i64)events_seen));
        out_sample->bias_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (edges_seen > 0u) {
        out_sample->trust_weight_avg = dom_history_clamp_ratio((q16_16)(trust_sum / (i32)edges_seen));
        out_sample->standard_weight_avg = dom_history_clamp_ratio((q16_16)(standard_sum / (i32)edges_seen));
    }
    out_sample->trade_volume_total = trade_total;
    out_sample->flags = flags;
    dom_history_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                              flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                              cost_base, budget);
    return 0;
}

int dom_history_resolve(dom_history_domain* domain,
                        u32 region_id,
                        u64 tick,
                        u64 tick_delta,
                        dom_domain_budget* budget,
                        dom_history_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_source;
    u32 cost_event;
    u32 cost_epoch;
    u32 cost_graph;
    u32 cost_node;
    u32 cost_edge;
    q48_16 confidence_total = 0;
    q48_16 uncertainty_total = 0;
    q48_16 bias_total = 0;
    q48_16 trade_total = 0;
    q16_16 trust_sum = 0;
    q16_16 standard_sum = 0;
    u32 sources_seen = 0u;
    u32 events_seen = 0u;
    u32 process_seen = 0u;
    u32 events_applied = 0u;
    u32 epochs_seen = 0u;
    u32 graphs_seen = 0u;
    u32 nodes_seen = 0u;
    u32 edges_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_history_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_HISTORY_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_history_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_history_region_collapsed(domain, region_id)) {
        const dom_history_macro_capsule* capsule = dom_history_find_capsule(domain, region_id);
        if (capsule) {
            out_result->source_count = capsule->source_count;
            out_result->event_count = capsule->event_count;
            out_result->epoch_count = capsule->epoch_count;
            out_result->graph_count = capsule->graph_count;
            out_result->node_count = capsule->node_count;
            out_result->edge_count = capsule->edge_count;
        }
        out_result->ok = 1u;
        out_result->flags = DOM_HISTORY_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_source = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_event = dom_history_budget_cost(domain->policy.cost_medium);
    cost_epoch = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_graph = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_node = dom_history_budget_cost(domain->policy.cost_coarse);
    cost_edge = dom_history_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->source_count; ++i) {
        u32 src_region = domain->sources[i].region_id;
        if (region_id != 0u && src_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, src_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_source)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }
        sources_seen += 1u;
        if ((domain->sources[i].flags & DOM_HISTORY_SOURCE_ARCHAEOLOGY) ||
            domain->sources[i].source_type == DOM_HISTORY_SOURCE_ARTIFACT) {
            flags |= DOM_HISTORY_RESOLVE_ARCHAEOLOGY;
        }
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_history_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, event_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }

        if (event->event_role == DOM_HISTORY_ROLE_PROCESS) {
            process_seen += 1u;
            continue;
        }

        events_seen += 1u;
        if (dom_history_apply_decay(event, tick_delta)) {
            event->flags |= DOM_HISTORY_EVENT_REVISED;
            flags |= DOM_HISTORY_RESOLVE_DECAYED;
        }
        confidence_total = d_q48_16_add(confidence_total, d_q48_16_from_q16_16(event->confidence));
        uncertainty_total = d_q48_16_add(uncertainty_total, d_q48_16_from_q16_16(event->uncertainty));
        bias_total = d_q48_16_add(bias_total, d_q48_16_from_q16_16(event->bias));
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_history_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (event->event_role != DOM_HISTORY_ROLE_PROCESS) {
            continue;
        }
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, event_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (dom_history_apply_process(domain, event, tick,
                                      &confidence_total, &uncertainty_total, &bias_total, &flags)) {
            events_applied += 1u;
        }
    }

    for (u32 i = 0u; i < domain->epoch_count; ++i) {
        u32 epoch_region = domain->epochs[i].region_id;
        if (region_id != 0u && epoch_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, epoch_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_epoch)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }
        epochs_seen += 1u;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        u32 graph_region = domain->graphs[i].region_id;
        if (region_id != 0u && graph_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, graph_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_graph)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }
        graphs_seen += 1u;
    }

    for (u32 i = 0u; i < domain->node_count; ++i) {
        u32 node_region = domain->nodes[i].region_id;
        if (region_id != 0u && node_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, node_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_node)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }
        nodes_seen += 1u;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        u32 edge_region = domain->edges[i].region_id;
        if (region_id != 0u && edge_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_history_region_collapsed(domain, edge_region)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_edge)) {
            flags |= DOM_HISTORY_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_HISTORY_REFUSE_NONE) {
                out_result->refusal_reason = DOM_HISTORY_REFUSE_BUDGET;
            }
            break;
        }
        edges_seen += 1u;
        trust_sum = d_q16_16_add(trust_sum, domain->edges[i].trust_weight);
        standard_sum = d_q16_16_add(standard_sum, domain->edges[i].standard_weight);
        trade_total = d_q48_16_add(trade_total, domain->edges[i].trade_volume);
    }

    out_result->ok = 1u;
    out_result->flags = flags;
    out_result->source_count = sources_seen;
    out_result->event_count = events_seen;
    out_result->process_count = process_seen;
    out_result->event_applied_count = events_applied;
    out_result->epoch_count = epochs_seen;
    out_result->graph_count = graphs_seen;
    out_result->node_count = nodes_seen;
    out_result->edge_count = edges_seen;
    if (events_seen > 0u) {
        q48_16 div = d_q48_16_div(confidence_total, d_q48_16_from_int((i64)events_seen));
        out_result->confidence_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(uncertainty_total, d_q48_16_from_int((i64)events_seen));
        out_result->uncertainty_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
        div = d_q48_16_div(bias_total, d_q48_16_from_int((i64)events_seen));
        out_result->bias_avg = dom_history_clamp_ratio(d_q16_16_from_q48_16(div));
    }
    if (edges_seen > 0u) {
        out_result->trust_weight_avg = dom_history_clamp_ratio((q16_16)(trust_sum / (i32)edges_seen));
        out_result->standard_weight_avg = dom_history_clamp_ratio((q16_16)(standard_sum / (i32)edges_seen));
    }
    out_result->trade_volume_total = trade_total;
    return 0;
}

int dom_history_domain_collapse_region(dom_history_domain* domain, u32 region_id)
{
    dom_history_macro_capsule capsule;
    u32 bias_bins[DOM_HISTORY_HIST_BINS];
    u32 confidence_bins[DOM_HISTORY_HIST_BINS];
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_history_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_HISTORY_MAX_CAPSULES) {
        return -2;
    }
    memset(bias_bins, 0, sizeof(bias_bins));
    memset(confidence_bins, 0, sizeof(confidence_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->source_count; ++i) {
        if (domain->sources[i].region_id != region_id) {
            continue;
        }
        capsule.source_count += 1u;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        const dom_history_event* event = &domain->events[i];
        if (event->region_id != region_id || event->event_role != DOM_HISTORY_ROLE_DERIVED) {
            continue;
        }
        capsule.event_count += 1u;
        if (event->category < DOM_HISTORY_EVENT_CLASS_COUNT) {
            capsule.event_category_counts[event->category] += 1u;
        }
        bias_bins[dom_history_hist_bin(event->bias)] += 1u;
        confidence_bins[dom_history_hist_bin(event->confidence)] += 1u;
    }
    for (u32 i = 0u; i < domain->epoch_count; ++i) {
        if (domain->epochs[i].region_id != region_id) {
            continue;
        }
        capsule.epoch_count += 1u;
    }
    for (u32 i = 0u; i < domain->graph_count; ++i) {
        if (domain->graphs[i].region_id != region_id) {
            continue;
        }
        capsule.graph_count += 1u;
    }
    for (u32 i = 0u; i < domain->node_count; ++i) {
        if (domain->nodes[i].region_id != region_id) {
            continue;
        }
        capsule.node_count += 1u;
    }
    for (u32 i = 0u; i < domain->edge_count; ++i) {
        if (domain->edges[i].region_id != region_id) {
            continue;
        }
        capsule.edge_count += 1u;
    }
    for (u32 b = 0u; b < DOM_HISTORY_HIST_BINS; ++b) {
        capsule.bias_hist[b] = dom_history_hist_bin_ratio(bias_bins[b], capsule.event_count);
        capsule.confidence_hist[b] = dom_history_hist_bin_ratio(confidence_bins[b], capsule.event_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_history_domain_expand_region(dom_history_domain* domain, u32 region_id)
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

u32 dom_history_domain_capsule_count(const dom_history_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_history_macro_capsule* dom_history_domain_capsule_at(const dom_history_domain* domain,
                                                               u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_history_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
