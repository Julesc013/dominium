#ifndef DOM_SIM_WORLD_H
#define DOM_SIM_WORLD_H

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "dom_core_id.h"
#include "dom_sim_tick.h"

#define DOM_SIM_WORLD_MAX_SURFACES 8

typedef struct DomSurfaceMeta {
    dom_surface_id id;
    dom_planet_id  planet;
    dom_i64        origin_x;
    dom_i64        origin_y;
    dom_i64        radius_m;
    dom_u32        flags;
} DomSurfaceMeta;

typedef struct DomSimWorld DomSimWorld;

dom_err_t dom_sim_world_create(const DomSimConfig *cfg, DomSimWorld **out_world);
void      dom_sim_world_destroy(DomSimWorld *world);
void      dom_sim_world_reset(DomSimWorld *world, DomTickId start_tick);

dom_err_t dom_sim_world_step(DomSimWorld *world);
DomSimTime dom_sim_world_time(const DomSimWorld *world);

dom_u32        dom_sim_world_surface_count(const DomSimWorld *world);
dom_surface_id dom_sim_world_default_surface(const DomSimWorld *world);
dom_err_t      dom_sim_world_create_surface(DomSimWorld *world,
                                            dom_planet_id planet,
                                            const DomSurfaceMeta *meta,
                                            DomSurfaceMeta *out_meta);
const DomSurfaceMeta *dom_sim_world_get_surface(const DomSimWorld *world, dom_surface_id id);
dom_err_t dom_sim_world_surface_of_coord(const DomSimWorld *world,
                                         dom_i64 x, dom_i64 y,
                                         dom_surface_id *out_surface);

#endif /* DOM_SIM_WORLD_H */
