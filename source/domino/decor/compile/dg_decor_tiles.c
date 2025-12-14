/* DECOR compiled tiles (C89). */
#include "decor/compile/dg_decor_tiles.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

void dg_decor_tiles_init(dg_decor_tiles *t) {
    if (!t) return;
    memset(t, 0, sizeof(*t));
}

void dg_decor_tiles_free(dg_decor_tiles *t) {
    if (!t) return;
    if (t->tiles) free(t->tiles);
    if (t->indices) free(t->indices);
    dg_decor_tiles_init(t);
}

void dg_decor_tiles_clear(dg_decor_tiles *t) {
    if (!t) return;
    t->tile_count = 0u;
    t->index_count = 0u;
}

int dg_decor_tiles_reserve(dg_decor_tiles *t, u32 tile_capacity, u32 index_capacity) {
    dg_decor_tile *tiles;
    u32 *indices;
    u32 new_tile_cap;
    u32 new_index_cap;

    if (!t) return -1;

    if (tile_capacity > t->tile_capacity) {
        new_tile_cap = t->tile_capacity ? t->tile_capacity : 8u;
        while (new_tile_cap < tile_capacity) {
            if (new_tile_cap > 0x7FFFFFFFu) {
                new_tile_cap = tile_capacity;
                break;
            }
            new_tile_cap *= 2u;
        }
        tiles = (dg_decor_tile *)realloc(t->tiles, sizeof(dg_decor_tile) * (size_t)new_tile_cap);
        if (!tiles) return -2;
        if (new_tile_cap > t->tile_capacity) {
            memset(&tiles[t->tile_capacity], 0, sizeof(dg_decor_tile) * (size_t)(new_tile_cap - t->tile_capacity));
        }
        t->tiles = tiles;
        t->tile_capacity = new_tile_cap;
    }

    if (index_capacity > t->index_capacity) {
        new_index_cap = t->index_capacity ? t->index_capacity : 16u;
        while (new_index_cap < index_capacity) {
            if (new_index_cap > 0x7FFFFFFFu) {
                new_index_cap = index_capacity;
                break;
            }
            new_index_cap *= 2u;
        }
        indices = (u32 *)realloc(t->indices, sizeof(u32) * (size_t)new_index_cap);
        if (!indices) return -3;
        if (new_index_cap > t->index_capacity) {
            memset(&indices[t->index_capacity], 0, sizeof(u32) * (size_t)(new_index_cap - t->index_capacity));
        }
        t->indices = indices;
        t->index_capacity = new_index_cap;
    }

    return 0;
}

static int cmp_u64_asc(const void *pa, const void *pb) {
    const u64 *a = (const u64 *)pa;
    const u64 *b = (const u64 *)pb;
    return D_DET_CMP_U64(*a, *b);
}

int dg_decor_tiles_build_from_instances(dg_decor_tiles *out, const dg_decor_instances *instances) {
    u32 i;
    u32 type_count;
    u64 *types;
    u32 unique_count;
    u32 idx_written;

    if (!out) return -1;
    dg_decor_tiles_clear(out);
    if (!instances || instances->count == 0u) return 0;

    /* Collect type ids. */
    type_count = instances->count;
    types = (u64 *)malloc(sizeof(u64) * (size_t)type_count);
    if (!types) return -2;
    for (i = 0u; i < type_count; ++i) {
        types[i] = (u64)instances->items[i].decor_type_id;
    }
    qsort(types, (size_t)type_count, sizeof(u64), cmp_u64_asc);

    /* Dedupe in-place. */
    unique_count = 0u;
    for (i = 0u; i < type_count; ++i) {
        if (i == 0u || types[i] != types[i - 1u]) {
            types[unique_count++] = types[i];
        }
    }

    /* Worst case: one tile per instance and indices == instance_count. */
    if (dg_decor_tiles_reserve(out, unique_count, instances->count) != 0) {
        free(types);
        return -3;
    }

    idx_written = 0u;
    for (i = 0u; i < unique_count; ++i) {
        u64 type_id = types[i];
        dg_decor_tile tile;
        u32 j;
        u32 start = idx_written;

        for (j = 0u; j < instances->count; ++j) {
            if ((u64)instances->items[j].decor_type_id == type_id) {
                if (idx_written >= out->index_capacity) {
                    /* Should not happen due to reserve; still keep safe. */
                    if (dg_decor_tiles_reserve(out, out->tile_capacity, out->index_capacity + 16u) != 0) {
                        free(types);
                        return -4;
                    }
                }
                out->indices[idx_written++] = j;
            }
        }

        tile.chunk_id = instances->items[0].chunk_id;
        tile.decor_type_id = (dg_decor_type_id)type_id;
        tile.index_offset = start;
        tile.index_count = idx_written - start;

        /* Skip empty tiles (defensive). */
        if (tile.index_count != 0u) {
            out->tiles[out->tile_count++] = tile;
        }
    }

    out->index_count = idx_written;
    free(types);
    return 0;
}

