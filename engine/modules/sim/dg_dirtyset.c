/*
FILE: source/domino/sim/dg_dirtyset.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/dg_dirtyset
RESPONSIBILITY: Implements `dg_dirtyset`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/dg_dirtyset.h"

static int dg_dirtyset_reserve_u32(void **arr, u32 elem_size, u32 *cap_inout, u32 new_cap) {
    void *p;
    u32 old_cap;
    if (!arr || !cap_inout) {
        return -1;
    }
    if (new_cap <= *cap_inout) {
        return 0;
    }
    old_cap = *cap_inout;
    p = realloc(*arr, (size_t)elem_size * (size_t)new_cap);
    if (!p) {
        return -2;
    }
    if (new_cap > old_cap) {
        memset((unsigned char *)p + ((size_t)elem_size * (size_t)old_cap), 0,
               (size_t)elem_size * (size_t)(new_cap - old_cap));
    }
    *arr = p;
    *cap_inout = new_cap;
    return 0;
}

static u32 dg_dirtyset_lower_bound_u32(const u32 *v, u32 n, u32 key) {
    u32 lo = 0u;
    u32 hi = n;
    u32 mid;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (v[mid] < key) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_dirtyset_add_u32(u32 **v, u32 *n, u32 *cap, u32 key) {
    u32 idx;
    int rc;
    if (!v || !n || !cap) {
        return -1;
    }
    if (key == 0u) {
        return -2;
    }
    idx = dg_dirtyset_lower_bound_u32(*v, *n, key);
    if (idx < *n && (*v)[idx] == key) {
        return 1; /* already present */
    }
    if (*n >= *cap) {
        u32 new_cap = (*cap == 0u) ? 32u : (*cap * 2u);
        if (new_cap < (*n + 1u)) {
            new_cap = *n + 1u;
        }
        rc = dg_dirtyset_reserve_u32((void **)v, (u32)sizeof(u32), cap, new_cap);
        if (rc != 0) {
            return -3;
        }
    }
    if (idx < *n) {
        memmove(&(*v)[idx + 1u], &(*v)[idx], sizeof(u32) * (size_t)(*n - idx));
    }
    (*v)[idx] = key;
    *n += 1u;
    return 0;
}

static int dg_dirtyset_remove_u32(u32 *v, u32 *n, u32 key) {
    u32 idx;
    if (!n) {
        return -1;
    }
    if (!v || *n == 0u) {
        return 1;
    }
    idx = dg_dirtyset_lower_bound_u32(v, *n, key);
    if (idx >= *n || v[idx] != key) {
        return 1;
    }
    if ((idx + 1u) < *n) {
        memmove(&v[idx], &v[idx + 1u], sizeof(u32) * (size_t)(*n - (idx + 1u)));
    }
    *n -= 1u;
    return 0;
}

static u32 dg_dirtyset_lower_bound_u64(const u64 *v, u32 n, u64 key) {
    u32 lo = 0u;
    u32 hi = n;
    u32 mid;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (v[mid] < key) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_dirtyset_add_u64(u64 **v, u32 *n, u32 *cap, u64 key) {
    u32 idx;
    if (!v || !n || !cap) {
        return -1;
    }
    if (key == 0u) {
        return -2;
    }
    idx = dg_dirtyset_lower_bound_u64(*v, *n, key);
    if (idx < *n && (*v)[idx] == key) {
        return 1;
    }
    if (*n >= *cap) {
        u32 new_cap = (*cap == 0u) ? 32u : (*cap * 2u);
        u64 *p;
        if (new_cap < (*n + 1u)) {
            new_cap = *n + 1u;
        }
        p = (u64 *)realloc(*v, sizeof(u64) * (size_t)new_cap);
        if (!p) {
            return -3;
        }
        if (new_cap > *cap) {
            memset(&p[*cap], 0, sizeof(u64) * (size_t)(new_cap - *cap));
        }
        *v = p;
        *cap = new_cap;
    }
    if (idx < *n) {
        memmove(&(*v)[idx + 1u], &(*v)[idx], sizeof(u64) * (size_t)(*n - idx));
    }
    (*v)[idx] = key;
    *n += 1u;
    return 0;
}

static int dg_dirtyset_remove_u64(u64 *v, u32 *n, u64 key) {
    u32 idx;
    if (!n) {
        return -1;
    }
    if (!v || *n == 0u) {
        return 1;
    }
    idx = dg_dirtyset_lower_bound_u64(v, *n, key);
    if (idx >= *n || v[idx] != key) {
        return 1;
    }
    if ((idx + 1u) < *n) {
        memmove(&v[idx], &v[idx + 1u], sizeof(u64) * (size_t)(*n - (idx + 1u)));
    }
    *n -= 1u;
    return 0;
}

static int dg_dirtyset_reserve_u64(u64 **arr, u32 *cap_inout, u32 new_cap) {
    u64 *p;
    u32 old_cap;
    if (!arr || !cap_inout) {
        return -1;
    }
    if (new_cap <= *cap_inout) {
        return 0;
    }
    old_cap = *cap_inout;
    p = (u64 *)realloc(*arr, sizeof(u64) * (size_t)new_cap);
    if (!p) {
        return -2;
    }
    if (new_cap > old_cap) {
        memset(&p[old_cap], 0, sizeof(u64) * (size_t)(new_cap - old_cap));
    }
    *arr = p;
    *cap_inout = new_cap;
    return 0;
}

void dg_dirtyset_init(dg_dirtyset *d) {
    if (!d) {
        return;
    }
    d->nodes = (dg_node_id *)0;
    d->node_count = 0u;
    d->node_capacity = 0u;
    d->edges = (dg_edge_id *)0;
    d->edge_count = 0u;
    d->edge_capacity = 0u;
    d->parts = (dg_part_id *)0;
    d->part_count = 0u;
    d->part_capacity = 0u;
}

void dg_dirtyset_free(dg_dirtyset *d) {
    if (!d) {
        return;
    }
    if (d->nodes) {
        free(d->nodes);
    }
    if (d->edges) {
        free(d->edges);
    }
    if (d->parts) {
        free(d->parts);
    }
    dg_dirtyset_init(d);
}

void dg_dirtyset_clear(dg_dirtyset *d) {
    if (!d) {
        return;
    }
    d->node_count = 0u;
    d->edge_count = 0u;
    d->part_count = 0u;
}

int dg_dirtyset_reserve(dg_dirtyset *d, u32 node_capacity, u32 edge_capacity, u32 part_capacity) {
    int rc;
    if (!d) {
        return -1;
    }
    rc = dg_dirtyset_reserve_u32((void **)&d->nodes, (u32)sizeof(dg_node_id), &d->node_capacity, node_capacity);
    if (rc != 0) {
        return -2;
    }
    rc = dg_dirtyset_reserve_u32((void **)&d->edges, (u32)sizeof(dg_edge_id), &d->edge_capacity, edge_capacity);
    if (rc != 0) {
        return -3;
    }
    rc = dg_dirtyset_reserve_u64(&d->parts, &d->part_capacity, part_capacity);
    if (rc != 0) {
        return -4;
    }
    return 0;
}

int dg_dirtyset_add_node(dg_dirtyset *d, dg_node_id node_id) {
    return dg_dirtyset_add_u32((u32 **)&d->nodes, &d->node_count, &d->node_capacity, (u32)node_id);
}

int dg_dirtyset_add_edge(dg_dirtyset *d, dg_edge_id edge_id) {
    return dg_dirtyset_add_u32((u32 **)&d->edges, &d->edge_count, &d->edge_capacity, (u32)edge_id);
}

int dg_dirtyset_add_part(dg_dirtyset *d, dg_part_id part_id) {
    return dg_dirtyset_add_u64((u64 **)&d->parts, &d->part_count, &d->part_capacity, (u64)part_id);
}

int dg_dirtyset_remove_node(dg_dirtyset *d, dg_node_id node_id) {
    if (!d) {
        return -1;
    }
    return dg_dirtyset_remove_u32((u32 *)d->nodes, &d->node_count, (u32)node_id);
}

int dg_dirtyset_remove_edge(dg_dirtyset *d, dg_edge_id edge_id) {
    if (!d) {
        return -1;
    }
    return dg_dirtyset_remove_u32((u32 *)d->edges, &d->edge_count, (u32)edge_id);
}

int dg_dirtyset_remove_part(dg_dirtyset *d, dg_part_id part_id) {
    if (!d) {
        return -1;
    }
    return dg_dirtyset_remove_u64((u64 *)d->parts, &d->part_count, (u64)part_id);
}

static int dg_dirtyset_merge_u32(u32 **dst_v, u32 *dst_n, u32 *dst_cap, const u32 *src_v, u32 src_n) {
    u32 i;
    if (!dst_v || !dst_n || !dst_cap) {
        return -1;
    }
    if (!src_v || src_n == 0u) {
        return 0;
    }
    for (i = 0u; i < src_n; ++i) {
        int rc = dg_dirtyset_add_u32(dst_v, dst_n, dst_cap, src_v[i]);
        if (rc < 0) {
            return rc;
        }
    }
    return 0;
}

static int dg_dirtyset_merge_u64(u64 **dst_v, u32 *dst_n, u32 *dst_cap, const u64 *src_v, u32 src_n) {
    u32 i;
    if (!dst_v || !dst_n || !dst_cap) {
        return -1;
    }
    if (!src_v || src_n == 0u) {
        return 0;
    }
    for (i = 0u; i < src_n; ++i) {
        int rc = dg_dirtyset_add_u64(dst_v, dst_n, dst_cap, src_v[i]);
        if (rc < 0) {
            return rc;
        }
    }
    return 0;
}

int dg_dirtyset_merge(dg_dirtyset *dst, const dg_dirtyset *src) {
    int rc;
    if (!dst || !src) {
        return -1;
    }
    rc = dg_dirtyset_merge_u32((u32 **)&dst->nodes, &dst->node_count, &dst->node_capacity, (const u32 *)src->nodes, src->node_count);
    if (rc != 0) {
        return -2;
    }
    rc = dg_dirtyset_merge_u32((u32 **)&dst->edges, &dst->edge_count, &dst->edge_capacity, (const u32 *)src->edges, src->edge_count);
    if (rc != 0) {
        return -3;
    }
    rc = dg_dirtyset_merge_u64((u64 **)&dst->parts, &dst->part_count, &dst->part_capacity, (const u64 *)src->parts, src->part_count);
    if (rc != 0) {
        return -4;
    }
    return 0;
}

u32 dg_dirtyset_node_count(const dg_dirtyset *d) {
    return d ? d->node_count : 0u;
}

u32 dg_dirtyset_edge_count(const dg_dirtyset *d) {
    return d ? d->edge_count : 0u;
}

u32 dg_dirtyset_part_count(const dg_dirtyset *d) {
    return d ? d->part_count : 0u;
}

dg_node_id dg_dirtyset_node_at(const dg_dirtyset *d, u32 index) {
    if (!d || !d->nodes || index >= d->node_count) {
        return DG_NODE_ID_INVALID;
    }
    return d->nodes[index];
}

dg_edge_id dg_dirtyset_edge_at(const dg_dirtyset *d, u32 index) {
    if (!d || !d->edges || index >= d->edge_count) {
        return DG_EDGE_ID_INVALID;
    }
    return d->edges[index];
}

dg_part_id dg_dirtyset_part_at(const dg_dirtyset *d, u32 index) {
    if (!d || !d->parts || index >= d->part_count) {
        return DG_PART_ID_INVALID;
    }
    return d->parts[index];
}

