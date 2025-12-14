/* TRANS deterministic compilation pipeline (C89). */
#include "trans/compile/dg_trans_compile.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "domino/core/fixed.h"
#include "core/dg_order_key.h"
#include "sim/sched/dg_phase.h"

static void dg_trans_compiled_init(dg_trans_compiled *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_trans_spatial_index_init(&c->spatial);
}

static void dg_trans_compiled_free(dg_trans_compiled *c) {
    u32 i;
    if (!c) return;

    if (c->alignments) {
        for (i = 0u; i < c->alignment_count; ++i) {
            dg_trans_compiled_alignment *a = &c->alignments[i];
            u32 si;
            if (a->slotmaps) {
                for (si = 0u; si < a->seg_count; ++si) {
                    dg_trans_segment_slotmap_free(&a->slotmaps[si]);
                }
                free(a->slotmaps);
            }
            if (a->segs) free(a->segs);
            memset(a, 0, sizeof(*a));
        }
        free(c->alignments);
    }

    if (c->junctions) {
        for (i = 0u; i < c->junction_count; ++i) {
            dg_trans_compiled_junction *j = &c->junctions[i];
            if (j->incidents) free(j->incidents);
            memset(j, 0, sizeof(*j));
        }
        free(c->junctions);
    }

    dg_trans_spatial_index_free(&c->spatial);
    dg_trans_compiled_init(c);
}

static u32 dg_trans_compiled_alignment_lower_bound(const dg_trans_compiled *c, dg_trans_alignment_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!c) return 0u;
    hi = c->alignment_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (c->alignments[mid].alignment_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 dg_trans_compiled_junction_lower_bound(const dg_trans_compiled *c, dg_trans_junction_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!c) return 0u;
    hi = c->junction_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (c->junctions[mid].junction_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static dg_trans_compiled_alignment *dg_trans_compiled_get_or_add_alignment(dg_trans_compiled *c, dg_trans_alignment_id id) {
    u32 idx;
    dg_trans_compiled_alignment *arr;
    u32 new_cap;
    if (!c || id == 0u) return (dg_trans_compiled_alignment *)0;

    idx = dg_trans_compiled_alignment_lower_bound(c, id);
    if (idx < c->alignment_count && c->alignments[idx].alignment_id == id) {
        return &c->alignments[idx];
    }

    if (c->alignment_count + 1u > c->alignment_capacity) {
        new_cap = c->alignment_capacity ? c->alignment_capacity : 8u;
        while (new_cap < c->alignment_count + 1u) {
            if (new_cap > 0x7FFFFFFFu) {
                new_cap = c->alignment_count + 1u;
                break;
            }
            new_cap *= 2u;
        }
        arr = (dg_trans_compiled_alignment *)realloc(c->alignments, sizeof(dg_trans_compiled_alignment) * (size_t)new_cap);
        if (!arr) return (dg_trans_compiled_alignment *)0;
        if (new_cap > c->alignment_capacity) {
            memset(&arr[c->alignment_capacity], 0, sizeof(dg_trans_compiled_alignment) * (size_t)(new_cap - c->alignment_capacity));
        }
        c->alignments = arr;
        c->alignment_capacity = new_cap;
    }

    if (idx < c->alignment_count) {
        memmove(&c->alignments[idx + 1u], &c->alignments[idx],
                sizeof(dg_trans_compiled_alignment) * (size_t)(c->alignment_count - idx));
    }
    memset(&c->alignments[idx], 0, sizeof(c->alignments[idx]));
    c->alignments[idx].alignment_id = id;
    c->alignments[idx].last_length_q = (dg_q)(-1);
    c->alignment_count += 1u;
    return &c->alignments[idx];
}

static dg_trans_compiled_junction *dg_trans_compiled_get_or_add_junction(dg_trans_compiled *c, dg_trans_junction_id id) {
    u32 idx;
    dg_trans_compiled_junction *arr;
    u32 new_cap;
    if (!c || id == 0u) return (dg_trans_compiled_junction *)0;

    idx = dg_trans_compiled_junction_lower_bound(c, id);
    if (idx < c->junction_count && c->junctions[idx].junction_id == id) {
        return &c->junctions[idx];
    }

    if (c->junction_count + 1u > c->junction_capacity) {
        new_cap = c->junction_capacity ? c->junction_capacity : 8u;
        while (new_cap < c->junction_count + 1u) {
            if (new_cap > 0x7FFFFFFFu) {
                new_cap = c->junction_count + 1u;
                break;
            }
            new_cap *= 2u;
        }
        arr = (dg_trans_compiled_junction *)realloc(c->junctions, sizeof(dg_trans_compiled_junction) * (size_t)new_cap);
        if (!arr) return (dg_trans_compiled_junction *)0;
        if (new_cap > c->junction_capacity) {
            memset(&arr[c->junction_capacity], 0, sizeof(dg_trans_compiled_junction) * (size_t)(new_cap - c->junction_capacity));
        }
        c->junctions = arr;
        c->junction_capacity = new_cap;
    }

    if (idx < c->junction_count) {
        memmove(&c->junctions[idx + 1u], &c->junctions[idx],
                sizeof(dg_trans_compiled_junction) * (size_t)(c->junction_count - idx));
    }
    memset(&c->junctions[idx], 0, sizeof(c->junctions[idx]));
    c->junctions[idx].junction_id = id;
    c->junction_count += 1u;
    return &c->junctions[idx];
}

void dg_trans_compiler_init(dg_trans_compiler *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
    dg_trans_compiled_init(&c->compiled);
    dg_trans_dirty_init(&c->dirty);
    dg_work_queue_init(&c->work_q);
    c->microseg_max_len_q = 0;
    c->chunk_size_q = 0;
}

void dg_trans_compiler_free(dg_trans_compiler *c) {
    if (!c) return;
    dg_trans_compiled_free(&c->compiled);
    dg_trans_dirty_free(&c->dirty);
    dg_work_queue_free(&c->work_q);
    dg_trans_compiler_init(c);
}

int dg_trans_compiler_reserve(dg_trans_compiler *c, u32 work_queue_capacity, u32 spatial_capacity) {
    if (!c) return -1;
    if (dg_work_queue_reserve(&c->work_q, work_queue_capacity) != 0) return -2;
    if (dg_trans_spatial_index_reserve(&c->compiled.spatial, spatial_capacity) != 0) return -3;
    return 0;
}

int dg_trans_compiler_set_params(dg_trans_compiler *c, dg_q microseg_max_len_q, dg_q chunk_size_q) {
    if (!c) return -1;
    if (microseg_max_len_q <= 0) return -2;
    if (chunk_size_q <= 0) return -3;
    c->microseg_max_len_q = microseg_max_len_q;
    c->chunk_size_q = chunk_size_q;
    return 0;
}

static const dg_trans_alignment *dg_trans_find_alignment(const dg_trans_compile_input *in, dg_trans_alignment_id id) {
    u32 i;
    if (!in || !in->alignments) return (const dg_trans_alignment *)0;
    for (i = 0u; i < in->alignment_count; ++i) {
        if (in->alignments[i].id == id) return &in->alignments[i];
    }
    return (const dg_trans_alignment *)0;
}

static const dg_trans_section_archetype *dg_trans_find_section(const dg_trans_compile_input *in, dg_trans_section_archetype_id id) {
    u32 i;
    if (!in || !in->sections) return (const dg_trans_section_archetype *)0;
    for (i = 0u; i < in->section_count; ++i) {
        if (in->sections[i].id == id) return &in->sections[i];
    }
    return (const dg_trans_section_archetype *)0;
}

static const dg_trans_junction *dg_trans_find_junction(const dg_trans_compile_input *in, dg_trans_junction_id id) {
    u32 i;
    if (!in || !in->junctions) return (const dg_trans_junction *)0;
    for (i = 0u; i < in->junction_count; ++i) {
        if (in->junctions[i].id == id) return &in->junctions[i];
    }
    return (const dg_trans_junction *)0;
}

static int dg_trans_compiled_alignment_resize(dg_trans_compiler *c, dg_trans_compiled_alignment *ca, u32 new_count) {
    dg_trans_microseg *new_segs;
    dg_trans_segment_slotmap *new_maps;
    u32 new_cap;
    u32 i;

    if (!c || !ca) return -1;

    if (new_count > ca->seg_capacity) {
        new_cap = ca->seg_capacity ? ca->seg_capacity : 16u;
        while (new_cap < new_count) {
            if (new_cap > 0x7FFFFFFFu) {
                new_cap = new_count;
                break;
            }
            new_cap *= 2u;
        }
        new_segs = (dg_trans_microseg *)realloc(ca->segs, sizeof(dg_trans_microseg) * (size_t)new_cap);
        if (!new_segs) return -2;
        new_maps = (dg_trans_segment_slotmap *)realloc(ca->slotmaps, sizeof(dg_trans_segment_slotmap) * (size_t)new_cap);
        if (!new_maps) {
            ca->segs = new_segs;
            return -3;
        }
        /* Zero-init new region. */
        if (new_cap > ca->seg_capacity) {
            memset(&new_segs[ca->seg_capacity], 0, sizeof(dg_trans_microseg) * (size_t)(new_cap - ca->seg_capacity));
            memset(&new_maps[ca->seg_capacity], 0, sizeof(dg_trans_segment_slotmap) * (size_t)(new_cap - ca->seg_capacity));
        }
        ca->segs = new_segs;
        ca->slotmaps = new_maps;
        ca->seg_capacity = new_cap;
    }

    /* If shrinking, free per-segment slotmaps and remove spatial entries for removed segments. */
    if (new_count < ca->seg_count) {
        for (i = new_count; i < ca->seg_count; ++i) {
            dg_trans_segment_id sid;
            sid.alignment_id = ca->alignment_id;
            sid.segment_index = i;
            (void)dg_trans_spatial_index_remove_segment(&c->compiled.spatial, &sid);
            dg_trans_segment_slotmap_free(&ca->slotmaps[i]);
        }
    }

    /* Initialize any newly added slotmap entries. */
    if (new_count > ca->seg_count) {
        for (i = ca->seg_count; i < new_count; ++i) {
            dg_trans_segment_slotmap_init(&ca->slotmaps[i]);
        }
    }

    ca->seg_count = new_count;
    return 0;
}

static u32 dg_trans_microseg_expected_count(dg_q length_q, dg_q max_len_q) {
    u64 len_raw;
    u64 max_raw;
    u64 n;
    if (length_q <= 0 || max_len_q <= 0) return 0u;
    len_raw = (u64)(i64)length_q;
    max_raw = (u64)(i64)max_len_q;
    if (max_raw == 0u) return 0u;
    n = (len_raw + max_raw - 1u) / max_raw;
    if (n > 0xFFFFFFFFULL) n = 0xFFFFFFFFULL;
    return (u32)n;
}

static dg_q dg_trans_mul_q_u32(dg_q v, u32 m) {
    u64 uv;
    u64 prod;
    if (v <= 0 || m == 0u) return 0;
    uv = (u64)(i64)v;
    prod = uv * (u64)m;
    if (prod > (u64)0x7FFFFFFFFFFFFFFFULL) {
        return (dg_q)0x7FFFFFFFFFFFFFFFLL;
    }
    return (dg_q)(i64)prod;
}

static int dg_trans_compile_microseg_range(dg_trans_compiler *c, const dg_trans_compile_input *in, dg_trans_alignment_id alignment_id, u32 seg0, u32 seg1) {
    const dg_trans_alignment *a;
    dg_trans_compiled_alignment *ca;
    dg_q length_q;
    u32 expected_count;
    u32 i;

    if (!c || !in) return -1;
    if (c->microseg_max_len_q <= 0) return -2;
    if (c->chunk_size_q <= 0) return -3;
    if (alignment_id == 0u) return -4;

    a = dg_trans_find_alignment(in, alignment_id);
    if (!a) return -5;

    ca = dg_trans_compiled_get_or_add_alignment(&c->compiled, alignment_id);
    if (!ca) return -6;

    if (dg_trans_alignment_length_q(a, &length_q) != 0) return -7;
    expected_count = dg_trans_microseg_expected_count(length_q, c->microseg_max_len_q);

    if (dg_trans_compiled_alignment_resize(c, ca, expected_count) != 0) return -8;
    ca->last_length_q = length_q;

    if (expected_count == 0u) return 0;
    if (seg0 >= expected_count) return 0;
    if (seg1 >= expected_count) seg1 = expected_count - 1u;
    if (seg1 < seg0) return 0;

    for (i = seg0; i <= seg1; ++i) {
        dg_trans_microseg seg;
        dg_q s_begin;
        dg_q s_end;
        dg_vec3_q p0;
        dg_vec3_q p1;
        dg_vec3_q tan;
        dg_q roll;
        dg_trans_aabb bbox;
        dg_trans_frame f;
        dg_trans_segment_id sid;

        s_begin = dg_trans_mul_q_u32(c->microseg_max_len_q, i);
        s_end = (dg_q)d_q48_16_add((q48_16)s_begin, (q48_16)c->microseg_max_len_q);
        if (s_end > length_q) s_end = length_q;

        (void)dg_trans_alignment_eval_pos(a, s_begin, &p0);
        (void)dg_trans_alignment_eval_pos(a, s_end, &p1);
        if (dg_trans_alignment_eval_tangent(a, s_begin, &tan) != 0) {
            /* Fallback: attempt tangent at end. */
            (void)dg_trans_alignment_eval_tangent(a, s_end, &tan);
        }
        (void)dg_trans_alignment_eval_roll(a, s_begin, &roll);

        bbox.min.x = (p0.x < p1.x) ? p0.x : p1.x;
        bbox.min.y = (p0.y < p1.y) ? p0.y : p1.y;
        bbox.min.z = (p0.z < p1.z) ? p0.z : p1.z;
        bbox.max.x = (p0.x > p1.x) ? p0.x : p1.x;
        bbox.max.y = (p0.y > p1.y) ? p0.y : p1.y;
        bbox.max.z = (p0.z > p1.z) ? p0.z : p1.z;

        if (dg_trans_frame_build(p0, tan, roll, &f) != 0) {
            /* As a last resort, build with world forward. */
            dg_vec3_q fw;
            fw.x = (dg_q)((i64)1 << 16);
            fw.y = 0;
            fw.z = 0;
            (void)dg_trans_frame_build(p0, fw, roll, &f);
        }

        memset(&seg, 0, sizeof(seg));
        seg.id.alignment_id = alignment_id;
        seg.id.segment_index = i;
        seg.s_begin = s_begin;
        seg.s_end = s_end;
        seg.bbox = bbox;
        seg.frame0 = f;

        ca->segs[i] = seg;

        /* Update chunk-aligned spatial index entries for this segment. */
        sid.alignment_id = alignment_id;
        sid.segment_index = i;
        (void)dg_trans_spatial_index_remove_segment(&c->compiled.spatial, &sid);
        (void)dg_trans_spatial_index_add_segment(&c->compiled.spatial, &ca->segs[i], c->chunk_size_q);
    }

    return 0;
}

static int dg_trans_compile_slotmap_range(dg_trans_compiler *c, const dg_trans_compile_input *in, dg_trans_alignment_id alignment_id, u32 seg0, u32 seg1) {
    const dg_trans_alignment *a;
    dg_trans_compiled_alignment *ca;
    const dg_trans_section_archetype *section;

    if (!c || !in) return -1;
    if (alignment_id == 0u) return -2;

    a = dg_trans_find_alignment(in, alignment_id);
    if (!a) return -3;
    ca = dg_trans_compiled_get_or_add_alignment(&c->compiled, alignment_id);
    if (!ca) return -4;

    section = dg_trans_find_section(in, a->section_id);
    if (!section) {
        /* No section: clear slotmaps in range. */
        u32 i;
        if (seg0 >= ca->seg_count) return 0;
        if (seg1 >= ca->seg_count) seg1 = ca->seg_count - 1u;
        for (i = seg0; i <= seg1; ++i) {
            dg_trans_segment_slotmap_clear(&ca->slotmaps[i]);
        }
        return 0;
    }

    return dg_trans_slotmap_rebuild_range(
        ca->slotmaps,
        ca->seg_count,
        ca->segs,
        ca->seg_count,
        alignment_id,
        section,
        in->attachments,
        in->attachment_count,
        seg0,
        seg1
    );
}

static int dg_trans_compile_junction(dg_trans_compiler *c, const dg_trans_compile_input *in, dg_trans_junction_id junction_id) {
    const dg_trans_junction *j;
    dg_trans_compiled_junction *cj;
    u32 need;

    if (!c || !in) return -1;
    if (junction_id == 0u) return -2;

    j = dg_trans_find_junction(in, junction_id);
    if (!j) return -3;

    cj = dg_trans_compiled_get_or_add_junction(&c->compiled, junction_id);
    if (!cj) return -4;

    need = j->incident_count;
    if (need == 0u) {
        cj->incident_count = 0u;
        return 0;
    }

    if (need > cj->incident_capacity) {
        u32 new_cap = cj->incident_capacity ? cj->incident_capacity : 4u;
        dg_trans_junction_incident *arr;
        while (new_cap < need) {
            if (new_cap > 0x7FFFFFFFu) {
                new_cap = need;
                break;
            }
            new_cap *= 2u;
        }
        arr = (dg_trans_junction_incident *)realloc(cj->incidents, sizeof(dg_trans_junction_incident) * (size_t)new_cap);
        if (!arr) return -5;
        if (new_cap > cj->incident_capacity) {
            memset(&arr[cj->incident_capacity], 0, sizeof(dg_trans_junction_incident) * (size_t)(new_cap - cj->incident_capacity));
        }
        cj->incidents = arr;
        cj->incident_capacity = new_cap;
    }

    memcpy(cj->incidents, j->incidents, sizeof(dg_trans_junction_incident) * (size_t)need);
    cj->incident_count = need;
    return 0;
}

int dg_trans_compiler_sync(dg_trans_compiler *c, const dg_trans_compile_input *in) {
    u32 i;
    if (!c || !in) return -1;
    for (i = 0u; i < in->alignment_count; ++i) {
        if (!dg_trans_compiled_get_or_add_alignment(&c->compiled, in->alignments[i].id)) return -2;
    }
    for (i = 0u; i < in->junction_count; ++i) {
        if (!dg_trans_compiled_get_or_add_junction(&c->compiled, in->junctions[i].id)) return -3;
    }
    return 0;
}

static int dg_trans_work_item_payload_equals(const dg_work_item *it, const unsigned char *p, u32 len) {
    u32 i;
    if (!it) return 0;
    if (it->payload_inline_len != len) return 0;
    for (i = 0u; i < len; ++i) {
        if (it->payload_inline[i] != p[i]) return 0;
    }
    return 1;
}

static int dg_trans_enqueue_unique(dg_work_queue *q, const dg_work_item *it, const unsigned char *payload, u32 payload_len) {
    u32 i;
    if (!q || !it) return -1;
    for (i = 0u; i < q->count; ++i) {
        const dg_work_item *e = &q->items[i];
        if (dg_order_key_cmp(&e->key, &it->key) != 0) continue;
        if (e->work_type_id != it->work_type_id) continue;
        if (payload_len <= DG_WORK_ITEM_INLINE_CAP) {
            if (dg_trans_work_item_payload_equals(e, payload, payload_len)) {
                return 1;
            }
        }
    }
    return dg_work_queue_push(q, it);
}

static void dg_trans_make_key_for_range(dg_order_key *out_key, dg_type_id work_type, dg_entity_id entity_id, u32 seg0) {
    dg_order_key k;
    dg_order_key_clear(&k);
    k.phase = (u16)DG_PH_TOPOLOGY;
    k._pad16 = 0u;
    k.domain_id = 0u;
    k.chunk_id = 0u;
    k.entity_id = entity_id;
    k.component_id = (u64)seg0;
    k.type_id = work_type;
    k.seq = 0u;
    k._pad32 = 0u;
    if (out_key) *out_key = k;
}

static void dg_trans_make_key_for_junction(dg_order_key *out_key, dg_type_id work_type, dg_entity_id junction_id) {
    dg_order_key k;
    dg_order_key_clear(&k);
    k.phase = (u16)DG_PH_TOPOLOGY;
    k._pad16 = 0u;
    k.domain_id = 0u;
    k.chunk_id = 0u;
    k.entity_id = junction_id;
    k.component_id = 0u;
    k.type_id = work_type;
    k.seq = 0u;
    k._pad32 = 0u;
    if (out_key) *out_key = k;
}

typedef struct dg_trans_work_range_payload {
    u64 alignment_id;
    u32 seg0;
    u32 seg1;
} dg_trans_work_range_payload;

typedef struct dg_trans_work_junction_payload {
    u64 junction_id;
} dg_trans_work_junction_payload;

int dg_trans_compiler_enqueue_dirty(dg_trans_compiler *c, dg_tick tick) {
    u32 i;
    if (!c) return -1;
    if (c->microseg_max_len_q <= 0) return -2;

    for (i = 0u; i < c->dirty.alignment_count; ++i) {
        dg_trans_dirty_alignment *da = &c->dirty.alignments[i];
        u32 seg0;
        u32 seg1;

        if (da->microseg.dirty) {
            dg_work_item it;
            dg_trans_work_range_payload pl;
            unsigned char bytes[DG_WORK_ITEM_INLINE_CAP];
            u32 cost;

            if (dg_trans_dirty_range_to_seg_span(da->microseg.s0, da->microseg.s1, c->microseg_max_len_q, &seg0, &seg1) == 0) {
                dg_work_item_clear(&it);
                dg_trans_make_key_for_range(&it.key, DG_TRANS_WORK_MICROSEG_RANGE, (dg_entity_id)da->alignment_id, seg0);
                it.work_type_id = DG_TRANS_WORK_MICROSEG_RANGE;
                cost = (seg1 >= seg0) ? (seg1 - seg0 + 1u) : 1u;
                it.cost_units = cost;
                it.enqueue_tick = tick;
                pl.alignment_id = da->alignment_id;
                pl.seg0 = seg0;
                pl.seg1 = seg1;
                memcpy(bytes, &pl, sizeof(pl));
                (void)dg_work_item_set_payload_inline(&it, bytes, (u32)sizeof(pl));
                (void)dg_trans_enqueue_unique(&c->work_q, &it, bytes, (u32)sizeof(pl));
            }
            da->microseg.dirty = D_FALSE;
        }

        if (da->slotmap.dirty) {
            dg_work_item it;
            dg_trans_work_range_payload pl;
            unsigned char bytes[DG_WORK_ITEM_INLINE_CAP];
            u32 cost;

            if (dg_trans_dirty_range_to_seg_span(da->slotmap.s0, da->slotmap.s1, c->microseg_max_len_q, &seg0, &seg1) == 0) {
                dg_work_item_clear(&it);
                dg_trans_make_key_for_range(&it.key, DG_TRANS_WORK_SLOTMAP_RANGE, (dg_entity_id)da->alignment_id, seg0);
                it.work_type_id = DG_TRANS_WORK_SLOTMAP_RANGE;
                cost = (seg1 >= seg0) ? (seg1 - seg0 + 1u) : 1u;
                it.cost_units = cost;
                it.enqueue_tick = tick;
                pl.alignment_id = da->alignment_id;
                pl.seg0 = seg0;
                pl.seg1 = seg1;
                memcpy(bytes, &pl, sizeof(pl));
                (void)dg_work_item_set_payload_inline(&it, bytes, (u32)sizeof(pl));
                (void)dg_trans_enqueue_unique(&c->work_q, &it, bytes, (u32)sizeof(pl));
            }
            da->slotmap.dirty = D_FALSE;
        }
    }

    for (i = 0u; i < c->dirty.junction_count; ++i) {
        dg_trans_dirty_junction *dj = &c->dirty.junctions[i];
        if (dj->dirty) {
            dg_work_item it;
            dg_trans_work_junction_payload pl;
            unsigned char bytes[DG_WORK_ITEM_INLINE_CAP];
            dg_work_item_clear(&it);
            dg_trans_make_key_for_junction(&it.key, DG_TRANS_WORK_JUNCTION, (dg_entity_id)dj->junction_id);
            it.work_type_id = DG_TRANS_WORK_JUNCTION;
            it.cost_units = 1u;
            it.enqueue_tick = tick;
            pl.junction_id = dj->junction_id;
            memcpy(bytes, &pl, sizeof(pl));
            (void)dg_work_item_set_payload_inline(&it, bytes, (u32)sizeof(pl));
            (void)dg_trans_enqueue_unique(&c->work_q, &it, bytes, (u32)sizeof(pl));
            dj->dirty = D_FALSE;
        }
    }

    return 0;
}

u32 dg_trans_compiler_process(dg_trans_compiler *c, const dg_trans_compile_input *in, dg_tick tick, u32 budget_units) {
    u32 processed = 0u;
    (void)tick;

    if (!c || !in) return 0u;
    if (budget_units == 0u) return 0u;

    while (1) {
        const dg_work_item *next = dg_work_queue_peek_next(&c->work_q);
        dg_work_item it;
        u32 cost;
        int rc;

        if (!next) break;
        cost = next->cost_units;
        if (cost == 0u) cost = 1u;

        if (budget_units != (u32)0xFFFFFFFFu && cost > budget_units) {
            /* Deterministic: stop if the next item does not fit. */
            break;
        }

        if (!dg_work_queue_pop_next(&c->work_q, &it)) break;

        rc = 0;
        if (it.work_type_id == DG_TRANS_WORK_MICROSEG_RANGE || it.work_type_id == DG_TRANS_WORK_SLOTMAP_RANGE) {
            dg_trans_work_range_payload pl;
            if (it.payload_inline_len != sizeof(pl)) {
                rc = -1;
            } else {
                memcpy(&pl, it.payload_inline, sizeof(pl));
                if (it.work_type_id == DG_TRANS_WORK_MICROSEG_RANGE) {
                    rc = dg_trans_compile_microseg_range(c, in, (dg_trans_alignment_id)pl.alignment_id, pl.seg0, pl.seg1);
                } else {
                    rc = dg_trans_compile_slotmap_range(c, in, (dg_trans_alignment_id)pl.alignment_id, pl.seg0, pl.seg1);
                }
            }
        } else if (it.work_type_id == DG_TRANS_WORK_JUNCTION) {
            dg_trans_work_junction_payload plj;
            if (it.payload_inline_len != sizeof(plj)) {
                rc = -1;
            } else {
                memcpy(&plj, it.payload_inline, sizeof(plj));
                rc = dg_trans_compile_junction(c, in, (dg_trans_junction_id)plj.junction_id);
            }
        }

        (void)rc; /* For now compilation failures do not abort the queue. */

        if (budget_units != (u32)0xFFFFFFFFu) {
            budget_units -= cost;
            if (budget_units == 0u) {
                processed += 1u;
                break;
            }
        }

        processed += 1u;
    }

    return processed;
}

u32 dg_trans_compiler_pending_work(const dg_trans_compiler *c) {
    if (!c) return 0u;
    return dg_work_queue_count(&c->work_q);
}

static int dg_trans_vec3_eq(dg_vec3_q a, dg_vec3_q b) {
    return (a.x == b.x) && (a.y == b.y) && (a.z == b.z);
}

static int dg_trans_frame_eq(const dg_trans_frame *a, const dg_trans_frame *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    if (!dg_trans_vec3_eq(a->origin, b->origin)) return 0;
    if (!dg_trans_vec3_eq(a->forward, b->forward)) return 0;
    if (!dg_trans_vec3_eq(a->right, b->right)) return 0;
    if (!dg_trans_vec3_eq(a->up, b->up)) return 0;
    return 1;
}

static int dg_trans_aabb_eq(const dg_trans_aabb *a, const dg_trans_aabb *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    if (!dg_trans_vec3_eq(a->min, b->min)) return 0;
    if (!dg_trans_vec3_eq(a->max, b->max)) return 0;
    return 1;
}

static int dg_trans_slotmap_eq(const dg_trans_segment_slotmap *a, const dg_trans_segment_slotmap *b) {
    u32 i;
    if (a == b) return 1;
    if (!a || !b) return 0;
    if (a->count != b->count) return 0;
    for (i = 0u; i < a->count; ++i) {
        const dg_trans_slot_occupancy *oa = &a->items[i];
        const dg_trans_slot_occupancy *ob = &b->items[i];
        if (oa->slot_id != ob->slot_id) return 0;
        if (oa->occupant_type_id != ob->occupant_type_id) return 0;
        if (oa->occupant_instance_id != ob->occupant_instance_id) return 0;
        if (oa->offset_t != ob->offset_t) return 0;
        if (oa->offset_h != ob->offset_h) return 0;
    }
    return 1;
}

static int dg_trans_chunk_coord_cmp_local(const dg_trans_chunk_coord *a, const dg_trans_chunk_coord *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP3_I32(a->cx, a->cy, a->cz, b->cx, b->cy, b->cz);
}

static int dg_trans_spatial_entry_cmp_local(const dg_trans_spatial_entry *a, const dg_trans_spatial_entry *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = dg_trans_chunk_coord_cmp_local(&a->chunk, &b->chunk);
    if (c) return c;
    return dg_trans_segment_id_cmp(&a->seg_id, &b->seg_id);
}

int dg_trans_compiler_check_invariants(const dg_trans_compiler *c, const dg_trans_compile_input *in) {
    u32 i;

    if (!c || !in) return -1;
    if (c->microseg_max_len_q <= 0) return -2;
    if (c->chunk_size_q <= 0) return -3;

    /* Compiled alignment table must be strictly sorted by alignment_id. */
    for (i = 1u; i < c->compiled.alignment_count; ++i) {
        if (c->compiled.alignments[i - 1u].alignment_id >= c->compiled.alignments[i].alignment_id) {
            return -10;
        }
    }

    /* Validate each compiled alignment against a deterministic rebuild from authoring. */
    for (i = 0u; i < c->compiled.alignment_count; ++i) {
        const dg_trans_compiled_alignment *ca = &c->compiled.alignments[i];
        const dg_trans_alignment *a;
        const dg_trans_section_archetype *section;
        dg_q length_q;
        u32 expected_count;
        u32 si;
        dg_trans_segment_slotmap *tmp_slotmaps = (dg_trans_segment_slotmap *)0;
        int rc;

        if (ca->alignment_id == 0u) return -11;

        a = dg_trans_find_alignment(in, ca->alignment_id);
        if (!a) return -12;
        if (dg_trans_alignment_length_q(a, &length_q) != 0) return -13;
        expected_count = dg_trans_microseg_expected_count(length_q, c->microseg_max_len_q);

        if (ca->seg_count != expected_count) return -14;
        if (expected_count > 0u && (!ca->segs || !ca->slotmaps)) return -15;

        for (si = 0u; si < expected_count; ++si) {
            const dg_trans_microseg *seg = &ca->segs[si];
            dg_q s_begin;
            dg_q s_end;
            dg_vec3_q p0;
            dg_vec3_q p1;
            dg_vec3_q tan;
            dg_q roll;
            dg_trans_aabb bbox;
            dg_trans_frame f;
            dg_trans_frame expected_f;

            if (seg->id.alignment_id != ca->alignment_id) return -20;
            if (seg->id.segment_index != si) return -21;

            s_begin = dg_trans_mul_q_u32(c->microseg_max_len_q, si);
            s_end = (dg_q)d_q48_16_add((q48_16)s_begin, (q48_16)c->microseg_max_len_q);
            if (s_end > length_q) s_end = length_q;

            if (seg->s_begin != s_begin) return -22;
            if (seg->s_end != s_end) return -23;

            if (dg_trans_alignment_eval_pos(a, s_begin, &p0) != 0) return -24;
            if (dg_trans_alignment_eval_pos(a, s_end, &p1) != 0) return -25;

            bbox.min.x = (p0.x < p1.x) ? p0.x : p1.x;
            bbox.min.y = (p0.y < p1.y) ? p0.y : p1.y;
            bbox.min.z = (p0.z < p1.z) ? p0.z : p1.z;
            bbox.max.x = (p0.x > p1.x) ? p0.x : p1.x;
            bbox.max.y = (p0.y > p1.y) ? p0.y : p1.y;
            bbox.max.z = (p0.z > p1.z) ? p0.z : p1.z;

            if (!dg_trans_aabb_eq(&seg->bbox, &bbox)) return -26;

            if (dg_trans_alignment_eval_tangent(a, s_begin, &tan) != 0) {
                (void)dg_trans_alignment_eval_tangent(a, s_end, &tan);
            }
            (void)dg_trans_alignment_eval_roll(a, s_begin, &roll);

            if (dg_trans_frame_build(p0, tan, roll, &f) != 0) {
                dg_vec3_q fw;
                fw.x = (dg_q)((i64)1 << 16);
                fw.y = 0;
                fw.z = 0;
                (void)dg_trans_frame_build(p0, fw, roll, &f);
            }

            expected_f = f;
            if (!dg_trans_frame_eq(&seg->frame0, &expected_f)) return -27;
        }

        section = dg_trans_find_section(in, a->section_id);
        if (!section) {
            for (si = 0u; si < expected_count; ++si) {
                if (ca->slotmaps[si].count != 0u) return -30;
            }
            continue;
        }

        /* Rebuild expected slotmaps and compare byte-stable content. */
        tmp_slotmaps = (dg_trans_segment_slotmap *)malloc(sizeof(dg_trans_segment_slotmap) * (size_t)expected_count);
        if (!tmp_slotmaps && expected_count != 0u) return -31;

        for (si = 0u; si < expected_count; ++si) {
            dg_trans_segment_slotmap_init(&tmp_slotmaps[si]);
        }

        rc = 0;
        if (expected_count != 0u) {
            rc = dg_trans_slotmap_rebuild_range(
                tmp_slotmaps,
                expected_count,
                ca->segs,
                expected_count,
                ca->alignment_id,
                section,
                in->attachments,
                in->attachment_count,
                0u,
                expected_count - 1u
            );
        }
        if (rc != 0) {
            for (si = 0u; si < expected_count; ++si) {
                dg_trans_segment_slotmap_free(&tmp_slotmaps[si]);
            }
            if (tmp_slotmaps) free(tmp_slotmaps);
            return -32;
        }

        for (si = 0u; si < expected_count; ++si) {
            if (!dg_trans_slotmap_eq(&ca->slotmaps[si], &tmp_slotmaps[si])) {
                rc = -33;
                break;
            }
        }

        for (si = 0u; si < expected_count; ++si) {
            dg_trans_segment_slotmap_free(&tmp_slotmaps[si]);
        }
        if (tmp_slotmaps) free(tmp_slotmaps);
        if (rc != 0) return rc;
    }

    /* Compiled junction table must be strictly sorted by junction_id. */
    for (i = 1u; i < c->compiled.junction_count; ++i) {
        if (c->compiled.junctions[i - 1u].junction_id >= c->compiled.junctions[i].junction_id) {
            return -40;
        }
    }

    for (i = 0u; i < c->compiled.junction_count; ++i) {
        const dg_trans_compiled_junction *cj = &c->compiled.junctions[i];
        const dg_trans_junction *j;
        u32 ji;
        if (cj->junction_id == 0u) return -41;
        j = dg_trans_find_junction(in, cj->junction_id);
        if (!j) return -42;
        if (cj->incident_count != j->incident_count) return -43;
        for (ji = 0u; ji < cj->incident_count; ++ji) {
            const dg_trans_junction_incident *a = &cj->incidents[ji];
            const dg_trans_junction_incident *b = &j->incidents[ji];
            if (a->alignment_id != b->alignment_id) return -44;
            if (a->port_index != b->port_index) return -45;
            if (a->station_s != b->station_s) return -46;
            if (a->level != b->level) return -47;
            if (a->min_radius != b->min_radius) return -48;
            if (a->max_grade != b->max_grade) return -49;
            if (a->clearance != b->clearance) return -50;
        }
    }

    /* Spatial index entries must be in canonical sorted order. */
    for (i = 1u; i < c->compiled.spatial.count; ++i) {
        const dg_trans_spatial_entry *a = &c->compiled.spatial.entries[i - 1u];
        const dg_trans_spatial_entry *b = &c->compiled.spatial.entries[i];
        if (dg_trans_spatial_entry_cmp_local(a, b) >= 0) return -60;
    }

    return 0;
}
