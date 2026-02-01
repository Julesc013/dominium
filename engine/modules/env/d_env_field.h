/*
FILE: source/domino/env/d_env_field.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / env/d_env_field
RESPONSIBILITY: Defines internal contract for `d_env_field`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Environmental field abstraction (C89). */
#ifndef D_ENV_FIELD_H
#define D_ENV_FIELD_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u16 d_env_field_id;

typedef struct d_env_field_desc_s {
    d_env_field_id field_id;
    u16            model_id;
    u16            flags;
} d_env_field_desc;

typedef struct d_env_field_cell_s {
    d_env_field_desc desc;
    q16_16           values[4];
} d_env_field_cell;

typedef struct d_env_sample_s {
    d_env_field_id field_id;
    u16            model_id;
    q16_16         values[4];
} d_env_sample;

u16 d_env_sample_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_env_sample  *out_samples,
    u16            max_samples
);

/* Sample without applying interior volume overrides. */
u16 d_env_sample_exterior_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_env_sample  *out_samples,
    u16            max_samples
);

void d_env_tick(d_world *w, u32 ticks);

typedef struct d_env_model_vtable_s {
    u16 model_id;

    void (*init_chunk)(
        d_world          *w,
        d_chunk          *chunk,
        d_env_field_cell *cell,
        const d_tlv_blob *params
    );

    void (*compute_base)(
        const d_world    *w,
        const d_chunk    *chunk,
        d_env_field_cell *cell
    );

    void (*tick)(
        d_world          *w,
        d_chunk          *chunk,
        d_env_field_cell *cell,
        u32               ticks
    );
} d_env_model_vtable;

int d_env_register_model(const d_env_model_vtable *vt);

/* Reserved field ids for built-in atmosphere model. */
#define D_ENV_FIELD_PRESSURE        1
#define D_ENV_FIELD_TEMPERATURE     2
#define D_ENV_FIELD_GAS0_FRACTION   3
#define D_ENV_FIELD_GAS1_FRACTION   4
#define D_ENV_FIELD_HUMIDITY        5
#define D_ENV_FIELD_WIND_X          6
#define D_ENV_FIELD_WIND_Y          7

/* Built-in model id for default atmosphere. */
#define D_ENV_MODEL_ATMOSPHERE_DEFAULT 1

#ifdef __cplusplus
}
#endif

#endif /* D_ENV_FIELD_H */
