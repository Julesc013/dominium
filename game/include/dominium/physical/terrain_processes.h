/*
FILE: include/dominium/physical/terrain_processes.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines terrain modification processes and deterministic application.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Terrain process outcomes are deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_TERRAIN_PROCESSES_H
#define DOMINIUM_PHYSICAL_TERRAIN_PROCESSES_H

#include "dominium/physical/field_storage.h"
#include "dominium/physical/physical_process.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_terrain_process_kind {
    DOM_TERRAIN_CLEAR_LAND = 1,
    DOM_TERRAIN_EXCAVATE = 2,
    DOM_TERRAIN_FILL = 3,
    DOM_TERRAIN_COMPACT = 4,
    DOM_TERRAIN_GRADE = 5,
    DOM_TERRAIN_TERRACE = 6,
    DOM_TERRAIN_DEFOREST = 7,
    DOM_TERRAIN_IRRIGATE = 8,
    DOM_TERRAIN_DRAIN = 9,
    DOM_TERRAIN_CONTAMINATE = 10,
    DOM_TERRAIN_REMEDIATE = 11
} dom_terrain_process_kind;

typedef struct dom_terrain_process_desc {
    u32 kind;
    u32 affected_field_mask;
    i32 delta_q16;
    i32 max_slope_q16;
    i32 min_bearing_q16;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 cost_units;
} dom_terrain_process_desc;

void dom_terrain_process_desc_default(u32 kind,
                                      dom_terrain_process_desc* out_desc);

int dom_terrain_apply_process(dom_field_storage* fields,
                              const dom_terrain_process_desc* desc,
                              u32 x,
                              u32 y,
                              const dom_physical_process_context* ctx,
                              dom_physical_process_result* out_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_TERRAIN_PROCESSES_H */
