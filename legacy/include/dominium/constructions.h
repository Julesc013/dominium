/*
FILE: include/dominium/constructions.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / constructions
RESPONSIBILITY: Defines the public contract for `constructions` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_CONSTRUCTIONS_H
#define DOMINIUM_CONSTRUCTIONS_H

#include <stddef.h>
#include "domino/baseline.h"

#include "domino/core.h"
#include "domino/dworld.h"
#include "domino/canvas.h"
#include "dominium/world.h"
#include "dominium/content_prefabs.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_construction_id: Public type used by `constructions`. */
typedef uint32_t dom_construction_id;

/* dom_construction_spawn_desc: Public type used by `constructions`. */
typedef struct dom_construction_spawn_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_prefab_id  prefab;
    dom_surface_id surface;
    WPosExact      position;
    uint32_t       owner_actor;
    uint32_t       flags;
} dom_construction_spawn_desc;

/* dom_construction_state: Public type used by `constructions`. */
typedef struct dom_construction_state {
    uint32_t          struct_size;
    uint32_t          struct_version;
    dom_construction_id id;
    dom_prefab_id     prefab;
    dom_surface_id    surface;
    WPosExact         position;
    uint32_t          flags;
} dom_construction_state;

/* Purpose: Spawn dom construction.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_construction_spawn(const dom_construction_spawn_desc* desc,
                                  dom_construction_id* out_id);
/* Purpose: Destroy construction.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_construction_destroy(dom_construction_id id);
/* Purpose: State dom construction get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_construction_get_state(dom_construction_id id,
                                      dom_construction_state* out_state,
                                      size_t out_state_size);
/* Purpose: Tick construction.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_construction_tick(dom_construction_id id, uint32_t dt_millis);
/* Purpose: Step constructions.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
dom_status dom_constructions_step(uint32_t dt_millis);
/* Purpose: Sim step.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void       dom_constructions_sim_step(dom_core* core, dom_instance_id inst, double dt_s);
/* Purpose: Debug step count.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
uint64_t   dom_constructions_debug_step_count(dom_instance_id inst);
/* Purpose: Canvas dom construction build.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool       dom_construction_build_canvas(dom_core* core,
                                         dom_instance_id inst,
                                         const char* canvas_id,
                                         dom_gfx_buffer* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONSTRUCTIONS_H */
