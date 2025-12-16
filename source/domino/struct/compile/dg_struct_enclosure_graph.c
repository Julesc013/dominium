/*
FILE: source/domino/struct/compile/dg_struct_enclosure_graph.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_enclosure_graph
RESPONSIBILITY: Implements `dg_struct_enclosure_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT enclosure graph compilation (C89). */
#include "struct/compile/dg_struct_enclosure_graph.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"

/* ------------------------ graph storage ------------------------ */

void dg_struct_enclosure_graph_init(dg_struct_enclosure_graph *g) {
    if (!g) return;
    memset(g, 0, sizeof(*g));
}

void dg_struct_enclosure_graph_free(dg_struct_enclosure_graph *g) {
    if (!g) return;
    if (g->rooms) free(g->rooms);
    if (g->edges) free(g->edges);
    dg_struct_enclosure_graph_init(g);
}

void dg_struct_enclosure_graph_clear(dg_struct_enclosure_graph *g) {
    if (!g) return;
    g->room_count = 0u;
    g->edge_count = 0u;
}

int dg_struct_enclosure_graph_reserve(dg_struct_enclosure_graph *g, u32 room_cap, u32 edge_cap) {
    dg_struct_room_node *rarr;
    dg_struct_room_edge *earr;
    u32 new_cap;
    if (!g) return -1;

    if (room_cap > g->room_capacity) {
        new_cap = g->room_capacity ? g->room_capacity : 8u;
        while (new_cap < room_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = room_cap; break; }
            new_cap *= 2u;
        }
        rarr = (dg_struct_room_node *)realloc(g->rooms, sizeof(dg_struct_room_node) * (size_t)new_cap);
        if (!rarr) return -2;
        if (new_cap > g->room_capacity) {
            memset(&rarr[g->room_capacity], 0, sizeof(dg_struct_room_node) * (size_t)(new_cap - g->room_capacity));
        }
        g->rooms = rarr;
        g->room_capacity = new_cap;
    }

    if (edge_cap > g->edge_capacity) {
        new_cap = g->edge_capacity ? g->edge_capacity : 8u;
        while (new_cap < edge_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = edge_cap; break; }
            new_cap *= 2u;
        }
        earr = (dg_struct_room_edge *)realloc(g->edges, sizeof(dg_struct_room_edge) * (size_t)new_cap);
        if (!earr) return -3;
        if (new_cap > g->edge_capacity) {
            memset(&earr[g->edge_capacity], 0, sizeof(dg_struct_room_edge) * (size_t)(new_cap - g->edge_capacity));
        }
        g->edges = earr;
        g->edge_capacity = new_cap;
    }

    return 0;
}

static u32 dg_struct_room_lower_bound(const dg_struct_enclosure_graph *g, dg_struct_room_id room_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!g) return 0u;
    hi = g->room_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (g->rooms[mid].id >= room_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_graph_set_room(dg_struct_enclosure_graph *g, const dg_struct_room_node *room) {
    u32 idx;
    if (!g || !room) return -1;
    if (room->id == 0u) return -2;
    idx = dg_struct_room_lower_bound(g, room->id);
    if (idx < g->room_count && g->rooms[idx].id == room->id) {
        g->rooms[idx] = *room;
        return 0;
    }
    if (g->room_count + 1u > g->room_capacity) {
        if (dg_struct_enclosure_graph_reserve(g, g->room_count + 1u, g->edge_capacity) != 0) return -3;
    }
    if (idx < g->room_count) {
        memmove(&g->rooms[idx + 1u], &g->rooms[idx], sizeof(dg_struct_room_node) * (size_t)(g->room_count - idx));
    }
    g->rooms[idx] = *room;
    g->room_count += 1u;
    return 0;
}

static int dg_struct_room_edge_cmp(const dg_struct_room_edge *a, const dg_struct_room_edge *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = D_DET_CMP_U64(a->room_a, b->room_a); if (c) return c;
    c = D_DET_CMP_U64(a->room_b, b->room_b); if (c) return c;
    c = D_DET_CMP_I32((i32)a->kind, (i32)b->kind); if (c) return c;
    c = D_DET_CMP_U64(a->id, b->id); if (c) return c;
    return 0;
}

static u32 dg_struct_edge_lower_bound(const dg_struct_enclosure_graph *g, const dg_struct_room_edge *key) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!g || !key) return 0u;
    hi = g->edge_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_room_edge_cmp(&g->edges[mid], key) >= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_graph_add_edge(dg_struct_enclosure_graph *g, const dg_struct_room_edge *edge) {
    u32 idx;
    if (!g || !edge) return -1;
    if (g->edge_count + 1u > g->edge_capacity) {
        if (dg_struct_enclosure_graph_reserve(g, g->room_capacity, g->edge_count + 1u) != 0) return -2;
    }
    idx = dg_struct_edge_lower_bound(g, edge);
    if (idx < g->edge_count) {
        memmove(&g->edges[idx + 1u], &g->edges[idx], sizeof(dg_struct_room_edge) * (size_t)(g->edge_count - idx));
    }
    g->edges[idx] = *edge;
    g->edge_count += 1u;
    return 0;
}

/* ------------------------ room spatial index ------------------------ */

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

static int dg_struct_room_entry_cmp_key(
    const dg_struct_chunk_coord       *chunk,
    dg_struct_id                       struct_id,
    dg_struct_room_id                  room_id,
    const dg_struct_room_spatial_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_struct_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    c = D_DET_CMP_U64(struct_id, e->struct_id);
    if (c) return c;
    return D_DET_CMP_U64(room_id, e->room_id);
}

static u32 dg_struct_room_lower_bound_entry(
    const dg_struct_room_spatial_index *idx,
    const dg_struct_chunk_coord        *chunk,
    dg_struct_id                        struct_id,
    dg_struct_room_id                   room_id
) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_room_entry_cmp_key(chunk, struct_id, room_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_room_spatial_add_entry(
    dg_struct_room_spatial_index *idx,
    const dg_struct_chunk_coord  *chunk,
    dg_struct_id                  struct_id,
    dg_struct_room_id             room_id,
    const dg_struct_aabb         *bbox
) {
    u32 pos;
    dg_struct_room_spatial_entry *e;
    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk || !bbox) return -2;

    pos = dg_struct_room_lower_bound_entry(idx, chunk, struct_id, room_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_struct_room_entry_cmp_key(chunk, struct_id, room_id, e) == 0) {
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
                sizeof(dg_struct_room_spatial_entry) * (size_t)(idx->count - pos));
    }
    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->struct_id = struct_id;
    e->room_id = room_id;
    e->bbox = *bbox;
    idx->count += 1u;
    return 0;
}

static int dg_struct_room_spatial_index_add_room(dg_struct_room_spatial_index *idx, const dg_struct_room_node *r, dg_q chunk_size_q) {
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
                rc = dg_struct_room_spatial_add_entry(idx, &c, r->struct_id, r->id, &r->bbox_world);
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

void dg_struct_room_spatial_index_init(dg_struct_room_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_struct_room_spatial_index_free(dg_struct_room_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) free(idx->entries);
    dg_struct_room_spatial_index_init(idx);
}

int dg_struct_room_spatial_index_reserve(dg_struct_room_spatial_index *idx, u32 capacity) {
    dg_struct_room_spatial_entry *e;
    if (!idx) return -1;
    dg_struct_room_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_struct_room_spatial_entry *)malloc(sizeof(dg_struct_room_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_struct_room_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_struct_room_spatial_index_clear(dg_struct_room_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_struct_room_spatial_index_remove_struct(dg_struct_room_spatial_index *idx, dg_struct_id struct_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || struct_id == 0u) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (idx->entries[i].struct_id == struct_id) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_struct_room_spatial_entry) * (size_t)(idx->count - (i + 1u)));
            }
            idx->count -= 1u;
            removed += 1u;
            continue;
        }
        i += 1u;
    }
    return removed;
}

/* ------------------------ rebuild logic ------------------------ */

static u64 dg_struct_hash_step(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

static dg_struct_room_id dg_struct_room_id_make(dg_struct_id struct_id, dg_struct_enclosure_id enclosure_id) {
    u64 h = 0x9E9B54E9A3C67B51ULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)enclosure_id);
    return (dg_struct_room_id)h;
}

static u64 dg_struct_room_edge_id_make(
    dg_struct_id struct_id,
    dg_struct_enclosure_id src_enclosure_id,
    u64 aperture_id,
    dg_struct_enclosure_id dst_enclosure_id,
    dg_struct_aperture_kind kind
) {
    u64 h = 0xC3A5C85C97CB3127ULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)src_enclosure_id);
    h = dg_struct_hash_step(h, (u64)aperture_id);
    h = dg_struct_hash_step(h, (u64)dst_enclosure_id);
    h = dg_struct_hash_step(h, (u64)(u32)kind);
    return h;
}

static const dg_struct_enclosure *dg_struct_find_enclosure(
    const dg_struct_enclosure *es, u32 count, dg_struct_enclosure_id id
) {
    u32 i;
    if (!es || id == 0u) return (const dg_struct_enclosure *)0;
    for (i = 0u; i < count; ++i) {
        if (es[i].id == id) return &es[i];
    }
    return (const dg_struct_enclosure *)0;
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

static const dg_struct_occ_region *dg_struct_occ_find_by_volume_id(const dg_struct_occupancy *occ, dg_struct_volume_id volume_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!occ || !occ->regions || volume_id == 0u) return (const dg_struct_occ_region *)0;
    hi = occ->region_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (occ->regions[mid].volume_id >= volume_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    if (lo < occ->region_count && occ->regions[lo].volume_id == volume_id) {
        return &occ->regions[lo];
    }
    return (const dg_struct_occ_region *)0;
}

static d_bool dg_struct_aabb_union_first(dg_struct_aabb *dst, d_bool have, const dg_struct_aabb *b) {
    if (!dst || !b) return have;
    if (!have) {
        *dst = *b;
        return D_TRUE;
    }
    if (b->min.x < dst->min.x) dst->min.x = b->min.x;
    if (b->min.y < dst->min.y) dst->min.y = b->min.y;
    if (b->min.z < dst->min.z) dst->min.z = b->min.z;
    if (b->max.x > dst->max.x) dst->max.x = b->max.x;
    if (b->max.y > dst->max.y) dst->max.y = b->max.y;
    if (b->max.z > dst->max.z) dst->max.z = b->max.z;
    return have;
}

int dg_struct_enclosure_graph_rebuild(
    dg_struct_enclosure_graph    *out,
    dg_struct_room_spatial_index *spatial,
    const dg_struct_instance     *inst,
    dg_struct_id                  struct_id,
    const dg_struct_enclosure    *enclosures,
    u32                           enclosure_count,
    const dg_struct_occupancy    *occ,
    dg_q                          chunk_size_q
) {
    u32 i;
    u32 edge_cap = 0u;
    int partial = 0;

    if (!out || !inst) return -1;
    if (struct_id == 0u) return -2;
    if (chunk_size_q <= 0) return -3;

    /* Pre-size edge capacity deterministically (sum apertures). */
    for (i = 0u; i < inst->enclosure_count; ++i) {
        const dg_struct_enclosure *e = dg_struct_find_enclosure(enclosures, enclosure_count, inst->enclosure_ids[i]);
        if (e) {
            edge_cap += e->aperture_count;
        }
    }

    if (dg_struct_enclosure_graph_reserve(out, inst->enclosure_count, edge_cap) != 0) {
        return -4;
    }
    dg_struct_enclosure_graph_clear(out);

    if (spatial) {
        (void)dg_struct_room_spatial_index_remove_struct(spatial, struct_id);
    }

    /* Rooms. */
    for (i = 0u; i < inst->enclosure_count; ++i) {
        dg_struct_enclosure_id eid = inst->enclosure_ids[i];
        const dg_struct_enclosure *e = dg_struct_find_enclosure(enclosures, enclosure_count, eid);
        dg_struct_room_node room;
        dg_struct_aabb bbox;
        d_bool have_bbox = D_FALSE;
        u32 vi;

        if (!e) return -5;

        memset(&bbox, 0, sizeof(bbox));
        for (vi = 0u; vi < e->volume_count; ++vi) {
            const dg_struct_occ_region *r = dg_struct_occ_find_by_volume_id(occ, e->volume_ids[vi]);
            if (r) {
                have_bbox = dg_struct_aabb_union_first(&bbox, have_bbox, &r->bbox_world);
            }
        }

        memset(&room, 0, sizeof(room));
        room.struct_id = struct_id;
        room.enclosure_id = eid;
        room.id = dg_struct_room_id_make(struct_id, eid);
        room.bbox_world = have_bbox ? bbox : room.bbox_world;

        if (dg_struct_graph_set_room(out, &room) != 0) return -6;
    }

    /* Edges. */
    for (i = 0u; i < inst->enclosure_count; ++i) {
        dg_struct_enclosure_id eid = inst->enclosure_ids[i];
        const dg_struct_enclosure *e = dg_struct_find_enclosure(enclosures, enclosure_count, eid);
        u32 ai;
        if (!e) return -7;
        for (ai = 0u; ai < e->aperture_count; ++ai) {
            const dg_struct_aperture *ap = &e->apertures[ai];
            dg_struct_room_edge edge;
            dg_struct_room_id ra;
            dg_struct_room_id rb;
            dg_struct_room_id lo;
            dg_struct_room_id hi;
            dg_struct_enclosure_id dst_eid;

            ra = dg_struct_room_id_make(struct_id, eid);
            dst_eid = ap->to_enclosure_id;
            if (dst_eid != 0u && dg_struct_u64_exists_sorted((const u64 *)inst->enclosure_ids, inst->enclosure_count, (u64)dst_eid)) {
                rb = dg_struct_room_id_make(struct_id, dst_eid);
            } else {
                rb = 0u;
            }

            lo = ra;
            hi = rb;
            if (hi < lo) {
                dg_struct_room_id t = lo;
                lo = hi;
                hi = t;
            }

            memset(&edge, 0, sizeof(edge));
            edge.id = dg_struct_room_edge_id_make(struct_id, eid, ap->aperture_id, dst_eid, ap->kind);
            edge.room_a = lo;
            edge.room_b = hi;
            edge.kind = ap->kind;

            if (dg_struct_graph_add_edge(out, &edge) != 0) return -8;
        }
    }

    if (spatial) {
        for (i = 0u; i < out->room_count; ++i) {
            int rc = dg_struct_room_spatial_index_add_room(spatial, &out->rooms[i], chunk_size_q);
            if (rc < 0) return rc;
            if (rc > 0) partial = 1;
        }
    }

    return partial ? 1 : 0;
}

