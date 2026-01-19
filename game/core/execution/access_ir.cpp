/*
FILE: game/core/execution/access_ir.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Access IR set helpers.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Deterministic append ordering only.
*/
#include "dominium/execution/access_ir.h"

void dom_access_set_init(dom_access_set *set, dom_access_decl *storage, u32 capacity)
{
    if (!set) {
        return;
    }
    set->items = storage;
    set->count = 0u;
    set->capacity = capacity;
}

void dom_access_set_clear(dom_access_set *set)
{
    if (!set) {
        return;
    }
    set->count = 0u;
}

int dom_access_set_add(dom_access_set *set, u64 resource_id, dom_access_mode mode)
{
    if (!set || !set->items) {
        return -1;
    }
    if (resource_id == 0u || mode == 0) {
        return -2;
    }
    if (set->count >= set->capacity) {
        return -3;
    }
    set->items[set->count].resource_id = resource_id;
    set->items[set->count].mode = mode;
    set->count += 1u;
    return 0;
}
