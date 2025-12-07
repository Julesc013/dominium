#include "sim_systems.h"

static void phase_input(SurfaceRuntime *surface, fix32 dt)
{
    (void)surface;
    (void)dt;
}

static void phase_ecs(SurfaceRuntime *surface, fix32 dt)
{
    (void)dt;
    if (!surface) return;
    ecs_tick(&surface->ecs, dt);
}

static void phase_networks(SurfaceRuntime *surface)
{
    (void)surface;
}

static void phase_fluids(SurfaceRuntime *surface)
{
    (void)surface;
}

static void phase_climate(SurfaceRuntime *surface)
{
    (void)surface;
}

static void phase_apply_edits(SurfaceRuntime *surface)
{
    (void)surface;
}

void sim_tick_surface(SurfaceRuntime *surface, WorldServices *ws, fix32 dt)
{
    (void)ws;
    if (!surface) return;
    phase_input(surface, dt);
    phase_ecs(surface, dt);
    phase_networks(surface);
    phase_fluids(surface);
    phase_climate(surface);
    phase_apply_edits(surface);
}
