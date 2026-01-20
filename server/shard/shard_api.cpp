/*
FILE: server/shard/shard_api.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard placement and message ordering helpers.
*/
#include "shard_api.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_shard_fnv1a64_u64(u64 h, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 dom_shard_hash_task(const dom_shard_task_key* key)
{
    u64 h = 1469598103934665603ULL;
    if (!key) {
        return h;
    }
    h = dom_shard_fnv1a64_u64(h, key->task_id);
    h = dom_shard_fnv1a64_u64(h, key->system_id);
    h = dom_shard_fnv1a64_u64(h, key->access_set_id);
    h = dom_shard_fnv1a64_u64(h, (u64)key->category);
    h = dom_shard_fnv1a64_u64(h, (u64)key->determinism_class);
    return h;
}

void dom_shard_registry_init(dom_shard_registry* registry,
                             dom_shard* storage,
                             u32 capacity)
{
    if (!registry) {
        return;
    }
    registry->shards = storage;
    registry->count = 0u;
    registry->capacity = capacity;
}

int dom_shard_registry_add(dom_shard_registry* registry,
                           const dom_shard* shard)
{
    u32 i;
    u32 insert_at = 0u;
    if (!registry || !shard) {
        return -1;
    }
    if (!registry->shards || registry->capacity == 0u) {
        return -2;
    }
    if (registry->count >= registry->capacity) {
        return -3;
    }
    while (insert_at < registry->count &&
           registry->shards[insert_at].shard_id < shard->shard_id) {
        insert_at += 1u;
    }
    for (i = registry->count; i > insert_at; --i) {
        registry->shards[i] = registry->shards[i - 1u];
    }
    registry->shards[insert_at] = *shard;
    registry->count += 1u;
    return 0;
}

dom_shard_id dom_shard_find_owner(const dom_shard_registry* registry,
                                  u64 owner_id)
{
    u32 i;
    if (!registry || !registry->shards || registry->count == 0u) {
        return 0u;
    }
    for (i = 0u; i < registry->count; ++i) {
        const dom_shard* shard = &registry->shards[i];
        const dom_shard_ownership_scope* scope = &shard->scope;
        if (scope->kind == DOM_SHARD_SCOPE_SYSTEM_DOMAIN) {
            if (owner_id == (u64)scope->domain_tag) {
                return shard->shard_id;
            }
        } else if (owner_id >= scope->start_id && owner_id <= scope->end_id) {
            return shard->shard_id;
        }
    }
    return 0u;
}

dom_shard_id dom_shard_place_task(const dom_shard_registry* registry,
                                  const dom_shard_task_key* key,
                                  dom_shard_id fallback_shard)
{
    u64 hash;
    u32 index;
    if (!registry || !registry->shards || registry->count == 0u || !key) {
        return fallback_shard;
    }
    if (key->primary_owner_id != 0u) {
        dom_shard_id owner = dom_shard_find_owner(registry, key->primary_owner_id);
        if (owner != 0u) {
            return owner;
        }
    }
    hash = dom_shard_hash_task(key);
    index = (u32)(hash % registry->count);
    return registry->shards[index].shard_id;
}

int dom_shard_validate_access(const dom_shard_registry* registry,
                              dom_shard_id local_shard,
                              u64 owner_id,
                              u32 access_kind)
{
    dom_shard_id owner;
    (void)access_kind;
    if (!registry) {
        return -1;
    }
    owner = dom_shard_find_owner(registry, owner_id);
    if (owner == 0u) {
        return -2;
    }
    if (owner != local_shard) {
        return -3;
    }
    return 0;
}

void dom_shard_message_queue_init(dom_shard_message_queue* queue,
                                  dom_shard_message* storage,
                                  u32 capacity)
{
    if (!queue) {
        return;
    }
    queue->messages = storage;
    queue->count = 0u;
    queue->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_shard_message) * (size_t)capacity);
    }
}

static int dom_shard_message_before(const dom_shard_message* a,
                                    const dom_shard_message* b)
{
    if (a->arrival_tick < b->arrival_tick) {
        return 1;
    }
    if (a->arrival_tick > b->arrival_tick) {
        return 0;
    }
    return (a->message_id < b->message_id) ? 1 : 0;
}

void dom_shard_message_queue_sort(dom_shard_message_queue* queue)
{
    u32 i;
    if (!queue || !queue->messages || queue->count < 2u) {
        return;
    }
    for (i = 1u; i < queue->count; ++i) {
        dom_shard_message key = queue->messages[i];
        u32 j = i;
        while (j > 0u && dom_shard_message_before(&key, &queue->messages[j - 1u])) {
            queue->messages[j] = queue->messages[j - 1u];
            j -= 1u;
        }
        queue->messages[j] = key;
    }
}

int dom_shard_message_queue_push(dom_shard_message_queue* queue,
                                 const dom_shard_message* message)
{
    if (!queue || !message || !queue->messages) {
        return -1;
    }
    if (queue->count >= queue->capacity) {
        return -2;
    }
    queue->messages[queue->count++] = *message;
    dom_shard_message_queue_sort(queue);
    return 0;
}

int dom_shard_message_queue_pop_ready(dom_shard_message_queue* queue,
                                      dom_act_time_t now,
                                      dom_shard_message* out_message)
{
    u32 i;
    if (!queue || !queue->messages || queue->count == 0u) {
        return -1;
    }
    if (queue->messages[0].arrival_tick > now) {
        return 1;
    }
    if (out_message) {
        *out_message = queue->messages[0];
    }
    for (i = 1u; i < queue->count; ++i) {
        queue->messages[i - 1u] = queue->messages[i];
    }
    queue->count -= 1u;
    return 0;
}

void dom_shard_log_init(dom_shard_log* log,
                        dom_shard_event_entry* event_storage,
                        u32 event_capacity,
                        dom_shard_message* message_storage,
                        u32 message_capacity)
{
    if (!log) {
        return;
    }
    log->events = event_storage;
    log->event_count = 0u;
    log->event_capacity = event_capacity;
    log->messages = message_storage;
    log->message_count = 0u;
    log->message_capacity = message_capacity;
    if (event_storage && event_capacity > 0u) {
        memset(event_storage, 0, sizeof(dom_shard_event_entry) * (size_t)event_capacity);
    }
    if (message_storage && message_capacity > 0u) {
        memset(message_storage, 0, sizeof(dom_shard_message) * (size_t)message_capacity);
    }
}

int dom_shard_log_record_event(dom_shard_log* log,
                               const dom_shard_event_entry* entry)
{
    if (!log || !entry || !log->events) {
        return -1;
    }
    if (log->event_count >= log->event_capacity) {
        return -2;
    }
    log->events[log->event_count++] = *entry;
    return 0;
}

int dom_shard_log_record_message(dom_shard_log* log,
                                 const dom_shard_message* message)
{
    if (!log || !message || !log->messages) {
        return -1;
    }
    if (log->message_count >= log->message_capacity) {
        return -2;
    }
    log->messages[log->message_count++] = *message;
    return 0;
}

u64 dom_shard_log_hash(const dom_shard_log* log)
{
    u32 i;
    u64 h = 1469598103934665603ULL;
    if (!log) {
        return h;
    }
    h = dom_shard_fnv1a64_u64(h, log->event_count);
    for (i = 0u; i < log->event_count; ++i) {
        const dom_shard_event_entry* e = &log->events[i];
        h = dom_shard_fnv1a64_u64(h, e->event_id);
        h = dom_shard_fnv1a64_u64(h, e->task_id);
        h = dom_shard_fnv1a64_u64(h, (u64)e->tick);
    }
    h = dom_shard_fnv1a64_u64(h, log->message_count);
    for (i = 0u; i < log->message_count; ++i) {
        const dom_shard_message* m = &log->messages[i];
        u32 j;
        h = dom_shard_fnv1a64_u64(h, m->source_shard);
        h = dom_shard_fnv1a64_u64(h, m->target_shard);
        h = dom_shard_fnv1a64_u64(h, m->message_id);
        h = dom_shard_fnv1a64_u64(h, m->task_id);
        h = dom_shard_fnv1a64_u64(h, (u64)m->arrival_tick);
        h = dom_shard_fnv1a64_u64(h, m->payload_size);
        if (m->payload && m->payload_size > 0u) {
            for (j = 0u; j < m->payload_size; ++j) {
                h ^= (u64)m->payload[j];
                h *= 1099511628211ULL;
            }
        }
    }
    return h;
}

int dom_shard_replay_apply(const dom_shard_log* log,
                           dom_shard_replay_state* out_state)
{
    if (!log || !out_state) {
        return -1;
    }
    out_state->hash = dom_shard_log_hash(log);
    out_state->event_count = log->event_count;
    out_state->message_count = log->message_count;
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
