/* Terrain height sampling helpers (C89). */
#ifndef D_WORLD_TERRAIN_H
#define D_WORLD_TERRAIN_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Sample terrain height at (x,y) in world coordinates; z is returned in q32_32. */
int d_world_height_at(d_world *w, q32_32 x, q32_32 y, q32_32 *out_z);

#ifdef __cplusplus
}
#endif

#endif /* D_WORLD_TERRAIN_H */

