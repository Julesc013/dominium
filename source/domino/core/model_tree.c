#include "domino/model_tree.h"

#include <stdlib.h>
#include <string.h>

struct dom_tree_model {
    dom_tree_model_desc desc;
};

dom_status dom_tree_model_create(const dom_tree_model_desc* desc, dom_tree_model** out_model)
{
    dom_tree_model* model;
    dom_tree_model_desc local_desc;

    if (!out_model) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_model = NULL;

    model = (dom_tree_model*)malloc(sizeof(dom_tree_model));
    if (!model) {
        return DOM_STATUS_ERROR;
    }
    memset(model, 0, sizeof(*model));

    if (desc) {
        local_desc = *desc;
    } else {
        memset(&local_desc, 0, sizeof(local_desc));
    }
    local_desc.struct_size = sizeof(dom_tree_model_desc);
    model->desc = local_desc;

    *out_model = model;
    return DOM_STATUS_OK;
}

void dom_tree_model_destroy(dom_tree_model* model)
{
    if (!model) {
        return;
    }
    free(model);
}

dom_status dom_tree_model_get_root(dom_tree_model* model, uint32_t index, dom_tree_node_desc* out_node)
{
    (void)index;
    if (!model || !out_node) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    memset(out_node, 0, sizeof(*out_node));
    out_node->struct_size = sizeof(dom_tree_node_desc);
    out_node->struct_version = 1u;
    out_node->depth = 0u;
    out_node->child_count = 0u;
    out_node->id = "";
    out_node->label = "";
    return DOM_STATUS_OK;
}

dom_status dom_tree_model_get_child(dom_tree_model* model, const char* parent_id, uint32_t index, dom_tree_node_desc* out_node)
{
    (void)parent_id;
    (void)index;
    if (!model || !out_node) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    memset(out_node, 0, sizeof(*out_node));
    out_node->struct_size = sizeof(dom_tree_node_desc);
    out_node->struct_version = 1u;
    out_node->depth = 1u;
    out_node->child_count = 0u;
    out_node->id = "";
    out_node->label = "";
    return DOM_STATUS_OK;
}
