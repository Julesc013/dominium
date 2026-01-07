/*
FILE: source/dominium/game/runtime/dom_cosmo_graph.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_cosmo_graph
RESPONSIBILITY: Implements deterministic cosmos graph registry.
*/
#include "runtime/dom_cosmo_graph.h"

#include <cstring>

#include "domino/io/container.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

static bool kind_valid(u32 kind) {
    return kind == dom::DOM_COSMO_KIND_FILAMENT ||
           kind == dom::DOM_COSMO_KIND_CLUSTER ||
           kind == dom::DOM_COSMO_KIND_GALAXY ||
           kind == dom::DOM_COSMO_KIND_SYSTEM;
}

static u32 expected_parent_kind(u32 kind) {
    switch (kind) {
    case dom::DOM_COSMO_KIND_CLUSTER:
        return dom::DOM_COSMO_KIND_FILAMENT;
    case dom::DOM_COSMO_KIND_GALAXY:
        return dom::DOM_COSMO_KIND_CLUSTER;
    case dom::DOM_COSMO_KIND_SYSTEM:
        return dom::DOM_COSMO_KIND_GALAXY;
    default:
        break;
    }
    return 0u;
}

static int compute_id(const char *stable_id, u64 *out_id) {
    if (!stable_id || !stable_id[0] || !out_id) {
        return dom::DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    return dom_id_hash64(stable_id, (u32)std::strlen(stable_id), out_id) == DOM_SPACETIME_OK
               ? dom::DOM_COSMO_GRAPH_OK
               : dom::DOM_COSMO_GRAPH_ERR;
}

static int find_entity_index(const std::vector<dom::dom_cosmo_entity> &list, u64 id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static int find_edge_index(const std::vector<dom::dom_cosmo_edge> &list, u64 id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static u64 fnv1a64_update(u64 h, const unsigned char *data, size_t len) {
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ull;
    }
    return h;
}

static u64 edge_id_hash(u64 src_id,
                        u64 dst_id,
                        u64 duration_ticks,
                        u32 cost,
                        u64 event_table_id) {
    unsigned char buf[8];
    u64 h = 14695981039346656037ull;

    dtlv_le_write_u64(buf, src_id);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u64(buf, dst_id);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u64(buf, duration_ticks);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u32(buf, cost);
    h = fnv1a64_update(h, buf, 4u);
    dtlv_le_write_u64(buf, event_table_id);
    h = fnv1a64_update(h, buf, 8u);
    return h;
}

static void insert_sorted_entity(std::vector<dom::dom_cosmo_entity> &list,
                                 const dom::dom_cosmo_entity &ent) {
    size_t i = 0u;
    for (; i < list.size(); ++i) {
        if (ent.id < list[i].id) {
            break;
        }
    }
    list.insert(list.begin() + (std::vector<dom::dom_cosmo_entity>::difference_type)i, ent);
}

static void insert_sorted_edge(std::vector<dom::dom_cosmo_edge> &list,
                               const dom::dom_cosmo_edge &edge) {
    size_t i = 0u;
    for (; i < list.size(); ++i) {
        if (edge.id < list[i].id) {
            break;
        }
    }
    list.insert(list.begin() + (std::vector<dom::dom_cosmo_edge>::difference_type)i, edge);
}

} // namespace

namespace dom {

dom_cosmo_graph_config::dom_cosmo_graph_config()
    : struct_size(sizeof(dom_cosmo_graph_config)),
      struct_version(DOM_COSMO_GRAPH_CONFIG_VERSION),
      max_entities(0u),
      max_edges(0u) {
}

dom_cosmo_entity::dom_cosmo_entity()
    : id(0ull),
      parent_id(0ull),
      kind(0u),
      stable_id() {
}

dom_cosmo_edge::dom_cosmo_edge()
    : id(0ull),
      src_id(0ull),
      dst_id(0ull),
      duration_ticks(0ull),
      cost(0u),
      event_table_id(0ull) {
}

dom_cosmo_edge_params::dom_cosmo_edge_params()
    : duration_ticks(0ull),
      cost(0u),
      event_table_id(0ull) {
}

dom_cosmo_graph::dom_cosmo_graph()
    : struct_size(sizeof(dom_cosmo_graph)),
      struct_version(1u),
      seed(0ull),
      config(),
      entities(),
      edges() {
}

int dom_cosmo_graph_init(dom_cosmo_graph *graph,
                         u64 seed,
                         const dom_cosmo_graph_config *config) {
    if (!graph) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    graph->struct_size = sizeof(dom_cosmo_graph);
    graph->struct_version = 1u;
    graph->seed = seed;
    graph->entities.clear();
    graph->edges.clear();
    if (config) {
        graph->config = *config;
    } else {
        graph->config = dom_cosmo_graph_config();
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_add_entity(dom_cosmo_graph *graph,
                               u32 kind,
                               const char *stable_id,
                               u64 parent_id,
                               u64 *out_id) {
    dom_cosmo_entity ent;
    u64 id = 0ull;

    if (!graph || !stable_id || !stable_id[0]) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    if (!kind_valid(kind)) {
        return DOM_COSMO_GRAPH_INVALID_KIND;
    }
    if (compute_id(stable_id, &id) != DOM_COSMO_GRAPH_OK) {
        return DOM_COSMO_GRAPH_ERR;
    }
    if (find_entity_index(graph->entities, id) >= 0) {
        return DOM_COSMO_GRAPH_DUPLICATE_ID;
    }
    if (graph->config.max_entities > 0u &&
        graph->entities.size() >= graph->config.max_entities) {
        return DOM_COSMO_GRAPH_ERR;
    }

    ent.id = id;
    ent.parent_id = parent_id;
    ent.kind = kind;
    ent.stable_id = stable_id;

    insert_sorted_entity(graph->entities, ent);
    if (out_id) {
        *out_id = id;
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_add_travel_edge(dom_cosmo_graph *graph,
                                    u64 src_id,
                                    u64 dst_id,
                                    const dom_cosmo_edge_params *params,
                                    u64 *out_edge_id) {
    dom_cosmo_edge edge;
    u64 id;

    if (!graph || !params) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    if (src_id == 0ull || dst_id == 0ull || src_id == dst_id) {
        return DOM_COSMO_GRAPH_INVALID_EDGE;
    }
    if (params->duration_ticks == 0ull) {
        return DOM_COSMO_GRAPH_INVALID_EDGE;
    }
    if (find_entity_index(graph->entities, src_id) < 0 ||
        find_entity_index(graph->entities, dst_id) < 0) {
        return DOM_COSMO_GRAPH_NOT_FOUND;
    }
    if (graph->config.max_edges > 0u &&
        graph->edges.size() >= graph->config.max_edges) {
        return DOM_COSMO_GRAPH_ERR;
    }

    id = edge_id_hash(src_id, dst_id, params->duration_ticks, params->cost, params->event_table_id);
    if (find_edge_index(graph->edges, id) >= 0) {
        return DOM_COSMO_GRAPH_DUPLICATE_ID;
    }

    edge.id = id;
    edge.src_id = src_id;
    edge.dst_id = dst_id;
    edge.duration_ticks = params->duration_ticks;
    edge.cost = params->cost;
    edge.event_table_id = params->event_table_id;
    insert_sorted_edge(graph->edges, edge);

    if (out_edge_id) {
        *out_edge_id = id;
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_validate(const dom_cosmo_graph *graph,
                             std::vector<std::string> *out_errors) {
    size_t i;
    if (out_errors) {
        out_errors->clear();
    }
    if (!graph) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }

    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        const u32 parent_kind = expected_parent_kind(ent.kind);
        const int parent_index = (ent.parent_id == 0ull)
                                     ? -1
                                     : find_entity_index(graph->entities, ent.parent_id);

        if (!kind_valid(ent.kind)) {
            if (out_errors) {
                out_errors->push_back("invalid_kind");
            }
            return DOM_COSMO_GRAPH_INVALID_KIND;
        }
        if (ent.kind == DOM_COSMO_KIND_FILAMENT) {
            if (ent.parent_id != 0ull) {
                if (out_errors) {
                    out_errors->push_back("filament_has_parent");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
        } else {
            if (ent.parent_id == 0ull || parent_index < 0) {
                if (out_errors) {
                    out_errors->push_back("missing_parent");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
            if (parent_kind != graph->entities[(size_t)parent_index].kind) {
                if (out_errors) {
                    out_errors->push_back("parent_kind_mismatch");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
        }

        {
            size_t guard = 0u;
            u64 cur = ent.parent_id;
            while (cur != 0ull && guard < graph->entities.size()) {
                if (cur == ent.id) {
                    if (out_errors) {
                        out_errors->push_back("cycle_detected");
                    }
                    return DOM_COSMO_GRAPH_CYCLE;
                }
                {
                    int idx = find_entity_index(graph->entities, cur);
                    if (idx < 0) {
                        break;
                    }
                    cur = graph->entities[(size_t)idx].parent_id;
                }
                guard += 1u;
            }
        }
    }

    for (i = 0u; i < graph->edges.size(); ++i) {
        const dom_cosmo_edge &edge = graph->edges[i];
        if (edge.src_id == 0ull || edge.dst_id == 0ull ||
            edge.src_id == edge.dst_id || edge.duration_ticks == 0ull) {
            if (out_errors) {
                out_errors->push_back("invalid_edge");
            }
            return DOM_COSMO_GRAPH_INVALID_EDGE;
        }
        if (find_entity_index(graph->entities, edge.src_id) < 0 ||
            find_entity_index(graph->entities, edge.dst_id) < 0) {
            if (out_errors) {
                out_errors->push_back("edge_missing_entity");
            }
            return DOM_COSMO_GRAPH_NOT_FOUND;
        }
    }

    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_iterate(const dom_cosmo_graph *graph,
                            u32 kind,
                            dom_cosmo_iter_fn fn,
                            void *user) {
    size_t i;
    if (!graph || !fn) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        if (kind == 0u || ent.kind == kind) {
            fn(&ent, user);
        }
    }
    return DOM_COSMO_GRAPH_OK;
}

const dom_cosmo_entity *dom_cosmo_graph_get_entity(const dom_cosmo_graph *graph, u64 id) {
    int idx;
    if (!graph || id == 0ull) {
        return 0;
    }
    idx = find_entity_index(graph->entities, id);
    if (idx < 0) {
        return 0;
    }
    return &graph->entities[(size_t)idx];
}

const dom_cosmo_edge *dom_cosmo_graph_get_edge(const dom_cosmo_graph *graph, u64 id) {
    int idx;
    if (!graph || id == 0ull) {
        return 0;
    }
    idx = find_edge_index(graph->edges, id);
    if (idx < 0) {
        return 0;
    }
    return &graph->edges[(size_t)idx];
}

u64 dom_cosmo_graph_hash(const dom_cosmo_graph *graph) {
    u64 h = 14695981039346656037ull;
    size_t i;
    if (!graph) {
        return 0ull;
    }
    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        h ^= ent.id;
        h *= 1099511628211ull;
        h ^= ent.parent_id;
        h *= 1099511628211ull;
        h ^= (u64)ent.kind;
        h *= 1099511628211ull;
    }
    for (i = 0u; i < graph->edges.size(); ++i) {
        const dom_cosmo_edge &edge = graph->edges[i];
        h ^= edge.id;
        h *= 1099511628211ull;
        h ^= edge.src_id;
        h *= 1099511628211ull;
        h ^= edge.dst_id;
        h *= 1099511628211ull;
        h ^= edge.duration_ticks;
        h *= 1099511628211ull;
        h ^= (u64)edge.cost;
        h *= 1099511628211ull;
        h ^= edge.event_table_id;
        h *= 1099511628211ull;
    }
    h ^= graph->seed;
    h *= 1099511628211ull;
    return h;
}

} // namespace dom
