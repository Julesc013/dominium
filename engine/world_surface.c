#include "world_surface.h"

#include <stdlib.h>
#include <string.h>

static u32 hash_chunk_key(const ChunkKey3D *key)
{
    u32 hx = (u32)key->gx * 73856093U;
    u32 hy = (u32)key->gy * 19349663U;
    u32 hz = (u32)key->gz * 83492791U;
    return hx ^ hy ^ hz;
}

static b32 keys_equal(const ChunkKey3D *a, const ChunkKey3D *b)
{
    return (a->gx == b->gx) && (a->gy == b->gy) && (a->gz == b->gz);
}

void surface_runtime_init(SurfaceRuntime *s,
                          u32 surface_id,
                          u64 seed,
                          MaterialRegistry *mreg,
                          VolumeRegistry *vreg,
                          RecipeRegistry *rreg,
                          RecipeId recipe)
{
    if (!s) return;
    memset(s, 0, sizeof(*s));
    s->surface_id = surface_id;
    s->seed = seed;
    s->mat_reg = mreg;
    s->vol_reg = vreg;
    s->recipe_reg = rreg;
    s->recipe_id = recipe;

    rng_seed(&s->rng_weather, seed ^ 0x1ULL);
    rng_seed(&s->rng_hydro, seed ^ 0x2ULL);
    rng_seed(&s->rng_misc, seed ^ 0x3ULL);
    ecs_init(&s->ecs, 16);
}

void surface_runtime_free(SurfaceRuntime *s)
{
    u32 i;
    if (!s) return;
    for (i = 0; i < SURFACE_CHUNK_TABLE_SIZE; ++i) {
        if (s->chunks[i].used && s->chunks[i].chunk) {
            chunk_runtime_free(s->chunks[i].chunk);
            free(s->chunks[i].chunk);
            s->chunks[i].chunk = NULL;
            s->chunks[i].used = FALSE;
        }
    }
    ecs_free(&s->ecs);
}

ChunkRuntime *surface_get_chunk(SurfaceRuntime *s, const ChunkKey3D *key, b32 create_if_missing)
{
    u32 idx;
    u32 start;
    if (!s || !key) return NULL;
    start = hash_chunk_key(key) & (SURFACE_CHUNK_TABLE_SIZE - 1U);
    idx = start;
    do {
        ChunkTableEntry *entry = &s->chunks[idx];
        if (entry->used) {
            if (entry->chunk && keys_equal(&entry->key, key)) {
                return entry->chunk;
            }
        } else if (create_if_missing) {
            ChunkRuntime *chunk = (ChunkRuntime *)malloc(sizeof(ChunkRuntime));
            if (!chunk) {
                return NULL;
            }
            chunk_runtime_init(chunk, key);
            entry->used = TRUE;
            entry->key = *key;
            entry->chunk = chunk;
            return chunk;
        } else {
            return NULL;
        }
        idx = (idx + 1U) & (SURFACE_CHUNK_TABLE_SIZE - 1U);
    } while (idx != start);
    return NULL;
}
