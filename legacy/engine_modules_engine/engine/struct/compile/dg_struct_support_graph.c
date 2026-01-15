/*
FILE: source/domino/struct/compile/dg_struct_support_graph.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/dg_struct_support_graph
RESPONSIBILITY: Implements `dg_struct_support_graph`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT support/load graph compilation (C89). */
#include "struct/compile/dg_struct_support_graph.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "domino/core/fixed.h"

/* ------------------------ graph storage ------------------------ */

void dg_struct_support_graph_init(dg_struct_support_graph *g) {
    if (!g) return;
    memset(g, 0, sizeof(*g));
}

void dg_struct_support_graph_free(dg_struct_support_graph *g) {
    if (!g) return;
    if (g->nodes) free(g->nodes);
    if (g->edges) free(g->edges);
    dg_struct_support_graph_init(g);
}

void dg_struct_support_graph_clear(dg_struct_support_graph *g) {
    if (!g) return;
    g->node_count = 0u;
    g->edge_count = 0u;
}

int dg_struct_support_graph_reserve(dg_struct_support_graph *g, u32 node_cap, u32 edge_cap) {
    dg_struct_support_node *narr;
    dg_struct_support_edge *earr;
    u32 new_cap;
    if (!g) return -1;

    if (node_cap > g->node_capacity) {
        new_cap = g->node_capacity ? g->node_capacity : 8u;
        while (new_cap < node_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = node_cap; break; }
            new_cap *= 2u;
        }
        narr = (dg_struct_support_node *)realloc(g->nodes, sizeof(dg_struct_support_node) * (size_t)new_cap);
        if (!narr) return -2;
        if (new_cap > g->node_capacity) {
            memset(&narr[g->node_capacity], 0, sizeof(dg_struct_support_node) * (size_t)(new_cap - g->node_capacity));
        }
        g->nodes = narr;
        g->node_capacity = new_cap;
    }

    if (edge_cap > g->edge_capacity) {
        new_cap = g->edge_capacity ? g->edge_capacity : 8u;
        while (new_cap < edge_cap) {
            if (new_cap > 0x7FFFFFFFu) { new_cap = edge_cap; break; }
            new_cap *= 2u;
        }
        earr = (dg_struct_support_edge *)realloc(g->edges, sizeof(dg_struct_support_edge) * (size_t)new_cap);
        if (!earr) return -3;
        if (new_cap > g->edge_capacity) {
            memset(&earr[g->edge_capacity], 0, sizeof(dg_struct_support_edge) * (size_t)(new_cap - g->edge_capacity));
        }
        g->edges = earr;
        g->edge_capacity = new_cap;
    }

    return 0;
}

static void dg_struct_sort_nodes_by_id(dg_struct_support_node *arr, u32 count) {
    u32 i;
    if (!arr || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_struct_support_node key = arr[i];
        u32 j = i;
        while (j > 0u && arr[j - 1u].id > key.id) {
            arr[j] = arr[j - 1u];
            j -= 1u;
        }
        arr[j] = key;
    }
}

static void dg_struct_sort_edges_by_id(dg_struct_support_edge *arr, u32 count) {
    u32 i;
    if (!arr || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        dg_struct_support_edge key = arr[i];
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

static int dg_struct_chunk_cmp(const dg_struct_chunk_coord *a, const dg_struct_chunk_coord *b) {
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    return D_DET_CMP3_I32(a->cx, a->cy, a->cz, b->cx, b->cy, b->cz);
}

static int dg_struct_support_entry_cmp_key(
    const dg_struct_chunk_coord          *chunk,
    dg_struct_id                          struct_id,
    dg_struct_support_node_id             node_id,
    const dg_struct_support_spatial_entry *e
) {
    int c;
    if (!e) return 1;
    c = dg_struct_chunk_cmp(chunk, &e->chunk);
    if (c) return c;
    c = D_DET_CMP_U64(struct_id, e->struct_id);
    if (c) return c;
    return D_DET_CMP_U64(node_id, e->node_id);
}

static u32 dg_struct_support_lower_bound_entry(
    const dg_struct_support_spatial_index *idx,
    const dg_struct_chunk_coord           *chunk,
    dg_struct_id                           struct_id,
    dg_struct_support_node_id              node_id
) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!idx || !chunk) return 0u;
    hi = idx->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_struct_support_entry_cmp_key(chunk, struct_id, node_id, &idx->entries[mid]) <= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_support_spatial_add_entry(
    dg_struct_support_spatial_index *idx,
    const dg_struct_chunk_coord     *chunk,
    dg_struct_id                     struct_id,
    dg_struct_support_node_id        node_id,
    dg_vec3_q                        pos_world
) {
    u32 pos;
    dg_struct_support_spatial_entry *e;
    if (!idx || !idx->entries || idx->capacity == 0u) return -1;
    if (!chunk) return -2;

    pos = dg_struct_support_lower_bound_entry(idx, chunk, struct_id, node_id);
    if (pos < idx->count) {
        e = &idx->entries[pos];
        if (dg_struct_support_entry_cmp_key(chunk, struct_id, node_id, e) == 0) {
            e->pos_world = pos_world;
            return 1;
        }
    }

    if (idx->count >= idx->capacity) {
        idx->probe_refused += 1u;
        return -3;
    }

    if (pos < idx->count) {
        memmove(&idx->entries[pos + 1u], &idx->entries[pos],
                sizeof(dg_struct_support_spatial_entry) * (size_t)(idx->count - pos));
    }
    e = &idx->entries[pos];
    memset(e, 0, sizeof(*e));
    e->chunk = *chunk;
    e->struct_id = struct_id;
    e->node_id = node_id;
    e->pos_world = pos_world;
    idx->count += 1u;
    return 0;
}

static int dg_struct_support_spatial_index_add_node(dg_struct_support_spatial_index *idx, const dg_struct_support_node *n, dg_q chunk_size_q) {
    dg_struct_chunk_coord c;
    int rc;
    if (!idx || !n) return -1;
    if (chunk_size_q <= 0) return -2;
    if (!idx->entries || idx->capacity == 0u) return -3;
    c = dg_struct_chunk_of_pos(n->pos_world, chunk_size_q);
    rc = dg_struct_support_spatial_add_entry(idx, &c, n->struct_id, n->id, n->pos_world);
    if (rc == -3) return 1;
    return (rc < 0) ? rc : 0;
}

void dg_struct_support_spatial_index_init(dg_struct_support_spatial_index *idx) {
    if (!idx) return;
    memset(idx, 0, sizeof(*idx));
}

void dg_struct_support_spatial_index_free(dg_struct_support_spatial_index *idx) {
    if (!idx) return;
    if (idx->owns_storage && idx->entries) free(idx->entries);
    dg_struct_support_spatial_index_init(idx);
}

int dg_struct_support_spatial_index_reserve(dg_struct_support_spatial_index *idx, u32 capacity) {
    dg_struct_support_spatial_entry *e;
    if (!idx) return -1;
    dg_struct_support_spatial_index_free(idx);
    if (capacity == 0u) return 0;
    e = (dg_struct_support_spatial_entry *)malloc(sizeof(dg_struct_support_spatial_entry) * (size_t)capacity);
    if (!e) return -2;
    memset(e, 0, sizeof(dg_struct_support_spatial_entry) * (size_t)capacity);
    idx->entries = e;
    idx->capacity = capacity;
    idx->count = 0u;
    idx->owns_storage = D_TRUE;
    idx->probe_refused = 0u;
    return 0;
}

void dg_struct_support_spatial_index_clear(dg_struct_support_spatial_index *idx) {
    if (!idx) return;
    idx->count = 0u;
}

u32 dg_struct_support_spatial_index_remove_struct(dg_struct_support_spatial_index *idx, dg_struct_id struct_id) {
    u32 removed = 0u;
    u32 i;
    if (!idx || !idx->entries || struct_id == 0u) return 0u;
    i = 0u;
    while (i < idx->count) {
        if (idx->entries[i].struct_id == struct_id) {
            if (i + 1u < idx->count) {
                memmove(&idx->entries[i], &idx->entries[i + 1u],
                        sizeof(dg_struct_support_spatial_entry) * (size_t)(idx->count - (i + 1u)));
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

static u64 dg_struct_hash_step(u64 h, u64 v) { return dg_det_hash_u64(h ^ v); }

static dg_struct_support_node_id dg_struct_support_node_id_make(dg_struct_id struct_id, dg_struct_occ_region_id region_id, u32 node_index) {
    u64 h = 0xA54FF53A5F1D36F1ULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)region_id);
    h = dg_struct_hash_step(h, (u64)node_index);
    return (dg_struct_support_node_id)h;
}

static dg_struct_support_edge_id dg_struct_support_edge_id_make(dg_struct_id struct_id, dg_struct_occ_region_id region_id) {
    u64 h = 0x510E527FADE682D1ULL;
    h = dg_struct_hash_step(h, (u64)struct_id);
    h = dg_struct_hash_step(h, (u64)region_id);
    return (dg_struct_support_edge_id)h;
}

int dg_struct_support_graph_rebuild(
    dg_struct_support_graph        *out,
    dg_struct_support_spatial_index *spatial,
    dg_struct_id                    struct_id,
    const dg_struct_occupancy      *occ,
    dg_q                            chunk_size_q
) {
    u32 i;
    u32 solid_count = 0u;
    u32 node_cap;
    u32 edge_cap;
    u32 nwrite;
    u32 ewrite;
    int partial = 0;
    dg_q cap_q;

    if (!out || !occ) return -1;
    if (struct_id == 0u) return -2;
    if (chunk_size_q <= 0) return -3;

    for (i = 0u; i < occ->region_count; ++i) {
        if (!occ->regions[i].is_void) solid_count += 1u;
    }

    node_cap = solid_count * 2u;
    edge_cap = solid_count;

    if (dg_struct_support_graph_reserve(out, node_cap, edge_cap) != 0) return -4;
    dg_struct_support_graph_clear(out);

    if (spatial) {
        (void)dg_struct_support_spatial_index_remove_struct(spatial, struct_id);
    }

    cap_q = (dg_q)d_q48_16_from_int(1);

    nwrite = 0u;
    ewrite = 0u;
    for (i = 0u; i < occ->region_count; ++i) {
        const dg_struct_occ_region *r = &occ->regions[i];
        if (r->is_void) continue;

        /* Node 0 at min corner. */
        out->nodes[nwrite].struct_id = struct_id;
        out->nodes[nwrite].pos_world = r->bbox_world.min;
        out->nodes[nwrite].capacity = cap_q;
        out->nodes[nwrite].id = dg_struct_support_node_id_make(struct_id, r->id, 0u);
        nwrite += 1u;

        /* Node 1 vertically above node 0 to max.z. */
        out->nodes[nwrite].struct_id = struct_id;
        out->nodes[nwrite].pos_world.x = r->bbox_world.min.x;
        out->nodes[nwrite].pos_world.y = r->bbox_world.min.y;
        out->nodes[nwrite].pos_world.z = r->bbox_world.max.z;
        out->nodes[nwrite].capacity = cap_q;
        out->nodes[nwrite].id = dg_struct_support_node_id_make(struct_id, r->id, 1u);
        nwrite += 1u;

        out->edges[ewrite].struct_id = struct_id;
        out->edges[ewrite].a = out->nodes[nwrite - 2u].id;
        out->edges[ewrite].b = out->nodes[nwrite - 1u].id;
        out->edges[ewrite].capacity = cap_q;
        out->edges[ewrite].id = dg_struct_support_edge_id_make(struct_id, r->id);
        ewrite += 1u;
    }

    out->node_count = nwrite;
    out->edge_count = ewrite;

    dg_struct_sort_nodes_by_id(out->nodes, out->node_count);
    dg_struct_sort_edges_by_id(out->edges, out->edge_count);

    if (spatial) {
        for (i = 0u; i < out->node_count; ++i) {
            int rc = dg_struct_support_spatial_index_add_node(spatial, &out->nodes[i], chunk_size_q);
            if (rc < 0) return rc;
            if (rc > 0) partial = 1;
        }
    }

    return partial ? 1 : 0;
}

