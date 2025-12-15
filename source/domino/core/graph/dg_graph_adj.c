#include <stdlib.h>
#include <string.h>

#include "core/graph/dg_graph_adj.h"

static int dg_graph_adj_key_cmp(dg_node_id a_n, dg_edge_id a_e, dg_node_id b_n, dg_edge_id b_e) {
    if (a_n < b_n) return -1;
    if (a_n > b_n) return 1;
    if (a_e < b_e) return -1;
    if (a_e > b_e) return 1;
    return 0;
}

static u32 dg_graph_adj_lower_bound(const dg_graph_node *n, dg_node_id neighbor_id, dg_edge_id edge_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!n || n->adj_count == 0u) {
        return 0u;
    }
    hi = n->adj_count;
    while (lo < hi) {
        int cmp;
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_graph_adj_key_cmp(n->neighbor_ids[mid], n->edge_ids[mid], neighbor_id, edge_id);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

void dg_graph_adj_free(dg_graph_node *n) {
    if (!n) {
        return;
    }
    if (n->neighbor_ids) {
        free(n->neighbor_ids);
    }
    if (n->edge_ids) {
        free(n->edge_ids);
    }
    n->neighbor_ids = (dg_node_id *)0;
    n->edge_ids = (dg_edge_id *)0;
    n->adj_count = 0u;
    n->adj_capacity = 0u;
}

static int dg_graph_adj_reserve(dg_graph_node *n, u32 cap) {
    dg_node_id *new_neighbors;
    dg_edge_id *new_edges;
    if (!n) {
        return -1;
    }
    if (cap <= n->adj_capacity) {
        return 0;
    }
    new_neighbors = (dg_node_id *)realloc(n->neighbor_ids, sizeof(dg_node_id) * (size_t)cap);
    if (!new_neighbors) {
        return -2;
    }
    n->neighbor_ids = new_neighbors;
    new_edges = (dg_edge_id *)realloc(n->edge_ids, sizeof(dg_edge_id) * (size_t)cap);
    if (!new_edges) {
        return -3;
    }
    n->edge_ids = new_edges;
    n->adj_capacity = cap;
    return 0;
}

int dg_graph_adj_insert(dg_graph_node *n, dg_node_id neighbor_id, dg_edge_id edge_id) {
    u32 idx;
    int rc;
    if (!n) {
        return -1;
    }
    if (neighbor_id == DG_NODE_ID_INVALID || edge_id == DG_EDGE_ID_INVALID) {
        return -2;
    }

    idx = dg_graph_adj_lower_bound(n, neighbor_id, edge_id);
    if (idx < n->adj_count) {
        if (dg_graph_adj_key_cmp(n->neighbor_ids[idx], n->edge_ids[idx], neighbor_id, edge_id) == 0) {
            return 1; /* duplicate */
        }
    }

    if (n->adj_count >= n->adj_capacity) {
        u32 new_cap = (n->adj_capacity == 0u) ? 4u : (n->adj_capacity * 2u);
        if (new_cap < (n->adj_count + 1u)) {
            new_cap = n->adj_count + 1u;
        }
        rc = dg_graph_adj_reserve(n, new_cap);
        if (rc != 0) {
            return -3;
        }
    }

    if (idx < n->adj_count) {
        memmove(&n->neighbor_ids[idx + 1u], &n->neighbor_ids[idx],
                sizeof(dg_node_id) * (size_t)(n->adj_count - idx));
        memmove(&n->edge_ids[idx + 1u], &n->edge_ids[idx],
                sizeof(dg_edge_id) * (size_t)(n->adj_count - idx));
    }
    n->neighbor_ids[idx] = neighbor_id;
    n->edge_ids[idx] = edge_id;
    n->adj_count += 1u;
    return 0;
}

int dg_graph_adj_remove(dg_graph_node *n, dg_node_id neighbor_id, dg_edge_id edge_id) {
    u32 idx;
    if (!n) {
        return -1;
    }
    if (n->adj_count == 0u) {
        return 1;
    }
    idx = dg_graph_adj_lower_bound(n, neighbor_id, edge_id);
    if (idx >= n->adj_count) {
        return 1;
    }
    if (dg_graph_adj_key_cmp(n->neighbor_ids[idx], n->edge_ids[idx], neighbor_id, edge_id) != 0) {
        return 1;
    }
    if ((idx + 1u) < n->adj_count) {
        memmove(&n->neighbor_ids[idx], &n->neighbor_ids[idx + 1u],
                sizeof(dg_node_id) * (size_t)(n->adj_count - (idx + 1u)));
        memmove(&n->edge_ids[idx], &n->edge_ids[idx + 1u],
                sizeof(dg_edge_id) * (size_t)(n->adj_count - (idx + 1u)));
    }
    n->adj_count -= 1u;
    return 0;
}

u32 dg_graph_adj_count(const dg_graph_node *n) {
    return n ? n->adj_count : 0u;
}

dg_node_id dg_graph_adj_neighbor_at(const dg_graph_node *n, u32 index) {
    if (!n || !n->neighbor_ids || index >= n->adj_count) {
        return DG_NODE_ID_INVALID;
    }
    return n->neighbor_ids[index];
}

dg_edge_id dg_graph_adj_edge_at(const dg_graph_node *n, u32 index) {
    if (!n || !n->edge_ids || index >= n->adj_count) {
        return DG_EDGE_ID_INVALID;
    }
    return n->edge_ids[index];
}

