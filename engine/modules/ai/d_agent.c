/*
FILE: source/domino/ai/d_agent.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ai/d_agent
RESPONSIBILITY: Implements `d_agent`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "ai/d_agent.h"

#include "job/d_job.h"
#include "job/d_job_planner.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "struct/d_struct.h"
#include "trans/d_trans_spline.h"

#define DAGENT_MAX_AGENTS 256u

typedef struct dagent_entry_s {
    d_world       *world;
    d_agent_state  st;
    int            in_use;
} dagent_entry;

static dagent_entry g_agents[DAGENT_MAX_AGENTS];
static d_agent_id g_next_agent_id = 1u;

static q32_32 dagent_q32_from_q16(q16_16 v) {
    return ((q32_32)v) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
}

static q32_32 dagent_abs_q32(q32_32 v) {
    return (v < 0) ? (q32_32)(-v) : v;
}

static q16_16 dagent_ticks_to_q16(u32 ticks) {
    if (ticks == 0u) {
        return 0;
    }
    if (ticks > 0x7FFFu) {
        ticks = 0x7FFFu;
    }
    return (q16_16)((i32)ticks << Q16_16_FRAC_BITS);
}

static dagent_entry *dagent_find_entry(d_world *w, d_agent_id id) {
    u32 i;
    if (!w || id == 0u) {
        return (dagent_entry *)0;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (g_agents[i].in_use && g_agents[i].world == w && g_agents[i].st.id == id) {
            return &g_agents[i];
        }
    }
    return (dagent_entry *)0;
}

static dagent_entry *dagent_alloc_entry(void) {
    u32 i;
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (!g_agents[i].in_use) {
            return &g_agents[i];
        }
    }
    return (dagent_entry *)0;
}

int d_agent_system_init(d_world *w) {
    u32 i;
    if (!w) {
        return -1;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (g_agents[i].in_use && g_agents[i].world == w) {
            memset(&g_agents[i], 0, sizeof(g_agents[i]));
        }
    }
    return 0;
}

void d_agent_system_shutdown(d_world *w) {
    (void)d_agent_system_init(w);
}

d_agent_id d_agent_register(d_world *w, const d_agent_state *init) {
    dagent_entry *slot;
    d_agent_state st;
    d_agent_id requested_id;
    if (!w || !init) {
        return 0u;
    }
    requested_id = init->id;
    if (requested_id != 0u) {
        if (dagent_find_entry(w, requested_id)) {
            return 0u;
        }
    }
    slot = dagent_alloc_entry();
    if (!slot) {
        return 0u;
    }
    st = *init;
    if (requested_id != 0u) {
        st.id = requested_id;
    } else {
        st.id = g_next_agent_id++;
    }
    if (st.flags == 0u) {
        st.flags = D_AGENT_FLAG_IDLE;
    }
    memset(slot, 0, sizeof(*slot));
    slot->world = w;
    slot->st = st;
    slot->in_use = 1;

    if (st.id >= g_next_agent_id) {
        g_next_agent_id = st.id + 1u;
    }
    return st.id;
}

int d_agent_unregister(d_world *w, d_agent_id id) {
    dagent_entry *e = dagent_find_entry(w, id);
    if (!e) {
        return -1;
    }
    memset(e, 0, sizeof(*e));
    return 0;
}

int d_agent_get(const d_world *w, d_agent_id id, d_agent_state *out) {
    u32 i;
    if (!w || id == 0u || !out) {
        return -1;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (g_agents[i].in_use && g_agents[i].world == (d_world *)w && g_agents[i].st.id == id) {
            *out = g_agents[i].st;
            return 0;
        }
    }
    return -1;
}

int d_agent_update(d_world *w, const d_agent_state *st) {
    dagent_entry *e;
    if (!w || !st || st->id == 0u) {
        return -1;
    }
    e = dagent_find_entry(w, st->id);
    if (!e) {
        return -1;
    }
    e->st = *st;
    return 0;
}

u32 d_agent_count(const d_world *w) {
    u32 i;
    u32 count = 0u;
    if (!w) {
        return 0u;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (g_agents[i].in_use && g_agents[i].world == (d_world *)w) {
            count += 1u;
        }
    }
    return count;
}

static int dagent_collect_ids(const d_world *w, d_agent_id *out_ids, u32 cap, u32 *out_count) {
    u32 i;
    u32 count = 0u;
    if (out_count) *out_count = 0u;
    if (!w || !out_ids || cap == 0u) {
        return -1;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (g_agents[i].in_use && g_agents[i].world == (d_world *)w) {
            if (count < cap) {
                out_ids[count++] = g_agents[i].st.id;
            }
        }
    }
    if (out_count) *out_count = count;
    return 0;
}

static void dagent_sort_ids(d_agent_id *ids, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_agent_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

int d_agent_get_by_index(const d_world *w, u32 index, d_agent_state *out) {
    d_agent_id ids[DAGENT_MAX_AGENTS];
    u32 count = 0u;
    if (!w || !out) {
        return -1;
    }
    if (dagent_collect_ids(w, ids, DAGENT_MAX_AGENTS, &count) != 0) {
        return -1;
    }
    if (index >= count) {
        return -1;
    }
    dagent_sort_ids(ids, count);
    return d_agent_get(w, ids[index], out);
}

static int dagent_target_for_job(d_world *w, const d_job_record *jr, q32_32 *out_x, q32_32 *out_y, q32_32 *out_z) {
    if (!out_x || !out_y || !out_z) {
        return -1;
    }
    *out_x = 0;
    *out_y = 0;
    *out_z = 0;
    if (!w || !jr) {
        return -1;
    }
    if (jr->target_struct_eid != 0u) {
        const d_struct_instance *inst = d_struct_get(w, (d_struct_instance_id)jr->target_struct_eid);
        if (inst) {
            *out_x = dagent_q32_from_q16(inst->pos_x);
            *out_y = dagent_q32_from_q16(inst->pos_y);
            *out_z = dagent_q32_from_q16(inst->pos_z);
            return 0;
        }
    }
    if (jr->target_spline_id != 0u) {
        q32_32 sx, sy, sz;
        if (d_trans_spline_sample_pos(w, jr->target_spline_id, (q16_16)(1 << 15), &sx, &sy, &sz) == 0) {
            *out_x = sx;
            *out_y = sy;
            *out_z = sz;
            return 0;
        }
    }
    *out_x = jr->target_x;
    *out_y = jr->target_y;
    *out_z = jr->target_z;
    return 0;
}

static void dagent_move_toward(d_agent_state *a, q32_32 tx, q32_32 ty, q32_32 tz, q32_32 max_step) {
    q32_32 remaining;
    if (!a) {
        return;
    }
    remaining = max_step;
    a->flags &= (u16)~D_AGENT_FLAG_IDLE;
    a->flags |= D_AGENT_FLAG_MOVING;

    while (remaining > 0) {
        if (a->pos_x != tx) {
            q32_32 dx = tx - a->pos_x;
            q32_32 adx = dagent_abs_q32(dx);
            q32_32 step = (adx < remaining) ? adx : remaining;
            a->pos_x += (dx < 0) ? (q32_32)(-step) : step;
            remaining -= step;
            continue;
        }
        if (a->pos_y != ty) {
            q32_32 dy = ty - a->pos_y;
            q32_32 ady = dagent_abs_q32(dy);
            q32_32 step = (ady < remaining) ? ady : remaining;
            a->pos_y += (dy < 0) ? (q32_32)(-step) : step;
            remaining -= step;
            continue;
        }
        if (a->pos_z != tz) {
            q32_32 dz = tz - a->pos_z;
            q32_32 adz = dagent_abs_q32(dz);
            q32_32 step = (adz < remaining) ? adz : remaining;
            a->pos_z += (dz < 0) ? (q32_32)(-step) : step;
            remaining -= step;
            continue;
        }
        break;
    }

    if (a->pos_x == tx && a->pos_y == ty && a->pos_z == tz) {
        a->flags &= (u16)~D_AGENT_FLAG_MOVING;
        a->flags |= D_AGENT_FLAG_EXECUTING;
    }
}

static q16_16 dagent_job_duration(const d_proto_job_template *tmpl) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    q16_16 dur;
    int rc;

    if (!tmpl) {
        return d_q16_16_from_int(1);
    }
    if (!tmpl->requirements.ptr || tmpl->requirements.len == 0u) {
        return d_q16_16_from_int(1);
    }

    dur = 0;
    offset = 0u;
    while ((rc = d_tlv_kv_next(&tmpl->requirements, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_JOB_REQ_DURATION) {
            if (d_tlv_kv_read_q16_16(&payload, &dur) == 0 && dur > 0) {
                return dur;
            }
        }
    }

    return d_q16_16_from_int(1);
}

void d_agent_tick(d_world *w, u32 ticks) {
    u32 i;
    q32_32 step_q32;
    if (!w || ticks == 0u) {
        return;
    }

    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        d_agent_state a;
        d_job_record jr;
        const d_proto_job_template *tmpl;
        q32_32 tx, ty, tz;

        if (!g_agents[i].in_use || g_agents[i].world != w) {
            continue;
        }
        a = g_agents[i].st;

        if (a.current_job == 0u) {
            a.flags = D_AGENT_FLAG_IDLE;
            g_agents[i].st = a;
            continue;
        }
        if (d_job_get(w, a.current_job, &jr) != 0) {
            a.current_job = 0u;
            a.flags = D_AGENT_FLAG_IDLE;
            g_agents[i].st = a;
            continue;
        }
        if (jr.state == D_JOB_STATE_CANCELLED || jr.state == D_JOB_STATE_COMPLETED) {
            a.current_job = 0u;
            a.flags = D_AGENT_FLAG_IDLE;
            g_agents[i].st = a;
            continue;
        }

        tmpl = d_content_get_job_template(jr.template_id);
        if (!tmpl) {
            (void)d_job_cancel(w, jr.id);
            a.current_job = 0u;
            a.flags = D_AGENT_FLAG_IDLE;
            g_agents[i].st = a;
            continue;
        }

        (void)dagent_target_for_job(w, &jr, &tx, &ty, &tz);
        step_q32 = dagent_q32_from_q16(a.caps.max_speed);
        step_q32 = (q32_32)((i64)step_q32 * (i64)(i32)ticks);

        if (a.pos_x != tx || a.pos_y != ty || a.pos_z != tz) {
            dagent_move_toward(&a, tx, ty, tz, step_q32);
            g_agents[i].st = a;
            continue;
        }

        /* At target: begin or continue work. */
        if (jr.state == D_JOB_STATE_ASSIGNED) {
            jr.state = D_JOB_STATE_RUNNING;
            jr.progress = 0;
            (void)d_job_update(w, &jr);
        }

        if (tmpl->purpose == 0u) {
            /* Unknown purpose: treat as no-op. */
            g_agents[i].st = a;
            continue;
        }
        if (tmpl->purpose == (u16)D_JOB_PURPOSE_OPERATE_PROCESS) {
            /* OPERATE_PROCESS: stays running while assigned. */
            g_agents[i].st = a;
            continue;
        }

        jr.progress = d_q16_16_add(jr.progress, dagent_ticks_to_q16(ticks));
        if (jr.progress >= dagent_job_duration(tmpl)) {
            jr.state = D_JOB_STATE_COMPLETED;
            (void)d_job_update(w, &jr);
            a.current_job = 0u;
            a.flags = D_AGENT_FLAG_IDLE;
        }

        g_agents[i].st = a;
    }
}

int d_agent_validate(const d_world *w) {
    u32 i;
    const u32 known_mask =
        D_TAG_CAP_WALK |
        D_TAG_CAP_DRIVE |
        D_TAG_CAP_OPERATE_PROCESS |
        D_TAG_CAP_HAUL |
        D_TAG_CAP_BUILD;

    if (!w) {
        return -1;
    }
    for (i = 0u; i < DAGENT_MAX_AGENTS; ++i) {
        if (!g_agents[i].in_use || g_agents[i].world != (d_world *)w) {
            continue;
        }
        if ((g_agents[i].st.caps.tags & ~known_mask) != 0u) {
            return -1;
        }
    }
    return 0;
}
