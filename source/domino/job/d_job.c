#include <stdlib.h>
#include <string.h>

#include "job/d_job.h"

#include "ai/d_agent.h"
#include "core/d_account.h"
#include "core/d_subsystem.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "job/d_job_planner.h"
#include "research/d_research_state.h"
#include "struct/d_struct.h"

#define DJOB_MAX_RECORDS 1024u

typedef struct djob_entry_s {
    d_world      *world;
    d_job_record  rec;
    u8            reward_applied;
    int           in_use;
} djob_entry;

static djob_entry g_jobs[DJOB_MAX_RECORDS];
static d_job_id g_next_job_id = 1u;
static int g_job_registered = 0;

static djob_entry *djob_find_entry(d_world *w, d_job_id id) {
    u32 i;
    if (!w || id == 0u) {
        return (djob_entry *)0;
    }
    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (g_jobs[i].in_use && g_jobs[i].world == w && g_jobs[i].rec.id == id) {
            return &g_jobs[i];
        }
    }
    return (djob_entry *)0;
}

static djob_entry *djob_alloc_entry(void) {
    u32 i;
    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (!g_jobs[i].in_use) {
            return &g_jobs[i];
        }
    }
    return (djob_entry *)0;
}

static void djob_sort_ids(d_job_id *ids, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_job_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

int d_job_system_init(d_world *w) {
    u32 i;
    if (!w) {
        return -1;
    }
    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (g_jobs[i].in_use && g_jobs[i].world == w) {
            memset(&g_jobs[i], 0, sizeof(g_jobs[i]));
        }
    }
    return 0;
}

void d_job_system_shutdown(d_world *w) {
    (void)d_job_system_init(w);
}

d_job_id d_job_create(d_world *w, const d_job_record *init) {
    djob_entry *slot;
    d_job_record jr;
    d_job_id id;

    if (!w || !init || init->template_id == 0u) {
        return 0u;
    }
    slot = djob_alloc_entry();
    if (!slot) {
        return 0u;
    }

    jr = *init;
    id = jr.id;
    if (id == 0u) {
        id = g_next_job_id++;
    }
    jr.id = id;
    if (jr.state != D_JOB_STATE_PENDING &&
        jr.state != D_JOB_STATE_ASSIGNED &&
        jr.state != D_JOB_STATE_RUNNING &&
        jr.state != D_JOB_STATE_COMPLETED &&
        jr.state != D_JOB_STATE_CANCELLED) {
        jr.state = D_JOB_STATE_PENDING;
    }

    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->rec = jr;
    slot->reward_applied = 0u;
    slot->in_use = 1;

    if (id >= g_next_job_id) {
        g_next_job_id = id + 1u;
    }
    return id;
}

int d_job_cancel(d_world *w, d_job_id id) {
    djob_entry *e;
    if (!w || id == 0u) {
        return -1;
    }
    e = djob_find_entry(w, id);
    if (!e) {
        return -1;
    }
    e->rec.state = D_JOB_STATE_CANCELLED;
    return 0;
}

int d_job_get(const d_world *w, d_job_id id, d_job_record *out) {
    u32 i;
    if (!w || id == 0u || !out) {
        return -1;
    }
    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (g_jobs[i].in_use && g_jobs[i].world == (d_world *)w && g_jobs[i].rec.id == id) {
            *out = g_jobs[i].rec;
            return 0;
        }
    }
    return -1;
}

int d_job_update(d_world *w, const d_job_record *jr) {
    djob_entry *e;
    if (!w || !jr || jr->id == 0u) {
        return -1;
    }
    e = djob_find_entry(w, jr->id);
    if (!e) {
        return -1;
    }
    e->rec = *jr;
    return 0;
}

u32 d_job_count(const d_world *w) {
    u32 i;
    u32 count = 0u;
    if (!w) {
        return 0u;
    }
    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (g_jobs[i].in_use && g_jobs[i].world == (d_world *)w) {
            count += 1u;
        }
    }
    return count;
}

int d_job_get_by_index(const d_world *w, u32 index, d_job_record *out) {
    d_job_id ids[DJOB_MAX_RECORDS];
    u32 i;
    u32 count = 0u;

    if (!w || !out) {
        return -1;
    }

    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        if (g_jobs[i].in_use && g_jobs[i].world == (d_world *)w) {
            ids[count++] = g_jobs[i].rec.id;
        }
    }
    if (index >= count) {
        return -1;
    }
    djob_sort_ids(ids, count);
    return d_job_get(w, ids[index], out);
}

static void djob_tick_apply_rewards(d_world *w) {
    u32 i;

    for (i = 0u; i < DJOB_MAX_RECORDS; ++i) {
        const d_proto_job_template *tmpl;
        u32 offset;
        u32 tag;
        d_tlv_blob payload;
        int rc;

        if (!g_jobs[i].in_use || g_jobs[i].world != w) {
            continue;
        }
        if (g_jobs[i].reward_applied) {
            continue;
        }
        if (g_jobs[i].rec.state != D_JOB_STATE_COMPLETED) {
            continue;
        }

        tmpl = d_content_get_job_template(g_jobs[i].rec.template_id);
        if (tmpl && tmpl->rewards.ptr && tmpl->rewards.len > 0u) {
            offset = 0u;
            while ((rc = d_tlv_kv_next(&tmpl->rewards, &offset, &tag, &payload)) == 0) {
                if (tag == D_TLV_JOB_REWARD_PAYMENT) {
                    u32 p_off = 0u;
                    u32 p_tag;
                    d_tlv_blob p_payload;
                    d_account_id from = 0u;
                    d_account_id to = 0u;
                    q32_32 amount = 0;
                    int prc;

                    while ((prc = d_tlv_kv_next(&payload, &p_off, &p_tag, &p_payload)) == 0) {
                        if (p_tag == D_TLV_JOB_PAY_FROM_ACCOUNT) {
                            u32 tmp = 0u;
                            if (d_tlv_kv_read_u32(&p_payload, &tmp) == 0) {
                                from = (d_account_id)tmp;
                            }
                        } else if (p_tag == D_TLV_JOB_PAY_TO_ACCOUNT) {
                            u32 tmp = 0u;
                            if (d_tlv_kv_read_u32(&p_payload, &tmp) == 0) {
                                to = (d_account_id)tmp;
                            }
                        } else if (p_tag == D_TLV_JOB_PAY_AMOUNT) {
                            if (p_payload.ptr && p_payload.len == 8u) {
                                memcpy(&amount, p_payload.ptr, sizeof(q32_32));
                            }
                        }
                    }

                    if (from != 0u && to != 0u && amount > 0) {
                        (void)d_account_transfer(from, to, amount);
                    }
                }
            }
        }

        {
            d_org_id org_id = 0u;
            if (g_jobs[i].rec.target_struct_eid != 0u) {
                const d_struct_instance *st = d_struct_get(w, (d_struct_instance_id)g_jobs[i].rec.target_struct_eid);
                if (st) {
                    org_id = st->owner_org;
                }
            }
            if (org_id == 0u && g_jobs[i].rec.target_spline_id != 0u) {
                d_spline_instance sp;
                if (d_trans_spline_get(w, g_jobs[i].rec.target_spline_id, &sp) == 0) {
                    org_id = sp.owner_org;
                }
            }
            if (org_id == 0u && g_jobs[i].rec.assigned_agent != 0u) {
                d_agent_state a;
                if (d_agent_get(w, g_jobs[i].rec.assigned_agent, &a) == 0) {
                    org_id = a.owner_org;
                }
            }
            d_research_apply_job_completion(org_id, g_jobs[i].rec.template_id);
        }

        /* Rewards are optional and treated as best-effort. */
        g_jobs[i].reward_applied = 1u;
    }
}

void d_job_tick(d_world *w, u32 ticks) {
    if (!w || ticks == 0u) {
        return;
    }
    d_job_planner_tick(w, ticks);
    d_agent_tick(w, ticks);
    djob_tick_apply_rewards(w);
}

static int d_job_save_instance(d_world *w, d_tlv_blob *out) {
    u32 version;
    u32 job_count;
    u32 agent_count;
    u32 i;
    u32 total;
    unsigned char *buf;
    unsigned char *dst;

    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    if (!w) {
        return 0;
    }

    job_count = d_job_count(w);
    agent_count = d_agent_count(w);
    if (job_count == 0u && agent_count == 0u) {
        return 0;
    }

    version = 3u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* job_count */
    total += job_count * (
        sizeof(d_job_id) +
        sizeof(d_job_template_id) +
        sizeof(u16) + sizeof(u16) + /* state + pad */
        sizeof(d_agent_id) +
        sizeof(u32) +
        sizeof(d_spline_id) +
        sizeof(q32_32) * 3u +
        sizeof(q16_16)
    );
    total += 4u; /* agent_count */
    total += agent_count * (
        sizeof(d_agent_id) +
        sizeof(u32) + /* owner_eid */
        sizeof(d_org_id) + /* owner_org */
        sizeof(u32) + /* caps.tags */
        sizeof(q16_16) * 2u +
        sizeof(d_job_id) +
        sizeof(q32_32) * 3u +
        sizeof(u16) + sizeof(u16) /* flags + pad */
    );

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;

    memcpy(dst, &version, 4u); dst += 4u;
    memcpy(dst, &job_count, 4u); dst += 4u;

    {
        u32 written = 0u;
        for (i = 0u; i < job_count; ++i) {
            d_job_record jr;
            u16 state16;
            u16 pad16 = 0u;
            if (d_job_get_by_index(w, i, &jr) != 0) {
                continue;
            }
            memcpy(dst, &jr.id, sizeof(d_job_id)); dst += sizeof(d_job_id);
            memcpy(dst, &jr.template_id, sizeof(d_job_template_id)); dst += sizeof(d_job_template_id);
            state16 = (u16)jr.state;
            memcpy(dst, &state16, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &pad16, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &jr.assigned_agent, sizeof(d_agent_id)); dst += sizeof(d_agent_id);
            memcpy(dst, &jr.target_struct_eid, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &jr.target_spline_id, sizeof(d_spline_id)); dst += sizeof(d_spline_id);
            memcpy(dst, &jr.target_x, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &jr.target_y, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &jr.target_z, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &jr.progress, sizeof(q16_16)); dst += sizeof(q16_16);
            written += 1u;
        }
        /* If iteration skipped entries (shouldn't), fix up count for determinism. */
        if (written != job_count) {
            unsigned char *count_ptr = buf + 4u;
            memcpy(count_ptr, &written, 4u);
            job_count = written;
        }
    }

    memcpy(dst, &agent_count, 4u); dst += 4u;
    {
        u32 written = 0u;
        for (i = 0u; i < agent_count; ++i) {
            d_agent_state a;
            u16 pad16 = 0u;
            if (d_agent_get_by_index(w, i, &a) != 0) {
                continue;
            }
            memcpy(dst, &a.id, sizeof(d_agent_id)); dst += sizeof(d_agent_id);
            memcpy(dst, &a.owner_eid, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &a.owner_org, sizeof(d_org_id)); dst += sizeof(d_org_id);
            memcpy(dst, &a.caps.tags, sizeof(u32)); dst += sizeof(u32);
            memcpy(dst, &a.caps.max_speed, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &a.caps.max_carry_mass, sizeof(q16_16)); dst += sizeof(q16_16);
            memcpy(dst, &a.current_job, sizeof(d_job_id)); dst += sizeof(d_job_id);
            memcpy(dst, &a.pos_x, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &a.pos_y, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &a.pos_z, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &a.flags, sizeof(u16)); dst += sizeof(u16);
            memcpy(dst, &pad16, sizeof(u16)); dst += sizeof(u16);
            written += 1u;
        }
        if (written != agent_count) {
            unsigned char *count_ptr = buf + 4u + 4u + job_count * (
                sizeof(d_job_id) +
                sizeof(d_job_template_id) +
                sizeof(u16) + sizeof(u16) +
                sizeof(d_agent_id) +
                sizeof(u32) +
                sizeof(d_spline_id) +
                sizeof(q32_32) * 3u +
                sizeof(q16_16)
            );
            memcpy(count_ptr, &written, 4u);
            agent_count = written;
        }
    }

    out->ptr = buf;
    out->len = (u32)(dst - buf);
    return 0;
}

static int d_job_load_instance(d_world *w, const d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 job_count;
    u32 agent_count;
    u32 i;

    if (!w || !in) {
        return -1;
    }
    if (!in->ptr || in->len == 0u) {
        return 0;
    }

    ptr = in->ptr;
    remaining = in->len;
    if (remaining < 4u) {
        return -1;
    }
    memcpy(&version, ptr, 4u); ptr += 4u; remaining -= 4u;
    if (version != 2u && version != 3u) {
        return -1;
    }
    if (remaining < 4u) {
        return -1;
    }
    memcpy(&job_count, ptr, 4u); ptr += 4u; remaining -= 4u;

    for (i = 0u; i < job_count; ++i) {
        d_job_record jr;
        u16 state16;
        u16 pad16;
        if (remaining < sizeof(d_job_id) + sizeof(d_job_template_id) +
                        sizeof(u16) * 2u +
                        sizeof(d_agent_id) +
                        sizeof(u32) + sizeof(d_spline_id) +
                        sizeof(q32_32) * 3u +
                        sizeof(q16_16)) {
            return -1;
        }
        memset(&jr, 0, sizeof(jr));
        memcpy(&jr.id, ptr, sizeof(d_job_id)); ptr += sizeof(d_job_id);
        memcpy(&jr.template_id, ptr, sizeof(d_job_template_id)); ptr += sizeof(d_job_template_id);
        memcpy(&state16, ptr, sizeof(u16)); ptr += sizeof(u16);
        memcpy(&pad16, ptr, sizeof(u16)); ptr += sizeof(u16);
        (void)pad16;
        jr.state = (d_job_state)state16;
        memcpy(&jr.assigned_agent, ptr, sizeof(d_agent_id)); ptr += sizeof(d_agent_id);
        memcpy(&jr.target_struct_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
        memcpy(&jr.target_spline_id, ptr, sizeof(d_spline_id)); ptr += sizeof(d_spline_id);
        memcpy(&jr.target_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&jr.target_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&jr.target_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&jr.progress, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        remaining -= (u32)(sizeof(d_job_id) + sizeof(d_job_template_id) +
                           sizeof(u16) * 2u +
                           sizeof(d_agent_id) +
                           sizeof(u32) + sizeof(d_spline_id) +
                           sizeof(q32_32) * 3u +
                           sizeof(q16_16));
        if (d_job_create(w, &jr) == 0u) {
            return -1;
        }
    }

    if (remaining < 4u) {
        return -1;
    }
    memcpy(&agent_count, ptr, 4u); ptr += 4u; remaining -= 4u;

    for (i = 0u; i < agent_count; ++i) {
        d_agent_state a;
        u16 pad16;
        u32 need = 0u;
        need += (u32)sizeof(d_agent_id);
        need += (u32)sizeof(u32);      /* owner_eid */
        need += (u32)sizeof(u32);      /* caps.tags */
        need += (u32)sizeof(q16_16) * 2u;
        need += (u32)sizeof(d_job_id);
        need += (u32)sizeof(q32_32) * 3u;
        need += (u32)sizeof(u16) * 2u; /* flags + pad */
        if (version >= 3u) {
            need += (u32)sizeof(d_org_id);
        }
        if (remaining < need) {
            return -1;
        }
        memset(&a, 0, sizeof(a));
        memcpy(&a.id, ptr, sizeof(d_agent_id)); ptr += sizeof(d_agent_id);
        memcpy(&a.owner_eid, ptr, sizeof(u32)); ptr += sizeof(u32);
        if (version >= 3u) {
            memcpy(&a.owner_org, ptr, sizeof(d_org_id)); ptr += sizeof(d_org_id);
        } else {
            a.owner_org = 0u;
        }
        memcpy(&a.caps.tags, ptr, sizeof(u32)); ptr += sizeof(u32);
        memcpy(&a.caps.max_speed, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&a.caps.max_carry_mass, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&a.current_job, ptr, sizeof(d_job_id)); ptr += sizeof(d_job_id);
        memcpy(&a.pos_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&a.pos_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&a.pos_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&a.flags, ptr, sizeof(u16)); ptr += sizeof(u16);
        memcpy(&pad16, ptr, sizeof(u16)); ptr += sizeof(u16);
        (void)pad16;
        remaining -= need;
        if (d_agent_register(w, &a) == 0u) {
            return -1;
        }
    }

    return 0;
}

static int d_job_save_chunk(d_world *w, d_chunk *chunk, d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_job_load_chunk(d_world *w, d_chunk *chunk, const d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void d_job_init_instance_subsys(d_world *w) {
    (void)d_job_system_init(w);
    (void)d_agent_system_init(w);
}

static void d_job_register_models(void) {
    /* No standalone models yet. */
}

static void d_job_load_protos(const d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_job_subsystem = {
    D_SUBSYS_JOB,
    "job",
    2u,
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
