/*
FILE: server/persistence/integrity_checkpoints.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic shard integrity checkpoints.
*/
#include "integrity_checkpoints.h"

#include "shard/shard_hashing.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_integrity_hash_mix(u64 hash, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((value >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

void dom_integrity_checkpoint_log_init(dom_integrity_checkpoint_log* log,
                                       dom_integrity_checkpoint* storage,
                                       u32 capacity)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_integrity_checkpoint) * (size_t)capacity);
    }
}

int dom_integrity_checkpoint_log_record(dom_integrity_checkpoint_log* log,
                                        const dom_integrity_checkpoint* checkpoint)
{
    if (!log || !checkpoint || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    log->entries[log->count++] = *checkpoint;
    return 0;
}

u64 dom_integrity_checkpoint_hash(const dom_integrity_checkpoint* checkpoint)
{
    u32 i;
    u64 hash = 1469598103934665603ULL;
    if (!checkpoint) {
        return hash;
    }
    hash = dom_integrity_hash_mix(hash, checkpoint->shard_id);
    hash = dom_integrity_hash_mix(hash, (u64)checkpoint->act_tick);
    hash = dom_integrity_hash_mix(hash, checkpoint->partition_count);
    for (i = 0u; i < checkpoint->partition_count; ++i) {
        hash = dom_integrity_hash_mix(hash, checkpoint->partition_ids[i]);
        hash = dom_integrity_hash_mix(hash, checkpoint->hash_values[i]);
    }
    hash = dom_integrity_hash_mix(hash, checkpoint->schema_version_count);
    for (i = 0u; i < checkpoint->schema_version_count; ++i) {
        hash = dom_integrity_hash_mix(hash, checkpoint->schema_versions[i]);
    }
    hash = dom_integrity_hash_mix(hash, checkpoint->mod_graph_hash);
    hash = dom_integrity_hash_mix(hash, checkpoint->engine_build_id);
    hash = dom_integrity_hash_mix(hash, checkpoint->game_build_id);
    return hash;
}

u64 dom_integrity_checkpoint_log_hash(const dom_integrity_checkpoint_log* log)
{
    u32 i;
    u64 hash = 1469598103934665603ULL;
    if (!log || !log->entries) {
        return hash;
    }
    hash = dom_integrity_hash_mix(hash, log->count);
    for (i = 0u; i < log->count; ++i) {
        hash = dom_integrity_hash_mix(hash, dom_integrity_checkpoint_hash(&log->entries[i]));
    }
    return hash;
}

int dom_integrity_checkpoint_build(dom_integrity_checkpoint* checkpoint,
                                   const dom_shard_log* shard_log,
                                   dom_shard_id shard_id,
                                   dom_act_time_t act_tick,
                                   const u32* partitions,
                                   u32 partition_count,
                                   const u64* schema_versions,
                                   u32 schema_version_count,
                                   u64 mod_graph_hash,
                                   u64 engine_build_id,
                                   u64 game_build_id)
{
    u32 i;
    if (!checkpoint || !partitions) {
        return -1;
    }
    if (partition_count > DOM_INTEGRITY_MAX_PARTITIONS) {
        return -2;
    }
    if (schema_version_count > DOM_INTEGRITY_MAX_SCHEMA_VERSIONS) {
        return -3;
    }

    checkpoint->shard_id = shard_id;
    checkpoint->act_tick = act_tick;
    checkpoint->partition_count = partition_count;
    for (i = 0u; i < partition_count; ++i) {
        checkpoint->partition_ids[i] = partitions[i];
        checkpoint->hash_values[i] = 0u;
    }
    if (dom_shard_compute_partition_hashes(shard_log,
                                           partitions,
                                           partition_count,
                                           checkpoint->hash_values) != 0) {
        return -4;
    }

    checkpoint->schema_version_count = schema_version_count;
    for (i = 0u; i < schema_version_count; ++i) {
        checkpoint->schema_versions[i] = schema_versions ? schema_versions[i] : 0u;
    }
    for (; i < DOM_INTEGRITY_MAX_SCHEMA_VERSIONS; ++i) {
        checkpoint->schema_versions[i] = 0u;
    }

    checkpoint->mod_graph_hash = mod_graph_hash;
    checkpoint->engine_build_id = engine_build_id;
    checkpoint->game_build_id = game_build_id;
    return 0;
}

dom_act_time_t dom_integrity_schedule_next(dom_integrity_schedule* schedule,
                                           dom_act_time_t now)
{
    if (!schedule || schedule->interval == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (schedule->next_due == 0u || schedule->next_due <= now) {
        if (now > (DOM_TIME_ACT_MAX - schedule->interval)) {
            schedule->next_due = DOM_TIME_ACT_MAX;
        } else {
            schedule->next_due = now + schedule->interval;
        }
    }
    return schedule->next_due;
}

int dom_integrity_witness_verify(const dom_integrity_checkpoint* expected,
                                 const dom_shard_log* shard_log,
                                 u32* out_mismatch_partition)
{
    u32 i;
    u64 recomputed[DOM_INTEGRITY_MAX_PARTITIONS];
    if (!expected || !shard_log) {
        return -1;
    }
    if (expected->partition_count > DOM_INTEGRITY_MAX_PARTITIONS) {
        return -2;
    }
    if (dom_shard_compute_partition_hashes(shard_log,
                                           expected->partition_ids,
                                           expected->partition_count,
                                           recomputed) != 0) {
        return -3;
    }
    for (i = 0u; i < expected->partition_count; ++i) {
        if (recomputed[i] != expected->hash_values[i]) {
            if (out_mismatch_partition) {
                *out_mismatch_partition = expected->partition_ids[i];
            }
            return 1;
        }
    }
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
