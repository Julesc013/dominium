#include <string.h>

#include "job/d_job_planner.h"

#include "ai/d_agent.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "job/d_job.h"
#include "policy/d_policy.h"
#include "struct/d_struct.h"

#define DJOB_PLANNER_MAX_JOBS   1024u
#define DJOB_PLANNER_MAX_AGENTS 256u

static int djobp_collect_job_ids(d_world *w, d_job_id *out_ids, u32 cap, u32 *out_count) {
    u32 i;
    u32 count;
    if (out_count) *out_count = 0u;
    if (!w || !out_ids || cap == 0u) {
        return -1;
    }
    count = d_job_count(w);
    if (count > cap) {
        count = cap;
    }
    for (i = 0u; i < count; ++i) {
        d_job_record jr;
        if (d_job_get_by_index(w, i, &jr) == 0) {
            out_ids[i] = jr.id;
        } else {
            out_ids[i] = 0u;
        }
    }
    if (out_count) *out_count = count;
    return 0;
}

static int djobp_collect_agent_ids(d_world *w, d_agent_id *out_ids, u32 cap, u32 *out_count) {
    u32 i;
    u32 count;
    if (out_count) *out_count = 0u;
    if (!w || !out_ids || cap == 0u) {
        return -1;
    }
    count = d_agent_count(w);
    if (count > cap) {
        count = cap;
    }
    for (i = 0u; i < count; ++i) {
        d_agent_state a;
        if (d_agent_get_by_index(w, i, &a) == 0) {
            out_ids[i] = a.id;
        } else {
            out_ids[i] = 0u;
        }
    }
    if (out_count) *out_count = count;
    return 0;
}

static void djobp_sort_u32(u32 *ids, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        u32 key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

static d_content_tag djobp_required_agent_tags(const d_tlv_blob *reqs) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    d_content_tag tags = 0u;
    int rc;

    if (!reqs || !reqs->ptr || reqs->len == 0u) {
        return 0u;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(reqs, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_JOB_REQ_AGENT_TAGS) {
            (void)d_tlv_kv_read_u32(&payload, &tags);
        }
    }

    return tags;
}

static int djobp_agent_eligible_for_job(d_world *w, d_agent_id aid, const d_job_record *jr, const d_proto_job_template *tmpl) {
    d_agent_state a;
    d_content_tag need;
    (void)jr;
    if (!w || !tmpl || aid == 0u) {
        return 0;
    }
    if (d_agent_get(w, aid, &a) != 0) {
        return 0;
    }
    if (a.current_job != 0u) {
        return 0;
    }
    need = djobp_required_agent_tags(&tmpl->requirements);
    if ((a.caps.tags & need) != need) {
        return 0;
    }
    return 1;
}

int d_job_request(
    d_world           *w,
    d_job_template_id  tmpl_id,
    u32                target_struct_eid,
    d_spline_id        target_spline_id,
    q32_32             x,
    q32_32             y,
    q32_32             z,
    d_job_id          *out_job_id
) {
    d_job_record jr;
    d_job_id id;
    d_org_id org_id = 0u;
    const d_proto_job_template *tmpl = (const d_proto_job_template *)0;

    if (out_job_id) {
        *out_job_id = 0u;
    }
    if (!w || tmpl_id == 0u) {
        return -1;
    }

    /* Policy gate job creation based on org + template context. */
    tmpl = d_content_get_job_template(tmpl_id);
    if (target_struct_eid != 0u) {
        const d_struct_instance *st = d_struct_get(w, (d_struct_instance_id)target_struct_eid);
        if (st) {
            org_id = st->owner_org;
        }
    }
    if (org_id == 0u && target_spline_id != 0u) {
        d_spline_instance sp;
        if (d_trans_spline_get(w, target_spline_id, &sp) == 0) {
            org_id = sp.owner_org;
        }
    }
    {
        d_policy_context ctx;
        d_policy_effect_result eff;
        memset(&ctx, 0, sizeof(ctx));
        ctx.org_id = org_id;
        ctx.subject_kind = D_POLICY_SUBJECT_JOB_TEMPLATE;
        ctx.subject_id = (u32)tmpl_id;
        ctx.subject_tags = tmpl ? tmpl->tags : 0u;
        (void)d_policy_evaluate(&ctx, &eff);
        if (eff.allowed == 0u) {
            return -1;
        }
    }

    memset(&jr, 0, sizeof(jr));
    jr.id = 0u;
    jr.template_id = tmpl_id;
    jr.state = D_JOB_STATE_PENDING;
    jr.assigned_agent = 0u;
    jr.target_struct_eid = target_struct_eid;
    jr.target_spline_id = target_spline_id;
    jr.target_x = x;
    jr.target_y = y;
    jr.target_z = z;
    jr.progress = 0;

    id = d_job_create(w, &jr);
    if (id == 0u) {
        return -1;
    }
    if (out_job_id) {
        *out_job_id = id;
    }
    return 0;
}

void d_job_planner_tick(d_world *w, u32 ticks) {
    d_job_id job_ids[DJOB_PLANNER_MAX_JOBS];
    d_agent_id agent_ids[DJOB_PLANNER_MAX_AGENTS];
    u32 job_count = 0u;
    u32 agent_count = 0u;
    u32 ji;
    u32 ai;

    (void)ticks;
    if (!w) {
        return;
    }

    if (djobp_collect_job_ids(w, (d_job_id *)job_ids, DJOB_PLANNER_MAX_JOBS, &job_count) != 0) {
        return;
    }
    if (djobp_collect_agent_ids(w, (d_agent_id *)agent_ids, DJOB_PLANNER_MAX_AGENTS, &agent_count) != 0) {
        return;
    }

    djobp_sort_u32((u32 *)job_ids, job_count);
    djobp_sort_u32((u32 *)agent_ids, agent_count);

    for (ji = 0u; ji < job_count; ++ji) {
        d_job_record jr;
        const d_proto_job_template *tmpl;

        if (job_ids[ji] == 0u) {
            continue;
        }
        if (d_job_get(w, job_ids[ji], &jr) != 0) {
            continue;
        }
        if (jr.state != D_JOB_STATE_PENDING) {
            continue;
        }
        tmpl = d_content_get_job_template(jr.template_id);
        if (!tmpl) {
            (void)d_job_cancel(w, jr.id);
            continue;
        }

        for (ai = 0u; ai < agent_count; ++ai) {
            d_agent_id aid = agent_ids[ai];
            d_agent_state a;

            if (aid == 0u) {
                continue;
            }
            if (!djobp_agent_eligible_for_job(w, aid, &jr, tmpl)) {
                continue;
            }
            if (d_agent_get(w, aid, &a) != 0) {
                continue;
            }

            jr.assigned_agent = aid;
            jr.state = D_JOB_STATE_ASSIGNED;
            jr.progress = 0;
            (void)d_job_update(w, &jr);

            a.current_job = jr.id;
            a.flags = D_AGENT_FLAG_MOVING;
            (void)d_agent_update(w, &a);

            agent_ids[ai] = 0u;
            break;
        }
    }
}
