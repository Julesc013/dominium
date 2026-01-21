/*
FILE: server/shard/shard_domain_index.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic index of domain sub-volumes owned by shards.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers; OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_DOMAIN_INDEX_H
#define DOMINIUM_SERVER_SHARD_DOMAIN_INDEX_H

#include "domino/world/domain_tile.h"
#include "shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

enum dom_shard_domain_flags {
    DOM_SHARD_DOMAIN_FLAG_STREAMING_ALLOWED = 1u << 0u,
    DOM_SHARD_DOMAIN_FLAG_SIMULATION_ALLOWED = 1u << 1u,
    DOM_SHARD_DOMAIN_FLAG_WHOLE_DOMAIN = 1u << 2u
};

typedef struct dom_shard_domain_assignment {
    dom_domain_id   domain_id;
    u64             tile_id;
    u32             resolution; /* dom_domain_resolution */
    dom_domain_aabb bounds;
    dom_shard_id    shard_id;
    u32             flags;
} dom_shard_domain_assignment;

typedef struct dom_shard_domain_index {
    dom_shard_domain_assignment* assignments;
    u32 count;
    u32 capacity;
    u32 overflow;
    u32 uncertain;
} dom_shard_domain_index;

void dom_shard_domain_index_init(dom_shard_domain_index* index,
                                 dom_shard_domain_assignment* storage,
                                 u32 capacity);
void dom_shard_domain_index_clear(dom_shard_domain_index* index);
int dom_shard_domain_index_add(dom_shard_domain_index* index,
                               const dom_shard_domain_assignment* assignment);
int dom_shard_domain_index_find_shard(const dom_shard_domain_index* index,
                                      dom_domain_id domain_id,
                                      u64 tile_id,
                                      dom_shard_id* out_shard);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_DOMAIN_INDEX_H */
