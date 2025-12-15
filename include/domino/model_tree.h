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
