#include <string.h>
#include "core_internal.h"

static void dom_copy_string(char* dst, size_t cap, const char* src)
{
    size_t len;

    if (!dst || cap == 0) {
        return;
    }

    if (!src) {
        dst[0] = '\0';
        return;
    }

    len = strlen(src);
    if (len >= cap) {
        len = cap - 1;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

bool dom_tree_get_root(dom_core* core, const char* tree_id, dom_tree_node_id* root_out)
{
    (void)core;

    if (!tree_id || !root_out) {
        return false;
    }

    if (strcmp(tree_id, "empty_tree") != 0) {
        return false;
    }

    *root_out = 1;
    return true;
}

bool dom_tree_get_node(dom_core* core, const char* tree_id, dom_tree_node_id id, dom_tree_node* out)
{
    (void)core;

    if (!tree_id || !out) {
        return false;
    }

    if (strcmp(tree_id, "empty_tree") != 0) {
        return false;
    }

    if (id != 1) {
        return false;
    }

    memset(out, 0, sizeof(*out));
    out->struct_size = sizeof(dom_tree_node);
    out->struct_version = 1;
    out->parent = 0;
    dom_copy_string(out->label, sizeof(out->label), "root");
    out->child_count = 0;
    return true;
}

bool dom_tree_get_child(dom_core* core, const char* tree_id, dom_tree_node_id parent, uint32_t index, dom_tree_node_id* child_out)
{
    (void)core;
    (void)parent;
    (void)index;
    (void)child_out;

    if (!tree_id) {
        return false;
    }

    if (strcmp(tree_id, "empty_tree") != 0) {
        return false;
    }

    return false;
}
