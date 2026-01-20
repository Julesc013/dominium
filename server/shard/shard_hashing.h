/*
FILE: server/shard/shard_hashing.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard hash computation helpers.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers; OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_HASHING_H
#define DOMINIUM_SERVER_SHARD_HASHING_H

#include "shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

u64 dom_shard_hash_partition(const dom_shard_log* log, u32 partition_id);
int dom_shard_compute_partition_hashes(const dom_shard_log* log,
                                       const u32* partitions,
                                       u32 partition_count,
                                       u64* out_hashes);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_HASHING_H */
