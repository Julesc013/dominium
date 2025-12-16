/*
FILE: source/domino/sim/_legacy/core_sim/sim_world.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/sim_world
RESPONSIBILITY: Implements `sim_world`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "sim_world.h"

static b32 ws_raycast(SurfaceRuntime *surface, void *ray_params, void *out_hit)
{
    (void)surface;
    (void)ray_params;
    (void)out_hit;
    return FALSE;
}

static b32 ws_overlap_sphere(SurfaceRuntime *surface, void *sphere_params, void *out_hits)
{
    (void)surface;
    (void)sphere_params;
    (void)out_hits;
    return FALSE;
}

static b32 ws_sample_geom(SurfaceRuntime *surface, const SimPos *pos, GeomSample *out)
{
    return geom_sample(surface, pos, out);
}

static b32 ws_sample_medium(SurfaceRuntime *surface, const SimPos *pos, void *out_medium)
{
    (void)surface;
    (void)pos;
    (void)out_medium;
    return FALSE;
}

static b32 ws_sample_field_scalar(SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldScalarSample *out)
{
    return field_sample_scalar(surface, pos, id, out);
}

static b32 ws_sample_field_vector(SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldVectorSample *out)
{
    return field_sample_vector(surface, pos, id, out);
}

void world_services_init(WorldServices *ws)
{
    if (!ws) return;
    ws->raycast = ws_raycast;
    ws->overlap_sphere = ws_overlap_sphere;
    ws->sample_geom = ws_sample_geom;
    ws->sample_medium = ws_sample_medium;
    ws->sample_field_scalar = ws_sample_field_scalar;
    ws->sample_field_vector = ws_sample_field_vector;
}
