#include <string.h>

#include "sim/d_sim_process.h"

#include "core/d_container_state.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "econ/d_econ_metrics.h"
#include "job/d_job.h"
#include "job/d_job_planner.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "struct/d_struct.h"

#define DSIM_PROCESS_MAX_WORLDS 8u
#define DSIM_PROCESS_MAX_STRUCTS 256u
#define DSIM_PROCESS_MAX_STATS 1024u

typedef struct dsim_process_world_s {
    d_world              *world;
    u32                   ticks_observed;
    d_sim_process_stats   stats[DSIM_PROCESS_MAX_STATS];
    u32                   stat_count;
    int                   in_use;
} dsim_process_world;

static dsim_process_world g_proc_worlds[DSIM_PROCESS_MAX_WORLDS];

static dsim_process_world *dproc_find_world(d_world *w) {
    u32 i;
    for (i = 0u; i < DSIM_PROCESS_MAX_WORLDS; ++i) {
        if (g_proc_worlds[i].in_use && g_proc_worlds[i].world == w) {
            return &g_proc_worlds[i];
        }
    }
    return (dsim_process_world *)0;
}

static dsim_process_world *dproc_get_or_create_world(d_world *w) {
    dsim_process_world *st;
    u32 i;
    if (!w) {
        return (dsim_process_world *)0;
    }
    st = dproc_find_world(w);
    if (st) {
        return st;
    }
    for (i = 0u; i < DSIM_PROCESS_MAX_WORLDS; ++i) {
        if (!g_proc_worlds[i].in_use) {
            memset(&g_proc_worlds[i], 0, sizeof(g_proc_worlds[i]));
            g_proc_worlds[i].world = w;
            g_proc_worlds[i].ticks_observed = 0u;
            g_proc_worlds[i].stat_count = 0u;
            g_proc_worlds[i].in_use = 1;
            return &g_proc_worlds[i];
        }
    }
    return (dsim_process_world *)0;
}

static d_sim_process_stats *dproc_stats_for_process(dsim_process_world *st, d_process_id pid) {
    u32 i;
    if (!st || pid == 0u) {
        return (d_sim_process_stats *)0;
    }
    for (i = 0u; i < st->stat_count; ++i) {
        if (st->stats[i].process_id == pid) {
            return &st->stats[i];
        }
    }
    if (st->stat_count >= DSIM_PROCESS_MAX_STATS) {
        return (d_sim_process_stats *)0;
    }
    memset(&st->stats[st->stat_count], 0, sizeof(st->stats[st->stat_count]));
    st->stats[st->stat_count].process_id = pid;
    st->stat_count += 1u;
    return &st->stats[st->stat_count - 1u];
}

static u32 dproc_container_count_item(const d_container_state *c, d_item_id item_id) {
    u32 i;
    u32 slots;
    if (!c || c->proto_id == 0u || !c->slots || item_id == 0u) {
        return 0u;
    }
    slots = (c->slot_count > 0u) ? (u32)c->slot_count : 1u;
    for (i = 0u; i < slots; ++i) {
        if (c->slots[i].item_id == item_id) {
            return c->slots[i].count;
        }
    }
    return 0u;
}

static u32 dproc_amount_per_cycle(q16_16 rate_per_tick, q16_16 base_duration) {
    i64 prod;
    q16_16 q;
    i32 v;
    if (rate_per_tick <= 0 || base_duration <= 0) {
        return 0u;
    }
    prod = (i64)rate_per_tick * (i64)base_duration;
    q = (q16_16)(prod >> Q16_16_FRAC_BITS);
    v = d_q16_16_to_int(q);
    if (v <= 0) {
        return 0u;
    }
    return (u32)v;
}

static d_process_id dproc_first_allowed_process(const d_proto_structure *proto) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u32 pid_u32;
    if (!proto || !proto->processes.ptr || proto->processes.len == 0u) {
        return 0u;
    }
    offset = 0u;
    while ((rc = d_tlv_kv_next(&proto->processes, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_STRUCT_PROCESS_ALLOWED) {
            if (d_tlv_kv_read_u32(&payload, &pid_u32) == 0) {
                return (d_process_id)pid_u32;
            }
        }
    }
    return 0u;
}

static int dproc_has_active_operator_job(d_world *w, u32 struct_eid) {
    u32 i;
    u32 count;
    if (!w || struct_eid == 0u) {
        return 0;
    }
    count = d_job_count(w);
    for (i = 0u; i < count; ++i) {
        d_job_record jr;
        const d_proto_job_template *tmpl;
        if (d_job_get_by_index(w, i, &jr) != 0) {
            continue;
        }
        if (jr.target_struct_eid != struct_eid) {
            continue;
        }
        if (jr.state != D_JOB_STATE_RUNNING) {
            continue;
        }
        tmpl = d_content_get_job_template(jr.template_id);
        if (!tmpl) {
            continue;
        }
        if (tmpl->purpose == (u16)D_JOB_PURPOSE_OPERATE_PROCESS) {
            return 1;
        }
    }
    return 0;
}

static int dproc_has_any_operator_job(d_world *w, u32 struct_eid) {
    u32 i;
    u32 count;
    if (!w || struct_eid == 0u) {
        return 0;
    }
    count = d_job_count(w);
    for (i = 0u; i < count; ++i) {
        d_job_record jr;
        const d_proto_job_template *tmpl;
        if (d_job_get_by_index(w, i, &jr) != 0) {
            continue;
        }
        if (jr.target_struct_eid != struct_eid) {
            continue;
        }
        if (jr.state == D_JOB_STATE_CANCELLED || jr.state == D_JOB_STATE_COMPLETED) {
            continue;
        }
        tmpl = d_content_get_job_template(jr.template_id);
        if (!tmpl) {
            continue;
        }
        if (tmpl->purpose == (u16)D_JOB_PURPOSE_OPERATE_PROCESS) {
            return 1;
        }
    }
    return 0;
}

static d_job_template_id dproc_find_operator_template(d_structure_proto_id sid, d_process_id pid) {
    u32 i;
    u32 count = d_content_job_template_count();
    d_job_template_id best = 0u;
    for (i = 0u; i < count; ++i) {
        const d_proto_job_template *t = d_content_get_job_template_by_index(i);
        if (!t) {
            continue;
        }
        if (t->purpose != (u16)D_JOB_PURPOSE_OPERATE_PROCESS) {
            continue;
        }
        if (t->process_id != 0u && pid != 0u && t->process_id != pid) {
            continue;
        }
        if (t->structure_id != 0u && sid != 0u && t->structure_id != sid) {
            continue;
        }
        if (best == 0u || t->id < best) {
            best = t->id;
        }
    }
    return best;
}

static void dproc_ensure_operator_job(d_world *w, const d_struct_instance *inst, const d_proto_structure *proto, d_process_id pid) {
    d_job_template_id tmpl_id;
    d_job_id jid;
    if (!w || !inst || !proto) {
        return;
    }
    if ((proto->tags & D_TAG_STRUCTURE_MACHINE) == 0u) {
        return;
    }
    if (dproc_has_any_operator_job(w, inst->id)) {
        return;
    }
    tmpl_id = dproc_find_operator_template(proto->id, pid);
    if (tmpl_id == 0u) {
        return;
    }
    jid = 0u;
    (void)d_job_request(w, tmpl_id, inst->id, 0u, 0, 0, 0, &jid);
}

static void dproc_tick_machine(
    dsim_process_world   *pst,
    d_world              *w,
    d_struct_instance    *inst,
    const d_proto_structure *proto,
    u32                   ticks
) {
    const d_proto_process *proc;
    d_process_id pid;
    q16_16 policy_mult;
    q16_16 dt;
    u32 term_i;
    u16 active = 0u;

    if (!pst || !w || !inst || !proto || ticks == 0u) {
        return;
    }

    pid = inst->machine.active_process_id;
    if (pid == 0u) {
        pid = dproc_first_allowed_process(proto);
        inst->machine.active_process_id = pid;
    }
    if (pid == 0u) {
        inst->machine.state_flags = D_MACHINE_FLAG_IDLE;
        return;
    }

    proc = d_content_get_process(pid);
    if (!proc || proc->base_duration <= 0) {
        inst->machine.state_flags = D_MACHINE_FLAG_IDLE;
        return;
    }

    policy_mult = d_q16_16_from_int(1);
    {
        d_policy_context ctx;
        d_policy_effect_result eff;
        memset(&ctx, 0, sizeof(ctx));
        ctx.org_id = inst->owner_org;
        ctx.subject_kind = D_POLICY_SUBJECT_PROCESS;
        ctx.subject_id = (u32)pid;
        ctx.subject_tags = proc->tags;
        (void)d_policy_evaluate(&ctx, &eff);
        if (eff.allowed == 0u || eff.multiplier == 0) {
            inst->machine.state_flags = (u16)(D_MACHINE_FLAG_BLOCKED | D_MACHINE_FLAG_POLICY_BLOCKED);
            return;
        }
        policy_mult = eff.multiplier;
    }

    /* Ensure operator jobs exist for agent-required machines. */
    dproc_ensure_operator_job(w, inst, proto, pid);

    if ((proto->tags & D_TAG_STRUCTURE_MACHINE) != 0u) {
        if (!dproc_has_active_operator_job(w, inst->id)) {
            inst->machine.state_flags = D_MACHINE_FLAG_IDLE;
            return;
        }
    }

    /* If we're not mid-cycle, require all inputs to be present before starting. */
    if (inst->machine.progress == 0) {
        for (term_i = 0u; term_i < (u32)proc->io_count; ++term_i) {
            const d_process_io_term *t = &proc->io_terms[term_i];
            u32 need;
            if (t->kind != (u16)D_PROCESS_IO_INPUT_ITEM) {
                continue;
            }
            need = dproc_amount_per_cycle(t->rate, proc->base_duration);
            if (need == 0u) {
                continue;
            }
            if (dproc_container_count_item(&inst->inv_in, t->item_id) < need) {
                inst->machine.state_flags = D_MACHINE_FLAG_IDLE;
                return;
            }
        }
    }

    dt = (q16_16)((i32)ticks << Q16_16_FRAC_BITS);
    dt = d_q16_16_mul(dt, policy_mult);
    if (dt <= 0) {
        inst->machine.state_flags = (u16)(D_MACHINE_FLAG_BLOCKED | D_MACHINE_FLAG_POLICY_BLOCKED);
        return;
    }
    inst->machine.progress = d_q16_16_add(inst->machine.progress, dt);
    inst->machine.state_flags = D_MACHINE_FLAG_ACTIVE;

    while (inst->machine.progress >= proc->base_duration) {
        /* Validate inputs at commit time. */
        for (term_i = 0u; term_i < (u32)proc->io_count; ++term_i) {
            const d_process_io_term *t = &proc->io_terms[term_i];
            u32 need;
            if (t->kind != (u16)D_PROCESS_IO_INPUT_ITEM) {
                continue;
            }
            need = dproc_amount_per_cycle(t->rate, proc->base_duration);
            if (need == 0u) {
                continue;
            }
            if (dproc_container_count_item(&inst->inv_in, t->item_id) < need) {
                inst->machine.state_flags = D_MACHINE_FLAG_BLOCKED;
                inst->machine.progress = proc->base_duration;
                return;
            }
        }

        /* Consume inputs then produce outputs. */
        for (term_i = 0u; term_i < (u32)proc->io_count; ++term_i) {
            const d_process_io_term *t = &proc->io_terms[term_i];
            u32 need;
            u32 unpacked = 0u;
            if (t->kind != (u16)D_PROCESS_IO_INPUT_ITEM) {
                continue;
            }
            need = dproc_amount_per_cycle(t->rate, proc->base_duration);
            if (need == 0u) {
                continue;
            }
            if (d_container_unpack_items(&inst->inv_in, t->item_id, need, &unpacked) != 0 || unpacked != need) {
                inst->machine.state_flags = D_MACHINE_FLAG_BLOCKED;
                inst->machine.progress = proc->base_duration;
                return;
            }
            if (unpacked > 0u) {
                q32_32 q = (q32_32)(((i64)unpacked) << Q32_32_FRAC_BITS);
                d_econ_register_production(inst->owner_org, t->item_id, -q);
            }
        }

        for (term_i = 0u; term_i < (u32)proc->io_count; ++term_i) {
            const d_process_io_term *t = &proc->io_terms[term_i];
            u32 outn;
            u32 packed = 0u;
            if (t->kind != (u16)D_PROCESS_IO_OUTPUT_ITEM) {
                continue;
            }
            outn = dproc_amount_per_cycle(t->rate, proc->base_duration);
            if (outn == 0u) {
                continue;
            }
            if (inst->inv_out.proto_id != 0u) {
                (void)d_container_pack_items(&inst->inv_out, t->item_id, outn, &packed);
            }
            if (packed > 0u) {
                q32_32 q = (q32_32)(((i64)packed) << Q32_32_FRAC_BITS);
                d_econ_register_production(inst->owner_org, t->item_id, q);
                d_sim_process_stats *s = dproc_stats_for_process(pst, pid);
                if (s) {
                    s->output_units += packed;
                }
                active = 1u;
            }
        }

        {
            d_sim_process_stats *s = dproc_stats_for_process(pst, pid);
            if (s) {
                s->cycles_completed += 1u;
            }
        }

        d_research_apply_process_completion(inst->owner_org, pid);

        inst->machine.progress = d_q16_16_sub(inst->machine.progress, proc->base_duration);
        if (inst->machine.progress < 0) {
            inst->machine.progress = 0;
        }
    }

    (void)active;
}

void d_sim_process_tick(d_world *w, u32 ticks) {
    dsim_process_world *pst;
    d_struct_instance_id ids[DSIM_PROCESS_MAX_STRUCTS];
    u32 count;
    u32 i;

    if (!w || ticks == 0u) {
        return;
    }
    pst = dproc_get_or_create_world(w);
    if (!pst) {
        return;
    }
    pst->ticks_observed += ticks;

    count = d_struct_count(w);
    if (count == 0u) {
        return;
    }
    if (count > DSIM_PROCESS_MAX_STRUCTS) {
        count = DSIM_PROCESS_MAX_STRUCTS;
    }

    {
        u32 filled = 0u;
        for (i = 0u; i < count; ++i) {
            const d_struct_instance *view = d_struct_get_by_index(w, i);
            if (!view) {
                break;
            }
            ids[filled++] = view->id;
        }
        count = filled;
    }

    /* Deterministic order by instance ID. */
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
        if (ids[i] == 0u) {
            continue;
        }
        inst = d_struct_get_mutable(w, ids[i]);
        if (!inst) {
            continue;
        }
        proto = d_content_get_structure(inst->proto_id);
        if (!proto) {
            continue;
        }
        if (!proto->processes.ptr || proto->processes.len == 0u) {
            continue;
        }
        dproc_tick_machine(pst, w, inst, proto, ticks);
    }
}

u32 d_sim_process_stats_count(const d_world *w) {
    dsim_process_world *pst;
    if (!w) {
        return 0u;
    }
    pst = dproc_find_world((d_world *)w);
    if (!pst) {
        return 0u;
    }
    return pst->stat_count;
}

static void dproc_sort_stats(d_sim_process_stats *s, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_sim_process_stats key = s[i];
        u32 j = i;
        while (j > 0u && s[j - 1u].process_id > key.process_id) {
            s[j] = s[j - 1u];
            --j;
        }
        s[j] = key;
    }
}

int d_sim_process_stats_get_by_index(const d_world *w, u32 index, d_sim_process_stats *out) {
    dsim_process_world *pst;
    d_sim_process_stats tmp[DSIM_PROCESS_MAX_STATS];
    u32 count;

    if (!w || !out) {
        return -1;
    }
    pst = dproc_find_world((d_world *)w);
    if (!pst) {
        return -1;
    }
    count = pst->stat_count;
    if (index >= count) {
        return -1;
    }
    memcpy(tmp, pst->stats, sizeof(d_sim_process_stats) * count);
    dproc_sort_stats(tmp, count);
    *out = tmp[index];
    out->ticks_observed = pst->ticks_observed;
    return 0;
}
