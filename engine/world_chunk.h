#ifndef DOM_WORLD_CHUNK_H
#define DOM_WORLD_CHUNK_H

#include "core_types.h"
#include "core_ids.h"
#include "world_addr.h"
#include "registry_material.h"

#define CHUNK_SAMPLES_PER_AXIS   32
#define CHUNK_SAMPLE_COUNT       (CHUNK_SAMPLES_PER_AXIS*CHUNK_SAMPLES_PER_AXIS*CHUNK_SAMPLES_PER_AXIS)

typedef struct ChunkTerrainCache {
    i16  phi[CHUNK_SAMPLE_COUNT];
    MatId mat[CHUNK_SAMPLE_COUNT];
    b32  valid;
} ChunkTerrainCache;

typedef struct ChunkRuntime {
    ChunkKey3D key;
    ChunkTerrainCache terrain;

    EntityId *entities;
    u32       entity_count;
    u32       entity_capacity;

    VolumeId *volumes;
    u32       volume_count;
    u32       volume_capacity;

    u32       dirty_flags;
} ChunkRuntime;

void chunk_runtime_init(ChunkRuntime *chunk, const ChunkKey3D *key);
void chunk_runtime_free(ChunkRuntime *chunk);

b32  chunk_add_entity(ChunkRuntime *chunk, EntityId id);

#endif /* DOM_WORLD_CHUNK_H */
