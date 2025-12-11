#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_subsystem.h"
#include "world/d_world.h"
#include "struct/d_struct.h"

#define DSTRUCT_MAX_INSTANCES 256u

typedef struct d_struct_entry {
    d_world           *world;
    d_struct_instance  inst;
    int                in_use;
} d_struct_entry;

static d_struct_entry g_struct_entries[DSTRUCT_MAX_INSTANCES];
static d_struct_instance_id g_struct_next_id = 1u;
static int g_struct_registered = 0;

static d_struct_entry *d_struct_find_entry(d_world *w, d_struct_instance_id id) {
    u32 i;
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use &&
            g_struct_entries[i].world == w &&
            g_struct_entries[i].inst.id == id) {
            return &g_struct_entries[i];
        }
    }
    return (d_struct_entry *)0;
}

d_struct_instance_id d_struct_create(
    d_world       *w,
    d_structure_id proto_id,
    q16_16        x, q16_16 y, q16_16 z,
    q16_16        yaw
) {
    u32 i;
    d_struct_entry *slot = (d_struct_entry *)0;
    d_chunk *chunk;

    if (!w || proto_id == 0u) {
        return 0u;
    }
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (!g_struct_entries[i].in_use) {
            slot = &g_struct_entries[i];
            break;
        }
    }
    if (!slot) {
        return 0u;
    }

    chunk = d_world_get_or_create_chunk(w, 0, 0);

    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->inst.id = g_struct_next_id++;
    slot->inst.proto_id = proto_id;
    slot->inst.pos_x = x;
    slot->inst.pos_y = y;
    slot->inst.pos_z = z;
    slot->inst.rot_yaw = yaw;
    slot->inst.rot_pitch = 0;
    slot->inst.rot_roll = 0;
    slot->inst.chunk_id = chunk ? chunk->chunk_id : 0u;
    slot->inst.flags = 0u;
    slot->inst.entity_id = 0u;
    slot->inst.state.ptr = (unsigned char *)0;
    slot->inst.state.len = 0u;
    slot->in_use = 1;
    return slot->inst.id;
}

int d_struct_destroy(
    d_world             *w,
    d_struct_instance_id id
) {
    d_struct_entry *entry = d_struct_find_entry(w, id);
    if (!entry) {
        return -1;
    }
    if (entry->inst.state.ptr) {
        free(entry->inst.state.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

static int d_struct_save_chunk(
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

    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use &&
            g_struct_entries[i].world == w &&
            g_struct_entries[i].inst.chunk_id == chunk->chunk_id) {
            count += 1u;
            total += sizeof(d_struct_instance_id) + sizeof(d_structure_id);
            total += sizeof(q16_16) * 6u; /* pos + rot */
            total += sizeof(u32) * 2u;    /* flags + entity_id */
            total += sizeof(u32);         /* state len */
            total += g_struct_entries[i].inst.state.len;
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

    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use &&
            g_struct_entries[i].world == w &&
            g_struct_entries[i].inst.chunk_id == chunk->chunk_id) {
            u32 state_len = g_struct_entries[i].inst.state.len;
            memcpy(dst, &g_struct_entries[i].inst.id, sizeof(d_struct_instance_id));
            dst += sizeof(d_struct_instance_id);
            memcpy(dst, &g_struct_entries[i].inst.proto_id, sizeof(d_structure_id));
            dst += sizeof(d_structure_id);
            memcpy(dst, &g_struct_entries[i].inst.pos_x, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.pos_y, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.pos_z, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.rot_yaw, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.rot_pitch, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.rot_roll, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_struct_entries[i].inst.flags, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_struct_entries[i].inst.entity_id, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &state_len, sizeof(u32));
            dst += sizeof(u32);
            if (state_len > 0u && g_struct_entries[i].inst.state.ptr) {
                memcpy(dst, g_struct_entries[i].inst.state.ptr, state_len);
                dst += state_len;
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_struct_load_chunk(
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
        d_struct_entry *entry = (d_struct_entry *)0;
        d_struct_instance inst;
        u32 state_len;
        u32 slot;

        if (remaining < sizeof(d_struct_instance_id) + sizeof(d_structure_id) +
                        sizeof(q16_16) * 6u + sizeof(u32) * 3u) {
            return -1;
        }

        memcpy(&inst.id, ptr, sizeof(d_struct_instance_id));
        ptr += sizeof(d_struct_instance_id);
        memcpy(&inst.proto_id, ptr, sizeof(d_structure_id));
        ptr += sizeof(d_structure_id);
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
        memcpy(&inst.entity_id, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&state_len, ptr, sizeof(u32));
        ptr += sizeof(u32);
        remaining -= sizeof(d_struct_instance_id) + sizeof(d_structure_id) +
                     sizeof(q16_16) * 6u + sizeof(u32) * 3u;

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

        for (slot = 0u; slot < DSTRUCT_MAX_INSTANCES; ++slot) {
            if (!g_struct_entries[slot].in_use) {
                entry = &g_struct_entries[slot];
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
        if (inst.id >= g_struct_next_id) {
            g_struct_next_id = inst.id + 1u;
        }
    }
    return 0;
}

static int d_struct_save_instance(d_world *w, d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_struct_load_instance(d_world *w, const d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_struct_init_instance_subsys(d_world *w) {
    u32 i;
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use && g_struct_entries[i].world == w) {
            if (g_struct_entries[i].inst.state.ptr) {
                free(g_struct_entries[i].inst.state.ptr);
            }
            memset(&g_struct_entries[i], 0, sizeof(g_struct_entries[i]));
        }
    }
}

static void d_struct_tick(d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static void d_struct_register_models(void) {
    /* placeholder for future model family */
}

static void d_struct_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_struct_subsystem = {
    D_SUBSYS_STRUCT,
    "struct",
    1u,
    d_struct_register_models,
    d_struct_load_protos,
    d_struct_init_instance_subsys,
    d_struct_tick,
    d_struct_save_chunk,
    d_struct_load_chunk,
    d_struct_save_instance,
    d_struct_load_instance
};

void d_struct_init(void) {
    if (g_struct_registered) {
        return;
    }
    if (d_subsystem_register(&g_struct_subsystem) == 0) {
        g_struct_registered = 1;
    }
}
