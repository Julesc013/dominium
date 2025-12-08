#ifndef DOMINO_MODEL_TREE_H_INCLUDED
#define DOMINO_MODEL_TREE_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_tree_model dom_tree_model;

typedef struct dom_tree_node_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* id;
    const char* label;
    uint32_t    depth;
    uint32_t    child_count;
} dom_tree_node_desc;

typedef struct dom_tree_model_desc {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t root_count;
} dom_tree_model_desc;

dom_status dom_tree_model_create(const dom_tree_model_desc* desc, dom_tree_model** out_model);
void       dom_tree_model_destroy(dom_tree_model* model);
dom_status dom_tree_model_get_root(dom_tree_model* model, uint32_t index, dom_tree_node_desc* out_node);
dom_status dom_tree_model_get_child(dom_tree_model* model, const char* parent_id, uint32_t index, dom_tree_node_desc* out_node);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_MODEL_TREE_H_INCLUDED */
