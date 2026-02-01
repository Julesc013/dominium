/*
FILE: source/domino/world/d_litho.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_litho
RESPONSIBILITY: Defines internal contract for `d_litho`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Lithosphere / terrain layers (C89). */
#ifndef D_LITHO_H
#define D_LITHO_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

#define D_LITHO_MAX_LAYERS 8u
#define D_LITHO_GRID_RES   16u

typedef struct d_world_layer_s {
    d_material_id material_id;
    q16_16        thickness;
} d_world_layer;

typedef struct d_world_layers_s {
    u16           layer_count;
    d_world_layer layers[D_LITHO_MAX_LAYERS];
} d_world_layers;

/* Sample layers under a (x,y) column; returns 0 on success. */
int d_litho_layers_at(
    d_world        *w,
    q32_32          x,
    q32_32          y,
    d_world_layers *out_layers
);

/* Subsystem hook */
void d_litho_init(void);
int d_litho_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_LITHO_H */
