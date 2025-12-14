/* STRUCT occupancy compilation and chunk-aligned spatial index (C89). */
#include "struct/compile/dg_struct_occupancy.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "domino/core/fixed.h"

/* ------------------------ region list helpers ------------------------ */

void dg_struct_occupancy_init(dg_struct_occupancy *o) {
    if (!o) return;
    memset(o, 0, sizeof(*o));
}

void dg_struct_occupancy_free(dg_struct_occupancy *o) {
    if (!o) return;
    if (o->regions) free(o->regions);
    dg_struct_occupancy_init(o);
}

void dg_struct_occupancy_clear(dg_struct_occupancy *o) {
    if (!o) return;
    o->region_count = 0u;
}

int dg_struct_occupancy_reserve(dg_struct_occupancy *o, u32 region_capacity) {
    dg_struct_occ_region *arr;
    u32 new_cap;
    if (!o) return -1;
    if (region_capacity <= o->region_capacity) return 0;
    new_cap = o->region_capacity ? o->region_capacity : 8u;
    while (new_cap < region_capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = region_capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_occ_region *)realloc(o->regions, sizeof(dg_struct_occ_region) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > o->region_capacity) {
        memset(&arr[o->region_capacity], 0, sizeof(dg_struct_occ_region) * (size_t)(new_cap - o->region_capacity));
    }
    o->regions = arr;
    o->region_capacity = new_cap;
    return 0;
}

/* ------------------------ spatial index helpers ------------------------ */

static i64 dg_struct_floor_div_i64(i64 a, i64 d) {
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

static i32 dg_struct_clamp_i64_i32(i64 v) {
    if (v > (i64)2147483647L) return (i32)2147483647L;
    if (v < (i64)(-2147483647L - 1L)) return (i32)(-2147483647L - 1L);
    return (i32)v;
}

static dg_struct_chunk_coord dg_struct_chunk_of_pos(dg_vec3_q p, dg_q chunk_size_q) {
    dg_struct_chunk_coord c;
    i64 d = (i64)chunk_size_q;
    if (d <= 0) {
        c.cx = 0; c.cy = 0; c.cz = 0;
        return c;
    }
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

static int dg_struct_occ_entry_cmp_key(
    const dg_struct_chunk_coord   *chunk,
    dg_struct_id                   struct_id,
    dg_struct_occ_region_id        region_id,
    const dg_struct_occ_spatial_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_struct_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    c = D_DET_CMP_U64(struct_id, e->struct_id);
    if (c) return c;
    return D_DET_CMP_U64(region_id, e->region_id);
}

static u32 dg_struct_occ_lower_bound(
    const dg_struct_occ_spatial_index *idx,
    const dg_struct_chunk_coord       *chunk,
    dg_struct_id                       struct_id,
    dg_struct_occ_region_id            region_id
) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_occ_entry_cmp_key(chunk, struct_id, region_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_occ_spatial_index_add_entry(
    dg_struct_occ_spatial_index *idx,
    const dg_struct_chunk_coord *chunk,
    dg_struct_id                 struct_id,
    dg_struct_occ_region_id      region_id,
    const dg_struct_aabb        *bbox
) {
    u32 pos;
    dg_struct_occ_spatial_entry *e;
    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk || !bbox) return -2;

    pos = dg_struct_occ_lower_bound(idx, chunk, struct_id, region_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_struct_occ_entry_cmp_key(chunk, struct_id, region_id, e) == 0) {
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
                sizeof(dg_struct_occ_spatial_entry) * (size_t)(idx->count - pos));
    }
    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->struct_id = struct_id;
    e->region_id = region_id;
    e->bbox = *bbox;
    idx->count += 1u;
    return 0;
}

void dg_struct_occ_spatial_index_init(dg_struct_occ_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_struct_occ_spatial_index_free(dg_struct_occ_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) {
        free(idx->entries);
    }
    dg_struct_occ_spatial_index_init(idx);
}

int dg_struct_occ_spatial_index_reserve(dg_struct_occ_spatial_index *idx, u32 capacity) {
    dg_struct_occ_spatial_entry *e;
    if (!idx) return -1;
    dg_struct_occ_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_struct_occ_spatial_entry *)malloc(sizeof(dg_struct_occ_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_struct_occ_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_struct_occ_spatial_index_clear(dg_struct_occ_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_struct_occ_spatial_index_count(const dg_struct_occ_spatial_index *idx) {
    return idx ? idx->count : 0u;
}

u32 dg_struct_occ_spatial_index_capacity(const dg_struct_occ_spatial_index *idx) {
    return idx ? idx->capacity : 0u;
}

u32 dg_struct_occ_spatial_index_probe_refused(const dg_struct_occ_spatial_index *idx) {
    return idx ? idx->probe_refused : 0u;
}

u32 dg_struct_occ_spatial_index_remove_struct(dg_struct_occ_spatial_index *idx, dg_struct_id struct_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || struct_id == 0u) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (idx->entries[i].struct_id == struct_id) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_struct_occ_spatial_entry) * (size_t)(idx->count - (i + 1u)));
            }
            idx->count -= 1u;
            removed += 1u;
            continue;
        }
        i += 1u;
    }
    return removed;
}

int dg_struct_occ_spatial_index_add_region(dg_struct_occ_spatial_index *idx, const dg_struct_occ_region *r, dg_q chunk_size_q) {
    dg_struct_chunk_coord cmin;
    dg_struct_chunk_coord cmax;
    i32 cx, cy, cz;
    int partial = 0;
    if (!idx || !r) return -1;
    if (chunk_size_q <= 0) return -2;
    if (!idx->entries || idx->capacity == 0u) return -3;

    dg_struct_chunk_range_for_aabb(&r->bbox_world, chunk_size_q, &cmin, &cmax);
    for (cz = cmin.cz; cz <= cmax.cz; ++cz) {
        for (cy = cmin.cy; cy <= cmax.cy; ++cy) {
            for (cx = cmin.cx; cx <= cmax.cx; ++cx) {
                dg_struct_chunk_coord c;
                int rc;
                c.cx = cx; c.cy = cy; c.cz = cz;
                rc = dg_struct_occ_spatial_index_add_entry(idx, &c, r->struct_id, r->id, &r->bbox_world);
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

/* ------------------------ rebuild logic ------------------------ */

static const dg_struct_footprint *dg_struct_find_footprint(
    const dg_struct_footprint *fps, u32 count, dg_struct_footprint_id id
) {
    u32 i;
    if (!fps || id == 0u) return (const dg_struct_footprint *)0;
    for (i = 0u; i < count; ++i) {
        if (fps[i].id == id) return &fps[i];
    }
    return (const dg_struct_footprint *)0;
}

static const dg_struct_volume *dg_struct_find_volume(
    const dg_struct_volume *vs, u32 count, dg_struct_volume_id id
) {
    u32 i;
    if (!vs || id == 0u) return (const dg_struct_volume *)0;
    for (i = 0u; i < count; ++i) {
        if (vs[i].id == id) return &vs[i];
    }
    return (const dg_struct_volume *)0;
}

static void dg_struct_aabb_union_inplace(dg_struct_aabb *dst, const dg_struct_aabb *b) {
    if (!dst || !b) return;
    if (b->min.x < dst->min.x) dst->min.x = b->min.x;
    if (b->min.y < dst->min.y) dst->min.y = b->min.y;
    if (b->min.z < dst->min.z) dst->min.z = b->min.z;
    if (b->max.x > dst->max.x) dst->max.x = b->max.x;
    if (b->max.y > dst->max.y) dst->max.y = b->max.y;
    if (b->max.z > dst->max.z) dst->max.z = b->max.z;
}

static int dg_struct_volume_local_aabb(
    const dg_struct_volume    *v,
    const dg_struct_footprint *fps,
    u32                        fp_count,
    const dg_struct_volume    *vols,
    u32                        vol_count,
    u32                        depth,
    dg_struct_aabb            *out
) {
    dg_struct_footprint_aabb2 fp_aabb;
    const dg_struct_footprint *fp;
    dg_struct_aabb tmp;
    d_bool have;
    u32 i;

    if (!out) return -1;
    memset(out, 0, sizeof(*out));
    if (!v) return -2;
    if (depth > 8u) return -3;

    switch (v->kind) {
    case DG_STRUCT_VOLUME_EXTRUDE:
        fp = dg_struct_find_footprint(fps, fp_count, v->u.extrude.footprint_id);
        if (!fp) return -10;
        if (dg_struct_footprint_get_aabb2(fp, &fp_aabb) != 0) return -11;
        out->min.x = fp_aabb.min_x;
        out->min.y = fp_aabb.min_y;
        out->min.z = v->u.extrude.base_z;
        out->max.x = fp_aabb.max_x;
        out->max.y = fp_aabb.max_y;
        out->max.z = (dg_q)d_q48_16_add((q48_16)v->u.extrude.base_z, (q48_16)v->u.extrude.height);
        return 0;
    case DG_STRUCT_VOLUME_SWEEP:
        fp = dg_struct_find_footprint(fps, fp_count, v->u.sweep.footprint_id);
        if (!fp) return -20;
        if (dg_struct_footprint_get_aabb2(fp, &fp_aabb) != 0) return -21;
        out->min.x = fp_aabb.min_x;
        out->min.y = fp_aabb.min_y;
        out->min.z = 0;
        out->max.x = (dg_q)d_q48_16_add((q48_16)fp_aabb.max_x, (q48_16)v->u.sweep.length);
        out->max.y = fp_aabb.max_y;
        out->max.z = v->u.sweep.height;
        return 0;
    case DG_STRUCT_VOLUME_BOOL:
        have = D_FALSE;
        memset(&tmp, 0, sizeof(tmp));
        for (i = 0u; i < v->u.boolean.term_count; ++i) {
            const dg_struct_volume_bool_term *t = &v->u.boolean.terms[i];
            const dg_struct_volume *opv;
            dg_struct_aabb op_box;
            int rc;
            opv = dg_struct_find_volume(vols, vol_count, t->volume_id);
            if (!opv) return -30;
            if (opv->id == v->id) return -31;
            rc = dg_struct_volume_local_aabb(opv, fps, fp_count, vols, vol_count, depth + 1u, &op_box);
            if (rc != 0) return rc;
            if (!have) {
                tmp = op_box;
                have = D_TRUE;
            } else {
                dg_struct_aabb_union_inplace(&tmp, &op_box);
            }
        }
        if (!have) return -32;
        *out = tmp;
        return 0;
    default:
        return -4;
    }
}

static dg_struct_aabb dg_struct_aabb_transform(const dg_struct_aabb *b, const dg_pose *pose) {
    dg_struct_aabb out;
    d_bool have = D_FALSE;
    dg_q xs[2];
    dg_q ys[2];
    dg_q zs[2];
    u32 xi, yi, zi;
    memset(&out, 0, sizeof(out));
    if (!b || !pose) return out;
    xs[0] = b->min.x; xs[1] = b->max.x;
    ys[0] = b->min.y; ys[1] = b->max.y;
    zs[0] = b->min.z; zs[1] = b->max.z;

    for (zi = 0u; zi < 2u; ++zi) {
        for (yi = 0u; yi < 2u; ++yi) {
            for (xi = 0u; xi < 2u; ++xi) {
                dg_vec3_q local;
                dg_vec3_q world;
                local.x = xs[xi];
                local.y = ys[yi];
                local.z = zs[zi];
                world = dg_pose_transform_point(pose, local, DG_ROUND_NEAR);
                if (!have) {
                    out.min = world;
                    out.max = world;
                    have = D_TRUE;
                } else {
                    if (world.x < out.min.x) out.min.x = world.x;
                    if (world.y < out.min.y) out.min.y = world.y;
                    if (world.z < out.min.z) out.min.z = world.z;
                    if (world.x > out.max.x) out.max.x = world.x;
                    if (world.y > out.max.y) out.max.y = world.y;
                    if (world.z > out.max.z) out.max.z = world.z;
                }
            }
        }
    }
    return out;
}

static u64 dg_struct_hash_step(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

static dg_struct_occ_region_id dg_struct_occ_region_id_make(dg_struct_id struct_id, dg_struct_volume_id volume_id, d_bool is_void) {
    u64 h = 0x53A2E9D16B5A3C1DULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)volume_id);
    h = dg_struct_hash_step(h, (u64)(is_void ? 1u : 0u));
    return (dg_struct_occ_region_id)h;
}

int dg_struct_occupancy_rebuild(
    dg_struct_occupancy         *out,
    dg_struct_occ_spatial_index *spatial,
    const dg_struct_instance    *inst,
    dg_struct_id                 struct_id,
    const dg_struct_footprint   *footprints,
    u32                          footprint_count,
    const dg_struct_volume      *volumes,
    u32                          volume_count,
    const d_world_frame         *frames,
    dg_tick                      tick,
    dg_q                         chunk_size_q
) {
    dg_pose anchor_pose;
    dg_pose world_pose;
    u32 i;
    int partial = 0;

    if (!out || !inst) return -1;
    if (struct_id == 0u) return -2;
    if (chunk_size_q <= 0) return -3;

    if (dg_anchor_eval(&inst->anchor, frames, tick, DG_ROUND_NEAR, &anchor_pose) != 0) {
        return -4;
    }
    world_pose = dg_pose_compose(&anchor_pose, &inst->local_pose, DG_ROUND_NEAR);

    if (dg_struct_occupancy_reserve(out, inst->volume_count) != 0) {
        return -5;
    }
    out->region_count = 0u;

    if (spatial) {
        (void)dg_struct_occ_spatial_index_remove_struct(spatial, struct_id);
    }

    for (i = 0u; i < inst->volume_count; ++i) {
        dg_struct_volume_id vid = inst->volume_ids[i];
        const dg_struct_volume *v = dg_struct_find_volume(volumes, volume_count, vid);
        dg_struct_aabb local_box;
        dg_struct_occ_region r;
        int rc;

        if (!v) return -6;
        rc = dg_struct_volume_local_aabb(v, footprints, footprint_count, volumes, volume_count, 0u, &local_box);
        if (rc != 0) return -7;

        memset(&r, 0, sizeof(r));
        r.struct_id = struct_id;
        r.volume_id = v->id;
        r.is_void = v->is_void ? D_TRUE : D_FALSE;
        r.id = dg_struct_occ_region_id_make(struct_id, v->id, r.is_void);
        r.bbox_world = dg_struct_aabb_transform(&local_box, &world_pose);

        out->regions[out->region_count++] = r;
    }

    if (spatial) {
        for (i = 0u; i < out->region_count; ++i) {
            int rc = dg_struct_occ_spatial_index_add_region(spatial, &out->regions[i], chunk_size_q);
            if (rc < 0) return rc;
            if (rc > 0) partial = 1;
        }
    }

    return partial ? 1 : 0;
}
