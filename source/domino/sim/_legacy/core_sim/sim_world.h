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
