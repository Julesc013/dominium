/*
FILE: source/domino/res/d_res_model_strata.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/d_res_model_strata
RESPONSIBILITY: Implements `d_res_model_strata`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "domino/core/fixed.h"
#include "domino/core/rng.h"
#include "content/d_content_extra.h"
#include "res/d_res_model.h"
#include "res/d_res.h"

typedef struct strata_params_s {
    q16_16 mean_grade;
    q16_16 mean_quantity;
    q16_16 noise_scale;
    q16_16 regen_rate;
} strata_params;

static int strata_next_tlv(const d_tlv_blob *blob, u32 *offset, u32 *tag, d_tlv_blob *payload) {
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1;
    }
    remaining = blob->len - *offset;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

static q16_16 strata_read_q16_16(const d_tlv_blob *payload, q16_16 def) {
    q16_16 out = def;
    if (!payload || payload->len != 4u || payload->ptr == (unsigned char *)0) {
        return def;
    }
    memcpy(&out, payload->ptr, sizeof(q16_16));
    return out;
}

static void strata_parse_params(const d_tlv_blob *blob, strata_params *out) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    strata_params tmp;

    if (!out) {
        return;
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.mean_grade = d_q16_16_from_int(1);
    tmp.mean_quantity = d_q16_16_from_int(0);
    tmp.noise_scale = d_q16_16_from_int(0);
    tmp.regen_rate = d_q16_16_from_int(0);

    if (!blob || !blob->ptr || blob->len == 0u) {
        *out = tmp;
        return;
    }

    while (1) {
        int rc = strata_next_tlv(blob, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            break;
        }
        switch (tag) {
        case D_TLV_RES_STRATA_MEAN_GRADE:
            tmp.mean_grade = strata_read_q16_16(&payload, tmp.mean_grade);
            break;
        case D_TLV_RES_STRATA_MEAN_QUANTITY:
            tmp.mean_quantity = strata_read_q16_16(&payload, tmp.mean_quantity);
            break;
        case D_TLV_RES_STRATA_NOISE_SCALE:
            tmp.noise_scale = strata_read_q16_16(&payload, tmp.noise_scale);
            break;
        case D_TLV_RES_STRATA_REGEN_RATE:
            tmp.regen_rate = strata_read_q16_16(&payload, tmp.regen_rate);
            break;
        default:
            break;
        }
    }
    *out = tmp;
}

static u32 strata_hash_coords(u64 seed, i32 cx, i32 cy, d_deposit_proto_id proto_id,
                              q32_32 x, q32_32 y, q32_32 z) {
    u32 h = (u32)(seed ^ (seed >> 32));
    h ^= (u32)proto_id + 0x9e3779b9u + (h << 6) + (h >> 2);
    h ^= (u32)cx + 0x9e3779b9u + (h << 6) + (h >> 2);
    h ^= (u32)cy + 0x9e3779b9u + (h << 6) + (h >> 2);
    h ^= (u32)(cx * 31 + cy * 17 + (i32)proto_id);
    h ^= (u32)(x >> Q32_32_FRAC_BITS) + 0x9e3779b9u + (h << 6) + (h >> 2);
    h ^= (u32)(y >> Q32_32_FRAC_BITS) + 0x9e3779b9u + (h << 6) + (h >> 2);
    h ^= (u32)(z >> Q32_32_FRAC_BITS) + 0x9e3779b9u + (h << 6) + (h >> 2);
    return h;
}

static q16_16 strata_noise_q16(u32 hash) {
    /* Map hash to [-1, 1] in q16_16. */
    i32 v = (i32)(hash & 0xFFFFu);
    v = (v & 0x7FFF) - 0x4000; /* range approx [-16384, 16383] */
    return (q16_16)((i64)v << (Q16_16_FRAC_BITS - 14));
}

static q16_16 strata_compute_quantity(d_world *w,
                                      d_chunk *chunk,
                                      const dres_channel_cell *cell,
                                      const strata_params *params,
                                      q32_32 x,
                                      q32_32 y,
                                      q32_32 z) {
    q16_16 noise_val;
    q16_16 base;
    q16_16 mult_noise;
    q16_16 multiplier;
    q16_16 qty;
    u32 hash = strata_hash_coords(w ? w->worldgen_seed : 0u,
                                  chunk ? chunk->cx : 0,
                                  chunk ? chunk->cy : 0,
                                  cell ? cell->proto_id : 0u,
                                  x, y, z);
    (void)cell;

    noise_val = strata_noise_q16(hash);
    mult_noise = d_q16_16_mul(params->noise_scale, noise_val);
    multiplier = d_q16_16_add(d_q16_16_from_int(1), mult_noise);
    base = d_q16_16_mul(params->mean_quantity, params->mean_grade);
    qty = d_q16_16_mul(base, multiplier);
    if (qty < 0) {
        qty = 0;
    }
    return qty;
}

static void strata_init_chunk(
    d_world           *w,
    d_chunk           *chunk,
    dres_channel_cell *cell
) {
    (void)w;
    (void)chunk;
    if (!cell) {
        return;
    }
    cell->initialized = 0u;
}

static void strata_compute_base(
    d_world           *w,
    const d_chunk     *chunk,
    dres_channel_cell *cell,
    q32_32             x,
    q32_32             y,
    q32_32             z
) {
    strata_params params;
    if (!cell) {
        return;
    }

    strata_parse_params(&cell->model_params, &params);
    if (!cell->initialized) {
        cell->values[0] = strata_compute_quantity(w, (d_chunk *)chunk, cell, &params, x, y, z);
        cell->initialized = 1u;
    }
    if (cell->values[0] < 0) {
        cell->values[0] = 0;
    }
}

static void strata_apply_delta(
    d_world           *w,
    d_chunk           *chunk,
    dres_channel_cell *cell,
    const q16_16      *delta_values,
    u32                seed_context
) {
    u16 i;
    (void)w;
    (void)chunk;
    (void)seed_context;
    if (!cell || !delta_values) {
        return;
    }
    for (i = 0u; i < DRES_VALUE_MAX; ++i) {
        q16_16 v = d_q16_16_add(cell->values[i], delta_values[i]);
        if (v < 0) {
            v = 0;
        }
        cell->values[i] = v;
    }
}

static void strata_tick(
    d_world           *w,
    d_chunk           *chunk,
    dres_channel_cell *cell,
    u32                ticks
) {
    strata_params params;
    q16_16 regen;
    (void)w;
    (void)chunk;
    if (!cell || ticks == 0u) {
        return;
    }
    strata_parse_params(&cell->model_params, &params);
    regen = params.regen_rate;
    if (regen != 0) {
        i64 delta = ((i64)regen) * (i64)ticks;
        q16_16 add = (q16_16)delta;
        cell->values[0] = d_q16_16_add(cell->values[0], add);
        if (cell->values[0] < 0) {
            cell->values[0] = 0;
        }
    }
}

static const dres_model_vtable g_strata_vt = {
    DRES_MODEL_STRATA_SOLID,
    strata_init_chunk,
    strata_compute_base,
    strata_apply_delta,
    strata_tick
};

void dres_register_strata_solid_model(void) {
    dres_register_model(&g_strata_vt);
}
