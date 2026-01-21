/*
FILE: server/shard/domain_shard_mapper.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic domain-driven shard mapping and partitioning.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers; OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_DOMAIN_SHARD_MAPPER_H
#define DOMINIUM_SERVER_DOMAIN_SHARD_MAPPER_H

#include "domino/world/domain_query.h"
#include "shard/shard_domain_index.h"

#ifdef __cplusplus
extern "C" {
#endif

enum dom_domain_shard_flags {
    DOM_DOMAIN_SHARD_FLAG_ALLOW_SPLIT = 1u << 0u,
    DOM_DOMAIN_SHARD_FLAG_ALLOW_STREAMING = 1u << 1u,
    DOM_DOMAIN_SHARD_FLAG_ALLOW_SIMULATION = 1u << 2u
};

typedef struct dom_domain_partition_params {
    u32 shard_count;
    u32 allow_split;
    u32 resolution; /* dom_domain_resolution */
    u32 max_tiles_per_domain;
    u32 budget_units;
    u64 global_seed;
} dom_domain_partition_params;

typedef struct dom_domain_shard_input {
    dom_domain_id domain_id;
    const dom_domain_volume* volume;
    u32 flags;
} dom_domain_shard_input;

void dom_domain_partition_params_init(dom_domain_partition_params* params);
d_bool dom_domain_shard_streaming_allowed(const dom_domain_shard_input* input);

int dom_domain_shard_map(const dom_domain_shard_input* inputs,
                         u32 input_count,
                         const dom_domain_partition_params* params,
                         dom_shard_domain_index* out_index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_DOMAIN_SHARD_MAPPER_H */
