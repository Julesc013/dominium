/*
FILE: source/domino/hydro/d_hydro.c
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
#include <stdlib.h>
#include <string.h>

#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "world/d_worldgen.h"
#include "hydro/d_hydro.h"
#include "res/d_res.h"

#define DHYDRO_MAX_MODELS         8u
#define DHYDRO_MAX_CHUNK_ENTRIES 256u
#define DHYDRO_GRID_RES          16u
#define DHYDRO_GRID_CELLS        (DHYDRO_GRID_RES * DHYDRO_GRID_RES)

typedef struct dhydro_chunk_entry_s {
    d_world     *world;
    d_chunk     *chunk;
    d_hydro_cell cells[DHYDRO_GRID_CELLS];
} dhydro_chunk_entry;

static d_hydro_model_vtable g_hydro_models[DHYDRO_MAX_MODELS];
static u32 g_hydro_model_count = 0u;

static dhydro_chunk_entry g_hydro_chunks[DHYDRO_MAX_CHUNK_ENTRIES];
static u32 g_hydro_chunk_count = 0u;

static int g_hydro_registered = 0;

static const d_hydro_model_vtable *dhydro_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_hydro_model_count; ++i) {
        if (g_hydro_models[i].model_id == model_id) {
            return &g_hydro_models[i];
        }
    }
    return (const d_hydro_model_vtable *)0;
}

int d_hydro_register_model(const d_hydro_model_vtable *vt) {
    d_model_desc desc;
    u32 i;
    if (!vt || vt->model_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_hydro_model_count; ++i) {
        if (g_hydro_models[i].model_id == vt->model_id) {
            return -2;
        }
    }
    if (g_hydro_model_count >= DHYDRO_MAX_MODELS) {
        return -3;
    }

    g_hydro_models[g_hydro_model_count] = *vt;

    desc.family_id = D_MODEL_FAMILY_HYDRO;
    desc.model_id = vt->model_id;
    desc.name = "hydro_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_hydro_models[g_hydro_model_count];

    if (d_model_register(&desc) != 0) {
        return -4;
    }

    g_hydro_model_count += 1u;
    return 0;
}

static dhydro_chunk_entry *dhydro_find_entry(d_world *w, d_chunk *chunk) {
    u32 i;
    if (!w || !chunk) {
        return (dhydro_chunk_entry *)0;
    }
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        if (g_hydro_chunks[i].world == w && g_hydro_chunks[i].chunk == chunk) {
            return &g_hydro_chunks[i];
        }
    }
    return (dhydro_chunk_entry *)0;
}

static dhydro_chunk_entry *dhydro_ensure_entry(d_world *w, d_chunk *chunk) {
    dhydro_chunk_entry *entry;
    if (!w || !chunk) {
        return (dhydro_chunk_entry *)0;
    }
    entry = dhydro_find_entry(w, chunk);
    if (entry) {
        return entry;
    }
    if (g_hydro_chunk_count >= DHYDRO_MAX_CHUNK_ENTRIES) {
        return (dhydro_chunk_entry *)0;
    }
    entry = &g_hydro_chunks[g_hydro_chunk_count];
    memset(entry, 0, sizeof(*entry));
    entry->world = w;
    entry->chunk = chunk;
    g_hydro_chunk_count += 1u;
    return entry;
}

static void dhydro_init_chunk_default(d_world *w, d_chunk *chunk, d_tlv_blob *params) {
    dhydro_chunk_entry *entry;
    u32 i;
    (void)params;
    entry = dhydro_ensure_entry(w, chunk);
    if (!entry) {
        return;
    }
    for (i = 0u; i < DHYDRO_GRID_CELLS; ++i) {
        entry->cells[i].surface_height = 0;
        entry->cells[i].depth = 0;
        entry->cells[i].velocity_x = 0;
        entry->cells[i].velocity_y = 0;
        entry->cells[i].flags = 0;
    }
}

static q16_16 dhydro_q16_from_i64_clamp(i64 v) {
    if (v > (i64)0x7FFFFFFF) {
        return (q16_16)0x7FFFFFFF;
    }
    if (v < (i64)0x80000000) {
        return (q16_16)0x80000000;
    }
    return (q16_16)v;
}

static q16_16 g_surface_snap[DHYDRO_MAX_CHUNK_ENTRIES * DHYDRO_GRID_CELLS];
static i64   g_surface_delta[DHYDRO_MAX_CHUNK_ENTRIES * DHYDRO_GRID_CELLS];
static i64   g_surface_velx[DHYDRO_MAX_CHUNK_ENTRIES * DHYDRO_GRID_CELLS];
static i64   g_surface_vely[DHYDRO_MAX_CHUNK_ENTRIES * DHYDRO_GRID_CELLS];

static void dhydro_surface_water_reset_buffers(d_world *w) {
    u32 i;
    if (!w) {
        return;
    }
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        dhydro_chunk_entry *entry = &g_hydro_chunks[i];
        u32 base;
        u32 k;
        if (entry->world != w) {
            continue;
        }
        base = i * DHYDRO_GRID_CELLS;
        for (k = 0u; k < DHYDRO_GRID_CELLS; ++k) {
            q16_16 d = entry->cells[k].depth;
            if (d < 0) {
                d = 0;
            }
            g_surface_snap[base + k] = d;
            g_surface_delta[base + k] = 0;
            g_surface_velx[base + k] = 0;
            g_surface_vely[base + k] = 0;
        }
    }
}

static void dhydro_surface_water_apply_edge(
    u32 a_entry_index,
    u32 a_cell_index,
    u32 b_entry_index,
    u32 b_cell_index,
    int axis /* 0 = Y, 1 = X */
) {
    u32 a_off;
    u32 b_off;
    q16_16 ha;
    q16_16 hb;
    i64 diff;
    i64 transfer_i64;
    q16_16 transfer;

    if (a_entry_index >= DHYDRO_MAX_CHUNK_ENTRIES || b_entry_index >= DHYDRO_MAX_CHUNK_ENTRIES) {
        return;
    }
    if (a_cell_index >= DHYDRO_GRID_CELLS || b_cell_index >= DHYDRO_GRID_CELLS) {
        return;
    }

    a_off = a_entry_index * DHYDRO_GRID_CELLS + a_cell_index;
    b_off = b_entry_index * DHYDRO_GRID_CELLS + b_cell_index;

    ha = g_surface_snap[a_off];
    hb = g_surface_snap[b_off];
    diff = (i64)ha - (i64)hb;
    transfer_i64 = diff >> 3; /* stable, limited per tick */
    transfer = dhydro_q16_from_i64_clamp(transfer_i64);

    /* Clamp by available water at the source. */
    if (transfer > 0) {
        if (transfer > ha) {
            transfer = ha;
        }
    } else if (transfer < 0) {
        q16_16 need = (q16_16)(-transfer);
        if (need > hb) {
            transfer = (q16_16)(-hb);
        }
    } else {
        return;
    }

    if (transfer == 0) {
        return;
    }

    g_surface_delta[a_off] -= (i64)transfer;
    g_surface_delta[b_off] += (i64)transfer;

    if (axis == 1) {
        g_surface_velx[a_off] += (i64)transfer;
        g_surface_velx[b_off] += (i64)transfer;
    } else {
        g_surface_vely[a_off] += (i64)transfer;
        g_surface_vely[b_off] += (i64)transfer;
    }
}

static void dhydro_surface_water_compute_flows(d_world *w) {
    u32 i;
    if (!w) {
        return;
    }
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        dhydro_chunk_entry *entry = &g_hydro_chunks[i];
        u32 x, y;
        if (entry->world != w || !entry->chunk) {
            continue;
        }
        for (y = 0u; y < DHYDRO_GRID_RES; ++y) {
            for (x = 0u; x < DHYDRO_GRID_RES; ++x) {
                u32 a_cell = y * DHYDRO_GRID_RES + x;

                /* East edge (+X chunk if boundary). */
                if (x + 1u < DHYDRO_GRID_RES) {
                    u32 b_cell = y * DHYDRO_GRID_RES + (x + 1u);
                    dhydro_surface_water_apply_edge(i, a_cell, i, b_cell, 1);
                } else {
                    d_chunk *nbr_chunk = d_world_find_chunk(w, entry->chunk->cx + 1, entry->chunk->cy);
                    dhydro_chunk_entry *nbr = nbr_chunk ? dhydro_find_entry(w, nbr_chunk) : (dhydro_chunk_entry *)0;
                    if (nbr) {
                        u32 j = (u32)(nbr - g_hydro_chunks);
                        u32 b_cell = y * DHYDRO_GRID_RES + 0u;
                        dhydro_surface_water_apply_edge(i, a_cell, j, b_cell, 1);
                    }
                }

                /* North edge (+Y chunk if boundary). */
                if (y + 1u < DHYDRO_GRID_RES) {
                    u32 b_cell = (y + 1u) * DHYDRO_GRID_RES + x;
                    dhydro_surface_water_apply_edge(i, a_cell, i, b_cell, 0);
                } else {
                    d_chunk *nbr_chunk = d_world_find_chunk(w, entry->chunk->cx, entry->chunk->cy + 1);
                    dhydro_chunk_entry *nbr = nbr_chunk ? dhydro_find_entry(w, nbr_chunk) : (dhydro_chunk_entry *)0;
                    if (nbr) {
                        u32 j = (u32)(nbr - g_hydro_chunks);
                        u32 b_cell = 0u * DHYDRO_GRID_RES + x;
                        dhydro_surface_water_apply_edge(i, a_cell, j, b_cell, 0);
                    }
                }
            }
        }
    }
}

static void dhydro_surface_water_apply_state(d_world *w) {
    u32 i;
    if (!w) {
        return;
    }
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        dhydro_chunk_entry *entry = &g_hydro_chunks[i];
        u32 base;
        u32 k;
        if (entry->world != w) {
            continue;
        }
        base = i * DHYDRO_GRID_CELLS;
        for (k = 0u; k < DHYDRO_GRID_CELLS; ++k) {
            i64 depth_i64 = (i64)g_surface_snap[base + k] + g_surface_delta[base + k];
            q16_16 depth;
            if (depth_i64 < 0) {
                depth_i64 = 0;
            }
            depth = dhydro_q16_from_i64_clamp(depth_i64);
            entry->cells[k].depth = depth;
            entry->cells[k].surface_height = depth;
            entry->cells[k].velocity_x = dhydro_q16_from_i64_clamp(g_surface_velx[base + k]);
            entry->cells[k].velocity_y = dhydro_q16_from_i64_clamp(g_surface_vely[base + k]);
        }
    }
}

static void dhydro_surface_water_exchange_res(d_world *w, u32 tick_seed) {
    u32 i;
    if (!w) {
        return;
    }
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        dhydro_chunk_entry *entry = &g_hydro_chunks[i];
        dres_sample samples[4];
        u16 count;
        q32_32 sx;
        q32_32 sy;
        q32_32 sz;
        u16 si;

        if (entry->world != w || !entry->chunk) {
            continue;
        }

        count = 4u;
        sx = ((q32_32)entry->chunk->cx) << Q32_32_FRAC_BITS;
        sy = ((q32_32)entry->chunk->cy) << Q32_32_FRAC_BITS;
        sz = 0;

        if (dres_sample_at(w, sx, sy, sz, 0u, samples, &count) != 0) {
            continue;
        }
        if (count == 0u) {
            continue;
        }

        for (si = 0u; si < count; ++si) {
            if ((samples[si].tags & D_TAG_MATERIAL_FLUID) != 0u) {
                i64 surface_total = 0;
                i64 reservoir_total;
                i64 diff;
                q16_16 delta[DRES_VALUE_MAX];
                u16 k;
                u32 cell_idx;
                q16_16 target;
                q16_16 remaining;
                i32 cells_left;

                for (cell_idx = 0u; cell_idx < DHYDRO_GRID_CELLS; ++cell_idx) {
                    surface_total += (i64)entry->cells[cell_idx].depth;
                }
                reservoir_total = (i64)samples[si].value[0];
                diff = reservoir_total - surface_total;

                if (diff == 0) {
                    break;
                }

                for (k = 0u; k < DRES_VALUE_MAX; ++k) {
                    delta[k] = 0;
                }

                /* Move a small fraction of the difference each tick. */
                if (diff > 0) {
                    i64 want_i64 = diff >> 6;
                    if (want_i64 > reservoir_total) {
                        want_i64 = reservoir_total;
                    }
                    target = dhydro_q16_from_i64_clamp(want_i64);
                    if (target <= 0) {
                        break;
                    }
                    remaining = target;
                    cells_left = (i32)DHYDRO_GRID_CELLS;
                    for (cell_idx = 0u; cell_idx < DHYDRO_GRID_CELLS; ++cell_idx) {
                        q16_16 per;
                        q16_16 add;
                        if (remaining <= 0 || cells_left <= 0) {
                            break;
                        }
                        per = d_q16_16_div(remaining, d_q16_16_from_int(cells_left));
                        add = per;
                        entry->cells[cell_idx].depth = d_q16_16_add(entry->cells[cell_idx].depth, add);
                        entry->cells[cell_idx].surface_height = entry->cells[cell_idx].depth;
                        remaining = d_q16_16_sub(remaining, add);
                        cells_left -= 1;
                    }
                    delta[0] = (q16_16)(-(target - remaining));
                    if (delta[0] != 0) {
                        (void)dres_apply_delta(w, &samples[si], delta, tick_seed);
                    }
                } else {
                    i64 want_i64 = (-diff) >> 6;
                    if (want_i64 > surface_total) {
                        want_i64 = surface_total;
                    }
                    target = dhydro_q16_from_i64_clamp(want_i64);
                    if (target <= 0) {
                        break;
                    }
                    remaining = target;
                    cells_left = (i32)DHYDRO_GRID_CELLS;
                    for (cell_idx = 0u; cell_idx < DHYDRO_GRID_CELLS; ++cell_idx) {
                        q16_16 per;
                        q16_16 take;
                        q16_16 d;
                        if (remaining <= 0 || cells_left <= 0) {
                            break;
                        }
                        per = d_q16_16_div(remaining, d_q16_16_from_int(cells_left));
                        d = entry->cells[cell_idx].depth;
                        take = per;
                        if (take > d) {
                            take = d;
                        }
                        entry->cells[cell_idx].depth = d_q16_16_sub(d, take);
                        entry->cells[cell_idx].surface_height = entry->cells[cell_idx].depth;
                        remaining = d_q16_16_sub(remaining, take);
                        cells_left -= 1;
                    }
                    delta[0] = (q16_16)(target - remaining);
                    if (delta[0] != 0) {
                        (void)dres_apply_delta(w, &samples[si], delta, tick_seed);
                    }
                }

                break;
            }
        }
    }
}

static void dhydro_tick_surface_water_world(d_world *w, u32 ticks) {
    u32 t;
    if (!w || ticks == 0u) {
        return;
    }
    for (t = 0u; t < ticks; ++t) {
        u32 tick_seed = (u32)(w->tick_count + t);
        dhydro_surface_water_reset_buffers(w);
        dhydro_surface_water_compute_flows(w);
        dhydro_surface_water_apply_state(w);
        dhydro_surface_water_exchange_res(w, tick_seed);
    }
}

static void dhydro_tick_surface_water(d_world *w, d_chunk *chunk, u32 ticks) {
    (void)w;
    (void)chunk;
    (void)ticks;
    /* Handled by the subsystem-level deterministic world tick. */
}

static void dhydro_sample_surface_water(
    const d_world *w,
    const d_chunk *chunk,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_hydro_cell  *out_cell
) {
    dhydro_chunk_entry *entry;
    u32 fx;
    u32 fy;
    u32 lx;
    u32 ly;
    u32 idx;
    (void)z;

    if (!w || !chunk || !out_cell) {
        return;
    }
    entry = dhydro_find_entry((d_world *)w, (d_chunk *)chunk);
    if (!entry) {
        memset(out_cell, 0, sizeof(*out_cell));
        return;
    }

    fx = (u32)x;
    fy = (u32)y;
    lx = (fx >> 28) & 0xFu;
    ly = (fy >> 28) & 0xFu;
    idx = ly * DHYDRO_GRID_RES + lx;
    if (idx >= DHYDRO_GRID_CELLS) {
        idx = 0u;
    }
    *out_cell = entry->cells[idx];
}

static const d_hydro_model_vtable g_surface_water_vt = {
    D_HYDRO_MODEL_SURFACE_WATER,
    dhydro_init_chunk_default,
    dhydro_tick_surface_water,
    dhydro_sample_surface_water
};

static void dhydro_worldgen_populate(struct d_world *w, struct d_chunk *chunk) {
    const d_hydro_model_vtable *vt;
    d_tlv_blob params;
    if (!w || !chunk) {
        return;
    }
    params.ptr = (unsigned char *)0;
    params.len = 0u;
    vt = dhydro_model_lookup(D_HYDRO_MODEL_SURFACE_WATER);
    if (vt && vt->init_chunk) {
        vt->init_chunk((d_world *)w, (d_chunk *)chunk, &params);
    }
}

void d_hydro_tick(d_world *w, u32 ticks) {
    if (!w || ticks == 0u) {
        return;
    }
    dhydro_tick_surface_water_world(w, ticks);
}

int d_hydro_sample_at(
    d_world      *w,
    q32_32        x,
    q32_32        y,
    q32_32        z,
    d_hydro_cell *out_cell
) {
    d_chunk *chunk;
    const d_hydro_model_vtable *vt;
    if (!w || !out_cell) {
        return -1;
    }
    chunk = d_world_find_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    if (!chunk) {
        chunk = d_world_get_or_create_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    }
    if (!chunk) {
        memset(out_cell, 0, sizeof(*out_cell));
        return 0;
    }
    if (!dhydro_find_entry(w, chunk)) {
        d_tlv_blob params;
        params.ptr = (unsigned char *)0;
        params.len = 0u;
        vt = dhydro_model_lookup(D_HYDRO_MODEL_SURFACE_WATER);
        if (vt && vt->init_chunk) {
            vt->init_chunk(w, chunk, &params);
        }
    }
    vt = dhydro_model_lookup(D_HYDRO_MODEL_SURFACE_WATER);
    if (vt && vt->sample) {
        vt->sample((const d_world *)w, (const d_chunk *)chunk, x, y, z, out_cell);
        return 0;
    }
    memset(out_cell, 0, sizeof(*out_cell));
    return 0;
}

static int dhydro_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    dhydro_chunk_entry *entry;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;
    (void)w;

    if (!out) {
        return -1;
    }
    entry = dhydro_find_entry(w, chunk);
    if (!entry) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total = 4u + (DHYDRO_GRID_CELLS * (sizeof(q16_16) * 5u));
    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    {
        u32 cell_count = DHYDRO_GRID_CELLS;
        memcpy(dst, &cell_count, sizeof(u32));
        dst += 4u;
    }

    for (i = 0u; i < DHYDRO_GRID_CELLS; ++i) {
        memcpy(dst, &entry->cells[i].surface_height, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &entry->cells[i].depth, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &entry->cells[i].velocity_x, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &entry->cells[i].velocity_y, sizeof(q16_16)); dst += sizeof(q16_16);
        memcpy(dst, &entry->cells[i].flags, sizeof(q16_16)); dst += sizeof(q16_16);
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int dhydro_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    dhydro_chunk_entry *entry;
    const unsigned char *ptr;
    u32 remaining;
    u32 cell_count;
    u32 i;

    if (!w || !chunk || !in) {
        return -1;
    }
    if (in->len == 0u) {
        return 0;
    }
    if (!in->ptr || in->len < 4u) {
        return -1;
    }

    ptr = in->ptr;
    remaining = in->len;
    memcpy(&cell_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;
    if (cell_count != DHYDRO_GRID_CELLS) {
        return -1;
    }
    if (remaining < DHYDRO_GRID_CELLS * (sizeof(q16_16) * 5u)) {
        return -1;
    }

    entry = dhydro_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }

    for (i = 0u; i < DHYDRO_GRID_CELLS; ++i) {
        memcpy(&entry->cells[i].surface_height, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&entry->cells[i].depth, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&entry->cells[i].velocity_x, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&entry->cells[i].velocity_y, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&entry->cells[i].flags, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
    }
    return 0;
}

static int dhydro_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dhydro_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void dhydro_init_instance_subsys(d_world *w) {
    u32 i;
    u32 dst = 0u;
    for (i = 0u; i < g_hydro_chunk_count; ++i) {
        if (g_hydro_chunks[i].world == w) {
            memset(&g_hydro_chunks[i], 0, sizeof(g_hydro_chunks[i]));
        } else {
            if (dst != i) {
                g_hydro_chunks[dst] = g_hydro_chunks[i];
            }
            dst += 1u;
        }
    }
    g_hydro_chunk_count = dst;
}

static void dhydro_register_models(void) {
    d_hydro_register_model(&g_surface_water_vt);
    {
        static const d_worldgen_provider prov = {
            3u,
            "hydro_default_provider",
            (const d_worldgen_provider_id *)0,
            dhydro_worldgen_populate
        };
        d_worldgen_register(&prov);
    }
}

static void dhydro_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_hydro_subsystem = {
    D_SUBSYS_HYDRO,
    "hydro",
    1u,
    dhydro_register_models,
    dhydro_load_protos,
    dhydro_init_instance_subsys,
    d_hydro_tick,
    dhydro_save_chunk,
    dhydro_load_chunk,
    dhydro_save_instance,
    dhydro_load_instance
};

void d_hydro_init(void) {
    if (g_hydro_registered) {
        return;
    }
    if (d_subsystem_register(&g_hydro_subsystem) == 0) {
        g_hydro_registered = 1;
    }
}
