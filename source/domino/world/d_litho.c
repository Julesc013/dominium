#include <stdlib.h>
#include <string.h>

#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "world/d_worldgen.h"
#include "world/d_litho.h"

#define DLITHO_MAX_CHUNK_ENTRIES 256u

typedef struct dlitho_chunk_entry_s {
    d_world       *world;
    d_chunk       *chunk;
    d_world_layers columns[D_LITHO_GRID_RES * D_LITHO_GRID_RES];
} dlitho_chunk_entry;

static dlitho_chunk_entry g_litho_chunks[DLITHO_MAX_CHUNK_ENTRIES];
static u32 g_litho_chunk_count = 0u;
static int g_litho_registered = 0;

static u32 dlitho_hash_u32(u64 seed, i32 cx, i32 cy, u32 lx, u32 ly) {
    u32 x = (u32)(seed ^ (seed >> 32));
    x ^= (u32)cx * 0x85ebca6bu;
    x ^= (u32)cy * 0xc2b2ae35u;
    x ^= (u32)lx * 0x27d4eb2du;
    x ^= (u32)ly * 0x165667b1u;
    x ^= x >> 16;
    x *= 0x7feb352du;
    x ^= x >> 15;
    x *= 0x846ca68bu;
    x ^= x >> 16;
    return x;
}

static dlitho_chunk_entry *dlitho_find_entry(d_world *w, d_chunk *chunk) {
    u32 i;
    if (!w || !chunk) {
        return (dlitho_chunk_entry *)0;
    }
    for (i = 0u; i < g_litho_chunk_count; ++i) {
        if (g_litho_chunks[i].world == w && g_litho_chunks[i].chunk == chunk) {
            return &g_litho_chunks[i];
        }
    }
    return (dlitho_chunk_entry *)0;
}

static dlitho_chunk_entry *dlitho_ensure_entry(d_world *w, d_chunk *chunk) {
    dlitho_chunk_entry *entry;
    if (!w || !chunk) {
        return (dlitho_chunk_entry *)0;
    }
    entry = dlitho_find_entry(w, chunk);
    if (entry) {
        return entry;
    }
    if (g_litho_chunk_count >= DLITHO_MAX_CHUNK_ENTRIES) {
        return (dlitho_chunk_entry *)0;
    }
    entry = &g_litho_chunks[g_litho_chunk_count];
    memset(entry, 0, sizeof(*entry));
    entry->world = w;
    entry->chunk = chunk;
    g_litho_chunk_count += 1u;
    return entry;
}

static d_material_id dlitho_pick_solid_material(u32 salt) {
    u32 count;
    u32 i;
    count = d_content_material_count();
    if (count == 0u) {
        return 0u;
    }
    /* Pick among solid-tagged materials, fall back to first. */
    {
        u32 picked = 0u;
        u32 seen = 0u;
        for (i = 0u; i < count; ++i) {
            const d_proto_material *m = d_content_get_material_by_index(i);
            if (!m) {
                continue;
            }
            if ((m->tags & D_TAG_MATERIAL_SOLID) == 0u) {
                continue;
            }
            if ((salt % (seen + 1u)) == 0u) {
                picked = m->id;
            }
            seen += 1u;
        }
        if (picked != 0u) {
            return picked;
        }
    }
    {
        const d_proto_material *m0 = d_content_get_material_by_index(0u);
        return m0 ? m0->id : 0u;
    }
}

static void dlitho_init_chunk_layers(d_world *w, d_chunk *chunk) {
    dlitho_chunk_entry *entry;
    u32 x, y;
    if (!w || !chunk) {
        return;
    }
    entry = dlitho_ensure_entry(w, chunk);
    if (!entry) {
        return;
    }
    for (y = 0u; y < D_LITHO_GRID_RES; ++y) {
        for (x = 0u; x < D_LITHO_GRID_RES; ++x) {
            u32 h = dlitho_hash_u32(w->meta.seed, chunk->cx, chunk->cy, x, y);
            d_material_id top = dlitho_pick_solid_material(h);
            d_world_layers *col = &entry->columns[y * D_LITHO_GRID_RES + x];
            memset(col, 0, sizeof(*col));
            col->layer_count = 1u;
            col->layers[0].material_id = top;
            col->layers[0].thickness = d_q16_16_from_int(1024);
        }
    }
}

static void dlitho_worldgen_populate(struct d_world *w, struct d_chunk *chunk) {
    dlitho_init_chunk_layers((d_world *)w, (d_chunk *)chunk);
}

int d_litho_layers_at(
    d_world        *w,
    q32_32          x,
    q32_32          y,
    d_world_layers *out_layers
) {
    d_chunk *chunk;
    dlitho_chunk_entry *entry;
    u32 fx;
    u32 fy;
    u32 lx;
    u32 ly;
    u32 idx;
    if (!w || !out_layers) {
        return -1;
    }
    chunk = d_world_find_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    if (!chunk) {
        chunk = d_world_get_or_create_chunk(w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    }
    if (!chunk) {
        memset(out_layers, 0, sizeof(*out_layers));
        return 0;
    }
    entry = dlitho_find_entry(w, chunk);
    if (!entry) {
        dlitho_init_chunk_layers(w, chunk);
        entry = dlitho_find_entry(w, chunk);
    }
    if (!entry) {
        memset(out_layers, 0, sizeof(*out_layers));
        return 0;
    }

    fx = (u32)x;
    fy = (u32)y;
    lx = (fx >> 28) & 0xFu;
    ly = (fy >> 28) & 0xFu;
    idx = ly * D_LITHO_GRID_RES + lx;
    if (idx >= D_LITHO_GRID_RES * D_LITHO_GRID_RES) {
        idx = 0u;
    }
    *out_layers = entry->columns[idx];
    return 0;
}

static int dlitho_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    dlitho_chunk_entry *entry;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;
    (void)w;

    if (!out) {
        return -1;
    }
    entry = dlitho_find_entry(w, chunk);
    if (!entry) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total = 4u;
    total += (D_LITHO_GRID_RES * D_LITHO_GRID_RES) * (2u + (D_LITHO_MAX_LAYERS * (sizeof(d_material_id) + sizeof(q16_16))));
    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    {
        u32 col_count = D_LITHO_GRID_RES * D_LITHO_GRID_RES;
        memcpy(dst, &col_count, sizeof(u32));
        dst += 4u;
    }

    for (i = 0u; i < (D_LITHO_GRID_RES * D_LITHO_GRID_RES); ++i) {
        u16 lc = entry->columns[i].layer_count;
        u32 l;
        memcpy(dst, &lc, sizeof(u16));
        dst += sizeof(u16);
        for (l = 0u; l < D_LITHO_MAX_LAYERS; ++l) {
            d_material_id mid = entry->columns[i].layers[l].material_id;
            q16_16 th = entry->columns[i].layers[l].thickness;
            memcpy(dst, &mid, sizeof(d_material_id)); dst += sizeof(d_material_id);
            memcpy(dst, &th, sizeof(q16_16)); dst += sizeof(q16_16);
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int dlitho_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    dlitho_chunk_entry *entry;
    const unsigned char *ptr;
    u32 remaining;
    u32 col_count;
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
    memcpy(&col_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;
    if (col_count != (D_LITHO_GRID_RES * D_LITHO_GRID_RES)) {
        return -1;
    }

    entry = dlitho_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }

    for (i = 0u; i < col_count; ++i) {
        u32 l;
        u16 lc;
        u32 need = (u32)sizeof(u16) + (D_LITHO_MAX_LAYERS * (sizeof(d_material_id) + sizeof(q16_16)));
        if (remaining < need) {
            return -1;
        }
        memcpy(&lc, ptr, sizeof(u16));
        ptr += sizeof(u16);
        remaining -= sizeof(u16);
        entry->columns[i].layer_count = lc;
        for (l = 0u; l < D_LITHO_MAX_LAYERS; ++l) {
            memcpy(&entry->columns[i].layers[l].material_id, ptr, sizeof(d_material_id));
            ptr += sizeof(d_material_id);
            memcpy(&entry->columns[i].layers[l].thickness, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            remaining -= sizeof(d_material_id) + sizeof(q16_16);
        }
    }

    return 0;
}

static int dlitho_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int dlitho_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void dlitho_init_instance_subsys(d_world *w) {
    u32 i;
    u32 dst = 0u;
    for (i = 0u; i < g_litho_chunk_count; ++i) {
        if (g_litho_chunks[i].world == w) {
            memset(&g_litho_chunks[i], 0, sizeof(g_litho_chunks[i]));
        } else {
            if (dst != i) {
                g_litho_chunks[dst] = g_litho_chunks[i];
            }
            dst += 1u;
        }
    }
    g_litho_chunk_count = dst;
}

static void dlitho_tick_stub(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static void dlitho_register_models(void) {
    static const d_worldgen_provider prov = {
        4u,
        "litho_default_provider",
        (const d_worldgen_provider_id *)0,
        dlitho_worldgen_populate
    };
    d_worldgen_register(&prov);
}

static void dlitho_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_litho_subsystem = {
    D_SUBSYS_LITHO,
    "litho",
    1u,
    dlitho_register_models,
    dlitho_load_protos,
    dlitho_init_instance_subsys,
    dlitho_tick_stub,
    dlitho_save_chunk,
    dlitho_load_chunk,
    dlitho_save_instance,
    dlitho_load_instance
};

void d_litho_init(void) {
    if (g_litho_registered) {
        return;
    }
    if (d_subsystem_register(&g_litho_subsystem) == 0) {
        g_litho_registered = 1;
    }
}

