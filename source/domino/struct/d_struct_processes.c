#include <stdlib.h>
#include <string.h>

#include "domino/core/fixed.h"
#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "res/d_res.h"
#include "struct/d_struct.h"
#include "sim/d_sim.h"

#define STRUCT_SAMPLE_MAX 4u

typedef struct process_params_s {
    q16_16 rate_per_tick;
    u32    deposit_slot;
    q16_16 depletion_amount;
    q16_16 output_per_tick;
    u32    output_item_id;
} process_params;

typedef struct struct_ports_s {
    int has_resource_in;
    i32 res_in_x;
    i32 res_in_y;
} struct_ports;

static int next_tlv(const d_tlv_blob *blob, u32 *offset, u32 *tag, d_tlv_blob *payload) {
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1;
    }
    remaining = blob->len - *offset;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

static u32 read_u32(const d_tlv_blob *payload, u32 def) {
    if (!payload || payload->len < sizeof(u32) || !payload->ptr) {
        return def;
    }
    if (payload->len >= sizeof(u32)) {
        u32 out;
        memcpy(&out, payload->ptr, sizeof(u32));
        return out;
    }
    return def;
}

static i32 read_i32(const d_tlv_blob *payload, i32 def) {
    if (!payload || payload->len < sizeof(i32) || !payload->ptr) {
        return def;
    }
    if (payload->len >= sizeof(i32)) {
        i32 out;
        memcpy(&out, payload->ptr, sizeof(i32));
        return out;
    }
    return def;
}

static q16_16 read_q16(const d_tlv_blob *payload, q16_16 def) {
    if (!payload || payload->len != sizeof(q16_16) || !payload->ptr) {
        return def;
    }
    return *((q16_16 *)payload->ptr);
}

static void parse_process_params(const d_proto_process *proc, process_params *out) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    process_params tmp;

    if (!out) {
        return;
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.rate_per_tick = d_q16_16_from_int(0);
    tmp.deposit_slot = 0u;
    tmp.depletion_amount = d_q16_16_from_int(0);
    tmp.output_per_tick = d_q16_16_from_int(0);
    tmp.output_item_id = 0u;

    if (!proc) {
        *out = tmp;
        return;
    }

    while (1) {
        int rc = next_tlv(&proc->params, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            break;
        }
        switch (tag) {
        case D_TLV_PROCESS_RATE_PER_TICK:
            tmp.rate_per_tick = read_q16(&payload, tmp.rate_per_tick);
            break;
        case D_TLV_PROCESS_DEPOSIT_VALUE_SLOT:
            tmp.deposit_slot = read_u32(&payload, tmp.deposit_slot);
            break;
        case D_TLV_PROCESS_DEPLETION_AMOUNT:
            tmp.depletion_amount = read_q16(&payload, tmp.depletion_amount);
            break;
        case D_TLV_PROCESS_OUTPUT_ITEM_ID:
            tmp.output_item_id = read_u32(&payload, tmp.output_item_id);
            break;
        case D_TLV_PROCESS_OUTPUT_PER_TICK:
            tmp.output_per_tick = read_q16(&payload, tmp.output_per_tick);
            break;
        default:
            break;
        }
    }
    *out = tmp;
}

static void parse_ports(const d_proto_structure *proto, struct_ports *ports) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    struct_ports tmp;
    if (!ports) {
        return;
    }
    memset(&tmp, 0, sizeof(tmp));
    if (!proto) {
        *ports = tmp;
        return;
    }

    while (1) {
        int rc = next_tlv(&proto->io, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            break;
        }
        if (tag == D_TLV_STRUCT_IO_PORT) {
            u32 port_off = 0u;
            u32 port_tag;
            d_tlv_blob port_field;
            u32 kind = 0u;
            i32 px = 0;
            i32 py = 0;
            while (1) {
                int prc = next_tlv(&payload, &port_off, &port_tag, &port_field);
                if (prc == 1) {
                    break;
                }
                if (prc != 0) {
                    break;
                }
                switch (port_tag) {
                case D_TLV_STRUCT_PORT_KIND:
                    kind = read_u32(&port_field, kind);
                    break;
                case D_TLV_STRUCT_PORT_POS_X:
                    px = read_i32(&port_field, px);
                    break;
                case D_TLV_STRUCT_PORT_POS_Y:
                    py = read_i32(&port_field, py);
                    break;
                default:
                    break;
                }
            }
            if (kind == D_STRUCT_PORT_RESOURCE_IN) {
                tmp.has_resource_in = 1;
                tmp.res_in_x = px;
                tmp.res_in_y = py;
            }
        }
    }

    *ports = tmp;
}

static q32_32 to_q32_32(q16_16 v) {
    return ((q32_32)v) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
}

static void run_process_for_instance(
    d_world               *w,
    d_struct_instance     *inst,
    const d_proto_structure *proto,
    d_process_id           proc_id,
    u32                    ticks,
    const struct_ports    *ports
) {
    const d_proto_process *proc;
    process_params params;
    dres_sample samples[STRUCT_SAMPLE_MAX];
    u16 sample_count = STRUCT_SAMPLE_MAX;
    u16 sample_index = 0u;
    q16_16 delta[DRES_VALUE_MAX];
    q16_16 depletion_total;
    q16_16 output_total_q = 0;
    u32 output_items = 0u;
    q16_16 rate_scale;
    q16_16 tick_scale;
    q16_16 total_scale;
    q16_16 sample_value;
    q16_16 zero_q = d_q16_16_from_int(0);
    q16_16 out_q_one = d_q16_16_from_int(1);

    if (!w || !inst || !proto) {
        return;
    }
    proc = d_content_get_process(proc_id);
    if (!proc) {
        return;
    }

    parse_process_params(proc, &params);
    if (params.output_item_id == 0u || params.depletion_amount == 0 || params.output_per_tick == 0 || params.rate_per_tick == 0) {
        return;
    }
    if (params.deposit_slot >= DRES_VALUE_MAX) {
        return;
    }

    tick_scale = (ticks > 0u) ? d_q16_16_from_int((i32)ticks) : out_q_one;
    rate_scale = params.rate_per_tick;
    total_scale = d_q16_16_mul(rate_scale, tick_scale);
    if (total_scale == 0) {
        total_scale = tick_scale;
    }

    {
        i64 scaled_dep = ((i64)params.depletion_amount * (i64)total_scale);
        depletion_total = (q16_16)(scaled_dep >> Q16_16_FRAC_BITS);
        if (depletion_total == 0 && params.depletion_amount != 0) {
            depletion_total = params.depletion_amount;
        }
    }

    output_total_q = (q16_16)(((i64)params.output_per_tick * (i64)total_scale) >> Q16_16_FRAC_BITS);
    if (output_total_q == 0 && params.output_per_tick != 0) {
        output_total_q = params.output_per_tick;
    }
    output_items = (u32)d_q16_16_to_int(output_total_q);

    {
        q16_16 pos_x = inst->pos_x;
        q16_16 pos_y = inst->pos_y;
        if (ports && ports->has_resource_in) {
            pos_x = d_q16_16_add(pos_x, d_q16_16_from_int(ports->res_in_x));
            pos_y = d_q16_16_add(pos_y, d_q16_16_from_int(ports->res_in_y));
        }
        if (dres_sample_at(w, to_q32_32(pos_x), to_q32_32(pos_y), to_q32_32(inst->pos_z), 0u, samples, &sample_count) != 0) {
            return;
        }
    }

    if (sample_count == 0u) {
        return;
    }
    {
        u16 chosen = 0u;
        u16 idx;
        sample_value = zero_q;
        for (idx = 0u; idx < sample_count; ++idx) {
            q16_16 v = samples[idx].value[params.deposit_slot];
            if (v > sample_value) {
                sample_value = v;
                chosen = idx;
            }
        }
        sample_index = chosen;
    }
    if (sample_value <= zero_q) {
        return;
    }

    memset(delta, 0, sizeof(delta));
    delta[params.deposit_slot] = (q16_16)(-depletion_total);
    if (dres_apply_delta(w, &samples[sample_index], delta, (u32)proc_id) != 0) {
        return;
    }

    if (output_items > 0u) {
        d_struct_inventory_add(&inst->inventory, params.output_item_id, output_items);
    }
}

static void struct_processes_tick(d_sim_context *ctx, u32 ticks) {
    d_world *w;
    u32 count;
    u32 i;
    d_struct_instance_id *ids = (d_struct_instance_id *)0;
    if (!ctx) {
        return;
    }
    w = ctx->world;
    if (!w) {
        return;
    }

    count = d_struct_count(w);
    if (count == 0u) {
        return;
    }

    ids = (d_struct_instance_id *)malloc(sizeof(d_struct_instance_id) * count);
    if (!ids) {
        return;
    }

    {
        u32 filled = 0u;
        for (i = 0u; i < count; ++i) {
            const d_struct_instance *inst_view = d_struct_get_by_index(w, i);
            if (!inst_view) {
                break;
            }
            ids[filled++] = inst_view->id;
        }
        count = filled;
    }

    if (count == 0u) {
        free(ids);
        return;
    }

    /* Insertion sort to ensure deterministic ID order. */
    for (i = 1u; i < count; ++i) {
        d_struct_instance_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }

    for (i = 0u; i < count; ++i) {
        d_struct_instance *inst;
        const d_proto_structure *proto;
        u32 offset = 0u;
        u32 tag;
        d_tlv_blob payload;
        struct_ports ports;
        d_struct_instance_id id = ids[i];

        if (id == 0u) {
            continue;
        }
        inst = d_struct_get_mutable(w, id);
        if (!inst) {
            continue;
        }
        proto = d_content_get_structure(inst->proto_id);
        if (!proto) {
            continue;
        }

        parse_ports(proto, &ports);
        while (1) {
            int rc = next_tlv(&proto->processes, &offset, &tag, &payload);
            if (rc == 1) {
                break;
            }
            if (rc != 0) {
                break;
            }
            if (tag == D_TLV_STRUCT_PROCESS_ALLOWED) {
                d_process_id pid = (d_process_id)read_u32(&payload, 0u);
                if (pid != 0u) {
                    run_process_for_instance(w, inst, proto, pid, ticks, &ports);
                }
            }
        }
    }

    free(ids);
}

static const dsim_system_vtable g_struct_processes_system = {
    1u,
    "struct_processes",
    (void (*)(d_sim_context *))0,
    struct_processes_tick,
    (void (*)(d_sim_context *))0
};

void d_struct_processes_register_system(void) {
    d_sim_register_system(&g_struct_processes_system);
}
