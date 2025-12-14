/* TRANS microsegment model + chunk-aligned spatial index (C89). */
#include "trans/compile/dg_trans_microseg.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

static i64 dg_trans_floor_div_i64(i64 a, i64 d) {
    i64 q;
    i64 r;
    if (d == 0) return 0;
    q = a / d; /* trunc toward zero (det invariant) */
    r = a % d;
    if (r != 0 && a < 0) {
        /* d is expected positive for our usage; adjust to floor. */
        q -= 1;
    }
    return q;
}

static i32 dg_trans_clamp_i64_i32(i64 v) {
    if (v > (i64)2147483647L) return (i32)2147483647L;
    if (v < (i64)(-2147483647L - 1L)) return (i32)(-2147483647L - 1L);
    return (i32)v;
}

static dg_trans_chunk_coord dg_trans_chunk_of_pos(dg_vec3_q p, dg_q chunk_size_q) {
    dg_trans_chunk_coord c;
    i64 d = (i64)chunk_size_q;
    if (d <= 0) {
        c.cx = 0; c.cy = 0; c.cz = 0;
        return c;
    }
    c.cx = dg_trans_clamp_i64_i32(dg_trans_floor_div_i64((i64)p.x, d));
    c.cy = dg_trans_clamp_i64_i32(dg_trans_floor_div_i64((i64)p.y, d));
    c.cz = dg_trans_clamp_i64_i32(dg_trans_floor_div_i64((i64)p.z, d));
    return c;
}

static void dg_trans_chunk_range_for_aabb(
    const dg_trans_aabb *b,
    dg_q                 chunk_size_q,
    dg_trans_chunk_coord *out_min,
    dg_trans_chunk_coord *out_max
) {
    dg_trans_chunk_coord c0;
    dg_trans_chunk_coord c1;
    dg_vec3_q p0;
    dg_vec3_q p1;
    if (!out_min || !out_max) return;
    out_min->cx = 0; out_min->cy = 0; out_min->cz = 0;
    out_max->cx = 0; out_max->cy = 0; out_max->cz = 0;
    if (!b) return;
    p0 = b->min;
    p1 = b->max;
    c0 = dg_trans_chunk_of_pos(p0, chunk_size_q);
    c1 = dg_trans_chunk_of_pos(p1, chunk_size_q);
    /* Ensure proper ordering. */
    out_min->cx = (c0.cx < c1.cx) ? c0.cx : c1.cx;
    out_min->cy = (c0.cy < c1.cy) ? c0.cy : c1.cy;
    out_min->cz = (c0.cz < c1.cz) ? c0.cz : c1.cz;
    out_max->cx = (c0.cx > c1.cx) ? c0.cx : c1.cx;
    out_max->cy = (c0.cy > c1.cy) ? c0.cy : c1.cy;
    out_max->cz = (c0.cz > c1.cz) ? c0.cz : c1.cz;
}

static int dg_trans_chunk_cmp(const dg_trans_chunk_coord *a, const dg_trans_chunk_coord *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP3_I32(a->cx, a->cy, a->cz, b->cx, b->cy, b->cz);
}

static int dg_trans_entry_cmp_key(const dg_trans_chunk_coord *chunk, const dg_trans_segment_id *seg_id, const dg_trans_spatial_entry *e) {
    int c;
    if (!e) return 1;
    c = dg_trans_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    return dg_trans_segment_id_cmp(seg_id, &e->seg_id);
}

static u32 dg_trans_lower_bound(const dg_trans_spatial_index *idx, const dg_trans_chunk_coord *chunk, const dg_trans_segment_id *seg_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk || !seg_id) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_trans_entry_cmp_key(chunk, seg_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 dg_trans_lower_bound_chunk(const dg_trans_spatial_index *idx, const dg_trans_chunk_coord *chunk) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_trans_chunk_cmp(&idx->entries[mid].chunk, chunk) >= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

void dg_trans_spatial_index_init(dg_trans_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_trans_spatial_index_free(dg_trans_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) {
        free(idx->entries);
    }
    dg_trans_spatial_index_init(idx);
}

int dg_trans_spatial_index_reserve(dg_trans_spatial_index *idx, u32 capacity) {
    dg_trans_spatial_entry *e;
    if (!idx) return -1;
    dg_trans_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_trans_spatial_entry *)malloc(sizeof(dg_trans_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_trans_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_trans_spatial_index_clear(dg_trans_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_trans_spatial_index_count(const dg_trans_spatial_index *idx) {
    return idx ? idx->count : 0u;
}

u32 dg_trans_spatial_index_capacity(const dg_trans_spatial_index *idx) {
    return idx ? idx->capacity : 0u;
}

u32 dg_trans_spatial_index_probe_refused(const dg_trans_spatial_index *idx) {
    return idx ? idx->probe_refused : 0u;
}

u32 dg_trans_spatial_index_remove_segment(dg_trans_spatial_index *idx, const dg_trans_segment_id *seg_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || !seg_id) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (dg_trans_segment_id_cmp(&idx->entries[i].seg_id, seg_id) == 0) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_trans_spatial_entry) * (size_t)(idx->count - (i + 1u)));
            }
            idx->count -= 1u;
            removed += 1u;
            continue;
        }
        i += 1u;
    }
    return removed;
}

static int dg_trans_spatial_index_add_entry(
    dg_trans_spatial_index       *idx,
    const dg_trans_chunk_coord   *chunk,
    const dg_trans_segment_id    *seg_id,
    const dg_trans_aabb          *bbox
) {
    u32 pos;
    dg_trans_spatial_entry *e;

    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk || !seg_id || !bbox) return -2;

    pos = dg_trans_lower_bound(idx, chunk, seg_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_trans_entry_cmp_key(chunk, seg_id, e) == 0) {
            /* Update in place. */
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
                sizeof(dg_trans_spatial_entry) * (size_t)(idx->count - pos));
    }

    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->seg_id = *seg_id;
    e->bbox = *bbox;
    idx->count += 1u;
    return 0;
}

int dg_trans_spatial_index_add_segment(dg_trans_spatial_index *idx, const dg_trans_microseg *seg, dg_q chunk_size_q) {
    dg_trans_chunk_coord cmin;
    dg_trans_chunk_coord cmax;
    i32 cx, cy, cz;
    int partial = 0;

    if (!idx || !seg) return -1;
    if (chunk_size_q <= 0) return -2;
    if (!idx->entries || idx->capacity == 0u) return -3;

    dg_trans_chunk_range_for_aabb(&seg->bbox, chunk_size_q, &cmin, &cmax);

    for (cz = cmin.cz; cz <= cmax.cz; ++cz) {
        for (cy = cmin.cy; cy <= cmax.cy; ++cy) {
            for (cx = cmin.cx; cx <= cmax.cx; ++cx) {
                dg_trans_chunk_coord c;
                int rc;
                c.cx = cx; c.cy = cy; c.cz = cz;
                rc = dg_trans_spatial_index_add_entry(idx, &c, &seg->id, &seg->bbox);
                if (rc < 0) {
                    partial = 1;
                    /* Deterministic: stop further inserts if capacity refused. */
                    if (rc == -3) return 1;
                    return rc;
                }
            }
        }
    }

    return partial ? 1 : 0;
}

static int dg_trans_seg_id_exists(const dg_trans_segment_id *arr, u32 count, const dg_trans_segment_id *id) {
    u32 i;
    if (!arr || !id) return 0;
    for (i = 0u; i < count; ++i) {
        if (dg_trans_segment_id_cmp(&arr[i], id) == 0) return 1;
    }
    return 0;
}

u32 dg_trans_spatial_query_pos(
    const dg_trans_spatial_index *idx,
    dg_vec3_q                     pos,
    dg_q                          chunk_size_q,
    dg_trans_segment_id          *out_seg_ids,
    u32                           max_out
) {
    dg_trans_chunk_coord chunk;
    u32 start;
    u32 i;
    u32 written = 0u;

    if (!idx || !idx->entries || !out_seg_ids || max_out == 0u) return 0u;
    if (chunk_size_q <= 0) return 0u;

    chunk = dg_trans_chunk_of_pos(pos, chunk_size_q);
    start = dg_trans_lower_bound_chunk(idx, &chunk);
    for (i = start; i < idx->count; ++i) {
        const dg_trans_spatial_entry *e = &idx->entries[i];
        if (dg_trans_chunk_cmp(&e->chunk, &chunk) != 0) break;
        out_seg_ids[written++] = e->seg_id;
        if (written >= max_out) break;
    }
    return written;
}

u32 dg_trans_spatial_query_aabb(
    const dg_trans_spatial_index *idx,
    const dg_trans_aabb          *query,
    dg_q                          chunk_size_q,
    dg_trans_segment_id          *out_seg_ids,
    u32                           max_out
) {
    dg_trans_chunk_coord cmin;
    dg_trans_chunk_coord cmax;
    i32 cx, cy, cz;
    u32 written = 0u;

    if (!idx || !idx->entries || !query || !out_seg_ids || max_out == 0u) return 0u;
    if (chunk_size_q <= 0) return 0u;

    dg_trans_chunk_range_for_aabb(query, chunk_size_q, &cmin, &cmax);

    for (cz = cmin.cz; cz <= cmax.cz; ++cz) {
        for (cy = cmin.cy; cy <= cmax.cy; ++cy) {
            for (cx = cmin.cx; cx <= cmax.cx; ++cx) {
                dg_trans_chunk_coord chunk;
                u32 start;
                u32 i;
                chunk.cx = cx; chunk.cy = cy; chunk.cz = cz;
                start = dg_trans_lower_bound_chunk(idx, &chunk);
                for (i = start; i < idx->count; ++i) {
                    const dg_trans_spatial_entry *e = &idx->entries[i];
                    if (dg_trans_chunk_cmp(&e->chunk, &chunk) != 0) break;
                    if (!dg_trans_seg_id_exists(out_seg_ids, written, &e->seg_id)) {
                        out_seg_ids[written++] = e->seg_id;
                        if (written >= max_out) return written;
                    }
                }
            }
        }
    }
    return written;
}

