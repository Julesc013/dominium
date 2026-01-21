/*
FILE: source/domino/world/domain_cache.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain_cache
RESPONSIBILITY: Implements deterministic tile cache with stable eviction.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: LRU with stable insert-order tie-break.
*/
#include "domino/world/domain_cache.h"

#include <stdlib.h>
#include <string.h>

void dom_domain_cache_init(dom_domain_cache* cache)
{
    if (!cache) {
        return;
    }
    memset(cache, 0, sizeof(*cache));
}

void dom_domain_cache_free(dom_domain_cache* cache)
{
    u32 i;
    if (!cache) {
        return;
    }
    if (cache->entries) {
        for (i = 0u; i < cache->capacity; ++i) {
            dom_domain_tile_free(&cache->entries[i].tile);
        }
        free(cache->entries);
        cache->entries = (dom_domain_cache_entry *)0;
    }
    cache->capacity = 0u;
    cache->count = 0u;
    cache->use_counter = 0u;
    cache->next_insert_order = 0u;
}

int dom_domain_cache_reserve(dom_domain_cache* cache, u32 capacity)
{
    dom_domain_cache_entry* new_entries;
    u32 old_cap;
    u32 i;
    if (!cache) {
        return -1;
    }
    if (capacity <= cache->capacity) {
        return 0;
    }
    new_entries = (dom_domain_cache_entry *)realloc(cache->entries,
                                                    capacity * sizeof(dom_domain_cache_entry));
    if (!new_entries) {
        return -1;
    }
    old_cap = cache->capacity;
    cache->entries = new_entries;
    cache->capacity = capacity;
    for (i = old_cap; i < cache->capacity; ++i) {
        memset(&cache->entries[i], 0, sizeof(dom_domain_cache_entry));
        dom_domain_tile_init(&cache->entries[i].tile);
        cache->entries[i].valid = D_FALSE;
    }
    return 0;
}

static dom_domain_cache_entry* dom_domain_cache_find_entry(dom_domain_cache* cache,
                                                           dom_domain_id domain_id,
                                                           u64 tile_id,
                                                           u32 resolution,
                                                           u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (dom_domain_cache_entry *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_domain_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version) {
            return entry;
        }
    }
    return (dom_domain_cache_entry *)0;
}

const dom_domain_tile* dom_domain_cache_peek(const dom_domain_cache* cache,
                                             dom_domain_id domain_id,
                                             u64 tile_id,
                                             u32 resolution,
                                             u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return (const dom_domain_tile *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        const dom_domain_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            continue;
        }
        if (entry->domain_id == domain_id &&
            entry->tile_id == tile_id &&
            entry->resolution == resolution &&
            entry->authoring_version == authoring_version) {
            return &entry->tile;
        }
    }
    return (const dom_domain_tile *)0;
}

const dom_domain_tile* dom_domain_cache_get(dom_domain_cache* cache,
                                            dom_domain_id domain_id,
                                            u64 tile_id,
                                            u32 resolution,
                                            u32 authoring_version)
{
    dom_domain_cache_entry* entry;
    if (!cache) {
        return (const dom_domain_tile *)0;
    }
    entry = dom_domain_cache_find_entry(cache, domain_id, tile_id, resolution, authoring_version);
    if (!entry) {
        return (const dom_domain_tile *)0;
    }
    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;
    return &entry->tile;
}

static dom_domain_cache_entry* dom_domain_cache_select_slot(dom_domain_cache* cache)
{
    u32 i;
    dom_domain_cache_entry* best = (dom_domain_cache_entry *)0;
    if (!cache || !cache->entries || cache->capacity == 0u) {
        return (dom_domain_cache_entry *)0;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_domain_cache_entry* entry = &cache->entries[i];
        if (!entry->valid) {
            return entry;
        }
        if (!best) {
            best = entry;
            continue;
        }
        if (entry->last_used < best->last_used) {
            best = entry;
        } else if (entry->last_used == best->last_used &&
                   entry->insert_order < best->insert_order) {
            best = entry;
        }
    }
    return best;
}

dom_domain_tile* dom_domain_cache_put(dom_domain_cache* cache,
                                      dom_domain_id domain_id,
                                      dom_domain_tile* tile)
{
    dom_domain_cache_entry* entry;
    if (!cache || !tile) {
        return (dom_domain_tile *)0;
    }
    if (!cache->entries || cache->capacity == 0u) {
        return (dom_domain_tile *)0;
    }

    entry = dom_domain_cache_find_entry(cache, domain_id, tile->tile_id,
                                        tile->resolution, tile->authoring_version);
    if (!entry) {
        entry = dom_domain_cache_select_slot(cache);
    }
    if (!entry) {
        return (dom_domain_tile *)0;
    }
    if (entry->valid) {
        dom_domain_tile_free(&entry->tile);
    } else {
        cache->count += 1u;
        entry->insert_order = cache->next_insert_order++;
    }

    entry->domain_id = domain_id;
    entry->tile_id = tile->tile_id;
    entry->resolution = tile->resolution;
    entry->authoring_version = tile->authoring_version;
    entry->tile = *tile;
    entry->valid = D_TRUE;

    cache->use_counter += 1u;
    entry->last_used = cache->use_counter;

    dom_domain_tile_init(tile);
    return &entry->tile;
}

void dom_domain_cache_invalidate_domain(dom_domain_cache* cache, dom_domain_id domain_id)
{
    u32 i;
    if (!cache || !cache->entries) {
        return;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_domain_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->domain_id == domain_id) {
            dom_domain_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

void dom_domain_cache_invalidate_version(dom_domain_cache* cache, u32 authoring_version)
{
    u32 i;
    if (!cache || !cache->entries) {
        return;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_domain_cache_entry* entry = &cache->entries[i];
        if (entry->valid && entry->authoring_version == authoring_version) {
            dom_domain_tile_free(&entry->tile);
            entry->valid = D_FALSE;
            if (cache->count > 0u) {
                cache->count -= 1u;
            }
        }
    }
}

void dom_domain_cache_invalidate_all(dom_domain_cache* cache)
{
    u32 i;
    if (!cache || !cache->entries) {
        return;
    }
    for (i = 0u; i < cache->capacity; ++i) {
        dom_domain_cache_entry* entry = &cache->entries[i];
        if (entry->valid) {
            dom_domain_tile_free(&entry->tile);
            entry->valid = D_FALSE;
        }
    }
    cache->count = 0u;
}
