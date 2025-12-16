/*
FILE: source/domino/env/d_env.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / env/d_env
RESPONSIBILITY: Implements `d_env`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "env/d_env.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"

#define DENV_MAX_FIELD_MODELS    8u
#define DENV_MAX_CHUNK_ENTRIES 256u
#define DENV_MAX_FIELDS_PER_CHUNK 32u

typedef struct denv_chunk_entry {
    d_world         *world;
    d_chunk         *chunk;
    denv_zone_state *zones;
    u32              zone_count;
    denv_portal     *portals;
    u32              portal_count;

    d_env_field_cell *fields;
    u32               field_count;
    u32               field_capacity;
} denv_chunk_entry;

static d_env_model_vtable g_env_models[DENV_MAX_FIELD_MODELS];
static u32 g_env_model_count = 0u;

static denv_chunk_entry g_env_chunks[DENV_MAX_CHUNK_ENTRIES];
static u32 g_env_chunk_count = 0u;

static int g_env_registered = 0;

static const d_env_model_vtable *denv_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_env_model_count; ++i) {
        if (g_env_models[i].model_id == model_id) {
            return &g_env_models[i];
        }
    }
    return (const d_env_model_vtable *)0;
}

int d_env_register_model(const d_env_model_vtable *vt) {
    d_model_desc desc;
    u32 i;
    if (!vt || vt->model_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_env_model_count; ++i) {
        if (g_env_models[i].model_id == vt->model_id) {
            return -2;
        }
    }
    if (g_env_model_count >= DENV_MAX_FIELD_MODELS) {
        return -3;
    }
    g_env_models[g_env_model_count] = *vt;

    desc.family_id = D_MODEL_FAMILY_ENV;
    desc.model_id = vt->model_id;
    desc.name = "env_field_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_env_models[g_env_model_count];

    if (d_model_register(&desc) != 0) {
        return -4;
    }

    g_env_model_count += 1u;
    return 0;
}

int denv_register_model(const d_env_model_vtable *vt) {
    return d_env_register_model(vt);
}

static void denv_free_fields(denv_chunk_entry *entry) {
    if (!entry) {
        return;
    }
    if (entry->fields) {
        free(entry->fields);
    }
    entry->fields = (d_env_field_cell *)0;
    entry->field_count = 0u;
    entry->field_capacity = 0u;
}

static int denv_reserve_fields(denv_chunk_entry *entry, u32 capacity) {
    d_env_field_cell *new_fields;
    u32 old_cap;
    if (!entry) {
        return -1;
    }
    if (capacity > DENV_MAX_FIELDS_PER_CHUNK) {
        return -1;
    }
    if (capacity <= entry->field_capacity) {
        return 0;
    }
    new_fields = (d_env_field_cell *)realloc(entry->fields, capacity * sizeof(d_env_field_cell));
    if (!new_fields) {
        return -1;
    }
    old_cap = entry->field_capacity;
    entry->fields = new_fields;
    entry->field_capacity = capacity;
    if (entry->field_capacity > old_cap) {
        u32 i;
        for (i = old_cap; i < entry->field_capacity; ++i) {
            memset(&entry->fields[i], 0, sizeof(d_env_field_cell));
        }
    }
    return 0;
}

static d_env_field_cell *denv_add_field(denv_chunk_entry *entry) {
    if (!entry) {
        return (d_env_field_cell *)0;
    }
    if (entry->field_count >= entry->field_capacity) {
        if (denv_reserve_fields(entry, entry->field_count + 1u) != 0) {
            return (d_env_field_cell *)0;
        }
    }
    memset(&entry->fields[entry->field_count], 0, sizeof(d_env_field_cell));
    entry->field_count += 1u;
    return &entry->fields[entry->field_count - 1u];
}

static d_env_field_cell *denv_find_field_cell(denv_chunk_entry *entry, d_env_field_id field_id) {
    u32 i;
    if (!entry || !entry->fields) {
        return (d_env_field_cell *)0;
    }
    for (i = 0u; i < entry->field_count; ++i) {
        if (entry->fields[i].desc.field_id == field_id) {
            return &entry->fields[i];
        }
    }
    return (d_env_field_cell *)0;
}

static void denv_init_default_fields(d_world *w, d_chunk *chunk, denv_chunk_entry *entry) {
    static const d_env_field_id k_fields[] = {
        D_ENV_FIELD_PRESSURE,
        D_ENV_FIELD_TEMPERATURE,
        D_ENV_FIELD_GAS0_FRACTION,
        D_ENV_FIELD_GAS1_FRACTION,
        D_ENV_FIELD_HUMIDITY,
        D_ENV_FIELD_WIND_X,
        D_ENV_FIELD_WIND_Y
    };
    u32 i;
    if (!w || !chunk || !entry) {
        return;
    }
    if (entry->field_count != 0u) {
        return;
    }
    for (i = 0u; i < (u32)(sizeof(k_fields) / sizeof(k_fields[0])); ++i) {
        d_env_field_cell *cell = denv_add_field(entry);
        const d_env_model_vtable *vt;
        if (!cell) {
            break;
        }
        memset(cell, 0, sizeof(*cell));
        cell->desc.field_id = k_fields[i];
        cell->desc.model_id = D_ENV_MODEL_ATMOSPHERE_DEFAULT;
        cell->desc.flags = 0u;
        vt = denv_model_lookup(cell->desc.model_id);
        if (vt && vt->init_chunk) {
            vt->init_chunk(w, chunk, cell, (const d_tlv_blob *)0);
        }
        if (vt && vt->compute_base) {
            vt->compute_base((const d_world *)w, (const d_chunk *)chunk, cell);
        }
    }
}

static u32 denv_hash_u32(u64 seed, i32 cx, i32 cy) {
    u32 x = (u32)(seed ^ (seed >> 32));
    x ^= (u32)cx * 0x85ebca6bu;
    x ^= (u32)cy * 0xc2b2ae35u;
    x ^= x >> 16;
    x *= 0x7feb352du;
    x ^= x >> 15;
    x *= 0x846ca68bu;
    x ^= x >> 16;
    return x;
}

static q16_16 denv_triangle_wave(u32 t, u32 period_ticks, q16_16 amplitude) {
    u32 half;
    u32 phase;
    i32 signed_unit;
    q16_16 unit_q16;
    q16_16 out;
    if (period_ticks == 0u) {
        return 0;
    }
    half = period_ticks / 2u;
    if (half == 0u) {
        return 0;
    }
    phase = t % period_ticks;
    if (phase < half) {
        signed_unit = (i32)phase;
    } else {
        signed_unit = (i32)(period_ticks - phase);
    }
    /* signed_unit in [0..half]; map to [-1..+1] with midpoint at half/2. */
    signed_unit = (signed_unit * 2) - (i32)half;
    unit_q16 = (q16_16)(((i64)signed_unit << Q16_16_FRAC_BITS) / (i32)half);
    out = d_q16_16_mul(unit_q16, amplitude);
    return out;
}

static q16_16 denv_q16_from_ratio(i32 num, i32 denom) {
    if (denom == 0) {
        return 0;
    }
    return (q16_16)(((i64)num << Q16_16_FRAC_BITS) / (i64)denom);
}

static void denv_atmo_init_chunk(
    d_world          *w,
    d_chunk          *chunk,
    d_env_field_cell *cell,
    const d_tlv_blob *params
) {
    u32 h;
    q16_16 altitude_m;
    q16_16 base;
    (void)params;

    if (!cell || !chunk) {
        return;
    }
    h = denv_hash_u32(w ? w->meta.seed : 0u, chunk->cx, chunk->cy);
    altitude_m = d_q16_16_from_int((i32)(h % 2000u));

    switch (cell->desc.field_id) {
    case D_ENV_FIELD_PRESSURE:
        base = d_q16_16_from_int(101);
        base = d_q16_16_sub(base, (q16_16)(altitude_m >> 18)); /* mild drop with altitude */
        cell->values[0] = base;
        cell->values[3] = base; /* store baseline */
        break;
    case D_ENV_FIELD_TEMPERATURE:
        base = d_q16_16_from_int(15);
        base = d_q16_16_sub(base, (q16_16)(altitude_m >> 17));
        cell->values[0] = base;
        cell->values[3] = base;
        break;
    case D_ENV_FIELD_GAS0_FRACTION:
        cell->values[0] = denv_q16_from_ratio(21, 100);
        cell->values[3] = cell->values[0];
        break;
    case D_ENV_FIELD_GAS1_FRACTION:
        cell->values[0] = denv_q16_from_ratio(4, 10000);
        cell->values[3] = cell->values[0];
        break;
    case D_ENV_FIELD_HUMIDITY:
        cell->values[0] = denv_q16_from_ratio(1, 2);
        cell->values[3] = cell->values[0];
        break;
    case D_ENV_FIELD_WIND_X:
    case D_ENV_FIELD_WIND_Y:
        cell->values[0] = 0;
        cell->values[3] = 0;
        break;
    default:
        break;
    }
}

static void denv_atmo_compute_base(
    const d_world    *w,
    const d_chunk    *chunk,
    d_env_field_cell *cell
) {
    u32 h;
    q16_16 altitude_m;
    q16_16 base;
    if (!cell || !chunk) {
        return;
    }

    h = denv_hash_u32(w ? w->meta.seed : 0u, chunk->cx, chunk->cy);
    altitude_m = d_q16_16_from_int((i32)(h % 2000u));

    switch (cell->desc.field_id) {
    case D_ENV_FIELD_PRESSURE:
        base = d_q16_16_from_int(101);
        base = d_q16_16_sub(base, (q16_16)(altitude_m >> 18));
        cell->values[3] = base;
        break;
    case D_ENV_FIELD_TEMPERATURE:
        base = d_q16_16_from_int(15);
        base = d_q16_16_sub(base, (q16_16)(altitude_m >> 17));
        cell->values[3] = base;
        break;
    case D_ENV_FIELD_GAS0_FRACTION:
        cell->values[3] = denv_q16_from_ratio(21, 100);
        break;
    case D_ENV_FIELD_GAS1_FRACTION:
        cell->values[3] = denv_q16_from_ratio(4, 10000);
        break;
    case D_ENV_FIELD_HUMIDITY:
        cell->values[3] = denv_q16_from_ratio(1, 2);
        break;
    case D_ENV_FIELD_WIND_X:
    case D_ENV_FIELD_WIND_Y:
        cell->values[3] = 0;
        break;
    default:
        break;
    }
}

static void denv_atmo_tick(
    d_world          *w,
    d_chunk          *chunk,
    d_env_field_cell *cell,
    u32               ticks
) {
    u32 seed_lo;
    u32 t;
    q16_16 desired;
    q16_16 v;
    q16_16 diff;
    q16_16 relax;
    (void)chunk;

    if (!w || !cell || ticks == 0u) {
        return;
    }
    seed_lo = (u32)(w->meta.seed & 0xFFFFFFFFu);
    t = w->tick_count + seed_lo;

    relax = d_q16_16_from_int((i32)ticks);

    switch (cell->desc.field_id) {
    case D_ENV_FIELD_TEMPERATURE:
        desired = d_q16_16_add(cell->values[3], denv_triangle_wave(t, 24000u, d_q16_16_from_int(8)));
        v = cell->values[0];
        diff = d_q16_16_sub(desired, v);
        v = d_q16_16_add(v, d_q16_16_mul((q16_16)(diff >> 4), relax));
        cell->values[0] = v;
        break;
    case D_ENV_FIELD_PRESSURE:
        desired = cell->values[3];
        v = cell->values[0];
        diff = d_q16_16_sub(desired, v);
        v = d_q16_16_add(v, d_q16_16_mul((q16_16)(diff >> 6), relax));
        cell->values[0] = v;
        break;
    case D_ENV_FIELD_HUMIDITY:
    case D_ENV_FIELD_GAS0_FRACTION:
    case D_ENV_FIELD_GAS1_FRACTION:
        desired = cell->values[3];
        v = cell->values[0];
        diff = d_q16_16_sub(desired, v);
        v = d_q16_16_add(v, d_q16_16_mul((q16_16)(diff >> 6), relax));
        cell->values[0] = v;
        break;
    case D_ENV_FIELD_WIND_X:
    case D_ENV_FIELD_WIND_Y:
        /* Stub: winds remain near zero. */
        break;
    default:
        break;
    }
}

static const d_env_model_vtable g_atmo_vt = {
    D_ENV_MODEL_ATMOSPHERE_DEFAULT,
    denv_atmo_init_chunk,
    denv_atmo_compute_base,
    denv_atmo_tick
};

static denv_chunk_entry *denv_find_entry(d_world *w, d_chunk *chunk) {
    u32 i;
    if (!w || !chunk) {
        return (denv_chunk_entry *)0;
    }
    for (i = 0u; i < g_env_chunk_count; ++i) {
        if (g_env_chunks[i].world == w && g_env_chunks[i].chunk == chunk) {
            return &g_env_chunks[i];
        }
    }
    return (denv_chunk_entry *)0;
}

static denv_chunk_entry *denv_ensure_entry(d_world *w, d_chunk *chunk) {
    denv_chunk_entry *entry = denv_find_entry(w, chunk);
    if (entry) {
        return entry;
    }
    if (g_env_chunk_count >= DENV_MAX_CHUNK_ENTRIES) {
        return (denv_chunk_entry *)0;
    }
    entry = &g_env_chunks[g_env_chunk_count];
    memset(entry, 0, sizeof(*entry));
    entry->world = w;
    entry->chunk = chunk;
    g_env_chunk_count += 1u;
    return entry;
}

int denv_init_chunk(d_world *w, d_chunk *chunk) {
    denv_chunk_entry *entry;
    if (!w || !chunk) {
        return -1;
    }
    entry = denv_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }
    if (entry->zone_count == 0u) {
        entry->zones = (denv_zone_state *)malloc(sizeof(denv_zone_state));
        if (!entry->zones) {
            return -1;
        }
        memset(entry->zones, 0, sizeof(denv_zone_state));
        entry->zone_count = 1u;
        entry->zones[0].id = (denv_zone_id)chunk->chunk_id;
        entry->zones[0].temperature = d_q16_16_from_int(15);
        entry->zones[0].pressure = d_q16_16_from_int(101);
        entry->zones[0].humidity = 0;
        entry->zones[0].gas_mix[0] = 0;
        entry->zones[0].gas_mix[1] = 0;
        entry->zones[0].gas_mix[2] = 0;
        entry->zones[0].gas_mix[3] = 0;
        entry->zones[0].pollution = 0;
        entry->zones[0].light_level = 0;
        entry->zones[0].extra.ptr = (unsigned char *)0;
        entry->zones[0].extra.len = 0u;
    }
    entry->portal_count = 0u;
    entry->portals = (denv_portal *)0;

    if (entry->field_capacity == 0u) {
        if (denv_reserve_fields(entry, 8u) != 0) {
            return -1;
        }
    }
    denv_init_default_fields(w, chunk, entry);
    return 0;
}

static q16_16 denv_q16_from_i64_clamp(i64 v) {
    if (v > (i64)0x7FFFFFFF) {
        return (q16_16)0x7FFFFFFF;
    }
    if (v < (i64)0x80000000) {
        return (q16_16)0x80000000;
    }
    return (q16_16)v;
}

static void denv_apply_atmo_diffusion(d_world *w, u32 ticks) {
    denv_chunk_entry *list[DENV_MAX_CHUNK_ENTRIES];
    q16_16 old_p[DENV_MAX_CHUNK_ENTRIES];
    q16_16 old_t[DENV_MAX_CHUNK_ENTRIES];
    i64 delta_p[DENV_MAX_CHUNK_ENTRIES];
    i64 delta_t[DENV_MAX_CHUNK_ENTRIES];
    u32 count = 0u;
    u32 i;

    if (!w || ticks == 0u) {
        return;
    }

    for (i = 0u; i < g_env_chunk_count; ++i) {
        denv_chunk_entry *entry = &g_env_chunks[i];
        if (entry->world != w) {
            continue;
        }
        if (!entry->fields || entry->field_count == 0u) {
            continue;
        }
        if (count < DENV_MAX_CHUNK_ENTRIES) {
            list[count] = entry;
            old_p[count] = 0;
            old_t[count] = 0;
            delta_p[count] = 0;
            delta_t[count] = 0;
            count += 1u;
        }
    }
    if (count == 0u) {
        return;
    }

    for (i = 0u; i < count; ++i) {
        d_env_field_cell *p = denv_find_field_cell(list[i], D_ENV_FIELD_PRESSURE);
        d_env_field_cell *t = denv_find_field_cell(list[i], D_ENV_FIELD_TEMPERATURE);
        if (p) old_p[i] = p->values[0];
        if (t) old_t[i] = t->values[0];
    }

    for (i = 0u; i < count; ++i) {
        denv_chunk_entry *entry = list[i];
        d_chunk *nbr_chunk;
        denv_chunk_entry *nbr_entry;
        u32 j;

        if (!entry || !entry->chunk) {
            continue;
        }

        /* +X neighbor */
        nbr_chunk = d_world_find_chunk(w, entry->chunk->cx + 1, entry->chunk->cy);
        if (nbr_chunk) {
            nbr_entry = denv_find_entry(w, nbr_chunk);
            if (nbr_entry) {
                for (j = 0u; j < count; ++j) {
                    if (list[j] == nbr_entry) {
                        i64 diff_p = (i64)old_p[i] - (i64)old_p[j];
                        i64 diff_t = (i64)old_t[i] - (i64)old_t[j];
                        q16_16 transfer_p = (q16_16)(diff_p >> 3);
                        q16_16 transfer_t = (q16_16)(diff_t >> 3);
                        i64 tp = (i64)transfer_p * (i64)ticks;
                        i64 tt = (i64)transfer_t * (i64)ticks;
                        delta_p[i] -= tp; delta_p[j] += tp;
                        delta_t[i] -= tt; delta_t[j] += tt;
                        break;
                    }
                }
            }
        }

        /* +Y neighbor */
        nbr_chunk = d_world_find_chunk(w, entry->chunk->cx, entry->chunk->cy + 1);
        if (nbr_chunk) {
            nbr_entry = denv_find_entry(w, nbr_chunk);
            if (nbr_entry) {
                for (j = 0u; j < count; ++j) {
                    if (list[j] == nbr_entry) {
                        i64 diff_p = (i64)old_p[i] - (i64)old_p[j];
                        i64 diff_t = (i64)old_t[i] - (i64)old_t[j];
                        q16_16 transfer_p = (q16_16)(diff_p >> 3);
                        q16_16 transfer_t = (q16_16)(diff_t >> 3);
                        i64 tp = (i64)transfer_p * (i64)ticks;
                        i64 tt = (i64)transfer_t * (i64)ticks;
                        delta_p[i] -= tp; delta_p[j] += tp;
                        delta_t[i] -= tt; delta_t[j] += tt;
                        break;
                    }
                }
            }
        }
    }

    for (i = 0u; i < count; ++i) {
        d_env_field_cell *p = denv_find_field_cell(list[i], D_ENV_FIELD_PRESSURE);
        d_env_field_cell *t = denv_find_field_cell(list[i], D_ENV_FIELD_TEMPERATURE);
        if (p) {
            p->values[0] = denv_q16_from_i64_clamp((i64)old_p[i] + delta_p[i]);
        }
        if (t) {
            t->values[0] = denv_q16_from_i64_clamp((i64)old_t[i] + delta_t[i]);
        }
    }
}

void d_env_tick(d_world *w, u32 ticks) {
    u32 i;
    if (!w || ticks == 0u) {
        return;
    }

    for (i = 0u; i < g_env_chunk_count; ++i) {
        denv_chunk_entry *entry = &g_env_chunks[i];
        u32 f;
        if (entry->world != w) {
            continue;
        }
        if (!entry->fields || entry->field_count == 0u) {
            continue;
        }
        for (f = 0u; f < entry->field_count; ++f) {
            d_env_field_cell *cell = &entry->fields[f];
            const d_env_model_vtable *vt = denv_model_lookup(cell->desc.model_id);
            if (vt && vt->tick) {
                vt->tick(w, entry->chunk, cell, ticks);
            }
        }
    }

    denv_apply_atmo_diffusion(w, ticks);

    for (i = 0u; i < g_env_chunk_count; ++i) {
        denv_chunk_entry *entry = &g_env_chunks[i];
        if (entry->world != w) {
            continue;
        }
        if (entry->zone_count > 0u && entry->zones) {
            d_env_field_cell *p = denv_find_field_cell(entry, D_ENV_FIELD_PRESSURE);
            d_env_field_cell *t = denv_find_field_cell(entry, D_ENV_FIELD_TEMPERATURE);
            d_env_field_cell *h = denv_find_field_cell(entry, D_ENV_FIELD_HUMIDITY);
            if (p) entry->zones[0].pressure = p->values[0];
            if (t) entry->zones[0].temperature = t->values[0];
            if (h) entry->zones[0].humidity = h->values[0];
        }
    }

    d_env_volume_tick(w, ticks);
}

void denv_tick(d_world *w, u32 ticks) {
    d_env_tick(w, ticks);
}

static u16 denv_sample_at_impl(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_env_sample  *out_samples,
    u16            max_samples,
    int            apply_volume
) {
    d_chunk *chunk;
    denv_chunk_entry *entry;
    const d_env_volume *vol = (const d_env_volume *)0;
    u16 out_count;
    u32 i;

    if (!w || !out_samples || max_samples == 0u) {
        return 0u;
    }

    chunk = d_world_find_chunk((d_world *)w, (i32)(x >> Q32_32_FRAC_BITS), (i32)(y >> Q32_32_FRAC_BITS));
    if (!chunk) {
        return 0u;
    }
    entry = denv_find_entry((d_world *)w, chunk);
    if (!entry) {
        if (denv_init_chunk((d_world *)w, chunk) != 0) {
            return 0u;
        }
        entry = denv_find_entry((d_world *)w, chunk);
    }
    if (!entry || !entry->fields || entry->field_count == 0u) {
        return 0u;
    }

    if (apply_volume) {
        d_env_volume_id vid = d_env_volume_find_at(w, x, y, z);
        vol = d_env_volume_get(w, vid);
    }

    out_count = 0u;
    for (i = 0u; i < entry->field_count && out_count < max_samples; ++i) {
        d_env_field_cell *cell = &entry->fields[i];
        const d_env_model_vtable *vt = denv_model_lookup(cell->desc.model_id);
        u16 j;

        if (vt && vt->compute_base) {
            vt->compute_base(w, chunk, cell);
        }

        out_samples[out_count].field_id = cell->desc.field_id;
        out_samples[out_count].model_id = cell->desc.model_id;
        for (j = 0u; j < 4u; ++j) {
            out_samples[out_count].values[j] = cell->values[j];
        }
        if (vol) {
            switch (cell->desc.field_id) {
            case D_ENV_FIELD_PRESSURE:
                out_samples[out_count].values[0] = vol->pressure;
                break;
            case D_ENV_FIELD_TEMPERATURE:
                out_samples[out_count].values[0] = vol->temperature;
                break;
            case D_ENV_FIELD_GAS0_FRACTION:
                out_samples[out_count].values[0] = vol->gas0_fraction;
                break;
            case D_ENV_FIELD_GAS1_FRACTION:
                out_samples[out_count].values[0] = vol->gas1_fraction;
                break;
            case D_ENV_FIELD_HUMIDITY:
                out_samples[out_count].values[0] = vol->humidity;
                break;
            default:
                break;
            }
        }
        out_count += 1u;
    }

    return out_count;
}

u16 d_env_sample_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_env_sample  *out_samples,
    u16            max_samples
) {
    return denv_sample_at_impl(w, x, y, z, out_samples, max_samples, 1);
}

u16 d_env_sample_exterior_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z,
    d_env_sample  *out_samples,
    u16            max_samples
) {
    return denv_sample_at_impl(w, x, y, z, out_samples, max_samples, 0);
}

static int denv_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    denv_chunk_entry *entry;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;
    (void)w;

    if (!out) {
        return -1;
    }
    entry = denv_find_entry(w, chunk);
    if (!entry) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    /* zone_count + portal_count stored as u32 */
    total = 8u;
    total += entry->zone_count * (sizeof(denv_zone_state) - sizeof(d_tlv_blob) + sizeof(u32));
    total += entry->portal_count * (sizeof(denv_portal) - sizeof(d_tlv_blob) + sizeof(u32));
    for (i = 0u; i < entry->zone_count; ++i) {
        total += entry->zones[i].extra.len;
    }
    for (i = 0u; i < entry->portal_count; ++i) {
        total += entry->portals[i].extra.len;
    }

    /* Field cells appended after portals (field_count + fixed-size cells). */
    total += 4u;
    if (entry->field_count > 0u && entry->fields) {
        u32 field_size = 6u + (sizeof(q16_16) * 4u);
        total += entry->field_count * field_size;
    }

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &entry->zone_count, sizeof(u32));
    dst += 4u;
    memcpy(dst, &entry->portal_count, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < entry->zone_count; ++i) {
        u32 extra_len = entry->zones[i].extra.len;
        memcpy(dst, &entry->zones[i].id, sizeof(denv_zone_id));
        dst += sizeof(denv_zone_id);
        memcpy(dst, &entry->zones[i].temperature, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &entry->zones[i].pressure, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &entry->zones[i].humidity, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, entry->zones[i].gas_mix, sizeof(q16_16) * 4u);
        dst += sizeof(q16_16) * 4u;
        memcpy(dst, &entry->zones[i].pollution, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &entry->zones[i].light_level, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &extra_len, sizeof(u32));
        dst += sizeof(u32);
        if (extra_len > 0u && entry->zones[i].extra.ptr) {
            memcpy(dst, entry->zones[i].extra.ptr, extra_len);
            dst += extra_len;
        }
    }

    for (i = 0u; i < entry->portal_count; ++i) {
        u32 extra_len = entry->portals[i].extra.len;
        memcpy(dst, &entry->portals[i].a, sizeof(denv_zone_id));
        dst += sizeof(denv_zone_id);
        memcpy(dst, &entry->portals[i].b, sizeof(denv_zone_id));
        dst += sizeof(denv_zone_id);
        memcpy(dst, &entry->portals[i].area, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &entry->portals[i].permeability, sizeof(q16_16));
        dst += sizeof(q16_16);
        memcpy(dst, &extra_len, sizeof(u32));
        dst += sizeof(u32);
        if (extra_len > 0u && entry->portals[i].extra.ptr) {
            memcpy(dst, entry->portals[i].extra.ptr, extra_len);
            dst += extra_len;
        }
    }

    {
        u32 field_count = entry->field_count;
        memcpy(dst, &field_count, sizeof(u32));
        dst += 4u;
        for (i = 0u; i < field_count; ++i) {
            u16 fid = entry->fields ? entry->fields[i].desc.field_id : 0u;
            u16 mid = entry->fields ? entry->fields[i].desc.model_id : 0u;
            u16 flg = entry->fields ? entry->fields[i].desc.flags : 0u;
            u16 j;
            memcpy(dst, &fid, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &mid, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &flg, sizeof(u16)); dst += sizeof(u16);
            for (j = 0u; j < 4u; ++j) {
                q16_16 v = entry->fields ? entry->fields[i].values[j] : 0;
                memcpy(dst, &v, sizeof(q16_16));
                dst += sizeof(q16_16);
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int denv_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    denv_chunk_entry *entry;
    const unsigned char *ptr;
    u32 remaining;
    u32 zone_count;
    u32 portal_count;
    u32 field_count = 0u;
    u32 i;
    (void)w;

    if (!chunk || !in) {
        return -1;
    }
    if (in->len == 0u) {
        return 0;
    }
    if (!in->ptr || in->len < 8u) {
        return -1;
    }

    ptr = in->ptr;
    remaining = in->len;

    memcpy(&zone_count, ptr, sizeof(u32));
    ptr += 4u;
    memcpy(&portal_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 8u;

    entry = denv_ensure_entry(w, chunk);
    if (!entry) {
        return -1;
    }
    if (entry->zones) {
        u32 z;
        for (z = 0u; z < entry->zone_count; ++z) {
            if (entry->zones[z].extra.ptr) {
                free(entry->zones[z].extra.ptr);
            }
        }
        free(entry->zones);
    }
    if (entry->portals) {
        u32 p;
        for (p = 0u; p < entry->portal_count; ++p) {
            if (entry->portals[p].extra.ptr) {
                free(entry->portals[p].extra.ptr);
            }
        }
        free(entry->portals);
    }
    if (entry->fields) {
        free(entry->fields);
    }
    entry->zones = (denv_zone_state *)0;
    entry->zone_count = 0u;
    entry->portals = (denv_portal *)0;
    entry->portal_count = 0u;
    entry->fields = (d_env_field_cell *)0;
    entry->field_count = 0u;
    entry->field_capacity = 0u;

    if (zone_count > 0u) {
        entry->zones = (denv_zone_state *)malloc(sizeof(denv_zone_state) * zone_count);
        if (!entry->zones) {
            return -1;
        }
        memset(entry->zones, 0, sizeof(denv_zone_state) * zone_count);
        entry->zone_count = zone_count;
        for (i = 0u; i < zone_count; ++i) {
            u32 extra_len;
            if (remaining < sizeof(denv_zone_id) + (sizeof(q16_16) * 8u) + sizeof(u32)) {
                return -1;
            }
            memcpy(&entry->zones[i].id, ptr, sizeof(denv_zone_id));
            ptr += sizeof(denv_zone_id);
            memcpy(&entry->zones[i].temperature, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&entry->zones[i].pressure, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&entry->zones[i].humidity, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(entry->zones[i].gas_mix, ptr, sizeof(q16_16) * 4u);
            ptr += sizeof(q16_16) * 4u;
            memcpy(&entry->zones[i].pollution, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&entry->zones[i].light_level, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&extra_len, ptr, sizeof(u32));
            ptr += sizeof(u32);
            remaining -= sizeof(denv_zone_id) + (sizeof(q16_16) * 8u) + sizeof(u32);
            entry->zones[i].extra.len = extra_len;
            if (extra_len > 0u) {
                entry->zones[i].extra.ptr = (unsigned char *)malloc(extra_len);
                if (!entry->zones[i].extra.ptr) {
                    return -1;
                }
                if (remaining < extra_len) {
                    return -1;
                }
                memcpy(entry->zones[i].extra.ptr, ptr, extra_len);
                ptr += extra_len;
                remaining -= extra_len;
            } else {
                entry->zones[i].extra.ptr = (unsigned char *)0;
            }
        }
    }

    if (portal_count > 0u) {
        entry->portals = (denv_portal *)malloc(sizeof(denv_portal) * portal_count);
        if (!entry->portals) {
            return -1;
        }
        memset(entry->portals, 0, sizeof(denv_portal) * portal_count);
        entry->portal_count = portal_count;
        for (i = 0u; i < portal_count; ++i) {
            u32 extra_len;
            if (remaining < (sizeof(denv_zone_id) * 2u) + (sizeof(q16_16) * 2u) + sizeof(u32)) {
                return -1;
            }
            memcpy(&entry->portals[i].a, ptr, sizeof(denv_zone_id));
            ptr += sizeof(denv_zone_id);
            memcpy(&entry->portals[i].b, ptr, sizeof(denv_zone_id));
            ptr += sizeof(denv_zone_id);
            memcpy(&entry->portals[i].area, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&entry->portals[i].permeability, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            memcpy(&extra_len, ptr, sizeof(u32));
            ptr += sizeof(u32);
            remaining -= (sizeof(denv_zone_id) * 2u) + (sizeof(q16_16) * 2u) + sizeof(u32);
            entry->portals[i].extra.len = extra_len;
            if (extra_len > 0u) {
                entry->portals[i].extra.ptr = (unsigned char *)malloc(extra_len);
                if (!entry->portals[i].extra.ptr) {
                    return -1;
                }
                if (remaining < extra_len) {
                    return -1;
                }
                memcpy(entry->portals[i].extra.ptr, ptr, extra_len);
                ptr += extra_len;
                remaining -= extra_len;
            } else {
                entry->portals[i].extra.ptr = (unsigned char *)0;
            }
        }
    }

    if (remaining >= 4u) {
        memcpy(&field_count, ptr, sizeof(u32));
        ptr += 4u;
        remaining -= 4u;
        if (field_count > 0u) {
            if (field_count > DENV_MAX_FIELDS_PER_CHUNK) {
                return -1;
            }
            entry->fields = (d_env_field_cell *)malloc(sizeof(d_env_field_cell) * field_count);
            if (!entry->fields) {
                return -1;
            }
            memset(entry->fields, 0, sizeof(d_env_field_cell) * field_count);
            entry->field_capacity = field_count;
            entry->field_count = field_count;
            for (i = 0u; i < field_count; ++i) {
                u16 fid;
                u16 mid;
                u16 flg;
                u16 j;
                u32 need = (u32)(sizeof(u16) * 3u) + (u32)(sizeof(q16_16) * 4u);
                if (remaining < need) {
                    return -1;
                }
                memcpy(&fid, ptr, sizeof(u16)); ptr += sizeof(u16);
                memcpy(&mid, ptr, sizeof(u16)); ptr += sizeof(u16);
                memcpy(&flg, ptr, sizeof(u16)); ptr += sizeof(u16);
                remaining -= (u32)sizeof(u16) * 3u;
                entry->fields[i].desc.field_id = fid;
                entry->fields[i].desc.model_id = mid;
                entry->fields[i].desc.flags = flg;
                for (j = 0u; j < 4u; ++j) {
                    memcpy(&entry->fields[i].values[j], ptr, sizeof(q16_16));
                    ptr += sizeof(q16_16);
                    remaining -= sizeof(q16_16);
                }
            }
        }
    }

    if (entry->field_capacity == 0u) {
        if (denv_reserve_fields(entry, 8u) != 0) {
            return -1;
        }
    }
    denv_init_default_fields(w, chunk, entry);

    return 0;
}

static int denv_save_instance(d_world *w, d_tlv_blob *out) {
    return d_env_volume_save_instance(w, out);
}

static int denv_load_instance(d_world *w, const d_tlv_blob *in) {
    return d_env_volume_load_instance(w, in);
}

static void denv_worldgen_populate(struct d_world *w, struct d_chunk *chunk) {
    if (!w || !chunk) {
        return;
    }
    (void)denv_init_chunk((d_world *)w, (d_chunk *)chunk);
}

static void denv_register_models(void) {
    (void)d_env_register_model(&g_atmo_vt);
    {
        static const d_worldgen_provider prov = {
            2u,
            "env_default_provider",
            (const d_worldgen_provider_id *)0,
            denv_worldgen_populate
        };
        d_worldgen_register(&prov);
    }
}

static void denv_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static void denv_init_instance_subsys(d_world *w) {
    u32 i;
    u32 dst = 0u;
    for (i = 0u; i < g_env_chunk_count; ++i) {
        if (g_env_chunks[i].world == w) {
            if (g_env_chunks[i].zones) {
                u32 z;
                for (z = 0u; z < g_env_chunks[i].zone_count; ++z) {
                    if (g_env_chunks[i].zones[z].extra.ptr) {
                        free(g_env_chunks[i].zones[z].extra.ptr);
                    }
                }
                free(g_env_chunks[i].zones);
            }
            if (g_env_chunks[i].portals) {
                u32 p;
                for (p = 0u; p < g_env_chunks[i].portal_count; ++p) {
                    if (g_env_chunks[i].portals[p].extra.ptr) {
                        free(g_env_chunks[i].portals[p].extra.ptr);
                    }
                }
                free(g_env_chunks[i].portals);
            }
            g_env_chunks[i].zones = (denv_zone_state *)0;
            g_env_chunks[i].portals = (denv_portal *)0;
            g_env_chunks[i].zone_count = 0u;
            g_env_chunks[i].portal_count = 0u;
            denv_free_fields(&g_env_chunks[i]);
        } else {
            if (dst != i) {
                g_env_chunks[dst] = g_env_chunks[i];
            }
            dst += 1u;
        }
    }
    g_env_chunk_count = dst;

    d_env_volume_init_instance(w);
}

static const d_subsystem_desc g_env_subsystem = {
    D_SUBSYS_ENV,
    "env",
    2u,
    denv_register_models,
    denv_load_protos,
    denv_init_instance_subsys,
    d_env_tick,
    denv_save_chunk,
    denv_load_chunk,
    denv_save_instance,
    denv_load_instance
};

void d_env_init(void) {
    if (g_env_registered) {
        return;
    }
    if (d_subsystem_register(&g_env_subsystem) == 0) {
        g_env_registered = 1;
    }
}
