/*
FILE: server/persistence/integrity_checkpoints.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic shard integrity checkpoints.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers; OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_PERSISTENCE_INTEGRITY_CHECKPOINTS_H
#define DOMINIUM_SERVER_PERSISTENCE_INTEGRITY_CHECKPOINTS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_INTEGRITY_MAX_PARTITIONS 8u
#define DOM_INTEGRITY_MAX_SCHEMA_VERSIONS 8u

typedef struct dom_integrity_checkpoint {
    dom_shard_id shard_id;
    dom_act_time_t act_tick;
    u32 partition_count;
    u32 partition_ids[DOM_INTEGRITY_MAX_PARTITIONS];
    u64 hash_values[DOM_INTEGRITY_MAX_PARTITIONS];
    u32 schema_version_count;
    u64 schema_versions[DOM_INTEGRITY_MAX_SCHEMA_VERSIONS];
    u64 mod_graph_hash;
    u64 engine_build_id;
    u64 game_build_id;
} dom_integrity_checkpoint;

typedef struct dom_integrity_checkpoint_log {
    dom_integrity_checkpoint* entries;
    u32 count;
    u32 capacity;
} dom_integrity_checkpoint_log;

typedef struct dom_integrity_schedule {
    dom_act_time_t interval;
    dom_act_time_t next_due;
} dom_integrity_schedule;

void dom_integrity_checkpoint_log_init(dom_integrity_checkpoint_log* log,
                                       dom_integrity_checkpoint* storage,
                                       u32 capacity);
int dom_integrity_checkpoint_log_record(dom_integrity_checkpoint_log* log,
                                        const dom_integrity_checkpoint* checkpoint);
u64 dom_integrity_checkpoint_hash(const dom_integrity_checkpoint* checkpoint);
u64 dom_integrity_checkpoint_log_hash(const dom_integrity_checkpoint_log* log);

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
                                   u64 game_build_id);

dom_act_time_t dom_integrity_schedule_next(dom_integrity_schedule* schedule,
                                           dom_act_time_t now);

int dom_integrity_witness_verify(const dom_integrity_checkpoint* expected,
                                 const dom_shard_log* shard_log,
                                 u32* out_mismatch_partition);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_PERSISTENCE_INTEGRITY_CHECKPOINTS_H */
