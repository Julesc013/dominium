#include <stdio.h>
#include <string.h>

#include "res/dg_tlv_canon.h"

#include "core/graph/dg_graph.h"
#include "core/graph/dg_graph_iter.h"

#include "core/graph/part/dg_graph_part.h"
#include "core/graph/part/dg_graph_boundary.h"

#include "sim/dg_dirtyset.h"
#include "sim/dg_rebuild.h"

#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#define TASSERT(cond, msg) do { \
    if (!(cond)) { \
        printf("FAIL: %s (line %u)\n", (msg), (unsigned int)__LINE__); \
        return 1; \
    } \
} while (0)

static u64 fnv1a64_bytes(u64 h, const unsigned char *data, u32 len) {
    u32 i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a64_u32_le(u64 h, u32 v) {
    unsigned char buf[4];
    dg_le_write_u32(buf, v);
    return fnv1a64_bytes(h, buf, 4u);
}

static u64 fnv1a64_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    return fnv1a64_bytes(h, buf, 8u);
}

static u64 hash_adj_pairs(const dg_graph *g, dg_node_id node_id) {
    dg_graph_neighbors_iter it;
    dg_graph_neighbor nb;
    u64 h = 14695981039346656037ULL;
    it = dg_graph_neighbors(g, node_id);
    while (dg_graph_neighbors_next(&it, &nb)) {
        h = fnv1a64_u32_le(h, (u32)nb.neighbor_id);
        h = fnv1a64_u32_le(h, (u32)nb.edge_id);
    }
    return h;
}

static u64 hash_graph_edges(const dg_graph *g) {
    u64 h = 14695981039346656037ULL;
    u32 i;
    for (i = 0u; i < dg_graph_edge_count(g); ++i) {
        const dg_graph_edge *e = dg_graph_edge_at(g, i);
        u32 a;
        u32 b;
        if (!e) {
            continue;
        }
        a = (u32)e->a;
        b = (u32)e->b;
        if (a > b) {
            u32 tmp = a;
            a = b;
            b = tmp;
        }
        h = fnv1a64_u32_le(h, (u32)e->id);
        h = fnv1a64_u32_le(h, a);
        h = fnv1a64_u32_le(h, b);
        h = fnv1a64_u32_le(h, (u32)e->flags);
    }
    return h;
}

/* --- 6.1 Adjacency canonical order test --- */

static int build_adj_case(dg_graph *g, const u32 *edge_order, u32 edge_order_n, u64 *out_hash) {
    dg_edge_id edges[5];
    dg_node_id u[5];
    dg_node_id v[5];
    u32 i;

    if (!g || !edge_order || !out_hash) {
        return -1;
    }

    dg_graph_init(g);
    for (i = 1u; i <= 5u; ++i) {
        TASSERT(dg_graph_add_node(g, (dg_node_id)i, (dg_node_id *)0) == 0, "add node");
    }

    /* Same graph, different insertion orders:
     * edges connect from node 1 with duplicates to node 3.
     */
    edges[0] = 20u; u[0] = 1u; v[0] = 3u;
    edges[1] = 10u; u[1] = 1u; v[1] = 2u;
    edges[2] = 15u; u[2] = 1u; v[2] = 3u;
    edges[3] = 5u;  u[3] = 1u; v[3] = 5u;
    edges[4] = 7u;  u[4] = 1u; v[4] = 4u;

    TASSERT(edge_order_n == 5u, "edge_order_n");
    for (i = 0u; i < edge_order_n; ++i) {
        u32 idx = edge_order[i];
        dg_edge_id out_id = 0u;
        TASSERT(dg_graph_add_edge(g, edges[idx], u[idx], v[idx], &out_id) == 0, "add edge");
        TASSERT(out_id == edges[idx], "edge id mismatch");
    }

    /* Verify adjacency is sorted by (neighbor_id, edge_id). */
    {
        dg_graph_neighbors_iter it = dg_graph_neighbors(g, 1u);
        dg_graph_neighbor nb;
        d_bool has_prev = D_FALSE;
        dg_node_id prev_n = 0u;
        dg_edge_id prev_e = 0u;
        while (dg_graph_neighbors_next(&it, &nb)) {
            if (has_prev) {
                TASSERT((nb.neighbor_id > prev_n) || (nb.neighbor_id == prev_n && nb.edge_id > prev_e),
                        "adjacency order invariant violated");
            }
            has_prev = D_TRUE;
            prev_n = nb.neighbor_id;
            prev_e = nb.edge_id;
        }
    }

    *out_hash = hash_adj_pairs(g, 1u);
    return 0;
}

static int test_adjacency_canonical_order(void) {
    dg_graph ga;
    dg_graph gb;
    u64 ha;
    u64 hb;
    u32 order_a[5] = { 3u, 0u, 4u, 1u, 2u };
    u32 order_b[5] = { 2u, 1u, 0u, 4u, 3u };

    TASSERT(build_adj_case(&ga, order_a, 5u, &ha) == 0, "build A");
    TASSERT(build_adj_case(&gb, order_b, 5u, &hb) == 0, "build B");
    TASSERT(ha == hb, "adjacency hash mismatch between builds");

    /* Expected canonical order for node 1:
     * (2,10) (3,15) (3,20) (4,7) (5,5)
     */
    {
        u64 exp = 14695981039346656037ULL;
        exp = fnv1a64_u32_le(exp, 2u); exp = fnv1a64_u32_le(exp, 10u);
        exp = fnv1a64_u32_le(exp, 3u); exp = fnv1a64_u32_le(exp, 15u);
        exp = fnv1a64_u32_le(exp, 3u); exp = fnv1a64_u32_le(exp, 20u);
        exp = fnv1a64_u32_le(exp, 4u); exp = fnv1a64_u32_le(exp, 7u);
        exp = fnv1a64_u32_le(exp, 5u); exp = fnv1a64_u32_le(exp, 5u);
        TASSERT(ha == exp, "adjacency order did not match expected canonical sequence");
    }

    dg_graph_free(&ga);
    dg_graph_free(&gb);
    return 0;
}

/* --- 6.2 Deterministic BFS/DFS test --- */

typedef struct visit_log_s {
    dg_node_id ids[32];
    u32        count;
} visit_log;

static void visit_log_fn(dg_node_id node_id, void *user_ctx) {
    visit_log *l = (visit_log *)user_ctx;
    if (!l) {
        return;
    }
    if (l->count >= 32u) {
        return;
    }
    l->ids[l->count++] = node_id;
}

static int build_traversal_graph(dg_graph *g, const u32 *edge_order, u32 edge_order_n) {
    /* Undirected edges (id,u,v). */
    dg_edge_id eid[5];
    dg_node_id u[5];
    dg_node_id v[5];
    u32 i;

    if (!g || !edge_order || edge_order_n != 5u) {
        return -1;
    }

    dg_graph_init(g);
    for (i = 1u; i <= 6u; ++i) {
        TASSERT(dg_graph_add_node(g, (dg_node_id)i, (dg_node_id *)0) == 0, "add node");
    }

    /* Ambiguous paths to node 5; deterministic traversal should be stable. */
    eid[0] = 40u; u[0] = 1u; v[0] = 2u;
    eid[1] = 10u; u[1] = 1u; v[1] = 3u;
    eid[2] = 30u; u[2] = 1u; v[2] = 4u;
    eid[3] = 20u; u[3] = 2u; v[3] = 5u;
    eid[4] = 50u; u[4] = 5u; v[4] = 6u;

    for (i = 0u; i < edge_order_n; ++i) {
        u32 idx = edge_order[i];
        TASSERT(dg_graph_add_edge(g, eid[idx], u[idx], v[idx], (dg_edge_id *)0) == 0, "add edge");
    }

    /* Add additional edges to create multiple equal-length discovery options. */
    TASSERT(dg_graph_add_edge(g, 60u, 3u, 5u, (dg_edge_id *)0) == 0, "add edge 3-5");
    TASSERT(dg_graph_add_edge(g, 70u, 4u, 5u, (dg_edge_id *)0) == 0, "add edge 4-5");
    return 0;
}

static int test_bfs_dfs_determinism(void) {
    dg_graph ga;
    dg_graph gb;
    u32 order_a[5] = { 3u, 0u, 4u, 1u, 2u };
    u32 order_b[5] = { 2u, 1u, 0u, 4u, 3u };
    visit_log bfs_a;
    visit_log bfs_b;
    visit_log dfs_a;
    visit_log dfs_b;
    u32 i;

    memset(&bfs_a, 0, sizeof(bfs_a));
    memset(&bfs_b, 0, sizeof(bfs_b));
    memset(&dfs_a, 0, sizeof(dfs_a));
    memset(&dfs_b, 0, sizeof(dfs_b));

    TASSERT(build_traversal_graph(&ga, order_a, 5u) == 0, "build traversal A");
    TASSERT(build_traversal_graph(&gb, order_b, 5u) == 0, "build traversal B");

    TASSERT(dg_graph_bfs(&ga, 1u, visit_log_fn, &bfs_a) == 0, "bfs A");
    TASSERT(dg_graph_bfs(&gb, 1u, visit_log_fn, &bfs_b) == 0, "bfs B");
    TASSERT(bfs_a.count == bfs_b.count, "bfs count mismatch");
    for (i = 0u; i < bfs_a.count; ++i) {
        TASSERT(bfs_a.ids[i] == bfs_b.ids[i], "bfs sequence mismatch");
    }

    TASSERT(dg_graph_dfs(&ga, 1u, visit_log_fn, &dfs_a) == 0, "dfs A");
    TASSERT(dg_graph_dfs(&gb, 1u, visit_log_fn, &dfs_b) == 0, "dfs B");
    TASSERT(dfs_a.count == dfs_b.count, "dfs count mismatch");
    for (i = 0u; i < dfs_a.count; ++i) {
        TASSERT(dfs_a.ids[i] == dfs_b.ids[i], "dfs sequence mismatch");
    }

    /* Expected canonical sequences for this graph. */
    {
        dg_node_id exp_bfs[6] = { 1u, 2u, 3u, 4u, 5u, 6u };
        dg_node_id exp_dfs[6] = { 1u, 2u, 5u, 3u, 4u, 6u };
        TASSERT(bfs_a.count == 6u, "bfs expected 6 nodes");
        TASSERT(dfs_a.count == 6u, "dfs expected 6 nodes");
        for (i = 0u; i < 6u; ++i) {
            TASSERT(bfs_a.ids[i] == exp_bfs[i], "bfs expected sequence mismatch");
            TASSERT(dfs_a.ids[i] == exp_dfs[i], "dfs expected sequence mismatch");
        }
    }

    dg_graph_free(&ga);
    dg_graph_free(&gb);
    return 0;
}

/* --- 6.3 Dirty set determinism test --- */

static u64 hash_dirtyset(const dg_dirtyset *d) {
    u64 h = 14695981039346656037ULL;
    u32 i;
    for (i = 0u; i < dg_dirtyset_part_count(d); ++i) {
        h = fnv1a64_u64_le(h, (u64)dg_dirtyset_part_at(d, i));
    }
    for (i = 0u; i < dg_dirtyset_node_count(d); ++i) {
        h = fnv1a64_u32_le(h, (u32)dg_dirtyset_node_at(d, i));
    }
    for (i = 0u; i < dg_dirtyset_edge_count(d); ++i) {
        h = fnv1a64_u32_le(h, (u32)dg_dirtyset_edge_at(d, i));
    }
    return h;
}

static int test_dirtyset_determinism(void) {
    dg_dirtyset a;
    dg_dirtyset b;
    u64 ha;
    u64 hb;

    dg_dirtyset_init(&a);
    dg_dirtyset_init(&b);

    /* Add in scrambled orders. */
    TASSERT(dg_dirtyset_add_node(&a, 5u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&a, 1u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&a, 3u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&a, 2u) == 0, "add node");

    TASSERT(dg_dirtyset_add_edge(&a, 10u) == 0, "add edge");
    TASSERT(dg_dirtyset_add_edge(&a, 7u) == 0, "add edge");
    TASSERT(dg_dirtyset_add_edge(&a, 9u) == 0, "add edge");

    TASSERT(dg_dirtyset_add_part(&a, 20u) == 0, "add part");
    TASSERT(dg_dirtyset_add_part(&a, 5u) == 0, "add part");
    TASSERT(dg_dirtyset_add_part(&a, 1u) == 0, "add part");

    TASSERT(dg_dirtyset_add_part(&b, 1u) == 0, "add part");
    TASSERT(dg_dirtyset_add_part(&b, 20u) == 0, "add part");
    TASSERT(dg_dirtyset_add_part(&b, 5u) == 0, "add part");

    TASSERT(dg_dirtyset_add_edge(&b, 9u) == 0, "add edge");
    TASSERT(dg_dirtyset_add_edge(&b, 10u) == 0, "add edge");
    TASSERT(dg_dirtyset_add_edge(&b, 7u) == 0, "add edge");

    TASSERT(dg_dirtyset_add_node(&b, 2u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&b, 3u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&b, 1u) == 0, "add node");
    TASSERT(dg_dirtyset_add_node(&b, 5u) == 0, "add node");

    ha = hash_dirtyset(&a);
    hb = hash_dirtyset(&b);
    TASSERT(ha == hb, "dirtyset hash mismatch");

    /* Verify canonical iteration order. */
    TASSERT(dg_dirtyset_part_at(&a, 0u) == 1u, "parts sorted");
    TASSERT(dg_dirtyset_part_at(&a, 1u) == 5u, "parts sorted");
    TASSERT(dg_dirtyset_part_at(&a, 2u) == 20u, "parts sorted");
    TASSERT(dg_dirtyset_node_at(&a, 0u) == 1u, "nodes sorted");
    TASSERT(dg_dirtyset_node_at(&a, 1u) == 2u, "nodes sorted");
    TASSERT(dg_dirtyset_node_at(&a, 2u) == 3u, "nodes sorted");
    TASSERT(dg_dirtyset_node_at(&a, 3u) == 5u, "nodes sorted");
    TASSERT(dg_dirtyset_edge_at(&a, 0u) == 7u, "edges sorted");
    TASSERT(dg_dirtyset_edge_at(&a, 1u) == 9u, "edges sorted");
    TASSERT(dg_dirtyset_edge_at(&a, 2u) == 10u, "edges sorted");

    dg_dirtyset_free(&a);
    dg_dirtyset_free(&b);
    return 0;
}

/* --- 6.4 Boundary stitching determinism test --- */

static int test_boundary_stitch_determinism(void) {
    dg_graph g1;
    dg_graph g2;
    dg_graph_part p;
    dg_graph_boundary_endpoint eps_a[4];
    dg_graph_boundary_endpoint eps_b[4];
    u32 i;
    u64 h1;
    u64 h2;

    dg_graph_init(&g1);
    dg_graph_init(&g2);
    dg_graph_part_init(&p);

    /* Nodes 1,2 in part 10; nodes 3,4 in part 20. */
    for (i = 1u; i <= 4u; ++i) {
        TASSERT(dg_graph_add_node(&g1, (dg_node_id)i, (dg_node_id *)0) == 0, "add node g1");
        TASSERT(dg_graph_add_node(&g2, (dg_node_id)i, (dg_node_id *)0) == 0, "add node g2");
    }
    TASSERT(dg_graph_part_set_node(&p, 1u, 10u) == 0, "assign");
    TASSERT(dg_graph_part_set_node(&p, 2u, 10u) == 0, "assign");
    TASSERT(dg_graph_part_set_node(&p, 3u, 20u) == 0, "assign");
    TASSERT(dg_graph_part_set_node(&p, 4u, 20u) == 0, "assign");

    /* Two boundary keys: 100 pairs (1,3), 200 pairs (2,4). */
    eps_a[0].boundary_key = 200u; eps_a[0].part_id = 20u; eps_a[0].node_id = 4u;
    eps_a[1].boundary_key = 100u; eps_a[1].part_id = 20u; eps_a[1].node_id = 3u;
    eps_a[2].boundary_key = 200u; eps_a[2].part_id = 10u; eps_a[2].node_id = 2u;
    eps_a[3].boundary_key = 100u; eps_a[3].part_id = 10u; eps_a[3].node_id = 1u;

    eps_b[0].boundary_key = 100u; eps_b[0].part_id = 10u; eps_b[0].node_id = 1u;
    eps_b[1].boundary_key = 200u; eps_b[1].part_id = 10u; eps_b[1].node_id = 2u;
    eps_b[2].boundary_key = 100u; eps_b[2].part_id = 20u; eps_b[2].node_id = 3u;
    eps_b[3].boundary_key = 200u; eps_b[3].part_id = 20u; eps_b[3].node_id = 4u;

    TASSERT(dg_graph_boundary_stitch(&g1, eps_a, 4u) == 0, "stitch A");
    TASSERT(dg_graph_boundary_stitch(&g2, eps_b, 4u) == 0, "stitch B");

    h1 = hash_graph_edges(&g1);
    h2 = hash_graph_edges(&g2);
    TASSERT(h1 == h2, "stitched edge hash mismatch");
    TASSERT(dg_graph_edge_count(&g1) == 2u, "expected 2 stitched edges");
    TASSERT(dg_graph_edge_count(&g2) == 2u, "expected 2 stitched edges");

    dg_graph_part_free(&p);
    dg_graph_free(&g1);
    dg_graph_free(&g2);
    return 0;
}

/* --- 6.5 Rebuild deferral test --- */

typedef struct rebuild_test_ctx_s {
    dg_graph *g;
    dg_part_id applied_parts[16];
    u32 applied_count;
} rebuild_test_ctx;

static u32 rebuild_cost_estimate(void *user_ctx, const dg_rebuild_work *work) {
    (void)user_ctx;
    if (!work) {
        return 1u;
    }
    if (work->kind == DG_REBUILD_WORK_PARTITION) {
        return 5u;
    }
    return 1u;
}

static int rebuild_execute(void *user_ctx, const dg_rebuild_work *work) {
    rebuild_test_ctx *ctx = (rebuild_test_ctx *)user_ctx;
    dg_node_id root = 100u;
    dg_node_id pnode;
    if (!ctx || !ctx->g || !work) {
        return -1;
    }
    if (work->kind != DG_REBUILD_WORK_PARTITION) {
        return 0;
    }
    if (ctx->applied_count < 16u) {
        ctx->applied_parts[ctx->applied_count++] = work->part_id;
    }
    pnode = (dg_node_id)work->part_id;
    (void)dg_graph_add_edge(ctx->g, DG_EDGE_ID_INVALID, root, pnode, (dg_edge_id *)0);
    return 0;
}

static int run_rebuild_case(u32 budget_limit, u64 *out_hash, rebuild_test_ctx *out_ctx, u32 *out_rem_n, dg_part_id *out_rem_parts) {
    dg_sched s;
    dg_rebuild_ctx rb;
    dg_rebuild_target tgt;
    dg_dirtyset dirty;
    dg_graph g;
    rebuild_test_ctx ctx;
    u32 i;

    if (!out_hash || !out_ctx || !out_rem_n || !out_rem_parts) {
        return -1;
    }

    dg_sched_init(&s);
    TASSERT(dg_sched_reserve(&s, 64u, 8u, 0u, 16u, 0u, 0u) == 0, "sched reserve");
    dg_sched_set_phase_budget_limit(&s, DG_PH_TOPOLOGY, budget_limit);

    dg_graph_init(&g);
    TASSERT(dg_graph_add_node(&g, 100u, (dg_node_id *)0) == 0, "add root node");
    for (i = 1u; i <= 4u; ++i) {
        TASSERT(dg_graph_add_node(&g, (dg_node_id)i, (dg_node_id *)0) == 0, "add partition node");
    }

    memset(&ctx, 0, sizeof(ctx));
    ctx.g = &g;

    dg_dirtyset_init(&dirty);
    /* Scrambled insertion order; scheduling must be canonical by IDs. */
    (void)dg_dirtyset_add_part(&dirty, 3u);
    (void)dg_dirtyset_add_part(&dirty, 1u);
    (void)dg_dirtyset_add_part(&dirty, 4u);
    (void)dg_dirtyset_add_part(&dirty, 2u);

    dg_rebuild_init(&rb);
    dg_rebuild_begin_tick(&rb, 1u);

    memset(&tgt, 0, sizeof(tgt));
    tgt.graph_type_id = 777u;
    tgt.graph_instance_id = 1u;
    tgt.domain_id = 0u;
    tgt.rebuild_vtbl.estimate_cost_units = rebuild_cost_estimate;
    tgt.rebuild_vtbl.execute = rebuild_execute;
    tgt.user_ctx = &ctx;

    dg_sched_set_work_handler(&s, dg_rebuild_sched_work_handler, &tgt);
    TASSERT(dg_rebuild_enqueue_from_dirty(&s, &rb, &dirty, &tgt) == 0, "enqueue rebuild work");

    TASSERT(dg_sched_tick(&s, (void *)0, 1u) == 0, "tick 1");

    /* Capture carryover queue state after tick 1. */
    {
        const dg_work_queue *q = &s.phase_queues[(u32)DG_PH_TOPOLOGY];
        u32 n = dg_work_queue_count(q);
        *out_rem_n = n;
        for (i = 0u; i < n; ++i) {
            const dg_work_item *it = dg_work_queue_at(q, i);
            dg_rebuild_work w;
            TASSERT(it != (const dg_work_item *)0, "queue at");
            TASSERT(dg_rebuild_work_from_item(it, &w) == 0, "decode work");
            out_rem_parts[i] = w.part_id;
        }
    }

    /* Run additional ticks until the phase queue is empty (bounded work). */
    for (i = 0u; i < 8u; ++i) {
        const dg_work_queue *q = &s.phase_queues[(u32)DG_PH_TOPOLOGY];
        if (dg_work_queue_count(q) == 0u) {
            break;
        }
        TASSERT(dg_sched_tick(&s, (void *)0, (dg_tick)(2u + i)) == 0, "tick N");
    }

    *out_hash = hash_graph_edges(&g);
    *out_ctx = ctx;

    dg_dirtyset_free(&dirty);
    dg_graph_free(&g);
    dg_sched_free(&s);
    return 0;
}

static int test_rebuild_deferral(void) {
    u64 full_hash;
    u64 def_hash;
    rebuild_test_ctx full_ctx;
    rebuild_test_ctx def_ctx;
    dg_part_id rem_parts[16];
    u32 rem_n = 0u;
    dg_part_id rem_parts_full[16];
    u32 rem_n_full = 0u;
    u32 i;

    memset(&full_ctx, 0, sizeof(full_ctx));
    memset(&def_ctx, 0, sizeof(def_ctx));

    /* Full rebuild: unlimited (or large) budget. */
    TASSERT(run_rebuild_case(100u, &full_hash, &full_ctx, &rem_n_full, rem_parts_full) == 0, "full rebuild");
    TASSERT(rem_n_full == 0u, "full rebuild should leave no carryover");

    /* Deferred rebuild: budget only fits 2 partition items per tick (cost 5 each). */
    TASSERT(run_rebuild_case(10u, &def_hash, &def_ctx, &rem_n, rem_parts) == 0, "deferred rebuild");

    /* After the first tick in the deferred case, expect carryover of partitions 3 and 4. */
    TASSERT(rem_n == 2u, "expected 2 carryover items after tick 1");
    TASSERT(rem_parts[0] == 3u && rem_parts[1] == 4u, "carryover queue order mismatch");

    TASSERT(full_hash == def_hash, "final rebuilt graph hash mismatch");

    TASSERT(full_ctx.applied_count == def_ctx.applied_count, "applied_count mismatch");
    for (i = 0u; i < full_ctx.applied_count; ++i) {
        TASSERT(full_ctx.applied_parts[i] == def_ctx.applied_parts[i], "applied sequence mismatch");
    }
    TASSERT(full_ctx.applied_count == 4u, "expected 4 applied partition rebuilds");
    return 0;
}

int main(void) {
    TASSERT(test_adjacency_canonical_order() == 0, "adjacency canonical order");
    TASSERT(test_bfs_dfs_determinism() == 0, "bfs/dfs determinism");
    TASSERT(test_dirtyset_determinism() == 0, "dirtyset determinism");
    TASSERT(test_boundary_stitch_determinism() == 0, "boundary stitching determinism");
    TASSERT(test_rebuild_deferral() == 0, "rebuild deferral determinism");
    printf("OK: graph_toolkit_determinism_test\n");
    return 0;
}
