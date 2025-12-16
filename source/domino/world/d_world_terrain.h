/*
FILE: source/domino/world/d_world_terrain.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_world_terrain
RESPONSIBILITY: Implements `d_world_terrain`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

