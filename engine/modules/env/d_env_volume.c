/*
FILE: source/domino/env/d_env_volume.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / env/d_env_volume
RESPONSIBILITY: Implements `d_env_volume`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "domino/core/fixed.h"

#define DENV_MAX_VOLUMES 1024u
#define DENV_MAX_EDGES   2048u

typedef struct denv_volume_entry_s {
    d_world      *world;
    d_env_volume  vol;
    int           in_use;
} denv_volume_entry;

typedef struct denv_edge_entry_s {
    d_world          *world;
    d_env_volume_edge edge;
    int              in_use;
} denv_edge_entry;

static denv_volume_entry g_volumes[DENV_MAX_VOLUMES];
static denv_edge_entry   g_edges[DENV_MAX_EDGES];
static d_env_volume_id   g_next_volume_id = 1u;

void d_env_volume_init_instance(d_world *w) {
    u32 i;
    u32 dst;
    if (!w) {
        return;
    }

    dst = 0u;
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == w) {
            memset(&g_volumes[i], 0, sizeof(g_volumes[i]));
        } else {
            if (dst != i) {
                g_volumes[dst] = g_volumes[i];
            }
            dst += 1u;
        }
    }
    for (i = dst; i < DENV_MAX_VOLUMES; ++i) {
        memset(&g_volumes[i], 0, sizeof(g_volumes[i]));
    }

    dst = 0u;
    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        if (g_edges[i].in_use && g_edges[i].world == w) {
            memset(&g_edges[i], 0, sizeof(g_edges[i]));
        } else {
            if (dst != i) {
                g_edges[dst] = g_edges[i];
            }
            dst += 1u;
        }
    }
    for (i = dst; i < DENV_MAX_EDGES; ++i) {
        memset(&g_edges[i], 0, sizeof(g_edges[i]));
    }
}

static denv_volume_entry *denv_find_volume_entry(d_world *w, d_env_volume_id id) {
    u32 i;
    if (!w || id == 0u) {
        return (denv_volume_entry *)0;
    }
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == w && g_volumes[i].vol.id == id) {
            return &g_volumes[i];
        }
    }
    return (denv_volume_entry *)0;
}

const d_env_volume *d_env_volume_get(const d_world *w, d_env_volume_id id) {
    denv_volume_entry *entry;
    entry = denv_find_volume_entry((d_world *)w, id);
    if (!entry) {
        return (const d_env_volume *)0;
    }
    return &entry->vol;
}

u32 d_env_volume_count(const d_world *w) {
    u32 i;
    u32 count;
    if (!w) {
        return 0u;
    }
    count = 0u;
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == (d_world *)w) {
            count += 1u;
        }
    }
    return count;
}

const d_env_volume *d_env_volume_get_by_index(const d_world *w, u32 index) {
    u32 i;
    u32 seen;
    if (!w) {
        return (const d_env_volume *)0;
    }
    seen = 0u;
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == (d_world *)w) {
            if (seen == index) {
                return &g_volumes[i].vol;
            }
            seen += 1u;
        }
    }
    return (const d_env_volume *)0;
}

static denv_volume_entry *denv_alloc_volume_slot(void) {
    u32 i;
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (!g_volumes[i].in_use) {
            return &g_volumes[i];
        }
    }
    return (denv_volume_entry *)0;
}

static denv_edge_entry *denv_alloc_edge_slot(void) {
    u32 i;
    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        if (!g_edges[i].in_use) {
            return &g_edges[i];
        }
    }
    return (denv_edge_entry *)0;
}

static int denv_point_in_aabb(q32_32 x, q32_32 y, q32_32 z, const d_env_volume *v) {
    if (!v) {
        return 0;
    }
    if (x < v->min_x || x > v->max_x) return 0;
    if (y < v->min_y || y > v->max_y) return 0;
    if (z < v->min_z || z > v->max_z) return 0;
    return 1;
}

d_env_volume_id d_env_volume_find_at(
    const d_world *w,
    q32_32         x,
    q32_32         y,
    q32_32         z
) {
    u32 i;
    if (!w) {
        return 0u;
    }
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == (d_world *)w) {
            if (denv_point_in_aabb(x, y, z, &g_volumes[i].vol)) {
                return g_volumes[i].vol.id;
            }
        }
    }
    return 0u;
}

d_env_volume_id d_env_volume_create(d_world *w, const d_env_volume *vol) {
    denv_volume_entry *slot;
    d_env_volume tmp;
    if (!w || !vol) {
        return 0u;
    }
    if (g_next_volume_id == 0u) {
        g_next_volume_id = 1u;
    }
    if (denv_find_volume_entry(w, vol->id) != (denv_volume_entry *)0 && vol->id != 0u) {
        return 0u;
    }
    slot = denv_alloc_volume_slot();
    if (!slot) {
        return 0u;
    }
    tmp = *vol;
    if (tmp.id == 0u) {
        tmp.id = g_next_volume_id++;
    } else if (tmp.id >= g_next_volume_id) {
        g_next_volume_id = tmp.id + 1u;
    }
    slot->world = w;
    slot->vol = tmp;
    slot->in_use = 1;
    return tmp.id;
}

int d_env_volume_destroy(d_world *w, d_env_volume_id id) {
    denv_volume_entry *entry;
    u32 i;
    if (!w || id == 0u) {
        return -1;
    }
    entry = denv_find_volume_entry(w, id);
    if (!entry) {
        return -1;
    }
    memset(entry, 0, sizeof(*entry));

    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        if (g_edges[i].in_use && g_edges[i].world == w) {
            if (g_edges[i].edge.a == id || g_edges[i].edge.b == id) {
                memset(&g_edges[i], 0, sizeof(g_edges[i]));
            }
        }
    }
    return 0;
}

int d_env_volume_remove_owned_by(d_world *w, u32 owner_struct_eid, u32 owner_vehicle_eid) {
    u32 i;
    int removed = 0;
    if (!w) {
        return -1;
    }
    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (!g_volumes[i].in_use || g_volumes[i].world != w) {
            continue;
        }
        if (owner_struct_eid != 0u && g_volumes[i].vol.owner_struct_eid == owner_struct_eid) {
            d_env_volume_destroy(w, g_volumes[i].vol.id);
            removed += 1;
            continue;
        }
        if (owner_vehicle_eid != 0u && g_volumes[i].vol.owner_vehicle_eid == owner_vehicle_eid) {
            d_env_volume_destroy(w, g_volumes[i].vol.id);
            removed += 1;
            continue;
        }
    }
    return removed;
}

int d_env_volume_add_edge(d_world *w, const d_env_volume_edge *edge) {
    denv_edge_entry *slot;
    if (!w || !edge) {
        return -1;
    }
    if (edge->a == edge->b) {
        return -2;
    }
    if (edge->a == 0u && edge->b == 0u) {
        return -2;
    }
    if (edge->a != 0u && !denv_find_volume_entry(w, edge->a)) {
        return -3;
    }
    if (edge->b != 0u && !denv_find_volume_entry(w, edge->b)) {
        return -3;
    }
    slot = denv_alloc_edge_slot();
    if (!slot) {
        return -4;
    }
    slot->world = w;
    slot->edge = *edge;
    slot->in_use = 1;
    return 0;
}

static q16_16 denv_sample_field0(const d_env_sample *samples, u16 count, d_env_field_id field_id) {
    u16 i;
    if (!samples || count == 0u) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (samples[i].field_id == field_id) {
            return samples[i].values[0];
        }
    }
    return 0;
}

void d_env_volume_tick(d_world *w, u32 ticks) {
    d_env_volume_id ids[DENV_MAX_VOLUMES];
    q16_16 dp[DENV_MAX_VOLUMES];
    q16_16 dt[DENV_MAX_VOLUMES];
    q16_16 dg0[DENV_MAX_VOLUMES];
    q16_16 dg1[DENV_MAX_VOLUMES];
    q16_16 dh[DENV_MAX_VOLUMES];
    q16_16 dpol[DENV_MAX_VOLUMES];
    u32 count = 0u;
    u32 i;

    if (!w || ticks == 0u) {
        return;
    }

    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == w) {
            if (count < DENV_MAX_VOLUMES) {
                ids[count] = g_volumes[i].vol.id;
                dp[count] = 0;
                dt[count] = 0;
                dg0[count] = 0;
                dg1[count] = 0;
                dh[count] = 0;
                dpol[count] = 0;
                count += 1u;
            }
        }
    }
    if (count == 0u) {
        return;
    }

    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        denv_edge_entry *e;
        denv_volume_entry *va;
        denv_volume_entry *vb;
        u32 ia, ib;
        q16_16 gas_k;
        q16_16 heat_k;
        q16_16 diff;
        q16_16 transfer;
        int a_is_ext;
        int b_is_ext;

        e = &g_edges[i];
        if (!e->in_use || e->world != w) {
            continue;
        }
        a_is_ext = (e->edge.a == 0u) ? 1 : 0;
        b_is_ext = (e->edge.b == 0u) ? 1 : 0;
        va = a_is_ext ? (denv_volume_entry *)0 : denv_find_volume_entry(w, e->edge.a);
        vb = b_is_ext ? (denv_volume_entry *)0 : denv_find_volume_entry(w, e->edge.b);
        if (!a_is_ext && !va) {
            continue;
        }
        if (!b_is_ext && !vb) {
            continue;
        }
        ia = 0xFFFFFFFFu;
        ib = 0xFFFFFFFFu;
        if (!a_is_ext) {
            for (ia = 0u; ia < count; ++ia) {
                if (ids[ia] == va->vol.id) break;
            }
            if (ia >= count) {
                continue;
            }
        }
        if (!b_is_ext) {
            for (ib = 0u; ib < count; ++ib) {
                if (ids[ib] == vb->vol.id) break;
            }
            if (ib >= count) {
                continue;
            }
        }
        if (!a_is_ext && !b_is_ext && ia == ib) {
            continue;
        }

        gas_k = e->edge.gas_conductance;
        heat_k = e->edge.heat_conductance;

        if (!a_is_ext && !b_is_ext) {
            diff = d_q16_16_sub(vb->vol.pressure, va->vol.pressure);
            transfer = d_q16_16_mul(diff, gas_k);
            dp[ia] = d_q16_16_add(dp[ia], transfer);
            dp[ib] = d_q16_16_sub(dp[ib], transfer);

            diff = d_q16_16_sub(vb->vol.temperature, va->vol.temperature);
            transfer = d_q16_16_mul(diff, heat_k);
            dt[ia] = d_q16_16_add(dt[ia], transfer);
            dt[ib] = d_q16_16_sub(dt[ib], transfer);

            diff = d_q16_16_sub(vb->vol.gas0_fraction, va->vol.gas0_fraction);
            transfer = d_q16_16_mul(diff, gas_k);
            dg0[ia] = d_q16_16_add(dg0[ia], transfer);
            dg0[ib] = d_q16_16_sub(dg0[ib], transfer);

            diff = d_q16_16_sub(vb->vol.gas1_fraction, va->vol.gas1_fraction);
            transfer = d_q16_16_mul(diff, gas_k);
            dg1[ia] = d_q16_16_add(dg1[ia], transfer);
            dg1[ib] = d_q16_16_sub(dg1[ib], transfer);

            diff = d_q16_16_sub(vb->vol.humidity, va->vol.humidity);
            transfer = d_q16_16_mul(diff, gas_k);
            dh[ia] = d_q16_16_add(dh[ia], transfer);
            dh[ib] = d_q16_16_sub(dh[ib], transfer);

            diff = d_q16_16_sub(vb->vol.pollutant, va->vol.pollutant);
            transfer = d_q16_16_mul(diff, gas_k);
            dpol[ia] = d_q16_16_add(dpol[ia], transfer);
            dpol[ib] = d_q16_16_sub(dpol[ib], transfer);
        } else {
            denv_volume_entry *v = a_is_ext ? vb : va;
            u32 iv = a_is_ext ? ib : ia;
            d_env_sample samples[16];
            u16 sample_count;
            q32_32 cx;
            q32_32 cy;
            q32_32 cz;
            q16_16 ext_p;
            q16_16 ext_t;
            q16_16 ext_g0;
            q16_16 ext_g1;
            q16_16 ext_h;

            if (!v || iv >= count) {
                continue;
            }

            cx = (q32_32)((v->vol.min_x + v->vol.max_x) >> 1);
            cy = (q32_32)((v->vol.min_y + v->vol.max_y) >> 1);
            cz = (q32_32)((v->vol.min_z + v->vol.max_z) >> 1);

            sample_count = d_env_sample_exterior_at(w, cx, cy, cz, samples, 16u);
            ext_p = denv_sample_field0(samples, sample_count, D_ENV_FIELD_PRESSURE);
            ext_t = denv_sample_field0(samples, sample_count, D_ENV_FIELD_TEMPERATURE);
            ext_g0 = denv_sample_field0(samples, sample_count, D_ENV_FIELD_GAS0_FRACTION);
            ext_g1 = denv_sample_field0(samples, sample_count, D_ENV_FIELD_GAS1_FRACTION);
            ext_h = denv_sample_field0(samples, sample_count, D_ENV_FIELD_HUMIDITY);

            diff = d_q16_16_sub(ext_p, v->vol.pressure);
            transfer = d_q16_16_mul(diff, gas_k);
            dp[iv] = d_q16_16_add(dp[iv], transfer);

            diff = d_q16_16_sub(ext_t, v->vol.temperature);
            transfer = d_q16_16_mul(diff, heat_k);
            dt[iv] = d_q16_16_add(dt[iv], transfer);

            diff = d_q16_16_sub(ext_g0, v->vol.gas0_fraction);
            transfer = d_q16_16_mul(diff, gas_k);
            dg0[iv] = d_q16_16_add(dg0[iv], transfer);

            diff = d_q16_16_sub(ext_g1, v->vol.gas1_fraction);
            transfer = d_q16_16_mul(diff, gas_k);
            dg1[iv] = d_q16_16_add(dg1[iv], transfer);

            diff = d_q16_16_sub(ext_h, v->vol.humidity);
            transfer = d_q16_16_mul(diff, gas_k);
            dh[iv] = d_q16_16_add(dh[iv], transfer);
        }
    }

    for (i = 0u; i < count; ++i) {
        denv_volume_entry *v;
        q16_16 mult;
        v = denv_find_volume_entry(w, ids[i]);
        if (!v) {
            continue;
        }
        mult = d_q16_16_from_int((i32)ticks);
        v->vol.pressure = d_q16_16_add(v->vol.pressure, d_q16_16_mul(dp[i], mult));
        v->vol.temperature = d_q16_16_add(v->vol.temperature, d_q16_16_mul(dt[i], mult));
        v->vol.gas0_fraction = d_q16_16_add(v->vol.gas0_fraction, d_q16_16_mul(dg0[i], mult));
        v->vol.gas1_fraction = d_q16_16_add(v->vol.gas1_fraction, d_q16_16_mul(dg1[i], mult));
        v->vol.humidity = d_q16_16_add(v->vol.humidity, d_q16_16_mul(dh[i], mult));
        v->vol.pollutant = d_q16_16_add(v->vol.pollutant, d_q16_16_mul(dpol[i], mult));
    }
}

int d_env_volume_save_instance(d_world *w, d_tlv_blob *out) {
    u32 vol_count = 0u;
    u32 edge_count = 0u;
    u32 total = 0u;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!out) {
        return -1;
    }

    if (!w) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == w) {
            vol_count += 1u;
        }
    }
    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        if (g_edges[i].in_use && g_edges[i].world == w) {
            edge_count += 1u;
        }
    }

    if (vol_count == 0u && edge_count == 0u) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total = 4u + 4u;
    total += vol_count * (4u + (sizeof(q32_32) * 6u) + (sizeof(u32) * 2u) + (sizeof(q16_16) * 6u));
    total += edge_count * ((sizeof(d_env_volume_id) * 2u) + (sizeof(q16_16) * 2u));

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &vol_count, sizeof(u32));
    dst += 4u;
    memcpy(dst, &edge_count, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < DENV_MAX_VOLUMES; ++i) {
        if (g_volumes[i].in_use && g_volumes[i].world == w) {
            const d_env_volume *v = &g_volumes[i].vol;
            memcpy(dst, &v->id, sizeof(d_env_volume_id));
            dst += sizeof(d_env_volume_id);
            memcpy(dst, &v->min_x, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->min_y, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->min_z, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->max_x, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->max_y, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->max_z, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &v->owner_struct_eid, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &v->owner_vehicle_eid, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &v->pressure, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &v->temperature, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &v->gas0_fraction, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &v->gas1_fraction, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &v->humidity, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &v->pollutant, sizeof(q16_16)); dst += sizeof(q16_16);
        }
    }

    for (i = 0u; i < DENV_MAX_EDGES; ++i) {
        if (g_edges[i].in_use && g_edges[i].world == w) {
            const d_env_volume_edge *e = &g_edges[i].edge;
            memcpy(dst, &e->a, sizeof(d_env_volume_id));
            dst += sizeof(d_env_volume_id);
            memcpy(dst, &e->b, sizeof(d_env_volume_id));
            dst += sizeof(d_env_volume_id);
            memcpy(dst, &e->gas_conductance, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &e->heat_conductance, sizeof(q16_16));
            dst += sizeof(q16_16);
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

int d_env_volume_load_instance(d_world *w, const d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 vol_count;
    u32 edge_count;
    u32 i;

    if (!w || !in) {
        return -1;
    }
    if (in->len == 0u) {
        d_env_volume_init_instance(w);
        return 0;
    }
    if (!in->ptr || in->len < 8u) {
        return -1;
    }

    d_env_volume_init_instance(w);

    ptr = in->ptr;
    remaining = in->len;
    memcpy(&vol_count, ptr, sizeof(u32));
    ptr += 4u;
    memcpy(&edge_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 8u;

    for (i = 0u; i < vol_count; ++i) {
        d_env_volume v;
        denv_volume_entry *slot;
        u32 need = sizeof(d_env_volume_id) + (sizeof(q32_32) * 6u) + (sizeof(u32) * 2u) + (sizeof(q16_16) * 6u);
        if (remaining < need) {
            return -1;
        }
        memset(&v, 0, sizeof(v));
        memcpy(&v.id, ptr, sizeof(d_env_volume_id));
        ptr += sizeof(d_env_volume_id);
        memcpy(&v.min_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.min_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.min_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.max_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.max_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.max_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&v.owner_struct_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
        memcpy(&v.owner_vehicle_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
        memcpy(&v.pressure, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&v.temperature, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&v.gas0_fraction, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&v.gas1_fraction, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&v.humidity, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&v.pollutant, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        remaining -= need;

        slot = denv_alloc_volume_slot();
        if (!slot) {
            return -1;
        }
        slot->world = w;
        slot->vol = v;
        slot->in_use = 1;
        if (v.id >= g_next_volume_id) {
            g_next_volume_id = v.id + 1u;
        }
    }

    for (i = 0u; i < edge_count; ++i) {
        d_env_volume_edge e;
        denv_edge_entry *slot;
        u32 need = (sizeof(d_env_volume_id) * 2u) + (sizeof(q16_16) * 2u);
        if (remaining < need) {
            return -1;
        }
        memset(&e, 0, sizeof(e));
        memcpy(&e.a, ptr, sizeof(d_env_volume_id));
        ptr += sizeof(d_env_volume_id);
        memcpy(&e.b, ptr, sizeof(d_env_volume_id));
        ptr += sizeof(d_env_volume_id);
        memcpy(&e.gas_conductance, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&e.heat_conductance, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        remaining -= need;

        slot = denv_alloc_edge_slot();
        if (!slot) {
            return -1;
        }
        slot->world = w;
        slot->edge = e;
        slot->in_use = 1;
    }

    return 0;
}
