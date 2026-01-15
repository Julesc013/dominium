/*
FILE: source/domino/sim/_legacy/core_sim/sim_systems.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/sim_systems
RESPONSIBILITY: Implements `sim_systems`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
