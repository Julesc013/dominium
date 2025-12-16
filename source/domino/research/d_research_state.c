/*
FILE: source/domino/research/d_research_state.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / research/d_research_state
RESPONSIBILITY: Implements `d_research_state`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "research/d_research_state.h"

#include "core/d_subsystem.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"

#define DRESEARCH_MAX_ORGS 256u

typedef struct d_research_org_entry_s {
    d_org_id            org_id;
    u16                 research_count;
    d_research_progress *researches;
    int                 in_use;
} d_research_org_entry;

static d_research_org_entry g_research_orgs[DRESEARCH_MAX_ORGS];
static int g_research_initialized = 0;
static int g_research_registered = 0;

static d_research_org_entry *dres_find_org(d_org_id org_id) {
    u32 i;
    if (org_id == 0u) {
        return (d_research_org_entry *)0;
    }
    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        if (g_research_orgs[i].in_use && g_research_orgs[i].org_id == org_id) {
            return &g_research_orgs[i];
        }
    }
    return (d_research_org_entry *)0;
}

static d_research_org_entry *dres_alloc_org(void) {
    u32 i;
    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        if (!g_research_orgs[i].in_use) {
            return &g_research_orgs[i];
        }
    }
    return (d_research_org_entry *)0;
}

static d_research_progress *dres_find_progress(d_research_org_entry *e, d_research_id id) {
    u32 i;
    if (!e || !e->researches || e->research_count == 0u || id == 0u) {
        return (d_research_progress *)0;
    }
    for (i = 0u; i < (u32)e->research_count; ++i) {
        if (e->researches[i].id == id) {
            return &e->researches[i];
        }
    }
    return (d_research_progress *)0;
}

static q32_32 dres_required_points(const d_proto_research *proto) {
    u32 off;
    u32 tag;
    d_tlv_blob payload;
    q32_32 req = 0;
    int rc;

    if (!proto || !proto->cost.ptr || proto->cost.len == 0u) {
        return 0;
    }

    off = 0u;
    while ((rc = d_tlv_kv_next(&proto->cost, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_RESEARCH_COST_REQUIRED) {
            if (payload.ptr && payload.len == 8u) {
                memcpy(&req, payload.ptr, sizeof(q32_32));
            }
        }
    }
    if (req < 0) {
        req = 0;
    }
    return req;
}

static int dres_prereqs_satisfied(d_research_org_entry *e, const d_proto_research *proto) {
    u32 i;
    if (!e || !proto) {
        return 0;
    }
    for (i = 0u; i < (u32)proto->prereq_count; ++i) {
        d_research_progress *p = dres_find_progress(e, proto->prereq_ids[i]);
        if (!p || p->state != (u8)D_RESEARCH_STATE_COMPLETED) {
            return 0;
        }
    }
    return 1;
}

static void dres_update_lock_states(d_research_org_entry *e) {
    u32 i;
    if (!e || !e->researches) {
        return;
    }
    for (i = 0u; i < (u32)e->research_count; ++i) {
        d_research_progress *p = &e->researches[i];
        const d_proto_research *proto;
        if (p->state != (u8)D_RESEARCH_STATE_LOCKED) {
            continue;
        }
        proto = d_content_get_research(p->id);
        if (proto && dres_prereqs_satisfied(e, proto)) {
            p->state = (u8)D_RESEARCH_STATE_PENDING;
        }
    }
}

static d_research_id dres_find_active_id(d_research_org_entry *e) {
    u32 i;
    if (!e || !e->researches) {
        return 0u;
    }
    for (i = 0u; i < (u32)e->research_count; ++i) {
        if (e->researches[i].state == (u8)D_RESEARCH_STATE_ACTIVE) {
            return e->researches[i].id;
        }
    }
    return 0u;
}

static d_research_id dres_first_unlocked_pending(d_research_org_entry *e) {
    u32 i;
    d_research_id best = 0u;
    if (!e || !e->researches) {
        return 0u;
    }
    for (i = 0u; i < (u32)e->research_count; ++i) {
        const d_research_progress *p = &e->researches[i];
        if (p->state == (u8)D_RESEARCH_STATE_PENDING || p->state == (u8)D_RESEARCH_STATE_ACTIVE) {
            if (best == 0u || p->id < best) {
                best = p->id;
            }
        }
    }
    return best;
}

static int dres_id_in_list(d_research_id id, const d_research_id *ids, u32 count) {
    u32 i;
    if (id == 0u || !ids) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (ids[i] == id) {
            return 1;
        }
    }
    return 0;
}

static void dres_list_add_unique(d_research_id id, d_research_id *ids, u32 cap, u32 *count) {
    if (!ids || !count || id == 0u) {
        return;
    }
    if (*count >= cap) {
        return;
    }
    if (dres_id_in_list(id, ids, *count)) {
        return;
    }
    ids[*count] = id;
    *count += 1u;
}

static void dres_sort_ids(d_research_id *ids, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_research_id key = ids[i];
        u32 j = i;
        while (j > 0u && ids[j - 1u] > key) {
            ids[j] = ids[j - 1u];
            --j;
        }
        ids[j] = key;
    }
}

static void dres_collect_candidates_for_kind(d_research_point_kind kind, d_research_id *out_ids, u32 cap, u32 *out_count) {
    u32 i;
    u32 count;
    if (!out_count) {
        return;
    }
    *out_count = 0u;
    if (!out_ids || cap == 0u) {
        return;
    }

    count = d_content_research_point_source_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_research_point_source *src = d_content_get_research_point_source_by_index(i);
        u32 off = 0u;
        u32 tag;
        d_tlv_blob payload;
        u32 tags_all = 0u;
        u32 tags_any = 0u;
        int rc;

        if (!src || src->kind != kind) {
            continue;
        }

        while ((rc = d_tlv_kv_next(&src->params, &off, &tag, &payload)) == 0) {
            if (tag == D_TLV_RP_SOURCE_TARGET_RESEARCH_ID) {
                u32 rid = 0u;
                if (d_tlv_kv_read_u32(&payload, &rid) == 0) {
                    dres_list_add_unique((d_research_id)rid, out_ids, cap, out_count);
                }
            } else if (tag == D_TLV_RP_SOURCE_TARGET_RESEARCH_TAGS_ALL) {
                u32 mask = 0u;
                if (d_tlv_kv_read_u32(&payload, &mask) == 0) {
                    tags_all |= mask;
                }
            } else if (tag == D_TLV_RP_SOURCE_TARGET_RESEARCH_TAGS_ANY) {
                u32 mask = 0u;
                if (d_tlv_kv_read_u32(&payload, &mask) == 0) {
                    tags_any |= mask;
                }
            }
        }

        if (tags_all != 0u || tags_any != 0u) {
            u32 ri;
            u32 rcount = d_content_research_count();
            for (ri = 0u; ri < rcount; ++ri) {
                const d_proto_research *r = d_content_get_research_by_index(ri);
                if (!r) {
                    continue;
                }
                if (tags_all != 0u && (r->tags & tags_all) != tags_all) {
                    continue;
                }
                if (tags_any != 0u && (r->tags & tags_any) == 0u) {
                    continue;
                }
                dres_list_add_unique(r->id, out_ids, cap, out_count);
            }
        }
    }

    dres_sort_ids(out_ids, *out_count);
}

static d_research_id dres_choose_target_for_candidates(d_research_org_entry *e, const d_research_id *ids, u32 count) {
    u32 i;
    d_research_id active;

    if (!e) {
        return 0u;
    }
    if (!ids || count == 0u) {
        return 0u;
    }

    active = dres_find_active_id(e);
    if (active != 0u && dres_id_in_list(active, ids, count)) {
        d_research_progress *p = dres_find_progress(e, active);
        if (p && p->state != (u8)D_RESEARCH_STATE_LOCKED && p->state != (u8)D_RESEARCH_STATE_COMPLETED) {
            return active;
        }
    }

    for (i = 0u; i < count; ++i) {
        d_research_progress *p = dres_find_progress(e, ids[i]);
        if (!p) {
            continue;
        }
        if (p->state == (u8)D_RESEARCH_STATE_COMPLETED || p->state == (u8)D_RESEARCH_STATE_LOCKED) {
            continue;
        }
        return p->id;
    }

    return 0u;
}

int d_research_system_init(void) {
    if (g_research_initialized) {
        return 0;
    }
    memset(g_research_orgs, 0, sizeof(g_research_orgs));
    g_research_initialized = 1;
    return 0;
}

void d_research_system_shutdown(void) {
    u32 i;
    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        if (g_research_orgs[i].in_use) {
            if (g_research_orgs[i].researches) {
                free(g_research_orgs[i].researches);
            }
            memset(&g_research_orgs[i], 0, sizeof(g_research_orgs[i]));
        }
    }
    memset(g_research_orgs, 0, sizeof(g_research_orgs));
    g_research_initialized = 0;
}

int d_research_org_init(d_org_id org_id) {
    d_research_org_entry *e;
    u32 count;
    u32 i;

    if (org_id == 0u) {
        return -1;
    }
    if (!g_research_initialized) {
        (void)d_research_system_init();
    }

    e = dres_find_org(org_id);
    if (e) {
        return 0;
    }
    e = dres_alloc_org();
    if (!e) {
        return -1;
    }

    memset(e, 0, sizeof(*e));
    e->org_id = org_id;
    e->researches = (d_research_progress *)0;
    e->research_count = 0u;
    e->in_use = 1;

    count = d_content_research_count();
    if (count > 0xFFFFu) {
        return -1;
    }
    if (count == 0u) {
        return 0;
    }

    e->researches = (d_research_progress *)malloc(sizeof(d_research_progress) * count);
    if (!e->researches) {
        memset(e, 0, sizeof(*e));
        return -1;
    }
    memset(e->researches, 0, sizeof(d_research_progress) * count);
    e->research_count = (u16)count;

    for (i = 0u; i < count; ++i) {
        const d_proto_research *r = d_content_get_research_by_index(i);
        if (!r) {
            continue;
        }
        e->researches[i].id = r->id;
        e->researches[i].progress = 0;
        e->researches[i].state = (u8)(r->prereq_count > 0u ? D_RESEARCH_STATE_LOCKED : D_RESEARCH_STATE_PENDING);
    }

    return 0;
}

int d_research_org_shutdown(d_org_id org_id) {
    d_research_org_entry *e = dres_find_org(org_id);
    if (!e) {
        return -1;
    }
    if (e->researches) {
        free(e->researches);
    }
    memset(e, 0, sizeof(*e));
    return 0;
}

int d_research_tick(d_org_id org_id, u32 ticks) {
    (void)org_id;
    (void)ticks;
    return 0;
}

int d_research_get_org_state(d_org_id org_id, d_research_org_state *out) {
    d_research_org_entry *e;
    if (!out) {
        return -1;
    }
    e = dres_find_org(org_id);
    if (!e) {
        return -1;
    }
    out->org_id = e->org_id;
    out->research_count = e->research_count;
    out->researches = e->researches;
    return 0;
}

int d_research_set_active(d_org_id org_id, d_research_id id) {
    d_research_org_entry *e;
    d_research_progress *p;
    u32 i;

    e = dres_find_org(org_id);
    if (!e) {
        return -1;
    }
    p = dres_find_progress(e, id);
    if (!p) {
        return -1;
    }
    if (p->state == (u8)D_RESEARCH_STATE_LOCKED || p->state == (u8)D_RESEARCH_STATE_COMPLETED) {
        return -1;
    }

    for (i = 0u; i < (u32)e->research_count; ++i) {
        if (e->researches[i].state == (u8)D_RESEARCH_STATE_ACTIVE) {
            e->researches[i].state = (u8)D_RESEARCH_STATE_PENDING;
        }
    }
    p->state = (u8)D_RESEARCH_STATE_ACTIVE;
    return 0;
}

int d_research_add_progress(d_org_id org_id, d_research_id id, q32_32 amount) {
    d_research_org_entry *e;
    d_research_progress *p;
    const d_proto_research *proto;
    q32_32 required;

    if (amount <= 0) {
        return -1;
    }
    e = dres_find_org(org_id);
    if (!e) {
        return -1;
    }
    p = dres_find_progress(e, id);
    if (!p) {
        return -1;
    }
    if (p->state == (u8)D_RESEARCH_STATE_LOCKED) {
        return -1;
    }
    if (p->state == (u8)D_RESEARCH_STATE_COMPLETED) {
        return 0;
    }

    proto = d_content_get_research(id);
    required = dres_required_points(proto);

    p->progress += amount;
    if (required > 0 && p->progress >= required) {
        p->progress = required;
        p->state = (u8)D_RESEARCH_STATE_COMPLETED;
        dres_update_lock_states(e);
    }
    if (required == 0) {
        p->state = (u8)D_RESEARCH_STATE_COMPLETED;
        dres_update_lock_states(e);
    }

    return 0;
}

int d_research_is_unlocked(d_org_id org_id, d_research_id id) {
    d_research_org_entry *e = dres_find_org(org_id);
    d_research_progress *p;
    if (!e) {
        return 0;
    }
    p = dres_find_progress(e, id);
    if (!p) {
        return 0;
    }
    return p->state != (u8)D_RESEARCH_STATE_LOCKED;
}

int d_research_is_completed(d_org_id org_id, d_research_id id) {
    d_research_org_entry *e = dres_find_org(org_id);
    d_research_progress *p;
    if (!e) {
        return 0;
    }
    p = dres_find_progress(e, id);
    if (!p) {
        return 0;
    }
    return p->state == (u8)D_RESEARCH_STATE_COMPLETED;
}

static void dres_apply_points(d_research_org_entry *e, d_research_point_kind kind, q32_32 amount) {
    d_research_id cand_ids[128];
    u32 cand_count = 0u;
    d_research_id target = 0u;

    if (!e || amount <= 0) {
        return;
    }

    dres_collect_candidates_for_kind(kind, cand_ids, 128u, &cand_count);
    if (cand_count > 0u) {
        target = dres_choose_target_for_candidates(e, cand_ids, cand_count);
    }
    if (target == 0u) {
        /* Fallback to active or first unlocked pending. */
        target = dres_find_active_id(e);
        if (target == 0u) {
            target = dres_first_unlocked_pending(e);
        }
    }
    if (target != 0u) {
        (void)d_research_add_progress(e->org_id, target, amount);
    }
}

void d_research_apply_process_completion(d_org_id org_id, d_process_id process_id) {
    d_research_org_entry *e;
    const d_proto_process *p;
    u32 i;
    if (org_id == 0u || process_id == 0u) {
        return;
    }
    e = dres_find_org(org_id);
    if (!e) {
        return;
    }
    p = d_content_get_process(process_id);
    if (!p || p->research_yield_count == 0u || !p->research_yields) {
        return;
    }
    for (i = 0u; i < (u32)p->research_yield_count; ++i) {
        d_research_point_yield y = p->research_yields[i];
        if (y.kind == 0u || y.amount <= 0) {
            continue;
        }
        dres_apply_points(e, y.kind, y.amount);
    }
}

void d_research_apply_job_completion(d_org_id org_id, d_job_template_id template_id) {
    d_research_org_entry *e;
    const d_proto_job_template *t;
    u32 i;
    if (org_id == 0u || template_id == 0u) {
        return;
    }
    e = dres_find_org(org_id);
    if (!e) {
        return;
    }
    t = d_content_get_job_template(template_id);
    if (!t || t->research_yield_count == 0u || !t->research_yields) {
        return;
    }
    for (i = 0u; i < (u32)t->research_yield_count; ++i) {
        d_research_point_yield y = t->research_yields[i];
        if (y.kind == 0u || y.amount <= 0) {
            continue;
        }
        dres_apply_points(e, y.kind, y.amount);
    }
}

static int d_research_save_chunk(struct d_world *w, struct d_chunk *chunk, struct d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_research_load_chunk(struct d_world *w, struct d_chunk *chunk, const struct d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void d_research_init_instance_subsys(struct d_world *w) {
    (void)w;
    d_research_system_shutdown();
    (void)d_research_system_init();
}

static void d_research_tick_subsys(struct d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static void dres_sort_progress(d_research_progress *p, u32 count) {
    u32 i;
    for (i = 1u; i < count; ++i) {
        d_research_progress key = p[i];
        u32 j = i;
        while (j > 0u && p[j - 1u].id > key.id) {
            p[j] = p[j - 1u];
            --j;
        }
        p[j] = key;
    }
}

static int d_research_save_instance(struct d_world *w, struct d_tlv_blob *out) {
    u32 version;
    u32 org_count = 0u;
    u32 i;
    u32 total;
    unsigned char *buf;
    unsigned char *dst;

    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;

    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        if (g_research_orgs[i].in_use) {
            org_count += 1u;
        }
    }
    if (org_count == 0u) {
        return 0;
    }

    version = 1u;
    total = 0u;
    total += 4u; /* version */
    total += 4u; /* org_count */
    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        if (!g_research_orgs[i].in_use) {
            continue;
        }
        total += sizeof(d_org_id);
        total += 4u; /* research_count (u32) */
        total += (u32)g_research_orgs[i].research_count * (sizeof(d_research_id) + sizeof(q32_32) + 4u);
    }

    buf = (unsigned char *)malloc(total);
    if (!buf) {
        return -1;
    }
    dst = buf;
    memcpy(dst, &version, 4u); dst += 4u;
    memcpy(dst, &org_count, 4u); dst += 4u;

    for (i = 0u; i < DRESEARCH_MAX_ORGS; ++i) {
        d_research_org_entry *e = &g_research_orgs[i];
        u32 rcnt;
        u32 ri;
        d_research_progress *tmp;

        if (!e->in_use) {
            continue;
        }

        rcnt = (u32)e->research_count;
        memcpy(dst, &e->org_id, sizeof(d_org_id)); dst += sizeof(d_org_id);
        memcpy(dst, &rcnt, 4u); dst += 4u;

        if (rcnt == 0u || !e->researches) {
            continue;
        }

        tmp = (d_research_progress *)malloc(sizeof(d_research_progress) * rcnt);
        if (!tmp) {
            free(buf);
            return -1;
        }
        memcpy(tmp, e->researches, sizeof(d_research_progress) * rcnt);
        dres_sort_progress(tmp, rcnt);

        for (ri = 0u; ri < rcnt; ++ri) {
            u8 state = tmp[ri].state;
            u8 pad[3] = { 0u, 0u, 0u };
            memcpy(dst, &tmp[ri].id, sizeof(d_research_id)); dst += sizeof(d_research_id);
            memcpy(dst, &tmp[ri].progress, sizeof(q32_32)); dst += sizeof(q32_32);
            memcpy(dst, &state, 1u); dst += 1u;
            memcpy(dst, pad, 3u); dst += 3u;
        }

        free(tmp);
    }

    out->ptr = buf;
    out->len = total;
    return 0;
}

static int d_research_load_instance(struct d_world *w, const struct d_tlv_blob *in) {
    const unsigned char *ptr;
    u32 remaining;
    u32 version;
    u32 org_count;
    u32 oi;

    (void)w;
    d_research_system_shutdown();
    (void)d_research_system_init();

    if (!in || !in->ptr || in->len == 0u) {
        return 0;
    }

    ptr = in->ptr;
    remaining = in->len;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(&version, ptr, 4u); ptr += 4u; remaining -= 4u;
    memcpy(&org_count, ptr, 4u); ptr += 4u; remaining -= 4u;
    if (version != 1u) {
        return -1;
    }

    for (oi = 0u; oi < org_count; ++oi) {
        d_org_id org_id;
        u32 rcnt;
        u32 ri;
        d_research_org_entry *e;

        if (remaining < sizeof(d_org_id) + 4u) {
            return -1;
        }
        memcpy(&org_id, ptr, sizeof(d_org_id)); ptr += sizeof(d_org_id); remaining -= sizeof(d_org_id);
        memcpy(&rcnt, ptr, 4u); ptr += 4u; remaining -= 4u;

        if (d_research_org_init(org_id) != 0) {
            return -1;
        }
        e = dres_find_org(org_id);
        if (!e) {
            return -1;
        }
        if ((u32)e->research_count != rcnt) {
            return -1;
        }

        for (ri = 0u; ri < rcnt; ++ri) {
            d_research_id rid;
            q32_32 prog;
            u8 state;
            u8 pad[3];
            d_research_progress *p;

            if (remaining < sizeof(d_research_id) + sizeof(q32_32) + 4u) {
                return -1;
            }
            memcpy(&rid, ptr, sizeof(d_research_id)); ptr += sizeof(d_research_id);
            memcpy(&prog, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
            memcpy(&state, ptr, 1u); ptr += 1u;
            memcpy(pad, ptr, 3u); ptr += 3u;
            (void)pad;
            remaining -= (u32)(sizeof(d_research_id) + sizeof(q32_32) + 4u);

            p = dres_find_progress(e, rid);
            if (!p) {
                return -1;
            }
            p->progress = prog;
            p->state = state;
        }
    }

    return remaining == 0u ? 0 : -1;
}

static void d_research_register_models(void) {
    /* No standalone models. */
}

static void d_research_load_protos(const struct d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_research_subsystem = {
    D_SUBSYS_RESEARCH,
    "research",
    1u,
    d_research_register_models,
    d_research_load_protos,
    d_research_init_instance_subsys,
    d_research_tick_subsys,
    d_research_save_chunk,
    d_research_load_chunk,
    d_research_save_instance,
    d_research_load_instance
};

void d_research_register_subsystem(void) {
    if (g_research_registered) {
        return;
    }
    if (d_subsystem_register(&g_research_subsystem) == 0) {
        g_research_registered = 1;
    }
}

