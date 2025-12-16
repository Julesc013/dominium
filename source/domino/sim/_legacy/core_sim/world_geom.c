/*
FILE: source/domino/sim/_legacy/core_sim/world_geom.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/world_geom
RESPONSIBILITY: Implements `world_geom`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "world_geom.h"

#include "world_surface.h"
#include "registry_recipe.h"

static u32 hash_coords(u32 x, u32 y, u32 seed)
{
    u32 h = seed ^ (x * 0x9E3779B1U) ^ (y * 0x85EBCA77U);
    h ^= h >> 16;
    h *= 0x7FEB352DU;
    h ^= h >> 15;
    h *= 0x846CA68BU;
    h ^= h >> 16;
    return h;
}

static i32 sample_heightfield(struct SurfaceRuntime *surface, const SimPos *pos)
{
    const RecipeDesc *recipe = NULL;
    u32 cell_x;
    u32 cell_y;
    u32 h;
    i32 base_height = 32;
    i32 height_range = 24;
    if (surface && surface->recipe_reg) {
        recipe = recipe_get(surface->recipe_reg, surface->recipe_id);
        if (recipe) {
            base_height = recipe->base_height_m;
            height_range = recipe->height_range_m;
        }
    }
    cell_x = ((u32)pos->sx << 16) | (u32)world_local_meter_x(pos);
    cell_y = ((u32)pos->sy << 16) | (u32)world_local_meter_y(pos);
    h = hash_coords(cell_x >> 4, cell_y >> 4, (u32)(surface ? surface->seed : 0U));
    return base_height + (i32)(h % (u32)height_range);
}

b32 geom_sample(struct SurfaceRuntime *surface, const SimPos *pos, GeomSample *out)
{
    i32 terrain_height;
    fix32 terrain_z;
    fix32 phi;
    if (!surface || !pos || !out) return FALSE;
    terrain_height = sample_heightfield(surface, pos);
    terrain_z = fix32_from_int(terrain_height);
    phi = pos->z - terrain_z;
    out->phi = phi;
    out->mat_id = (phi < 0) ? 1 : 0; /* 1 = ground, 0 = air */
    return TRUE;
}
