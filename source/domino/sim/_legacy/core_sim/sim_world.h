/*
FILE: source/domino/sim/_legacy/core_sim/sim_world.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/sim_world
RESPONSIBILITY: Defines internal contract for `sim_world`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SIM_WORLD_H
#define DOM_SIM_WORLD_H

#include "core_types.h"
#include "world_surface.h"
#include "world_geom.h"
#include "world_fields.h"

typedef struct WorldServices {
    b32 (*raycast)(SurfaceRuntime *surface, void *ray_params, void *out_hit);
    b32 (*overlap_sphere)(SurfaceRuntime *surface, void *sphere_params, void *out_hits);

    b32 (*sample_geom)(SurfaceRuntime *surface, const SimPos *pos, GeomSample *out);
    b32 (*sample_medium)(SurfaceRuntime *surface, const SimPos *pos, void *out_medium);
    b32 (*sample_field_scalar)(SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldScalarSample *out);
    b32 (*sample_field_vector)(SurfaceRuntime *surface, const SimPos *pos, FieldId id, FieldVectorSample *out);
} WorldServices;

void world_services_init(WorldServices *ws);

#endif /* DOM_SIM_WORLD_H */
