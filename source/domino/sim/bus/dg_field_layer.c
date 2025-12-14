#include <stdlib.h>
#include <string.h>

#include "sim/bus/dg_field_layer.h"

#define DG_FIELD_LAYER_MAX_RES 1024u

static u16 dg_field_layer_clamp_u16(u16 v, u16 lo, u16 hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static u32 dg_field_layer_index(const dg_field_layer *layer, u16 x, u16 y, u16 z, u32 comp) {
    u32 idx;
    u32 rx;
    u32 ry;
    u32 dim;

    rx = (u32)layer->res_x;
    ry = (u32)layer->res_y;
    dim = (u32)layer->dim;

    idx = (u32)z;
    idx = idx * ry + (u32)y;
    idx = idx * rx + (u32)x;
    idx = idx * dim + comp;
    return idx;
}

void dg_field_layer_init(dg_field_layer *layer) {
    if (!layer) {
        return;
    }
    memset(layer, 0, sizeof(*layer));
}

void dg_field_layer_free(dg_field_layer *layer) {
    if (!layer) {
        return;
    }
    if (layer->values) {
        free(layer->values);
    }
    dg_field_layer_init(layer);
}

int dg_field_layer_configure(
    dg_field_layer *layer,
    dg_domain_id    domain_id,
    dg_chunk_id     chunk_id,
    dg_type_id      field_type_id,
    u8              dim,
    u16             res_x,
    u16             res_y,
    u16             res_z
) {
    u64 grid_count64;
    u64 value_count64;
    u32 value_count;
    q16_16 *vals;

    if (!layer) {
        return -1;
    }
    if (dim == 0u) {
        return -2;
    }
    if (res_x == 0u || res_y == 0u || res_z == 0u) {
        return -3;
    }
    if (res_x > (u16)DG_FIELD_LAYER_MAX_RES ||
        res_y > (u16)DG_FIELD_LAYER_MAX_RES ||
        res_z > (u16)DG_FIELD_LAYER_MAX_RES) {
        return -4;
    }

    grid_count64 = (u64)res_x * (u64)res_y;
    grid_count64 = grid_count64 * (u64)res_z;
    value_count64 = grid_count64 * (u64)dim;
    if (value_count64 > (u64)0xFFFFFFFFu) {
        return -5;
    }
    value_count = (u32)value_count64;

    vals = (q16_16 *)malloc(sizeof(q16_16) * (size_t)value_count);
    if (!vals) {
        return -6;
    }
    memset(vals, 0, sizeof(q16_16) * (size_t)value_count);

    dg_field_layer_free(layer);

    layer->domain_id = domain_id;
    layer->chunk_id = chunk_id;
    layer->field_type_id = field_type_id;
    layer->dim = dim;
    layer->res_x = res_x;
    layer->res_y = res_y;
    layer->res_z = res_z;
    layer->values = vals;
    layer->value_count = value_count;
    return 0;
}

int dg_field_layer_set_cell(
    dg_field_layer *layer,
    u16             x,
    u16             y,
    u16             z,
    const q16_16   *in_values,
    u32             in_dim
) {
    u32 i;
    u32 dim;
    u32 idx0;

    if (!layer || !layer->values) {
        return -1;
    }
    dim = (u32)layer->dim;
    if (!in_values && in_dim != 0u) {
        return -2;
    }

    x = dg_field_layer_clamp_u16(x, 0u, (u16)(layer->res_x - 1u));
    y = dg_field_layer_clamp_u16(y, 0u, (u16)(layer->res_y - 1u));
    z = dg_field_layer_clamp_u16(z, 0u, (u16)(layer->res_z - 1u));

    idx0 = dg_field_layer_index(layer, x, y, z, 0u);
    for (i = 0u; i < dim; ++i) {
        q16_16 v = 0;
        if (i < in_dim) {
            v = in_values[i];
        }
        layer->values[idx0 + i] = v;
    }
    return 0;
}

int dg_field_layer_get_cell(
    const dg_field_layer *layer,
    u16                   x,
    u16                   y,
    u16                   z,
    q16_16               *out_values,
    u32                   out_dim
) {
    u32 i;
    u32 dim;
    u32 idx0;

    if (!layer || !layer->values || !out_values) {
        return -1;
    }
    dim = (u32)layer->dim;

    x = dg_field_layer_clamp_u16(x, 0u, (u16)(layer->res_x - 1u));
    y = dg_field_layer_clamp_u16(y, 0u, (u16)(layer->res_y - 1u));
    z = dg_field_layer_clamp_u16(z, 0u, (u16)(layer->res_z - 1u));

    idx0 = dg_field_layer_index(layer, x, y, z, 0u);
    for (i = 0u; i < out_dim; ++i) {
        out_values[i] = (i < dim) ? layer->values[idx0 + i] : 0;
    }
    return 0;
}

static q16_16 dg_field_layer_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static q16_16 dg_field_layer_saturate_q16_16_i64(i64 v) {
    if (v > (i64)0x7FFFFFFF) {
        return (q16_16)0x7FFFFFFF;
    }
    if (v < (i64)0x80000000) {
        return (q16_16)0x80000000;
    }
    return (q16_16)v;
}

int dg_field_layer_sample_trilinear(
    const dg_field_layer *layer,
    q16_16                x,
    q16_16                y,
    q16_16                z,
    q16_16               *out_values,
    u32                   out_dim
) {
    u32 d;
    u32 dim;
    u32 rx;
    u32 ry;
    u32 rz;
    q16_16 one;
    q16_16 max_x;
    q16_16 max_y;
    q16_16 max_z;
    i32 ix;
    i32 iy;
    i32 iz;
    u16 bx;
    u16 by;
    u16 bz;
    q16_16 fx;
    q16_16 fy;
    q16_16 fz;
    q16_16 wx0, wx1, wy0, wy1, wz0, wz1;

    if (!layer || !layer->values || !out_values) {
        return -1;
    }
    dim = (u32)layer->dim;
    if (out_dim < dim) {
        return -2;
    }

    rx = (u32)layer->res_x;
    ry = (u32)layer->res_y;
    rz = (u32)layer->res_z;
    if (rx == 0u || ry == 0u || rz == 0u) {
        return -3;
    }

    one = (q16_16)(1L << Q16_16_FRAC_BITS);
    max_x = (q16_16)(((i32)(layer->res_x - 1u)) << Q16_16_FRAC_BITS);
    max_y = (q16_16)(((i32)(layer->res_y - 1u)) << Q16_16_FRAC_BITS);
    max_z = (q16_16)(((i32)(layer->res_z - 1u)) << Q16_16_FRAC_BITS);

    x = dg_field_layer_clamp_q16_16(x, 0, max_x);
    y = dg_field_layer_clamp_q16_16(y, 0, max_y);
    z = dg_field_layer_clamp_q16_16(z, 0, max_z);

    /* Base indices + fractions. If axis has only one point, force base=0, frac=0. */
    if (rx < 2u) {
        bx = 0u;
        fx = 0;
    } else {
        ix = (i32)(x >> Q16_16_FRAC_BITS);
        if ((u32)ix >= rx - 1u) {
            bx = (u16)(rx - 2u);
            fx = one;
        } else {
            bx = (u16)ix;
            fx = (q16_16)(x - (q16_16)(((i32)bx) << Q16_16_FRAC_BITS));
        }
    }

    if (ry < 2u) {
        by = 0u;
        fy = 0;
    } else {
        iy = (i32)(y >> Q16_16_FRAC_BITS);
        if ((u32)iy >= ry - 1u) {
            by = (u16)(ry - 2u);
            fy = one;
        } else {
            by = (u16)iy;
            fy = (q16_16)(y - (q16_16)(((i32)by) << Q16_16_FRAC_BITS));
        }
    }

    if (rz < 2u) {
        bz = 0u;
        fz = 0;
    } else {
        iz = (i32)(z >> Q16_16_FRAC_BITS);
        if ((u32)iz >= rz - 1u) {
            bz = (u16)(rz - 2u);
            fz = one;
        } else {
            bz = (u16)iz;
            fz = (q16_16)(z - (q16_16)(((i32)bz) << Q16_16_FRAC_BITS));
        }
    }

    wx0 = (q16_16)(one - fx);
    wx1 = fx;
    wy0 = (q16_16)(one - fy);
    wy1 = fy;
    wz0 = (q16_16)(one - fz);
    wz1 = fz;

    for (d = 0u; d < dim; ++d) {
        i64 acc = 0;
        u16 x0 = bx;
        u16 y0 = by;
        u16 z0 = bz;
        u16 x1 = (u16)((rx < 2u) ? bx : (bx + 1u));
        u16 y1 = (u16)((ry < 2u) ? by : (by + 1u));
        u16 z1 = (u16)((rz < 2u) ? bz : (bz + 1u));

        /* Fixed neighbor order:
         * (0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1)
         */
        {
            i64 w;
            q16_16 v;

            w = (i64)wx0 * (i64)wy0 * (i64)wz0;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x0, y0, z0, d)];
            acc += (i64)v * w;

            w = (i64)wx1 * (i64)wy0 * (i64)wz0;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x1, y0, z0, d)];
            acc += (i64)v * w;

            w = (i64)wx0 * (i64)wy1 * (i64)wz0;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x0, y1, z0, d)];
            acc += (i64)v * w;

            w = (i64)wx1 * (i64)wy1 * (i64)wz0;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x1, y1, z0, d)];
            acc += (i64)v * w;

            w = (i64)wx0 * (i64)wy0 * (i64)wz1;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x0, y0, z1, d)];
            acc += (i64)v * w;

            w = (i64)wx1 * (i64)wy0 * (i64)wz1;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x1, y0, z1, d)];
            acc += (i64)v * w;

            w = (i64)wx0 * (i64)wy1 * (i64)wz1;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x0, y1, z1, d)];
            acc += (i64)v * w;

            w = (i64)wx1 * (i64)wy1 * (i64)wz1;
            w >>= 32;
            v = layer->values[dg_field_layer_index(layer, x1, y1, z1, d)];
            acc += (i64)v * w;
        }

        out_values[d] = dg_field_layer_saturate_q16_16_i64(acc >> Q16_16_FRAC_BITS);
    }

    for (; d < out_dim; ++d) {
        out_values[d] = 0;
    }

    return 0;
}

