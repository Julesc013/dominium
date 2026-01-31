/*
FILE: source/domino/world/standard_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/standard_fields
RESPONSIBILITY: Implements deterministic standards, toolchains, and meta-tool resolution.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/standard_fields.h"

#include "domino/core/fixed_math.h"

#include <string.h>

#define DOM_STANDARD_RESOLVE_COST_BASE 1u

static q16_16 dom_standard_clamp_ratio(q16_16 value)
{
    if (value < 0) {
        return 0;
    }
    if (value > DOM_STANDARD_RATIO_ONE_Q16) {
        return DOM_STANDARD_RATIO_ONE_Q16;
    }
    return value;
}

static q16_16 dom_standard_adjust_clamped(q16_16 base, q16_16 delta)
{
    q16_16 sum = d_q16_16_add(base, delta);
    return dom_standard_clamp_ratio(sum);
}

static void dom_standard_definition_init(dom_standard_definition* def)
{
    if (!def) {
        return;
    }
    memset(def, 0, sizeof(*def));
}

static void dom_standard_version_init(dom_standard_version* version)
{
    if (!version) {
        return;
    }
    memset(version, 0, sizeof(*version));
    version->status = DOM_STANDARD_STATUS_UNSET;
}

static void dom_standard_scope_init(dom_standard_scope* scope)
{
    if (!scope) {
        return;
    }
    memset(scope, 0, sizeof(*scope));
}

static void dom_standard_event_init(dom_standard_event* event)
{
    if (!event) {
        return;
    }
    memset(event, 0, sizeof(*event));
    event->process_type = DOM_STANDARD_PROCESS_UNSET;
}

static void dom_meta_tool_init(dom_meta_tool* tool)
{
    if (!tool) {
        return;
    }
    memset(tool, 0, sizeof(*tool));
}

static void dom_toolchain_edge_init(dom_toolchain_edge* edge)
{
    if (!edge) {
        return;
    }
    memset(edge, 0, sizeof(*edge));
}

static void dom_toolchain_graph_init(dom_toolchain_graph* graph)
{
    if (!graph) {
        return;
    }
    memset(graph, 0, sizeof(*graph));
}

static int dom_standard_find_definition_index(const dom_standard_domain* domain, u32 standard_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->definition_count; ++i) {
        if (domain->definitions[i].standard_id == standard_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_standard_find_version_index(const dom_standard_domain* domain, u32 version_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->version_count; ++i) {
        if (domain->versions[i].version_id == version_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_standard_find_scope_index(const dom_standard_domain* domain, u32 scope_id)
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

static int dom_standard_find_event_index(const dom_standard_domain* domain, u32 event_id)
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

static int dom_standard_find_tool_index(const dom_standard_domain* domain, u32 tool_id)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->tool_count; ++i) {
        if (domain->tools[i].tool_id == tool_id) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_standard_find_edge_index(const dom_standard_domain* domain, u32 edge_id)
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

static int dom_standard_find_graph_index(const dom_standard_domain* domain, u32 graph_id)
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

static int dom_standard_find_scope_for_event(const dom_standard_domain* domain,
                                             const dom_standard_event* event)
{
    if (!domain || !event) {
        return -1;
    }
    if (event->scope_id != 0u) {
        return dom_standard_find_scope_index(domain, event->scope_id);
    }
    for (u32 i = 0u; i < domain->scope_count; ++i) {
        const dom_standard_scope* scope = &domain->scopes[i];
        if (event->standard_id != 0u && scope->standard_id != event->standard_id) {
            continue;
        }
        if (event->version_id != 0u && scope->version_id != event->version_id) {
            continue;
        }
        return (int)i;
    }
    return -1;
}

static dom_standard_version* dom_standard_find_version_for_scope(dom_standard_domain* domain,
                                                                 const dom_standard_scope* scope)
{
    int index;
    if (!domain || !scope) {
        return (dom_standard_version*)0;
    }
    index = dom_standard_find_version_index(domain, scope->version_id);
    if (index < 0) {
        return (dom_standard_version*)0;
    }
    return &domain->versions[index];
}

static d_bool dom_standard_domain_is_active(const dom_standard_domain* domain)
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

static d_bool dom_standard_region_collapsed(const dom_standard_domain* domain, u32 region_id)
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

static const dom_standard_macro_capsule* dom_standard_find_capsule(const dom_standard_domain* domain,
                                                                   u32 region_id)
{
    if (!domain) {
        return (const dom_standard_macro_capsule*)0;
    }
    for (u32 i = 0u; i < domain->capsule_count; ++i) {
        if (domain->capsules[i].region_id == region_id) {
            return &domain->capsules[i];
        }
    }
    return (const dom_standard_macro_capsule*)0;
}

static void dom_standard_query_meta_refused(dom_domain_query_meta* meta,
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

static void dom_standard_query_meta_ok(dom_domain_query_meta* meta,
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

static u32 dom_standard_budget_cost(u32 cost_units)
{
    return (cost_units == 0u) ? DOM_STANDARD_RESOLVE_COST_BASE : cost_units;
}

static u32 dom_standard_event_bin(u32 process_type)
{
    switch (process_type) {
        case DOM_STANDARD_PROCESS_PROPOSE: return 0u;
        case DOM_STANDARD_PROCESS_ADOPT: return 1u;
        case DOM_STANDARD_PROCESS_AUDIT: return 2u;
        case DOM_STANDARD_PROCESS_ENFORCE: return 3u;
        case DOM_STANDARD_PROCESS_REVOKE: return 4u;
        default: return 0u;
    }
}

static void dom_standard_update_scope_flags(dom_standard_scope* scope,
                                            const dom_standard_version* version)
{
    if (!scope) {
        return;
    }
    scope->flags &= ~(DOM_STANDARD_SCOPE_ADOPTED |
                      DOM_STANDARD_SCOPE_NONCOMPLIANT |
                      DOM_STANDARD_SCOPE_LOCKED_IN |
                      DOM_STANDARD_SCOPE_REVOKED);

    if (version && version->status == DOM_STANDARD_STATUS_REVOKED) {
        scope->flags |= DOM_STANDARD_SCOPE_REVOKED;
        return;
    }

    if (scope->adoption_rate > 0) {
        if (!version || version->adoption_threshold <= 0 ||
            scope->adoption_rate >= version->adoption_threshold) {
            scope->flags |= DOM_STANDARD_SCOPE_ADOPTED;
        }
    }
    if (scope->compliance_rate < scope->adoption_rate) {
        scope->flags |= DOM_STANDARD_SCOPE_NONCOMPLIANT;
    }
    if (scope->lock_in_index > 0) {
        scope->flags |= DOM_STANDARD_SCOPE_LOCKED_IN;
    }
}

static d_bool dom_standard_apply_event(dom_standard_domain* domain,
                                       dom_standard_event* event,
                                       u64 tick,
                                       u32* out_flags,
                                       u32* out_revocations)
{
    int scope_index;
    dom_standard_scope* scope;
    dom_standard_version* version;
    d_bool changed = D_FALSE;
    if (!domain || !event) {
        return D_FALSE;
    }
    if (event->flags & DOM_STANDARD_EVENT_APPLIED) {
        return D_FALSE;
    }
    if (event->event_tick > tick) {
        return D_FALSE;
    }

    scope_index = dom_standard_find_scope_for_event(domain, event);
    if (scope_index < 0) {
        event->flags |= DOM_STANDARD_EVENT_FAILED;
        return D_FALSE;
    }

    scope = &domain->scopes[scope_index];
    version = dom_standard_find_version_for_scope(domain, scope);

    switch (event->process_type) {
        case DOM_STANDARD_PROCESS_PROPOSE:
            if (version && version->status == DOM_STANDARD_STATUS_UNSET) {
                version->status = DOM_STANDARD_STATUS_ACTIVE;
                changed = D_TRUE;
            }
            if (event->delta_adoption != 0) {
                scope->adoption_rate = dom_standard_adjust_clamped(scope->adoption_rate,
                                                                  event->delta_adoption);
                changed = D_TRUE;
                if (out_flags) {
                    *out_flags |= DOM_STANDARD_RESOLVE_ADOPTION_SHIFT;
                }
            }
            break;
        case DOM_STANDARD_PROCESS_ADOPT:
            if (event->delta_adoption != 0) {
                scope->adoption_rate = dom_standard_adjust_clamped(scope->adoption_rate,
                                                                  event->delta_adoption);
                changed = D_TRUE;
                if (out_flags) {
                    *out_flags |= DOM_STANDARD_RESOLVE_ADOPTION_SHIFT;
                }
            }
            break;
        case DOM_STANDARD_PROCESS_AUDIT:
            if (event->delta_compliance != 0) {
                scope->compliance_rate = dom_standard_adjust_clamped(scope->compliance_rate,
                                                                    event->delta_compliance);
                changed = D_TRUE;
                if (out_flags) {
                    *out_flags |= DOM_STANDARD_RESOLVE_COMPLIANCE_SHIFT;
                }
            }
            break;
        case DOM_STANDARD_PROCESS_ENFORCE:
            if (event->delta_compliance != 0) {
                scope->compliance_rate = dom_standard_adjust_clamped(scope->compliance_rate,
                                                                    event->delta_compliance);
                changed = D_TRUE;
                if (out_flags) {
                    *out_flags |= DOM_STANDARD_RESOLVE_COMPLIANCE_SHIFT;
                }
            }
            if (event->delta_lock_in != 0) {
                scope->lock_in_index = dom_standard_adjust_clamped(scope->lock_in_index,
                                                                  event->delta_lock_in);
                changed = D_TRUE;
                if (out_flags) {
                    *out_flags |= DOM_STANDARD_RESOLVE_LOCKIN_SHIFT;
                }
            }
            break;
        case DOM_STANDARD_PROCESS_REVOKE:
            scope->adoption_rate = 0;
            scope->compliance_rate = 0;
            scope->lock_in_index = 0;
            scope->flags |= DOM_STANDARD_SCOPE_REVOKED;
            if (version) {
                version->status = DOM_STANDARD_STATUS_REVOKED;
                version->flags |= DOM_STANDARD_VERSION_REVOKED;
            }
            changed = D_TRUE;
            if (out_flags) {
                *out_flags |= DOM_STANDARD_RESOLVE_REVOCATION;
            }
            if (out_revocations) {
                *out_revocations += 1u;
            }
            break;
        default:
            event->flags |= DOM_STANDARD_EVENT_FAILED;
            return D_FALSE;
    }

    dom_standard_update_scope_flags(scope, version);
    event->flags |= DOM_STANDARD_EVENT_APPLIED;
    return changed;
}

static q16_16 dom_standard_hist_bin_ratio(u32 count, u32 total)
{
    if (total == 0u) {
        return 0;
    }
    return (q16_16)(((u64)count << Q16_16_FRAC_BITS) / total);
}

static u32 dom_standard_hist_bin(q16_16 ratio)
{
    q16_16 clamped = dom_standard_clamp_ratio(ratio);
    u32 scaled = (u32)(((i64)clamped * (DOM_STANDARD_HIST_BINS - 1u)) >> Q16_16_FRAC_BITS);
    if (scaled >= DOM_STANDARD_HIST_BINS) {
        scaled = DOM_STANDARD_HIST_BINS - 1u;
    }
    return scaled;
}

void dom_standard_surface_desc_init(dom_standard_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->meters_per_unit = d_q16_16_from_int(1);
    desc->definition_count = 0u;
    desc->version_count = 0u;
    desc->scope_count = 0u;
    desc->event_count = 0u;
    desc->tool_count = 0u;
    desc->edge_count = 0u;
    desc->graph_count = 0u;
    for (u32 i = 0u; i < DOM_STANDARD_MAX_DEFINITIONS; ++i) {
        desc->definitions[i].standard_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_VERSIONS; ++i) {
        desc->versions[i].version_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_SCOPES; ++i) {
        desc->scopes[i].scope_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_EVENTS; ++i) {
        desc->events[i].event_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_TOOLS; ++i) {
        desc->tools[i].tool_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_EDGES; ++i) {
        desc->edges[i].edge_id = 0u;
    }
    for (u32 i = 0u; i < DOM_STANDARD_MAX_GRAPHS; ++i) {
        desc->graphs[i].graph_id = 0u;
    }
}

void dom_standard_domain_init(dom_standard_domain* domain,
                              const dom_standard_surface_desc* desc)
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

    domain->definition_count = (desc->definition_count > DOM_STANDARD_MAX_DEFINITIONS)
                                 ? DOM_STANDARD_MAX_DEFINITIONS
                                 : desc->definition_count;
    domain->version_count = (desc->version_count > DOM_STANDARD_MAX_VERSIONS)
                              ? DOM_STANDARD_MAX_VERSIONS
                              : desc->version_count;
    domain->scope_count = (desc->scope_count > DOM_STANDARD_MAX_SCOPES)
                            ? DOM_STANDARD_MAX_SCOPES
                            : desc->scope_count;
    domain->event_count = (desc->event_count > DOM_STANDARD_MAX_EVENTS)
                            ? DOM_STANDARD_MAX_EVENTS
                            : desc->event_count;
    domain->tool_count = (desc->tool_count > DOM_STANDARD_MAX_TOOLS)
                           ? DOM_STANDARD_MAX_TOOLS
                           : desc->tool_count;
    domain->edge_count = (desc->edge_count > DOM_STANDARD_MAX_EDGES)
                           ? DOM_STANDARD_MAX_EDGES
                           : desc->edge_count;
    domain->graph_count = (desc->graph_count > DOM_STANDARD_MAX_GRAPHS)
                            ? DOM_STANDARD_MAX_GRAPHS
                            : desc->graph_count;

    for (u32 i = 0u; i < domain->definition_count; ++i) {
        dom_standard_definition_init(&domain->definitions[i]);
        domain->definitions[i].standard_id = desc->definitions[i].standard_id;
        domain->definitions[i].subject_domain_id = desc->definitions[i].subject_domain_id;
        domain->definitions[i].specification_id = desc->definitions[i].specification_id;
        domain->definitions[i].current_version_id = desc->definitions[i].current_version_id;
        domain->definitions[i].compatibility_policy_id = desc->definitions[i].compatibility_policy_id;
        domain->definitions[i].issuing_institution_id = desc->definitions[i].issuing_institution_id;
        domain->definitions[i].adoption_req_count = desc->definitions[i].adoption_req_count;
        for (u32 a = 0u; a < DOM_STANDARD_MAX_ADOPTION_REQS; ++a) {
            domain->definitions[i].adoption_req_ids[a] = desc->definitions[i].adoption_req_ids[a];
        }
        domain->definitions[i].enforcement_count = desc->definitions[i].enforcement_count;
        for (u32 e = 0u; e < DOM_STANDARD_MAX_ENFORCEMENTS; ++e) {
            domain->definitions[i].enforcement_ids[e] = desc->definitions[i].enforcement_ids[e];
        }
        domain->definitions[i].provenance_id = desc->definitions[i].provenance_id;
        domain->definitions[i].region_id = desc->definitions[i].region_id;
        domain->definitions[i].flags = desc->definitions[i].flags;
    }

    for (u32 i = 0u; i < domain->version_count; ++i) {
        dom_standard_version_init(&domain->versions[i]);
        domain->versions[i].version_id = desc->versions[i].version_id;
        domain->versions[i].standard_id = desc->versions[i].standard_id;
        domain->versions[i].version_tag_id = desc->versions[i].version_tag_id;
        domain->versions[i].compatibility_group_id = desc->versions[i].compatibility_group_id;
        domain->versions[i].compatibility_score = desc->versions[i].compatibility_score;
        domain->versions[i].adoption_threshold = desc->versions[i].adoption_threshold;
        domain->versions[i].status = desc->versions[i].status;
        domain->versions[i].release_tick = desc->versions[i].release_tick;
        domain->versions[i].provenance_id = desc->versions[i].provenance_id;
        domain->versions[i].region_id = desc->versions[i].region_id;
        domain->versions[i].flags = desc->versions[i].flags;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        dom_standard_scope_init(&domain->scopes[i]);
        domain->scopes[i].scope_id = desc->scopes[i].scope_id;
        domain->scopes[i].standard_id = desc->scopes[i].standard_id;
        domain->scopes[i].version_id = desc->scopes[i].version_id;
        domain->scopes[i].spatial_domain_id = desc->scopes[i].spatial_domain_id;
        domain->scopes[i].subject_domain_id = desc->scopes[i].subject_domain_id;
        domain->scopes[i].adoption_rate = desc->scopes[i].adoption_rate;
        domain->scopes[i].compliance_rate = desc->scopes[i].compliance_rate;
        domain->scopes[i].lock_in_index = desc->scopes[i].lock_in_index;
        domain->scopes[i].enforcement_level = desc->scopes[i].enforcement_level;
        domain->scopes[i].provenance_id = desc->scopes[i].provenance_id;
        domain->scopes[i].region_id = desc->scopes[i].region_id;
        domain->scopes[i].flags = desc->scopes[i].flags;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_standard_event_init(&domain->events[i]);
        domain->events[i].event_id = desc->events[i].event_id;
        domain->events[i].process_type = desc->events[i].process_type;
        domain->events[i].standard_id = desc->events[i].standard_id;
        domain->events[i].version_id = desc->events[i].version_id;
        domain->events[i].scope_id = desc->events[i].scope_id;
        domain->events[i].delta_adoption = desc->events[i].delta_adoption;
        domain->events[i].delta_compliance = desc->events[i].delta_compliance;
        domain->events[i].delta_lock_in = desc->events[i].delta_lock_in;
        domain->events[i].event_tick = desc->events[i].event_tick;
        domain->events[i].provenance_id = desc->events[i].provenance_id;
        domain->events[i].region_id = desc->events[i].region_id;
        domain->events[i].flags = desc->events[i].flags;
    }

    for (u32 i = 0u; i < domain->tool_count; ++i) {
        dom_meta_tool_init(&domain->tools[i]);
        domain->tools[i].tool_id = desc->tools[i].tool_id;
        domain->tools[i].tool_type_id = desc->tools[i].tool_type_id;
        domain->tools[i].input_standard_id = desc->tools[i].input_standard_id;
        domain->tools[i].output_standard_id = desc->tools[i].output_standard_id;
        domain->tools[i].capacity = desc->tools[i].capacity;
        domain->tools[i].energy_cost = desc->tools[i].energy_cost;
        domain->tools[i].heat_output = desc->tools[i].heat_output;
        domain->tools[i].error_rate = desc->tools[i].error_rate;
        domain->tools[i].bias = desc->tools[i].bias;
        domain->tools[i].provenance_id = desc->tools[i].provenance_id;
        domain->tools[i].region_id = desc->tools[i].region_id;
        domain->tools[i].flags = desc->tools[i].flags;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        dom_toolchain_edge_init(&domain->edges[i]);
        domain->edges[i].edge_id = desc->edges[i].edge_id;
        domain->edges[i].from_tool_id = desc->edges[i].from_tool_id;
        domain->edges[i].to_tool_id = desc->edges[i].to_tool_id;
        domain->edges[i].input_standard_id = desc->edges[i].input_standard_id;
        domain->edges[i].output_standard_id = desc->edges[i].output_standard_id;
        domain->edges[i].compatibility_score = desc->edges[i].compatibility_score;
        domain->edges[i].provenance_id = desc->edges[i].provenance_id;
        domain->edges[i].region_id = desc->edges[i].region_id;
        domain->edges[i].flags = desc->edges[i].flags;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        dom_toolchain_graph_init(&domain->graphs[i]);
        domain->graphs[i].graph_id = desc->graphs[i].graph_id;
        domain->graphs[i].node_count = desc->graphs[i].node_count;
        for (u32 n = 0u; n < DOM_STANDARD_MAX_GRAPH_NODES; ++n) {
            domain->graphs[i].node_tool_ids[n] = desc->graphs[i].node_tool_ids[n];
        }
        domain->graphs[i].edge_count = desc->graphs[i].edge_count;
        for (u32 e = 0u; e < DOM_STANDARD_MAX_GRAPH_EDGES; ++e) {
            domain->graphs[i].edge_ids[e] = desc->graphs[i].edge_ids[e];
        }
        domain->graphs[i].provenance_id = desc->graphs[i].provenance_id;
        domain->graphs[i].region_id = desc->graphs[i].region_id;
        domain->graphs[i].flags = desc->graphs[i].flags;
    }

    domain->capsule_count = 0u;
}

void dom_standard_domain_free(dom_standard_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->definition_count = 0u;
    domain->version_count = 0u;
    domain->scope_count = 0u;
    domain->event_count = 0u;
    domain->tool_count = 0u;
    domain->edge_count = 0u;
    domain->graph_count = 0u;
    domain->capsule_count = 0u;
}

void dom_standard_domain_set_state(dom_standard_domain* domain,
                                   u32 existence_state,
                                   u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_standard_domain_set_policy(dom_standard_domain* domain,
                                    const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_standard_definition_query(const dom_standard_domain* domain,
                                  u32 standard_id,
                                  dom_domain_budget* budget,
                                  dom_standard_definition_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_STANDARD_DEF_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_definition_index(domain, standard_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->definitions[index].region_id)) {
        out_sample->standard_id = domain->definitions[index].standard_id;
        out_sample->region_id = domain->definitions[index].region_id;
        out_sample->flags = DOM_STANDARD_DEF_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->standard_id = domain->definitions[index].standard_id;
    out_sample->subject_domain_id = domain->definitions[index].subject_domain_id;
    out_sample->specification_id = domain->definitions[index].specification_id;
    out_sample->current_version_id = domain->definitions[index].current_version_id;
    out_sample->compatibility_policy_id = domain->definitions[index].compatibility_policy_id;
    out_sample->issuing_institution_id = domain->definitions[index].issuing_institution_id;
    out_sample->adoption_req_count = domain->definitions[index].adoption_req_count;
    out_sample->enforcement_count = domain->definitions[index].enforcement_count;
    out_sample->provenance_id = domain->definitions[index].provenance_id;
    out_sample->region_id = domain->definitions[index].region_id;
    out_sample->flags = domain->definitions[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_standard_version_query(const dom_standard_domain* domain,
                               u32 version_id,
                               dom_domain_budget* budget,
                               dom_standard_version_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_STANDARD_VERSION_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_version_index(domain, version_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->versions[index].region_id)) {
        out_sample->version_id = domain->versions[index].version_id;
        out_sample->region_id = domain->versions[index].region_id;
        out_sample->flags = DOM_STANDARD_VERSION_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->version_id = domain->versions[index].version_id;
    out_sample->standard_id = domain->versions[index].standard_id;
    out_sample->version_tag_id = domain->versions[index].version_tag_id;
    out_sample->compatibility_group_id = domain->versions[index].compatibility_group_id;
    out_sample->compatibility_score = domain->versions[index].compatibility_score;
    out_sample->adoption_threshold = domain->versions[index].adoption_threshold;
    out_sample->status = domain->versions[index].status;
    out_sample->release_tick = domain->versions[index].release_tick;
    out_sample->provenance_id = domain->versions[index].provenance_id;
    out_sample->region_id = domain->versions[index].region_id;
    out_sample->flags = domain->versions[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_standard_scope_query(const dom_standard_domain* domain,
                             u32 scope_id,
                             dom_domain_budget* budget,
                             dom_standard_scope_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_STANDARD_SCOPE_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_scope_index(domain, scope_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->scopes[index].region_id)) {
        out_sample->scope_id = domain->scopes[index].scope_id;
        out_sample->region_id = domain->scopes[index].region_id;
        out_sample->flags = DOM_STANDARD_SCOPE_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->scope_id = domain->scopes[index].scope_id;
    out_sample->standard_id = domain->scopes[index].standard_id;
    out_sample->version_id = domain->scopes[index].version_id;
    out_sample->spatial_domain_id = domain->scopes[index].spatial_domain_id;
    out_sample->subject_domain_id = domain->scopes[index].subject_domain_id;
    out_sample->adoption_rate = domain->scopes[index].adoption_rate;
    out_sample->compliance_rate = domain->scopes[index].compliance_rate;
    out_sample->lock_in_index = domain->scopes[index].lock_in_index;
    out_sample->enforcement_level = domain->scopes[index].enforcement_level;
    out_sample->provenance_id = domain->scopes[index].provenance_id;
    out_sample->region_id = domain->scopes[index].region_id;
    out_sample->flags = domain->scopes[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_standard_event_query(const dom_standard_domain* domain,
                             u32 event_id,
                             dom_domain_budget* budget,
                             dom_standard_event_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_STANDARD_EVENT_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_event_index(domain, event_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->events[index].region_id)) {
        out_sample->event_id = domain->events[index].event_id;
        out_sample->region_id = domain->events[index].region_id;
        out_sample->flags = DOM_STANDARD_EVENT_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->event_id = domain->events[index].event_id;
    out_sample->process_type = domain->events[index].process_type;
    out_sample->standard_id = domain->events[index].standard_id;
    out_sample->version_id = domain->events[index].version_id;
    out_sample->scope_id = domain->events[index].scope_id;
    out_sample->delta_adoption = domain->events[index].delta_adoption;
    out_sample->delta_compliance = domain->events[index].delta_compliance;
    out_sample->delta_lock_in = domain->events[index].delta_lock_in;
    out_sample->event_tick = domain->events[index].event_tick;
    out_sample->provenance_id = domain->events[index].provenance_id;
    out_sample->region_id = domain->events[index].region_id;
    out_sample->flags = domain->events[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_meta_tool_query(const dom_standard_domain* domain,
                        u32 tool_id,
                        dom_domain_budget* budget,
                        dom_meta_tool_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_META_TOOL_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_tool_index(domain, tool_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->tools[index].region_id)) {
        out_sample->tool_id = domain->tools[index].tool_id;
        out_sample->region_id = domain->tools[index].region_id;
        out_sample->flags = DOM_META_TOOL_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->tool_id = domain->tools[index].tool_id;
    out_sample->tool_type_id = domain->tools[index].tool_type_id;
    out_sample->input_standard_id = domain->tools[index].input_standard_id;
    out_sample->output_standard_id = domain->tools[index].output_standard_id;
    out_sample->capacity = domain->tools[index].capacity;
    out_sample->energy_cost = domain->tools[index].energy_cost;
    out_sample->heat_output = domain->tools[index].heat_output;
    out_sample->error_rate = domain->tools[index].error_rate;
    out_sample->bias = domain->tools[index].bias;
    out_sample->provenance_id = domain->tools[index].provenance_id;
    out_sample->region_id = domain->tools[index].region_id;
    out_sample->flags = domain->tools[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_toolchain_edge_query(const dom_standard_domain* domain,
                             u32 edge_id,
                             dom_domain_budget* budget,
                             dom_toolchain_edge_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_TOOLCHAIN_EDGE_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_edge_index(domain, edge_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->edges[index].region_id)) {
        out_sample->edge_id = domain->edges[index].edge_id;
        out_sample->region_id = domain->edges[index].region_id;
        out_sample->flags = DOM_TOOLCHAIN_EDGE_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->edge_id = domain->edges[index].edge_id;
    out_sample->from_tool_id = domain->edges[index].from_tool_id;
    out_sample->to_tool_id = domain->edges[index].to_tool_id;
    out_sample->input_standard_id = domain->edges[index].input_standard_id;
    out_sample->output_standard_id = domain->edges[index].output_standard_id;
    out_sample->compatibility_score = domain->edges[index].compatibility_score;
    out_sample->provenance_id = domain->edges[index].provenance_id;
    out_sample->region_id = domain->edges[index].region_id;
    out_sample->flags = domain->edges[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_toolchain_graph_query(const dom_standard_domain* domain,
                              u32 graph_id,
                              dom_domain_budget* budget,
                              dom_toolchain_graph_sample* out_sample)
{
    u32 cost;
    int index;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));
    out_sample->flags = DOM_TOOLCHAIN_GRAPH_UNRESOLVED;

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost = dom_standard_budget_cost(domain->policy.cost_full);
    if (!dom_domain_budget_consume(budget, cost)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    index = dom_standard_find_graph_index(domain, graph_id);
    if (index < 0) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_NO_SOURCE, budget);
        return 0;
    }

    if (dom_standard_region_collapsed(domain, domain->graphs[index].region_id)) {
        out_sample->graph_id = domain->graphs[index].graph_id;
        out_sample->region_id = domain->graphs[index].region_id;
        out_sample->flags = DOM_TOOLCHAIN_GRAPH_COLLAPSED;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost, budget);
        return 0;
    }

    out_sample->graph_id = domain->graphs[index].graph_id;
    out_sample->node_count = domain->graphs[index].node_count;
    out_sample->edge_count = domain->graphs[index].edge_count;
    out_sample->provenance_id = domain->graphs[index].provenance_id;
    out_sample->region_id = domain->graphs[index].region_id;
    out_sample->flags = domain->graphs[index].flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               DOM_DOMAIN_CONFIDENCE_EXACT, cost, budget);
    return 0;
}

int dom_standard_region_query(const dom_standard_domain* domain,
                              u32 region_id,
                              dom_domain_budget* budget,
                              dom_standard_region_sample* out_sample)
{
    u32 cost_base;
    u32 cost_definition;
    u32 cost_version;
    u32 cost_scope;
    u32 cost_event;
    u32 cost_tool;
    u32 cost_edge;
    u32 cost_graph;
    q48_16 adoption_total = 0;
    q48_16 compliance_total = 0;
    q48_16 lock_in_total = 0;
    q48_16 compatibility_total = 0;
    u32 compat_seen = 0u;
    u32 flags = 0u;
    if (!domain || !out_sample) {
        return -1;
    }
    memset(out_sample, 0, sizeof(*out_sample));

    if (!dom_standard_domain_is_active(domain)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE, budget);
        return 0;
    }

    cost_base = dom_standard_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        dom_standard_query_meta_refused(&out_sample->meta, DOM_DOMAIN_REFUSE_BUDGET, budget);
        return 0;
    }

    if (region_id != 0u && dom_standard_region_collapsed(domain, region_id)) {
        const dom_standard_macro_capsule* capsule = dom_standard_find_capsule(domain, region_id);
        if (capsule) {
            out_sample->region_id = capsule->region_id;
            out_sample->definition_count = capsule->definition_count;
            out_sample->version_count = capsule->version_count;
            out_sample->scope_count = capsule->scope_count;
            out_sample->event_count = capsule->event_count;
            out_sample->tool_count = capsule->tool_count;
            out_sample->edge_count = capsule->edge_count;
            out_sample->graph_count = capsule->graph_count;
            out_sample->adoption_avg = capsule->adoption_avg;
            out_sample->compliance_avg = capsule->compliance_avg;
            out_sample->lock_in_avg = capsule->lock_in_avg;
            out_sample->compatibility_avg = capsule->compatibility_avg;
            for (u32 i = 0u; i < DOM_STANDARD_EVENT_BINS; ++i) {
                out_sample->event_type_counts[i] = capsule->event_type_counts[i];
            }
        }
        out_sample->flags = DOM_STANDARD_RESOLVE_PARTIAL;
        dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                                   DOM_DOMAIN_CONFIDENCE_UNKNOWN, cost_base, budget);
        return 0;
    }

    cost_definition = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_version = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_scope = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_event = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_tool = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_edge = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_graph = dom_standard_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->definition_count; ++i) {
        u32 def_region = domain->definitions[i].region_id;
        if (region_id != 0u && def_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, def_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_definition)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        out_sample->definition_count += 1u;
    }

    for (u32 i = 0u; i < domain->version_count; ++i) {
        u32 ver_region = domain->versions[i].region_id;
        if (region_id != 0u && ver_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, ver_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_version)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->versions[i].compatibility_score));
        compat_seen += 1u;
        out_sample->version_count += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        u32 scope_region = domain->scopes[i].region_id;
        if (region_id != 0u && scope_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, scope_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_scope)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        adoption_total = d_q48_16_add(adoption_total,
                                      d_q48_16_from_q16_16(domain->scopes[i].adoption_rate));
        compliance_total = d_q48_16_add(compliance_total,
                                        d_q48_16_from_q16_16(domain->scopes[i].compliance_rate));
        lock_in_total = d_q48_16_add(lock_in_total,
                                     d_q48_16_from_q16_16(domain->scopes[i].lock_in_index));
        out_sample->scope_count += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        u32 event_region = domain->events[i].region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, event_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        out_sample->event_count += 1u;
        out_sample->event_type_counts[dom_standard_event_bin(domain->events[i].process_type)] += 1u;
    }

    for (u32 i = 0u; i < domain->tool_count; ++i) {
        u32 tool_region = domain->tools[i].region_id;
        if (region_id != 0u && tool_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, tool_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_tool)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        out_sample->tool_count += 1u;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        u32 edge_region = domain->edges[i].region_id;
        if (region_id != 0u && edge_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, edge_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_edge)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->edges[i].compatibility_score));
        compat_seen += 1u;
        out_sample->edge_count += 1u;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        u32 graph_region = domain->graphs[i].region_id;
        if (region_id != 0u && graph_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, graph_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_graph)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            break;
        }
        out_sample->graph_count += 1u;
    }

    out_sample->region_id = region_id;
    if (out_sample->scope_count > 0u) {
        out_sample->adoption_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(adoption_total,
                                             d_q48_16_from_int((i64)out_sample->scope_count))));
        out_sample->compliance_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compliance_total,
                                             d_q48_16_from_int((i64)out_sample->scope_count))));
        out_sample->lock_in_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(lock_in_total,
                                             d_q48_16_from_int((i64)out_sample->scope_count))));
    }
    if (compat_seen > 0u) {
        out_sample->compatibility_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compatibility_total,
                                             d_q48_16_from_int((i64)compat_seen))));
    }
    out_sample->flags = flags;
    dom_standard_query_meta_ok(&out_sample->meta, DOM_DOMAIN_RES_ANALYTIC,
                               flags ? DOM_DOMAIN_CONFIDENCE_UNKNOWN : DOM_DOMAIN_CONFIDENCE_EXACT,
                               cost_base, budget);
    return 0;
}

int dom_standard_resolve(dom_standard_domain* domain,
                         u32 region_id,
                         u64 tick,
                         u64 tick_delta,
                         dom_domain_budget* budget,
                         dom_standard_resolve_result* out_result)
{
    u32 cost_base;
    u32 cost_definition;
    u32 cost_version;
    u32 cost_scope;
    u32 cost_event;
    u32 cost_tool;
    u32 cost_edge;
    u32 cost_graph;
    q48_16 adoption_total = 0;
    q48_16 compliance_total = 0;
    q48_16 lock_in_total = 0;
    q48_16 compatibility_total = 0;
    u32 compat_seen = 0u;
    u32 flags = 0u;
    u32 revocations = 0u;
    if (!domain || !out_result) {
        return -1;
    }
    memset(out_result, 0, sizeof(*out_result));

    if (!dom_standard_domain_is_active(domain)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_STANDARD_REFUSE_DOMAIN_INACTIVE;
        return 0;
    }

    cost_base = dom_standard_budget_cost(domain->policy.cost_analytic);
    if (!dom_domain_budget_consume(budget, cost_base)) {
        out_result->ok = 0u;
        out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
        return 0;
    }

    if (region_id != 0u && dom_standard_region_collapsed(domain, region_id)) {
        const dom_standard_macro_capsule* capsule = dom_standard_find_capsule(domain, region_id);
        if (capsule) {
            out_result->definition_count = capsule->definition_count;
            out_result->version_count = capsule->version_count;
            out_result->scope_count = capsule->scope_count;
            out_result->event_count = capsule->event_count;
            out_result->tool_count = capsule->tool_count;
            out_result->edge_count = capsule->edge_count;
            out_result->graph_count = capsule->graph_count;
            out_result->adoption_avg = capsule->adoption_avg;
            out_result->compliance_avg = capsule->compliance_avg;
            out_result->lock_in_avg = capsule->lock_in_avg;
            out_result->compatibility_avg = capsule->compatibility_avg;
            for (u32 i = 0u; i < DOM_STANDARD_EVENT_BINS; ++i) {
                out_result->event_type_counts[i] = capsule->event_type_counts[i];
            }
        }
        out_result->ok = 1u;
        out_result->flags = DOM_STANDARD_RESOLVE_PARTIAL;
        return 0;
    }

    if (tick_delta == 0u) {
        tick_delta = 1u;
    }

    cost_definition = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_version = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_scope = dom_standard_budget_cost(domain->policy.cost_medium);
    cost_event = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_tool = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_edge = dom_standard_budget_cost(domain->policy.cost_coarse);
    cost_graph = dom_standard_budget_cost(domain->policy.cost_coarse);

    for (u32 i = 0u; i < domain->definition_count; ++i) {
        u32 def_region = domain->definitions[i].region_id;
        if (region_id != 0u && def_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, def_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_definition)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        out_result->definition_count += 1u;
    }

    for (u32 i = 0u; i < domain->version_count; ++i) {
        u32 ver_region = domain->versions[i].region_id;
        if (region_id != 0u && ver_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, ver_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_version)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->versions[i].compatibility_score));
        compat_seen += 1u;
        out_result->version_count += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        u32 scope_region = domain->scopes[i].region_id;
        if (region_id != 0u && scope_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, scope_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_scope)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        adoption_total = d_q48_16_add(adoption_total,
                                      d_q48_16_from_q16_16(domain->scopes[i].adoption_rate));
        compliance_total = d_q48_16_add(compliance_total,
                                        d_q48_16_from_q16_16(domain->scopes[i].compliance_rate));
        lock_in_total = d_q48_16_add(lock_in_total,
                                     d_q48_16_from_q16_16(domain->scopes[i].lock_in_index));
        out_result->scope_count += 1u;
    }

    for (u32 i = 0u; i < domain->event_count; ++i) {
        dom_standard_event* event = &domain->events[i];
        u32 event_region = event->region_id;
        if (region_id != 0u && event_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, event_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_event)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        out_result->event_count += 1u;
        if (dom_standard_apply_event(domain, event, tick, &flags, &revocations)) {
            out_result->event_applied_count += 1u;
            out_result->event_type_counts[dom_standard_event_bin(event->process_type)] += 1u;
        }
    }

    for (u32 i = 0u; i < domain->tool_count; ++i) {
        u32 tool_region = domain->tools[i].region_id;
        if (region_id != 0u && tool_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, tool_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_tool)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        out_result->tool_count += 1u;
    }

    for (u32 i = 0u; i < domain->edge_count; ++i) {
        u32 edge_region = domain->edges[i].region_id;
        if (region_id != 0u && edge_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, edge_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_edge)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->edges[i].compatibility_score));
        compat_seen += 1u;
        out_result->edge_count += 1u;
    }

    for (u32 i = 0u; i < domain->graph_count; ++i) {
        u32 graph_region = domain->graphs[i].region_id;
        if (region_id != 0u && graph_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, graph_region)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            continue;
        }
        if (!dom_domain_budget_consume(budget, cost_graph)) {
            flags |= DOM_STANDARD_RESOLVE_PARTIAL;
            if (out_result->refusal_reason == DOM_STANDARD_REFUSE_NONE) {
                out_result->refusal_reason = DOM_STANDARD_REFUSE_BUDGET;
            }
            break;
        }
        out_result->graph_count += 1u;
    }

    for (u32 i = 0u; i < domain->scope_count; ++i) {
        dom_standard_scope* scope = &domain->scopes[i];
        u32 scope_region = scope->region_id;
        if (region_id != 0u && scope_region != region_id) {
            continue;
        }
        if (region_id == 0u && dom_standard_region_collapsed(domain, scope_region)) {
            continue;
        }
        dom_standard_update_scope_flags(scope, dom_standard_find_version_for_scope(domain, scope));
    }

    out_result->ok = 1u;
    if (out_result->event_applied_count > 0u) {
        flags |= DOM_STANDARD_RESOLVE_EVENTS_APPLIED;
    }
    if (revocations > 0u) {
        flags |= DOM_STANDARD_RESOLVE_REVOCATION;
    }
    out_result->flags = flags;

    if (out_result->scope_count > 0u) {
        out_result->adoption_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(adoption_total,
                                             d_q48_16_from_int((i64)out_result->scope_count))));
        out_result->compliance_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compliance_total,
                                             d_q48_16_from_int((i64)out_result->scope_count))));
        out_result->lock_in_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(lock_in_total,
                                             d_q48_16_from_int((i64)out_result->scope_count))));
    }
    if (compat_seen > 0u) {
        out_result->compatibility_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compatibility_total,
                                             d_q48_16_from_int((i64)compat_seen))));
    }
    return 0;
}

int dom_standard_domain_collapse_region(dom_standard_domain* domain, u32 region_id)
{
    dom_standard_macro_capsule capsule;
    u32 adoption_bins[DOM_STANDARD_HIST_BINS];
    u32 compliance_bins[DOM_STANDARD_HIST_BINS];
    u32 lock_in_bins[DOM_STANDARD_HIST_BINS];
    q48_16 adoption_total = 0;
    q48_16 compliance_total = 0;
    q48_16 lock_in_total = 0;
    q48_16 compatibility_total = 0;
    u32 compat_seen = 0u;
    if (!domain || region_id == 0u) {
        return -1;
    }
    if (dom_standard_region_collapsed(domain, region_id)) {
        return 0;
    }
    if (domain->capsule_count >= DOM_STANDARD_MAX_CAPSULES) {
        return -2;
    }
    memset(adoption_bins, 0, sizeof(adoption_bins));
    memset(compliance_bins, 0, sizeof(compliance_bins));
    memset(lock_in_bins, 0, sizeof(lock_in_bins));
    memset(&capsule, 0, sizeof(capsule));
    capsule.capsule_id = (u64)region_id;
    capsule.region_id = region_id;

    for (u32 i = 0u; i < domain->definition_count; ++i) {
        if (domain->definitions[i].region_id != region_id) {
            continue;
        }
        capsule.definition_count += 1u;
    }
    for (u32 i = 0u; i < domain->version_count; ++i) {
        if (domain->versions[i].region_id != region_id) {
            continue;
        }
        capsule.version_count += 1u;
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->versions[i].compatibility_score));
        compat_seen += 1u;
    }
    for (u32 i = 0u; i < domain->scope_count; ++i) {
        if (domain->scopes[i].region_id != region_id) {
            continue;
        }
        capsule.scope_count += 1u;
        adoption_total = d_q48_16_add(adoption_total,
                                      d_q48_16_from_q16_16(domain->scopes[i].adoption_rate));
        compliance_total = d_q48_16_add(compliance_total,
                                        d_q48_16_from_q16_16(domain->scopes[i].compliance_rate));
        lock_in_total = d_q48_16_add(lock_in_total,
                                     d_q48_16_from_q16_16(domain->scopes[i].lock_in_index));
        adoption_bins[dom_standard_hist_bin(domain->scopes[i].adoption_rate)] += 1u;
        compliance_bins[dom_standard_hist_bin(domain->scopes[i].compliance_rate)] += 1u;
        lock_in_bins[dom_standard_hist_bin(domain->scopes[i].lock_in_index)] += 1u;
    }
    for (u32 i = 0u; i < domain->event_count; ++i) {
        if (domain->events[i].region_id != region_id) {
            continue;
        }
        capsule.event_count += 1u;
        capsule.event_type_counts[dom_standard_event_bin(domain->events[i].process_type)] += 1u;
    }
    for (u32 i = 0u; i < domain->tool_count; ++i) {
        if (domain->tools[i].region_id != region_id) {
            continue;
        }
        capsule.tool_count += 1u;
    }
    for (u32 i = 0u; i < domain->edge_count; ++i) {
        if (domain->edges[i].region_id != region_id) {
            continue;
        }
        capsule.edge_count += 1u;
        compatibility_total = d_q48_16_add(compatibility_total,
                                           d_q48_16_from_q16_16(domain->edges[i].compatibility_score));
        compat_seen += 1u;
    }
    for (u32 i = 0u; i < domain->graph_count; ++i) {
        if (domain->graphs[i].region_id != region_id) {
            continue;
        }
        capsule.graph_count += 1u;
    }

    if (capsule.scope_count > 0u) {
        capsule.adoption_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(adoption_total,
                                             d_q48_16_from_int((i64)capsule.scope_count))));
        capsule.compliance_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compliance_total,
                                             d_q48_16_from_int((i64)capsule.scope_count))));
        capsule.lock_in_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(lock_in_total,
                                             d_q48_16_from_int((i64)capsule.scope_count))));
    }
    if (compat_seen > 0u) {
        capsule.compatibility_avg = dom_standard_clamp_ratio(
            d_q16_16_from_q48_16(d_q48_16_div(compatibility_total,
                                             d_q48_16_from_int((i64)compat_seen))));
    }
    for (u32 b = 0u; b < DOM_STANDARD_HIST_BINS; ++b) {
        capsule.adoption_hist[b] = dom_standard_hist_bin_ratio(adoption_bins[b], capsule.scope_count);
        capsule.compliance_hist[b] = dom_standard_hist_bin_ratio(compliance_bins[b], capsule.scope_count);
        capsule.lock_in_hist[b] = dom_standard_hist_bin_ratio(lock_in_bins[b], capsule.scope_count);
    }
    domain->capsules[domain->capsule_count++] = capsule;
    return 0;
}

int dom_standard_domain_expand_region(dom_standard_domain* domain, u32 region_id)
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

u32 dom_standard_domain_capsule_count(const dom_standard_domain* domain)
{
    return domain ? domain->capsule_count : 0u;
}

const dom_standard_macro_capsule* dom_standard_domain_capsule_at(const dom_standard_domain* domain,
                                                                 u32 index)
{
    if (!domain || index >= domain->capsule_count) {
        return (const dom_standard_macro_capsule*)0;
    }
    return &domain->capsules[index];
}
