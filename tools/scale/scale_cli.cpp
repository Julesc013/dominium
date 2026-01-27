#include "scale/scale_cli.h"

#include "domino/sim/sim.h"
#include "dominium/interest_set.h"
#include "dominium/rules/scale/scale_collapse_expand.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

static void scale_print_timeline(const dom_scale_event_log* log)
{
    if (!log || !log->events) {
        return;
    }
    for (u32 i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        printf("event[%u]=%s tick=%lld domain=%llu capsule=%llu refusal=%s defer=%s\n",
               i,
               scale_event_kind_to_string(ev->kind),
               (long long)ev->tick,
               (unsigned long long)ev->domain_id,
               (unsigned long long)ev->capsule_id,
               dom_scale_refusal_to_string(ev->refusal_code),
               dom_scale_defer_to_string(ev->defer_code));
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
    dom_scale_domain_slot domain_storage[1];
    dom_interest_state interest_storage[1];
    dom_scale_event_log event_log;
    dom_scale_event event_storage[16];
    dom_scale_commit_token token;
    dom_scale_domain_slot slot_init;
    dom_scale_operation_result result;
    dom_scale_resource_entry resources[4];
    const char* case_token = case_name ? case_name : "budget";

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
    (void)scale_init_resource_domain(&slot_init, resources, (u32)(sizeof(resources) / sizeof(resources[0])));
    if (case_name && (strcmp(case_name, "unsupported") == 0 || strcmp(case_name, "unsupported_domain") == 0)) {
        slot_init.domain_kind = 99u;
    }

    if (dom_scale_register_domain(&ctx, &slot_init) != 0) {
        fprintf(stderr, "scale: refusal register failed\n");
        return 2;
    }

    if (!case_name || strcmp(case_name, "budget") == 0) {
        ctx.budget_policy.collapse_budget_per_tick = 1u;
        ctx.budget_policy.collapse_cost_units = 2u;
        case_token = "budget";
    } else if (case_name && (strcmp(case_name, "tier2") == 0 || strcmp(case_name, "tier2_interest") == 0)) {
        interest_storage[0].state = DOM_REL_HOT;
        interest_storage[0].last_change_tick = now_tick;
        case_token = "tier2";
    }

    dom_scale_commit_token_make(&token, now_tick, 0u);
    memset(&result, 0, sizeof(result));
    (void)dom_scale_collapse_domain(&ctx, &token, slot_init.domain_id, 1u, &result);

    printf("scenario=refusal case=%s workers=%u invariants=%s refusal=%s refusal_code=%u defer=%s\n",
           case_token,
           workers,
           "SCALE0-CONSERVE-002,SCALE0-COMMIT-003,SCALE0-REPLAY-008",
           dom_scale_refusal_to_string(result.refusal_code),
           (unsigned int)result.refusal_code,
           dom_scale_defer_to_string(result.defer_code));
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
    printf("  scale refusal <budget|tier2|unsupported> [--workers N]\n");
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

    scale_print_help();
    return 2;
}
