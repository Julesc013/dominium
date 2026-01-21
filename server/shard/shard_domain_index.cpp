/*
FILE: server/shard/shard_domain_index.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic index of domain sub-volumes owned by shards.
*/
#include "shard_domain_index.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

void dom_shard_domain_index_init(dom_shard_domain_index* index,
                                 dom_shard_domain_assignment* storage,
                                 u32 capacity)
{
    if (!index) {
        return;
    }
    index->assignments = storage;
    index->count = 0u;
    index->capacity = capacity;
    index->overflow = 0u;
    index->uncertain = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_shard_domain_assignment) * (size_t)capacity);
    }
}

void dom_shard_domain_index_clear(dom_shard_domain_index* index)
{
    if (!index) {
        return;
    }
    index->count = 0u;
    index->overflow = 0u;
    index->uncertain = 0u;
}

static int dom_shard_domain_assignment_before(const dom_shard_domain_assignment* a,
                                              const dom_shard_domain_assignment* b)
{
    if (a->domain_id < b->domain_id) {
        return 1;
    }
    if (a->domain_id > b->domain_id) {
        return 0;
    }
    if (a->resolution < b->resolution) {
        return 1;
    }
    if (a->resolution > b->resolution) {
        return 0;
    }
    return (a->tile_id < b->tile_id) ? 1 : 0;
}

int dom_shard_domain_index_add(dom_shard_domain_index* index,
                               const dom_shard_domain_assignment* assignment)
{
    u32 insert_at;
    u32 i;
    if (!index || !assignment || !index->assignments) {
        return -1;
    }
    if (index->count >= index->capacity) {
        index->overflow = 1u;
        return -2;
    }
    insert_at = 0u;
    while (insert_at < index->count &&
           dom_shard_domain_assignment_before(&index->assignments[insert_at], assignment)) {
        insert_at += 1u;
    }
    for (i = index->count; i > insert_at; --i) {
        index->assignments[i] = index->assignments[i - 1u];
    }
    index->assignments[insert_at] = *assignment;
    index->count += 1u;
    return 0;
}

int dom_shard_domain_index_find_shard(const dom_shard_domain_index* index,
                                      dom_domain_id domain_id,
                                      u64 tile_id,
                                      dom_shard_id* out_shard)
{
    u32 i;
    if (!index || !index->assignments) {
        return -1;
    }
    for (i = 0u; i < index->count; ++i) {
        const dom_shard_domain_assignment* a = &index->assignments[i];
        if (a->domain_id == domain_id && a->tile_id == tile_id) {
            if (out_shard) {
                *out_shard = a->shard_id;
            }
            return 0;
        }
    }
    return 1;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
