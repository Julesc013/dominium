#include "dom_sim_world.h"
#include "dom_core_mem.h"
#include "dom_sim_ecs.h"
#include "dom_sim_events.h"
#include "dom_sim_jobs.h"
#include <string.h>

struct DomSimWorld {
    DomSimConfig   cfg;
    DomSurfaceMeta surfaces[DOM_SIM_WORLD_MAX_SURFACES];
    dom_u32        surface_count;
    dom_surface_id default_surface;
};

static void dom_sim_world_clear_surfaces(DomSimWorld *world)
{
    dom_u32 i;
    if (!world) return;
    for (i = 0; i < DOM_SIM_WORLD_MAX_SURFACES; ++i) {
        memset(&world->surfaces[i], 0, sizeof(DomSurfaceMeta));
    }
    world->surface_count = 0;
    world->default_surface = 0;
}

static dom_err_t dom_sim_world_add_default_surface(DomSimWorld *world)
{
    DomSurfaceMeta meta;
    if (!world) return DOM_ERR_INVALID_ARG;
    dom_sim_world_clear_surfaces(world);
    if (world->surface_count >= DOM_SIM_WORLD_MAX_SURFACES) return DOM_ERR_BOUNDS;
    memset(&meta, 0, sizeof(meta));
    meta.id = (dom_surface_id)(world->surface_count + 1);
    meta.planet = 1;
    meta.origin_x = 0;
    meta.origin_y = 0;
    meta.radius_m = 0;
    meta.flags = 0;
    world->surfaces[world->surface_count] = meta;
    world->surface_count += 1;
    world->default_surface = meta.id;
    return DOM_OK;
}

dom_err_t dom_sim_world_create(const DomSimConfig *cfg, DomSimWorld **out_world)
{
    DomSimWorld *w;
    dom_err_t err;
    if (!cfg || !out_world) return DOM_ERR_INVALID_ARG;
    w = (DomSimWorld *)dom_alloc_zero((dom_u32)sizeof(DomSimWorld));
    if (!w) return DOM_ERR_OUT_OF_MEMORY;
    w->cfg = *cfg;

    err = dom_sim_tick_init(cfg);
    if (err != DOM_OK) {
        dom_free(w);
        return err;
    }
    err = dom_sim_ecs_init();
    if (err != DOM_OK) {
        dom_free(w);
        return err;
    }
    err = dom_sim_events_init();
    if (err != DOM_OK) {
        dom_free(w);
        return err;
    }
    err = dom_sim_jobs_init();
    if (err != DOM_OK) {
        dom_free(w);
        return err;
    }
    err = dom_sim_world_add_default_surface(w);
    if (err != DOM_OK) {
        dom_free(w);
        return err;
    }
    *out_world = w;
    return DOM_OK;
}

void dom_sim_world_destroy(DomSimWorld *world)
{
    if (!world) return;
    dom_free(world);
}

void dom_sim_world_reset(DomSimWorld *world, DomTickId start_tick)
{
    if (!world) return;
    dom_sim_tick_reset(start_tick);
    dom_sim_ecs_reset();
    dom_sim_events_reset();
    dom_sim_jobs_reset();
    dom_sim_world_add_default_surface(world);
}

dom_err_t dom_sim_world_step(DomSimWorld *world)
{
    if (!world) return DOM_ERR_INVALID_ARG;
    return dom_sim_tick_step();
}

DomSimTime dom_sim_world_time(const DomSimWorld *world)
{
    (void)world;
    return dom_sim_tick_get_time();
}

dom_u32 dom_sim_world_surface_count(const DomSimWorld *world)
{
    return world ? world->surface_count : 0;
}

dom_surface_id dom_sim_world_default_surface(const DomSimWorld *world)
{
    return world ? world->default_surface : 0;
}

dom_err_t dom_sim_world_create_surface(DomSimWorld *world,
                                       dom_planet_id planet,
                                       const DomSurfaceMeta *meta,
                                       DomSurfaceMeta *out_meta)
{
    dom_u32 index;
    DomSurfaceMeta dst;
    if (!world || !meta) return DOM_ERR_INVALID_ARG;
    if (world->surface_count >= DOM_SIM_WORLD_MAX_SURFACES) return DOM_ERR_BOUNDS;
    index = world->surface_count;
    memset(&dst, 0, sizeof(dst));
    dst.id = (dom_surface_id)(index + 1);
    dst.planet = planet;
    dst.origin_x = meta->origin_x;
    dst.origin_y = meta->origin_y;
    dst.radius_m = meta->radius_m;
    dst.flags = meta->flags;
    world->surfaces[index] = dst;
    world->surface_count = index + 1;
    if (world->default_surface == 0) {
        world->default_surface = dst.id;
    }
    if (out_meta) {
        *out_meta = dst;
    }
    return DOM_OK;
}

const DomSurfaceMeta *dom_sim_world_get_surface(const DomSimWorld *world, dom_surface_id id)
{
    dom_u32 i;
    if (!world || id == 0) return 0;
    for (i = 0; i < world->surface_count; ++i) {
        if (world->surfaces[i].id == id) {
            return &world->surfaces[i];
        }
    }
    return 0;
}

dom_err_t dom_sim_world_surface_of_coord(const DomSimWorld *world,
                                         dom_i64 x, dom_i64 y,
                                         dom_surface_id *out_surface)
{
    (void)x;
    (void)y;
    if (!world || !out_surface) return DOM_ERR_INVALID_ARG;
    *out_surface = world->default_surface;
    return *out_surface ? DOM_OK : DOM_ERR_NOT_FOUND;
}
