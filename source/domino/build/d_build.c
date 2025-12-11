#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "build/d_build.h"

#define DBUILD_MAX_INSTANCES 256u

typedef struct d_build_entry {
    d_world             *world;
    d_building_instance  inst;
    int                  in_use;
} d_build_entry;

static d_build_entry g_build_entries[DBUILD_MAX_INSTANCES];
static d_building_instance_id g_build_next_id = 1u;
static int g_build_registered = 0;

static d_build_entry *d_build_find_entry(d_world *w, d_building_instance_id id) {
    u32 i;
    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (g_build_entries[i].in_use &&
            g_build_entries[i].world == w &&
            g_build_entries[i].inst.id == id) {
            return &g_build_entries[i];
        }
    }
    return (d_build_entry *)0;
}

d_building_instance_id d_build_create(
    d_world             *w,
    d_building_proto_id  proto_id,
    q16_16               x, q16_16 y, q16_16 z,
    q16_16               yaw
) {
    u32 i;
    d_build_entry *slot = (d_build_entry *)0;
    d_chunk *chunk;

    if (!w || proto_id == 0u) {
        return 0u;
    }

    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (!g_build_entries[i].in_use) {
            slot = &g_build_entries[i];
            break;
        }
    }
    if (!slot) {
        return 0u;
    }

    chunk = d_world_get_or_create_chunk(w, 0, 0);

    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->inst.id = g_build_next_id++;
    slot->inst.proto_id = proto_id;
    slot->inst.pos_x = x;
    slot->inst.pos_y = y;
    slot->inst.pos_z = z;
    slot->inst.rot_yaw = yaw;
    slot->inst.rot_pitch = 0;
    slot->inst.rot_roll = 0;
    slot->inst.chunk_id = chunk ? chunk->chunk_id : 0u;
    slot->inst.flags = 0u;
    slot->inst.state.ptr = (unsigned char *)0;
    slot->inst.state.len = 0u;
    slot->in_use = 1;
    return slot->inst.id;
}

int d_build_destroy(
    d_world              *w,
    d_building_instance_id id
) {
    d_build_entry *entry = d_build_find_entry(w, id);
    if (!entry) {
        return -1;
    }
    if (entry->inst.state.ptr) {
        free(entry->inst.state.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

static int d_build_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    u32 count = 0u;
    u32 total;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!out) {
        return -1;
    }
    if (!w || !chunk) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return -1;
    }

    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (g_build_entries[i].in_use &&
            g_build_entries[i].world == w &&
            g_build_entries[i].inst.chunk_id == chunk->chunk_id) {
            count += 1u;
        }
    }
    if (count == 0u) {
        out->ptr = (unsigned char *)0;
        out->len = 0u;
        return 0;
    }

    total = 4u;
    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (g_build_entries[i].in_use &&
            g_build_entries[i].world == w &&
            g_build_entries[i].inst.chunk_id == chunk->chunk_id) {
            total += sizeof(d_building_instance_id) + sizeof(d_building_proto_id);
            total += sizeof(q16_16) * 6u; /* position + rotation */
            total += sizeof(u32); /* flags */
            total += sizeof(u32); /* state length */
            total += g_build_entries[i].inst.state.len;
        }
    }

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &count, sizeof(u32));
    dst += 4u;

    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (g_build_entries[i].in_use &&
            g_build_entries[i].world == w &&
            g_build_entries[i].inst.chunk_id == chunk->chunk_id) {
            u32 state_len = g_build_entries[i].inst.state.len;
            memcpy(dst, &g_build_entries[i].inst.id, sizeof(d_building_instance_id));
            dst += sizeof(d_building_instance_id);
            memcpy(dst, &g_build_entries[i].inst.proto_id, sizeof(d_building_proto_id));
            dst += sizeof(d_building_proto_id);
            memcpy(dst, &g_build_entries[i].inst.pos_x, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.pos_y, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.pos_z, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.rot_yaw, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.rot_pitch, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.rot_roll, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_build_entries[i].inst.flags, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &state_len, sizeof(u32));
            dst += sizeof(u32);
            if (state_len > 0u && g_build_entries[i].inst.state.ptr) {
                memcpy(dst, g_build_entries[i].inst.state.ptr, state_len);
                dst += state_len;
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_build_load_chunk(
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
        d_building_instance inst;
        u32 state_len;
        d_building_instance_id new_id;
        d_build_entry *entry = (d_build_entry *)0;
        u32 slot;

        if (remaining < sizeof(d_building_instance_id) + sizeof(d_building_proto_id) +
                        sizeof(q16_16) * 6u + sizeof(u32) + sizeof(u32)) {
            return -1;
        }
        memcpy(&inst.id, ptr, sizeof(d_building_instance_id));
        ptr += sizeof(d_building_instance_id);
        memcpy(&inst.proto_id, ptr, sizeof(d_building_proto_id));
        ptr += sizeof(d_building_proto_id);
        memcpy(&inst.pos_x, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.pos_y, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.pos_z, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_yaw, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_pitch, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.rot_roll, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.flags, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&state_len, ptr, sizeof(u32));
        ptr += sizeof(u32);
        remaining -= sizeof(d_building_instance_id) + sizeof(d_building_proto_id) +
                     sizeof(q16_16) * 6u + sizeof(u32) + sizeof(u32);

        inst.state.ptr = (unsigned char *)0;
        inst.state.len = state_len;
        inst.chunk_id = chunk->chunk_id;
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

        for (slot = 0u; slot < DBUILD_MAX_INSTANCES; ++slot) {
            if (!g_build_entries[slot].in_use) {
                entry = &g_build_entries[slot];
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
        entry->in_use = 1;
        new_id = inst.id;
        if (new_id >= g_build_next_id) {
            g_build_next_id = new_id + 1u;
        }
    }
    return 0;
}

static int d_build_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_build_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_build_init_instance_subsys(d_world *w) {
    u32 i;
    for (i = 0u; i < DBUILD_MAX_INSTANCES; ++i) {
        if (g_build_entries[i].in_use && g_build_entries[i].world == w) {
            if (g_build_entries[i].inst.state.ptr) {
                free(g_build_entries[i].inst.state.ptr);
            }
            memset(&g_build_entries[i], 0, sizeof(g_build_entries[i]));
        }
    }
}

static void d_build_tick(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static void d_build_register_models(void) {
    /* Placeholder: building models can be registered later. */
}

static void d_build_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_build_subsystem = {
    D_SUBSYS_BUILD,
    "build",
    1u,
    d_build_register_models,
    d_build_load_protos,
    d_build_init_instance_subsys,
    d_build_tick,
    d_build_save_chunk,
    d_build_load_chunk,
    d_build_save_instance,
    d_build_load_instance
};

void d_build_init(void) {
    if (g_build_registered) {
        return;
    }
    if (d_subsystem_register(&g_build_subsystem) == 0) {
        g_build_registered = 1;
    }
}
