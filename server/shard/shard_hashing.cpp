/*
FILE: server/shard/shard_hashing.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard hash computation helpers.
*/
#include "shard_hashing.h"

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_shard_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

u64 dom_shard_hash_partition(const dom_shard_log* log, u32 partition_id)
{
    u64 hash = 1469598103934665603ULL;
    if (!log) {
        return hash;
    }
    hash = dom_shard_hash_mix(hash, partition_id);
    hash = dom_shard_hash_mix(hash, log->event_count);
    hash = dom_shard_hash_mix(hash, log->message_count);
    if (log->events && log->event_count > 0u) {
        u32 i;
        for (i = 0u; i < log->event_count; ++i) {
            const dom_shard_event_entry* entry = &log->events[i];
            hash = dom_shard_hash_mix(hash, entry->event_id);
            hash = dom_shard_hash_mix(hash, entry->task_id);
            hash = dom_shard_hash_mix(hash, (u64)entry->tick);
        }
    }
    if (log->messages && log->message_count > 0u) {
        u32 i;
        for (i = 0u; i < log->message_count; ++i) {
            const dom_shard_message* msg = &log->messages[i];
            hash = dom_shard_hash_mix(hash, msg->message_id);
            hash = dom_shard_hash_mix(hash, msg->task_id);
            hash = dom_shard_hash_mix(hash, msg->arrival_tick);
            hash = dom_shard_hash_mix(hash, msg->payload_size);
        }
    }
    return hash;
}

int dom_shard_compute_partition_hashes(const dom_shard_log* log,
                                       const u32* partitions,
                                       u32 partition_count,
                                       u64* out_hashes)
{
    u32 i;
    if (!out_hashes || !partitions) {
        return -1;
    }
    for (i = 0u; i < partition_count; ++i) {
        out_hashes[i] = dom_shard_hash_partition(log, partitions[i]);
    }
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
