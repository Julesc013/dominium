/* Resource subsystem core types (C89). */
#ifndef D_RES_H
#define D_RES_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "content/d_content.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DRES_VALUE_MAX 8

typedef struct dres_channel_desc {
    u16 channel_id;      /* stable ID, data-driven from deposit/material protos */
    u16 model_family;    /* usually D_MODEL_FAMILY_RES */
    u16 model_id;        /* which resource model handles this channel */
    u16 flags;           /* bit flags: e.g. SURFACE, UNDERGROUND, REGENERATES, etc. */
} dres_channel_desc;

typedef struct dres_channel_cell {
    dres_channel_desc desc;
    d_content_tag     tags;
    d_deposit_proto_id proto_id;
    d_material_id     material_id;
    d_tlv_blob        model_params;
    u8                initialized;
    q16_16            values[DRES_VALUE_MAX];
    q16_16            deltas[DRES_VALUE_MAX]; /* base+delta for sample; -inf or sentinel for none */
} dres_channel_cell;

/* Sample result – resolved values at position. */
typedef struct dres_sample {
    u16                channel_id;
    u16                model_family;
    u16                model_id;
    u16                _pad;
    const d_chunk     *chunk;
    q32_32             pos_x;
    q32_32             pos_y;
    q32_32             pos_z;
    d_deposit_proto_id proto_id;
    d_content_tag      tags;
    q16_16             value[DRES_VALUE_MAX];
    /* Optionally: link to deposit proto or extra TLV if needed later. */
} dres_sample;

/* Sample resource channels at world-space coordinates. */
int dres_sample_at(
    d_world      *w,
    q32_32        x,
    q32_32        y,
    q32_32        z,
    u16           channel_mask,   /* bitmask or filter; for now may be unused */
    dres_sample  *out_samples,
    u16          *in_out_count    /* in: max, out: actual count */
);

/* Apply a delta to a previously sampled channel. */
int dres_apply_delta(
    d_world            *w,
    const dres_sample  *sample,
    const q16_16       *delta_values,
    u32                 seed_context
);

/* Called from worldgen providers to initialize per-chunk resource state. */
int dres_init_chunk(
    d_world *w,
    d_chunk *chunk
);

/* Initialization hook for subsystem registration. */
void d_res_init(void);
int d_res_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_RES_H */
