/* Deterministic field layer storage (C89).
 *
 * A field layer is the chunk-local storage backing a single (domain, chunk,
 * field_type_id) triple. Values are fixed-point only.
 */
#ifndef DG_FIELD_LAYER_H
#define DG_FIELD_LAYER_H

#include "domino/core/fixed.h"
#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_field_layer {
    dg_domain_id domain_id;
    dg_chunk_id  chunk_id;
    dg_type_id   field_type_id;

    u8  dim;   /* 1..N */
    u16 res_x; /* grid points per axis (>= 2 recommended) */
    u16 res_y;
    u16 res_z;

    q16_16 *values;   /* length = res_x*res_y*res_z*dim */
    u32     value_count;
} dg_field_layer;

void dg_field_layer_init(dg_field_layer *layer);
void dg_field_layer_free(dg_field_layer *layer);

int dg_field_layer_configure(
    dg_field_layer *layer,
    dg_domain_id    domain_id,
    dg_chunk_id     chunk_id,
    dg_type_id      field_type_id,
    u8              dim,
    u16             res_x,
    u16             res_y,
    u16             res_z
);

int dg_field_layer_set_cell(
    dg_field_layer *layer,
    u16             x,
    u16             y,
    u16             z,
    const q16_16   *in_values,
    u32             in_dim
);

int dg_field_layer_get_cell(
    const dg_field_layer *layer,
    u16                   x,
    u16                   y,
    u16                   z,
    q16_16               *out_values,
    u32                   out_dim
);

/* Deterministic trilinear sampling in chunk-local grid coordinates (Q16.16).
 * x/y/z are in "grid point" units: integer part selects a point, fractional
 * part interpolates toward +1 neighbors.
 */
int dg_field_layer_sample_trilinear(
    const dg_field_layer *layer,
    q16_16                x,
    q16_16                y,
    q16_16                z,
    q16_16               *out_values,
    u32                   out_dim
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FIELD_LAYER_H */

