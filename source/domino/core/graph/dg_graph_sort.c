#include <stdlib.h>

#include "core/graph/dg_graph_sort.h"

static int dg_graph_sort_cmp_u32(const void *a, const void *b) {
    u32 va = *(const u32 *)a;
    u32 vb = *(const u32 *)b;
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
}

static int dg_graph_sort_cmp_u64(const void *a, const void *b) {
    u64 va = *(const u64 *)a;
    u64 vb = *(const u64 *)b;
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
}

void dg_graph_sort_u32(u32 *v, u32 n) {
    if (!v || n < 2u) {
        return;
    }
    qsort(v, (size_t)n, sizeof(u32), dg_graph_sort_cmp_u32);
}

void dg_graph_sort_u64(u64 *v, u32 n) {
    if (!v || n < 2u) {
        return;
    }
    qsort(v, (size_t)n, sizeof(u64), dg_graph_sort_cmp_u64);
}

void dg_graph_sort_node_ids(dg_node_id *v, u32 n) {
    dg_graph_sort_u32((u32 *)v, n);
}

void dg_graph_sort_edge_ids(dg_edge_id *v, u32 n) {
    dg_graph_sort_u32((u32 *)v, n);
}

