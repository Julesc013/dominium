#include <stdlib.h>
#include <string.h>

#include "core/graph/part/dg_graph_boundary.h"

static int dg_graph_boundary_ep_cmp(const void *a, const void *b) {
    const dg_graph_boundary_endpoint *ea = (const dg_graph_boundary_endpoint *)a;
    const dg_graph_boundary_endpoint *eb = (const dg_graph_boundary_endpoint *)b;
    if (ea->boundary_key < eb->boundary_key) return -1;
    if (ea->boundary_key > eb->boundary_key) return 1;
    if (ea->part_id < eb->part_id) return -1;
    if (ea->part_id > eb->part_id) return 1;
    if (ea->node_id < eb->node_id) return -1;
    if (ea->node_id > eb->node_id) return 1;
    return 0;
}

int dg_graph_boundary_stitch(dg_graph *g, const dg_graph_boundary_endpoint *eps, u32 ep_count) {
    dg_graph_boundary_endpoint *tmp;
    u32 i;
    u32 group_start;

    if (!g) {
        return -1;
    }
    if (!eps && ep_count != 0u) {
        return -2;
    }
    if (ep_count == 0u) {
        return 0;
    }

    tmp = (dg_graph_boundary_endpoint *)malloc(sizeof(dg_graph_boundary_endpoint) * (size_t)ep_count);
    if (!tmp) {
        return -3;
    }
    memcpy(tmp, eps, sizeof(dg_graph_boundary_endpoint) * (size_t)ep_count);

    if (ep_count > 1u) {
        qsort(tmp, (size_t)ep_count, sizeof(dg_graph_boundary_endpoint), dg_graph_boundary_ep_cmp);
    }

    /* Reject exact duplicate endpoints (strict order expected for determinism). */
    for (i = 1u; i < ep_count; ++i) {
        if (dg_graph_boundary_ep_cmp(&tmp[i - 1u], &tmp[i]) == 0) {
            free(tmp);
            return -4;
        }
    }

    group_start = 0u;
    while (group_start < ep_count) {
        u32 group_end = group_start + 1u;
        u32 a;
        u64 key = tmp[group_start].boundary_key;

        while (group_end < ep_count && tmp[group_end].boundary_key == key) {
            group_end += 1u;
        }

        /* Canonical: endpoints are already sorted by (key, part_id, node_id).
         * Create edges in lexicographic pair order (a,b) over this sorted list.
         */
        for (a = group_start; a < group_end; ++a) {
            u32 b;
            for (b = a + 1u; b < group_end; ++b) {
                dg_edge_id out_id;
                int rc;
                if (tmp[a].part_id == tmp[b].part_id) {
                    continue; /* do not stitch within a partition */
                }
                rc = dg_graph_add_edge(g, DG_EDGE_ID_INVALID, tmp[a].node_id, tmp[b].node_id, &out_id);
                if (rc != 0) {
                    free(tmp);
                    return -5;
                }
            }
        }

        group_start = group_end;
    }

    free(tmp);
    return 0;
}

