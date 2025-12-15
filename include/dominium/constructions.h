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

typedef uint32_t dom_construction_id;

typedef struct dom_construction_spawn_desc {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_prefab_id  prefab;
    dom_surface_id surface;
    WPosExact      position;
    uint32_t       owner_actor;
    uint32_t       flags;
} dom_construction_spawn_desc;

typedef struct dom_construction_state {
    uint32_t          struct_size;
    uint32_t          struct_version;
    dom_construction_id id;
    dom_prefab_id     prefab;
    dom_surface_id    surface;
    WPosExact         position;
    uint32_t          flags;
} dom_construction_state;

dom_status dom_construction_spawn(const dom_construction_spawn_desc* desc,
                                  dom_construction_id* out_id);
dom_status dom_construction_destroy(dom_construction_id id);
dom_status dom_construction_get_state(dom_construction_id id,
                                      dom_construction_state* out_state,
                                      size_t out_state_size);
dom_status dom_construction_tick(dom_construction_id id, uint32_t dt_millis);
dom_status dom_constructions_step(uint32_t dt_millis);
void       dom_constructions_sim_step(dom_core* core, dom_instance_id inst, double dt_s);
uint64_t   dom_constructions_debug_step_count(dom_instance_id inst);
bool       dom_construction_build_canvas(dom_core* core,
                                         dom_instance_id inst,
                                         const char* canvas_id,
                                         dom_gfx_buffer* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_CONSTRUCTIONS_H */
