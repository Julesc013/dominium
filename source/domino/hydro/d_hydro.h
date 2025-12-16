/*
FILE: source/domino/hydro/d_hydro.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / hydro/d_hydro
RESPONSIBILITY: Implements `d_hydro`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Hydrology subsystem (C89). */
#ifndef D_HYDRO_H
#define D_HYDRO_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u16 d_hydro_model_id;

typedef struct d_hydro_cell_s {
    q16_16 surface_height;
    q16_16 depth;
    q16_16 velocity_x;
    q16_16 velocity_y;
    q16_16 flags;
} d_hydro_cell;

typedef struct d_hydro_model_vtable_s {
    d_hydro_model_id model_id;

    void (*init_chunk)(
        d_world    *w,
        d_chunk    *chunk,
        d_tlv_blob *params
    );

    void (*tick)(
        d_world    *w,
        d_chunk    *chunk,
        u32         ticks
    );

    void (*sample)(
        const d_world *w,
        const d_chunk *chunk,
        q32_32         x,
        q32_32         y,
        q32_32         z,
        d_hydro_cell  *out_cell
    );
} d_hydro_model_vtable;

int d_hydro_register_model(const d_hydro_model_vtable *vt);
void d_hydro_tick(d_world *w, u32 ticks);

/* Convenience sampling API for the active model. */
int d_hydro_sample_at(
    d_world      *w,
    q32_32        x,
    q32_32        y,
    q32_32        z,
    d_hydro_cell *out_cell
);

/* Built-in model ids. */
#define D_HYDRO_MODEL_SURFACE_WATER 1

/* Subsystem hook */
void d_hydro_init(void);
int d_hydro_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_HYDRO_H */
