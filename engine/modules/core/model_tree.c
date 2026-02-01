/*
FILE: source/domino/core/model_tree.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/model_tree
RESPONSIBILITY: Implements `model_tree`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include "core_internal.h"

#define DOM_PACKAGES_TREE_ROOT_ID      1u
#define DOM_PACKAGES_TREE_KIND_BASE    0x00000100u
#define DOM_PACKAGES_TREE_PACKAGE_BASE 0x00010000u

typedef struct dom_tree_kind_entry {
    dom_package_kind kind;
    const char*      label;
} dom_tree_kind_entry;

static const dom_tree_kind_entry g_package_kind_nodes[] = {
    { DOM_PKG_KIND_UNKNOWN, "Unknown" },
    { DOM_PKG_KIND_MOD,     "Mods" },
    { DOM_PKG_KIND_CONTENT, "Content" },
    { DOM_PKG_KIND_PRODUCT, "Products" },
    { DOM_PKG_KIND_TOOL,    "Tools" },
    { DOM_PKG_KIND_PACK,    "Packs" }
};

#define DOM_KIND_NODE_COUNT (sizeof(g_package_kind_nodes) / sizeof(g_package_kind_nodes[0]))

static int dom_tree_is_packages_tree(const char* tree_id)
{
    if (!tree_id) {
        return 0;
    }
    return strcmp(tree_id, "packages_tree") == 0;
}

static dom_package_record* dom_tree_find_package(dom_core* core, dom_package_id id)
{
    uint32_t i;

    if (!core || id == 0u) {
        return NULL;
    }

    for (i = 0u; i < core->package_count; ++i) {
        if (core->packages[i].info.id == id) {
            return &core->packages[i];
        }
    }
    return NULL;
}

static uint32_t dom_tree_count_kind(dom_core* core, dom_package_kind kind)
{
    uint32_t i;
    uint32_t count;

    if (!core) {
        return 0u;
    }

    count = 0u;
    for (i = 0u; i < core->package_count; ++i) {
        if (core->packages[i].info.kind == kind) {
            count += 1u;
        }
    }
    return count;
}

static uint32_t dom_tree_kind_index(dom_package_kind kind)
{
    uint32_t i;

    for (i = 0u; i < (uint32_t)DOM_KIND_NODE_COUNT; ++i) {
        if (g_package_kind_nodes[i].kind == kind) {
            return i;
        }
    }
    return 0u;
}

bool dom_tree_get_root(dom_core* core, const char* tree_id, dom_tree_node_id* root_out)
{
    (void)core;

    if (!root_out || !dom_tree_is_packages_tree(tree_id)) {
        return false;
    }

    *root_out = DOM_PACKAGES_TREE_ROOT_ID;
    return true;
}

bool dom_tree_get_node(dom_core* core, const char* tree_id, dom_tree_node_id id, dom_tree_node* out)
{
    uint32_t kind_index;

    if (!core || !tree_id || !out) {
        return false;
    }
    if (!dom_tree_is_packages_tree(tree_id)) {
        return false;
    }

    memset(out, 0, sizeof(*out));
    out->struct_size = sizeof(dom_tree_node);
    out->struct_version = 1;

    if (id == DOM_PACKAGES_TREE_ROOT_ID) {
        out->parent = 0u;
        dom_copy_string(out->label, sizeof(out->label), "Packages");
        out->child_count = (uint32_t)DOM_KIND_NODE_COUNT;
        return true;
    }

    if (id >= DOM_PACKAGES_TREE_KIND_BASE &&
        id < DOM_PACKAGES_TREE_KIND_BASE + (dom_tree_node_id)DOM_KIND_NODE_COUNT) {
        kind_index = (uint32_t)(id - DOM_PACKAGES_TREE_KIND_BASE);
        out->parent = DOM_PACKAGES_TREE_ROOT_ID;
        dom_copy_string(out->label, sizeof(out->label), g_package_kind_nodes[kind_index].label);
        out->child_count = dom_tree_count_kind(core, g_package_kind_nodes[kind_index].kind);
        return true;
    }

    if (id >= DOM_PACKAGES_TREE_PACKAGE_BASE) {
        dom_package_id      pkg_id;
        dom_package_record* rec;

        pkg_id = (dom_package_id)(id - DOM_PACKAGES_TREE_PACKAGE_BASE);
        rec = dom_tree_find_package(core, pkg_id);
        if (!rec) {
            return false;
        }

        kind_index = dom_tree_kind_index(rec->info.kind);
        out->parent = DOM_PACKAGES_TREE_KIND_BASE + kind_index;
        dom_copy_string(out->label, sizeof(out->label), rec->info.name);
        out->child_count = 0u;
        return true;
    }

    return false;
}

bool dom_tree_get_child(dom_core* core,
                        const char* tree_id,
                        dom_tree_node_id parent,
                        uint32_t index,
                        dom_tree_node_id* child_out)
{
    uint32_t i;
    uint32_t match_index;

    if (!core || !tree_id || !child_out) {
        return false;
    }
    if (!dom_tree_is_packages_tree(tree_id)) {
        return false;
    }

    if (parent == DOM_PACKAGES_TREE_ROOT_ID) {
        if (index >= (uint32_t)DOM_KIND_NODE_COUNT) {
            return false;
        }
        *child_out = DOM_PACKAGES_TREE_KIND_BASE + index;
        return true;
    }

    if (parent >= DOM_PACKAGES_TREE_KIND_BASE &&
        parent < DOM_PACKAGES_TREE_KIND_BASE + (dom_tree_node_id)DOM_KIND_NODE_COUNT) {
        uint32_t         kind_index;
        dom_package_kind kind;

        kind_index = (uint32_t)(parent - DOM_PACKAGES_TREE_KIND_BASE);
        kind = g_package_kind_nodes[kind_index].kind;

        match_index = 0u;
        for (i = 0u; i < core->package_count; ++i) {
            if (core->packages[i].info.kind != kind) {
                continue;
            }
            if (match_index == index) {
                *child_out = DOM_PACKAGES_TREE_PACKAGE_BASE + core->packages[i].info.id;
                return true;
            }
            match_index += 1u;
        }
        return false;
    }

    return false;
}
