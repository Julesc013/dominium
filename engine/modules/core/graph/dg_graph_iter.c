/*
FILE: source/domino/core/graph/dg_graph_iter.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph_iter
RESPONSIBILITY: Implements `dg_graph_iter`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "core/graph/dg_graph_iter.h"

#include "core/det_invariants.h"

static d_bool dg_graph_is_canonical(const dg_graph *g) {
    u32 i;
    if (!g) {
        return D_TRUE;
    }
    if (g->node_count > 1u && g->nodes) {
        for (i = 1u; i < g->node_count; ++i) {
            if (g->nodes[i - 1u].id >= g->nodes[i].id) {
                return D_FALSE;
            }
        }
    }
    if (g->edge_count > 1u && g->edges) {
        for (i = 1u; i < g->edge_count; ++i) {
            if (g->edges[i - 1u].id >= g->edges[i].id) {
                return D_FALSE;
            }
        }
    }
    if (g->nodes) {
        for (i = 0u; i < g->node_count; ++i) {
            const dg_graph_node *n = &g->nodes[i];
            u32 j;
            if (n->adj_count == 0u) {
                continue;
            }
            if (!n->neighbor_ids || !n->edge_ids) {
                return D_FALSE;
            }
            for (j = 1u; j < n->adj_count; ++j) {
                dg_node_id pn = n->neighbor_ids[j - 1u];
                dg_node_id cn = n->neighbor_ids[j];
                dg_edge_id pe = n->edge_ids[j - 1u];
                dg_edge_id ce = n->edge_ids[j];
                if (pn > cn) {
                    return D_FALSE;
                }
                if (pn == cn && pe > ce) {
                    return D_FALSE;
                }
            }
        }
    }
    return D_TRUE;
}

dg_graph_neighbors_iter dg_graph_neighbors(const dg_graph *g, dg_node_id node_id) {
    dg_graph_neighbors_iter it;
    const dg_graph_node *n;
    memset(&it, 0, sizeof(it));
    it.node = (const dg_graph_node *)0;
    it.index = 0u;
    if (!g) {
        return it;
    }
    n = dg_graph_find_node(g, node_id);
    it.node = n;
    return it;
}

d_bool dg_graph_neighbors_next(dg_graph_neighbors_iter *it, dg_graph_neighbor *out) {
    if (!it || !it->node) {
        return D_FALSE;
    }
    if (it->index >= it->node->adj_count) {
        return D_FALSE;
    }
    if (out) {
        out->neighbor_id = it->node->neighbor_ids[it->index];
        out->edge_id = it->node->edge_ids[it->index];
    }
    it->index += 1u;
    return D_TRUE;
}

static int dg_graph_alloc_visit_scratch(u32 n, unsigned char **out_vis, u32 **out_stack) {
    unsigned char *vis;
    u32 *stack;
    if (!out_vis || !out_stack) {
        return -1;
    }
    *out_vis = (unsigned char *)0;
    *out_stack = (u32 *)0;
    if (n == 0u) {
        return 0;
    }
    vis = (unsigned char *)malloc((size_t)n);
    if (!vis) {
        return -2;
    }
    memset(vis, 0, (size_t)n);
    stack = (u32 *)malloc(sizeof(u32) * (size_t)n);
    if (!stack) {
        free(vis);
        return -3;
    }
    *out_vis = vis;
    *out_stack = stack;
    return 0;
}

int dg_graph_bfs(const dg_graph *g, dg_node_id start_id, dg_graph_visit_fn fn, void *user_ctx) {
    u32 ncount;
    unsigned char *visited;
    u32 *queue;
    u32 head;
    u32 tail;
    u32 start_idx;
    int rc;

    if (!g) {
        return -1;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_graph_is_canonical(g) == D_TRUE);
#endif
    ncount = dg_graph_node_count(g);
    if (ncount == 0u) {
        return 1;
    }
    rc = dg_graph_find_node_index(g, start_id, &start_idx);
    if (rc != 0) {
        return 1;
    }

    rc = dg_graph_alloc_visit_scratch(ncount, &visited, &queue);
    if (rc != 0) {
        return -2;
    }

    head = 0u;
    tail = 0u;
    visited[start_idx] = 1u;
    queue[tail++] = start_idx;

    while (head < tail) {
        const dg_graph_node *n;
        u32 idx;
        u32 i;

        idx = queue[head++];
        n = dg_graph_node_at(g, idx);
        if (!n) {
            continue;
        }
        if (fn) {
            fn(n->id, user_ctx);
        }
        for (i = 0u; i < n->adj_count; ++i) {
            dg_node_id nbr_id;
            u32 nbr_idx;
            nbr_id = n->neighbor_ids[i];
            if (dg_graph_find_node_index(g, nbr_id, &nbr_idx) != 0) {
                continue;
            }
            if (!visited[nbr_idx]) {
                visited[nbr_idx] = 1u;
                queue[tail++] = nbr_idx;
            }
        }
    }

    free(queue);
    free(visited);
    return 0;
}

int dg_graph_dfs(const dg_graph *g, dg_node_id start_id, dg_graph_visit_fn fn, void *user_ctx) {
    u32 ncount;
    unsigned char *visited;
    u32 *stack;
    u32 sp;
    u32 start_idx;
    int rc;

    if (!g) {
        return -1;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_graph_is_canonical(g) == D_TRUE);
#endif
    ncount = dg_graph_node_count(g);
    if (ncount == 0u) {
        return 1;
    }
    rc = dg_graph_find_node_index(g, start_id, &start_idx);
    if (rc != 0) {
        return 1;
    }

    rc = dg_graph_alloc_visit_scratch(ncount, &visited, &stack);
    if (rc != 0) {
        return -2;
    }

    sp = 0u;
    stack[sp++] = start_idx;

    while (sp != 0u) {
        const dg_graph_node *n;
        u32 idx;
        u32 i;

        idx = stack[--sp];
        if (visited[idx]) {
            continue;
        }
        visited[idx] = 1u;

        n = dg_graph_node_at(g, idx);
        if (!n) {
            continue;
        }
        if (fn) {
            fn(n->id, user_ctx);
        }

        /* Push neighbors in reverse canonical order so pop yields ascending. */
        i = n->adj_count;
        while (i != 0u) {
            dg_node_id nbr_id;
            u32 nbr_idx;
            i -= 1u;
            nbr_id = n->neighbor_ids[i];
            if (dg_graph_find_node_index(g, nbr_id, &nbr_idx) != 0) {
                continue;
            }
            if (!visited[nbr_idx]) {
                stack[sp++] = nbr_idx;
            }
        }
    }

    free(stack);
    free(visited);
    return 0;
}

int dg_graph_topo_walk(const dg_graph *g, dg_graph_visit_fn fn, void *user_ctx) {
    u32 ncount;
    u32 ecount;
    u32 *indeg;
    u32 *queue;
    u32 qcount;
    u32 out_count;
    u32 i;

    if (!g) {
        return -1;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_graph_is_canonical(g) == D_TRUE);
#endif
    ncount = dg_graph_node_count(g);
    if (ncount == 0u) {
        return 0;
    }
    ecount = dg_graph_edge_count(g);

    indeg = (u32 *)malloc(sizeof(u32) * (size_t)ncount);
    if (!indeg) {
        return -2;
    }
    memset(indeg, 0, sizeof(u32) * (size_t)ncount);

    for (i = 0u; i < ecount; ++i) {
        const dg_graph_edge *e = dg_graph_edge_at(g, i);
        u32 a_idx;
        u32 b_idx;
        if (!e) {
            continue;
        }
        if (dg_graph_find_node_index(g, e->a, &a_idx) != 0) {
            continue;
        }
        if (dg_graph_find_node_index(g, e->b, &b_idx) != 0) {
            continue;
        }
        if ((e->flags & DG_EDGE_FLAG_DIRECTED) != 0u) {
            indeg[b_idx] += 1u;
        } else {
            indeg[a_idx] += 1u;
            indeg[b_idx] += 1u;
        }
    }

    queue = (u32 *)malloc(sizeof(u32) * (size_t)ncount);
    if (!queue) {
        free(indeg);
        return -3;
    }
    qcount = 0u;
    for (i = 0u; i < ncount; ++i) {
        if (indeg[i] == 0u) {
            queue[qcount++] = i; /* nodes are already sorted by id */
        }
    }

    out_count = 0u;
    while (qcount != 0u) {
        u32 idx;
        u32 j;
        const dg_graph_node *n;

        /* Pop smallest node id available (queue kept sorted by node index). */
        idx = queue[0];
        if (qcount > 1u) {
            memmove(&queue[0], &queue[1], sizeof(u32) * (size_t)(qcount - 1u));
        }
        qcount -= 1u;

        n = dg_graph_node_at(g, idx);
        if (n && fn) {
            fn(n->id, user_ctx);
        }
        out_count += 1u;

        /* Decrement indegrees of outbound neighbors (deterministic).
         * NOTE: This uses adjacency, which for undirected edges yields arcs
         * in both directions and will typically prevent DAG ordering.
         */
        if (n) {
            for (j = 0u; j < n->adj_count; ++j) {
                dg_node_id nbr_id;
                u32 nbr_idx;
                nbr_id = n->neighbor_ids[j];
                if (dg_graph_find_node_index(g, nbr_id, &nbr_idx) != 0) {
                    continue;
                }
                if (indeg[nbr_idx] != 0u) {
                    indeg[nbr_idx] -= 1u;
                    if (indeg[nbr_idx] == 0u) {
                        /* Insert into queue keeping it sorted by node index.
                         * Since node indices follow node_id order, this is canonical.
                         */
                        u32 ins = 0u;
                        while (ins < qcount && queue[ins] < nbr_idx) {
                            ins += 1u;
                        }
                        if (ins < qcount) {
                            memmove(&queue[ins + 1u], &queue[ins], sizeof(u32) * (size_t)(qcount - ins));
                        }
                        queue[ins] = nbr_idx;
                        qcount += 1u;
                    }
                }
            }
        }
    }

    free(queue);
    free(indeg);

    if (out_count != ncount) {
        return 1; /* cycle detected */
    }
    return 0;
}

int dg_graph_shortest_path_unweighted(
    const dg_graph *g,
    dg_node_id      start_id,
    dg_node_id      goal_id,
    dg_node_id     *out_path,
    u32             out_cap,
    u32            *out_len
) {
    u32 ncount;
    unsigned char *visited;
    u32 *queue;
    i32 *prev;
    u32 head;
    u32 tail;
    u32 start_idx;
    u32 goal_idx;
    int rc;

    if (!g || !out_len) {
        return -1;
    }
#ifndef NDEBUG
    DG_DET_GUARD_SORTED(dg_graph_is_canonical(g) == D_TRUE);
#endif
    *out_len = 0u;

    ncount = dg_graph_node_count(g);
    if (ncount == 0u) {
        return 2;
    }
    if (dg_graph_find_node_index(g, start_id, &start_idx) != 0) {
        return 2;
    }
    if (dg_graph_find_node_index(g, goal_id, &goal_idx) != 0) {
        return 2;
    }

    rc = dg_graph_alloc_visit_scratch(ncount, &visited, &queue);
    if (rc != 0) {
        return -2;
    }
    prev = (i32 *)malloc(sizeof(i32) * (size_t)ncount);
    if (!prev) {
        free(queue);
        free(visited);
        return -3;
    }
    {
        u32 i;
        for (i = 0u; i < ncount; ++i) {
            prev[i] = -1;
        }
    }

    head = 0u;
    tail = 0u;
    visited[start_idx] = 1u;
    queue[tail++] = start_idx;

    while (head < tail) {
        const dg_graph_node *n;
        u32 idx;
        u32 i;

        idx = queue[head++];
        if (idx == goal_idx) {
            break;
        }
        n = dg_graph_node_at(g, idx);
        if (!n) {
            continue;
        }
        for (i = 0u; i < n->adj_count; ++i) {
            dg_node_id nbr_id;
            u32 nbr_idx;
            nbr_id = n->neighbor_ids[i];
            if (dg_graph_find_node_index(g, nbr_id, &nbr_idx) != 0) {
                continue;
            }
            if (!visited[nbr_idx]) {
                visited[nbr_idx] = 1u;
                prev[nbr_idx] = (i32)idx;
                queue[tail++] = nbr_idx;
            }
        }
    }

    if (!visited[goal_idx]) {
        free(prev);
        free(queue);
        free(visited);
        return 1; /* no path */
    }

    /* Reconstruct path by following prev links, then reverse into out_path. */
    {
        u32 len = 0u;
        u32 cur = goal_idx;

        while (cur != start_idx) {
            if (len >= ncount) {
                break;
            }
            len += 1u;
            cur = (u32)prev[cur];
        }
        len += 1u; /* include start */

        if (out_path && out_cap >= len) {
            u32 w = len;
            cur = goal_idx;
            while (w != 0u) {
                const dg_graph_node *n = dg_graph_node_at(g, cur);
                w -= 1u;
                out_path[w] = n ? n->id : DG_NODE_ID_INVALID;
                if (cur == start_idx) {
                    break;
                }
                cur = (u32)prev[cur];
            }
        }

        *out_len = len;
    }

    free(prev);
    free(queue);
    free(visited);
    return 0;
}
