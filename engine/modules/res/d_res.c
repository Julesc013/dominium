/*
FILE: source/domino/res/d_res.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / res/d_res
RESPONSIBILITY: Implements `d_res`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/core/fixed.h"
#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "world/d_worldgen.h"
#include "res/d_res.h"
#include "res/d_res_model.h"
#include "content/d_content_extra.h"

#define DRES_MAX_MODELS           16u
#define DRES_MAX_CHUNK_ENTRIES   256u
#define DRES_MAX_CELLS_PER_CHUNK   4u

typedef struct dres_chunk_entry {
    d_world           *world;
    d_chunk           *chunk;
    dres_channel_cell *cells;
    u32                cell_count;
    u32                cell_capacity;
} dres_chunk_entry;

static dres_model_vtable g_res_models[DRES_MAX_MODELS];
static u32 g_res_model_count = 0u;

static dres_chunk_entry g_res_chunks[DRES_MAX_CHUNK_ENTRIES];
static u32 g_res_chunk_count = 0u;

static int g_res_registered = 0;

static void dres_worldgen_populate(struct d_world *w, struct d_chunk *chunk);
static u32 dres_worldgen_hash(u64 seed, i32 cx, i32 cy, d_deposit_proto_id proto_id);

static void dres_free_cell(dres_channel_cell *cell) {
    if (!cell) {
        return;
    }
    if (cell->model_params.ptr) {
        free(cell->model_params.ptr);
    }
    cell->model_params.ptr = (unsigned char *)0;
    cell->model_params.len = 0u;
}

static int dres_reserve_cells(dres_chunk_entry *entry, u32 capacity) {
    dres_channel_cell *new_cells;
    u32 old_cap;
    if (!entry) {
        return -1;
    }
    if (capacity > DRES_MAX_CELLS_PER_CHUNK) {
        return -1;
    }
    if (capacity <= entry->cell_capacity) {
        return 0;
    }
    new_cells = (dres_channel_cell *)realloc(entry->cells, capacity * sizeof(dres_channel_cell));
    if (!new_cells) {
        return -1;
    }
    old_cap = entry->cell_capacity;
    entry->cells = new_cells;
    entry->cell_capacity = capacity;
    if (entry->cell_capacity > old_cap) {
        u32 i;
        for (i = old_cap; i < entry->cell_capacity; ++i) {
            memset(&entry->cells[i], 0, sizeof(dres_channel_cell));
        }
    }
    return 0;
}

static dres_channel_cell *dres_add_cell(dres_chunk_entry *entry) {
    if (!entry) {
        return (dres_channel_cell *)0;
    }
    if (entry->cell_count >= entry->cell_capacity) {
        if (dres_reserve_cells(entry, entry->cell_count + 1u) != 0) {
            return (dres_channel_cell *)0;
        }
    }
    memset(&entry->cells[entry->cell_count], 0, sizeof(dres_channel_cell));
    entry->cell_count += 1u;
    return &entry->cells[entry->cell_count - 1u];
}

static const dres_model_vtable *dres_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_res_model_count; ++i) {
        if (g_res_models[i].model_id == model_id) {
            return &g_res_models[i];
        }
    }
    return (const dres_model_vtable *)0;
}

int dres_register_model(const dres_model_vtable *vt) {
    d_model_desc desc;
    u32 i;
    if (!vt || vt->model_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_res_model_count; ++i) {
        if (g_res_models[i].model_id == vt->model_id) {
            return -2;
        }
    }
    if (g_res_model_count >= DRES_MAX_MODELS) {
        return -3;
    }

    g_res_models[g_res_model_count] = *vt;

    desc.family_id = D_MODEL_FAMILY_RES;
    desc.model_id = vt->model_id;
    desc.name = "res_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_res_models[g_res_model_count];

    if (d_model_register(&desc) != 0) {
        return -4;
    }

    g_res_model_count += 1u;
    return 0;
}

static dres_chunk_entry *dres_find_entry(d_world *w, d_chunk *chunk) {
    u32 i;
    if (!w || !chunk) {
        return (dres_chunk_entry *)0;
    }
    for (i = 0u; i < g_res_chunk_count; ++i) {
        if (g_res_chunks[i].world == w && g_res_chunks[i].chunk == chunk) {
            return &g_res_chunks[i];
        }
    }
    return (dres_chunk_entry *)0;
}

static dres_chunk_entry *dres_ensure_entry(d_world *w, d_chunk *chunk) {
    dres_chunk_entry *entry;
    if (!w || !chunk) {
        return (dres_chunk_entry *)0;
    }
    entry = dres_find_entry(w, chunk);
    if (entry) {
        return entry;
    }
    if (g_res_chunk_count >= DRES_MAX_CHUNK_ENTRIES) {
        return (dres_chunk_entry *)0;
    }
    entry = &g_res_chunks[g_res_chunk_count];
    memset(entry, 0, sizeof(*entry));
    entry->world = w;
    entry->chunk = chunk;
    g_res_chunk_count += 1u;
    return entry;
}

int dres_init_chunk(d_world *w, d_chunk *chunk) {
    dres_chunk_entry *entry;
    if (!w || !chunk) {
        return -1;
    }
    entry = dres_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }
    if (entry->cell_capacity == 0u) {
        if (dres_reserve_cells(entry, DRES_MAX_CELLS_PER_CHUNK) != 0) {
            return -1;
        }
    }
    return 0;
}

int dres_sample_at(
    d_world      *w,
    q32_32        x,
    q32_32        y,
    q32_32        z,
    u16           channel_mask,
    dres_sample  *out_samples,
    u16          *in_out_count
) {
    d_chunk *chunk;
    dres_chunk_entry *entry;
    u16 max_out;
    u16 count;
    u16 i;
    (void)channel_mask;
    (void)z;

    if (!w || !in_out_count) {
        return -1;
    }
    max_out = *in_out_count;
    if (max_out == 0u) {
        return 0;
    }

    chunk = d_world_find_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    if (!chunk) {
        chunk = d_world_get_or_create_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    }
    if (!chunk) {
        *in_out_count = 0u;
        return 0;
    }

    entry = dres_find_entry(w, chunk);
    if (!entry) {
        if (dres_init_chunk(w, chunk) != 0) {
            *in_out_count = 0u;
            return 0;
        }
        entry = dres_find_entry(w, chunk);
    }
    if (!entry || entry->cell_count == 0u || !entry->cells || !out_samples) {
        *in_out_count = 0u;
        return 0;
    }

    count = entry->cell_count;
    if (count > max_out) {
        count = max_out;
    }
    for (i = 0u; i < count; ++i) {
        dres_channel_cell *cell = &entry->cells[i];
        const dres_model_vtable *vt = dres_model_lookup(cell->desc.model_id);
        u16 j;
        if (vt && vt->compute_base) {
            vt->compute_base(w, chunk, cell, x, y, z);
        }
        out_samples[i].channel_id = cell->desc.channel_id;
        out_samples[i].model_family = cell->desc.model_family;
        out_samples[i].model_id = cell->desc.model_id;
        out_samples[i]._pad = 0u;
        out_samples[i].chunk = chunk;
        out_samples[i].pos_x = x;
        out_samples[i].pos_y = y;
        out_samples[i].pos_z = z;
        out_samples[i].proto_id = cell->proto_id;
        out_samples[i].tags = cell->tags;
        for (j = 0u; j < DRES_VALUE_MAX; ++j) {
            out_samples[i].value[j] = cell->values[j];
        }
    }
    *in_out_count = count;
    return 0;
}

int dres_apply_delta(
    d_world            *w,
    const dres_sample  *sample,
    const q16_16       *delta_values,
    u32                 seed_context
) {
    u32 i;
    if (!w || !sample || !delta_values) {
        return -1;
    }
    for (i = 0u; i < g_res_chunk_count; ++i) {
        dres_chunk_entry *entry = &g_res_chunks[i];
        u32 c;
        if (entry->world != w || entry->cell_count == 0u || !entry->cells) {
            continue;
        }
        if (sample->chunk && entry->chunk != sample->chunk) {
            continue;
        }
        for (c = 0u; c < entry->cell_count; ++c) {
            dres_channel_cell *cell = &entry->cells[c];
            const dres_model_vtable *vt;
            u16 j;
            if (cell->desc.channel_id != sample->channel_id) {
                continue;
            }
            vt = dres_model_lookup(cell->desc.model_id);
            if (vt && vt->apply_delta) {
                vt->apply_delta(w, entry->chunk, cell, delta_values, seed_context);
                return 0;
            }
            for (j = 0u; j < DRES_VALUE_MAX; ++j) {
                cell->values[j] = d_q16_16_add(cell->values[j], delta_values[j]);
            }
            return 0;
        }
    }
    return -1;
}

static int dres_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    dres_chunk_entry *entry;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;
    (void)w;

    if (!out) {
        return -1;
    }
    entry = dres_find_entry(w, chunk);
    if (!entry || entry->cell_count == 0u || !entry->cells) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total = 4u;
    for (i = 0u; i < entry->cell_count; ++i) {
        u32 params_len = entry->cells[i].model_params.len;
        u32 cell_size = sizeof(dres_channel_desc) +
                        sizeof(d_content_tag) +
                        sizeof(d_deposit_proto_id) +
                        sizeof(d_material_id) +
                        sizeof(u32) + /* initialized flag */
                        sizeof(u32) + /* params len */
                        params_len +
                        (sizeof(q16_16) * DRES_VALUE_MAX * 2u);
        if (params_len > 0u && entry->cells[i].model_params.ptr == (unsigned char *)0) {
            return -1;
        }
        if (total > 0xFFFFFFFFu - cell_size) {
            return -1;
        }
        total += cell_size;
    }

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &entry->cell_count, sizeof(u32));
    dst += 4u;
    for (i = 0u; i < entry->cell_count; ++i) {
        u32 init_flag = entry->cells[i].initialized ? 1u : 0u;
        u32 params_len = entry->cells[i].model_params.len;
        memcpy(dst, &entry->cells[i].desc, sizeof(dres_channel_desc));
        dst += sizeof(dres_channel_desc);
        memcpy(dst, &entry->cells[i].tags, sizeof(d_content_tag));
        dst += sizeof(d_content_tag);
        memcpy(dst, &entry->cells[i].proto_id, sizeof(d_deposit_proto_id));
        dst += sizeof(d_deposit_proto_id);
        memcpy(dst, &entry->cells[i].material_id, sizeof(d_material_id));
        dst += sizeof(d_material_id);
        memcpy(dst, &init_flag, sizeof(u32));
        dst += sizeof(u32);
        memcpy(dst, &params_len, sizeof(u32));
        dst += sizeof(u32);
        if (params_len > 0u) {
            memcpy(dst, entry->cells[i].model_params.ptr, params_len);
            dst += params_len;
        }
        memcpy(dst, entry->cells[i].values, sizeof(q16_16) * DRES_VALUE_MAX);
        dst += sizeof(q16_16) * DRES_VALUE_MAX;
        memcpy(dst, entry->cells[i].deltas, sizeof(q16_16) * DRES_VALUE_MAX);
        dst += sizeof(q16_16) * DRES_VALUE_MAX;
    }

    out->ptr = buf;
    out->len = total;
    return 0;
}

static int dres_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    dres_chunk_entry *entry;
    const unsigned char *ptr;
    u32 remaining;
    u32 cell_count;
    u32 i;
    (void)w;

    if (!chunk || !in) {
        return -1;
    }
    if (in->len == 0u) {
        return 0;
    }
    if (!in->ptr) {
        return -1;
    }
    if (in->len < 4u) {
        return -1;
    }

    ptr = in->ptr;
    remaining = in->len;

    memcpy(&cell_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;

    entry = dres_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }
    if (entry->cells) {
        u32 c;
        for (c = 0u; c < entry->cell_count; ++c) {
            dres_free_cell(&entry->cells[c]);
        }
        free(entry->cells);
        entry->cells = (dres_channel_cell *)0;
        entry->cell_capacity = 0u;
        entry->cell_count = 0u;
    }
    if (cell_count > 0u) {
        if (dres_reserve_cells(entry, cell_count) != 0) {
            return -1;
        }
        entry->cell_count = cell_count;
        for (i = 0u; i < cell_count; ++i) {
            u32 init_flag = 0u;
            u32 params_len = 0u;
            u32 cell_bytes = sizeof(dres_channel_desc) +
                             sizeof(d_content_tag) +
                             sizeof(d_deposit_proto_id) +
                             sizeof(d_material_id) +
                             sizeof(u32) + sizeof(u32);
            if (remaining < cell_bytes) {
                return -1;
            }

            memcpy(&entry->cells[i].desc, ptr, sizeof(dres_channel_desc));
            ptr += sizeof(dres_channel_desc);
            memcpy(&entry->cells[i].tags, ptr, sizeof(d_content_tag));
            ptr += sizeof(d_content_tag);
            memcpy(&entry->cells[i].proto_id, ptr, sizeof(d_deposit_proto_id));
            ptr += sizeof(d_deposit_proto_id);
            memcpy(&entry->cells[i].material_id, ptr, sizeof(d_material_id));
            ptr += sizeof(d_material_id);
            memcpy(&init_flag, ptr, sizeof(u32));
            ptr += sizeof(u32);
            memcpy(&params_len, ptr, sizeof(u32));
            ptr += sizeof(u32);
            remaining -= cell_bytes;

            entry->cells[i].initialized = (u8)(init_flag ? 1u : 0u);
            entry->cells[i].model_params.ptr = (unsigned char *)0;
            entry->cells[i].model_params.len = params_len;

            if (params_len > 0u) {
                if (params_len > remaining) {
                    return -1;
                }
                entry->cells[i].model_params.ptr = (unsigned char *)malloc(params_len);
                if (!entry->cells[i].model_params.ptr) {
                    return -1;
                }
                memcpy(entry->cells[i].model_params.ptr, ptr, params_len);
                ptr += params_len;
                remaining -= params_len;
            }

            if (remaining < sizeof(q16_16) * DRES_VALUE_MAX * 2u) {
                return -1;
            }
            memcpy(entry->cells[i].values, ptr, sizeof(q16_16) * DRES_VALUE_MAX);
            ptr += sizeof(q16_16) * DRES_VALUE_MAX;
            memcpy(entry->cells[i].deltas, ptr, sizeof(q16_16) * DRES_VALUE_MAX);
            ptr += sizeof(q16_16) * DRES_VALUE_MAX;
            remaining -= sizeof(q16_16) * DRES_VALUE_MAX * 2u;
        }
    }
    return 0;
}

static int dres_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dres_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    if (!in) {
        return -1;
    }
    return 0;
}

static void dres_tick(d_world *w, u32 ticks) {
    u32 i;
    for (i = 0u; i < g_res_chunk_count; ++i) {
        dres_chunk_entry *entry = &g_res_chunks[i];
        u32 c;
        if (entry->world != w || entry->cell_count == 0u || !entry->cells) {
            continue;
        }
        for (c = 0u; c < entry->cell_count; ++c) {
            const dres_model_vtable *vt = dres_model_lookup(entry->cells[c].desc.model_id);
            if (vt && vt->tick) {
                vt->tick(w, entry->chunk, &entry->cells[c], ticks);
            }
        }
    }
}

static void dres_register_worldgen(void) {
    static const d_worldgen_provider prov = {
        1u,
        "demo_strata_provider",
        (const d_worldgen_provider_id *)0,
        dres_worldgen_populate
    };
    d_worldgen_register(&prov);
}

static u32 dres_worldgen_hash(u64 seed, i32 cx, i32 cy, d_deposit_proto_id proto_id) {
    u32 x = (u32)(seed ^ (seed >> 32));
    x ^= (u32)proto_id * 0x9e3779b9u;
    x ^= (u32)cx * 0x85ebca6bu;
    x ^= (u32)cy * 0xc2b2ae35u;
    x ^= x >> 16;
    x *= 0x7feb352du;
    x ^= x >> 15;
    x *= 0x846ca68bu;
    x ^= x >> 16;
    return x;
}

static void dres_worldgen_populate(struct d_world *w, struct d_chunk *chunk) {
    dres_chunk_entry *entry;
    u32 dep_count;
    u32 i;

    if (!w || !chunk) {
        return;
    }
    if (dres_init_chunk((d_world *)w, (d_chunk *)chunk) != 0) {
        return;
    }
    entry = dres_find_entry(w, chunk);
    if (!entry) {
        return;
    }

    dep_count = d_content_deposit_count();
    for (i = 0u; i < dep_count; ++i) {
        const d_proto_deposit *dep = d_content_get_deposit_by_index(i);
        dres_channel_cell *cell;
        const dres_model_vtable *vt;
        if (!dep) {
            continue;
        }
        if ((dep->tags & D_TAG_DEPOSIT_STRATA_SOLID) == 0u) {
            continue;
        }
        {
            u32 noise = dres_worldgen_hash(w->worldgen_seed, chunk->cx, chunk->cy, dep->id);
            if ((noise & 0xFFFFu) < 0x4000u) {
                continue;
            }
        }
        vt = dres_model_lookup(dep->model_id);
        if (!vt) {
            continue;
        }
        cell = dres_add_cell(entry);
        if (!cell) {
            continue;
        }
        memset(cell, 0, sizeof(*cell));
        cell->desc.channel_id = (u16)(dep->id & 0xFFFFu);
        cell->desc.model_family = D_MODEL_FAMILY_RES;
        cell->desc.model_id = dep->model_id;
        cell->desc.flags = 0u;
        cell->tags = dep->tags;
        cell->proto_id = dep->id;
        cell->material_id = dep->material_id;
        cell->initialized = 0u;
        if (dep->model_params.len > 0u) {
            cell->model_params.len = dep->model_params.len;
            cell->model_params.ptr = (unsigned char *)malloc(dep->model_params.len);
            if (cell->model_params.ptr) {
                memcpy(cell->model_params.ptr, dep->model_params.ptr, dep->model_params.len);
            } else {
                cell->model_params.len = 0u;
            }
        }
        if (vt->init_chunk) {
            vt->init_chunk(w, chunk, cell);
        }
    }
}

static void dres_register_models(void) {
    dres_register_strata_solid_model();
    dres_register_worldgen();
}

static void dres_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static void dres_init_instance_subsys(d_world *w) {
    u32 i;
    u32 dst = 0u;
    for (i = 0u; i < g_res_chunk_count; ++i) {
        if (g_res_chunks[i].world == w) {
            if (g_res_chunks[i].cells) {
                u32 c;
                for (c = 0u; c < g_res_chunks[i].cell_count; ++c) {
                    dres_free_cell(&g_res_chunks[i].cells[c]);
                }
                free(g_res_chunks[i].cells);
            }
            g_res_chunks[i].cells = (dres_channel_cell *)0;
            g_res_chunks[i].cell_count = 0u;
            g_res_chunks[i].cell_capacity = 0u;
        } else {
            if (dst != i) {
                g_res_chunks[dst] = g_res_chunks[i];
            }
            dst += 1u;
        }
    }
    g_res_chunk_count = dst;
}

static const d_subsystem_desc g_res_subsystem = {
    D_SUBSYS_RES,
    "res",
    1u,
    dres_register_models,
    dres_load_protos,
    dres_init_instance_subsys,
    dres_tick,
    dres_save_chunk,
    dres_load_chunk,
    dres_save_instance,
    dres_load_instance
};

void d_res_init(void) {
    if (g_res_registered) {
        return;
    }
    if (d_subsystem_register(&g_res_subsystem) == 0) {
        g_res_registered = 1;
    }
}
