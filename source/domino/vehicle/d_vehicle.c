#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "vehicle/d_vehicle.h"
#include "vehicle/d_vehicle_model.h"

#define DVEH_MAX_MODELS     8u
#define DVEH_MAX_INSTANCES 128u

typedef struct d_vehicle_entry {
    d_world            *world;
    d_vehicle_instance  inst;
    u16                 model_id;
    int                 in_use;
} d_vehicle_entry;

static dveh_model_vtable g_veh_models[DVEH_MAX_MODELS];
static u32 g_veh_model_count = 0u;

static d_vehicle_entry g_vehicle_entries[DVEH_MAX_INSTANCES];
static d_vehicle_instance_id g_vehicle_next_id = 1u;
static int g_vehicle_registered = 0;

int dveh_register_model(const dveh_model_vtable *vt) {
    d_model_desc desc;
    u32 i;
    if (!vt || vt->model_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_veh_model_count; ++i) {
        if (g_veh_models[i].model_id == vt->model_id) {
            return -2;
        }
    }
    if (g_veh_model_count >= DVEH_MAX_MODELS) {
        return -3;
    }
    g_veh_models[g_veh_model_count] = *vt;
    desc.family_id = D_MODEL_FAMILY_VEH;
    desc.model_id = vt->model_id;
    desc.name = "veh_model";
    desc.version = 1u;
    desc.fn_table = (void *)&g_veh_models[g_veh_model_count];
    if (d_model_register(&desc) != 0) {
        return -4;
    }
    g_veh_model_count += 1u;
    return 0;
}

static const dveh_model_vtable *d_vehicle_model_lookup(u16 model_id) {
    u32 i;
    for (i = 0u; i < g_veh_model_count; ++i) {
        if (g_veh_models[i].model_id == model_id) {
            return &g_veh_models[i];
        }
    }
    return (const dveh_model_vtable *)0;
}

static d_vehicle_entry *d_vehicle_find_entry(d_world *w, d_vehicle_instance_id id) {
    u32 i;
    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (g_vehicle_entries[i].in_use &&
            g_vehicle_entries[i].world == w &&
            g_vehicle_entries[i].inst.id == id) {
            return &g_vehicle_entries[i];
        }
    }
    return (d_vehicle_entry *)0;
}

d_vehicle_instance_id d_vehicle_create(
    d_world             *w,
    d_vehicle_proto_id   proto_id,
    q16_16              x, q16_16 y, q16_16 z
) {
    u32 i;
    d_vehicle_entry *slot = (d_vehicle_entry *)0;
    d_chunk *chunk;

    if (!w || proto_id == 0u) {
        return 0u;
    }
    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (!g_vehicle_entries[i].in_use) {
            slot = &g_vehicle_entries[i];
            break;
        }
    }
    if (!slot) {
        return 0u;
    }

    chunk = d_world_get_or_create_chunk(w, 0, 0);

    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->inst.id = g_vehicle_next_id++;
    slot->inst.proto_id = proto_id;
    slot->inst.pos_x = x;
    slot->inst.pos_y = y;
    slot->inst.pos_z = z;
    slot->inst.vel_x = 0;
    slot->inst.vel_y = 0;
    slot->inst.vel_z = 0;
    slot->inst.rot_yaw = 0;
    slot->inst.rot_pitch = 0;
    slot->inst.rot_roll = 0;
    slot->inst.chunk_id = chunk ? chunk->chunk_id : 0u;
    slot->inst.flags = 0u;
    slot->inst.entity_id = 0u;
    slot->inst.state.ptr = (unsigned char *)0;
    slot->inst.state.len = 0u;
    slot->model_id = 1u;
    slot->in_use = 1;
    return slot->inst.id;
}

int d_vehicle_destroy(
    d_world               *w,
    d_vehicle_instance_id  id
) {
    d_vehicle_entry *entry = d_vehicle_find_entry(w, id);
    if (!entry) {
        return -1;
    }
    if (entry->inst.state.ptr) {
        free(entry->inst.state.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

static int d_vehicle_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    u32 count = 0u;
    u32 total = 4u;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!w || !chunk || !out) {
        return -1;
    }

    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (g_vehicle_entries[i].in_use &&
            g_vehicle_entries[i].world == w &&
            g_vehicle_entries[i].inst.chunk_id == chunk->chunk_id) {
            count += 1u;
            total += sizeof(d_vehicle_instance_id) + sizeof(d_vehicle_proto_id);
            total += sizeof(q16_16) * 9u; /* pos, vel, rot */
            total += sizeof(u32) * 2u;    /* flags, entity_id */
            total += sizeof(u32);         /* state len */
            total += g_vehicle_entries[i].inst.state.len;
        }
    }
    if (count == 0u) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &count, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (g_vehicle_entries[i].in_use &&
            g_vehicle_entries[i].world == w &&
            g_vehicle_entries[i].inst.chunk_id == chunk->chunk_id) {
            u32 state_len = g_vehicle_entries[i].inst.state.len;
            memcpy(dst, &g_vehicle_entries[i].inst.id, sizeof(d_vehicle_instance_id));
            dst += sizeof(d_vehicle_instance_id);
            memcpy(dst, &g_vehicle_entries[i].inst.proto_id, sizeof(d_vehicle_proto_id));
            dst += sizeof(d_vehicle_proto_id);
            memcpy(dst, &g_vehicle_entries[i].inst.pos_x, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.pos_y, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.pos_z, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.vel_x, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.vel_y, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.vel_z, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.rot_yaw, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.rot_pitch, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.rot_roll, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_vehicle_entries[i].inst.flags, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_vehicle_entries[i].inst.entity_id, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &state_len, sizeof(u32));
            dst += sizeof(u32);
            if (state_len > 0u && g_vehicle_entries[i].inst.state.ptr) {
                memcpy(dst, g_vehicle_entries[i].inst.state.ptr, state_len);
                dst += state_len;
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_vehicle_load_chunk(
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
        d_vehicle_instance inst;
        u32 state_len;
        d_vehicle_entry *entry = (d_vehicle_entry *)0;
        u32 slot;

        if (remaining < sizeof(d_vehicle_instance_id) + sizeof(d_vehicle_proto_id) +
                        sizeof(q16_16) * 9u + sizeof(u32) * 3u) {
            return -1;
        }

        memcpy(&inst.id, ptr, sizeof(d_vehicle_instance_id));
        ptr += sizeof(d_vehicle_instance_id);
        memcpy(&inst.proto_id, ptr, sizeof(d_vehicle_proto_id));
        ptr += sizeof(d_vehicle_proto_id);
        memcpy(&inst.pos_x, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.pos_y, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.pos_z, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.vel_x, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.vel_y, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.vel_z, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_yaw, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_pitch, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_roll, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.flags, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&inst.entity_id, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&state_len, ptr, sizeof(u32));
        ptr += sizeof(u32);
        remaining -= sizeof(d_vehicle_instance_id) + sizeof(d_vehicle_proto_id) +
                     sizeof(q16_16) * 9u + sizeof(u32) * 3u;

        inst.chunk_id = chunk->chunk_id;
        inst.state.len = state_len;
        inst.state.ptr = (unsigned char *)0;
        if (state_len > 0u) {
            if (remaining < state_len) {
                return -1;
            }
            inst.state.ptr = (unsigned char *)malloc(state_len);
            if (!inst.state.ptr) {
                return -1;
            }
            memcpy(inst.state.ptr, ptr, state_len);
            ptr += state_len;
            remaining -= state_len;
        }

        for (slot = 0u; slot < DVEH_MAX_INSTANCES; ++slot) {
            if (!g_vehicle_entries[slot].in_use) {
                entry = &g_vehicle_entries[slot];
                break;
            }
        }
        if (!entry) {
            if (inst.state.ptr) {
                free(inst.state.ptr);
            }
            return -1;
        }

        memset(entry, 0, sizeof(*entry));
        entry->world = w;
        entry->inst = inst;
        entry->model_id = 1u;
        entry->in_use = 1;
        if (inst.id >= g_vehicle_next_id) {
            g_vehicle_next_id = inst.id + 1u;
        }
    }
    return 0;
}

static int d_vehicle_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_vehicle_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_vehicle_init_instance_subsys(d_world *w) {
    u32 i;
    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (g_vehicle_entries[i].in_use && g_vehicle_entries[i].world == w) {
            if (g_vehicle_entries[i].inst.state.ptr) {
                free(g_vehicle_entries[i].inst.state.ptr);
            }
            memset(&g_vehicle_entries[i], 0, sizeof(g_vehicle_entries[i]));
        }
    }
}

static void d_vehicle_tick(d_world *w, u32 ticks) {
    u32 i;
    for (i = 0u; i < DVEH_MAX_INSTANCES; ++i) {
        if (g_vehicle_entries[i].in_use && g_vehicle_entries[i].world == w) {
            const dveh_model_vtable *vt = d_vehicle_model_lookup(g_vehicle_entries[i].model_id);
            if (vt && vt->tick_vehicle) {
                vt->tick_vehicle(w, &g_vehicle_entries[i].inst, ticks);
            }
        }
    }
}

static void d_vehicle_register_dummy_model(void) {
    dveh_model_vtable vt;
    memset(&vt, 0, sizeof(vt));
    vt.model_id = 1u;
    vt.tick_vehicle = (void (*)(d_world *, d_vehicle_instance *, u32))0;
    dveh_register_model(&vt);
}

static void d_vehicle_register_models(void) {
    d_vehicle_register_dummy_model();
}

static void d_vehicle_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_veh_subsystem = {
    D_SUBSYS_VEH,
    "veh",
    1u,
    d_vehicle_register_models,
    d_vehicle_load_protos,
    d_vehicle_init_instance_subsys,
    d_vehicle_tick,
    d_vehicle_save_chunk,
    d_vehicle_load_chunk,
    d_vehicle_save_instance,
    d_vehicle_load_instance
};

void d_vehicle_init(void) {
    if (g_vehicle_registered) {
        return;
    }
    if (d_subsystem_register(&g_veh_subsystem) == 0) {
        g_vehicle_registered = 1;
    }
}
