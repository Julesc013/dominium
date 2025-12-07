#include "world_chunk.h"

#include <stdlib.h>
#include <string.h>

#define CHUNK_DIRTY_TERRAIN 0x1

static b32 ensure_entity_capacity(ChunkRuntime *chunk, u32 needed)
{
    u32 new_cap;
    EntityId *new_entities;
    if (chunk->entity_capacity >= needed) {
        return TRUE;
    }
    new_cap = (chunk->entity_capacity == 0) ? 4U : (chunk->entity_capacity * 2U);
    if (new_cap < needed) {
        new_cap = needed;
    }
    new_entities = (EntityId *)realloc(chunk->entities, sizeof(EntityId) * new_cap);
    if (!new_entities) {
        return FALSE;
    }
    chunk->entities = new_entities;
    chunk->entity_capacity = new_cap;
    return TRUE;
}

void chunk_runtime_init(ChunkRuntime *chunk, const ChunkKey3D *key)
{
    if (!chunk) return;
    memset(chunk, 0, sizeof(*chunk));
    if (key) {
        chunk->key = *key;
    }
    chunk->terrain.valid = FALSE;
}

void chunk_runtime_free(ChunkRuntime *chunk)
{
    if (!chunk) return;
    if (chunk->entities) {
        free(chunk->entities);
        chunk->entities = NULL;
    }
    if (chunk->volumes) {
        free(chunk->volumes);
        chunk->volumes = NULL;
    }
    chunk->entity_capacity = 0;
    chunk->entity_count = 0;
    chunk->volume_capacity = 0;
    chunk->volume_count = 0;
}

b32 chunk_add_entity(ChunkRuntime *chunk, EntityId id)
{
    if (!chunk) return FALSE;
    if (!ensure_entity_capacity(chunk, chunk->entity_count + 1U)) {
        return FALSE;
    }
    chunk->entities[chunk->entity_count++] = id;
    chunk->dirty_flags |= CHUNK_DIRTY_TERRAIN;
    return TRUE;
}
