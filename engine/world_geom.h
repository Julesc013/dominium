#ifndef DOM_WORLD_GEOM_H
#define DOM_WORLD_GEOM_H

#include "core_fixed.h"
#include "registry_material.h"
#include "world_addr.h"

struct SurfaceRuntime;

typedef struct GeomSample {
    fix32 phi;
    MatId mat_id;
} GeomSample;

b32 geom_sample(struct SurfaceRuntime *surface, const SimPos *pos, GeomSample *out);

#endif /* DOM_WORLD_GEOM_H */
