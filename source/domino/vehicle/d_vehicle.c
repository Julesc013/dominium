#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "core/d_tlv_kv.h"
#include "core/d_model.h"
#include "core/d_subsystem.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"
#include "world/d_world.h"
#include "vehicle/d_vehicle.h"
#include "vehicle/d_vehicle_model.h"

#define DVEH_MAX_MODELS     8u
#define DVEH_MAX_INSTANCES 128u
#define DVEH_MAX_ENV_VOLUMES 16u
#define DVEH_MAX_ENV_EDGES   32u
#define DVEH_ENV_DEFAULT_CONDUCTANCE ((q16_16)(1 << 12)) /* 1/16 in Q16.16 */

typedef struct dveh_env_vol_def_s {
    q16_16 min_x, min_y, min_z;
    q16_16 max_x, max_y, max_z;
} dveh_env_vol_def;

typedef struct dveh_env_edge_def_s {
    u16   a;
    u16   b; /* 0 = exterior */
    q16_16 gas_k;
    q16_16 heat_k;
} dveh_env_edge_def;

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

static q32_32 dveh_q32_from_q16(q16_16 v) {
    return ((q32_32)v) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
}

static q16_16 dveh_sample_field0(const d_env_sample *samples, u16 count, d_env_field_id field_id) {
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

static int dveh_parse_env_volume_def(const d_tlv_blob *in, dveh_env_vol_def *out) {
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

static int dveh_parse_env_edge_def(const d_tlv_blob *in, dveh_env_edge_def *out) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));
    out->gas_k = DVEH_ENV_DEFAULT_CONDUCTANCE;
    out->heat_k = DVEH_ENV_DEFAULT_CONDUCTANCE;
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

static void dveh_collect_env_defs(
    const d_tlv_blob     *params,
    dveh_env_vol_def     *vols,
    u32                  *in_out_vol_count,
    dveh_env_edge_def    *edges,
    u32                  *in_out_edge_count
) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 vol_count;
    u32 edge_count;

    if (in_out_vol_count) *in_out_vol_count = 0u;
    if (in_out_edge_count) *in_out_edge_count = 0u;
    if (!params || !params->ptr || params->len == 0u) {
        return;
    }
    if (!vols || !edges || !in_out_vol_count || !in_out_edge_count) {
        return;
    }

    offset = 0u;
    vol_count = 0u;
    edge_count = 0u;
    while ((rc = d_tlv_kv_next(params, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_VOLUME) {
            if (vol_count < DVEH_MAX_ENV_VOLUMES) {
                (void)dveh_parse_env_volume_def(&payload, &vols[vol_count]);
                vol_count += 1u;
            }
        } else if (tag == D_TLV_ENV_EDGE) {
            if (edge_count < DVEH_MAX_ENV_EDGES) {
                (void)dveh_parse_env_edge_def(&payload, &edges[edge_count]);
                edge_count += 1u;
            }
        }
    }

    *in_out_vol_count = vol_count;
    *in_out_edge_count = edge_count;
}

static void dveh_build_env_for_instance(d_world *w, const d_vehicle_instance *inst) {
    const d_proto_vehicle *proto;
    dveh_env_vol_def vols[DVEH_MAX_ENV_VOLUMES];
    dveh_env_edge_def edges[DVEH_MAX_ENV_EDGES];
    u32 vol_count;
    u32 edge_count;
    d_env_volume_id vol_ids[DVEH_MAX_ENV_VOLUMES + 1u];
    q32_32 base_x;
    q32_32 base_y;
    q32_32 base_z;
    u32 i;

    if (!w || !inst || inst->proto_id == 0u) {
        return;
    }
    proto = d_content_get_vehicle(inst->proto_id);
    if (!proto) {
        return;
    }

    vol_count = 0u;
    edge_count = 0u;
    dveh_collect_env_defs(&proto->params, vols, &vol_count, edges, &edge_count);
    if (vol_count == 0u) {
        return;
    }

    (void)d_env_volume_remove_owned_by(w, 0u, (u32)inst->id);
    memset(vol_ids, 0, sizeof(vol_ids));

    base_x = dveh_q32_from_q16(inst->pos_x);
    base_y = dveh_q32_from_q16(inst->pos_y);
    base_z = dveh_q32_from_q16(inst->pos_z);

    for (i = 0u; i < vol_count; ++i) {
        d_env_volume v;
        d_env_sample samples[16];
        u16 sample_count;
        q32_32 cx;
        q32_32 cy;
        q32_32 cz;

        memset(&v, 0, sizeof(v));
        v.min_x = base_x + dveh_q32_from_q16(vols[i].min_x);
        v.min_y = base_y + dveh_q32_from_q16(vols[i].min_y);
        v.min_z = base_z + dveh_q32_from_q16(vols[i].min_z);
        v.max_x = base_x + dveh_q32_from_q16(vols[i].max_x);
        v.max_y = base_y + dveh_q32_from_q16(vols[i].max_y);
        v.max_z = base_z + dveh_q32_from_q16(vols[i].max_z);
        v.owner_struct_eid = 0u;
        v.owner_vehicle_eid = (u32)inst->id;

        cx = (q32_32)((v.min_x + v.max_x) >> 1);
        cy = (q32_32)((v.min_y + v.max_y) >> 1);
        cz = (q32_32)((v.min_z + v.max_z) >> 1);

        sample_count = d_env_sample_exterior_at(w, cx, cy, cz, samples, 16u);
        v.pressure = dveh_sample_field0(samples, sample_count, D_ENV_FIELD_PRESSURE);
        v.temperature = dveh_sample_field0(samples, sample_count, D_ENV_FIELD_TEMPERATURE);
        v.gas0_fraction = dveh_sample_field0(samples, sample_count, D_ENV_FIELD_GAS0_FRACTION);
        v.gas1_fraction = dveh_sample_field0(samples, sample_count, D_ENV_FIELD_GAS1_FRACTION);
        v.humidity = dveh_sample_field0(samples, sample_count, D_ENV_FIELD_HUMIDITY);
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

    dveh_build_env_for_instance(w, &slot->inst);
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
    (void)d_env_volume_remove_owned_by(w, 0u, (u32)id);
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
