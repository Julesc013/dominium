/* Environment model vtable (C89). */
#ifndef D_ENV_MODEL_H
#define D_ENV_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "env/d_env.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct denv_model_vtable {
    u16 model_id;

    void (*init_chunk)(
        d_world        *w,
        d_chunk        *chunk
    );

    void (*tick)(
        d_world         *w,
        d_chunk         *chunk,
        denv_zone_state *zones,
        u32              zone_count,
        denv_portal     *portals,
        u32              portal_count,
        u32              ticks
    );
} denv_model_vtable;

int denv_register_model(const denv_model_vtable *vt);

#ifdef __cplusplus
}
#endif

#endif /* D_ENV_MODEL_H */
