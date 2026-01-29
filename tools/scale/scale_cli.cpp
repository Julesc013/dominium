#include "scale/scale_cli.h"

#include "domino/sim/sim.h"
#include "dominium/interest_set.h"
#include "dominium/rules/scale/scale_collapse_expand.h"

static void scale_macro_override_interval(dom_scale_context* ctx,
                                          dom_act_time_t interval);

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SCALE_CONSTCOST_MAX_DOMAINS 64u
#define SCALE_CONSTCOST_EVENT_CAP 2048u

static u64 scale_fnv1a64_init(void)
{
    return 0xcbf29ce484222325ull;
}

static u64 scale_hash_u64(u64 hash, u64 value)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((value >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((value >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((value >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((value >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((value >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((value >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((value >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(value & 0xFFu);
    for (size_t i = 0; i < sizeof(bytes); ++i) {
        hash ^= (u64)bytes[i];
        hash *= 0x100000001b3ull;
    }
    return hash;
}

static u64 scale_hash_bytes(u64 hash, const unsigned char* bytes, u32 len)
{
    if (!bytes) {
        return hash;
    }
    for (u32 i = 0u; i < len; ++i) {
        hash ^= (u64)bytes[i];
        hash *= 0x100000001b3ull;
    }
    return hash;
}

static int scale_parse_u32(const char* text, u32* out_value)
{
    const char* p = text;
    u64 value = 0u;
    if (!text || !out_value || *text == '\0') {
        return 0;
    }
    while (*p) {
        char c = *p++;
        if (c < '0' || c > '9') {
            return 0;
        }
        value = value * 10u + (u64)(c - '0');
    }
    *out_value = (u32)value;
    return 1;
}

static u32 scale_parse_workers(int argc, char** argv, u32 default_workers)
{
    u32 workers = default_workers;
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], "--workers") == 0 && i + 1 < argc) {
            u32 parsed = 0u;
            if (scale_parse_u32(argv[i + 1], &parsed) && parsed > 0u) {
                workers = parsed;
            }
        }
    }
    return workers;
}

static u32 scale_parse_domain_kind(const char* text)
{
    if (!text) {
        return 0u;
    }
    if (strcmp(text, "resources") == 0) {
        return DOM_SCALE_DOMAIN_RESOURCES;
    }
    if (strcmp(text, "network") == 0) {
        return DOM_SCALE_DOMAIN_NETWORK;
    }
    if (strcmp(text, "agents") == 0) {
        return DOM_SCALE_DOMAIN_AGENTS;
    }
    return 0u;
}

static const char* scale_domain_name(u32 kind)
{
    switch (kind) {
    case DOM_SCALE_DOMAIN_RESOURCES: return "resources";
    case DOM_SCALE_DOMAIN_NETWORK: return "network";
    case DOM_SCALE_DOMAIN_AGENTS: return "agents";
    default: break;
    }
    return "unknown";
}

static const char* scale_event_kind_to_string(u32 kind)
{
    switch (kind) {
    case DOM_SCALE_EVENT_COLLAPSE: return "collapse";
    case DOM_SCALE_EVENT_EXPAND: return "expand";
    case DOM_SCALE_EVENT_REFUSAL: return "refusal";
    case DOM_SCALE_EVENT_DEFER: return "defer";
    case DOM_SCALE_EVENT_MACRO_SCHEDULE: return "macro_schedule";
    case DOM_SCALE_EVENT_MACRO_EXECUTE: return "macro_execute";
    case DOM_SCALE_EVENT_MACRO_COMPACT: return "macro_compact";
    default: break;
    }
    return "unknown";
}

static const char* scale_budget_kind_to_string(u32 kind)
{
    switch (kind) {
    case DOM_SCALE_BUDGET_ACTIVE_DOMAIN: return "active_domain";
    case DOM_SCALE_BUDGET_REFINEMENT: return "refinement";
    case DOM_SCALE_BUDGET_COLLAPSE: return "collapse";
    case DOM_SCALE_BUDGET_MACRO_EVENT: return "macro_event";
    case DOM_SCALE_BUDGET_AGENT_PLANNING: return "agent_planning";
    case DOM_SCALE_BUDGET_SNAPSHOT: return "snapshot";
    case DOM_SCALE_BUDGET_DEFER_QUEUE: return "defer_queue";
    default: break;
    }
    return "none";
}

static const char* scale_deferred_kind_to_string(u32 kind)
{
    switch (kind) {
    case DOM_SCALE_DEFERRED_COLLAPSE: return "collapse";
    case DOM_SCALE_DEFERRED_EXPAND: return "expand";
    case DOM_SCALE_DEFERRED_MACRO_EVENT: return "macro_event";
    case DOM_SCALE_DEFERRED_PLANNING: return "planning";
    case DOM_SCALE_DEFERRED_SNAPSHOT: return "snapshot";
    default: break;
    }
    return "unknown";
}

static d_world* scale_make_world(void)
{
    d_world_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.seed = 123u;
    cfg.width = 1u;
    cfg.height = 1u;
    return d_world_create_from_config(&cfg);
}

static u64 scale_global_hash(dom_scale_domain_slot* domains,
                             u32 domain_count,
                             dom_act_time_t tick,
                             u32 workers)
{
    u64 hash = scale_fnv1a64_init();
    for (u32 i = 0u; i < domain_count; ++i) {
        u64 domain_hash = dom_scale_domain_hash(&domains[i], tick, workers);
        hash = scale_hash_u64(hash, domain_hash);
    }
    return hash;
}

static u64 scale_event_log_hash(const dom_scale_event_log* log)
{
    u64 hash = scale_fnv1a64_init();
    if (!log || !log->events) {
        return hash;
    }
    hash = scale_hash_u64(hash, log->count);
    hash = scale_hash_u64(hash, log->overflow);
    for (u32 i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        hash = scale_hash_u64(hash, ev->kind);
        hash = scale_hash_u64(hash, ev->domain_id);
        hash = scale_hash_u64(hash, ev->domain_kind);
        hash = scale_hash_u64(hash, ev->capsule_id);
        hash = scale_hash_u64(hash, ev->reason_code);
        hash = scale_hash_u64(hash, ev->refusal_code);
        hash = scale_hash_u64(hash, ev->defer_code);
        hash = scale_hash_u64(hash, ev->detail_code);
        hash = scale_hash_u64(hash, ev->seed_value);
        hash = scale_hash_u64(hash, ev->budget_kind);
        hash = scale_hash_u64(hash, ev->budget_limit);
        hash = scale_hash_u64(hash, ev->budget_used);
        hash = scale_hash_u64(hash, ev->budget_cost);
        hash = scale_hash_u64(hash, ev->budget_queue);
        hash = scale_hash_u64(hash, ev->budget_overflow);
        hash = scale_hash_u64(hash, (u64)ev->tick);
    }
    return hash;
}

static void scale_print_timeline(const dom_scale_event_log* log)
{
    if (!log || !log->events) {
        return;
    }
    for (u32 i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        if (ev->budget_kind != DOM_SCALE_BUDGET_NONE) {
            printf("event[%u]=%s tick=%lld domain=%llu capsule=%llu refusal=%s defer=%s detail=%u budget=%s used=%u limit=%u cost=%u queue=%u overflow=%u\n",
                   i,
                   scale_event_kind_to_string(ev->kind),
                   (long long)ev->tick,
                   (unsigned long long)ev->domain_id,
                   (unsigned long long)ev->capsule_id,
                   dom_scale_refusal_to_string(ev->refusal_code),
                   dom_scale_defer_to_string(ev->defer_code),
                   (unsigned int)ev->detail_code,
                   scale_budget_kind_to_string(ev->budget_kind),
                   (unsigned int)ev->budget_used,
                   (unsigned int)ev->budget_limit,
                   (unsigned int)ev->budget_cost,
                   (unsigned int)ev->budget_queue,
                   (unsigned int)ev->budget_overflow);
        } else {
            printf("event[%u]=%s tick=%lld domain=%llu capsule=%llu refusal=%s defer=%s detail=%u\n",
                   i,
                   scale_event_kind_to_string(ev->kind),
                   (long long)ev->tick,
                   (unsigned long long)ev->domain_id,
                   (unsigned long long)ev->capsule_id,
                   dom_scale_refusal_to_string(ev->refusal_code),
                   dom_scale_defer_to_string(ev->defer_code),
                   (unsigned int)ev->detail_code);
        }
    }
}

static u32 scale_init_resource_domain(dom_scale_domain_slot* slot,
                                      dom_scale_resource_entry* entries,
                                      u32 capacity)
{
    u32 count = capacity < 3u ? capacity : 3u;
    if (!slot || !entries || capacity == 0u) {
        return 0u;
    }
    memset(slot, 0, sizeof(*slot));
    entries[0].resource_id = 1u;
    entries[0].quantity = 100u;
    if (count > 1u) {
        entries[1].resource_id = 2u;
        entries[1].quantity = 5u;
    }
    if (count > 2u) {
        entries[2].resource_id = 3u;
        entries[2].quantity = 2000u;
    }
    slot->domain_id = 1001u;
    slot->domain_kind = DOM_SCALE_DOMAIN_RESOURCES;
    slot->tier = DOM_FID_MESO;
    slot->last_transition_tick = 0;
    slot->resources.entries = entries;
    slot->resources.capacity = capacity;
    slot->resources.count = count;
    return count;
}

static u32 scale_init_resource_domain_with_id(dom_scale_domain_slot* slot,
                                              dom_scale_resource_entry* entries,
                                              u32 capacity,
                                              u64 domain_id,
                                              u32 quantity_bias)
{
    u32 count = scale_init_resource_domain(slot, entries, capacity);
    if (!slot || count == 0u) {
        return 0u;
    }
    slot->domain_id = domain_id;
    entries[0].quantity += (u64)quantity_bias;
    if (count > 1u) {
        entries[1].quantity += (u64)(quantity_bias % 7u);
    }
    if (count > 2u) {
        entries[2].quantity += (u64)(quantity_bias % 13u);
    }
    slot->resources.count = count;
    return count;
}

static void scale_init_network_domain(dom_scale_domain_slot* slot,
                                      dom_scale_network_node* nodes,
                                      u32 node_capacity,
                                      dom_scale_network_edge* edges,
                                      u32 edge_capacity)
{
    if (!slot || !nodes || !edges || node_capacity < 2u || edge_capacity < 2u) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    nodes[0].node_id = 10u;
    nodes[0].node_kind = 1u;
    nodes[1].node_id = 20u;
    nodes[1].node_kind = 1u;
    edges[0].edge_id = 100u;
    edges[0].from_node_id = 10u;
    edges[0].to_node_id = 20u;
    edges[0].capacity_units = 1000u;
    edges[0].buffer_units = 200u;
    edges[0].wear_bucket0 = 1u;
    edges[0].wear_bucket1 = 2u;
    edges[0].wear_bucket2 = 3u;
    edges[0].wear_bucket3 = 4u;
    edges[1].edge_id = 200u;
    edges[1].from_node_id = 20u;
    edges[1].to_node_id = 10u;
    edges[1].capacity_units = 500u;
    edges[1].buffer_units = 100u;
    edges[1].wear_bucket0 = 2u;
    edges[1].wear_bucket1 = 1u;
    edges[1].wear_bucket2 = 1u;
    edges[1].wear_bucket3 = 0u;
    slot->domain_id = 2001u;
    slot->domain_kind = DOM_SCALE_DOMAIN_NETWORK;
    slot->tier = DOM_FID_MICRO;
    slot->last_transition_tick = 0;
    slot->network.nodes = nodes;
    slot->network.node_capacity = node_capacity;
    slot->network.node_count = 2u;
    slot->network.edges = edges;
    slot->network.edge_capacity = edge_capacity;
    slot->network.edge_count = 2u;
}

static void scale_init_agent_domain(dom_scale_domain_slot* slot,
                                    dom_scale_agent_entry* agents,
                                    u32 capacity)
{
    if (!slot || !agents || capacity < 4u) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    agents[0].agent_id = 30001u;
    agents[0].role_id = 1u;
    agents[0].trait_mask = 1u;
    agents[0].planning_bucket = 2u;
    agents[1].agent_id = 30002u;
    agents[1].role_id = 1u;
    agents[1].trait_mask = 2u;
    agents[1].planning_bucket = 1u;
    agents[2].agent_id = 30003u;
    agents[2].role_id = 2u;
    agents[2].trait_mask = 1u;
    agents[2].planning_bucket = 3u;
    agents[3].agent_id = 30004u;
    agents[3].role_id = 2u;
    agents[3].trait_mask = 1u;
    agents[3].planning_bucket = 1u;
    slot->domain_id = 3001u;
    slot->domain_kind = DOM_SCALE_DOMAIN_AGENTS;
    slot->tier = DOM_FID_MESO;
    slot->last_transition_tick = 0;
    slot->agents.entries = agents;
    slot->agents.capacity = capacity;
    slot->agents.count = 4u;
}

static int scale_run_collapse_expand(u32 domain_kind,
                                     u32 workers,
                                     int show_summary,
                                     int show_timeline)
{
    const dom_act_time_t now_tick = 10;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[1];
    dom_interest_state interest_storage[1];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[32];
    dom_scale_commit_token token;
    dom_scale_domain_slot slot_init;
    dom_scale_domain_slot* slot = 0;
    dom_scale_operation_result collapse_res;
    dom_scale_operation_result expand_res;
    dom_macro_capsule_blob blob;
    dom_scale_capsule_summary summary;
    u64 hash_before = 0u;
    u64 hash_after = 0u;
    int hash_match = 0;
    int success = 0;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           now_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;

    memset(&slot_init, 0, sizeof(slot_init));
    if (domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        (void)scale_init_resource_domain(&slot_init, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    } else if (domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        scale_init_network_domain(&slot_init,
                                  nodes,
                                  (u32)(sizeof(nodes) / sizeof(nodes[0])),
                                  edges,
                                  (u32)(sizeof(edges) / sizeof(edges[0])));
    } else if (domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        scale_init_agent_domain(&slot_init, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
    } else {
        fprintf(stderr, "scale: unsupported domain kind\n");
        return 2;
    }

    if (dom_scale_register_domain(&ctx, &slot_init) != 0) {
        fprintf(stderr, "scale: failed to register domain\n");
        return 2;
    }
    slot = dom_scale_find_domain(&ctx, slot_init.domain_id);
    if (!slot) {
        fprintf(stderr, "scale: domain not found after register\n");
        return 2;
    }

    hash_before = dom_scale_domain_hash(slot, now_tick, workers);
    dom_scale_commit_token_make(&token, now_tick, 0u);
    memset(&collapse_res, 0, sizeof(collapse_res));
    memset(&expand_res, 0, sizeof(expand_res));
    (void)dom_scale_collapse_domain(&ctx, &token, slot->domain_id, 1u, &collapse_res);
    (void)dom_scale_expand_domain(&ctx, &token, slot->capsule_id, DOM_FID_MICRO, 2u, &expand_res);
    hash_after = dom_scale_domain_hash(slot, now_tick, workers);
    hash_match = (hash_before == hash_after) ? 1 : 0;
    success = (collapse_res.refusal_code == 0u &&
               collapse_res.defer_code == 0u &&
               expand_res.refusal_code == 0u &&
               expand_res.defer_code == 0u &&
               hash_match);

    printf("scenario=collapse_expand domain=%s domain_kind=%u workers=%u invariants=%s\n",
           scale_domain_name(domain_kind),
           domain_kind,
           workers,
           "SCALE0-PROJECTION-001,SCALE0-CONSERVE-002,SCALE0-COMMIT-003,SCALE0-DETERMINISM-004,SCALE0-NO-EXNIHILO-007,SCALE0-REPLAY-008");
    printf("collapse_refusal=%s collapse_defer=%s expand_refusal=%s expand_defer=%s\n",
           dom_scale_refusal_to_string(collapse_res.refusal_code),
           dom_scale_defer_to_string(collapse_res.defer_code),
           dom_scale_refusal_to_string(expand_res.refusal_code),
           dom_scale_defer_to_string(expand_res.defer_code));
    printf("hash_before=%llu hash_after=%llu hash_match=%u capsule_id=%llu capsule_hash=%llu\n",
           (unsigned long long)hash_before,
           (unsigned long long)hash_after,
           (unsigned int)hash_match,
           (unsigned long long)expand_res.capsule_id,
           (unsigned long long)expand_res.capsule_hash);

    memset(&blob, 0, sizeof(blob));
    memset(&summary, 0, sizeof(summary));
    if (show_summary &&
        dom_macro_capsule_store_get_blob(world, expand_res.capsule_id, &blob) &&
        dom_scale_capsule_summarize(blob.bytes, blob.byte_count, &summary) == 0) {
        printf("summary.capsule_id=%llu summary.domain_id=%llu summary.domain_kind=%u summary.source_tick=%lld summary.invariant_hash=%llu summary.statistic_hash=%llu\n",
               (unsigned long long)summary.capsule_id,
               (unsigned long long)summary.domain_id,
               (unsigned int)summary.domain_kind,
               (long long)summary.source_tick,
               (unsigned long long)summary.invariant_hash,
               (unsigned long long)summary.statistic_hash);
        printf("summary.invariant_count=%u summary.statistic_count=%u\n",
               (unsigned int)summary.invariant_count,
               (unsigned int)summary.statistic_count);
    }

    if (show_timeline) {
        scale_print_timeline(&event_log);
    }

    return success ? 0 : 1;
}

static int scale_collapse_and_summary(u32 domain_kind,
                                      u32 workers,
                                      u32 variant,
                                      dom_scale_capsule_summary* out_summary,
                                      u64* out_capsule_hash)
{
    const dom_act_time_t now_tick = 10;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[1];
    dom_interest_state interest_storage[1];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[16];
    dom_scale_commit_token token;
    dom_scale_domain_slot slot_init;
    dom_scale_operation_result collapse_res;
    dom_macro_capsule_blob blob;
    dom_scale_capsule_summary summary;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           now_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;

    memset(&slot_init, 0, sizeof(slot_init));
    if (domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
        (void)scale_init_resource_domain(&slot_init, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
        resources[0].quantity += variant;
    } else if (domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
        scale_init_network_domain(&slot_init,
                                  nodes,
                                  (u32)(sizeof(nodes) / sizeof(nodes[0])),
                                  edges,
                                  (u32)(sizeof(edges) / sizeof(edges[0])));
        edges[0].buffer_units += variant;
    } else if (domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
        scale_init_agent_domain(&slot_init, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
        agents[0].trait_mask += variant;
    } else {
        return 0;
    }

    if (dom_scale_register_domain(&ctx, &slot_init) != 0) {
        return 0;
    }

    dom_scale_commit_token_make(&token, now_tick, 0u);
    memset(&collapse_res, 0, sizeof(collapse_res));
    (void)dom_scale_collapse_domain(&ctx, &token, slot_init.domain_id, 1u, &collapse_res);
    if (collapse_res.refusal_code != 0u || collapse_res.defer_code != 0u) {
        return 0;
    }

    memset(&blob, 0, sizeof(blob));
    memset(&summary, 0, sizeof(summary));
    if (!dom_macro_capsule_store_get_blob(world, collapse_res.capsule_id, &blob)) {
        return 0;
    }
    if (dom_scale_capsule_summarize(blob.bytes, blob.byte_count, &summary) != 0) {
        return 0;
    }

    if (out_summary) {
        *out_summary = summary;
    }
    if (out_capsule_hash) {
        *out_capsule_hash = collapse_res.capsule_hash;
    }
    return 1;
}

static int scale_run_diff(u32 domain_kind, u32 workers)
{
    dom_scale_capsule_summary a;
    dom_scale_capsule_summary b;
    u64 hash_a = 0u;
    u64 hash_b = 0u;
    int ok_a = 0;
    int ok_b = 0;
    memset(&a, 0, sizeof(a));
    memset(&b, 0, sizeof(b));
    ok_a = scale_collapse_and_summary(domain_kind, workers, 0u, &a, &hash_a);
    ok_b = scale_collapse_and_summary(domain_kind, workers, 1u, &b, &hash_b);
    if (!ok_a || !ok_b) {
        fprintf(stderr, "scale: diff setup failed\n");
        return 2;
    }
    printf("scenario=diff domain=%s domain_kind=%u workers=%u invariants=%s\n",
           scale_domain_name(domain_kind),
           domain_kind,
           workers,
           "SCALE0-PROJECTION-001,SCALE0-CONSERVE-002,SCALE0-REPLAY-008");
    printf("capsule_a=%llu capsule_b=%llu capsule_hash_a=%llu capsule_hash_b=%llu\n",
           (unsigned long long)a.capsule_id,
           (unsigned long long)b.capsule_id,
           (unsigned long long)hash_a,
           (unsigned long long)hash_b);
    printf("invariant_hash_equal=%u statistic_hash_equal=%u capsule_hash_equal=%u\n",
           (unsigned int)(a.invariant_hash == b.invariant_hash),
           (unsigned int)(a.statistic_hash == b.statistic_hash),
           (unsigned int)(hash_a == hash_b));
    return 0;
}

static int scale_run_interest(u32 workers, const char* pattern)
{
    const dom_act_time_t now_tick = 10;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[2];
    dom_interest_state interest_storage[2];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[32];
    dom_scale_commit_token token;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_agent_entry agents[8];
    dom_scale_operation_result results[4];
    dom_interest_set interest;
    u64 global_hash = 0u;
    u64 target_domain_id = 0u;

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           now_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        fprintf(stderr, "scale: interest register failed\n");
        return 2;
    }

    dom_scale_commit_token_make(&token, now_tick, 0u);
    (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u, 0);

    dom_interest_set_init(&interest);
    (void)dom_interest_set_reserve(&interest, 4u);
    target_domain_id = (pattern && (strcmp(pattern, "B") == 0 || strcmp(pattern, "b") == 0))
                           ? agent_slot.domain_id
                           : res_slot.domain_id;
    (void)dom_interest_set_add(&interest,
                               DOM_INTEREST_TARGET_REGION,
                               target_domain_id,
                               DOM_INTEREST_REASON_PLAYER_FOCUS,
                               DOM_INTEREST_STRENGTH_HIGH,
                               DOM_INTEREST_PERSISTENT);
    dom_interest_set_finalize(&interest);

    memset(results, 0, sizeof(results));
    (void)dom_scale_apply_interest(&ctx, &token, &interest, results, (u32)(sizeof(results) / sizeof(results[0])));
    dom_interest_set_free(&interest);

    global_hash = scale_global_hash(domain_storage, ctx.domain_count, now_tick, workers);
    printf("scenario=interest pattern=%s workers=%u invariants=%s global_hash=%llu\n",
           pattern ? pattern : "A",
           workers,
           "SCALE0-INTEREST-006,SCALE0-CONSERVE-002,SCALE0-COMMIT-003",
           (unsigned long long)global_hash);
    return 0;
}

static int scale_run_refusal(u32 workers, const char* case_name)
{
    const dom_act_time_t now_tick = 10;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[2];
    dom_interest_state interest_storage[2];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[64];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot slot_a;
    dom_scale_domain_slot slot_b;
    dom_scale_operation_result result_a;
    dom_scale_operation_result result_b;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];
    const char* case_token = case_name ? case_name : "budget";
    u32 log_refusal = 0u;
    u32 log_defer = 0u;

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           now_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;

    memset(&slot_a, 0, sizeof(slot_a));
    memset(&slot_b, 0, sizeof(slot_b));
    (void)scale_init_resource_domain(&slot_a, resources, (u32)(sizeof(resources) / sizeof(resources[0])));

    if (case_name && (strcmp(case_name, "planning") == 0 || strcmp(case_name, "agent_planning") == 0)) {
        (void)scale_init_agent_domain(&slot_a, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
        case_token = "planning";
    }
    if (case_name && (strcmp(case_name, "unsupported") == 0 || strcmp(case_name, "unsupported_domain") == 0)) {
        slot_a.domain_kind = 99u;
        case_token = "unsupported";
    }

    if (dom_scale_register_domain(&ctx, &slot_a) != 0) {
        fprintf(stderr, "scale: refusal register failed\n");
        return 2;
    }

    if (!case_name || strcmp(case_name, "budget") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 1u;
        ctx.budget_policy.collapse_cost_units = 2u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        case_token = "budget";
    } else if (strcmp(case_name, "snapshot") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 100u;
        ctx.budget_policy.snapshot_budget_per_tick = 1u;
        ctx.budget_policy.snapshot_cost_units = 2u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        case_token = "snapshot";
    } else if (strcmp(case_name, "refinement") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 100u;
        ctx.budget_policy.snapshot_budget_per_tick = 100u;
        ctx.budget_policy.refinement_budget_per_tick = 1u;
        ctx.budget_policy.refinement_cost_units = 2u;
        ctx.budget_policy.expand_budget_per_tick = 100u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        case_token = "refinement";
    } else if (strcmp(case_name, "macro") == 0 || strcmp(case_name, "macro_event") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 100u;
        ctx.budget_policy.snapshot_budget_per_tick = 100u;
        ctx.budget_policy.macro_event_budget_per_tick = 1u;
        ctx.budget_policy.macro_event_cost_units = 2u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        case_token = "macro";
    } else if (strcmp(case_name, "planning") == 0 || strcmp(case_name, "agent_planning") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 100u;
        ctx.budget_policy.snapshot_budget_per_tick = 100u;
        ctx.budget_policy.refinement_budget_per_tick = 100u;
        ctx.budget_policy.expand_budget_per_tick = 100u;
        ctx.budget_policy.planning_budget_per_tick = 1u;
        ctx.budget_policy.planning_cost_units = 2u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        case_token = "planning";
    } else if (strcmp(case_name, "active") == 0 || strcmp(case_name, "active_domain") == 0) {
        ctx.budget_policy.active_domain_budget = 1u;
        ctx.budget_policy.collapse_budget_per_tick = 100u;
        ctx.budget_policy.snapshot_budget_per_tick = 100u;
        ctx.budget_policy.refinement_budget_per_tick = 100u;
        ctx.budget_policy.expand_budget_per_tick = 100u;
        ctx.budget_policy.deferred_queue_limit = 0u;
        scale_init_network_domain(&slot_b,
                                  nodes,
                                  (u32)(sizeof(nodes) / sizeof(nodes[0])),
                                  edges,
                                  (u32)(sizeof(edges) / sizeof(edges[0])));
        if (dom_scale_register_domain(&ctx, &slot_b) != 0) {
            fprintf(stderr, "scale: refusal register failed\n");
            return 2;
        }
        case_token = "active";
    } else if (strcmp(case_name, "tier2") == 0 || strcmp(case_name, "tier2_interest") == 0) {
        interest_storage[0].state = DOM_REL_HOT;
        interest_storage[0].last_change_tick = now_tick;
        case_token = "tier2";
    }

    dom_scale_commit_token_make(&token, now_tick, 0u);

    memset(&result_a, 0, sizeof(result_a));
    memset(&result_b, 0, sizeof(result_b));
    (void)dom_scale_collapse_domain(&ctx, &token, slot_a.domain_id, 1u, &result_a);

    if (strcmp(case_token, "refinement") == 0 || strcmp(case_token, "planning") == 0) {
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[0].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &result_a);
    } else if (strcmp(case_token, "active") == 0) {
        (void)dom_scale_collapse_domain(&ctx, &token, slot_b.domain_id, 1u, &result_b);
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[0].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &result_a);
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[1].capsule_id,
                                      DOM_FID_MICRO,
                                      3u,
                                      &result_b);
    } else if (strcmp(case_token, "macro") == 0) {
        dom_scale_macro_policy_default(&macro_policy);
        macro_policy.macro_interval_ticks = 1;
        scale_macro_override_interval(&ctx, macro_policy.macro_interval_ticks);
        ctx.now_tick = now_tick + 8;
        dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
        (void)dom_scale_macro_advance(&ctx, &token, ctx.now_tick, &macro_policy, 0);
    }

    for (u32 i = 0u; i < event_log.count; ++i) {
        const dom_scale_event* ev = &event_log.events[i];
        if (ev->refusal_code != 0u) {
            log_refusal = ev->refusal_code;
        }
        if (ev->defer_code != 0u) {
            log_defer = ev->defer_code;
        }
    }

    if (result_b.refusal_code != 0u) {
        log_refusal = result_b.refusal_code;
    } else if (result_a.refusal_code != 0u) {
        log_refusal = result_a.refusal_code;
    }
    if (result_b.defer_code != 0u) {
        log_defer = result_b.defer_code;
    } else if (result_a.defer_code != 0u) {
        log_defer = result_a.defer_code;
    }

    printf("scenario=refusal case=%s workers=%u invariants=%s refusal=%s refusal_code=%u defer=%s\n",
           case_token,
           workers,
           "SCALE0-CONSERVE-002,SCALE0-COMMIT-003,SCALE0-REPLAY-008,SCALE3-ADMISSION-010",
           dom_scale_refusal_to_string(log_refusal),
           (unsigned int)log_refusal,
           dom_scale_defer_to_string(log_defer));
    scale_print_timeline(&event_log);
    return 0;
}

static void scale_print_budget_snapshot(const dom_scale_budget_snapshot* snap)
{
    if (!snap) {
        return;
    }
    printf("budget.tick=%lld tier2=%u/%u tier1=%u/%u refinement=%u/%u planning=%u/%u collapse=%u/%u expand=%u/%u macro=%u/%u snapshot=%u/%u deferred=%u/%u deferred_overflow=%u refusals_active=%u refusals_refine=%u refusals_macro=%u refusals_planning=%u refusals_snapshot=%u refusals_collapse=%u refusals_defer_limit=%u\n",
           (long long)snap->tick,
           (unsigned int)snap->active_tier2_domains,
           (unsigned int)snap->tier2_limit,
           (unsigned int)snap->active_tier1_domains,
           (unsigned int)snap->tier1_limit,
           (unsigned int)snap->refinement_used,
           (unsigned int)snap->refinement_limit,
           (unsigned int)snap->planning_used,
           (unsigned int)snap->planning_limit,
           (unsigned int)snap->collapse_used,
           (unsigned int)snap->collapse_limit,
           (unsigned int)snap->expand_used,
           (unsigned int)snap->expand_limit,
           (unsigned int)snap->macro_event_used,
           (unsigned int)snap->macro_event_limit,
           (unsigned int)snap->snapshot_used,
           (unsigned int)snap->snapshot_limit,
           (unsigned int)snap->deferred_count,
           (unsigned int)snap->deferred_limit,
           (unsigned int)snap->deferred_overflow,
           (unsigned int)snap->refusal_active_domain_limit,
           (unsigned int)snap->refusal_refinement_budget,
           (unsigned int)snap->refusal_macro_event_budget,
           (unsigned int)snap->refusal_agent_planning_budget,
           (unsigned int)snap->refusal_snapshot_budget,
           (unsigned int)snap->refusal_collapse_budget,
           (unsigned int)snap->refusal_defer_queue_limit);
}

static void scale_print_deferred_ops(const dom_scale_context* ctx)
{
    u32 count;
    if (!ctx) {
        return;
    }
    count = dom_scale_deferred_count(ctx);
    printf("deferred.count=%u\n", (unsigned int)count);
    for (u32 i = 0u; i < count; ++i) {
        dom_scale_deferred_op op;
        if (!dom_scale_deferred_get(ctx, i, &op)) {
            continue;
        }
        printf("deferred[%u]=%s budget=%s domain=%llu capsule=%llu tier=%u requested_tick=%lld reason=%u\n",
               (unsigned int)i,
               scale_deferred_kind_to_string(op.kind),
               scale_budget_kind_to_string(op.budget_kind),
               (unsigned long long)op.domain_id,
               (unsigned long long)op.capsule_id,
               (unsigned int)op.target_tier,
               (long long)op.requested_tick,
               (unsigned int)op.reason_code);
    }
}

static int scale_run_budgets(u32 workers, dom_act_time_t target_tick)
{
    const dom_act_time_t start_tick = 0;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[3];
    dom_interest_state interest_storage[3];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[128];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot net_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];
    dom_scale_budget_snapshot snap;

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.collapse_budget_per_tick = 1000u;
    ctx.budget_policy.refinement_budget_per_tick = 1u;
    ctx.budget_policy.expand_budget_per_tick = 1u;
    ctx.budget_policy.macro_event_budget_per_tick = 1u;
    ctx.budget_policy.planning_budget_per_tick = 1u;
    ctx.budget_policy.snapshot_budget_per_tick = 1u;
    ctx.budget_policy.macro_queue_limit = 1024u;
    ctx.budget_policy.deferred_queue_limit = 16u;

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&net_slot, 0, sizeof(net_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_network_domain(&net_slot,
                              nodes,
                              (u32)(sizeof(nodes) / sizeof(nodes[0])),
                              edges,
                              (u32)(sizeof(edges) / sizeof(edges[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));

    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        return 2;
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, net_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u, 0);

    dom_scale_macro_policy_default(&macro_policy);
    ctx.now_tick = target_tick;
    dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
    (void)dom_scale_macro_advance(&ctx, &token, target_tick, &macro_policy, 0);
    for (u32 i = 0u; i < ctx.domain_count; ++i) {
        dom_scale_operation_result expand_res;
        memset(&expand_res, 0, sizeof(expand_res));
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[i].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &expand_res);
    }

    dom_scale_budget_snapshot_current(&ctx, &snap);
    printf("scenario=budgets ticks=%lld workers=%u invariants=%s\n",
           (long long)target_tick,
           workers,
           "SCALE0-DETERMINISM-004,SCALE0-COMMIT-003,SCALE0-CONSERVE-002");
    scale_print_budget_snapshot(&snap);
    scale_print_deferred_ops(&ctx);
    scale_print_timeline(&event_log);
    return 0;
}

static int scale_run_constcost(u32 workers,
                               u32 domain_count,
                               u32 active_count,
                               dom_act_time_t target_tick)
{
    const dom_act_time_t start_tick = 0;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[SCALE_CONSTCOST_MAX_DOMAINS];
    dom_interest_state interest_storage[SCALE_CONSTCOST_MAX_DOMAINS];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[SCALE_CONSTCOST_EVENT_CAP];
    dom_scale_commit_token token;
    dom_scale_budget_snapshot snap;
    dom_scale_resource_entry resource_storage[SCALE_CONSTCOST_MAX_DOMAINS][4];
    u32 expand_failures = 0u;
    u32 refusal_events = 0u;
    u32 defer_events = 0u;
    u32 expand_events = 0u;
    u64 active_hash = scale_fnv1a64_init();
    u64 event_hash;

    if (!world) {
        return 2;
    }
    if (domain_count == 0u) {
        domain_count = 1u;
    }
    if (domain_count > SCALE_CONSTCOST_MAX_DOMAINS) {
        domain_count = SCALE_CONSTCOST_MAX_DOMAINS;
    }
    if (active_count == 0u) {
        active_count = 1u;
    }
    if (active_count > domain_count) {
        active_count = domain_count;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           domain_count,
                           interest_storage,
                           domain_count,
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx.budget_policy.refinement_budget_per_tick = 1000000u;
    ctx.budget_policy.expand_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx.budget_policy.planning_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = 1000000u;
    ctx.budget_policy.deferred_queue_limit = 128u;

    for (u32 i = 0u; i < domain_count; ++i) {
        dom_scale_domain_slot slot;
        u64 domain_id = 1001u + (u64)(i * 10u);
        memset(&slot, 0, sizeof(slot));
        (void)scale_init_resource_domain_with_id(&slot,
                                                 resource_storage[i],
                                                 (u32)(sizeof(resource_storage[i]) / sizeof(resource_storage[i][0])),
                                                 domain_id,
                                                 i + 1u);
        if (dom_scale_register_domain(&ctx, &slot) != 0) {
            return 2;
        }
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    for (u32 i = 0u; i < domain_count; ++i) {
        (void)dom_scale_collapse_domain(&ctx, &token, ctx.domains[i].domain_id, 1u + i, 0);
    }

    /* Isolate measurement to active work only. */
    dom_scale_event_log_clear(&event_log);
    dom_scale_deferred_clear(&ctx);

    ctx.now_tick = target_tick;
    ctx.budget_policy.active_domain_budget = active_count;
    ctx.budget_policy.refinement_budget_per_tick = active_count;
    ctx.budget_policy.expand_budget_per_tick = active_count;
    ctx.budget_policy.snapshot_budget_per_tick = active_count;
    ctx.budget_policy.macro_event_budget_per_tick = 1u;
    ctx.budget_policy.deferred_queue_limit = 32u;
    dom_scale_commit_token_make(&token, ctx.now_tick, 0u);

    for (u32 i = 0u; i < active_count; ++i) {
        dom_scale_operation_result expand_res;
        memset(&expand_res, 0, sizeof(expand_res));
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[i].capsule_id,
                                      DOM_FID_MICRO,
                                      100u + i,
                                      &expand_res);
        if (expand_res.refusal_code != 0u || expand_res.defer_code != 0u) {
            expand_failures += 1u;
        }
    }

    for (u32 i = 0u; i < event_log.count; ++i) {
        const dom_scale_event* ev = &event_log.events[i];
        if (ev->kind == DOM_SCALE_EVENT_EXPAND) {
            expand_events += 1u;
        }
        if (ev->refusal_code != 0u) {
            refusal_events += 1u;
        }
        if (ev->defer_code != 0u) {
            defer_events += 1u;
        }
    }

    for (u32 i = 0u; i < active_count; ++i) {
        active_hash = scale_hash_u64(active_hash,
                                     dom_scale_domain_hash(&ctx.domains[i], ctx.now_tick, workers));
    }

    dom_scale_budget_snapshot_current(&ctx, &snap);
    event_hash = scale_event_log_hash(&event_log);

    printf("scenario=constcost domains=%u active=%u ticks=%lld workers=%u invariants=%s\n",
           (unsigned int)domain_count,
           (unsigned int)active_count,
           (long long)target_tick,
           workers,
           "SCALE0-DETERMINISM-004,SCALE3-BUDGET-009,SCALE3-CONSTCOST-011");
    printf("constcost.event_hash=%llu constcost.active_hash=%llu expand_failures=%u\n",
           (unsigned long long)event_hash,
           (unsigned long long)active_hash,
           (unsigned int)expand_failures);
    printf("events.total=%u events.expand=%u events.refusal=%u events.defer=%u\n",
           (unsigned int)event_log.count,
           (unsigned int)expand_events,
           (unsigned int)refusal_events,
           (unsigned int)defer_events);
    scale_print_budget_snapshot(&snap);
    return expand_failures == 0u ? 0 : 1;
}

static int scale_run_stress(u32 workers, u32 domain_count, dom_act_time_t target_tick)
{
    const dom_act_time_t start_tick = 0;
    const u32 steps = 32u;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[SCALE_CONSTCOST_MAX_DOMAINS];
    dom_interest_state interest_storage[SCALE_CONSTCOST_MAX_DOMAINS];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[SCALE_CONSTCOST_EVENT_CAP];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_budget_snapshot snap;
    dom_scale_resource_entry resource_storage[SCALE_CONSTCOST_MAX_DOMAINS][4];
    u32 macro_exec_events = 0u;
    u32 macro_refusals = 0u;
    u64 event_hash;

    if (!world) {
        return 2;
    }
    if (domain_count == 0u) {
        domain_count = 1u;
    }
    if (domain_count > SCALE_CONSTCOST_MAX_DOMAINS) {
        domain_count = SCALE_CONSTCOST_MAX_DOMAINS;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           domain_count,
                           interest_storage,
                           domain_count,
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = domain_count * 2u;
    if (ctx.budget_policy.macro_queue_limit < domain_count) {
        ctx.budget_policy.macro_queue_limit = domain_count;
    }
    ctx.budget_policy.deferred_queue_limit = 64u;

    for (u32 i = 0u; i < domain_count; ++i) {
        dom_scale_domain_slot slot;
        u64 domain_id = 5001u + (u64)(i * 10u);
        memset(&slot, 0, sizeof(slot));
        (void)scale_init_resource_domain_with_id(&slot,
                                                 resource_storage[i],
                                                 (u32)(sizeof(resource_storage[i]) / sizeof(resource_storage[i][0])),
                                                 domain_id,
                                                 i + 3u);
        if (dom_scale_register_domain(&ctx, &slot) != 0) {
            return 2;
        }
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    for (u32 i = 0u; i < domain_count; ++i) {
        (void)dom_scale_collapse_domain(&ctx, &token, ctx.domains[i].domain_id, 7u + i, 0);
    }

    dom_scale_event_log_clear(&event_log);
    dom_scale_deferred_clear(&ctx);

    dom_scale_macro_policy_default(&macro_policy);
    macro_policy.macro_interval_ticks = target_tick > 0 ? (target_tick / (dom_act_time_t)steps) : 1;
    if (macro_policy.macro_interval_ticks <= 0) {
        macro_policy.macro_interval_ticks = 1;
    }

    ctx.budget_policy.macro_event_budget_per_tick = 1u;
    ctx.budget_policy.snapshot_budget_per_tick = 1u;
    ctx.budget_policy.refinement_budget_per_tick = 1u;
    ctx.budget_policy.expand_budget_per_tick = 1u;

    for (u32 step = 1u; step <= steps; ++step) {
        ctx.now_tick = (dom_act_time_t)((target_tick * (dom_act_time_t)step) / (dom_act_time_t)steps);
        dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
        (void)dom_scale_macro_advance(&ctx, &token, ctx.now_tick, &macro_policy, 0);
    }

    for (u32 i = 0u; i < event_log.count; ++i) {
        const dom_scale_event* ev = &event_log.events[i];
        if (ev->kind == DOM_SCALE_EVENT_MACRO_EXECUTE) {
            macro_exec_events += 1u;
        }
        if (ev->refusal_code != 0u) {
            macro_refusals += 1u;
        }
    }

    dom_scale_budget_snapshot_current(&ctx, &snap);
    event_hash = scale_event_log_hash(&event_log);

    printf("scenario=stress domains=%u ticks=%lld workers=%u invariants=%s\n",
           (unsigned int)domain_count,
           (long long)target_tick,
           workers,
           "SCALE0-DETERMINISM-004,SCALE3-BUDGET-009,SCALE3-CONSTCOST-011");
    printf("stress.event_hash=%llu macro_exec_events=%u macro_refusals=%u queue_count=%u schedule_count=%u\n",
           (unsigned long long)event_hash,
           (unsigned int)macro_exec_events,
           (unsigned int)macro_refusals,
           (unsigned int)dom_macro_event_queue_count(world),
           (unsigned int)dom_macro_schedule_store_count(world));
    scale_print_budget_snapshot(&snap);

    return snap.deferred_overflow == 0u ? 0 : 1;
}

static u32 scale_parse_flag_u32(int argc, char** argv, const char* flag, u32 default_value)
{
    u32 value = default_value;
    for (int i = 0; i + 1 < argc; ++i) {
        if (strcmp(argv[i], flag) != 0) {
            continue;
        }
        u32 parsed = 0u;
        if (scale_parse_u32(argv[i + 1], &parsed)) {
            value = parsed;
        }
    }
    return value;
}

static int scale_parse_flag_bool(int argc, char** argv, const char* flag, int default_value)
{
    int value = default_value;
    for (int i = 0; i + 1 < argc; ++i) {
        if (strcmp(argv[i], flag) != 0) {
            continue;
        }
        u32 parsed = 0u;
        if (scale_parse_u32(argv[i + 1], &parsed)) {
            value = parsed ? 1 : 0;
        }
    }
    return value;
}

static int scale_compare_resources(const dom_scale_domain_slot* slot,
                                   const dom_scale_resource_entry* initial,
                                   u32 initial_count)
{
    if (!slot || !initial) {
        return 0;
    }
    if (slot->resources.count != initial_count) {
        return 0;
    }
    for (u32 i = 0u; i < initial_count; ++i) {
        int found = 0;
        for (u32 j = 0u; j < slot->resources.count; ++j) {
            if (slot->resources.entries[j].resource_id == initial[i].resource_id &&
                slot->resources.entries[j].quantity == initial[i].quantity) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return 0;
        }
    }
    return 1;
}

static int scale_compare_network(const dom_scale_domain_slot* slot,
                                 const dom_scale_network_node* initial_nodes,
                                 u32 initial_node_count,
                                 const dom_scale_network_edge* initial_edges,
                                 u32 initial_edge_count)
{
    if (!slot || !initial_nodes || !initial_edges) {
        return 0;
    }
    if (slot->network.node_count != initial_node_count ||
        slot->network.edge_count != initial_edge_count) {
        return 0;
    }
    for (u32 i = 0u; i < initial_node_count; ++i) {
        int found = 0;
        for (u32 j = 0u; j < slot->network.node_count; ++j) {
            if (slot->network.nodes[j].node_id == initial_nodes[i].node_id &&
                slot->network.nodes[j].node_kind == initial_nodes[i].node_kind) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return 0;
        }
    }
    for (u32 i = 0u; i < initial_edge_count; ++i) {
        int found = 0;
        for (u32 j = 0u; j < slot->network.edge_count; ++j) {
            const dom_scale_network_edge* edge = &slot->network.edges[j];
            if (edge->edge_id == initial_edges[i].edge_id &&
                edge->from_node_id == initial_edges[i].from_node_id &&
                edge->to_node_id == initial_edges[i].to_node_id &&
                edge->capacity_units == initial_edges[i].capacity_units &&
                edge->buffer_units == initial_edges[i].buffer_units) {
                found = 1;
                break;
            }
        }
        if (!found) {
            return 0;
        }
    }
    return 1;
}

static int scale_compare_agents(const dom_scale_domain_slot* slot, u32 initial_count)
{
    if (!slot) {
        return 0;
    }
    return slot->agents.count == initial_count ? 1 : 0;
}

static u64 scale_macro_state_hash(const d_world* world)
{
    u64 hash = scale_fnv1a64_init();
    dom_macro_capsule_blob blob;
    dom_macro_schedule_entry schedule;
    dom_macro_event_entry ev;
    u32 count = 0u;
    if (!world) {
        return 0u;
    }
    count = dom_macro_capsule_store_count(world);
    for (u32 i = 0u; i < count; ++i) {
        if (dom_macro_capsule_store_get_by_index(world, i, &blob) != 0) {
            continue;
        }
        hash = scale_hash_u64(hash, blob.capsule_id);
        hash = scale_hash_u64(hash, blob.domain_id);
        hash = scale_hash_u64(hash, (u64)blob.source_tick);
        hash = scale_hash_bytes(hash, blob.bytes, blob.byte_count);
    }
    count = dom_macro_schedule_store_count(world);
    for (u32 i = 0u; i < count; ++i) {
        if (dom_macro_schedule_store_get_by_index(world, i, &schedule) != 0) {
            continue;
        }
        hash = scale_hash_u64(hash, schedule.domain_id);
        hash = scale_hash_u64(hash, schedule.capsule_id);
        hash = scale_hash_u64(hash, (u64)schedule.last_event_time);
        hash = scale_hash_u64(hash, (u64)schedule.next_event_time);
        hash = scale_hash_u64(hash, (u64)schedule.interval_ticks);
        hash = scale_hash_u64(hash, schedule.executed_events);
    }
    count = dom_macro_event_queue_count(world);
    for (u32 i = 0u; i < count; ++i) {
        if (dom_macro_event_queue_get_by_index(world, i, &ev) != 0) {
            continue;
        }
        hash = scale_hash_u64(hash, ev.domain_id);
        hash = scale_hash_u64(hash, ev.event_id);
        hash = scale_hash_u64(hash, (u64)ev.event_time);
        hash = scale_hash_u64(hash, ev.order_key);
    }
    return hash;
}

typedef struct scale_macro_result {
    u64 macro_hash;
    u64 micro_hash;
    u32 invariants_ok;
    u32 executed_events;
    u32 queue_count;
    u32 schedule_count;
    u32 expand_failures;
} scale_macro_result;

static void scale_macro_override_interval(dom_scale_context* ctx, dom_act_time_t interval)
{
    u32 count;
    dom_scale_commit_token token;
    if (!ctx || !ctx->world || interval <= 0) {
        return;
    }
    dom_scale_commit_token_make(&token, ctx->now_tick, 0u);
    count = dom_macro_schedule_store_count(ctx->world);
    for (u32 i = 0u; i < count; ++i) {
        dom_macro_schedule_entry schedule;
        if (dom_macro_schedule_store_get_by_index(ctx->world, i, &schedule) != 0) {
            continue;
        }
        schedule.interval_ticks = interval;
        schedule.next_event_time = schedule.last_event_time + interval;
        (void)dom_macro_schedule_store_set(ctx->world, &schedule);
        (void)dom_macro_event_queue_remove_domain(ctx->world, schedule.domain_id);
        (void)dom_scale_macro_request_reschedule(ctx, &token, schedule.domain_id, 0u);
    }
}

static int scale_macro_run(u32 workers,
                           dom_act_time_t target_tick,
                           u32 macro_interval,
                           int compaction_enabled,
                           scale_macro_result* out_result)
{
    const dom_act_time_t start_tick = 0;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[3];
    dom_interest_state interest_storage[3];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[512];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot net_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];
    dom_scale_resource_entry initial_resources[4];
    dom_scale_network_node initial_nodes[4];
    dom_scale_network_edge initial_edges[4];
    u32 initial_agent_count = 0u;
    scale_macro_result result;

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx.budget_policy.compaction_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = 1000000u;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.expand_budget_per_tick = 1000000u;
    ctx.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx.budget_policy.refinement_budget_per_tick = 1000000u;
    ctx.budget_policy.planning_budget_per_tick = 1000000u;
    ctx.budget_policy.deferred_queue_limit = 128u;
    if (compaction_enabled) {
        ctx.budget_policy.compaction_event_threshold = 16u;
        ctx.budget_policy.compaction_time_threshold = 256;
    } else {
        ctx.budget_policy.compaction_event_threshold = 0u;
        ctx.budget_policy.compaction_time_threshold = 0;
    }

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&net_slot, 0, sizeof(net_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_network_domain(&net_slot,
                              nodes,
                              (u32)(sizeof(nodes) / sizeof(nodes[0])),
                              edges,
                              (u32)(sizeof(edges) / sizeof(edges[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
    memcpy(initial_resources, resources, sizeof(initial_resources));
    memcpy(initial_nodes, nodes, sizeof(initial_nodes));
    memcpy(initial_edges, edges, sizeof(initial_edges));
    initial_agent_count = agent_slot.agents.count;

    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        return 2;
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, net_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u, 0);

    dom_scale_macro_policy_default(&macro_policy);
    if (macro_interval > 0u) {
        macro_policy.macro_interval_ticks = (dom_act_time_t)macro_interval;
        scale_macro_override_interval(&ctx, macro_policy.macro_interval_ticks);
    }

    ctx.now_tick = target_tick;
    dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
    (void)dom_scale_macro_advance(&ctx, &token, target_tick, &macro_policy, 0);
    if (compaction_enabled) {
        for (u32 i = 0u; i < ctx.domain_count; ++i) {
            (void)dom_scale_macro_compact(&ctx,
                                          &token,
                                          ctx.domains[i].domain_id,
                                          target_tick,
                                          &macro_policy,
                                          0);
        }
    }

    memset(&result, 0, sizeof(result));
    result.macro_hash = scale_macro_state_hash(world);
    result.queue_count = dom_macro_event_queue_count(world);
    result.schedule_count = dom_macro_schedule_store_count(world);
    for (u32 i = 0u; i < result.schedule_count; ++i) {
        dom_macro_schedule_entry schedule;
        if (dom_macro_schedule_store_get_by_index(world, i, &schedule) != 0) {
            continue;
        }
        result.executed_events += schedule.executed_events;
    }

    result.invariants_ok = 1u;
    result.expand_failures = 0u;
    for (u32 i = 0u; i < ctx.domain_count; ++i) {
        dom_scale_operation_result expand_res;
        memset(&expand_res, 0, sizeof(expand_res));
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[i].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &expand_res);
        if (expand_res.refusal_code != 0u || expand_res.defer_code != 0u) {
            result.expand_failures += 1u;
            result.invariants_ok = 0u;
        }
    }
    result.micro_hash = scale_global_hash(domain_storage, ctx.domain_count, ctx.now_tick, workers);
    result.invariants_ok = (result.invariants_ok &&
                            scale_compare_resources(&domain_storage[0], initial_resources, res_slot.resources.count) &&
                            scale_compare_network(&domain_storage[1],
                                                  initial_nodes,
                                                  net_slot.network.node_count,
                                                  initial_edges,
                                                  net_slot.network.edge_count) &&
                            scale_compare_agents(&domain_storage[2], initial_agent_count)) ? 1u : 0u;

    if (out_result) {
        *out_result = result;
    }
    return result.invariants_ok ? 0 : 1;
}

static int scale_run_macro_long(u32 workers,
                                dom_act_time_t target_tick,
                                u32 macro_interval,
                                int compaction_enabled)
{
    scale_macro_result result;
    int rc = scale_macro_run(workers, target_tick, macro_interval, compaction_enabled, &result);
    printf("scenario=macro_long ticks=%lld interval=%u compaction=%u workers=%u invariants=%s\n",
           (long long)target_tick,
           (unsigned int)macro_interval,
           (unsigned int)(compaction_enabled ? 1u : 0u),
           workers,
           "SCALE0-CONSERVE-002,SCALE0-DETERMINISM-004,SCALE0-REPLAY-008");
    printf("macro_hash=%llu micro_hash=%llu invariants_ok=%u executed_events=%u queue_count=%u schedule_count=%u expand_failures=%u\n",
           (unsigned long long)result.macro_hash,
           (unsigned long long)result.micro_hash,
           (unsigned int)result.invariants_ok,
           (unsigned int)result.executed_events,
           (unsigned int)result.queue_count,
           (unsigned int)result.schedule_count,
           (unsigned int)result.expand_failures);
    return rc;
}

static int scale_run_macro_compare(u32 workers, dom_act_time_t target_tick, u32 macro_interval)
{
    scale_macro_result no_compact;
    scale_macro_result compact;
    int rc_a = scale_macro_run(workers, target_tick, macro_interval, 0, &no_compact);
    int rc_b = scale_macro_run(workers, target_tick, macro_interval, 1, &compact);
    int macro_match = (no_compact.macro_hash == compact.macro_hash) ? 1 : 0;
    int micro_match = (no_compact.micro_hash == compact.micro_hash) ? 1 : 0;
    printf("scenario=macro_compare ticks=%lld interval=%u workers=%u invariants=%s\n",
           (long long)target_tick,
           (unsigned int)macro_interval,
           workers,
           "SCALE0-DETERMINISM-004,SCALE0-REPLAY-008,SCALE0-CONSERVE-002");
    printf("macro_hash_a=%llu macro_hash_b=%llu macro_hash_match=%u micro_hash_a=%llu micro_hash_b=%llu micro_hash_match=%u\n",
           (unsigned long long)no_compact.macro_hash,
           (unsigned long long)compact.macro_hash,
           (unsigned int)macro_match,
           (unsigned long long)no_compact.micro_hash,
           (unsigned long long)compact.micro_hash,
           (unsigned int)micro_match);
    if (rc_a != 0 || rc_b != 0) {
        return 1;
    }
    return (macro_match && micro_match) ? 0 : 1;
}

static int scale_run_macro_replay(u32 workers, dom_act_time_t target_tick, u32 macro_interval)
{
    const dom_act_time_t start_tick = 0;
    const char* temp_path = "scale_macro_tmp.tlv";
    d_world* world = scale_make_world();
    d_world* loaded_world = 0;
    dom_scale_context ctx;
    dom_scale_context ctx_loaded;
    dom_scale_domain_slot domain_storage[3];
    dom_scale_domain_slot loaded_domain_storage[3];
    dom_interest_state interest_storage[3];
    dom_interest_state loaded_interest_storage[3];
    dom_scale_event_log event_log;
    dom_scale_event_log loaded_event_log;
    dom_scale_event event_storage[512];
    dom_scale_event loaded_event_storage[512];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot net_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];
    dom_scale_resource_entry initial_resources[4];
    dom_scale_network_node initial_nodes[4];
    dom_scale_network_edge initial_edges[4];
    u32 initial_agent_count = 0u;
    u64 macro_hash = 0u;
    u64 micro_hash = 0u;
    u64 replay_micro_hash = 0u;
    int invariants_ok = 1;

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx.budget_policy.compaction_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = 1000000u;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.expand_budget_per_tick = 1000000u;

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&net_slot, 0, sizeof(net_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_network_domain(&net_slot,
                              nodes,
                              (u32)(sizeof(nodes) / sizeof(nodes[0])),
                              edges,
                              (u32)(sizeof(edges) / sizeof(edges[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
    memcpy(initial_resources, resources, sizeof(initial_resources));
    memcpy(initial_nodes, nodes, sizeof(initial_nodes));
    memcpy(initial_edges, edges, sizeof(initial_edges));
    initial_agent_count = agent_slot.agents.count;

    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        return 2;
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, net_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u, 0);

    dom_scale_macro_policy_default(&macro_policy);
    if (macro_interval > 0u) {
        macro_policy.macro_interval_ticks = (dom_act_time_t)macro_interval;
        scale_macro_override_interval(&ctx, macro_policy.macro_interval_ticks);
    }

    ctx.now_tick = target_tick;
    dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
    (void)dom_scale_macro_advance(&ctx, &token, target_tick, &macro_policy, 0);
    macro_hash = scale_macro_state_hash(world);

    if (!d_world_save_tlv(world, temp_path)) {
        return 2;
    }

    for (u32 i = 0u; i < ctx.domain_count; ++i) {
        dom_scale_operation_result expand_res;
        memset(&expand_res, 0, sizeof(expand_res));
        (void)dom_scale_expand_domain(&ctx,
                                      &token,
                                      ctx.domains[i].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &expand_res);
        if (expand_res.refusal_code != 0u || expand_res.defer_code != 0u) {
            invariants_ok = 0;
        }
    }
    micro_hash = scale_global_hash(domain_storage, ctx.domain_count, ctx.now_tick, workers);
    invariants_ok = invariants_ok &&
                    scale_compare_resources(&domain_storage[0], initial_resources, res_slot.resources.count) &&
                    scale_compare_network(&domain_storage[1],
                                          initial_nodes,
                                          net_slot.network.node_count,
                                          initial_edges,
                                          net_slot.network.edge_count) &&
                    scale_compare_agents(&domain_storage[2], initial_agent_count);

    loaded_world = d_world_load_tlv(temp_path);
    (void)remove(temp_path);
    if (!loaded_world) {
        return 2;
    }

    dom_scale_event_log_init(&loaded_event_log,
                             loaded_event_storage,
                             (u32)(sizeof(loaded_event_storage) / sizeof(loaded_event_storage[0])));
    dom_scale_context_init(&ctx_loaded,
                           loaded_world,
                           loaded_domain_storage,
                           (u32)(sizeof(loaded_domain_storage) / sizeof(loaded_domain_storage[0])),
                           loaded_interest_storage,
                           (u32)(sizeof(loaded_interest_storage) / sizeof(loaded_interest_storage[0])),
                           &loaded_event_log,
                           target_tick,
                           workers);
    ctx_loaded.budget_policy.min_dwell_ticks = 0;
    ctx_loaded.interest_policy.min_dwell_ticks = 0;
    ctx_loaded.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.compaction_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.macro_queue_limit = 1000000u;
    ctx_loaded.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.expand_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.refinement_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.planning_budget_per_tick = 1000000u;
    ctx_loaded.budget_policy.deferred_queue_limit = 128u;

    if (dom_scale_register_domain(&ctx_loaded, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx_loaded, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx_loaded, &agent_slot) != 0) {
        return 2;
    }
    if (macro_interval > 0u) {
        scale_macro_override_interval(&ctx_loaded, macro_policy.macro_interval_ticks);
    }

    for (u32 i = 0u; i < ctx_loaded.domain_count; ++i) {
        dom_macro_schedule_entry schedule;
        if (dom_macro_schedule_store_get(loaded_world, ctx_loaded.domains[i].domain_id, &schedule) == 0) {
            ctx_loaded.domains[i].tier = DOM_FID_LATENT;
            ctx_loaded.domains[i].capsule_id = schedule.capsule_id;
        }
    }

    dom_scale_commit_token_make(&token, ctx_loaded.now_tick, 0u);
    (void)dom_scale_macro_advance(&ctx_loaded, &token, target_tick, &macro_policy, 0);
    for (u32 i = 0u; i < ctx_loaded.domain_count; ++i) {
        dom_scale_operation_result expand_res;
        memset(&expand_res, 0, sizeof(expand_res));
        (void)dom_scale_expand_domain(&ctx_loaded,
                                      &token,
                                      ctx_loaded.domains[i].capsule_id,
                                      DOM_FID_MICRO,
                                      2u,
                                      &expand_res);
        if (expand_res.refusal_code != 0u || expand_res.defer_code != 0u) {
            invariants_ok = 0;
        }
    }
    replay_micro_hash = scale_global_hash(loaded_domain_storage, ctx_loaded.domain_count, ctx_loaded.now_tick, workers);

    printf("scenario=macro_replay ticks=%lld interval=%u workers=%u invariants=%s\n",
           (long long)target_tick,
           (unsigned int)macro_interval,
           workers,
           "SCALE0-REPLAY-008,SCALE0-DETERMINISM-004,SCALE0-CONSERVE-002");
    printf("macro_hash=%llu micro_hash=%llu replay_micro_hash=%llu replay_hash_match=%u invariants_ok=%u\n",
           (unsigned long long)macro_hash,
           (unsigned long long)micro_hash,
           (unsigned long long)replay_micro_hash,
           (unsigned int)(micro_hash == replay_micro_hash ? 1u : 0u),
           (unsigned int)(invariants_ok ? 1u : 0u));
    return (invariants_ok && micro_hash == replay_micro_hash) ? 0 : 1;
}

static int scale_run_macro_transition(u32 workers, dom_act_time_t target_tick, u32 macro_interval)
{
    const dom_act_time_t start_tick = 0;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[3];
    dom_interest_state interest_storage[3];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[512];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot net_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];
    dom_scale_resource_entry initial_resources[4];
    dom_scale_network_node initial_nodes[4];
    dom_scale_network_edge initial_edges[4];
    u32 initial_agent_count = 0u;
    u32 drift_count = 0u;
    u32 cycles = 4u;

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx.budget_policy.compaction_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = 1000000u;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.expand_budget_per_tick = 1000000u;
    ctx.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx.budget_policy.refinement_budget_per_tick = 1000000u;
    ctx.budget_policy.planning_budget_per_tick = 1000000u;
    ctx.budget_policy.deferred_queue_limit = 128u;

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&net_slot, 0, sizeof(net_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_network_domain(&net_slot,
                              nodes,
                              (u32)(sizeof(nodes) / sizeof(nodes[0])),
                              edges,
                              (u32)(sizeof(edges) / sizeof(edges[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));
    memcpy(initial_resources, resources, sizeof(initial_resources));
    memcpy(initial_nodes, nodes, sizeof(initial_nodes));
    memcpy(initial_edges, edges, sizeof(initial_edges));
    initial_agent_count = agent_slot.agents.count;

    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        return 2;
    }

    dom_scale_macro_policy_default(&macro_policy);
    if (macro_interval > 0u) {
        macro_policy.macro_interval_ticks = (dom_act_time_t)macro_interval;
    }

    for (u32 cycle = 0u; cycle < cycles; ++cycle) {
        ctx.now_tick = (dom_act_time_t)((cycle + 1u) * (target_tick / (dom_act_time_t)cycles));
        dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
        (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u + cycle, 0);
        (void)dom_scale_collapse_domain(&ctx, &token, net_slot.domain_id, 1u + cycle, 0);
        (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u + cycle, 0);
        if (macro_interval > 0u) {
            scale_macro_override_interval(&ctx, macro_policy.macro_interval_ticks);
        }
        (void)dom_scale_macro_advance(&ctx, &token, ctx.now_tick, &macro_policy, 0);
        for (u32 i = 0u; i < ctx.domain_count; ++i) {
            dom_scale_operation_result expand_res;
            memset(&expand_res, 0, sizeof(expand_res));
            (void)dom_scale_expand_domain(&ctx,
                                          &token,
                                          ctx.domains[i].capsule_id,
                                          DOM_FID_MICRO,
                                          2u + cycle,
                                          &expand_res);
            if (expand_res.refusal_code != 0u || expand_res.defer_code != 0u) {
                drift_count += 1u;
            }
        }
        if (!scale_compare_resources(&domain_storage[0], initial_resources, res_slot.resources.count) ||
            !scale_compare_network(&domain_storage[1],
                                   initial_nodes,
                                   net_slot.network.node_count,
                                   initial_edges,
                                   net_slot.network.edge_count) ||
            !scale_compare_agents(&domain_storage[2], initial_agent_count)) {
            drift_count += 1u;
        }
    }

    printf("scenario=macro_transition ticks=%lld interval=%u workers=%u invariants=%s drift_count=%u\n",
           (long long)target_tick,
           (unsigned int)macro_interval,
           workers,
           "SCALE0-CONSERVE-002,SCALE0-DETERMINISM-004,SCALE0-INTEREST-006",
           (unsigned int)drift_count);
    return drift_count == 0u ? 0 : 1;
}

static int scale_run_macro_timeline(u32 workers, dom_act_time_t target_tick, u32 macro_interval)
{
    const dom_act_time_t start_tick = 0;
    d_world* world = scale_make_world();
    dom_scale_context ctx;
    dom_scale_domain_slot domain_storage[3];
    dom_interest_state interest_storage[3];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[1024];
    dom_scale_commit_token token;
    dom_scale_macro_policy macro_policy;
    dom_scale_domain_slot res_slot;
    dom_scale_domain_slot net_slot;
    dom_scale_domain_slot agent_slot;
    dom_scale_resource_entry resources[4];
    dom_scale_network_node nodes[4];
    dom_scale_network_edge edges[4];
    dom_scale_agent_entry agents[8];

    if (!world) {
        return 2;
    }

    dom_scale_event_log_init(&event_log, event_storage, (u32)(sizeof(event_storage) / sizeof(event_storage[0])));
    dom_scale_context_init(&ctx,
                           world,
                           domain_storage,
                           (u32)(sizeof(domain_storage) / sizeof(domain_storage[0])),
                           interest_storage,
                           (u32)(sizeof(interest_storage) / sizeof(interest_storage[0])),
                           &event_log,
                           start_tick,
                           workers);
    ctx.budget_policy.min_dwell_ticks = 0;
    ctx.interest_policy.min_dwell_ticks = 0;
    ctx.budget_policy.macro_event_budget_per_tick = 1000000u;
    ctx.budget_policy.compaction_budget_per_tick = 1000000u;
    ctx.budget_policy.macro_queue_limit = 1000000u;
    ctx.budget_policy.collapse_budget_per_tick = 1000000u;
    ctx.budget_policy.expand_budget_per_tick = 1000000u;
    ctx.budget_policy.snapshot_budget_per_tick = 1000000u;
    ctx.budget_policy.refinement_budget_per_tick = 1000000u;
    ctx.budget_policy.planning_budget_per_tick = 1000000u;
    ctx.budget_policy.deferred_queue_limit = 128u;
    ctx.budget_policy.compaction_event_threshold = 8u;
    ctx.budget_policy.compaction_time_threshold = 128;

    memset(&res_slot, 0, sizeof(res_slot));
    memset(&net_slot, 0, sizeof(net_slot));
    memset(&agent_slot, 0, sizeof(agent_slot));
    (void)scale_init_resource_domain(&res_slot, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    scale_init_network_domain(&net_slot,
                              nodes,
                              (u32)(sizeof(nodes) / sizeof(nodes[0])),
                              edges,
                              (u32)(sizeof(edges) / sizeof(edges[0])));
    scale_init_agent_domain(&agent_slot, agents, (u32)(sizeof(agents) / sizeof(agents[0])));

    if (dom_scale_register_domain(&ctx, &res_slot) != 0 ||
        dom_scale_register_domain(&ctx, &net_slot) != 0 ||
        dom_scale_register_domain(&ctx, &agent_slot) != 0) {
        return 2;
    }

    dom_scale_commit_token_make(&token, start_tick, 0u);
    (void)dom_scale_collapse_domain(&ctx, &token, res_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, net_slot.domain_id, 1u, 0);
    (void)dom_scale_collapse_domain(&ctx, &token, agent_slot.domain_id, 1u, 0);

    dom_scale_macro_policy_default(&macro_policy);
    if (macro_interval > 0u) {
        macro_policy.macro_interval_ticks = (dom_act_time_t)macro_interval;
        scale_macro_override_interval(&ctx, macro_policy.macro_interval_ticks);
    }

    ctx.now_tick = target_tick;
    dom_scale_commit_token_make(&token, ctx.now_tick, 0u);
    (void)dom_scale_macro_advance(&ctx, &token, target_tick, &macro_policy, 0);
    for (u32 i = 0u; i < ctx.domain_count; ++i) {
        (void)dom_scale_macro_compact(&ctx,
                                      &token,
                                      ctx.domains[i].domain_id,
                                      target_tick,
                                      &macro_policy,
                                      0);
    }

    printf("scenario=macro_timeline ticks=%lld interval=%u workers=%u invariants=%s macro_hash=%llu queue_count=%u\n",
           (long long)target_tick,
           (unsigned int)macro_interval,
           workers,
           "SCALE0-DETERMINISM-004,SCALE0-REPLAY-008",
           (unsigned long long)scale_macro_state_hash(world),
           (unsigned int)dom_macro_event_queue_count(world));
    scale_print_timeline(&event_log);
    return 0;
}

static void scale_print_help(void)
{
    printf("scale commands:\n");
    printf("  scale collapse-expand <resources|network|agents> [--workers N]\n");
    printf("  scale inspect <resources|network|agents> [--workers N]\n");
    printf("  scale diff <resources|network|agents> [--workers N]\n");
    printf("  scale validate <resources|network|agents> [--workers N]\n");
    printf("  scale timeline <resources|network|agents> [--workers N]\n");
    printf("  scale interest <A|B> [--workers N]\n");
    printf("  scale thread <resources|network|agents> [--workers N]\n");
    printf("  scale refusal <budget|active|refinement|macro|planning|snapshot|tier2|unsupported> [--workers N]\n");
    printf("  scale budgets <ticks> [--workers N]\n");
    printf("  scale constcost <domains> [--active N] [--ticks T] [--workers N]\n");
    printf("  scale stress <domains> [--ticks T] [--workers N]\n");
    printf("  scale macro-long <ticks> [--interval N] [--compact 0|1] [--workers N]\n");
    printf("  scale macro-compare <ticks> [--interval N] [--workers N]\n");
    printf("  scale macro-replay <ticks> [--interval N] [--workers N]\n");
    printf("  scale macro-transition <ticks> [--interval N] [--workers N]\n");
    printf("  scale macro-timeline <ticks> [--interval N] [--workers N]\n");
}

extern "C" int tools_run_scale_cli(int argc, char** argv)
{
    const char* subcmd = 0;
    const char* value_arg = 0;
    u32 workers = 1u;
    int skip_next = 0;
    if (argc <= 0 || !argv) {
        scale_print_help();
        return 0;
    }
    subcmd = argv[0];
    workers = scale_parse_workers(argc, argv, 1u);
    for (int i = 1; i < argc; ++i) {
        if (skip_next) {
            skip_next = 0;
            continue;
        }
        if (strcmp(argv[i], "--workers") == 0) {
            skip_next = 1;
            continue;
        }
        if (argv[i][0] != '-') {
            value_arg = argv[i];
            break;
        }
    }

    if (strcmp(subcmd, "collapse-expand") == 0 || strcmp(subcmd, "thread") == 0) {
        u32 domain_kind = scale_parse_domain_kind(value_arg ? value_arg : "resources");
        if (domain_kind == 0u) {
            scale_print_help();
            return 2;
        }
        return scale_run_collapse_expand(domain_kind, workers, 0, 0);
    }
    if (strcmp(subcmd, "inspect") == 0) {
        u32 domain_kind = scale_parse_domain_kind(value_arg ? value_arg : "resources");
        if (domain_kind == 0u) {
            scale_print_help();
            return 2;
        }
        return scale_run_collapse_expand(domain_kind, workers, 1, 0);
    }
    if (strcmp(subcmd, "validate") == 0) {
        u32 domain_kind = scale_parse_domain_kind(value_arg ? value_arg : "resources");
        if (domain_kind == 0u) {
            scale_print_help();
            return 2;
        }
        return scale_run_collapse_expand(domain_kind, workers, 0, 0);
    }
    if (strcmp(subcmd, "timeline") == 0) {
        u32 domain_kind = scale_parse_domain_kind(value_arg ? value_arg : "resources");
        if (domain_kind == 0u) {
            scale_print_help();
            return 2;
        }
        return scale_run_collapse_expand(domain_kind, workers, 0, 1);
    }
    if (strcmp(subcmd, "diff") == 0) {
        u32 domain_kind = scale_parse_domain_kind(value_arg ? value_arg : "resources");
        if (domain_kind == 0u) {
            scale_print_help();
            return 2;
        }
        return scale_run_diff(domain_kind, workers);
    }
    if (strcmp(subcmd, "interest") == 0) {
        const char* pattern = value_arg ? value_arg : "A";
        return scale_run_interest(workers, pattern);
    }
    if (strcmp(subcmd, "refusal") == 0) {
        return scale_run_refusal(workers, value_arg);
    }
    if (strcmp(subcmd, "budgets") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 4096;
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_budgets(workers, ticks);
    }
    if (strcmp(subcmd, "constcost") == 0) {
        u32 domains = 32u;
        u32 active = scale_parse_flag_u32(argc, argv, "--active", 1u);
        u32 ticks_u32 = scale_parse_flag_u32(argc, argv, "--ticks", 4096u);
        dom_act_time_t ticks = (dom_act_time_t)ticks_u32;
        if (value_arg) {
            (void)scale_parse_u32(value_arg, &domains);
        }
        return scale_run_constcost(workers, domains, active, ticks);
    }
    if (strcmp(subcmd, "stress") == 0) {
        u32 domains = 32u;
        u32 ticks_u32 = scale_parse_flag_u32(argc, argv, "--ticks", 262144u);
        dom_act_time_t ticks = (dom_act_time_t)ticks_u32;
        if (value_arg) {
            (void)scale_parse_u32(value_arg, &domains);
        }
        return scale_run_stress(workers, domains, ticks);
    }
    if (strcmp(subcmd, "macro-long") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 36500;
        u32 interval = scale_parse_flag_u32(argc, argv, "--interval", 256u);
        int compact_flag = scale_parse_flag_bool(argc, argv, "--compact", 1);
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_macro_long(workers, ticks, interval, compact_flag);
    }
    if (strcmp(subcmd, "macro-compare") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 36500;
        u32 interval = scale_parse_flag_u32(argc, argv, "--interval", 256u);
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_macro_compare(workers, ticks, interval);
    }
    if (strcmp(subcmd, "macro-replay") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 36500;
        u32 interval = scale_parse_flag_u32(argc, argv, "--interval", 256u);
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_macro_replay(workers, ticks, interval);
    }
    if (strcmp(subcmd, "macro-transition") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 36500;
        u32 interval = scale_parse_flag_u32(argc, argv, "--interval", 256u);
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_macro_transition(workers, ticks, interval);
    }
    if (strcmp(subcmd, "macro-timeline") == 0) {
        u32 ticks_u32 = 0u;
        dom_act_time_t ticks = 36500;
        u32 interval = scale_parse_flag_u32(argc, argv, "--interval", 256u);
        if (value_arg && scale_parse_u32(value_arg, &ticks_u32)) {
            ticks = (dom_act_time_t)ticks_u32;
        }
        return scale_run_macro_timeline(workers, ticks, interval);
    }

    scale_print_help();
    return 2;
}
