/*
FILE: server/shard/dom_cross_shard_log.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic cross-shard message log helpers.
DETERMINISM: Ordering and idempotency checks are stable across platforms.
*/
#include "dom_cross_shard_log.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_cross_shard_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_cross_shard_idempotency_size(const dom_cross_shard_log* log)
{
    if (!log) {
        return 0u;
    }
    if (log->idempotency_capacity == 0u) {
        return 0u;
    }
    return (log->idempotency_count < log->idempotency_capacity)
        ? log->idempotency_count
        : log->idempotency_capacity;
}

static int dom_cross_shard_compare(const dom_cross_shard_message* a,
                                   const dom_cross_shard_message* b)
{
    if (a->delivery_tick != b->delivery_tick) {
        return (a->delivery_tick < b->delivery_tick) ? -1 : 1;
    }
    if (a->causal_key != b->causal_key) {
        return (a->causal_key < b->causal_key) ? -1 : 1;
    }
    if (a->origin_shard_id != b->origin_shard_id) {
        return (a->origin_shard_id < b->origin_shard_id) ? -1 : 1;
    }
    if (a->dest_shard_id != b->dest_shard_id) {
        return (a->dest_shard_id < b->dest_shard_id) ? -1 : 1;
    }
    if (a->domain_id != b->domain_id) {
        return (a->domain_id < b->domain_id) ? -1 : 1;
    }
    if (a->order_key != b->order_key) {
        return (a->order_key < b->order_key) ? -1 : 1;
    }
    if (a->message_id != b->message_id) {
        return (a->message_id < b->message_id) ? -1 : 1;
    }
    if (a->sequence != b->sequence) {
        return (a->sequence < b->sequence) ? -1 : 1;
    }
    if (a->payload_hash != b->payload_hash) {
        return (a->payload_hash < b->payload_hash) ? -1 : 1;
    }
    return 0;
}

static void dom_cross_shard_sort(dom_cross_shard_log* log)
{
    u32 i;
    if (!log || !log->messages || log->message_count < 2u) {
        return;
    }
    /* Insertion sort keeps ordering stable for identical keys. */
    for (i = 1u; i < log->message_count; ++i) {
        dom_cross_shard_message key = log->messages[i];
        u32 j = i;
        while (j > 0u && dom_cross_shard_compare(&key, &log->messages[j - 1u]) < 0) {
            log->messages[j] = log->messages[j - 1u];
            --j;
        }
        log->messages[j] = key;
    }
}

static int dom_cross_shard_idempotency_seen(const dom_cross_shard_log* log,
                                            dom_shard_id dest_shard_id,
                                            u64 idempotency_key)
{
    u32 i;
    u32 size = dom_cross_shard_idempotency_size(log);
    if (!log || !log->idempotency_entries || idempotency_key == 0u) {
        return 0;
    }
    for (i = 0u; i < size; ++i) {
        const dom_cross_shard_idempotency_entry* entry = &log->idempotency_entries[i];
        if (entry->dest_shard_id == dest_shard_id && entry->idempotency_key == idempotency_key) {
            return 1;
        }
    }
    return 0;
}

static void dom_cross_shard_idempotency_record(dom_cross_shard_log* log,
                                               dom_shard_id dest_shard_id,
                                               u64 idempotency_key)
{
    dom_cross_shard_idempotency_entry* entry;
    u32 slot;
    if (!log || !log->idempotency_entries || log->idempotency_capacity == 0u || idempotency_key == 0u) {
        return;
    }
    slot = (log->idempotency_count < log->idempotency_capacity)
        ? log->idempotency_count
        : (log->idempotency_count % log->idempotency_capacity);
    entry = &log->idempotency_entries[slot];
    entry->dest_shard_id = dest_shard_id;
    entry->idempotency_key = idempotency_key;
    log->idempotency_count += 1u;
}

void dom_cross_shard_log_init(dom_cross_shard_log* log,
                              dom_cross_shard_message* message_storage,
                              u32 message_capacity,
                              dom_cross_shard_idempotency_entry* idempotency_storage,
                              u32 idempotency_capacity)
{
    if (!log) {
        return;
    }
    log->messages = message_storage;
    log->message_capacity = message_capacity;
    log->message_count = 0u;
    log->message_overflow = 0u;
    log->idempotency_entries = idempotency_storage;
    log->idempotency_capacity = idempotency_capacity;
    log->idempotency_count = 0u;
}

void dom_cross_shard_log_clear(dom_cross_shard_log* log)
{
    if (!log) {
        return;
    }
    log->message_count = 0u;
    log->message_overflow = 0u;
    log->idempotency_count = 0u;
}

int dom_cross_shard_log_append(dom_cross_shard_log* log,
                               const dom_cross_shard_message* message)
{
    dom_cross_shard_message local;
    if (!log || !message) {
        return -1;
    }
    if (!log->messages || log->message_capacity == 0u) {
        log->message_overflow += 1u;
        return -2;
    }
    if (log->message_count >= log->message_capacity) {
        log->message_overflow += 1u;
        return -3;
    }
    local = *message;
    if (local.order_key == 0u) {
        local.order_key = local.message_id;
    }
    log->messages[log->message_count] = local;
    log->message_count += 1u;
    dom_cross_shard_sort(log);
    return 0;
}

int dom_cross_shard_log_pop_next_ready(dom_cross_shard_log* log,
                                       dom_act_time_t up_to_tick,
                                       dom_cross_shard_message* out_message,
                                       u32* out_skipped_idempotent)
{
    u32 i;
    u32 skipped = 0u;
    if (!log || !out_message) {
        return 0;
    }
    dom_cross_shard_sort(log);
    for (i = 0u; i < log->message_count; ++i) {
        dom_cross_shard_message msg = log->messages[i];
        if (msg.delivery_tick > up_to_tick) {
            break;
        }
        if (msg.idempotency_key != 0u &&
            dom_cross_shard_idempotency_seen(log, msg.dest_shard_id, msg.idempotency_key)) {
            if (i + 1u < log->message_count) {
                memmove(&log->messages[i],
                        &log->messages[i + 1u],
                        (size_t)(log->message_count - (i + 1u)) * sizeof(log->messages[0]));
            }
            log->message_count -= 1u;
            skipped += 1u;
            i -= 1u;
            continue;
        }
        if (msg.idempotency_key != 0u) {
            dom_cross_shard_idempotency_record(log, msg.dest_shard_id, msg.idempotency_key);
        }
        if (i + 1u < log->message_count) {
            memmove(&log->messages[i],
                    &log->messages[i + 1u],
                    (size_t)(log->message_count - (i + 1u)) * sizeof(log->messages[0]));
        }
        log->message_count -= 1u;
        *out_message = msg;
        if (out_skipped_idempotent) {
            *out_skipped_idempotent = skipped;
        }
        return 1;
    }
    if (out_skipped_idempotent) {
        *out_skipped_idempotent = skipped;
    }
    return 0;
}

u64 dom_cross_shard_log_hash(const dom_cross_shard_log* log)
{
    u64 hash = 1469598103934665603ULL;
    u32 i;
    u32 id_size = dom_cross_shard_idempotency_size(log);
    if (!log) {
        return hash;
    }
    hash = dom_cross_shard_hash_mix(hash, log->message_count);
    hash = dom_cross_shard_hash_mix(hash, log->message_capacity);
    hash = dom_cross_shard_hash_mix(hash, log->message_overflow);
    hash = dom_cross_shard_hash_mix(hash, log->idempotency_count);
    hash = dom_cross_shard_hash_mix(hash, log->idempotency_capacity);
    if (log->messages) {
        for (i = 0u; i < log->message_count; ++i) {
            const dom_cross_shard_message* msg = &log->messages[i];
            hash = dom_cross_shard_hash_mix(hash, msg->message_id);
            hash = dom_cross_shard_hash_mix(hash, msg->idempotency_key);
            hash = dom_cross_shard_hash_mix(hash, msg->origin_shard_id);
            hash = dom_cross_shard_hash_mix(hash, msg->dest_shard_id);
            hash = dom_cross_shard_hash_mix(hash, msg->domain_id);
            hash = dom_cross_shard_hash_mix(hash, (u64)msg->origin_tick);
            hash = dom_cross_shard_hash_mix(hash, (u64)msg->delivery_tick);
            hash = dom_cross_shard_hash_mix(hash, msg->causal_key);
            hash = dom_cross_shard_hash_mix(hash, msg->order_key);
            hash = dom_cross_shard_hash_mix(hash, msg->message_kind);
            hash = dom_cross_shard_hash_mix(hash, msg->sequence);
            hash = dom_cross_shard_hash_mix(hash, msg->payload_hash);
        }
    }
    if (log->idempotency_entries) {
        for (i = 0u; i < id_size; ++i) {
            const dom_cross_shard_idempotency_entry* entry = &log->idempotency_entries[i];
            hash = dom_cross_shard_hash_mix(hash, entry->dest_shard_id);
            hash = dom_cross_shard_hash_mix(hash, entry->idempotency_key);
        }
    }
    return hash;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

