#include <stdlib.h>
#include <string.h>

#include "core/graph/dg_graph.h"
#include "core/graph/dg_graph_adj.h"

static int dg_graph_reserve_nodes(dg_graph *g, u32 cap) {
    dg_graph_node *new_nodes;
    u32 old_cap;
    if (!g) {
        return -1;
    }
    if (cap <= g->node_capacity) {
        return 0;
    }
    old_cap = g->node_capacity;
    new_nodes = (dg_graph_node *)realloc(g->nodes, sizeof(dg_graph_node) * (size_t)cap);
    if (!new_nodes) {
        return -2;
    }
    if (cap > old_cap) {
        memset(&new_nodes[old_cap], 0, sizeof(dg_graph_node) * (size_t)(cap - old_cap));
    }
    g->nodes = new_nodes;
    g->node_capacity = cap;
    return 0;
}

static int dg_graph_reserve_edges(dg_graph *g, u32 cap) {
    dg_graph_edge *new_edges;
    u32 old_cap;
    if (!g) {
        return -1;
    }
    if (cap <= g->edge_capacity) {
        return 0;
    }
    old_cap = g->edge_capacity;
    new_edges = (dg_graph_edge *)realloc(g->edges, sizeof(dg_graph_edge) * (size_t)cap);
    if (!new_edges) {
        return -2;
    }
    if (cap > old_cap) {
        memset(&new_edges[old_cap], 0, sizeof(dg_graph_edge) * (size_t)(cap - old_cap));
    }
    g->edges = new_edges;
    g->edge_capacity = cap;
    return 0;
}

void dg_graph_init(dg_graph *g) {
    if (!g) {
        return;
    }
    g->nodes = (dg_graph_node *)0;
    g->node_count = 0u;
    g->node_capacity = 0u;
    g->edges = (dg_graph_edge *)0;
    g->edge_count = 0u;
    g->edge_capacity = 0u;
    g->next_node_id = (dg_node_id)1u;
    g->next_edge_id = (dg_edge_id)1u;
}

void dg_graph_free(dg_graph *g) {
    u32 i;
    if (!g) {
        return;
    }
    for (i = 0u; i < g->node_count; ++i) {
        dg_graph_adj_free(&g->nodes[i]);
    }
    if (g->nodes) {
        free(g->nodes);
    }
    if (g->edges) {
        free(g->edges);
    }
    dg_graph_init(g);
}

int dg_graph_reserve(dg_graph *g, u32 node_capacity, u32 edge_capacity) {
    int rc;
    if (!g) {
        return -1;
    }
    rc = dg_graph_reserve_nodes(g, node_capacity);
    if (rc != 0) {
        return -2;
    }
    rc = dg_graph_reserve_edges(g, edge_capacity);
    if (rc != 0) {
        return -3;
    }
    return 0;
}

u32 dg_graph_node_count(const dg_graph *g) {
    return g ? g->node_count : 0u;
}

u32 dg_graph_edge_count(const dg_graph *g) {
    return g ? g->edge_count : 0u;
}

const dg_graph_node *dg_graph_node_at(const dg_graph *g, u32 index) {
    if (!g || !g->nodes || index >= g->node_count) {
        return (const dg_graph_node *)0;
    }
    return &g->nodes[index];
}

const dg_graph_edge *dg_graph_edge_at(const dg_graph *g, u32 index) {
    if (!g || !g->edges || index >= g->edge_count) {
        return (const dg_graph_edge *)0;
    }
    return &g->edges[index];
}

static int dg_graph_node_cmp_id(const dg_graph_node *n, dg_node_id id) {
    if (n->id < id) return -1;
    if (n->id > id) return 1;
    return 0;
}

int dg_graph_find_node_index(const dg_graph *g, dg_node_id id, u32 *out_index) {
    u32 lo, hi, mid;
    if (!g || !out_index) {
        return -1;
    }
    if (!g->nodes || g->node_count == 0u) {
        return 1;
    }
    lo = 0u;
    hi = g->node_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_graph_node_cmp_id(&g->nodes[mid], id) < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < g->node_count && g->nodes[lo].id == id) {
        *out_index = lo;
        return 0;
    }
    return 1;
}

const dg_graph_node *dg_graph_find_node(const dg_graph *g, dg_node_id id) {
    u32 idx;
    if (!g) {
        return (const dg_graph_node *)0;
    }
    if (dg_graph_find_node_index(g, id, &idx) != 0) {
        return (const dg_graph_node *)0;
    }
    return &g->nodes[idx];
}

static int dg_graph_edge_cmp_id(const dg_graph_edge *e, dg_edge_id id) {
    if (e->id < id) return -1;
    if (e->id > id) return 1;
    return 0;
}

int dg_graph_find_edge_index(const dg_graph *g, dg_edge_id id, u32 *out_index) {
    u32 lo, hi, mid;
    if (!g || !out_index) {
        return -1;
    }
    if (!g->edges || g->edge_count == 0u) {
        return 1;
    }
    lo = 0u;
    hi = g->edge_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (dg_graph_edge_cmp_id(&g->edges[mid], id) < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < g->edge_count && g->edges[lo].id == id) {
        *out_index = lo;
        return 0;
    }
    return 1;
}

const dg_graph_edge *dg_graph_find_edge(const dg_graph *g, dg_edge_id id) {
    u32 idx;
    if (!g) {
        return (const dg_graph_edge *)0;
    }
    if (dg_graph_find_edge_index(g, id, &idx) != 0) {
        return (const dg_graph_edge *)0;
    }
    return &g->edges[idx];
}

static u32 dg_graph_node_upper_bound(const dg_graph *g, dg_node_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!g) {
        return 0u;
    }
    hi = g->node_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (g->nodes[mid].id <= id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static u32 dg_graph_edge_upper_bound(const dg_graph *g, dg_edge_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!g) {
        return 0u;
    }
    hi = g->edge_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (g->edges[mid].id <= id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

int dg_graph_add_node(dg_graph *g, dg_node_id id, dg_node_id *out_id) {
    dg_graph_node n;
    u32 idx;
    int rc;
    if (!g) {
        return -1;
    }

    if (id == DG_NODE_ID_INVALID) {
        id = g->next_node_id++;
        if (id == DG_NODE_ID_INVALID) {
            return -2;
        }
    } else {
        if (id >= g->next_node_id) {
            g->next_node_id = id + 1u;
        }
    }

    if (dg_graph_find_node(g, id) != (const dg_graph_node *)0) {
        return 1;
    }

    if (g->node_count >= g->node_capacity) {
        u32 new_cap = (g->node_capacity == 0u) ? 16u : (g->node_capacity * 2u);
        if (new_cap < (g->node_count + 1u)) {
            new_cap = g->node_count + 1u;
        }
        rc = dg_graph_reserve_nodes(g, new_cap);
        if (rc != 0) {
            return -3;
        }
    }

    memset(&n, 0, sizeof(n));
    n.id = id;
    n.neighbor_ids = (dg_node_id *)0;
    n.edge_ids = (dg_edge_id *)0;
    n.adj_count = 0u;
    n.adj_capacity = 0u;

    idx = dg_graph_node_upper_bound(g, id);
    if (idx < g->node_count) {
        memmove(&g->nodes[idx + 1u], &g->nodes[idx],
                sizeof(dg_graph_node) * (size_t)(g->node_count - idx));
    }
    g->nodes[idx] = n;
    g->node_count += 1u;
    if (out_id) {
        *out_id = id;
    }
    return 0;
}

static int dg_graph_add_edge_impl(dg_graph *g, dg_edge_id id, dg_node_id a, dg_node_id b, dg_edge_flags flags, dg_edge_id *out_id) {
    dg_graph_edge e;
    u32 idx;
    int rc;
    u32 a_idx;
    u32 b_idx;

    if (!g) {
        return -1;
    }
    if (a == DG_NODE_ID_INVALID || b == DG_NODE_ID_INVALID) {
        return -2;
    }
    if (dg_graph_find_node_index(g, a, &a_idx) != 0) {
        return -3;
    }
    if (dg_graph_find_node_index(g, b, &b_idx) != 0) {
        return -4;
    }

    if (id == DG_EDGE_ID_INVALID) {
        id = g->next_edge_id++;
        if (id == DG_EDGE_ID_INVALID) {
            return -5;
        }
    } else {
        if (id >= g->next_edge_id) {
            g->next_edge_id = id + 1u;
        }
    }

    if (dg_graph_find_edge(g, id) != (const dg_graph_edge *)0) {
        return 1;
    }

    if (g->edge_count >= g->edge_capacity) {
        u32 new_cap = (g->edge_capacity == 0u) ? 32u : (g->edge_capacity * 2u);
        if (new_cap < (g->edge_count + 1u)) {
            new_cap = g->edge_count + 1u;
        }
        rc = dg_graph_reserve_edges(g, new_cap);
        if (rc != 0) {
            return -6;
        }
    }

    memset(&e, 0, sizeof(e));
    e.id = id;
    e.a = a;
    e.b = b;
    e.flags = flags;

    idx = dg_graph_edge_upper_bound(g, id);
    if (idx < g->edge_count) {
        memmove(&g->edges[idx + 1u], &g->edges[idx],
                sizeof(dg_graph_edge) * (size_t)(g->edge_count - idx));
    }
    g->edges[idx] = e;
    g->edge_count += 1u;

    /* Update adjacency (canonical insertion into per-node arrays). */
    rc = dg_graph_adj_insert(&g->nodes[a_idx], b, id);
    if (rc != 0) {
        (void)dg_graph_remove_edge(g, id);
        return -7;
    }
    if ((flags & DG_EDGE_FLAG_DIRECTED) == 0u) {
        rc = dg_graph_adj_insert(&g->nodes[b_idx], a, id);
        if (rc != 0) {
            (void)dg_graph_remove_edge(g, id);
            return -8;
        }
    }

    if (out_id) {
        *out_id = id;
    }
    return 0;
}

int dg_graph_add_edge(dg_graph *g, dg_edge_id id, dg_node_id a, dg_node_id b, dg_edge_id *out_id) {
    return dg_graph_add_edge_impl(g, id, a, b, DG_EDGE_FLAG_NONE, out_id);
}

int dg_graph_add_edge_dir(dg_graph *g, dg_edge_id id, dg_node_id a, dg_node_id b, dg_edge_id *out_id) {
    return dg_graph_add_edge_impl(g, id, a, b, DG_EDGE_FLAG_DIRECTED, out_id);
}

int dg_graph_remove_edge(dg_graph *g, dg_edge_id id) {
    u32 idx;
    dg_graph_edge e;
    u32 a_idx;
    u32 b_idx;
    int rc;

    if (!g) {
        return -1;
    }
    rc = dg_graph_find_edge_index(g, id, &idx);
    if (rc != 0) {
        return rc; /* 1: not found */
    }
    e = g->edges[idx];

    if (dg_graph_find_node_index(g, e.a, &a_idx) == 0) {
        (void)dg_graph_adj_remove(&g->nodes[a_idx], e.b, e.id);
    }
    if ((e.flags & DG_EDGE_FLAG_DIRECTED) == 0u) {
        if (dg_graph_find_node_index(g, e.b, &b_idx) == 0) {
            (void)dg_graph_adj_remove(&g->nodes[b_idx], e.a, e.id);
        }
    }

    if ((idx + 1u) < g->edge_count) {
        memmove(&g->edges[idx], &g->edges[idx + 1u],
                sizeof(dg_graph_edge) * (size_t)(g->edge_count - (idx + 1u)));
    }
    g->edge_count -= 1u;
    return 0;
}

