/* STRUCT carrier compilation (C89). */
#include "struct/compile/dg_struct_carrier_compile.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "domino/core/fixed.h"

/* ------------------------ compiled storage ------------------------ */

void dg_struct_carrier_compiled_init(dg_struct_carrier_compiled *c) {
    if (!c) return;
    memset(c, 0, sizeof(*c));
}

void dg_struct_carrier_compiled_free(dg_struct_carrier_compiled *c) {
    if (!c) return;
    if (c->items) free(c->items);
    dg_struct_carrier_compiled_init(c);
}

void dg_struct_carrier_compiled_clear(dg_struct_carrier_compiled *c) {
    if (!c) return;
    c->count = 0u;
}

int dg_struct_carrier_compiled_reserve(dg_struct_carrier_compiled *c, u32 capacity) {
    dg_struct_carrier_artifact *arr;
    u32 new_cap;
    if (!c) return -1;
    if (capacity <= c->capacity) return 0;
    new_cap = c->capacity ? c->capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) { new_cap = capacity; break; }
        new_cap *= 2u;
    }
    arr = (dg_struct_carrier_artifact *)realloc(c->items, sizeof(dg_struct_carrier_artifact) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > c->capacity) {
        memset(&arr[c->capacity], 0, sizeof(dg_struct_carrier_artifact) * (size_t)(new_cap - c->capacity));
    }
    c->items = arr;
    c->capacity = new_cap;
    return 0;
}

static void dg_struct_sort_carriers_by_id(dg_struct_carrier_artifact *arr, u32 count) {
    u32 i;
    if (!arr || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_struct_carrier_artifact key = arr[i];
        u32 j = i;
        while (j > 0u && arr[j - 1u].id > key.id) {
            arr[j] = arr[j - 1u];
            j -= 1u;
        }
        arr[j] = key;
    }
}

/* ------------------------ spatial index ------------------------ */

static i64 dg_struct_floor_div_i64(i64 a, i64 d) {
    i64 q;
    i64 r;
    if (d == 0) return 0;
    q = a / d;
    r = a % d;
    if (r != 0 && a < 0) q -= 1;
    return q;
}

static i32 dg_struct_clamp_i64_i32(i64 v) {
    if (v > (i64)2147483647L) return (i32)2147483647L;
    if (v < (i64)(-2147483647L - 1L)) return (i32)(-2147483647L - 1L);
    return (i32)v;
}

static dg_struct_chunk_coord dg_struct_chunk_of_pos(dg_vec3_q p, dg_q chunk_size_q) {
    dg_struct_chunk_coord c;
    i64 d = (i64)chunk_size_q;
    if (d <= 0) { c.cx = 0; c.cy = 0; c.cz = 0; return c; }
    c.cx = dg_struct_clamp_i64_i32(dg_struct_floor_div_i64((i64)p.x, d));
    c.cy = dg_struct_clamp_i64_i32(dg_struct_floor_div_i64((i64)p.y, d));
    c.cz = dg_struct_clamp_i64_i32(dg_struct_floor_div_i64((i64)p.z, d));
    return c;
}

static void dg_struct_chunk_range_for_aabb(
    const dg_struct_aabb  *b,
    dg_q                  chunk_size_q,
    dg_struct_chunk_coord *out_min,
    dg_struct_chunk_coord *out_max
) {
    dg_struct_chunk_coord c0;
    dg_struct_chunk_coord c1;
    dg_vec3_q p0;
    dg_vec3_q p1;
    if (!out_min || !out_max) return;
    out_min->cx = 0; out_min->cy = 0; out_min->cz = 0;
    out_max->cx = 0; out_max->cy = 0; out_max->cz = 0;
    if (!b) return;
    p0 = b->min;
    p1 = b->max;
    c0 = dg_struct_chunk_of_pos(p0, chunk_size_q);
    c1 = dg_struct_chunk_of_pos(p1, chunk_size_q);
    out_min->cx = (c0.cx < c1.cx) ? c0.cx : c1.cx;
    out_min->cy = (c0.cy < c1.cy) ? c0.cy : c1.cy;
    out_min->cz = (c0.cz < c1.cz) ? c0.cz : c1.cz;
    out_max->cx = (c0.cx > c1.cx) ? c0.cx : c1.cx;
    out_max->cy = (c0.cy > c1.cy) ? c0.cy : c1.cy;
    out_max->cz = (c0.cz > c1.cz) ? c0.cz : c1.cz;
}

static int dg_struct_chunk_cmp(const dg_struct_chunk_coord *a, const dg_struct_chunk_coord *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP3_I32(a->cx, a->cy, a->cz, b->cx, b->cy, b->cz);
}

static int dg_struct_carrier_entry_cmp_key(
    const dg_struct_chunk_coord          *chunk,
    dg_struct_id                          struct_id,
    dg_struct_carrier_artifact_id         artifact_id,
    const dg_struct_carrier_spatial_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_struct_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    c = D_DET_CMP_U64(struct_id, e->struct_id);
    if (c) return c;
    return D_DET_CMP_U64(artifact_id, e->artifact_id);
}

static u32 dg_struct_carrier_lower_bound_entry(
    const dg_struct_carrier_spatial_index *idx,
    const dg_struct_chunk_coord           *chunk,
    dg_struct_id                           struct_id,
    dg_struct_carrier_artifact_id          artifact_id
) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_carrier_entry_cmp_key(chunk, struct_id, artifact_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_carrier_spatial_add_entry(
    dg_struct_carrier_spatial_index *idx,
    const dg_struct_chunk_coord     *chunk,
    dg_struct_id                     struct_id,
    dg_struct_carrier_artifact_id    artifact_id,
    const dg_struct_aabb            *bbox
) {
    u32 pos;
    dg_struct_carrier_spatial_entry *e;
    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk || !bbox) return -2;

    pos = dg_struct_carrier_lower_bound_entry(idx, chunk, struct_id, artifact_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_struct_carrier_entry_cmp_key(chunk, struct_id, artifact_id, e) == 0) {
            e->bbox = *bbox;
            return 1;
        }
    }

    if (idx->count >= idx->capacity) {
        idx->probe_refused += 1u;
        return -3;
    }

    if (pos < idx->count) {
        memmove(&idx->entries[pos + 1u], &idx->entries[pos],
                sizeof(dg_struct_carrier_spatial_entry) * (size_t)(idx->count - pos));
    }
    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->struct_id = struct_id;
    e->artifact_id = artifact_id;
    e->bbox = *bbox;
    idx->count += 1u;
    return 0;
}

static int dg_struct_carrier_spatial_index_add_artifact(dg_struct_carrier_spatial_index *idx, const dg_struct_carrier_artifact *a, dg_q chunk_size_q) {
    dg_struct_chunk_coord cmin;
    dg_struct_chunk_coord cmax;
    i32 cx, cy, cz;
    int partial = 0;
    if (!idx || !a) return -1;
    if (chunk_size_q <= 0) return -2;
    if (!idx->entries || idx->capacity == 0u) return -3;
    dg_struct_chunk_range_for_aabb(&a->bbox_world, chunk_size_q, &cmin, &cmax);
    for (cz = cmin.cz; cz <= cmax.cz; ++cz) {
        for (cy = cmin.cy; cy <= cmax.cy; ++cy) {
            for (cx = cmin.cx; cx <= cmax.cx; ++cx) {
                dg_struct_chunk_coord c;
                int rc;
                c.cx = cx; c.cy = cy; c.cz = cz;
                rc = dg_struct_carrier_spatial_add_entry(idx, &c, a->struct_id, a->id, &a->bbox_world);
                if (rc < 0) {
                    partial = 1;
                    if (rc == -3) return 1;
                    return rc;
                }
            }
        }
    }
    return partial ? 1 : 0;
}

void dg_struct_carrier_spatial_index_init(dg_struct_carrier_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_struct_carrier_spatial_index_free(dg_struct_carrier_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) free(idx->entries);
    dg_struct_carrier_spatial_index_init(idx);
}

int dg_struct_carrier_spatial_index_reserve(dg_struct_carrier_spatial_index *idx, u32 capacity) {
    dg_struct_carrier_spatial_entry *e;
    if (!idx) return -1;
    dg_struct_carrier_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_struct_carrier_spatial_entry *)malloc(sizeof(dg_struct_carrier_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_struct_carrier_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_struct_carrier_spatial_index_clear(dg_struct_carrier_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_struct_carrier_spatial_index_remove_struct(dg_struct_carrier_spatial_index *idx, dg_struct_id struct_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || struct_id == 0u) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (idx->entries[i].struct_id == struct_id) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_struct_carrier_spatial_entry) * (size_t)(idx->count - (i + 1u)));
            }
            idx->count -= 1u;
            removed += 1u;
            continue;
        }
        i += 1u;
    }
    return removed;
}

/* ------------------------ rebuild ------------------------ */

static const dg_struct_carrier_intent *dg_struct_find_intent(
    const dg_struct_carrier_intent *cs, u32 count, dg_struct_carrier_intent_id id
) {
    u32 i;
    if (!cs || id == 0u) return (const dg_struct_carrier_intent *)0;
    for (i = 0u; i < count; ++i) {
        if (cs[i].id == id) return &cs[i];
    }
    return (const dg_struct_carrier_intent *)0;
}

static u64 dg_struct_hash_step(u64 h, u64 v) { return dg_det_hash_u64(h ^ v); }

static dg_struct_carrier_artifact_id dg_struct_carrier_artifact_id_make(dg_struct_id struct_id, dg_struct_carrier_intent_id intent_id) {
    u64 h = 0xBB67AE8584CAA73BULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)intent_id);
    return (dg_struct_carrier_artifact_id)h;
}

static dg_q dg_struct_q_max(dg_q a, dg_q b) { return (a > b) ? a : b; }

static dg_struct_aabb dg_struct_aabb_span_with_extents(dg_vec3_q p0, dg_vec3_q p1, dg_q ex, dg_q ey, dg_q ez) {
    dg_struct_aabb b;
    dg_vec3_q lo;
    dg_vec3_q hi;
    lo.x = (p0.x < p1.x) ? p0.x : p1.x;
    lo.y = (p0.y < p1.y) ? p0.y : p1.y;
    lo.z = (p0.z < p1.z) ? p0.z : p1.z;
    hi.x = (p0.x > p1.x) ? p0.x : p1.x;
    hi.y = (p0.y > p1.y) ? p0.y : p1.y;
    hi.z = (p0.z > p1.z) ? p0.z : p1.z;

    b.min.x = (dg_q)d_q48_16_sub((q48_16)lo.x, (q48_16)ex);
    b.min.y = (dg_q)d_q48_16_sub((q48_16)lo.y, (q48_16)ey);
    b.min.z = (dg_q)d_q48_16_sub((q48_16)lo.z, (q48_16)ez);
    b.max.x = (dg_q)d_q48_16_add((q48_16)hi.x, (q48_16)ex);
    b.max.y = (dg_q)d_q48_16_add((q48_16)hi.y, (q48_16)ey);
    b.max.z = (dg_q)d_q48_16_add((q48_16)hi.z, (q48_16)ez);
    return b;
}

int dg_struct_carrier_compile_rebuild(
    dg_struct_carrier_compiled      *out,
    dg_struct_carrier_spatial_index *spatial,
    const dg_struct_instance        *inst,
    dg_struct_id                     struct_id,
    const dg_struct_carrier_intent  *intents,
    u32                              intent_count,
    const d_world_frame             *frames,
    dg_tick                          tick,
    dg_q                             chunk_size_q
) {
    u32 i;
    int partial = 0;

    if (!out || !inst) return -1;
    if (struct_id == 0u) return -2;
    if (chunk_size_q <= 0) return -3;

    if (dg_struct_carrier_compiled_reserve(out, inst->carrier_intent_count) != 0) return -4;
    dg_struct_carrier_compiled_clear(out);

    if (spatial) {
        (void)dg_struct_carrier_spatial_index_remove_struct(spatial, struct_id);
    }

    for (i = 0u; i < inst->carrier_intent_count; ++i) {
        dg_struct_carrier_intent_id cid = inst->carrier_intent_ids[i];
        const dg_struct_carrier_intent *ci = dg_struct_find_intent(intents, intent_count, cid);
        dg_struct_carrier_artifact a;
        dg_pose p0;
        dg_pose p1;
        dg_q half_w;
        dg_q ez;
        int rc;

        if (!ci) return -5;

        rc = dg_anchor_eval(&ci->a0, frames, tick, DG_ROUND_NEAR, &p0);
        if (rc != 0) return -6;
        rc = dg_anchor_eval(&ci->a1, frames, tick, DG_ROUND_NEAR, &p1);
        if (rc != 0) return -7;

        half_w = (dg_q)(ci->width / 2);
        ez = dg_struct_q_max(ci->height, ci->depth);

        memset(&a, 0, sizeof(a));
        a.struct_id = struct_id;
        a.intent_id = ci->id;
        a.kind = ci->kind;
        a.id = dg_struct_carrier_artifact_id_make(struct_id, ci->id);
        a.a0_world = p0;
        a.a1_world = p1;
        a.width = ci->width;
        a.height = ci->height;
        a.depth = ci->depth;
        a.bbox_world = dg_struct_aabb_span_with_extents(p0.pos, p1.pos, half_w, half_w, ez);

        out->items[out->count++] = a;
    }

    dg_struct_sort_carriers_by_id(out->items, out->count);

    if (spatial) {
        for (i = 0u; i < out->count; ++i) {
            int rc = dg_struct_carrier_spatial_index_add_artifact(spatial, &out->items[i], chunk_size_q);
            if (rc < 0) return rc;
            if (rc > 0) partial = 1;
        }
    }

    return partial ? 1 : 0;
}

