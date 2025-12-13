#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "content/d_content_extra.h"
#include "core/d_tlv_kv.h"
#include "core/d_subsystem.h"
#include "env/d_env_field.h"
#include "world/d_world.h"
#include "job/d_job.h"

#define DJOB_MAX_INSTANCES 256u

typedef struct d_job_entry {
    d_world        *world;
    d_job_instance  inst;
    int             in_use;
} d_job_entry;

static d_job_entry g_job_entries[DJOB_MAX_INSTANCES];
static d_job_instance_id g_job_next_id = 1u;
static int g_job_registered = 0;

typedef struct djob_env_req_s {
    u16   field_id;
    q16_16 min_v;
    q16_16 max_v;
} djob_env_req;

static q32_32 djob_q32_from_q16(q16_16 v) {
    return ((q32_32)v) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
}

static int djob_parse_env_req(const d_tlv_blob *in, djob_env_req *out) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));
    out->min_v = (q16_16)0x80000000;
    out->max_v = (q16_16)0x7FFFFFFF;
    if (!in || !in->ptr || in->len == 0u) {
        return 0;
    }
    offset = 0u;
    while ((rc = d_tlv_kv_next(in, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_JOB_ENV_FIELD_ID:
            (void)d_tlv_kv_read_u16(&payload, &out->field_id);
            break;
        case D_TLV_JOB_ENV_MIN:
            (void)d_tlv_kv_read_q16_16(&payload, &out->min_v);
            break;
        case D_TLV_JOB_ENV_MAX:
            (void)d_tlv_kv_read_q16_16(&payload, &out->max_v);
            break;
        default:
            break;
        }
    }
    if (out->max_v < out->min_v) {
        q16_16 tmp = out->min_v; out->min_v = out->max_v; out->max_v = tmp;
    }
    return 0;
}

static u32 djob_collect_env_reqs(const d_tlv_blob *params, djob_env_req *out_reqs, u32 max_reqs) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 count;

    if (!out_reqs || max_reqs == 0u) {
        return 0u;
    }
    if (!params || !params->ptr || params->len == 0u) {
        return 0u;
    }

    offset = 0u;
    count = 0u;
    while ((rc = d_tlv_kv_next(params, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_JOB_ENV_RANGE) {
            djob_env_req req;
            (void)djob_parse_env_req(&payload, &req);
            if (req.field_id != 0u && count < max_reqs) {
                out_reqs[count] = req;
                count += 1u;
            }
        }
    }
    return count;
}

static int djob_env_req_pass(const d_env_sample *samples, u16 sample_count, const djob_env_req *req) {
    u16 i;
    if (!samples || !req) {
        return 0;
    }
    for (i = 0u; i < sample_count; ++i) {
        if (samples[i].field_id == req->field_id) {
            q16_16 v = samples[i].values[0];
            if (v < req->min_v || v > req->max_v) {
                return 0;
            }
            return 1;
        }
    }
    return 0;
}

static d_job_entry *d_job_find_entry(d_world *w, d_job_instance_id id) {
    u32 i;
    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (g_job_entries[i].in_use &&
            g_job_entries[i].world == w &&
            g_job_entries[i].inst.id == id) {
            return &g_job_entries[i];
        }
    }
    return (d_job_entry *)0;
}

d_job_instance_id d_job_create(
    d_world           *w,
    d_job_template_id  template_id,
    q16_16            x, q16_16 y, q16_16 z
) {
    u32 i;
    d_job_entry *slot = (d_job_entry *)0;
    if (!w || template_id == 0u) {
        return 0u;
    }
    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (!g_job_entries[i].in_use) {
            slot = &g_job_entries[i];
            break;
        }
    }
    if (!slot) {
        return 0u;
    }
    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->inst.id = g_job_next_id++;
    slot->inst.template_id = template_id;
    slot->inst.flags = 0u;
    slot->inst.subject_entity_id = 0u;
    slot->inst.target_entity_id = 0u;
    slot->inst.target_x = x;
    slot->inst.target_y = y;
    slot->inst.target_z = z;
    slot->inst.params.ptr = (unsigned char *)0;
    slot->inst.params.len = 0u;
    slot->in_use = 1;
    return slot->inst.id;
}

int d_job_destroy(
    d_world          *w,
    d_job_instance_id id
) {
    d_job_entry *entry = d_job_find_entry(w, id);
    if (!entry) {
        return -1;
    }
    if (entry->inst.params.ptr) {
        free(entry->inst.params.ptr);
    }
    memset(entry, 0, sizeof(*entry));
    return 0;
}

static void d_job_tick(d_world *w, u32 ticks) {
    u32 i;
    (void)ticks;
    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (g_job_entries[i].in_use && g_job_entries[i].world == w) {
            const d_proto_job_template *tmpl = d_content_get_job_template(g_job_entries[i].inst.template_id);
            djob_env_req reqs[8];
            u32 req_count;
            d_env_sample samples[16];
            u16 sample_count;
            q32_32 x32;
            q32_32 y32;
            q32_32 z32;
            u32 r;
            int ok;

            g_job_entries[i].inst.flags &= ~D_JOB_FLAG_ENV_UNSUITABLE;
            if (!tmpl) {
                continue;
            }

            req_count = djob_collect_env_reqs(&tmpl->params, reqs, 8u);
            if (req_count == 0u) {
                continue;
            }

            x32 = djob_q32_from_q16(g_job_entries[i].inst.target_x);
            y32 = djob_q32_from_q16(g_job_entries[i].inst.target_y);
            z32 = djob_q32_from_q16(g_job_entries[i].inst.target_z);
            sample_count = d_env_sample_at(w, x32, y32, z32, samples, 16u);

            ok = 1;
            for (r = 0u; r < req_count; ++r) {
                if (!djob_env_req_pass(samples, sample_count, &reqs[r])) {
                    ok = 0;
                    break;
                }
            }
            if (!ok) {
                g_job_entries[i].inst.flags |= D_JOB_FLAG_ENV_UNSUITABLE;
            }
        }
    }
}

static int d_job_save_chunk(
    d_world    *w,
    d_chunk    *chunk,
    d_tlv_blob *out
) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_job_load_chunk(
    d_world          *w,
    d_chunk          *chunk,
    const d_tlv_blob *in
) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static int d_job_save_instance(d_world *w, d_tlv_blob *out) {
    u32 count = 0u;
    u32 total = 4u;
    u32 i;
    unsigned char *buf;
    unsigned char *dst;

    if (!out) {
        return -1;
    }
    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (g_job_entries[i].in_use && g_job_entries[i].world == w) {
            count += 1u;
            total += sizeof(d_job_instance_id) + sizeof(d_job_template_id);
            total += sizeof(u32) * 3u; /* flags + subject + target entity */
            total += sizeof(q16_16) * 3u; /* target coords */
            total += sizeof(u32); /* params len */
            total += g_job_entries[i].inst.params.len;
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

    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (g_job_entries[i].in_use && g_job_entries[i].world == w) {
            u32 params_len = g_job_entries[i].inst.params.len;
            memcpy(dst, &g_job_entries[i].inst.id, sizeof(d_job_instance_id));
            dst += sizeof(d_job_instance_id);
            memcpy(dst, &g_job_entries[i].inst.template_id, sizeof(d_job_template_id));
            dst += sizeof(d_job_template_id);
            memcpy(dst, &g_job_entries[i].inst.flags, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_job_entries[i].inst.subject_entity_id, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_job_entries[i].inst.target_entity_id, sizeof(u32));
            dst += sizeof(u32);
            memcpy(dst, &g_job_entries[i].inst.target_x, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_job_entries[i].inst.target_y, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &g_job_entries[i].inst.target_z, sizeof(q16_16));
            dst += sizeof(q16_16);
            memcpy(dst, &params_len, sizeof(u32));
            dst += sizeof(u32);
            if (params_len > 0u && g_job_entries[i].inst.params.ptr) {
                memcpy(dst, g_job_entries[i].inst.params.ptr, params_len);
                dst += params_len;
            }
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_job_load_instance(d_world *w, const d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 count;
    u32 i;

    if (!w || !in) {
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
        d_job_instance inst;
        d_job_entry *entry = (d_job_entry *)0;
        u32 params_len;
        u32 slot;

        if (remaining < sizeof(d_job_instance_id) + sizeof(d_job_template_id) + sizeof(u32) * 4u + sizeof(q16_16) * 3u) {
            return -1;
        }

        memcpy(&inst.id, ptr, sizeof(d_job_instance_id));
        ptr += sizeof(d_job_instance_id);
        memcpy(&inst.template_id, ptr, sizeof(d_job_template_id));
        ptr += sizeof(d_job_template_id);
        memcpy(&inst.flags, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&inst.subject_entity_id, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&inst.target_entity_id, ptr, sizeof(u32));
        ptr += sizeof(u32);
        memcpy(&inst.target_x, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.target_y, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&inst.target_z, ptr, sizeof(q16_16));
        ptr += sizeof(q16_16);
        memcpy(&params_len, ptr, sizeof(u32));
        ptr += sizeof(u32);
        remaining -= sizeof(d_job_instance_id) + sizeof(d_job_template_id) + sizeof(u32) * 4u + sizeof(q16_16) * 3u;

        inst.params.len = params_len;
        inst.params.ptr = (unsigned char *)0;
        if (params_len > 0u) {
            if (remaining < params_len) {
                return -1;
            }
            inst.params.ptr = (unsigned char *)malloc(params_len);
            if (!inst.params.ptr) {
                return -1;
            }
            memcpy(inst.params.ptr, ptr, params_len);
            ptr += params_len;
            remaining -= params_len;
        }

        for (slot = 0u; slot < DJOB_MAX_INSTANCES; ++slot) {
            if (!g_job_entries[slot].in_use) {
                entry = &g_job_entries[slot];
                break;
            }
        }
        if (!entry) {
            if (inst.params.ptr) {
                free(inst.params.ptr);
            }
            return -1;
        }
        memset(entry, 0, sizeof(*entry));
        entry->world = w;
        entry->inst = inst;
        entry->in_use = 1;
        if (inst.id >= g_job_next_id) {
            g_job_next_id = inst.id + 1u;
        }
    }
    return 0;
}

static void d_job_init_instance_subsys(d_world *w) {
    u32 i;
    for (i = 0u; i < DJOB_MAX_INSTANCES; ++i) {
        if (g_job_entries[i].in_use && g_job_entries[i].world == w) {
            if (g_job_entries[i].inst.params.ptr) {
                free(g_job_entries[i].inst.params.ptr);
            }
            memset(&g_job_entries[i], 0, sizeof(g_job_entries[i]));
        }
    }
}

static void d_job_register_models(void) {
    /* No job-specific model family yet. */
}

static void d_job_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_job_subsystem = {
    D_SUBSYS_JOB,
    "job",
    1u,
    d_job_register_models,
    d_job_load_protos,
    d_job_init_instance_subsys,
    d_job_tick,
    d_job_save_chunk,
    d_job_load_chunk,
    d_job_save_instance,
    d_job_load_instance
};

void d_job_init(void) {
    if (g_job_registered) {
        return;
    }
    if (d_subsystem_register(&g_job_subsystem) == 0) {
        g_job_registered = 1;
    }
}
