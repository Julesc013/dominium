/*
FILE: server/net/dom_server_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / net
RESPONSIBILITY: Deterministic authoritative server runtime for MMO-1.
*/
#include "dom_server_runtime.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SERVER_NS_DOMAIN = 1u,
    DOM_SERVER_NS_INTENT = 2u,
    DOM_SERVER_NS_EVENT = 3u,
    DOM_SERVER_NS_MESSAGE = 4u
};

enum {
    DOM_SERVER_MESSAGE_OWNERSHIP_TRANSFER = 1u
};

enum {
    DOM_SERVER_DETAIL_NONE = 0u,
    DOM_SERVER_DETAIL_CLIENT_SHARD = 1u,
    DOM_SERVER_DETAIL_INSPECT_ONLY = 2u,
    DOM_SERVER_DETAIL_DOMAIN_OWNER = 3u,
    DOM_SERVER_DETAIL_DOMAIN_UNKNOWN = 4u,
    DOM_SERVER_DETAIL_DEST_SHARD = 5u,
    DOM_SERVER_DETAIL_BUDGET_DEFER_LIMIT = 6u,
    DOM_SERVER_DETAIL_IDEMPOTENT_DUP = 7u,
    DOM_SERVER_DETAIL_MACRO_UNSUPPORTED = 8u
};

static u64 dom_server_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static d_world* dom_server_make_world(u32 seed)
{
    d_world_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.seed = seed ? seed : 123u;
    cfg.width = 1u;
    cfg.height = 1u;
    return d_world_create_from_config(&cfg);
}

static void dom_server_scale_begin_tick(dom_scale_context* ctx, dom_act_time_t tick)
{
    if (!ctx) {
        return;
    }
    ctx->now_tick = tick;
    if (ctx->budget_state.budget_tick == tick) {
        return;
    }
    ctx->budget_state.budget_tick = tick;
    ctx->budget_state.refinement_used = 0u;
    ctx->budget_state.planning_used = 0u;
    ctx->budget_state.collapse_used = 0u;
    ctx->budget_state.expand_used = 0u;
    ctx->budget_state.macro_event_used = 0u;
    ctx->budget_state.compaction_used = 0u;
    ctx->budget_state.snapshot_used = 0u;
}

static u64 dom_server_domain_hash(const dom_scale_domain_slot* slot,
                                  dom_act_time_t tick,
                                  u32 workers)
{
    if (!slot) {
        return 1469598103934665603ULL;
    }
    return dom_scale_domain_hash(slot, tick, workers);
}

static u64 dom_server_scale_event_hash(const dom_scale_event_log* log)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!log || !log->events) {
        return hash;
    }
    hash = dom_server_hash_mix(hash, log->count);
    hash = dom_server_hash_mix(hash, log->overflow);
    for (i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        hash = dom_server_hash_mix(hash, ev->kind);
        hash = dom_server_hash_mix(hash, ev->domain_id);
        hash = dom_server_hash_mix(hash, ev->domain_kind);
        hash = dom_server_hash_mix(hash, ev->capsule_id);
        hash = dom_server_hash_mix(hash, ev->reason_code);
        hash = dom_server_hash_mix(hash, ev->refusal_code);
        hash = dom_server_hash_mix(hash, ev->defer_code);
        hash = dom_server_hash_mix(hash, ev->detail_code);
        hash = dom_server_hash_mix(hash, ev->seed_value);
        hash = dom_server_hash_mix(hash, ev->budget_kind);
        hash = dom_server_hash_mix(hash, ev->budget_limit);
        hash = dom_server_hash_mix(hash, ev->budget_used);
        hash = dom_server_hash_mix(hash, ev->budget_cost);
        hash = dom_server_hash_mix(hash, ev->budget_queue);
        hash = dom_server_hash_mix(hash, ev->budget_overflow);
        hash = dom_server_hash_mix(hash, (u64)ev->tick);
    }
    return hash;
}

static void dom_server_client_budget_reset(dom_server_client* client, dom_act_time_t tick)
{
    if (!client) {
        return;
    }
    client->budget_state.tick = tick;
    client->budget_state.intents_limit = client->policy.intents_per_tick;
    client->budget_state.intents_used = 0u;
    client->budget_state.bytes_limit = client->policy.bytes_per_tick;
    client->budget_state.bytes_used = 0u;
}

static int dom_server_client_idempotent_seen(const dom_server_client* client, u64 key)
{
    u32 i;
    if (!client || key == 0u) {
        return 0;
    }
    for (i = 0u; i < client->idempotency_count; ++i) {
        if (client->idempotency_keys[i] == key) {
            return 1;
        }
    }
    return 0;
}

static void dom_server_client_idempotent_record(dom_server_client* client, u64 key)
{
    u32 slot;
    if (!client || key == 0u) {
        return;
    }
    slot = (client->idempotency_count < DOM_SERVER_MAX_CLIENT_IDEMPOTENCY)
        ? client->idempotency_count
        : (client->idempotency_count % DOM_SERVER_MAX_CLIENT_IDEMPOTENCY);
    client->idempotency_keys[slot] = key;
    client->idempotency_count += 1u;
}

static int dom_server_owner_index(const dom_server_runtime* runtime, u64 domain_id)
{
    u32 i;
    if (!runtime) {
        return -1;
    }
    for (i = 0u; i < runtime->owner_count; ++i) {
        if (runtime->owners[i].domain_id == domain_id) {
            return (int)i;
        }
    }
    return -1;
}

static dom_shard_id dom_server_owner_get(const dom_server_runtime* runtime, u64 domain_id)
{
    int idx = dom_server_owner_index(runtime, domain_id);
    if (idx < 0) {
        return 0u;
    }
    return runtime->owners[(u32)idx].owner_shard_id;
}

static void dom_server_owner_set(dom_server_runtime* runtime,
                                 u64 domain_id,
                                 dom_shard_id owner_shard_id)
{
    int idx;
    if (!runtime || domain_id == 0u) {
        return;
    }
    idx = dom_server_owner_index(runtime, domain_id);
    if (idx >= 0) {
        runtime->owners[(u32)idx].owner_shard_id = owner_shard_id;
        return;
    }
    if (runtime->owner_count >= DOM_SERVER_MAX_DOMAIN_OWNERS) {
        return;
    }
    runtime->owners[runtime->owner_count].domain_id = domain_id;
    runtime->owners[runtime->owner_count].owner_shard_id = owner_shard_id;
    runtime->owner_count += 1u;
}

static dom_server_client* dom_server_find_client(dom_server_runtime* runtime, u64 client_id)
{
    u32 i;
    if (!runtime) {
        return 0;
    }
    for (i = 0u; i < runtime->client_count; ++i) {
        if (runtime->clients[i].client_id == client_id) {
            return &runtime->clients[i];
        }
    }
    return 0;
}

static dom_server_shard* dom_server_find_shard(dom_server_runtime* runtime, dom_shard_id shard_id)
{
    u32 i;
    if (!runtime || shard_id == 0u) {
        return 0;
    }
    for (i = 0u; i < runtime->shard_count; ++i) {
        if (runtime->shards[i].shard_id == shard_id) {
            return &runtime->shards[i];
        }
    }
    return 0;
}

static dom_scale_domain_slot* dom_server_find_domain(dom_server_runtime* runtime,
                                                     dom_server_shard** out_shard,
                                                     u64 domain_id)
{
    u32 i;
    if (out_shard) {
        *out_shard = 0;
    }
    if (!runtime || domain_id == 0u) {
        return 0;
    }
    for (i = 0u; i < runtime->shard_count; ++i) {
        dom_scale_domain_slot* slot = dom_scale_find_domain(&runtime->shards[i].scale_ctx, domain_id);
        if (slot) {
            if (out_shard) {
                *out_shard = &runtime->shards[i];
            }
            return slot;
        }
    }
    return 0;
}

static int dom_server_intent_compare(const dom_server_intent* a, const dom_server_intent* b)
{
    if (a->intent_tick != b->intent_tick) {
        return (a->intent_tick < b->intent_tick) ? -1 : 1;
    }
    if (a->target_shard_id != b->target_shard_id) {
        return (a->target_shard_id < b->target_shard_id) ? -1 : 1;
    }
    if (a->domain_id != b->domain_id) {
        return (a->domain_id < b->domain_id) ? -1 : 1;
    }
    if (a->client_id != b->client_id) {
        return (a->client_id < b->client_id) ? -1 : 1;
    }
    if (a->intent_id != b->intent_id) {
        return (a->intent_id < b->intent_id) ? -1 : 1;
    }
    return 0;
}

static void dom_server_sort_intents(dom_server_intent* intents, u32 count)
{
    u32 i;
    if (!intents || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_server_intent key = intents[i];
        u32 j = i;
        while (j > 0u && dom_server_intent_compare(&key, &intents[j - 1u]) < 0) {
            intents[j] = intents[j - 1u];
            --j;
        }
        intents[j] = key;
    }
}

static void dom_server_sort_deferred(dom_server_deferred_intent* deferred, u32 count)
{
    u32 i;
    if (!deferred || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_server_deferred_intent key = deferred[i];
        u32 j = i;
        while (j > 0u && dom_server_intent_compare(&key.intent, &deferred[j - 1u].intent) < 0) {
            deferred[j] = deferred[j - 1u];
            --j;
        }
        deferred[j] = key;
    }
}

static int dom_server_event_append(dom_server_runtime* runtime,
                                   dom_server_shard* shard,
                                   const dom_server_event* event)
{
    dom_server_event out = *event;
    dom_global_id id;
    u64 packed = 0u;
    if (!runtime || !event) {
        return -1;
    }
    if (runtime->event_count >= DOM_SERVER_MAX_EVENTS) {
        runtime->event_overflow += 1u;
        return -2;
    }
    if (shard) {
        if (dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_EVENT, &id, &packed) == 0) {
            out.event_id = packed;
        }
    } else {
        out.event_id = (u64)runtime->event_count + 1u;
    }
    runtime->events[runtime->event_count] = out;
    runtime->event_count += 1u;
    return 0;
}

static void dom_server_capture_scale_budget(dom_scale_context* ctx,
                                            dom_scale_budget_snapshot* out_snapshot)
{
    if (!ctx || !out_snapshot) {
        return;
    }
    dom_scale_budget_snapshot_current(ctx, out_snapshot);
}

static void dom_server_fill_scale_budget_from_events(dom_server_shard* shard,
                                                     u32 start_index,
                                                     dom_server_event* event)
{
    u32 i;
    if (!shard || !event) {
        return;
    }
    for (i = start_index; i < shard->scale_event_log.count; ++i) {
        const dom_scale_event* ev = &shard->scale_event_log.events[i];
        if (ev->budget_kind != DOM_SCALE_BUDGET_NONE) {
            event->budget_kind = ev->budget_kind;
            event->budget_limit = ev->budget_limit;
            event->budget_used = ev->budget_used;
            event->budget_cost = ev->budget_cost;
        }
        if (ev->refusal_code != 0u) {
            event->refusal_code = ev->refusal_code;
            event->detail_code = ev->detail_code;
        }
        if (ev->defer_code != DOM_SCALE_DEFER_NONE) {
            event->defer_code = ev->defer_code;
            event->detail_code = ev->detail_code;
        }
    }
}

static int dom_server_client_budget_consume(dom_server_client* client,
                                            dom_act_time_t tick,
                                            u32 payload_bytes,
                                            u32* out_refusal)
{
    if (out_refusal) {
        *out_refusal = DOM_SERVER_REFUSE_NONE;
    }
    if (!client) {
        if (out_refusal) {
            *out_refusal = DOM_SERVER_REFUSE_INVALID_INTENT;
        }
        return 0;
    }
    if (client->budget_state.tick != tick) {
        dom_server_client_budget_reset(client, tick);
    }
    if (client->budget_state.intents_limit > 0u &&
        client->budget_state.intents_used + 1u > client->budget_state.intents_limit) {
        if (out_refusal) {
            *out_refusal = DOM_SERVER_REFUSE_RATE_LIMIT;
        }
        return 0;
    }
    if (client->budget_state.bytes_limit > 0u &&
        client->budget_state.bytes_used + payload_bytes > client->budget_state.bytes_limit) {
        if (out_refusal) {
            *out_refusal = DOM_SERVER_REFUSE_RATE_LIMIT;
        }
        return 0;
    }
    client->budget_state.intents_used += 1u;
    client->budget_state.bytes_used += payload_bytes;
    return 1;
}

static void dom_server_resource_domain(dom_scale_domain_slot* slot,
                                       dom_scale_resource_entry* entries,
                                       u32 capacity,
                                       u64 domain_id,
                                       u32 bias)
{
    u32 count = capacity < 3u ? capacity : 3u;
    if (!slot || !entries || capacity == 0u) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    entries[0].resource_id = domain_id + 1u;
    entries[0].quantity = 100u + bias;
    if (count > 1u) {
        entries[1].resource_id = domain_id + 2u;
        entries[1].quantity = 5u + (bias % 7u);
    }
    if (count > 2u) {
        entries[2].resource_id = domain_id + 3u;
        entries[2].quantity = 2000u + (bias % 13u);
    }
    slot->domain_id = domain_id;
    slot->domain_kind = DOM_SCALE_DOMAIN_RESOURCES;
    slot->tier = DOM_FID_MESO;
    slot->last_transition_tick = 0;
    slot->resources.entries = entries;
    slot->resources.capacity = capacity;
    slot->resources.count = count;
}

static void dom_server_network_domain(dom_scale_domain_slot* slot,
                                      dom_scale_network_node* nodes,
                                      u32 node_capacity,
                                      dom_scale_network_edge* edges,
                                      u32 edge_capacity,
                                      u64 domain_id,
                                      u32 bias)
{
    if (!slot || !nodes || !edges || node_capacity < 2u || edge_capacity < 2u) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    nodes[0].node_id = domain_id + 10u;
    nodes[0].node_kind = 1u;
    nodes[1].node_id = domain_id + 20u;
    nodes[1].node_kind = 1u;
    edges[0].edge_id = domain_id + 100u;
    edges[0].from_node_id = nodes[0].node_id;
    edges[0].to_node_id = nodes[1].node_id;
    edges[0].capacity_units = 1000u + (bias % 31u);
    edges[0].buffer_units = 200u + (bias % 17u);
    edges[0].wear_bucket0 = 1u;
    edges[0].wear_bucket1 = 2u;
    edges[0].wear_bucket2 = 3u;
    edges[0].wear_bucket3 = 4u;
    edges[1].edge_id = domain_id + 200u;
    edges[1].from_node_id = nodes[1].node_id;
    edges[1].to_node_id = nodes[0].node_id;
    edges[1].capacity_units = 500u + (bias % 19u);
    edges[1].buffer_units = 100u + (bias % 11u);
    edges[1].wear_bucket0 = 2u;
    edges[1].wear_bucket1 = 1u;
    edges[1].wear_bucket2 = 1u;
    edges[1].wear_bucket3 = 0u;
    slot->domain_id = domain_id;
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

static void dom_server_agent_domain(dom_scale_domain_slot* slot,
                                    dom_scale_agent_entry* agents,
                                    u32 capacity,
                                    u64 domain_id,
                                    u32 bias)
{
    if (!slot || !agents || capacity < 4u) {
        return;
    }
    memset(slot, 0, sizeof(*slot));
    agents[0].agent_id = domain_id + 1u;
    agents[0].role_id = 1u;
    agents[0].trait_mask = 1u;
    agents[0].planning_bucket = 2u;
    agents[1].agent_id = domain_id + 2u;
    agents[1].role_id = 1u;
    agents[1].trait_mask = 2u + (bias % 3u);
    agents[1].planning_bucket = 1u;
    agents[2].agent_id = domain_id + 3u;
    agents[2].role_id = 2u;
    agents[2].trait_mask = 1u;
    agents[2].planning_bucket = 3u;
    agents[3].agent_id = domain_id + 4u;
    agents[3].role_id = 2u;
    agents[3].trait_mask = 1u;
    agents[3].planning_bucket = 1u;
    slot->domain_id = domain_id;
    slot->domain_kind = DOM_SCALE_DOMAIN_AGENTS;
    slot->tier = DOM_FID_MESO;
    slot->last_transition_tick = 0;
    slot->agents.entries = agents;
    slot->agents.capacity = capacity;
    slot->agents.count = 4u;
}

static int dom_server_shard_init(dom_server_shard* shard,
                                 const dom_server_runtime_config* config,
                                 dom_shard_id shard_id)
{
    dom_global_id gid;
    u64 domain_resource = 0u;
    u64 domain_network = 0u;
    u64 domain_agents = 0u;
    u32 bias = shard_id * 13u;
    if (!shard || !config || shard_id == 0u) {
        return -1;
    }
    memset(shard, 0, sizeof(*shard));
    shard->shard_id = shard_id;
    shard->world = dom_server_make_world(123u + shard_id);
    if (!shard->world) {
        return -2;
    }

    dom_scale_event_log_init(&shard->scale_event_log,
                             shard->scale_events,
                             (u32)(sizeof(shard->scale_events) / sizeof(shard->scale_events[0])));

    dom_scale_context_init(&shard->scale_ctx,
                           shard->world,
                           shard->domain_storage,
                           DOM_SERVER_MAX_DOMAINS_PER_SHARD,
                           shard->interest_storage,
                           DOM_SERVER_MAX_DOMAINS_PER_SHARD,
                           &shard->scale_event_log,
                           config->start_tick,
                           config->worker_count);
    shard->scale_ctx.interest_policy.min_dwell_ticks = 0;
    shard->scale_ctx.budget_policy = config->scale_budget_policy;

    shard->macro_policy = config->macro_policy;
    dom_global_id_gen_init(&shard->id_gen, (u16)shard_id);

    (void)dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_DOMAIN, &gid, &domain_resource);
    (void)dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_DOMAIN, &gid, &domain_network);
    (void)dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_DOMAIN, &gid, &domain_agents);

    dom_server_resource_domain(&shard->domain_storage[0],
                               shard->resource_entries,
                               (u32)(sizeof(shard->resource_entries) / sizeof(shard->resource_entries[0])),
                               domain_resource,
                               bias);
    dom_server_network_domain(&shard->domain_storage[1],
                              shard->network_nodes,
                              (u32)(sizeof(shard->network_nodes) / sizeof(shard->network_nodes[0])),
                              shard->network_edges,
                              (u32)(sizeof(shard->network_edges) / sizeof(shard->network_edges[0])),
                              domain_network,
                              bias + 7u);
    dom_server_agent_domain(&shard->domain_storage[2],
                            shard->agent_entries,
                            (u32)(sizeof(shard->agent_entries) / sizeof(shard->agent_entries[0])),
                            domain_agents,
                            bias + 11u);

    if (dom_scale_register_domain(&shard->scale_ctx, &shard->domain_storage[0]) != 0 ||
        dom_scale_register_domain(&shard->scale_ctx, &shard->domain_storage[1]) != 0 ||
        dom_scale_register_domain(&shard->scale_ctx, &shard->domain_storage[2]) != 0) {
        return -3;
    }
    return 0;
}

static void dom_server_snapshot_for_shard(dom_server_shard* shard,
                                          dom_server_snapshot_fragment* out_snapshot)
{
    dom_scale_domain_slot* slot = 0;
    if (!shard || !out_snapshot) {
        return;
    }
    memset(out_snapshot, 0, sizeof(*out_snapshot));
    slot = dom_scale_find_domain(&shard->scale_ctx, shard->domain_storage[0].domain_id);
    if (!slot) {
        return;
    }
    out_snapshot->shard_id = shard->shard_id;
    out_snapshot->domain_id = slot->domain_id;
    out_snapshot->domain_kind = slot->domain_kind;
    out_snapshot->tick = shard->scale_ctx.now_tick;
    out_snapshot->tier = slot->tier;
    out_snapshot->domain_hash = dom_server_domain_hash(slot,
                                                       shard->scale_ctx.now_tick,
                                                       shard->scale_ctx.worker_count);
    out_snapshot->capsule_id = slot->capsule_id;
}

static u64 dom_server_capability_hash(const dom_server_client* client)
{
    u64 hash = 1469598103934665603ULL;
    if (!client) {
        return hash;
    }
    hash = dom_server_hash_mix(hash, client->policy.capability_mask);
    hash = dom_server_hash_mix(hash, client->policy.inspect_only);
    hash = dom_server_hash_mix(hash, client->policy.intents_per_tick);
    hash = dom_server_hash_mix(hash, client->policy.bytes_per_tick);
    return hash;
}

static void dom_server_emit_budget_snapshot(dom_server_runtime* runtime,
                                            dom_server_shard* shard,
                                            dom_server_client* client)
{
    dom_server_event ev;
    if (!runtime || !shard || !client) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.tick = runtime->now_tick;
    ev.shard_id = shard->shard_id;
    ev.client_id = client->client_id;
    ev.event_kind = DOM_SERVER_EVENT_BUDGET_SNAPSHOT;
    ev.client_budget = client->budget_state;
    dom_server_capture_scale_budget(&shard->scale_ctx, &ev.scale_budget);
    (void)dom_server_event_append(runtime, shard, &ev);
}

static int dom_server_queue_deferred(dom_server_runtime* runtime,
                                     const dom_server_intent* intent,
                                     u32 refusal_code)
{
    u32 limit = runtime ? runtime->config.deferred_limit : 0u;
    if (!runtime || !intent) {
        return 0;
    }
    if (limit == 0u) {
        limit = DOM_SERVER_MAX_DEFERRED;
    }
    if (limit > DOM_SERVER_MAX_DEFERRED) {
        limit = DOM_SERVER_MAX_DEFERRED;
    }
    if (runtime->deferred_count >= limit) {
        runtime->deferred_overflow += 1u;
        return 0;
    }
    runtime->deferred[runtime->deferred_count].intent = *intent;
    runtime->deferred[runtime->deferred_count].intent.intent_tick = runtime->now_tick + 1;
    runtime->deferred[runtime->deferred_count].refusal_code = refusal_code;
    runtime->deferred_count += 1u;
    dom_server_sort_deferred(runtime->deferred, runtime->deferred_count);
    return 1;
}

static int dom_server_macro_budget_consume(dom_scale_context* ctx, dom_act_time_t tick)
{
    u32 cost;
    if (!ctx) {
        return 0;
    }
    dom_server_scale_begin_tick(ctx, tick);
    cost = ctx->budget_policy.macro_event_cost_units ? ctx->budget_policy.macro_event_cost_units : 1u;
    if (ctx->budget_policy.macro_event_budget_per_tick > 0u &&
        ctx->budget_state.macro_event_used + cost > ctx->budget_policy.macro_event_budget_per_tick) {
        ctx->budget_state.refusal_macro_event_budget += 1u;
        return 0;
    }
    ctx->budget_state.macro_event_used += cost;
    return 1;
}

static int dom_server_apply_message(dom_server_runtime* runtime,
                                    const dom_cross_shard_message* msg)
{
    dom_server_shard* dest_shard = 0;
    dom_scale_budget_snapshot budget_snapshot;
    dom_server_event ev;
    if (!runtime || !msg) {
        return 0;
    }
    dest_shard = dom_server_find_shard(runtime, msg->dest_shard_id);
    if (!dest_shard) {
        return 0;
    }
    dom_server_scale_begin_tick(&dest_shard->scale_ctx, runtime->now_tick);
    memset(&budget_snapshot, 0, sizeof(budget_snapshot));
    dom_server_capture_scale_budget(&dest_shard->scale_ctx, &budget_snapshot);

    memset(&ev, 0, sizeof(ev));
    ev.tick = runtime->now_tick;
    ev.shard_id = dest_shard->shard_id;
    ev.domain_id = msg->domain_id;
    ev.causal_id = msg->message_id;
    ev.event_kind = DOM_SERVER_EVENT_MESSAGE_APPLY;
    ev.intent_kind = DOM_SERVER_INTENT_TRANSFER_OWNERSHIP;

    if (!dom_server_macro_budget_consume(&dest_shard->scale_ctx, runtime->now_tick)) {
        ev.refusal_code = DOM_SERVER_REFUSE_MACRO_EVENT_BUDGET;
        ev.detail_code = DOM_SERVER_DETAIL_BUDGET_DEFER_LIMIT;
        ev.scale_budget = budget_snapshot;
        (void)dom_server_event_append(runtime, dest_shard, &ev);
        return 0;
    }

    if (msg->message_kind == DOM_SERVER_MESSAGE_OWNERSHIP_TRANSFER) {
        dom_server_owner_set(runtime, msg->domain_id, msg->dest_shard_id);
        runtime->message_applied += 1u;
        dom_server_capture_scale_budget(&dest_shard->scale_ctx, &ev.scale_budget);
        (void)dom_server_event_append(runtime, dest_shard, &ev);
        return 1;
    }
    return 0;
}

static int dom_server_handle_transfer(dom_server_runtime* runtime,
                                      dom_server_shard* shard,
                                      const dom_server_intent* intent,
                                      dom_scale_domain_slot* slot)
{
    dom_cross_shard_message msg;
    dom_global_id gid;
    u64 message_id = 0u;
    dom_shard_id dest_shard_id = (dom_shard_id)intent->payload_u32;
    if (!runtime || !shard || !intent || !slot) {
        return 0;
    }
    if (dest_shard_id == 0u || dest_shard_id > runtime->shard_count) {
        return 0;
    }
    memset(&msg, 0, sizeof(msg));
    (void)dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_MESSAGE, &gid, &message_id);
    msg.message_id = message_id;
    msg.idempotency_key = intent->idempotency_key ? intent->idempotency_key : intent->intent_id;
    msg.origin_shard_id = shard->shard_id;
    msg.dest_shard_id = dest_shard_id;
    msg.domain_id = slot->domain_id;
    msg.origin_tick = runtime->now_tick;
    msg.delivery_tick = runtime->now_tick;
    msg.causal_key = slot->domain_id;
    msg.order_key = intent->intent_id;
    msg.message_kind = DOM_SERVER_MESSAGE_OWNERSHIP_TRANSFER;
    msg.sequence = (u32)(runtime->message_sequence & 0xFFFFFFFFu);
    msg.payload_hash = dom_server_hash_mix(intent->intent_id, dest_shard_id);

    if (dom_cross_shard_log_append(&runtime->message_log, &msg) != 0) {
        return 0;
    }
    runtime->message_sequence += 1u;
    return 1;
}

static void dom_server_emit_intent_event(dom_server_runtime* runtime,
                                         dom_server_shard* shard,
                                         dom_server_client* client,
                                         const dom_server_intent* intent,
                                         u32 event_kind,
                                         const dom_scale_operation_result* result,
                                         u32 scale_event_start,
                                         u32 refusal_code,
                                         u32 detail_code)
{
    dom_server_event ev;
    if (!runtime || !intent) {
        return;
    }
    memset(&ev, 0, sizeof(ev));
    ev.tick = runtime->now_tick;
    ev.shard_id = shard ? shard->shard_id : intent->target_shard_id;
    ev.client_id = client ? client->client_id : intent->client_id;
    ev.domain_id = intent->domain_id;
    ev.capsule_id = intent->capsule_id;
    ev.causal_id = intent->intent_id;
    ev.event_kind = event_kind;
    ev.intent_kind = intent->intent_kind;
    ev.refusal_code = refusal_code;
    ev.detail_code = detail_code;
    if (result) {
        ev.domain_id = result->domain_id;
        ev.capsule_id = result->capsule_id;
    }
    if (client) {
        ev.client_budget = client->budget_state;
    }
    if (shard) {
        dom_server_capture_scale_budget(&shard->scale_ctx, &ev.scale_budget);
        dom_server_fill_scale_budget_from_events(shard, scale_event_start, &ev);
    }
    (void)dom_server_event_append(runtime, shard, &ev);
}

static int dom_server_process_intent(dom_server_runtime* runtime,
                                     const dom_server_intent* intent)
{
    dom_server_client* client = 0;
    dom_server_shard* shard = 0;
    dom_server_shard* domain_shard = 0;
    dom_scale_domain_slot* slot = 0;
    dom_scale_commit_token token;
    dom_scale_operation_result result;
    u32 scale_event_start = 0u;
    u32 refusal_code = DOM_SERVER_REFUSE_NONE;
    u32 payload_bytes = intent ? intent->payload_bytes : 0u;
    if (!runtime || !intent) {
        return 0;
    }

    client = dom_server_find_client(runtime, intent->client_id);
    shard = dom_server_find_shard(runtime, intent->target_shard_id);
    if (!client || !shard) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_INVALID_INTENT,
                                     DOM_SERVER_DETAIL_CLIENT_SHARD);
        return 0;
    }
    if (client->shard_id != shard->shard_id) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_DOMAIN_FORBIDDEN,
                                     DOM_SERVER_DETAIL_CLIENT_SHARD);
        return 0;
    }

    if (!dom_server_client_budget_consume(client, runtime->now_tick, payload_bytes, &refusal_code)) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     refusal_code,
                                     DOM_SERVER_DETAIL_NONE);
        return 0;
    }

    if (client->policy.inspect_only && intent->intent_kind != DOM_SERVER_INTENT_OBSERVE) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_CAPABILITY_MISSING,
                                     DOM_SERVER_DETAIL_INSPECT_ONLY);
        return 0;
    }

    if (intent->idempotency_key != 0u &&
        dom_server_client_idempotent_seen(client, intent->idempotency_key)) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_ACCEPT,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_NONE,
                                     DOM_SERVER_DETAIL_IDEMPOTENT_DUP);
        return 1;
    }

    slot = dom_server_find_domain(runtime, &domain_shard, intent->domain_id);
    if (!slot || !domain_shard) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_INVALID_INTENT,
                                     DOM_SERVER_DETAIL_DOMAIN_UNKNOWN);
        return 0;
    }
    if (domain_shard->shard_id != shard->shard_id ||
        dom_server_owner_get(runtime, slot->domain_id) != shard->shard_id) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_REFUSE,
                                     0,
                                     0u,
                                     DOM_SERVER_REFUSE_DOMAIN_FORBIDDEN,
                                     DOM_SERVER_DETAIL_DOMAIN_OWNER);
        return 0;
    }

    dom_server_scale_begin_tick(&shard->scale_ctx, runtime->now_tick);
    dom_scale_commit_token_make(&token, runtime->now_tick, 0u);
    memset(&result, 0, sizeof(result));
    scale_event_start = shard->scale_event_log.count;

    if (intent->intent_kind == DOM_SERVER_INTENT_OBSERVE) {
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_ACCEPT,
                                     0,
                                     scale_event_start,
                                     DOM_SERVER_REFUSE_NONE,
                                     DOM_SERVER_DETAIL_NONE);
        dom_server_emit_budget_snapshot(runtime, shard, client);
        dom_server_client_idempotent_record(client, intent->idempotency_key);
        return 1;
    }

    if (intent->intent_kind == DOM_SERVER_INTENT_COLLAPSE) {
        (void)dom_scale_collapse_domain(&shard->scale_ctx,
                                        &token,
                                        slot->domain_id,
                                        intent->detail_code ? intent->detail_code : 1u,
                                        &result);
        if (result.refusal_code != 0u) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         &result,
                                         scale_event_start,
                                         result.refusal_code,
                                         result.reason_code);
            return 0;
        }
        if (result.defer_code != DOM_SCALE_DEFER_NONE) {
            if (!dom_server_queue_deferred(runtime, intent, result.defer_code)) {
                dom_server_emit_intent_event(runtime,
                                             shard,
                                             client,
                                             intent,
                                             DOM_SERVER_EVENT_INTENT_REFUSE,
                                             &result,
                                             scale_event_start,
                                             DOM_SERVER_REFUSE_DEFER_QUEUE_LIMIT,
                                             DOM_SERVER_DETAIL_BUDGET_DEFER_LIMIT);
                return 0;
            }
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_DEFER,
                                         &result,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_NONE,
                                         result.defer_code);
            return 1;
        }
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_COLLAPSE,
                                     &result,
                                     scale_event_start,
                                     DOM_SERVER_REFUSE_NONE,
                                     result.reason_code);
        dom_server_client_idempotent_record(client, intent->idempotency_key);
        return 1;
    }

    if (intent->intent_kind == DOM_SERVER_INTENT_EXPAND) {
        u64 capsule_id = intent->capsule_id ? intent->capsule_id : slot->capsule_id;
        if (capsule_id == 0u) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         0,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_INVALID_INTENT,
                                         DOM_SERVER_DETAIL_DOMAIN_UNKNOWN);
            return 0;
        }
        (void)dom_scale_expand_domain(&shard->scale_ctx,
                                      &token,
                                      capsule_id,
                                      DOM_FID_MICRO,
                                      intent->detail_code ? intent->detail_code : 2u,
                                      &result);
        if (result.refusal_code != 0u) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         &result,
                                         scale_event_start,
                                         result.refusal_code,
                                         result.reason_code);
            return 0;
        }
        if (result.defer_code != DOM_SCALE_DEFER_NONE) {
            if (!dom_server_queue_deferred(runtime, intent, result.defer_code)) {
                dom_server_emit_intent_event(runtime,
                                             shard,
                                             client,
                                             intent,
                                             DOM_SERVER_EVENT_INTENT_REFUSE,
                                             &result,
                                             scale_event_start,
                                             DOM_SERVER_REFUSE_DEFER_QUEUE_LIMIT,
                                             DOM_SERVER_DETAIL_BUDGET_DEFER_LIMIT);
                return 0;
            }
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_DEFER,
                                         &result,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_NONE,
                                         result.defer_code);
            return 1;
        }
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_EXPAND,
                                     &result,
                                     scale_event_start,
                                     DOM_SERVER_REFUSE_NONE,
                                     result.reason_code);
        dom_server_client_idempotent_record(client, intent->idempotency_key);
        return 1;
    }

    if (intent->intent_kind == DOM_SERVER_INTENT_MACRO_ADVANCE) {
        u32 executed = 0u;
        dom_act_time_t up_to_tick = intent->detail_code ? (dom_act_time_t)intent->detail_code : runtime->now_tick;
        if ((client->policy.capability_mask & 1u) == 0u) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         0,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_CAPABILITY_MISSING,
                                         DOM_SERVER_DETAIL_MACRO_UNSUPPORTED);
            return 0;
        }
        (void)dom_scale_macro_advance(&shard->scale_ctx,
                                      &token,
                                      up_to_tick,
                                      &shard->macro_policy,
                                      &executed);
        if (executed == 0u && shard->scale_ctx.budget_state.refusal_macro_event_budget > 0u) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         0,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_MACRO_EVENT_BUDGET,
                                         DOM_SERVER_DETAIL_NONE);
            return 0;
        }
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_INTENT_ACCEPT,
                                     0,
                                     scale_event_start,
                                     DOM_SERVER_REFUSE_NONE,
                                     executed);
        dom_server_client_idempotent_record(client, intent->idempotency_key);
        return 1;
    }

    if (intent->intent_kind == DOM_SERVER_INTENT_TRANSFER_OWNERSHIP) {
        if (!dom_server_handle_transfer(runtime, shard, intent, slot)) {
            dom_server_emit_intent_event(runtime,
                                         shard,
                                         client,
                                         intent,
                                         DOM_SERVER_EVENT_INTENT_REFUSE,
                                         0,
                                         scale_event_start,
                                         DOM_SERVER_REFUSE_INVALID_INTENT,
                                         DOM_SERVER_DETAIL_DEST_SHARD);
            return 0;
        }
        dom_server_emit_intent_event(runtime,
                                     shard,
                                     client,
                                     intent,
                                     DOM_SERVER_EVENT_OWNERSHIP_TRANSFER,
                                     0,
                                     scale_event_start,
                                     DOM_SERVER_REFUSE_NONE,
                                     intent->payload_u32);
        dom_server_client_idempotent_record(client, intent->idempotency_key);
        return 1;
    }

    dom_server_emit_intent_event(runtime,
                                 shard,
                                 client,
                                 intent,
                                 DOM_SERVER_EVENT_INTENT_REFUSE,
                                 0,
                                 scale_event_start,
                                 DOM_SERVER_REFUSE_INVALID_INTENT,
                                 DOM_SERVER_DETAIL_NONE);
    return 0;
}

static void dom_server_process_deferred(dom_server_runtime* runtime)
{
    dom_server_deferred_intent pending[DOM_SERVER_MAX_DEFERRED];
    u32 pending_count = 0u;
    u32 i;
    if (!runtime || runtime->deferred_count == 0u) {
        return;
    }
    for (i = 0u; i < runtime->deferred_count; ++i) {
        dom_server_deferred_intent* item = &runtime->deferred[i];
        if (item->intent.intent_tick > runtime->now_tick) {
            pending[pending_count++] = *item;
            continue;
        }
        if (!dom_server_process_intent(runtime, &item->intent)) {
            pending[pending_count++] = *item;
        }
    }
    runtime->deferred_count = pending_count;
    for (i = 0u; i < pending_count; ++i) {
        runtime->deferred[i] = pending[i];
    }
    dom_server_sort_deferred(runtime->deferred, runtime->deferred_count);
}

static void dom_server_process_messages(dom_server_runtime* runtime)
{
    dom_cross_shard_message msg;
    u32 skipped = 0u;
    if (!runtime) {
        return;
    }
    while (dom_cross_shard_log_pop_next_ready(&runtime->message_log,
                                              runtime->now_tick,
                                              &msg,
                                              &skipped)) {
        (void)skipped;
        (void)dom_server_apply_message(runtime, &msg);
    }
}

static void dom_server_collect_ready_intents(dom_server_runtime* runtime,
                                             dom_server_intent* out_ready,
                                             u32* out_ready_count)
{
    u32 i;
    u32 ready_count = 0u;
    if (!runtime || !out_ready || !out_ready_count) {
        return;
    }
    for (i = 0u; i < runtime->intent_count; ++i) {
        if (runtime->intents[i].intent_tick <= runtime->now_tick) {
            out_ready[ready_count++] = runtime->intents[i];
        }
    }
    dom_server_sort_intents(out_ready, ready_count);
    *out_ready_count = ready_count;
}

static void dom_server_retain_future_intents(dom_server_runtime* runtime)
{
    dom_server_intent future[DOM_SERVER_MAX_INTENTS];
    u32 future_count = 0u;
    u32 i;
    if (!runtime) {
        return;
    }
    for (i = 0u; i < runtime->intent_count; ++i) {
        if (runtime->intents[i].intent_tick > runtime->now_tick) {
            future[future_count++] = runtime->intents[i];
        }
    }
    runtime->intent_count = future_count;
    for (i = 0u; i < future_count; ++i) {
        runtime->intents[i] = future[i];
    }
    dom_server_sort_intents(runtime->intents, runtime->intent_count);
}

void dom_server_runtime_config_default(dom_server_runtime_config* config)
{
    if (!config) {
        return;
    }
    memset(config, 0, sizeof(*config));
    config->start_tick = 0;
    config->shard_count = 1u;
    config->worker_count = 1u;
    dom_scale_budget_policy_default(&config->scale_budget_policy);
    config->scale_budget_policy.min_dwell_ticks = 0;
    dom_scale_macro_policy_default(&config->macro_policy);
    config->default_client_policy.intents_per_tick = 16u;
    config->default_client_policy.bytes_per_tick = 1024u;
    config->default_client_policy.inspect_only = 0u;
    config->default_client_policy.capability_mask = 1u;
    config->deferred_limit = DOM_SERVER_MAX_DEFERRED;
}

int dom_server_runtime_init(dom_server_runtime* runtime,
                            const dom_server_runtime_config* config)
{
    u32 i;
    dom_server_runtime_config local;
    if (!runtime) {
        return -1;
    }
    dom_server_runtime_config_default(&local);
    if (config) {
        local = *config;
    }
    if (local.shard_count == 0u) {
        local.shard_count = 1u;
    }
    if (local.shard_count > DOM_SERVER_MAX_SHARDS) {
        local.shard_count = DOM_SERVER_MAX_SHARDS;
    }
    memset(runtime, 0, sizeof(*runtime));
    runtime->config = local;
    runtime->now_tick = local.start_tick;
    runtime->shard_count = local.shard_count;
    runtime->message_sequence = 0u;
    runtime->message_applied = 0u;

    dom_cross_shard_log_init(&runtime->message_log,
                             runtime->message_storage,
                             DOM_SERVER_MAX_MESSAGES,
                             runtime->message_idempotency,
                             DOM_SERVER_MAX_IDEMPOTENCY);

    for (i = 0u; i < runtime->shard_count; ++i) {
        dom_server_shard* shard = &runtime->shards[i];
        dom_shard_id shard_id = (dom_shard_id)(i + 1u);
        if (dom_server_shard_init(shard, &runtime->config, shard_id) != 0) {
            return -2;
        }
        dom_server_owner_set(runtime, shard->domain_storage[0].domain_id, shard_id);
        dom_server_owner_set(runtime, shard->domain_storage[1].domain_id, shard_id);
        dom_server_owner_set(runtime, shard->domain_storage[2].domain_id, shard_id);
        dom_server_scale_begin_tick(&shard->scale_ctx, runtime->now_tick);
    }
    return 0;
}

int dom_server_runtime_add_client(dom_server_runtime* runtime,
                                  u64 client_id,
                                  dom_shard_id shard_id,
                                  const dom_server_client_policy* policy)
{
    dom_server_client* client;
    if (!runtime || client_id == 0u || shard_id == 0u) {
        return -1;
    }
    if (!dom_server_find_shard(runtime, shard_id)) {
        return -2;
    }
    client = dom_server_find_client(runtime, client_id);
    if (client) {
        return -3;
    }
    if (runtime->client_count >= DOM_SERVER_MAX_CLIENTS) {
        return -4;
    }
    client = &runtime->clients[runtime->client_count++];
    memset(client, 0, sizeof(*client));
    client->client_id = client_id;
    client->shard_id = shard_id;
    client->policy = policy ? *policy : runtime->config.default_client_policy;
    dom_server_client_budget_reset(client, runtime->now_tick);
    return 0;
}

int dom_server_runtime_submit_intent(dom_server_runtime* runtime,
                                     const dom_server_intent* intent,
                                     u32 payload_bytes)
{
    dom_server_intent local;
    dom_server_shard* shard = 0;
    dom_global_id gid;
    u64 packed = 0u;
    if (!runtime || !intent) {
        return -1;
    }
    if (runtime->intent_count >= DOM_SERVER_MAX_INTENTS) {
        runtime->intent_overflow += 1u;
        return -2;
    }
    shard = dom_server_find_shard(runtime, intent->target_shard_id);
    if (!shard) {
        return -3;
    }
    local = *intent;
    if (local.intent_tick == 0) {
        local.intent_tick = runtime->now_tick;
    }
    local.payload_bytes = payload_bytes;
    if (local.intent_id == 0u) {
        (void)dom_global_id_next(&shard->id_gen, DOM_SERVER_NS_INTENT, &gid, &packed);
        local.intent_id = packed;
    }
    runtime->intents[runtime->intent_count++] = local;
    dom_server_sort_intents(runtime->intents, runtime->intent_count);
    return 0;
}

int dom_server_runtime_tick(dom_server_runtime* runtime, dom_act_time_t tick)
{
    dom_act_time_t t;
    if (!runtime) {
        return -1;
    }
    if (tick < runtime->now_tick) {
        return -2;
    }
    for (t = runtime->now_tick; t <= tick; ++t) {
        dom_server_intent ready[DOM_SERVER_MAX_INTENTS];
        u32 ready_count = 0u;
        u32 i;
        runtime->now_tick = t;
        for (i = 0u; i < runtime->client_count; ++i) {
            dom_server_client_budget_reset(&runtime->clients[i], runtime->now_tick);
        }
        for (i = 0u; i < runtime->shard_count; ++i) {
            dom_server_scale_begin_tick(&runtime->shards[i].scale_ctx, runtime->now_tick);
        }
        dom_server_process_messages(runtime);
        dom_server_process_deferred(runtime);
        dom_server_collect_ready_intents(runtime, ready, &ready_count);
        for (i = 0u; i < ready_count; ++i) {
            (void)dom_server_process_intent(runtime, &ready[i]);
        }
        dom_server_retain_future_intents(runtime);
        if (t == tick) {
            break;
        }
    }
    return 0;
}

int dom_server_runtime_join(dom_server_runtime* runtime,
                            u64 client_id,
                            dom_server_join_bundle* out_bundle)
{
    dom_server_client* client;
    dom_server_shard* shard;
    dom_server_event ev;
    if (!runtime || !out_bundle) {
        return -1;
    }
    client = dom_server_find_client(runtime, client_id);
    if (!client) {
        return -2;
    }
    shard = dom_server_find_shard(runtime, client->shard_id);
    if (!shard) {
        return -3;
    }
    memset(out_bundle, 0, sizeof(*out_bundle));
    out_bundle->client_id = client->client_id;
    out_bundle->assigned_shard_id = shard->shard_id;
    out_bundle->tick = runtime->now_tick;
    out_bundle->world_hash = dom_server_runtime_hash(runtime);
    out_bundle->capability_hash = dom_server_capability_hash(client);
    dom_server_snapshot_for_shard(shard, &out_bundle->snapshot);
    out_bundle->inspect_only = client->policy.inspect_only;
    out_bundle->event_tail_index = runtime->event_count;
    out_bundle->message_tail_index = (u32)(runtime->message_sequence & 0xFFFFFFFFu);

    memset(&ev, 0, sizeof(ev));
    ev.tick = runtime->now_tick;
    ev.shard_id = shard->shard_id;
    ev.client_id = client->client_id;
    ev.event_kind = DOM_SERVER_EVENT_JOIN;
    ev.client_budget = client->budget_state;
    dom_server_capture_scale_budget(&shard->scale_ctx, &ev.scale_budget);
    (void)dom_server_event_append(runtime, shard, &ev);
    return 0;
}

int dom_server_runtime_resync(dom_server_runtime* runtime,
                              u64 client_id,
                              dom_shard_id shard_id,
                              u32 allow_partial,
                              dom_server_resync_bundle* out_bundle)
{
    dom_server_client* client;
    dom_server_shard* shard;
    dom_server_event ev;
    u32 refusal = DOM_SERVER_REFUSE_NONE;
    if (!runtime || !out_bundle) {
        return -1;
    }
    client = dom_server_find_client(runtime, client_id);
    shard = dom_server_find_shard(runtime, shard_id);
    if (!client || !shard) {
        return -2;
    }
    if (!allow_partial && client->policy.inspect_only) {
        refusal = DOM_SERVER_REFUSE_CAPABILITY_MISSING;
    }
    memset(out_bundle, 0, sizeof(*out_bundle));
    out_bundle->client_id = client->client_id;
    out_bundle->shard_id = shard->shard_id;
    out_bundle->tick = runtime->now_tick;
    out_bundle->world_hash = dom_server_runtime_hash(runtime);
    dom_server_snapshot_for_shard(shard, &out_bundle->snapshot);
    out_bundle->event_tail_index = runtime->event_count;
    out_bundle->message_tail_index = (u32)(runtime->message_sequence & 0xFFFFFFFFu);
    out_bundle->refusal_code = refusal;

    memset(&ev, 0, sizeof(ev));
    ev.tick = runtime->now_tick;
    ev.shard_id = shard->shard_id;
    ev.client_id = client->client_id;
    ev.event_kind = DOM_SERVER_EVENT_RESYNC;
    ev.refusal_code = refusal;
    ev.client_budget = client->budget_state;
    dom_server_capture_scale_budget(&shard->scale_ctx, &ev.scale_budget);
    (void)dom_server_event_append(runtime, shard, &ev);
    return refusal == DOM_SERVER_REFUSE_NONE ? 0 : 1;
}

u64 dom_server_runtime_hash(const dom_server_runtime* runtime)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!runtime) {
        return hash;
    }
    hash = dom_server_hash_mix(hash, runtime->now_tick);
    hash = dom_server_hash_mix(hash, runtime->shard_count);
    hash = dom_server_hash_mix(hash, runtime->client_count);
    hash = dom_server_hash_mix(hash, runtime->intent_count);
    hash = dom_server_hash_mix(hash, runtime->deferred_count);
    hash = dom_server_hash_mix(hash, runtime->owner_count);
    hash = dom_server_hash_mix(hash, runtime->event_count);
    hash = dom_server_hash_mix(hash, runtime->event_overflow);
    hash = dom_server_hash_mix(hash, runtime->message_sequence);
    hash = dom_server_hash_mix(hash, runtime->message_applied);
    hash = dom_server_hash_mix(hash, dom_cross_shard_log_hash(&runtime->message_log));
    for (i = 0u; i < runtime->owner_count; ++i) {
        hash = dom_server_hash_mix(hash, runtime->owners[i].domain_id);
        hash = dom_server_hash_mix(hash, runtime->owners[i].owner_shard_id);
    }
    for (i = 0u; i < runtime->shard_count; ++i) {
        const dom_server_shard* shard = &runtime->shards[i];
        u32 d;
        hash = dom_server_hash_mix(hash, shard->shard_id);
        hash = dom_server_hash_mix(hash, dom_server_scale_event_hash(&shard->scale_event_log));
        for (d = 0u; d < shard->scale_ctx.domain_count; ++d) {
            const dom_scale_domain_slot* slot = &shard->scale_ctx.domains[d];
            hash = dom_server_hash_mix(hash,
                                       dom_server_domain_hash(slot,
                                                              runtime->now_tick,
                                                              shard->scale_ctx.worker_count));
        }
    }
    for (i = 0u; i < runtime->event_count; ++i) {
        const dom_server_event* ev = &runtime->events[i];
        hash = dom_server_hash_mix(hash, ev->event_id);
        hash = dom_server_hash_mix(hash, ev->tick);
        hash = dom_server_hash_mix(hash, ev->shard_id);
        hash = dom_server_hash_mix(hash, ev->client_id);
        hash = dom_server_hash_mix(hash, ev->domain_id);
        hash = dom_server_hash_mix(hash, ev->capsule_id);
        hash = dom_server_hash_mix(hash, ev->event_kind);
        hash = dom_server_hash_mix(hash, ev->intent_kind);
        hash = dom_server_hash_mix(hash, ev->refusal_code);
        hash = dom_server_hash_mix(hash, ev->defer_code);
        hash = dom_server_hash_mix(hash, ev->budget_kind);
        hash = dom_server_hash_mix(hash, ev->budget_limit);
        hash = dom_server_hash_mix(hash, ev->budget_used);
        hash = dom_server_hash_mix(hash, ev->budget_cost);
        hash = dom_server_hash_mix(hash, ev->detail_code);
        hash = dom_server_hash_mix(hash, ev->payload_u32);
    }
    return hash;
}

u32 dom_server_runtime_event_count(const dom_server_runtime* runtime)
{
    return runtime ? runtime->event_count : 0u;
}

int dom_server_runtime_event_get(const dom_server_runtime* runtime,
                                 u32 index,
                                 dom_server_event* out_event)
{
    if (!runtime || !out_event || index >= runtime->event_count) {
        return 0;
    }
    *out_event = runtime->events[index];
    return 1;
}

int dom_server_runtime_set_scale_budget(dom_server_runtime* runtime,
                                        dom_shard_id shard_id,
                                        const dom_scale_budget_policy* policy)
{
    dom_server_shard* shard;
    if (!runtime || !policy) {
        return -1;
    }
    shard = dom_server_find_shard(runtime, shard_id);
    if (!shard) {
        return -2;
    }
    shard->scale_ctx.budget_policy = *policy;
    dom_server_scale_begin_tick(&shard->scale_ctx, runtime->now_tick);
    return 0;
}

int dom_server_runtime_set_client_policy(dom_server_runtime* runtime,
                                         u64 client_id,
                                         const dom_server_client_policy* policy)
{
    dom_server_client* client;
    if (!runtime || !policy) {
        return -1;
    }
    client = dom_server_find_client(runtime, client_id);
    if (!client) {
        return -2;
    }
    client->policy = *policy;
    dom_server_client_budget_reset(client, runtime->now_tick);
    return 0;
}

int dom_server_runtime_budget_snapshot(dom_server_runtime* runtime,
                                       u64 client_id,
                                       dom_server_budget_state* out_state)
{
    dom_server_client* client;
    if (!runtime || !out_state) {
        return -1;
    }
    client = dom_server_find_client(runtime, client_id);
    if (!client) {
        return -2;
    }
    *out_state = client->budget_state;
    return 0;
}

int dom_server_runtime_scale_snapshot(dom_server_runtime* runtime,
                                      dom_shard_id shard_id,
                                      dom_scale_budget_snapshot* out_snapshot)
{
    dom_server_shard* shard;
    if (!runtime || !out_snapshot) {
        return -1;
    }
    shard = dom_server_find_shard(runtime, shard_id);
    if (!shard) {
        return -2;
    }
    dom_server_scale_begin_tick(&shard->scale_ctx, runtime->now_tick);
    dom_scale_budget_snapshot_current(&shard->scale_ctx, out_snapshot);
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
