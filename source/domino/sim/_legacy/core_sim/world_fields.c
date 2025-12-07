#include "world_fields.h"

#include "world_surface.h"
#include "registry_recipe.h"

static u32 hash_coords(u32 x, u32 y, u32 seed)
{
    u32 h = seed ^ (x * 0x27d4eb2dU) ^ (y * 0x165667b1U);
    h ^= h >> 15;
    h *= 0x85ebca6bU;
    h ^= h >> 13;
    h *= 0xc2b2ae35U;
    h ^= h >> 16;
    return h;
}

static i32 evaluate_height(struct SurfaceRuntime *surface, const SimPos *pos)
{
    const RecipeDesc *recipe = NULL;
    i32 base_height = 32;
    i32 height_range = 24;
    u32 cell_x = ((u32)pos->sx << 16) | (u32)world_local_meter_x(pos);
    u32 cell_y = ((u32)pos->sy << 16) | (u32)world_local_meter_y(pos);
    u32 h = hash_coords(cell_x >> 4, cell_y >> 4, (u32)(surface ? surface->seed : 0U));
    if (surface && surface->recipe_reg) {
        recipe = recipe_get(surface->recipe_reg, surface->recipe_id);
        if (recipe) {
            base_height = recipe->base_height_m;
            height_range = recipe->height_range_m;
        }
    }
    return base_height + (i32)(h % (u32)height_range);
}

b32 field_sample_scalar(struct SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldScalarSample *out)
{
    if (!surface || !pos || !out) return FALSE;
    if (id == FIELD_ID_ELEVATION) {
        out->value = fix32_from_int(evaluate_height(surface, pos));
        return TRUE;
    } else if (id == FIELD_ID_TEMPERATURE) {
        out->value = fix32_from_int(280); /* Stub: 280K */
        return TRUE;
    }
    return FALSE;
}

b32 field_sample_vector(struct SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldVectorSample *out)
{
    (void)surface;
    (void)pos;
    (void)id;
    if (!out) return FALSE;
    out->x = 0;
    out->y = 0;
    out->z = 0;
    return FALSE;
}
