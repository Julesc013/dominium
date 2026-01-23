/*
FILE: include/domino/topology.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / topology
RESPONSIBILITY: Defines the topology DAG interface and read-only traversal.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Traversal order and query results are deterministic.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_TOPOLOGY_H
#define DOMINO_TOPOLOGY_H

#include "domino/core/types.h"
#include "domino/domain.h"
#include "domino/representation.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque topology container. */
typedef struct dom_topology dom_topology;

/* Opaque topology node handle. */
typedef struct dom_topology_node dom_topology_node;

/* dom_topology_node_id: Stable identifier for a topology node. */
typedef u64 dom_topology_node_id;

/* dom_topology_node_ref: Stable, versioned node reference. */
typedef struct dom_topology_node_ref {
    dom_topology_node_id id;
    u32                  version;
} dom_topology_node_ref;

/* dom_topology_trait_id: Data-defined trait identifier. */
typedef u64 dom_topology_trait_id;

/* dom_topology_trait_set_view: Read-only view of sorted trait ids. */
typedef struct dom_topology_trait_set_view {
    const dom_topology_trait_id* ids;
    u32                          count;
} dom_topology_trait_set_view;

/* Purpose: Resolve a topology node handle from a stable node reference. */
const dom_topology_node* dom_topology_resolve_node(const dom_topology* topo,
                                                   dom_topology_node_ref ref);

/* Purpose: Get the stable node reference for a handle. */
dom_topology_node_ref dom_topology_node_ref_of(const dom_topology_node* node);

/* Purpose: Get parent node handle (NULL if root). */
const dom_topology_node* dom_topology_get_parent(const dom_topology* topo,
                                                 const dom_topology_node* node);

/* Purpose: Get child nodes (stable deterministic order). */
u32 dom_topology_get_children(const dom_topology* topo,
                              const dom_topology_node* node,
                              const dom_topology_node** out_nodes,
                              u32 max_out);

/* Purpose: Query nodes by trait id (deterministic order). */
u32 dom_topology_query_by_trait(const dom_topology* topo,
                                dom_topology_trait_id trait_id,
                                dom_topology_node_ref* out_nodes,
                                u32 max_out);

/* Purpose: Query node traits (deterministic order). */
u32 dom_topology_node_traits(const dom_topology* topo,
                             const dom_topology_node* node,
                             dom_topology_trait_id* out_traits,
                             u32 max_out);

/* Purpose: Resolve domain volumes attached to a node (deterministic order). */
u32 dom_topology_resolve_domain_volumes(const dom_topology* topo,
                                        const dom_topology_node* node,
                                        dom_domain_volume_ref* out_domains,
                                        u32 max_out);

/* Purpose: Query representation tier metadata for a node at a given LOD. */
int dom_topology_node_representation(const dom_topology* topo,
                                     const dom_topology_node* node,
                                     u32 lod_index,
                                     dom_representation_meta* out_meta);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_TOPOLOGY_H */
