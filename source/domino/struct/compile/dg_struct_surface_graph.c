/* STRUCT surface graph compilation (C89). */
#include "struct/compile/dg_struct_surface_graph.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "domino/core/fixed.h"

/* ------------------------ graph storage ------------------------ */

void dg_struct_surface_graph_init(dg_struct_surface_graph *g) {
    if (!g) return;
    memset(g, 0, sizeof(*g));
}

void dg_struct_surface_graph_free(dg_struct_surface_graph *g) {
    if (!g) return;
    if (g->surfaces) free(g->surfaces);
    if (g->sockets) free(g->sockets);
    dg_struct_surface_graph_init(g);
}

void dg_struct_surface_graph_clear(dg_struct_surface_graph *g) {
    if (!g) return;
    g->surface_count = 0u;
    g->socket_count = 0u;
}

int dg_struct_surface_graph_reserve(dg_struct_surface_graph *g, u32 surface_cap, u32 socket_cap) {
    dg_struct_compiled_surface *sarr;
    dg_struct_compiled_socket *carr;
    u32 new_cap;
    if (!g) return -1;

    if (surface_cap > g->surface_capacity) {
        new_cap = g->surface_capacity ? g->surface_capacity : 8u;
        while (new_cap < surface_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = surface_cap; break; }
            new_cap *= 2u;
        }
        sarr = (dg_struct_compiled_surface *)realloc(g->surfaces, sizeof(dg_struct_compiled_surface) * (size_t)new_cap);
        if (!sarr) return -2;
        if (new_cap > g->surface_capacity) {
            memset(&sarr[g->surface_capacity], 0, sizeof(dg_struct_compiled_surface) * (size_t)(new_cap - g->surface_capacity));
        }
        g->surfaces = sarr;
        g->surface_capacity = new_cap;
    }

    if (socket_cap > g->socket_capacity) {
        new_cap = g->socket_capacity ? g->socket_capacity : 8u;
        while (new_cap < socket_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = socket_cap; break; }
            new_cap *= 2u;
        }
        carr = (dg_struct_compiled_socket *)realloc(g->sockets, sizeof(dg_struct_compiled_socket) * (size_t)new_cap);
        if (!carr) return -3;
        if (new_cap > g->socket_capacity) {
            memset(&carr[g->socket_capacity], 0, sizeof(dg_struct_compiled_socket) * (size_t)(new_cap - g->socket_capacity));
        }
        g->sockets = carr;
        g->socket_capacity = new_cap;
    }

    return 0;
}

/* ------------------------ stable ID helpers ------------------------ */

static u64 dg_struct_hash_step(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

dg_struct_surface_id dg_struct_surface_id_make(dg_struct_id struct_id, dg_struct_surface_template_id template_id) {
    u64 h = 0x6A09E667F3BCC909ULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)template_id);
    return (dg_struct_surface_id)h;
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

static int dg_struct_surface_entry_cmp_key(
    const dg_struct_chunk_coord           *chunk,
    dg_struct_id                           struct_id,
    dg_struct_surface_id                   surface_id,
    const dg_struct_surface_spatial_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_struct_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    c = D_DET_CMP_U64(struct_id, e->struct_id);
    if (c) return c;
    return D_DET_CMP_U64(surface_id, e->surface_id);
}

static u32 dg_struct_surface_lower_bound_entry(
    const dg_struct_surface_spatial_index *idx,
    const dg_struct_chunk_coord           *chunk,
    dg_struct_id                           struct_id,
    dg_struct_surface_id                   surface_id
) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_surface_entry_cmp_key(chunk, struct_id, surface_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_surface_spatial_add_entry(
    dg_struct_surface_spatial_index *idx,
    const dg_struct_chunk_coord     *chunk,
    dg_struct_id                     struct_id,
    dg_struct_surface_id             surface_id,
    const dg_struct_aabb            *bbox
) {
    u32 pos;
    dg_struct_surface_spatial_entry *e;
    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk || !bbox) return -2;

    pos = dg_struct_surface_lower_bound_entry(idx, chunk, struct_id, surface_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_struct_surface_entry_cmp_key(chunk, struct_id, surface_id, e) == 0) {
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
                sizeof(dg_struct_surface_spatial_entry) * (size_t)(idx->count - pos));
    }
    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->struct_id = struct_id;
    e->surface_id = surface_id;
    e->bbox = *bbox;
    idx->count += 1u;
    return 0;
}

static int dg_struct_surface_spatial_index_add_surface(dg_struct_surface_spatial_index *idx, const dg_struct_compiled_surface *s, dg_q chunk_size_q) {
    dg_struct_chunk_coord cmin;
    dg_struct_chunk_coord cmax;
    i32 cx, cy, cz;
    int partial = 0;
    if (!idx || !s) return -1;
    if (chunk_size_q <= 0) return -2;
    if (!idx->entries || idx->capacity == 0u) return -3;
    dg_struct_chunk_range_for_aabb(&s->bbox_world, chunk_size_q, &cmin, &cmax);
    for (cz = cmin.cz; cz <= cmax.cz; ++cz) {
        for (cy = cmin.cy; cy <= cmax.cy; ++cy) {
            for (cx = cmin.cx; cx <= cmax.cx; ++cx) {
                dg_struct_chunk_coord c;
                int rc;
                c.cx = cx; c.cy = cy; c.cz = cz;
                rc = dg_struct_surface_spatial_add_entry(idx, &c, s->struct_id, s->id, &s->bbox_world);
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

void dg_struct_surface_spatial_index_init(dg_struct_surface_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_struct_surface_spatial_index_free(dg_struct_surface_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) free(idx->entries);
    dg_struct_surface_spatial_index_init(idx);
}

int dg_struct_surface_spatial_index_reserve(dg_struct_surface_spatial_index *idx, u32 capacity) {
    dg_struct_surface_spatial_entry *e;
    if (!idx) return -1;
    dg_struct_surface_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_struct_surface_spatial_entry *)malloc(sizeof(dg_struct_surface_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_struct_surface_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_struct_surface_spatial_index_clear(dg_struct_surface_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_struct_surface_spatial_index_remove_struct(dg_struct_surface_spatial_index *idx, dg_struct_id struct_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || struct_id == 0u) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (idx->entries[i].struct_id == struct_id) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_struct_surface_spatial_entry) * (size_t)(idx->count - (i + 1u)));
            }
            idx->count -= 1u;
            removed += 1u;
            continue;
        }
        i += 1u;
    }
    return removed;
}

/* ------------------------ rebuild helpers ------------------------ */

static const dg_struct_surface_template *dg_struct_find_surface_template(
    const dg_struct_surface_template *ts, u32 count, dg_struct_surface_template_id id
) {
    u32 i;
    if (!ts || id == 0u) return (const dg_struct_surface_template *)0;
    for (i = 0u; i < count; ++i) {
        if (ts[i].id == id) return &ts[i];
    }
    return (const dg_struct_surface_template *)0;
}

static const dg_struct_socket *dg_struct_find_socket(
    const dg_struct_socket *ss, u32 count, dg_struct_socket_id id
) {
    u32 i;
    if (!ss || id == 0u) return (const dg_struct_socket *)0;
    for (i = 0u; i < count; ++i) {
        if (ss[i].id == id) return &ss[i];
    }
    return (const dg_struct_socket *)0;
}

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

static int dg_struct_u64_exists_sorted(const u64 *arr, u32 count, u64 v) {
    u32 lo = 0u;
    u32 hi = count;
    u32 mid;
    if (!arr || count == 0u) return 0;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (arr[mid] >= v) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    if (lo < count && arr[lo] == v) return 1;
    return 0;
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
    case DG_STRUCT_VOLUME_BOOL:
        have = D_FALSE;
        memset(&tmp, 0, sizeof(tmp));
        for (i = 0u; i < v->u.boolean.term_count; ++i) {
            const dg_struct_volume_bool_term *t = &v->u.boolean.terms[i];
            const dg_struct_volume *opv = dg_struct_find_volume(vols, vol_count, t->volume_id);
            dg_struct_aabb op_box;
            int rc;
            if (!opv) return -20;
            if (opv->id == v->id) return -21;
            rc = dg_struct_volume_local_aabb(opv, fps, fp_count, vols, vol_count, depth + 1u, &op_box);
            if (rc != 0) return rc;
            if (!have) {
                tmp = op_box;
                have = D_TRUE;
            } else {
                if (op_box.min.x < tmp.min.x) tmp.min.x = op_box.min.x;
                if (op_box.min.y < tmp.min.y) tmp.min.y = op_box.min.y;
                if (op_box.min.z < tmp.min.z) tmp.min.z = op_box.min.z;
                if (op_box.max.x > tmp.max.x) tmp.max.x = op_box.max.x;
                if (op_box.max.y > tmp.max.y) tmp.max.y = op_box.max.y;
                if (op_box.max.z > tmp.max.z) tmp.max.z = op_box.max.z;
            }
        }
        if (!have) return -22;
        *out = tmp;
        return 0;
    default:
        return -4;
    }
}

static dg_q dg_struct_abs_q(dg_q v) { return (v < 0) ? (dg_q)(-v) : v; }

static int dg_struct_face_from_aabb(
    const dg_struct_aabb        *b,
    dg_struct_volume_face_kind   face_kind,
    u32                          face_index,
    dg_vec3_q                   *out_origin,
    dg_vec3_q                   *out_u_axis,
    dg_vec3_q                   *out_v_axis,
    dg_q                        *out_u_len,
    dg_q                        *out_v_len
) {
    const dg_q QONE = (dg_q)((i64)1 << 16);
    dg_q dx;
    dg_q dy;
    dg_q dz;
    if (!b || !out_origin || !out_u_axis || !out_v_axis || !out_u_len || !out_v_len) return -1;

    dx = (dg_q)d_q48_16_sub((q48_16)b->max.x, (q48_16)b->min.x);
    dy = (dg_q)d_q48_16_sub((q48_16)b->max.y, (q48_16)b->min.y);
    dz = (dg_q)d_q48_16_sub((q48_16)b->max.z, (q48_16)b->min.z);

    memset(out_origin, 0, sizeof(*out_origin));
    memset(out_u_axis, 0, sizeof(*out_u_axis));
    memset(out_v_axis, 0, sizeof(*out_v_axis));
    *out_u_len = 0;
    *out_v_len = 0;

    switch (face_kind) {
    case DG_STRUCT_VOL_FACE_TOP:
        out_origin->x = b->min.x;
        out_origin->y = b->min.y;
        out_origin->z = b->max.z;
        out_u_axis->x = QONE; out_u_axis->y = 0; out_u_axis->z = 0;
        out_v_axis->x = 0; out_v_axis->y = QONE; out_v_axis->z = 0;
        *out_u_len = dg_struct_abs_q(dx);
        *out_v_len = dg_struct_abs_q(dy);
        return 0;
    case DG_STRUCT_VOL_FACE_BOTTOM:
        out_origin->x = b->min.x;
        out_origin->y = b->min.y;
        out_origin->z = b->min.z;
        out_u_axis->x = QONE; out_u_axis->y = 0; out_u_axis->z = 0;
        out_v_axis->x = 0; out_v_axis->y = QONE; out_v_axis->z = 0;
        *out_u_len = dg_struct_abs_q(dx);
        *out_v_len = dg_struct_abs_q(dy);
        return 0;
    case DG_STRUCT_VOL_FACE_SIDE: {
        u32 side = face_index % 4u;
        if (side == 0u) {
            /* +X */
            out_origin->x = b->max.x;
            out_origin->y = b->min.y;
            out_origin->z = b->min.z;
            out_u_axis->x = 0; out_u_axis->y = QONE; out_u_axis->z = 0;
            out_v_axis->x = 0; out_v_axis->y = 0; out_v_axis->z = QONE;
            *out_u_len = dg_struct_abs_q(dy);
            *out_v_len = dg_struct_abs_q(dz);
        } else if (side == 1u) {
            /* -X */
            out_origin->x = b->min.x;
            out_origin->y = b->max.y;
            out_origin->z = b->min.z;
            out_u_axis->x = 0; out_u_axis->y = (dg_q)(-QONE); out_u_axis->z = 0;
            out_v_axis->x = 0; out_v_axis->y = 0; out_v_axis->z = QONE;
            *out_u_len = dg_struct_abs_q(dy);
            *out_v_len = dg_struct_abs_q(dz);
        } else if (side == 2u) {
            /* +Y */
            out_origin->x = b->max.x;
            out_origin->y = b->max.y;
            out_origin->z = b->min.z;
            out_u_axis->x = (dg_q)(-QONE); out_u_axis->y = 0; out_u_axis->z = 0;
            out_v_axis->x = 0; out_v_axis->y = 0; out_v_axis->z = QONE;
            *out_u_len = dg_struct_abs_q(dx);
            *out_v_len = dg_struct_abs_q(dz);
        } else {
            /* -Y */
            out_origin->x = b->min.x;
            out_origin->y = b->min.y;
            out_origin->z = b->min.z;
            out_u_axis->x = QONE; out_u_axis->y = 0; out_u_axis->z = 0;
            out_v_axis->x = 0; out_v_axis->y = 0; out_v_axis->z = QONE;
            *out_u_len = dg_struct_abs_q(dx);
            *out_v_len = dg_struct_abs_q(dz);
        }
        return 0;
    }
    default:
        return -2;
    }
}

static dg_vec3_q dg_struct_local_offset_axis(dg_vec3_q origin, const dg_vec3_q *axis, dg_q len) {
    dg_vec3_q p = origin;
    if (!axis) return p;
    if (axis->x > 0) p.x = (dg_q)d_q48_16_add((q48_16)p.x, (q48_16)len);
    if (axis->x < 0) p.x = (dg_q)d_q48_16_sub((q48_16)p.x, (q48_16)len);
    if (axis->y > 0) p.y = (dg_q)d_q48_16_add((q48_16)p.y, (q48_16)len);
    if (axis->y < 0) p.y = (dg_q)d_q48_16_sub((q48_16)p.y, (q48_16)len);
    if (axis->z > 0) p.z = (dg_q)d_q48_16_add((q48_16)p.z, (q48_16)len);
    if (axis->z < 0) p.z = (dg_q)d_q48_16_sub((q48_16)p.z, (q48_16)len);
    return p;
}

static dg_vec3_q dg_struct_vec3_sub(dg_vec3_q a, dg_vec3_q b) {
    dg_vec3_q o;
    o.x = (dg_q)d_q48_16_sub((q48_16)a.x, (q48_16)b.x);
    o.y = (dg_q)d_q48_16_sub((q48_16)a.y, (q48_16)b.y);
    o.z = (dg_q)d_q48_16_sub((q48_16)a.z, (q48_16)b.z);
    return o;
}

static dg_struct_aabb dg_struct_aabb_from_points4(dg_vec3_q p0, dg_vec3_q p1, dg_vec3_q p2, dg_vec3_q p3) {
    dg_struct_aabb b;
    b.min = p0;
    b.max = p0;
    if (p1.x < b.min.x) b.min.x = p1.x; if (p1.y < b.min.y) b.min.y = p1.y; if (p1.z < b.min.z) b.min.z = p1.z;
    if (p1.x > b.max.x) b.max.x = p1.x; if (p1.y > b.max.y) b.max.y = p1.y; if (p1.z > b.max.z) b.max.z = p1.z;
    if (p2.x < b.min.x) b.min.x = p2.x; if (p2.y < b.min.y) b.min.y = p2.y; if (p2.z < b.min.z) b.min.z = p2.z;
    if (p2.x > b.max.x) b.max.x = p2.x; if (p2.y > b.max.y) b.max.y = p2.y; if (p2.z > b.max.z) b.max.z = p2.z;
    if (p3.x < b.min.x) b.min.x = p3.x; if (p3.y < b.min.y) b.min.y = p3.y; if (p3.z < b.min.z) b.min.z = p3.z;
    if (p3.x > b.max.x) b.max.x = p3.x; if (p3.y > b.max.y) b.max.y = p3.y; if (p3.z > b.max.z) b.max.z = p3.z;
    return b;
}

static void dg_struct_sort_surfaces_by_id(dg_struct_compiled_surface *arr, u32 count) {
    u32 i;
    if (!arr || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_struct_compiled_surface key = arr[i];
        u32 j = i;
        while (j > 0u && arr[j - 1u].id > key.id) {
            arr[j] = arr[j - 1u];
            j -= 1u;
        }
        arr[j] = key;
    }
}

static void dg_struct_sort_sockets_by_id(dg_struct_compiled_socket *arr, u32 count) {
    u32 i;
    if (!arr || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_struct_compiled_socket key = arr[i];
        u32 j = i;
        while (j > 0u && arr[j - 1u].id > key.id) {
            arr[j] = arr[j - 1u];
            j -= 1u;
        }
        arr[j] = key;
    }
}

/* ------------------------ rebuild ------------------------ */

int dg_struct_surface_graph_rebuild(
    dg_struct_surface_graph         *out,
    dg_struct_surface_spatial_index *spatial,
    const dg_struct_instance        *inst,
    dg_struct_id                     struct_id,
    const dg_struct_surface_template *templates,
    u32                              template_count,
    const dg_struct_socket           *sockets,
    u32                              socket_count,
    const dg_struct_footprint        *footprints,
    u32                              footprint_count,
    const dg_struct_volume           *volumes,
    u32                              volume_count,
    const d_world_frame              *frames,
    dg_tick                          tick,
    dg_q                             chunk_size_q
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

    if (dg_struct_surface_graph_reserve(out, inst->surface_template_count, inst->socket_count) != 0) {
        return -5;
    }
    dg_struct_surface_graph_clear(out);

    if (spatial) {
        (void)dg_struct_surface_spatial_index_remove_struct(spatial, struct_id);
    }

    /* Surfaces (unsorted first). */
    for (i = 0u; i < inst->surface_template_count; ++i) {
        dg_struct_surface_template_id tid = inst->surface_template_ids[i];
        const dg_struct_surface_template *t = dg_struct_find_surface_template(templates, template_count, tid);
        const dg_struct_volume *v;
        dg_struct_aabb local_box;
        dg_vec3_q origin_l;
        dg_vec3_q u_axis_l;
        dg_vec3_q v_axis_l;
        dg_q u_len;
        dg_q v_len;
        dg_vec3_q u_end_l;
        dg_vec3_q v_end_l;
        dg_vec3_q uv_end_l;
        dg_vec3_q origin_w;
        dg_vec3_q u_end_w;
        dg_vec3_q v_end_w;
        dg_vec3_q uv_end_w;
        dg_struct_compiled_surface s;
        int rc;

        if (!t) return -6;
        v = dg_struct_find_volume(volumes, volume_count, t->volume_id);
        if (!v) return -7;

        rc = dg_struct_volume_local_aabb(v, footprints, footprint_count, volumes, volume_count, 0u, &local_box);
        if (rc != 0) return -8;

        rc = dg_struct_face_from_aabb(&local_box, t->face_kind, t->face_index, &origin_l, &u_axis_l, &v_axis_l, &u_len, &v_len);
        if (rc != 0) return -9;

        u_end_l = dg_struct_local_offset_axis(origin_l, &u_axis_l, u_len);
        v_end_l = dg_struct_local_offset_axis(origin_l, &v_axis_l, v_len);
        uv_end_l = dg_struct_local_offset_axis(u_end_l, &v_axis_l, v_len);

        origin_w = dg_pose_transform_point(&world_pose, origin_l, DG_ROUND_NEAR);
        u_end_w = dg_pose_transform_point(&world_pose, u_end_l, DG_ROUND_NEAR);
        v_end_w = dg_pose_transform_point(&world_pose, v_end_l, DG_ROUND_NEAR);
        uv_end_w = dg_pose_transform_point(&world_pose, uv_end_l, DG_ROUND_NEAR);

        memset(&s, 0, sizeof(s));
        s.struct_id = struct_id;
        s.template_id = t->id;
        s.id = dg_struct_surface_id_make(struct_id, t->id);
        s.volume_id = t->volume_id;
        s.enclosure_id = t->enclosure_id;
        s.face_kind = t->face_kind;
        s.face_index = t->face_index;
        s.origin_world = origin_w;
        s.u_vec_world = dg_struct_vec3_sub(u_end_w, origin_w);
        s.v_vec_world = dg_struct_vec3_sub(v_end_w, origin_w);
        s.u_len = u_len;
        s.v_len = v_len;
        s.bbox_world = dg_struct_aabb_from_points4(origin_w, u_end_w, v_end_w, uv_end_w);

        out->surfaces[out->surface_count++] = s;
    }

    /* Sockets (unsorted first). */
    for (i = 0u; i < inst->socket_count; ++i) {
        dg_struct_socket_id sid = inst->socket_ids[i];
        const dg_struct_socket *s = dg_struct_find_socket(sockets, socket_count, sid);
        dg_struct_compiled_socket cs;
        if (!s) return -10;
        if (!dg_struct_u64_exists_sorted((const u64 *)inst->surface_template_ids, inst->surface_template_count, (u64)s->surface_template_id)) {
            return -11;
        }
        memset(&cs, 0, sizeof(cs));
        cs.id = s->id;
        cs.struct_id = struct_id;
        cs.surface_id = dg_struct_surface_id_make(struct_id, s->surface_template_id);
        cs.u = s->u;
        cs.v = s->v;
        cs.offset = s->offset;
        out->sockets[out->socket_count++] = cs;
    }

    dg_struct_sort_surfaces_by_id(out->surfaces, out->surface_count);
    dg_struct_sort_sockets_by_id(out->sockets, out->socket_count);

    if (spatial) {
        for (i = 0u; i < out->surface_count; ++i) {
            int rc = dg_struct_surface_spatial_index_add_surface(spatial, &out->surfaces[i], chunk_size_q);
            if (rc < 0) return rc;
            if (rc > 0) partial = 1;
        }
    }

    return partial ? 1 : 0;
}
