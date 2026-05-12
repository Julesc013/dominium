/*
FILE: source/tests/dom_cosmo_graph_determinism_test.cpp
MODULE: Repository
PURPOSE: Ensures cosmos graph ordering is deterministic across build paths.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_cosmo_graph.h"

extern "C" {
#include "domino/core/spacetime.h"
}

static u64 stable_id_hash(const char *stable_id) {
    u64 out = 0ull;
    int rc = dom_id_hash64(stable_id, (u32)std::strlen(stable_id), &out);
    assert(rc == DOM_SPACETIME_OK);
    return out;
}

static void build_graph(dom::dom_cosmo_graph &graph, bool reverse_order) {
    u64 filament_a = stable_id_hash("filament.a");
    u64 cluster_a = stable_id_hash("cluster.a");
    u64 galaxy_a = stable_id_hash("galaxy.a");
    u64 system_a = stable_id_hash("system.a");
    u64 cluster_b = stable_id_hash("cluster.b");
    u64 galaxy_b = stable_id_hash("galaxy.b");
    u64 system_b = stable_id_hash("system.b");
    u64 out_id = 0ull;
    dom::dom_cosmo_edge_params params;

    assert(dom::dom_cosmo_graph_init(&graph, 42ull, 0) == dom::DOM_COSMO_GRAPH_OK);

    if (!reverse_order) {
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_FILAMENT,
                                               "filament.a", 0ull, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == filament_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                               "cluster.a", filament_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == cluster_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                               "galaxy.a", cluster_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == galaxy_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                               "system.a", galaxy_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == system_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                               "cluster.b", filament_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == cluster_b);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                               "galaxy.b", cluster_b, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == galaxy_b);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                               "system.b", galaxy_b, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == system_b);
    } else {
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                               "system.b", galaxy_b, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == system_b);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                               "galaxy.b", cluster_b, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == galaxy_b);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                               "cluster.b", filament_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == cluster_b);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_SYSTEM,
                                               "system.a", galaxy_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == system_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_GALAXY,
                                               "galaxy.a", cluster_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == galaxy_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_CLUSTER,
                                               "cluster.a", filament_a, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == cluster_a);
        assert(dom::dom_cosmo_graph_add_entity(&graph, dom::DOM_COSMO_KIND_FILAMENT,
                                               "filament.a", 0ull, &out_id) == dom::DOM_COSMO_GRAPH_OK);
        assert(out_id == filament_a);
    }

    params.duration_ticks = 120ull;
    params.cost = 5u;
    params.event_table_id = 0ull;
    if (!reverse_order) {
        assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system_a, system_b, &params, &out_id)
               == dom::DOM_COSMO_GRAPH_OK);
        params.duration_ticks = 60ull;
        assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system_b, system_a, &params, &out_id)
               == dom::DOM_COSMO_GRAPH_OK);
    } else {
        assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system_b, system_a, &params, &out_id)
               == dom::DOM_COSMO_GRAPH_OK);
        params.duration_ticks = 60ull;
        assert(dom::dom_cosmo_graph_add_travel_edge(&graph, system_a, system_b, &params, &out_id)
               == dom::DOM_COSMO_GRAPH_OK);
    }

    assert(dom::dom_cosmo_graph_validate(&graph, 0) == dom::DOM_COSMO_GRAPH_OK);
}

int main(void) {
    dom::dom_cosmo_graph graph_a;
    dom::dom_cosmo_graph graph_b;
    size_t i;

    build_graph(graph_a, false);
    build_graph(graph_b, true);

    assert(graph_a.entities.size() == graph_b.entities.size());
    assert(graph_a.edges.size() == graph_b.edges.size());

    for (i = 0u; i < graph_a.entities.size(); ++i) {
        const dom::dom_cosmo_entity &a = graph_a.entities[i];
        const dom::dom_cosmo_entity &b = graph_b.entities[i];
        assert(a.id == b.id);
        assert(a.parent_id == b.parent_id);
        assert(a.kind == b.kind);
        assert(a.stable_id == b.stable_id);
    }
    for (i = 0u; i < graph_a.edges.size(); ++i) {
        const dom::dom_cosmo_edge &a = graph_a.edges[i];
        const dom::dom_cosmo_edge &b = graph_b.edges[i];
        assert(a.id == b.id);
        assert(a.src_id == b.src_id);
        assert(a.dst_id == b.dst_id);
        assert(a.duration_ticks == b.duration_ticks);
        assert(a.cost == b.cost);
        assert(a.event_table_id == b.event_table_id);
    }

    assert(dom::dom_cosmo_graph_hash(&graph_a) == dom::dom_cosmo_graph_hash(&graph_b));

    std::printf("dom_cosmo_graph_determinism_test: OK\n");
    return 0;
}
