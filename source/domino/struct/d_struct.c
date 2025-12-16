/*
FILE: source/domino/struct/d_struct.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/d_struct
RESPONSIBILITY: Implements `d_struct`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "core/d_tlv_kv.h"
#include "core/d_subsystem.h"
#include "core/d_container_state.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "world/d_world.h"
#include "struct/d_struct.h"
#include "sim/d_sim_process.h"

#define DSTRUCT_MAX_INSTANCES 256u
#define DSTRUCT_MAX_ENV_VOLUMES 32u
#define DSTRUCT_MAX_ENV_EDGES   64u
#define DSTRUCT_ENV_DEFAULT_CONDUCTANCE ((q16_16)(1 << 12)) /* 1/16 in Q16.16 */

typedef struct dstruct_env_vol_def_s {
    q16_16 min_x, min_y, min_z;
    q16_16 max_x, max_y, max_z;
} dstruct_env_vol_def;

typedef struct dstruct_env_edge_def_s {
    u16   a;
    u16   b; /* 0 = exterior */
    q16_16 gas_k;
    q16_16 heat_k;
} dstruct_env_edge_def;

typedef struct d_struct_entry {
    d_world           *world;
    d_struct_instance  inst;
    int                in_use;
} d_struct_entry;

static d_struct_entry g_struct_entries[DSTRUCT_MAX_INSTANCES];
static d_struct_instance_id g_struct_next_id = 1u;
static int g_struct_registered = 0;

static q32_32 dstruct_q32_from_q16(q16_16 v) {
    return ((q32_32)v) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
}

static q16_16 dstruct_sample_field0(const d_env_sample *samples, u16 count, d_env_field_id field_id) {
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

static void dstruct_layout_container_ids(const d_proto_structure *proto,
                                        d_container_proto_id *out_in,
                                        d_container_proto_id *out_out) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 tmp;

    if (out_in) *out_in = 0u;
    if (out_out) *out_out = 0u;
    if (!proto || !out_in || !out_out) {
        return;
    }
    if (!proto->layout.ptr || proto->layout.len == 0u) {
        return;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(&proto->layout, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_STRUCT_LAYOUT_INV_IN_CONTAINER:
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                *out_in = (d_container_proto_id)tmp;
            }
            break;
        case D_TLV_STRUCT_LAYOUT_INV_OUT_CONTAINER:
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                *out_out = (d_container_proto_id)tmp;
            }
            break;
        default:
            break;
        }
    }
}

static int dstruct_parse_env_volume_def(const d_tlv_blob *in, dstruct_env_vol_def *out) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));
    if (!in || !in->ptr || in->len == 0u) {
        return 0;
    }
    offset = 0u;
    while ((rc = d_tlv_kv_next(in, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_ENV_VOLUME_MIN_X:
            (void)d_tlv_kv_read_q16_16(&payload, &out->min_x);
            break;
        case D_TLV_ENV_VOLUME_MIN_Y:
            (void)d_tlv_kv_read_q16_16(&payload, &out->min_y);
            break;
        case D_TLV_ENV_VOLUME_MIN_Z:
            (void)d_tlv_kv_read_q16_16(&payload, &out->min_z);
            break;
        case D_TLV_ENV_VOLUME_MAX_X:
            (void)d_tlv_kv_read_q16_16(&payload, &out->max_x);
            break;
        case D_TLV_ENV_VOLUME_MAX_Y:
            (void)d_tlv_kv_read_q16_16(&payload, &out->max_y);
            break;
        case D_TLV_ENV_VOLUME_MAX_Z:
            (void)d_tlv_kv_read_q16_16(&payload, &out->max_z);
            break;
        default:
            break;
        }
    }
    if (out->max_x < out->min_x) {
        q16_16 tmp = out->min_x; out->min_x = out->max_x; out->max_x = tmp;
    }
    if (out->max_y < out->min_y) {
        q16_16 tmp = out->min_y; out->min_y = out->max_y; out->max_y = tmp;
    }
    if (out->max_z < out->min_z) {
        q16_16 tmp = out->min_z; out->min_z = out->max_z; out->max_z = tmp;
    }
    return 0;
}

static int dstruct_parse_env_edge_def(const d_tlv_blob *in, dstruct_env_edge_def *out) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));
    out->gas_k = DSTRUCT_ENV_DEFAULT_CONDUCTANCE;
    out->heat_k = DSTRUCT_ENV_DEFAULT_CONDUCTANCE;
    if (!in || !in->ptr || in->len == 0u) {
        return 0;
    }
    offset = 0u;
    while ((rc = d_tlv_kv_next(in, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_ENV_EDGE_A:
            (void)d_tlv_kv_read_u16(&payload, &out->a);
            break;
        case D_TLV_ENV_EDGE_B:
            (void)d_tlv_kv_read_u16(&payload, &out->b);
            break;
        case D_TLV_ENV_EDGE_GAS_K:
            (void)d_tlv_kv_read_q16_16(&payload, &out->gas_k);
            break;
        case D_TLV_ENV_EDGE_HEAT_K:
            (void)d_tlv_kv_read_q16_16(&payload, &out->heat_k);
            break;
        default:
            break;
        }
    }
    return 0;
}

static void dstruct_collect_env_defs(
    const d_tlv_blob      *layout,
    dstruct_env_vol_def   *vols,
    u32                   *in_out_vol_count,
    dstruct_env_edge_def  *edges,
    u32                   *in_out_edge_count
) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 vol_count;
    u32 edge_count;

    if (in_out_vol_count) *in_out_vol_count = 0u;
    if (in_out_edge_count) *in_out_edge_count = 0u;
    if (!layout || !layout->ptr || layout->len == 0u) {
        return;
    }
    if (!vols || !edges || !in_out_vol_count || !in_out_edge_count) {
        return;
    }

    offset = 0u;
    vol_count = 0u;
    edge_count = 0u;
    while ((rc = d_tlv_kv_next(layout, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_VOLUME) {
            if (vol_count < DSTRUCT_MAX_ENV_VOLUMES) {
                (void)dstruct_parse_env_volume_def(&payload, &vols[vol_count]);
                vol_count += 1u;
            }
        } else if (tag == D_TLV_ENV_EDGE) {
            if (edge_count < DSTRUCT_MAX_ENV_EDGES) {
                (void)dstruct_parse_env_edge_def(&payload, &edges[edge_count]);
                edge_count += 1u;
            }
        }
    }

    *in_out_vol_count = vol_count;
    *in_out_edge_count = edge_count;
}

static void dstruct_build_env_for_instance(d_world *w, const d_struct_instance *inst) {
    const d_proto_structure *proto;
    dstruct_env_vol_def vols[DSTRUCT_MAX_ENV_VOLUMES];
    dstruct_env_edge_def edges[DSTRUCT_MAX_ENV_EDGES];
    u32 vol_count;
    u32 edge_count;
    d_env_volume_id vol_ids[DSTRUCT_MAX_ENV_VOLUMES + 1u];
    q32_32 base_x;
    q32_32 base_y;
    q32_32 base_z;
    u32 i;

    if (!w || !inst || inst->proto_id == 0u) {
        return;
    }
    proto = d_content_get_structure(inst->proto_id);
    if (!proto) {
        return;
    }

    vol_count = 0u;
    edge_count = 0u;
    dstruct_collect_env_defs(&proto->layout, vols, &vol_count, edges, &edge_count);
    if (vol_count == 0u) {
        return;
    }

    (void)d_env_volume_remove_owned_by(w, (u32)inst->id, 0u);
    memset(vol_ids, 0, sizeof(vol_ids));

    base_x = dstruct_q32_from_q16(inst->pos_x);
    base_y = dstruct_q32_from_q16(inst->pos_y);
    base_z = dstruct_q32_from_q16(inst->pos_z);

    for (i = 0u; i < vol_count; ++i) {
        d_env_volume v;
        d_env_sample samples[16];
        u16 sample_count;
        q32_32 cx;
        q32_32 cy;
        q32_32 cz;

        memset(&v, 0, sizeof(v));
        v.min_x = base_x + dstruct_q32_from_q16(vols[i].min_x);
        v.min_y = base_y + dstruct_q32_from_q16(vols[i].min_y);
        v.min_z = base_z + dstruct_q32_from_q16(vols[i].min_z);
        v.max_x = base_x + dstruct_q32_from_q16(vols[i].max_x);
        v.max_y = base_y + dstruct_q32_from_q16(vols[i].max_y);
        v.max_z = base_z + dstruct_q32_from_q16(vols[i].max_z);
        v.owner_struct_eid = (u32)inst->id;
        v.owner_vehicle_eid = 0u;

        cx = (q32_32)((v.min_x + v.max_x) >> 1);
        cy = (q32_32)((v.min_y + v.max_y) >> 1);
        cz = (q32_32)((v.min_z + v.max_z) >> 1);

        sample_count = d_env_sample_exterior_at(w, cx, cy, cz, samples, 16u);
        v.pressure = dstruct_sample_field0(samples, sample_count, D_ENV_FIELD_PRESSURE);
        v.temperature = dstruct_sample_field0(samples, sample_count, D_ENV_FIELD_TEMPERATURE);
        v.gas0_fraction = dstruct_sample_field0(samples, sample_count, D_ENV_FIELD_GAS0_FRACTION);
        v.gas1_fraction = dstruct_sample_field0(samples, sample_count, D_ENV_FIELD_GAS1_FRACTION);
        v.humidity = dstruct_sample_field0(samples, sample_count, D_ENV_FIELD_HUMIDITY);
        v.pollutant = 0;

        vol_ids[i + 1u] = d_env_volume_create(w, &v);
    }

    for (i = 0u; i < edge_count; ++i) {
        d_env_volume_edge e;
        u16 a = edges[i].a;
        u16 b = edges[i].b;
        if (a == 0u || a > vol_count) {
            continue;
        }
        if (b > vol_count) {
            continue;
        }
        if (vol_ids[a] == 0u) {
            continue;
        }
        if (b != 0u && vol_ids[b] == 0u) {
            continue;
        }
        e.a = vol_ids[a];
        e.b = (b == 0u) ? 0u : vol_ids[b];
        e.gas_conductance = edges[i].gas_k;
        e.heat_conductance = edges[i].heat_k;
        (void)d_env_volume_add_edge(w, &e);
    }
}

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

static d_chunk *d_struct_chunk_for_position(d_world *w, q16_16 x, q16_16 y) {
    i32 cx = d_q16_16_to_int(x);
    i32 cy = d_q16_16_to_int(y);
    return d_world_get_or_create_chunk(w, cx, cy);
}

static d_struct_entry *d_struct_alloc_entry(void) {
    u32 i;
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (!g_struct_entries[i].in_use) {
            return &g_struct_entries[i];
        }
    }
    return (d_struct_entry *)0;
}

static void d_struct_copy_state_blob(d_tlv_blob *dst, const d_tlv_blob *src) {
    if (!dst) {
        return;
    }
    dst->ptr = (unsigned char *)0;
    dst->len = 0u;
    if (!src || !src->ptr || src->len == 0u) {
        return;
    }
    dst->ptr = (unsigned char *)malloc(src->len);
    if (!dst->ptr) {
        dst->len = 0u;
        return;
    }
    memcpy(dst->ptr, src->ptr, src->len);
    dst->len = src->len;
}

d_struct_instance_id d_struct_create(
    d_world       *w,
    d_structure_proto_id proto_id,
    q16_16        x, q16_16 y, q16_16 z,
    q16_16        yaw
) {
    d_struct_instance inst;
    memset(&inst, 0, sizeof(inst));
    inst.proto_id = proto_id;
    inst.pos_x = x;
    inst.pos_y = y;
    inst.pos_z = z;
    inst.rot_yaw = yaw;
    inst.rot_pitch = 0;
    inst.rot_roll = 0;
    return d_struct_spawn(w, &inst);
}

d_struct_instance_id d_struct_spawn(
    d_world                 *w,
    const d_struct_instance *inst_template
) {
    d_struct_entry *slot;
    d_chunk *chunk;
    d_struct_instance copy;
    const d_proto_structure *proto;
    d_container_proto_id inv_in_id;
    d_container_proto_id inv_out_id;

    if (!w || !inst_template || inst_template->proto_id == 0u) {
        return 0u;
    }
    slot = d_struct_alloc_entry();
    if (!slot) {
        return 0u;
    }

    chunk = d_struct_chunk_for_position(w, inst_template->pos_x, inst_template->pos_y);

    memset(slot, 0, sizeof(*slot));
    memset(&copy, 0, sizeof(copy));
    copy.proto_id = inst_template->proto_id;
    copy.owner_org = inst_template->owner_org;
    copy.pos_x = inst_template->pos_x;
    copy.pos_y = inst_template->pos_y;
    copy.pos_z = inst_template->pos_z;
    copy.rot_yaw = inst_template->rot_yaw;
    copy.rot_pitch = inst_template->rot_pitch;
    copy.rot_roll = inst_template->rot_roll;
    copy.flags = inst_template->flags;
    copy.entity_id = inst_template->entity_id;
    copy.machine = inst_template->machine;
    copy.id = g_struct_next_id++;
    copy.chunk_id = chunk ? chunk->chunk_id : 0u;
    if (copy.entity_id == 0u) {
        copy.entity_id = (u32)copy.id;
    }

    proto = d_content_get_structure(copy.proto_id);
    inv_in_id = 0u;
    inv_out_id = 0u;
    dstruct_layout_container_ids(proto, &inv_in_id, &inv_out_id);
    if (inv_in_id != 0u) {
        if (d_container_state_init(&copy.inv_in, inv_in_id) != 0) {
            memset(&copy.inv_in, 0, sizeof(copy.inv_in));
        }
    }
    if (inv_out_id != 0u) {
        if (d_container_state_init(&copy.inv_out, inv_out_id) != 0) {
            memset(&copy.inv_out, 0, sizeof(copy.inv_out));
        }
    }
    d_struct_copy_state_blob(&copy.state, &inst_template->state);

    slot->world = w;
    slot->inst = copy;
    slot->in_use = 1;

    dstruct_build_env_for_instance(w, &slot->inst);
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
    (void)d_env_volume_remove_owned_by(w, (u32)id, 0u);
    d_container_state_free(&entry->inst.inv_in);
    d_container_state_free(&entry->inst.inv_out);
    if (entry->inst.state.ptr) {
        free(entry->inst.state.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

const d_struct_instance *d_struct_get(d_world *w, d_struct_instance_id id) {
    d_struct_entry *entry = d_struct_find_entry(w, id);
    if (!entry) {
        return (const d_struct_instance *)0;
    }
    return &entry->inst;
}

d_struct_instance *d_struct_get_mutable(d_world *w, d_struct_instance_id id) {
    return (d_struct_instance *)d_struct_get(w, id);
}

const d_struct_instance *d_struct_get_by_index(d_world *w, u32 index) {
    u32 count = 0u;
    u32 i;
    if (!w) {
        return (const d_struct_instance *)0;
    }
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use && g_struct_entries[i].world == w) {
            if (count == index) {
                return &g_struct_entries[i].inst;
            }
            count += 1u;
        }
    }
    return (const d_struct_instance *)0;
}

u32 d_struct_count(d_world *w) {
    u32 count = 0u;
    u32 i;
    if (!w) {
        return 0u;
    }
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use && g_struct_entries[i].world == w) {
            count += 1u;
        }
    }
    return count;
}

int d_struct_get_inventory_summary(
    d_world     *w,
    d_entity_id  struct_eid,
    d_item_id   *out_item_id,
    u32         *out_count
) {
    const d_struct_instance *inst;
    u32 i;
    if (!w || struct_eid == 0u) {
        return -1;
    }
    inst = d_struct_get(w, (d_struct_instance_id)struct_eid);
    if (!inst) {
        return -1;
    }

    if (out_item_id) *out_item_id = 0u;
    if (out_count) *out_count = 0u;

    /* Prefer outbound inventory (storage for bins, outputs for machines). */
    if (inst->inv_out.proto_id != 0u && inst->inv_out.slots) {
        u32 slots = (inst->inv_out.slot_count > 0u) ? (u32)inst->inv_out.slot_count : 1u;
        for (i = 0u; i < slots; ++i) {
            if (inst->inv_out.slots[i].item_id != 0u && inst->inv_out.slots[i].count > 0u) {
                if (out_item_id) *out_item_id = inst->inv_out.slots[i].item_id;
                if (out_count) *out_count = inst->inv_out.slots[i].count;
                return 0;
            }
        }
    }
    if (inst->inv_in.proto_id != 0u && inst->inv_in.slots) {
        u32 slots = (inst->inv_in.slot_count > 0u) ? (u32)inst->inv_in.slot_count : 1u;
        for (i = 0u; i < slots; ++i) {
            if (inst->inv_in.slots[i].item_id != 0u && inst->inv_in.slots[i].count > 0u) {
                if (out_item_id) *out_item_id = inst->inv_in.slots[i].item_id;
                if (out_count) *out_count = inst->inv_in.slots[i].count;
                return 0;
            }
        }
    }
    return 0;
}

static int d_struct_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    u32 version = 3u;
    u32 count = 0u;
    u32 total = 0u;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!w || !chunk || !out) {
        return -1;
    }

    total = 8u; /* version + count */
    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use &&
            g_struct_entries[i].world == w &&
            g_struct_entries[i].inst.chunk_id == chunk->chunk_id) {
            const d_struct_instance *inst = &g_struct_entries[i].inst;
            u32 in_slots = 0u;
            u32 out_slots = 0u;
            if (inst->inv_in.proto_id != 0u && inst->inv_in.slots) {
                in_slots = (inst->inv_in.slot_count > 0u) ? (u32)inst->inv_in.slot_count : 1u;
            }
            if (inst->inv_out.proto_id != 0u && inst->inv_out.slots) {
                out_slots = (inst->inv_out.slot_count > 0u) ? (u32)inst->inv_out.slot_count : 1u;
            }

            count += 1u;
            total += sizeof(d_struct_instance_id) + sizeof(d_structure_proto_id) + sizeof(d_org_id);
            total += sizeof(q16_16) * 6u; /* pos + rot */
            total += sizeof(u32) * 2u;    /* flags + entity_id */
            total += sizeof(u32) + sizeof(q16_16) + sizeof(u16) + sizeof(u16); /* machine runtime */
            total += 16u + in_slots * (sizeof(u32) * 2u);  /* inv_in */
            total += 16u + out_slots * (sizeof(u32) * 2u); /* inv_out */
            total += sizeof(u32);         /* state len */
            total += inst->state.len;
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

    memcpy(dst, &version, sizeof(u32)); dst += 4u;
    memcpy(dst, &count, sizeof(u32)); dst += 4u;

    for (i = 0u; i < DSTRUCT_MAX_INSTANCES; ++i) {
        if (g_struct_entries[i].in_use &&
            g_struct_entries[i].world == w &&
            g_struct_entries[i].inst.chunk_id == chunk->chunk_id) {
            const d_struct_instance *inst = &g_struct_entries[i].inst;
            u32 state_len = inst->state.len;
            u32 in_slots = 0u;
            u32 out_slots = 0u;
            u16 pad16 = 0u;
            u32 si;

            memcpy(dst, &inst->id, sizeof(d_struct_instance_id)); dst += sizeof(d_struct_instance_id);
            memcpy(dst, &inst->proto_id, sizeof(d_structure_proto_id)); dst += sizeof(d_structure_proto_id);
            memcpy(dst, &inst->owner_org, sizeof(d_org_id)); dst += sizeof(d_org_id);

            memcpy(dst, &inst->pos_x, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->pos_y, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->pos_z, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->rot_yaw, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->rot_pitch, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->rot_roll, sizeof(q16_16)); dst += sizeof(q16_16);

            memcpy(dst, &inst->flags, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &inst->entity_id, sizeof(u32)); dst += sizeof(u32);

            /* Machine runtime */
            memcpy(dst, &inst->machine.active_process_id, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &inst->machine.progress, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->machine.state_flags, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &pad16, sizeof(u16)); dst += sizeof(u16);

            /* inv_in */
            if (inst->inv_in.proto_id != 0u && inst->inv_in.slots) {
                in_slots = (inst->inv_in.slot_count > 0u) ? (u32)inst->inv_in.slot_count : 1u;
            }
            memcpy(dst, &inst->inv_in.proto_id, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &inst->inv_in.used_volume, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->inv_in.used_mass, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->inv_in.slot_count, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &pad16, sizeof(u16)); dst += sizeof(u16);
            for (si = 0u; si < in_slots; ++si) {
                memcpy(dst, &inst->inv_in.slots[si].item_id, sizeof(u32)); dst += sizeof(u32);
                memcpy(dst, &inst->inv_in.slots[si].count, sizeof(u32)); dst += sizeof(u32);
            }

            /* inv_out */
            if (inst->inv_out.proto_id != 0u && inst->inv_out.slots) {
                out_slots = (inst->inv_out.slot_count > 0u) ? (u32)inst->inv_out.slot_count : 1u;
            }
            memcpy(dst, &inst->inv_out.proto_id, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &inst->inv_out.used_volume, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->inv_out.used_mass, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &inst->inv_out.slot_count, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &pad16, sizeof(u16)); dst += sizeof(u16);
            for (si = 0u; si < out_slots; ++si) {
                memcpy(dst, &inst->inv_out.slots[si].item_id, sizeof(u32)); dst += sizeof(u32);
                memcpy(dst, &inst->inv_out.slots[si].count, sizeof(u32)); dst += sizeof(u32);
            }

            memcpy(dst, &state_len, sizeof(u32)); dst += sizeof(u32);
            if (state_len > 0u && inst->state.ptr) {
                memcpy(dst, inst->state.ptr, state_len);
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
    u32 version;
    u32 count;
    u32 i;

    if (!w || !chunk || !in) {
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

#define DSTRUCT_READ(dst_ptr, nbytes)                    \
    do {                                                 \
        if (remaining < (u32)(nbytes)) return -1;        \
        memcpy((dst_ptr), ptr, (u32)(nbytes));           \
        ptr += (u32)(nbytes);                            \
        remaining -= (u32)(nbytes);                      \
    } while (0)

    DSTRUCT_READ(&version, sizeof(u32));
    if (version != 2u && version != 3u) {
        return -1;
    }
    DSTRUCT_READ(&count, sizeof(u32));

    for (i = 0u; i < count; ++i) {
        d_struct_entry *entry = (d_struct_entry *)0;
        d_struct_instance inst;
        u32 state_len;
        u32 slot;
        u16 pad16;
        u32 in_proto;
        q16_16 in_used_vol;
        q16_16 in_used_mass;
        u16 in_slot_count;
        u32 out_proto;
        q16_16 out_used_vol;
        q16_16 out_used_mass;
        u16 out_slot_count;

        memset(&inst, 0, sizeof(inst));

        DSTRUCT_READ(&inst.id, sizeof(d_struct_instance_id));
        DSTRUCT_READ(&inst.proto_id, sizeof(d_structure_proto_id));
        if (version >= 3u) {
            DSTRUCT_READ(&inst.owner_org, sizeof(d_org_id));
        } else {
            inst.owner_org = 0u;
        }

        DSTRUCT_READ(&inst.pos_x, sizeof(q16_16));
        DSTRUCT_READ(&inst.pos_y, sizeof(q16_16));
        DSTRUCT_READ(&inst.pos_z, sizeof(q16_16));
        DSTRUCT_READ(&inst.rot_yaw, sizeof(q16_16));
        DSTRUCT_READ(&inst.rot_pitch, sizeof(q16_16));
        DSTRUCT_READ(&inst.rot_roll, sizeof(q16_16));

        DSTRUCT_READ(&inst.flags, sizeof(u32));
        DSTRUCT_READ(&inst.entity_id, sizeof(u32));

        DSTRUCT_READ(&inst.machine.active_process_id, sizeof(u32));
        DSTRUCT_READ(&inst.machine.progress, sizeof(q16_16));
        DSTRUCT_READ(&inst.machine.state_flags, sizeof(u16));
        DSTRUCT_READ(&pad16, sizeof(u16));
        (void)pad16;

        /* inv_in header + slots */
        DSTRUCT_READ(&in_proto, sizeof(u32));
        DSTRUCT_READ(&in_used_vol, sizeof(q16_16));
        DSTRUCT_READ(&in_used_mass, sizeof(q16_16));
        DSTRUCT_READ(&in_slot_count, sizeof(u16));
        DSTRUCT_READ(&pad16, sizeof(u16));

        if (in_proto != 0u) {
            u32 slots_in = (in_slot_count > 0u) ? (u32)in_slot_count : 1u;
            u32 si;
            if (d_container_state_init(&inst.inv_in, (d_container_proto_id)in_proto) != 0) {
                return -1;
            }
            if (inst.inv_in.slot_count != in_slot_count) {
                d_container_state_free(&inst.inv_in);
                return -1;
            }
            for (si = 0u; si < slots_in; ++si) {
                DSTRUCT_READ(&inst.inv_in.slots[si].item_id, sizeof(u32));
                DSTRUCT_READ(&inst.inv_in.slots[si].count, sizeof(u32));
            }
            inst.inv_in.used_volume = in_used_vol;
            inst.inv_in.used_mass = in_used_mass;
        }

        /* inv_out header + slots */
        DSTRUCT_READ(&out_proto, sizeof(u32));
        DSTRUCT_READ(&out_used_vol, sizeof(q16_16));
        DSTRUCT_READ(&out_used_mass, sizeof(q16_16));
        DSTRUCT_READ(&out_slot_count, sizeof(u16));
        DSTRUCT_READ(&pad16, sizeof(u16));

        if (out_proto != 0u) {
            u32 slots_out = (out_slot_count > 0u) ? (u32)out_slot_count : 1u;
            u32 si;
            if (d_container_state_init(&inst.inv_out, (d_container_proto_id)out_proto) != 0) {
                d_container_state_free(&inst.inv_in);
                return -1;
            }
            if (inst.inv_out.slot_count != out_slot_count) {
                d_container_state_free(&inst.inv_in);
                d_container_state_free(&inst.inv_out);
                return -1;
            }
            for (si = 0u; si < slots_out; ++si) {
                DSTRUCT_READ(&inst.inv_out.slots[si].item_id, sizeof(u32));
                DSTRUCT_READ(&inst.inv_out.slots[si].count, sizeof(u32));
            }
            inst.inv_out.used_volume = out_used_vol;
            inst.inv_out.used_mass = out_used_mass;
        }

        DSTRUCT_READ(&state_len, sizeof(u32));

        inst.chunk_id = chunk->chunk_id;
        if (inst.entity_id == 0u) {
            inst.entity_id = (u32)inst.id;
        }

        inst.state.len = state_len;
        inst.state.ptr = (unsigned char *)0;
        if (state_len > 0u) {
            if (remaining < state_len) {
                d_container_state_free(&inst.inv_in);
                d_container_state_free(&inst.inv_out);
                return -1;
            }
            inst.state.ptr = (unsigned char *)malloc(state_len);
            if (!inst.state.ptr) {
                d_container_state_free(&inst.inv_in);
                d_container_state_free(&inst.inv_out);
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
            d_container_state_free(&inst.inv_in);
            d_container_state_free(&inst.inv_out);
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
            d_container_state_free(&g_struct_entries[i].inst.inv_in);
            d_container_state_free(&g_struct_entries[i].inst.inv_out);
            if (g_struct_entries[i].inst.state.ptr) {
                free(g_struct_entries[i].inst.state.ptr);
            }
            memset(&g_struct_entries[i], 0, sizeof(g_struct_entries[i]));
        }
    }
}

static void d_struct_tick(d_world *w, u32 ticks) {
    d_sim_process_tick(w, ticks);
}

static void d_struct_register_models(void) {
    /* No standalone models yet. */
}

static void d_struct_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_struct_subsystem = {
    D_SUBSYS_STRUCT,
    "struct",
    2u,
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
