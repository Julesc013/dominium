/*
FILE: source/domino/res/d_res_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/d_res_model
RESPONSIBILITY: Implements `d_res_model`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Resource model vtable (C89). */
#ifndef D_RES_MODEL_H
#define D_RES_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "res/d_res.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DRES_MODEL_STRATA_SOLID 1u

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

/* Built-in registration helpers */
void dres_register_strata_solid_model(void);

#ifdef __cplusplus
}
#endif

#endif /* D_RES_MODEL_H */
