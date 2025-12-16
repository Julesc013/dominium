/*
FILE: include/domino/model_tree.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / model_tree
RESPONSIBILITY: Defines the public contract for `model_tree` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_MODEL_TREE_H_INCLUDED
#define DOMINO_MODEL_TREE_H_INCLUDED

#include "domino/baseline.h"
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t dom_tree_node_id;

typedef struct dom_tree_node {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_tree_node_id parent;
    char             label[128];
    uint32_t         child_count;
} dom_tree_node;

bool dom_tree_get_root(dom_core* core, const char* tree_id, dom_tree_node_id* root_out);
bool dom_tree_get_node(dom_core* core, const char* tree_id, dom_tree_node_id id, dom_tree_node* out);
bool dom_tree_get_child(dom_core* core, const char* tree_id, dom_tree_node_id parent, uint32_t index, dom_tree_node_id* child_out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MODEL_TREE_H_INCLUDED */
