/*
FILE: server/persistence/dom_checkpointing.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic MMO checkpoint capture, storage, and recovery.
*/
#include "dom_checkpointing.h"

#include "net/dom_server_runtime.h"

#include <string.h>

static u64 dom_checkpoint_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static void dom_checkpoint_clear_worlds(dom_checkpoint_record* record)
{
    u32 i;
    if (!record) {
        return;
    }
    for (i = 0u; i < DOM_SERVER_MAX_SHARDS; ++i) {
        record->world_clones[i] = (d_world*)0;
    }
}

static void dom_checkpoint_destroy_worlds(d_world** worlds, u32 count)
{
    u32 i;
    if (!worlds) {
        return;
    }
    for (i = 0u; i < count; ++i) {
        if (worlds[i]) {
            d_world_destroy_instance(worlds[i]);
            worlds[i] = (d_world*)0;
        }
    }
}

static u64 dom_checkpoint_scale_event_hash(const dom_scale_event_log* log)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!log || !log->events) {
        return hash;
    }
    hash = dom_checkpoint_hash_mix(hash, log->count);
    hash = dom_checkpoint_hash_mix(hash, log->overflow);
    for (i = 0u; i < log->count; ++i) {
        const dom_scale_event* ev = &log->events[i];
        hash = dom_checkpoint_hash_mix(hash, ev->kind);
        hash = dom_checkpoint_hash_mix(hash, ev->domain_id);
        hash = dom_checkpoint_hash_mix(hash, ev->domain_kind);
        hash = dom_checkpoint_hash_mix(hash, ev->capsule_id);
        hash = dom_checkpoint_hash_mix(hash, ev->reason_code);
        hash = dom_checkpoint_hash_mix(hash, ev->refusal_code);
        hash = dom_checkpoint_hash_mix(hash, ev->defer_code);
        hash = dom_checkpoint_hash_mix(hash, ev->detail_code);
        hash = dom_checkpoint_hash_mix(hash, ev->seed_value);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_kind);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_limit);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_used);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_cost);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_queue);
        hash = dom_checkpoint_hash_mix(hash, ev->budget_overflow);
        hash = dom_checkpoint_hash_mix(hash, (u64)ev->tick);
    }
    return hash;
}

static u64 dom_checkpoint_budget_state_hash(const dom_scale_budget_state* state)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!state) {
        return hash;
    }
    hash = dom_checkpoint_hash_mix(hash, state->active_tier2_domains);
    hash = dom_checkpoint_hash_mix(hash, state->active_tier1_domains);
    hash = dom_checkpoint_hash_mix(hash, state->refinement_used);
    hash = dom_checkpoint_hash_mix(hash, state->planning_used);
    hash = dom_checkpoint_hash_mix(hash, state->collapse_used);
    hash = dom_checkpoint_hash_mix(hash, state->expand_used);
    hash = dom_checkpoint_hash_mix(hash, state->macro_event_used);
    hash = dom_checkpoint_hash_mix(hash, state->compaction_used);
    hash = dom_checkpoint_hash_mix(hash, state->snapshot_used);
    hash = dom_checkpoint_hash_mix(hash, (u64)state->budget_tick);
    hash = dom_checkpoint_hash_mix(hash, state->deferred_count);
    hash = dom_checkpoint_hash_mix(hash, state->deferred_overflow);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_active_domain_limit);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_refinement_budget);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_macro_event_budget);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_agent_planning_budget);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_snapshot_budget);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_collapse_budget);
    hash = dom_checkpoint_hash_mix(hash, state->refusal_defer_queue_limit);
    for (i = 0u; i < state->deferred_count && i < DOM_SCALE_DEFER_QUEUE_CAP; ++i) {
        const dom_scale_deferred_op* op = &state->deferred_ops[i];
        hash = dom_checkpoint_hash_mix(hash, op->kind);
        hash = dom_checkpoint_hash_mix(hash, op->budget_kind);
        hash = dom_checkpoint_hash_mix(hash, op->domain_id);
        hash = dom_checkpoint_hash_mix(hash, op->capsule_id);
        hash = dom_checkpoint_hash_mix(hash, op->target_tier);
        hash = dom_checkpoint_hash_mix(hash, (u64)op->requested_tick);
        hash = dom_checkpoint_hash_mix(hash, op->reason_code);
    }
    return hash;
}

static u64 dom_checkpoint_budget_snapshot_hash(const dom_scale_budget_snapshot* snap)
{
    u64 hash = 1469598103934665603ULL;
    if (!snap) {
        return hash;
    }
    hash = dom_checkpoint_hash_mix(hash, (u64)snap->tick);
    hash = dom_checkpoint_hash_mix(hash, snap->active_tier1_domains);
    hash = dom_checkpoint_hash_mix(hash, snap->active_tier2_domains);
    hash = dom_checkpoint_hash_mix(hash, snap->tier1_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->tier2_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->refinement_used);
    hash = dom_checkpoint_hash_mix(hash, snap->refinement_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->planning_used);
    hash = dom_checkpoint_hash_mix(hash, snap->planning_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->collapse_used);
    hash = dom_checkpoint_hash_mix(hash, snap->collapse_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->expand_used);
    hash = dom_checkpoint_hash_mix(hash, snap->expand_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->macro_event_used);
    hash = dom_checkpoint_hash_mix(hash, snap->macro_event_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->snapshot_used);
    hash = dom_checkpoint_hash_mix(hash, snap->snapshot_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->deferred_count);
    hash = dom_checkpoint_hash_mix(hash, snap->deferred_overflow);
    hash = dom_checkpoint_hash_mix(hash, snap->deferred_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_active_domain_limit);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_refinement_budget);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_macro_event_budget);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_agent_planning_budget);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_snapshot_budget);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_collapse_budget);
    hash = dom_checkpoint_hash_mix(hash, snap->refusal_defer_queue_limit);
    return hash;
}

static u64 dom_checkpoint_shard_hash(const dom_shard_checkpoint* shard,
                                     dom_act_time_t tick,
                                     u32 workers)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!shard) {
        return hash;
    }
    hash = dom_checkpoint_hash_mix(hash, shard->shard_id);
    hash = dom_checkpoint_hash_mix(hash, (u64)tick);
    hash = dom_checkpoint_hash_mix(hash, workers);
    hash = dom_checkpoint_hash_mix(hash, shard->lifecycle_state);
    hash = dom_checkpoint_hash_mix(hash, shard->version_id);
    hash = dom_checkpoint_hash_mix(hash, shard->capability_mask);
    hash = dom_checkpoint_hash_mix(hash, shard->baseline_hash);
    hash = dom_checkpoint_hash_mix(hash, shard->world_checksum);
    hash = dom_checkpoint_hash_mix(hash, shard->domain_count);
    for (i = 0u; i < shard->domain_count && i < DOM_SERVER_MAX_DOMAINS_PER_SHARD; ++i) {
        hash = dom_checkpoint_hash_mix(hash, shard->domain_hashes[i]);
        hash = dom_checkpoint_hash_mix(hash, shard->capsule_ids[i]);
    }
    hash = dom_checkpoint_hash_mix(hash, dom_checkpoint_budget_state_hash(&shard->budget_state));
    hash = dom_checkpoint_hash_mix(hash, dom_checkpoint_budget_snapshot_hash(&shard->budget_snapshot));
    hash = dom_checkpoint_hash_mix(hash, shard->scale_event_hash);
    hash = dom_checkpoint_hash_mix(hash, shard->scale_event_count);
    hash = dom_checkpoint_hash_mix(hash, shard->scale_event_overflow);
    return hash;
}

static int dom_checkpoint_copy_domains(dom_shard_checkpoint* out,
                                       const dom_server_shard* shard,
                                       dom_act_time_t tick)
{
    u32 i;
    u32 res_off = 0u;
    u32 node_off = 0u;
    u32 edge_off = 0u;
    u32 agent_off = 0u;
    const u32 res_cap = (u32)(sizeof(out->resource_entries) / sizeof(out->resource_entries[0]));
    const u32 node_cap = (u32)(sizeof(out->network_nodes) / sizeof(out->network_nodes[0]));
    const u32 edge_cap = (u32)(sizeof(out->network_edges) / sizeof(out->network_edges[0]));
    const u32 agent_cap = (u32)(sizeof(out->agent_entries) / sizeof(out->agent_entries[0]));

    if (!out || !shard) {
        return -1;
    }
    out->domain_count = shard->scale_ctx.domain_count;
    if (out->domain_count > DOM_SERVER_MAX_DOMAINS_PER_SHARD) {
        out->domain_count = DOM_SERVER_MAX_DOMAINS_PER_SHARD;
    }

    for (i = 0u; i < out->domain_count; ++i) {
        const dom_scale_domain_slot* src = &shard->scale_ctx.domains[i];
        dom_scale_domain_slot* dst = &out->domains[i];
        memset(dst, 0, sizeof(*dst));
        dst->domain_id = src->domain_id;
        dst->domain_kind = src->domain_kind;
        dst->tier = src->tier;
        dst->last_transition_tick = src->last_transition_tick;
        dst->capsule_id = src->capsule_id;

        if (src->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
            const u32 count = src->resources.count;
            if (res_off + count > res_cap) {
                return -2;
            }
            if (count > 0u && src->resources.entries) {
                memcpy(&out->resource_entries[res_off],
                       src->resources.entries,
                       sizeof(out->resource_entries[0]) * (size_t)count);
            }
            dst->resources.entries = &out->resource_entries[res_off];
            dst->resources.count = count;
            dst->resources.capacity = res_cap - res_off;
            res_off += count;
        } else if (src->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
            const u32 node_count = src->network.node_count;
            const u32 edge_count = src->network.edge_count;
            if (node_off + node_count > node_cap || edge_off + edge_count > edge_cap) {
                return -3;
            }
            if (node_count > 0u && src->network.nodes) {
                memcpy(&out->network_nodes[node_off],
                       src->network.nodes,
                       sizeof(out->network_nodes[0]) * (size_t)node_count);
            }
            if (edge_count > 0u && src->network.edges) {
                memcpy(&out->network_edges[edge_off],
                       src->network.edges,
                       sizeof(out->network_edges[0]) * (size_t)edge_count);
            }
            dst->network.nodes = &out->network_nodes[node_off];
            dst->network.node_count = node_count;
            dst->network.node_capacity = node_cap - node_off;
            dst->network.edges = &out->network_edges[edge_off];
            dst->network.edge_count = edge_count;
            dst->network.edge_capacity = edge_cap - edge_off;
            node_off += node_count;
            edge_off += edge_count;
        } else if (src->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
            const u32 count = src->agents.count;
            if (agent_off + count > agent_cap) {
                return -4;
            }
            if (count > 0u && src->agents.entries) {
                memcpy(&out->agent_entries[agent_off],
                       src->agents.entries,
                       sizeof(out->agent_entries[0]) * (size_t)count);
            }
            dst->agents.entries = &out->agent_entries[agent_off];
            dst->agents.count = count;
            dst->agents.capacity = agent_cap - agent_off;
            agent_off += count;
        } else {
            return -5;
        }

        out->capsule_ids[i] = dst->capsule_id;
        out->domain_hashes[i] = dom_scale_domain_hash(dst, tick, shard->scale_ctx.worker_count);
    }

    for (; i < DOM_SERVER_MAX_DOMAINS_PER_SHARD; ++i) {
        out->capsule_ids[i] = 0u;
        out->domain_hashes[i] = 0u;
    }

    return 0;
}

static int dom_checkpoint_restore_domains(dom_server_shard* shard,
                                          const dom_shard_checkpoint* chk,
                                          dom_act_time_t tick)
{
    u32 i;
    u32 res_off = 0u;
    u32 node_off = 0u;
    u32 edge_off = 0u;
    u32 agent_off = 0u;
    const u32 res_cap = (u32)(sizeof(shard->resource_entries) / sizeof(shard->resource_entries[0]));
    const u32 node_cap = (u32)(sizeof(shard->network_nodes) / sizeof(shard->network_nodes[0]));
    const u32 edge_cap = (u32)(sizeof(shard->network_edges) / sizeof(shard->network_edges[0]));
    const u32 agent_cap = (u32)(sizeof(shard->agent_entries) / sizeof(shard->agent_entries[0]));

    if (!shard || !chk) {
        return -1;
    }

    shard->scale_ctx.domain_count = chk->domain_count;
    if (shard->scale_ctx.domain_count > DOM_SERVER_MAX_DOMAINS_PER_SHARD) {
        shard->scale_ctx.domain_count = DOM_SERVER_MAX_DOMAINS_PER_SHARD;
    }

    for (i = 0u; i < shard->scale_ctx.domain_count; ++i) {
        const dom_scale_domain_slot* src = &chk->domains[i];
        dom_scale_domain_slot* dst = &shard->domain_storage[i];
        const u64 expected_hash = chk->domain_hashes[i];

        memset(dst, 0, sizeof(*dst));
        dst->domain_id = src->domain_id;
        dst->domain_kind = src->domain_kind;
        dst->tier = src->tier;
        dst->last_transition_tick = src->last_transition_tick;
        dst->capsule_id = src->capsule_id;

        if (src->domain_kind == DOM_SCALE_DOMAIN_RESOURCES) {
            const u32 count = src->resources.count;
            if (res_off + count > res_cap) {
                return -2;
            }
            if (count > 0u && src->resources.entries) {
                memcpy(&shard->resource_entries[res_off],
                       src->resources.entries,
                       sizeof(shard->resource_entries[0]) * (size_t)count);
            }
            dst->resources.entries = &shard->resource_entries[res_off];
            dst->resources.count = count;
            dst->resources.capacity = res_cap - res_off;
            res_off += count;
        } else if (src->domain_kind == DOM_SCALE_DOMAIN_NETWORK) {
            const u32 node_count = src->network.node_count;
            const u32 edge_count = src->network.edge_count;
            if (node_off + node_count > node_cap || edge_off + edge_count > edge_cap) {
                return -3;
            }
            if (node_count > 0u && src->network.nodes) {
                memcpy(&shard->network_nodes[node_off],
                       src->network.nodes,
                       sizeof(shard->network_nodes[0]) * (size_t)node_count);
            }
            if (edge_count > 0u && src->network.edges) {
                memcpy(&shard->network_edges[edge_off],
                       src->network.edges,
                       sizeof(shard->network_edges[0]) * (size_t)edge_count);
            }
            dst->network.nodes = &shard->network_nodes[node_off];
            dst->network.node_count = node_count;
            dst->network.node_capacity = node_cap - node_off;
            dst->network.edges = &shard->network_edges[edge_off];
            dst->network.edge_count = edge_count;
            dst->network.edge_capacity = edge_cap - edge_off;
            node_off += node_count;
            edge_off += edge_count;
        } else if (src->domain_kind == DOM_SCALE_DOMAIN_AGENTS) {
            const u32 count = src->agents.count;
            if (agent_off + count > agent_cap) {
                return -4;
            }
            if (count > 0u && src->agents.entries) {
                memcpy(&shard->agent_entries[agent_off],
                       src->agents.entries,
                       sizeof(shard->agent_entries[0]) * (size_t)count);
            }
            dst->agents.entries = &shard->agent_entries[agent_off];
            dst->agents.count = count;
            dst->agents.capacity = agent_cap - agent_off;
            agent_off += count;
        } else {
            return -5;
        }

        if (expected_hash != 0u) {
            const u64 hash = dom_scale_domain_hash(dst, tick, shard->scale_ctx.worker_count);
            if (hash != expected_hash) {
                return -6;
            }
        }
    }

    return 0;
}

void dom_checkpoint_policy_default(dom_checkpoint_policy* policy)
{
    if (!policy) {
        return;
    }
    memset(policy, 0, sizeof(*policy));
    policy->interval_ticks = 256u;
    policy->macro_event_stride = 128u;
    policy->checkpoint_before_transfer = 1u;
    policy->max_records = DOM_CHECKPOINT_MAX_RECORDS;
}

void dom_checkpoint_store_init(dom_checkpoint_store* store,
                               dom_checkpoint_record* storage,
                               u32 capacity)
{
    u32 i;
    if (!store) {
        return;
    }
    memset(store, 0, sizeof(*store));
    store->records = storage;
    store->capacity = capacity;
    if (!storage || capacity == 0u) {
        store->capacity = 0u;
        return;
    }
    for (i = 0u; i < capacity; ++i) {
        memset(&storage[i], 0, sizeof(storage[i]));
        dom_checkpoint_clear_worlds(&storage[i]);
    }
}

const dom_checkpoint_record* dom_checkpoint_store_last(const dom_checkpoint_store* store)
{
    u32 index;
    if (!store || !store->records || store->capacity == 0u || store->count == 0u) {
        return 0;
    }
    index = store->head == 0u ? (store->capacity - 1u) : (store->head - 1u);
    if (index >= store->capacity) {
        return 0;
    }
    return &store->records[index];
}

int dom_checkpoint_store_record(dom_checkpoint_store* store,
                                dom_checkpoint_record* record)
{
    dom_checkpoint_record* dst;
    u32 i;
    if (!store || !store->records || store->capacity == 0u || !record) {
        return -1;
    }

    dst = &store->records[store->head];
    if (store->count >= store->capacity) {
        dom_checkpoint_record_dispose(dst);
        store->overflow += 1u;
    } else {
        store->count += 1u;
    }

    memcpy(dst, record, sizeof(*dst));
    for (i = 0u; i < DOM_SERVER_MAX_SHARDS; ++i) {
        dst->world_clones[i] = record->world_clones[i];
        record->world_clones[i] = (d_world*)0;
    }

    store->head += 1u;
    if (store->head >= store->capacity) {
        store->head = 0u;
    }
    return 0;
}

static const dom_checkpoint_record* dom_checkpoint_store_at(const dom_checkpoint_store* store,
                                                            u32 ordinal)
{
    u32 idx;
    u32 start;
    if (!store || !store->records || store->capacity == 0u || ordinal >= store->count) {
        return 0;
    }
    start = (store->head + store->capacity - store->count) % store->capacity;
    idx = (start + ordinal) % store->capacity;
    return &store->records[idx];
}

u64 dom_checkpoint_store_hash(const dom_checkpoint_store* store)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    if (!store || !store->records || store->capacity == 0u) {
        return hash;
    }
    hash = dom_checkpoint_hash_mix(hash, store->capacity);
    hash = dom_checkpoint_hash_mix(hash, store->count);
    hash = dom_checkpoint_hash_mix(hash, store->head);
    hash = dom_checkpoint_hash_mix(hash, store->overflow);
    for (i = 0u; i < store->count; ++i) {
        const dom_checkpoint_record* rec = dom_checkpoint_store_at(store, i);
        u32 s;
        if (!rec) {
            continue;
        }
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.schema_version);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.checkpoint_id);
        hash = dom_checkpoint_hash_mix(hash, (u64)rec->manifest.tick);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.trigger_reason);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.worlddef_hash);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.capability_lock_hash);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.runtime_hash);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.lifecycle_hash);
        hash = dom_checkpoint_hash_mix(hash, rec->lifecycle_count);
        hash = dom_checkpoint_hash_mix(hash, rec->lifecycle_overflow);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.message_sequence);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.message_applied);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.macro_events_executed);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.event_count);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.event_overflow);
        hash = dom_checkpoint_hash_mix(hash, rec->manifest.shard_count);
        hash = dom_checkpoint_hash_mix(hash, rec->intent_count);
        hash = dom_checkpoint_hash_mix(hash, rec->intent_overflow);
        hash = dom_checkpoint_hash_mix(hash, rec->deferred_count);
        hash = dom_checkpoint_hash_mix(hash, rec->deferred_overflow);
        hash = dom_checkpoint_hash_mix(hash, rec->event_count);
        hash = dom_checkpoint_hash_mix(hash, rec->event_overflow);
        hash = dom_checkpoint_hash_mix(hash, rec->owner_count);
        hash = dom_checkpoint_hash_mix(hash, rec->message_count);
        hash = dom_checkpoint_hash_mix(hash, rec->idempotency_count);
        for (s = 0u; s < rec->manifest.shard_count && s < DOM_SERVER_MAX_SHARDS; ++s) {
            const dom_shard_checkpoint* shard = &rec->shards[s];
            hash = dom_checkpoint_hash_mix(hash, shard->shard_hash);
            if (rec->world_clones[s]) {
                hash = dom_checkpoint_hash_mix(hash, d_world_checksum(rec->world_clones[s]));
            }
        }
    }
    return hash;
}

static u64 dom_checkpoint_make_id(const dom_server_runtime* runtime,
                                  u32 trigger_reason)
{
    u64 hash = 1469598103934665603ULL;
    u64 lifecycle_hash;
    if (!runtime) {
        return hash;
    }
    lifecycle_hash = dom_shard_lifecycle_log_hash(&runtime->lifecycle_log);
    hash = dom_checkpoint_hash_mix(hash, (u64)runtime->now_tick);
    hash = dom_checkpoint_hash_mix(hash, trigger_reason);
    hash = dom_checkpoint_hash_mix(hash, lifecycle_hash);
    hash = dom_checkpoint_hash_mix(hash, runtime->config.worlddef_hash);
    hash = dom_checkpoint_hash_mix(hash, runtime->config.capability_lock_hash);
    hash = dom_checkpoint_hash_mix(hash, runtime->message_sequence);
    hash = dom_checkpoint_hash_mix(hash, runtime->message_applied);
    hash = dom_checkpoint_hash_mix(hash, runtime->macro_events_executed);
    hash = dom_checkpoint_hash_mix(hash, dom_server_runtime_hash(runtime));
    return hash;
}

int dom_checkpoint_capture(dom_checkpoint_record* out_record,
                           const dom_server_runtime* runtime,
                           u32 trigger_reason)
{
    u32 i;
    u32 lifecycle_cap;
    u64 lifecycle_hash;
    if (!out_record || !runtime) {
        return -1;
    }

    memset(out_record, 0, sizeof(*out_record));
    dom_checkpoint_clear_worlds(out_record);

    lifecycle_hash = dom_shard_lifecycle_log_hash(&runtime->lifecycle_log);

    out_record->manifest.schema_version = DOM_CHECKPOINT_SCHEMA_VERSION;
    out_record->manifest.tick = runtime->now_tick;
    out_record->manifest.trigger_reason = trigger_reason;
    out_record->manifest.worlddef_hash = runtime->config.worlddef_hash;
    out_record->manifest.capability_lock_hash = runtime->config.capability_lock_hash;
    out_record->manifest.runtime_hash = dom_server_runtime_hash(runtime);
    out_record->manifest.lifecycle_hash = lifecycle_hash;
    out_record->manifest.message_sequence = runtime->message_sequence;
    out_record->manifest.message_applied = runtime->message_applied;
    out_record->manifest.macro_events_executed = runtime->macro_events_executed;
    out_record->manifest.event_count = runtime->event_count;
    out_record->manifest.event_overflow = runtime->event_overflow;
    out_record->manifest.shard_count = runtime->shard_count;
    out_record->manifest.checkpoint_id = dom_checkpoint_make_id(runtime, trigger_reason);

    lifecycle_cap = (u32)(sizeof(out_record->lifecycle_entries) /
                          sizeof(out_record->lifecycle_entries[0]));
    out_record->lifecycle_count = runtime->lifecycle_log.count;
    out_record->lifecycle_overflow = runtime->lifecycle_log.overflow;
    if (out_record->lifecycle_count > lifecycle_cap) {
        return -20;
    }
    if (out_record->lifecycle_count > 0u && runtime->lifecycle_log.entries) {
        memcpy(out_record->lifecycle_entries,
               runtime->lifecycle_log.entries,
               sizeof(out_record->lifecycle_entries[0]) *
                   (size_t)out_record->lifecycle_count);
    }

    out_record->intent_count = runtime->intent_count;
    out_record->intent_overflow = runtime->intent_overflow;
    if (out_record->intent_count > DOM_SERVER_MAX_INTENTS) {
        return -21;
    }
    if (out_record->intent_count > 0u) {
        memcpy(out_record->intents,
               runtime->intents,
               sizeof(out_record->intents[0]) * (size_t)out_record->intent_count);
    }

    out_record->deferred_count = runtime->deferred_count;
    out_record->deferred_overflow = runtime->deferred_overflow;
    if (out_record->deferred_count > DOM_SERVER_MAX_DEFERRED) {
        return -22;
    }
    for (i = 0u; i < out_record->deferred_count; ++i) {
        out_record->deferred[i].intent = runtime->deferred[i].intent;
        out_record->deferred[i].refusal_code = runtime->deferred[i].refusal_code;
    }

    out_record->event_count = runtime->event_count;
    out_record->event_overflow = runtime->event_overflow;
    if (out_record->event_count > DOM_SERVER_MAX_EVENTS) {
        return -2;
    }
    if (out_record->event_count > 0u) {
        memcpy(out_record->events,
               runtime->events,
               sizeof(out_record->events[0]) * (size_t)out_record->event_count);
    }

    out_record->owner_count = runtime->owner_count;
    if (out_record->owner_count > DOM_SERVER_MAX_DOMAIN_OWNERS) {
        return -3;
    }
    if (out_record->owner_count > 0u) {
        memcpy(out_record->owners,
               runtime->owners,
               sizeof(out_record->owners[0]) * (size_t)out_record->owner_count);
    }

    out_record->message_count = runtime->message_log.message_count;
    if (out_record->message_count > DOM_SERVER_MAX_MESSAGES) {
        return -4;
    }
    if (out_record->message_count > 0u) {
        memcpy(out_record->messages,
               runtime->message_storage,
               sizeof(out_record->messages[0]) * (size_t)out_record->message_count);
    }

    out_record->idempotency_count = runtime->message_log.idempotency_count;
    if (out_record->idempotency_count > DOM_SERVER_MAX_IDEMPOTENCY) {
        return -5;
    }
    if (out_record->idempotency_count > 0u) {
        memcpy(out_record->idempotency,
               runtime->message_idempotency,
               sizeof(out_record->idempotency[0]) * (size_t)out_record->idempotency_count);
    }

    for (i = 0u; i < runtime->shard_count && i < DOM_SERVER_MAX_SHARDS; ++i) {
        const dom_server_shard* shard = &runtime->shards[i];
        dom_shard_checkpoint* chk = &out_record->shards[i];
        dom_scale_budget_snapshot_current(&shard->scale_ctx, &chk->budget_snapshot);
        chk->shard_id = shard->shard_id;
        chk->tick = runtime->now_tick;
        chk->lifecycle_state = shard->lifecycle_state;
        chk->version_id = shard->version_id;
        chk->capability_mask = shard->capability_mask;
        chk->baseline_hash = shard->baseline_hash;
        chk->world_checksum = shard->world ? d_world_checksum(shard->world) : 0u;
        chk->budget_state = shard->scale_ctx.budget_state;
        chk->budget_state.budget_tick = runtime->now_tick;

        if (dom_checkpoint_copy_domains(chk, shard, runtime->now_tick) != 0) {
            return -6;
        }

        chk->scale_event_count = shard->scale_event_log.count;
        chk->scale_event_overflow = shard->scale_event_log.overflow;
        if (chk->scale_event_count >
            (u32)(sizeof(chk->scale_events) / sizeof(chk->scale_events[0]))) {
            return -7;
        }
        if (chk->scale_event_count > 0u) {
            memcpy(chk->scale_events,
                   shard->scale_events,
                   sizeof(chk->scale_events[0]) * (size_t)chk->scale_event_count);
        }
        chk->scale_event_hash = dom_checkpoint_scale_event_hash(&shard->scale_event_log);
        chk->shard_hash = dom_checkpoint_shard_hash(chk,
                                                    runtime->now_tick,
                                                    shard->scale_ctx.worker_count);

        if (!shard->world) {
            return -8;
        }
        out_record->world_clones[i] = d_world_clone(shard->world);
        if (!out_record->world_clones[i]) {
            return -9;
        }
    }

    return 0;
}

static void dom_checkpoint_client_reset(dom_server_client* client, dom_act_time_t tick)
{
    if (!client) {
        return;
    }
    client->budget_state.tick = tick;
    client->budget_state.intents_limit = client->policy.intents_per_tick;
    client->budget_state.bytes_limit = client->policy.bytes_per_tick;
    client->budget_state.intents_used = 0u;
    client->budget_state.bytes_used = 0u;
    client->idempotency_count = 0u;
}

int dom_checkpoint_recover(dom_server_runtime* runtime,
                           const dom_checkpoint_record* record,
                           u32* out_refusal_code)
{
    u32 i;
    u32 lifecycle_cap;
    u64 lifecycle_hash;
    dom_shard_lifecycle_log log_view;
    d_world* new_worlds[DOM_SERVER_MAX_SHARDS];
    dom_server_shard shadow;
    int pre_rc;
    if (out_refusal_code) {
        *out_refusal_code = DOM_SERVER_REFUSE_NONE;
    }
    if (!runtime || !record) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_INVALID_INTENT;
        }
        return -1;
    }
    for (i = 0u; i < DOM_SERVER_MAX_SHARDS; ++i) {
        new_worlds[i] = (d_world*)0;
    }

    if (record->manifest.schema_version != DOM_CHECKPOINT_SCHEMA_VERSION) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_CAPABILITY_MISSING;
        }
        return -2;
    }

    lifecycle_cap = (u32)(sizeof(record->lifecycle_entries) / sizeof(record->lifecycle_entries[0]));
    if (record->lifecycle_count > lifecycle_cap) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_SCHEMA_INCOMPATIBLE;
        }
        return -3;
    }
    memset(&log_view, 0, sizeof(log_view));
    log_view.entries = (dom_shard_lifecycle_entry*)record->lifecycle_entries;
    log_view.count = record->lifecycle_count;
    log_view.capacity = lifecycle_cap;
    log_view.overflow = record->lifecycle_overflow;
    lifecycle_hash = dom_shard_lifecycle_log_hash(&log_view);
    if (record->manifest.lifecycle_hash != lifecycle_hash) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
        }
        return -4;
    }

    if (record->manifest.worlddef_hash != runtime->config.worlddef_hash ||
        record->manifest.capability_lock_hash != runtime->config.capability_lock_hash) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_CAPABILITY_MISSING;
        }
        return -4;
    }

    if (record->manifest.shard_count != runtime->shard_count ||
        record->manifest.shard_count > DOM_SERVER_MAX_SHARDS) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_INVALID_INTENT;
        }
        return -5;
    }

    if (record->intent_count > DOM_SERVER_MAX_INTENTS ||
        record->deferred_count > DOM_SERVER_MAX_DEFERRED ||
        record->event_count > DOM_SERVER_MAX_EVENTS ||
        record->owner_count > DOM_SERVER_MAX_DOMAIN_OWNERS ||
        record->message_count > DOM_SERVER_MAX_MESSAGES ||
        record->idempotency_count > DOM_SERVER_MAX_IDEMPOTENCY) {
        if (out_refusal_code) {
            *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
        }
        return -6;
    }

    for (i = 0u; i < runtime->shard_count; ++i) {
        const dom_shard_checkpoint* chk = &record->shards[i];
        const dom_server_shard* shard = &runtime->shards[i];
        const u32 scale_cap = (u32)(sizeof(shard->scale_events) / sizeof(shard->scale_events[0]));
        if (!record->world_clones[i]) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
            }
            dom_checkpoint_destroy_worlds(new_worlds, DOM_SERVER_MAX_SHARDS);
            return -7;
        }
        if (chk->shard_id != shard->shard_id) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_SERVER_REFUSE_INVALID_INTENT;
            }
            dom_checkpoint_destroy_worlds(new_worlds, DOM_SERVER_MAX_SHARDS);
            return -8;
        }
        if (chk->scale_event_count > scale_cap) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
            }
            dom_checkpoint_destroy_worlds(new_worlds, DOM_SERVER_MAX_SHARDS);
            return -13;
        }
        shadow = *shard;
        pre_rc = dom_checkpoint_restore_domains(&shadow, chk, record->manifest.tick);
        if (pre_rc != 0) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
            }
            dom_checkpoint_destroy_worlds(new_worlds, DOM_SERVER_MAX_SHARDS);
            return -14;
        }
        new_worlds[i] = d_world_clone(record->world_clones[i]);
        if (!new_worlds[i]) {
            if (out_refusal_code) {
                *out_refusal_code = DOM_SERVER_REFUSE_INTEGRITY_VIOLATION;
            }
            dom_checkpoint_destroy_worlds(new_worlds, DOM_SERVER_MAX_SHARDS);
            return -15;
        }
    }

    for (i = 0u; i < runtime->shard_count; ++i) {
        const dom_shard_checkpoint* chk = &record->shards[i];
        dom_server_shard* shard = &runtime->shards[i];
        d_world_destroy_instance(shard->world);
        shard->world = new_worlds[i];
        shard->scale_ctx.world = new_worlds[i];
        shard->scale_ctx.now_tick = record->manifest.tick;
        shard->scale_ctx.budget_state = chk->budget_state;
        shard->scale_ctx.budget_state.budget_tick = record->manifest.tick;
        shard->lifecycle_state = chk->lifecycle_state;
        shard->version_id = chk->version_id;
        shard->capability_mask = chk->capability_mask;
        shard->baseline_hash = chk->baseline_hash;

        shard->scale_event_log.count = chk->scale_event_count;
        shard->scale_event_log.overflow = chk->scale_event_overflow;
        if (shard->scale_event_log.count > 0u) {
            memcpy(shard->scale_events,
                   chk->scale_events,
                   sizeof(shard->scale_events[0]) * (size_t)shard->scale_event_log.count);
        }

        (void)dom_checkpoint_restore_domains(shard, chk, record->manifest.tick);
    }

    runtime->now_tick = record->manifest.tick;
    runtime->message_sequence = record->manifest.message_sequence;
    runtime->message_applied = record->manifest.message_applied;
    runtime->macro_events_executed = record->manifest.macro_events_executed;

    runtime->intent_count = record->intent_count;
    runtime->intent_overflow = record->intent_overflow;
    if (runtime->intent_count > 0u) {
        memcpy(runtime->intents,
               record->intents,
               sizeof(runtime->intents[0]) * (size_t)runtime->intent_count);
    }

    runtime->deferred_count = record->deferred_count;
    runtime->deferred_overflow = record->deferred_overflow;
    for (i = 0u; i < runtime->deferred_count; ++i) {
        runtime->deferred[i].intent = record->deferred[i].intent;
        runtime->deferred[i].refusal_code = record->deferred[i].refusal_code;
    }

    runtime->event_count = record->event_count;
    runtime->event_overflow = record->event_overflow;
    if (runtime->event_count > 0u) {
        memcpy(runtime->events,
               record->events,
               sizeof(runtime->events[0]) * (size_t)runtime->event_count);
    }

    runtime->owner_count = record->owner_count;
    if (runtime->owner_count > 0u) {
        memcpy(runtime->owners,
               record->owners,
               sizeof(runtime->owners[0]) * (size_t)runtime->owner_count);
    }

    dom_cross_shard_log_init(&runtime->message_log,
                             runtime->message_storage,
                             DOM_SERVER_MAX_MESSAGES,
                             runtime->message_idempotency,
                             DOM_SERVER_MAX_IDEMPOTENCY);
    runtime->message_log.message_count = record->message_count;
    runtime->message_log.idempotency_count = record->idempotency_count;
    if (record->message_count > 0u) {
        memcpy(runtime->message_storage,
               record->messages,
               sizeof(runtime->message_storage[0]) * (size_t)record->message_count);
    }
    if (record->idempotency_count > 0u) {
        memcpy(runtime->message_idempotency,
               record->idempotency,
               sizeof(runtime->message_idempotency[0]) * (size_t)record->idempotency_count);
    }

    lifecycle_cap = (u32)(sizeof(runtime->lifecycle_entries) / sizeof(runtime->lifecycle_entries[0]));
    dom_shard_lifecycle_log_init(&runtime->lifecycle_log,
                                 runtime->lifecycle_entries,
                                 lifecycle_cap);
    runtime->lifecycle_log.count = record->lifecycle_count;
    runtime->lifecycle_log.overflow = record->lifecycle_overflow;
    if (record->lifecycle_count > 0u) {
        memcpy(runtime->lifecycle_entries,
               record->lifecycle_entries,
               sizeof(runtime->lifecycle_entries[0]) * (size_t)record->lifecycle_count);
    }

    for (i = 0u; i < runtime->client_count; ++i) {
        dom_checkpoint_client_reset(&runtime->clients[i], runtime->now_tick);
    }

    return 0;
}

void dom_checkpoint_record_dispose(dom_checkpoint_record* record)
{
    u32 i;
    if (!record) {
        return;
    }
    for (i = 0u; i < DOM_SERVER_MAX_SHARDS; ++i) {
        if (record->world_clones[i]) {
            d_world_destroy_instance(record->world_clones[i]);
            record->world_clones[i] = (d_world*)0;
        }
    }
}
