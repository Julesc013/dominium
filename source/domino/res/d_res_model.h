/* Resource model vtable (C89). */
#ifndef D_RES_MODEL_H
#define D_RES_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "res/d_res.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dres_model_vtable {
    u16 model_id;  /* used within D_MODEL_FAMILY_RES */

    void (*init_chunk)(
        d_world           *w,
        d_chunk           *chunk,
        dres_channel_cell *cell
    );

    void (*compute_base)(
        d_world           *w,
        const d_chunk     *chunk,
        dres_channel_cell *cell,
        q32_32             x,
        q32_32             y,
        q32_32             z
    );

    void (*apply_delta)(
        d_world           *w,
        d_chunk           *chunk,
        dres_channel_cell *cell,
        const q16_16      *delta_values,
        u32                seed_context
    );

    void (*tick)(
        d_world           *w,
        d_chunk           *chunk,
        dres_channel_cell *cell,
        u32                ticks
    );
} dres_model_vtable;

/* Register a resource model; thin wrapper around d_model_register. */
int dres_register_model(const dres_model_vtable *vt);

#ifdef __cplusplus
}
#endif

#endif /* D_RES_MODEL_H */
