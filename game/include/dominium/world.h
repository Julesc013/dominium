/*
FILE: include/dominium/world.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / world
RESPONSIBILITY: Defines the public contract for `world` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_WORLD_H
#define DOMINIUM_WORLD_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "domino/sim.h"
#include "domino/dworld.h"
#include "domino/canvas.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_world: Public type used by `world`. */
typedef struct dom_world dom_world;

/* dom_surface_id: Public type used by `world`. */
typedef uint32_t dom_surface_id;
/* dom_surface_frame_id: Public type used by `world`. */
typedef uint32_t dom_surface_frame_id;

/* dom_world_desc: Public type used by `world`. */
typedef struct dom_world_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_core* core;
    dom_sim*  sim;
} dom_world_desc;

/* dom_surface_desc: Public type used by `world`. */
typedef struct dom_surface_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    uint64_t    seed;
    uint32_t    tier;
    const char* recipe_id;
} dom_surface_desc;

/* dom_surface_info: Public type used by `world`. */
typedef struct dom_surface_info {
    uint32_t      struct_size;
    uint32_t      struct_version;
    dom_surface_id id;
    uint64_t      seed;
    uint32_t      tier;
} dom_surface_info;

/* dom_surface_frame_view: Public type used by `world`. */
typedef struct dom_surface_frame_view {
    uint32_t          struct_size;
    uint32_t          struct_version;
    dom_surface_id    surface;
    dom_surface_frame_id frame;
    uint64_t          tick_index;
} dom_surface_frame_view;

/* Purpose: Create world.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_create(const dom_world_desc* desc, dom_world** out_world);
/* Purpose: Destroy world.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void       dom_world_destroy(dom_world* world);

/* Purpose: Tick world.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_tick(dom_world* world, uint32_t dt_millis);

/* Purpose: Create surface.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_create_surface(dom_world* world,
                                    const dom_surface_desc* desc,
                                    dom_surface_id* out_surface);
/* Purpose: Remove surface.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_remove_surface(dom_world* world, dom_surface_id surface);
/* Purpose: Get surface info.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_get_surface_info(dom_world* world,
                                      dom_surface_id surface,
                                      dom_surface_info* out_info,
                                      size_t out_info_size);

/* Purpose: Acquire frame.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_acquire_frame(dom_world* world,
                                   dom_surface_id surface,
                                   dom_surface_frame_view* out_frame);
/* Purpose: Release frame.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_world_release_frame(dom_world* world,
                                   dom_surface_frame_id frame);

/* Purpose: Sim step.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dom_world_sim_step(dom_core* core, dom_instance_id inst, double dt_s);
/* Purpose: Debug step count.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint64_t dom_world_debug_step_count(dom_instance_id inst);

/* Purpose: Build surface canvas.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_world_build_surface_canvas(dom_core* core,
                                    dom_instance_id inst,
                                    dom_gfx_buffer* out);

/* Purpose: Build orbit canvas.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_world_build_orbit_canvas(dom_core* core,
                                  dom_instance_id inst,
                                  dom_gfx_buffer* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_WORLD_H */
