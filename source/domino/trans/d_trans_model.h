/* Transport model vtable (C89). */
#ifndef D_TRANS_MODEL_H
#define D_TRANS_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "trans/d_trans.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dtrans_model_vtable {
    u16 model_id; /* within D_MODEL_FAMILY_TRANS */

    /* Called to tick a spline instance. */
    void (*tick_spline)(
        d_world           *w,
        d_spline_instance *spline,
        u32                ticks
    );
} dtrans_model_vtable;

int dtrans_register_model(const dtrans_model_vtable *vt);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_MODEL_H */
