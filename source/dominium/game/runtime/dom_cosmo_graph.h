/*
FILE: source/dominium/game/runtime/dom_cosmo_graph.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_cosmo_graph
RESPONSIBILITY: Defines deterministic cosmos graph registry (logical universe scale).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; floating-point math.
*/
#ifndef DOM_COSMO_GRAPH_H
#define DOM_COSMO_GRAPH_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

namespace dom {

enum {
    DOM_COSMO_GRAPH_OK = 0,
    DOM_COSMO_GRAPH_ERR = -1,
    DOM_COSMO_GRAPH_INVALID_ARGUMENT = -2,
    DOM_COSMO_GRAPH_DUPLICATE_ID = -3,
    DOM_COSMO_GRAPH_NOT_FOUND = -4,
    DOM_COSMO_GRAPH_INVALID_KIND = -5,
    DOM_COSMO_GRAPH_INVALID_PARENT = -6,
    DOM_COSMO_GRAPH_INVALID_EDGE = -7,
    DOM_COSMO_GRAPH_CYCLE = -8
};

enum DomCosmoEntityKind {
    DOM_COSMO_KIND_FILAMENT = 1u,
    DOM_COSMO_KIND_CLUSTER = 2u,
    DOM_COSMO_KIND_GALAXY = 3u,
    DOM_COSMO_KIND_SYSTEM = 4u
};

enum {
    DOM_COSMO_GRAPH_CONFIG_VERSION = 1u
};

struct dom_cosmo_graph_config {
    u32 struct_size;
    u32 struct_version;
    u32 max_entities;
    u32 max_edges;

    dom_cosmo_graph_config();
};

struct dom_cosmo_entity {
    u64 id;
    u64 parent_id;
    u32 kind;
    std::string stable_id;

    dom_cosmo_entity();
};

struct dom_cosmo_edge {
    u64 id;
    u64 src_id;
    u64 dst_id;
    u64 duration_ticks;
    u32 cost;
    u64 event_table_id;

    dom_cosmo_edge();
};

struct dom_cosmo_edge_params {
    u64 duration_ticks;
    u32 cost;
    u64 event_table_id;

    dom_cosmo_edge_params();
};

struct dom_cosmo_graph {
    u32 struct_size;
    u32 struct_version;
    u64 seed;
    dom_cosmo_graph_config config;
    std::vector<dom_cosmo_entity> entities;
    std::vector<dom_cosmo_edge> edges;

    dom_cosmo_graph();
};

typedef void (*dom_cosmo_iter_fn)(const dom_cosmo_entity *ent, void *user);

int dom_cosmo_graph_init(dom_cosmo_graph *graph,
                         u64 seed,
                         const dom_cosmo_graph_config *config);
int dom_cosmo_graph_add_entity(dom_cosmo_graph *graph,
                               u32 kind,
                               const char *stable_id,
                               u64 parent_id,
                               u64 *out_id);
int dom_cosmo_graph_add_travel_edge(dom_cosmo_graph *graph,
                                    u64 src_id,
                                    u64 dst_id,
                                    const dom_cosmo_edge_params *params,
                                    u64 *out_edge_id);
int dom_cosmo_graph_validate(const dom_cosmo_graph *graph,
                             std::vector<std::string> *out_errors);
int dom_cosmo_graph_iterate(const dom_cosmo_graph *graph,
                            u32 kind,
                            dom_cosmo_iter_fn fn,
                            void *user);
const dom_cosmo_entity *dom_cosmo_graph_get_entity(const dom_cosmo_graph *graph, u64 id);
const dom_cosmo_edge *dom_cosmo_graph_get_edge(const dom_cosmo_graph *graph, u64 id);
u64 dom_cosmo_graph_hash(const dom_cosmo_graph *graph);

} // namespace dom

#endif /* DOM_COSMO_GRAPH_H */
