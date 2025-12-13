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
