#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "trans/d_trans.h"
#include "trans/d_trans_model.h"

#define DTRANS_MAX_MODELS     8u
#define DTRANS_MAX_INSTANCES 64u

typedef struct d_trans_entry {
    d_world           *world;
    d_spline_instance  inst;
    u16                model_id; /* placeholder for future profile->model mapping */
    int                in_use;
} d_trans_entry;

static dtrans_model_vtable g_trans_models[DTRANS_MAX_MODELS];
static u32 g_trans_model_count = 0u;

static d_trans_entry g_trans_entries[DTRANS_MAX_INSTANCES];
static d_spline_instance_id g_trans_next_id = 1u;
static int g_trans_registered = 0;

int dtrans_register_model(const dtrans_model_vtable *vt) {
    d_model_desc desc;
    u32 i;
    if (!vt || vt->model_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_trans_model_count; ++i) {
        if (g_trans_models[i].model_id == vt->model_id) {
            return -2;
        }
    }
    if (g_trans_model_count >= DTRANS_MAX_MODELS) {
        return -3;
    }
    g_trans_models[g_trans_model_count] = *vt;

    desc.family_id = D_MODEL_FAMILY_TRANS;
    desc.model_id = vt->model_id;
    desc.name = "trans_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_trans_models[g_trans_model_count];
    if (d_model_register(&desc) != 0) {
        return -4;
    }

    g_trans_model_count += 1u;
    return 0;
}

static const dtrans_model_vtable *d_trans_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_trans_model_count; ++i) {
        if (g_trans_models[i].model_id == model_id) {
            return &g_trans_models[i];
        }
    }
    return (const dtrans_model_vtable *)0;
}

static d_trans_entry *d_trans_find_entry(d_world *w, d_spline_instance_id id) {
    u32 i;
    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (g_trans_entries[i].in_use &&
            g_trans_entries[i].world == w &&
            g_trans_entries[i].inst.id == id) {
            return &g_trans_entries[i];
        }
    }
    return (d_trans_entry *)0;
}

d_spline_instance_id d_trans_create_spline(
    d_world              *w,
    d_spline_profile_id   profile_id,
    const d_spline_knot  *knots,
    u16                   knot_count
) {
    u32 i;
    d_trans_entry *slot = (d_trans_entry *)0;
    d_chunk *chunk;

    if (!w || knot_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (!g_trans_entries[i].in_use) {
            slot = &g_trans_entries[i];
            break;
        }
    }
    if (!slot) {
        return 0u;
    }

    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->inst.id = g_trans_next_id++;
    slot->inst.profile_id = profile_id;
    slot->inst.knot_count = knot_count;
    slot->inst.knots = (d_spline_knot *)malloc(sizeof(d_spline_knot) * knot_count);
    if (!slot->inst.knots) {
        memset(slot, 0, sizeof(*slot));
        return 0u;
    }
    memcpy(slot->inst.knots, knots, sizeof(d_spline_knot) * knot_count);
    slot->inst.state.ptr = (unsigned char *)0;
    slot->inst.state.len = 0u;
    slot->model_id = 1u;
    chunk = d_world_get_or_create_chunk(w, 0, 0);
    slot->inst.chunk_id_start = chunk ? chunk->chunk_id : 0u;
    slot->inst.chunk_id_end = chunk ? chunk->chunk_id : 0u;
    slot->in_use = 1;
    return slot->inst.id;
}

int d_trans_destroy_spline(
    d_world               *w,
    d_spline_instance_id   id
) {
    d_trans_entry *entry = d_trans_find_entry(w, id);
    if (!entry) {
        return -1;
    }
    if (entry->inst.knots) {
        free(entry->inst.knots);
    }
    if (entry->inst.state.ptr) {
        free(entry->inst.state.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

static int d_trans_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    u32 count = 0u;
    u32 total = 0u;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!w || !chunk || !out) {
        return -1;
    }

    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (g_trans_entries[i].in_use &&
            g_trans_entries[i].world == w &&
            (g_trans_entries[i].inst.chunk_id_start == chunk->chunk_id ||
             g_trans_entries[i].inst.chunk_id_end == chunk->chunk_id)) {
            count += 1u;
            total += sizeof(d_spline_instance_id) + sizeof(d_spline_profile_id);
            total += sizeof(u32) * 2u; /* chunk ids */
            total += sizeof(u16);      /* knot count */
            total += sizeof(d_spline_knot) * g_trans_entries[i].inst.knot_count;
            total += sizeof(u32);      /* state len */
            total += g_trans_entries[i].inst.state.len;
        }
    }

    if (count == 0u) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total += 4u; /* count */
    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &count, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (g_trans_entries[i].in_use &&
            g_trans_entries[i].world == w &&
            (g_trans_entries[i].inst.chunk_id_start == chunk->chunk_id ||
             g_trans_entries[i].inst.chunk_id_end == chunk->chunk_id)) {
            u32 state_len = g_trans_entries[i].inst.state.len;
            memcpy(dst, &g_trans_entries[i].inst.id, sizeof(d_spline_instance_id));
            dst += sizeof(d_spline_instance_id);
            memcpy(dst, &g_trans_entries[i].inst.profile_id, sizeof(d_spline_profile_id));
            dst += sizeof(d_spline_profile_id);
            memcpy(dst, &g_trans_entries[i].inst.chunk_id_start, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_trans_entries[i].inst.chunk_id_end, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_trans_entries[i].inst.knot_count, sizeof(u16));
            dst += sizeof(u16);
            if (g_trans_entries[i].inst.knot_count > 0u) {
                memcpy(dst, g_trans_entries[i].inst.knots,
                       sizeof(d_spline_knot) * g_trans_entries[i].inst.knot_count);
                dst += sizeof(d_spline_knot) * g_trans_entries[i].inst.knot_count;
            }
            memcpy(dst, &state_len, sizeof(u32));
            dst += sizeof(u32);
            if (state_len > 0u && g_trans_entries[i].inst.state.ptr) {
                memcpy(dst, g_trans_entries[i].inst.state.ptr, state_len);
                dst += state_len;
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_trans_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    const unsigned char *ptr;
    u32 remaining;
    u32 count;
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
    memcpy(&count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;

    for (i = 0u; i < count; ++i) {
        d_trans_entry *entry = (d_trans_entry *)0;
        d_spline_instance inst;
        u32 state_len;
        u16 knot_count;
        u32 slot;

        if (remaining < sizeof(d_spline_instance_id) + sizeof(d_spline_profile_id) + sizeof(u32) * 2u + sizeof(u16) + sizeof(u32)) {
            return -1;
        }
        memset(&inst, 0, sizeof(inst));

        memcpy(&inst.id, ptr, sizeof(d_spline_instance_id));
        ptr += sizeof(d_spline_instance_id);
        memcpy(&inst.profile_id, ptr, sizeof(d_spline_profile_id));
        ptr += sizeof(d_spline_profile_id);
        memcpy(&inst.chunk_id_start, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&inst.chunk_id_end, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&knot_count, ptr, sizeof(u16));
        ptr += sizeof(u16);
        remaining -= sizeof(d_spline_instance_id) + sizeof(d_spline_profile_id) + sizeof(u32) * 2u + sizeof(u16);

        inst.knot_count = knot_count;
        inst.knots = (d_spline_knot *)0;
        if (knot_count > 0u) {
            if (remaining < sizeof(d_spline_knot) * knot_count) {
                return -1;
            }
            inst.knots = (d_spline_knot *)malloc(sizeof(d_spline_knot) * knot_count);
            if (!inst.knots) {
                return -1;
            }
            memcpy(inst.knots, ptr, sizeof(d_spline_knot) * knot_count);
            ptr += sizeof(d_spline_knot) * knot_count;
            remaining -= sizeof(d_spline_knot) * knot_count;
        }

        memcpy(&state_len, ptr, sizeof(u32));
        ptr += sizeof(u32);
        remaining -= sizeof(u32);
        inst.state.len = state_len;
        inst.state.ptr = (unsigned char *)0;
        if (state_len > 0u) {
            if (remaining < state_len) {
                if (inst.knots) free(inst.knots);
                return -1;
            }
            inst.state.ptr = (unsigned char *)malloc(state_len);
            if (!inst.state.ptr) {
                if (inst.knots) free(inst.knots);
                return -1;
            }
            memcpy(inst.state.ptr, ptr, state_len);
            ptr += state_len;
            remaining -= state_len;
        }

        for (slot = 0u; slot < DTRANS_MAX_INSTANCES; ++slot) {
            if (!g_trans_entries[slot].in_use) {
                entry = &g_trans_entries[slot];
                break;
            }
        }
        if (!entry) {
            if (inst.knots) free(inst.knots);
            if (inst.state.ptr) free(inst.state.ptr);
            return -1;
        }
        memset(entry, 0, sizeof(*entry));
        entry->world = w;
        entry->inst = inst;
        entry->model_id = 1u;
        entry->in_use = 1;
        if (inst.id >= g_trans_next_id) {
            g_trans_next_id = inst.id + 1u;
        }
    }
    return 0;
}

static int d_trans_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_trans_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_trans_init_instance_subsys(d_world *w) {
    u32 i;
    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (g_trans_entries[i].in_use && g_trans_entries[i].world == w) {
            if (g_trans_entries[i].inst.knots) {
                free(g_trans_entries[i].inst.knots);
            }
            if (g_trans_entries[i].inst.state.ptr) {
                free(g_trans_entries[i].inst.state.ptr);
            }
            memset(&g_trans_entries[i], 0, sizeof(g_trans_entries[i]));
        }
    }
}

static void d_trans_tick(d_world *w, u32 ticks) {
    u32 i;
    (void)ticks;
    for (i = 0u; i < DTRANS_MAX_INSTANCES; ++i) {
        if (g_trans_entries[i].in_use && g_trans_entries[i].world == w) {
            const dtrans_model_vtable *vt = d_trans_model_lookup(g_trans_entries[i].model_id);
            if (vt && vt->tick_spline) {
                vt->tick_spline(w, &g_trans_entries[i].inst, ticks);
            }
        }
    }
}

static void d_trans_register_dummy_model(void) {
    dtrans_model_vtable vt;
    memset(&vt, 0, sizeof(vt));
    vt.model_id = 1u;
    vt.tick_spline = (void (*)(d_world *, d_spline_instance *, u32))0;
    dtrans_register_model(&vt);
}

static void d_trans_register_models(void) {
    d_trans_register_dummy_model();
}

static void d_trans_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_trans_subsystem = {
    D_SUBSYS_TRANS,
    "trans",
    1u,
    d_trans_register_models,
    d_trans_load_protos,
    d_trans_init_instance_subsys,
    d_trans_tick,
    d_trans_save_chunk,
    d_trans_load_chunk,
    d_trans_save_instance,
    d_trans_load_instance
};

void d_trans_init(void) {
    if (g_trans_registered) {
        return;
    }
    if (d_subsystem_register(&g_trans_subsystem) == 0) {
        g_trans_registered = 1;
    }
}
