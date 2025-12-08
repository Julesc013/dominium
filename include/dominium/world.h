#ifndef DOMINIUM_WORLD_H
#define DOMINIUM_WORLD_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/sim.h"
#include "domino/dworld.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_world dom_world;

typedef uint32_t dom_surface_id;
typedef uint32_t dom_surface_frame_id;

typedef struct dom_world_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_core* core;
    dom_sim*  sim;
} dom_world_desc;

typedef struct dom_surface_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    uint64_t    seed;
    uint32_t    tier;
    const char* recipe_id;
} dom_surface_desc;

typedef struct dom_surface_info {
    uint32_t      struct_size;
    uint32_t      struct_version;
    dom_surface_id id;
    uint64_t      seed;
    uint32_t      tier;
} dom_surface_info;

typedef struct dom_surface_frame_view {
    uint32_t          struct_size;
    uint32_t          struct_version;
    dom_surface_id    surface;
    dom_surface_frame_id frame;
    uint64_t          tick_index;
} dom_surface_frame_view;

dom_status dom_world_create(const dom_world_desc* desc, dom_world** out_world);
void       dom_world_destroy(dom_world* world);

dom_status dom_world_tick(dom_world* world, uint32_t dt_millis);

dom_status dom_world_create_surface(dom_world* world,
                                    const dom_surface_desc* desc,
                                    dom_surface_id* out_surface);
dom_status dom_world_remove_surface(dom_world* world, dom_surface_id surface);
dom_status dom_world_get_surface_info(dom_world* world,
                                      dom_surface_id surface,
                                      dom_surface_info* out_info,
                                      size_t out_info_size);

dom_status dom_world_acquire_frame(dom_world* world,
                                   dom_surface_id surface,
                                   dom_surface_frame_view* out_frame);
dom_status dom_world_release_frame(dom_world* world,
                                   dom_surface_frame_id frame);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_WORLD_H */
