#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/core/fixed.h"
#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "env/d_env.h"
#include "env/d_env_model.h"

#define DENV_MAX_MODELS          8u
#define DENV_MAX_CHUNK_ENTRIES 256u

typedef struct denv_chunk_entry {
    d_world         *world;
    d_chunk         *chunk;
    denv_zone_state *zones;
    u32              zone_count;
    denv_portal     *portals;
    u32              portal_count;
} denv_chunk_entry;

static denv_model_vtable g_env_models[DENV_MAX_MODELS];
static u32 g_env_model_count = 0u;

static denv_chunk_entry g_env_chunks[DENV_MAX_CHUNK_ENTRIES];
static u32 g_env_chunk_count = 0u;

static int g_env_registered = 0;

static const denv_model_vtable *denv_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_env_model_count; ++i) {
        if (g_env_models[i].model_id == model_id) {
            return &g_env_models[i];
        }
    }
    return (const denv_model_vtable *)0;
}

int denv_register_model(const denv_model_vtable *vt) {
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
    if (g_env_model_count >= DENV_MAX_MODELS) {
        return -3;
    }
    g_env_models[g_env_model_count] = *vt;

    desc.family_id = D_MODEL_FAMILY_ENV;
    desc.model_id = vt->model_id;
    desc.name = "env_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_env_models[g_env_model_count];

    if (d_model_register(&desc) != 0) {
        return -4;
    }

    g_env_model_count += 1u;
    return 0;
}

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
    const denv_model_vtable *vt;
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

    vt = denv_model_lookup(1u);
    if (vt && vt->init_chunk) {
        vt->init_chunk(w, chunk);
    }
    return 0;
}

void denv_tick(d_world *w, u32 ticks) {
    u32 i;
    for (i = 0u; i < g_env_chunk_count; ++i) {
        denv_chunk_entry *entry = &g_env_chunks[i];
        const denv_model_vtable *vt;
        if (entry->world != w) {
            continue;
        }
        vt = denv_model_lookup(1u);
        if (vt && vt->tick) {
            vt->tick(w,
                     entry->chunk,
                     entry->zones,
                     entry->zone_count,
                     entry->portals,
                     entry->portal_count,
                     ticks);
        }
    }
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
        free(entry->zones);
    }
    if (entry->portals) {
        free(entry->portals);
    }
    entry->zones = (denv_zone_state *)0;
    entry->zone_count = 0u;
    entry->portals = (denv_portal *)0;
    entry->portal_count = 0u;

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

    return 0;
}

static int denv_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int denv_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void denv_register_dummy_model(void) {
    denv_model_vtable vt;
    memset(&vt, 0, sizeof(vt));
    vt.model_id = 1u;
    vt.init_chunk = (void (*)(d_world *, d_chunk *))0;
    vt.tick = (void (*)(d_world *, d_chunk *, denv_zone_state *, u32, denv_portal *, u32, u32))0;
    denv_register_model(&vt);
}

static void denv_register_models(void) {
    denv_register_dummy_model();
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
        } else {
            if (dst != i) {
                g_env_chunks[dst] = g_env_chunks[i];
            }
            dst += 1u;
        }
    }
    g_env_chunk_count = dst;
}

static const d_subsystem_desc g_env_subsystem = {
    D_SUBSYS_ENV,
    "env",
    1u,
    denv_register_models,
    denv_load_protos,
    denv_init_instance_subsys,
    denv_tick,
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
