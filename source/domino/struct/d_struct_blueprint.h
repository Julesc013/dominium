#ifndef D_STRUCT_BLUEPRINT_H
#define D_STRUCT_BLUEPRINT_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Instantiate blueprint at world position (x,y,z), no rotation for now. */
int d_struct_spawn_blueprint(
    d_world                  *w,
    const d_proto_blueprint  *bp,
    q16_16                    x,
    q16_16                    y,
    q16_16                    z
);

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_BLUEPRINT_H */
