/*
FILE: source/domino/sim/_legacy/core_sim/world_surface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/world_surface
RESPONSIBILITY: Implements `world_surface`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_WORLD_SURFACE_H
#define DOM_WORLD_SURFACE_H

#include "core_types.h"
#include "core_ids.h"
#include "core_rng.h"
#include "world_chunk.h"
#include "ecs.h"
#include "registry_material.h"
#include "registry_volume.h"
#include "registry_recipe.h"

#define SURFACE_CHUNK_TABLE_SIZE 8192

typedef struct ChunkTableEntry {
    ChunkKey3D    key;
    ChunkRuntime *chunk;
    b32           used;
} ChunkTableEntry;

typedef struct SurfaceRuntime {
    u32 surface_id;
    u64 seed;
    MaterialRegistry *mat_reg;
    VolumeRegistry   *vol_reg;
    RecipeRegistry   *recipe_reg;
    RecipeId          recipe_id;

    ChunkTableEntry chunks[SURFACE_CHUNK_TABLE_SIZE];

    RNGState rng_weather;
    RNGState rng_hydro;
    RNGState rng_misc;

    ECS ecs;

    void *atmo_ctx;
    void *hydro_ctx;
    void *fluidspace_ctx;
    void *thermal_ctx;
    void *net_hydraulic_ctx;
    void *net_electric_ctx;
    void *net_logic_ctx;
} SurfaceRuntime;

void surface_runtime_init(SurfaceRuntime *s,
                          u32 surface_id,
                          u64 seed,
                          MaterialRegistry *mreg,
                          VolumeRegistry *vreg,
                          RecipeRegistry *rreg,
                          RecipeId recipe);
void surface_runtime_free(SurfaceRuntime *s);

ChunkRuntime *surface_get_chunk(SurfaceRuntime *s, const ChunkKey3D *key, b32 create_if_missing);

#endif /* DOM_WORLD_SURFACE_H */
