/*
FILE: game/rules/infrastructure/production_chain.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / infrastructure
RESPONSIBILITY: Implements deterministic production recipes and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Recipe ordering is deterministic.
*/
#include "dominium/rules/infrastructure/production_chain.h"

#include <string.h>

void production_recipe_registry_init(production_recipe_registry* reg,
                                     production_recipe* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->recipes = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(production_recipe) * (size_t)capacity);
    }
}

static void production_recipe_sort_items(production_recipe_item* items, u32 count)
{
    u32 i;
    if (!items || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        production_recipe_item key = items[i];
        u32 j = i;
        while (j > 0u) {
            production_recipe_item prev = items[j - 1u];
            if (prev.asset_id <= key.asset_id) {
                break;
            }
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

static u32 production_recipe_find_index(const production_recipe_registry* reg,
                                        u64 recipe_id,
                                        int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->recipes) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->recipes[i].recipe_id == recipe_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->recipes[i].recipe_id > recipe_id) {
            break;
        }
    }
    return i;
}

int production_recipe_register(production_recipe_registry* reg,
                               const production_recipe* recipe)
{
    int found = 0;
    u32 idx;
    u32 i;
    production_recipe* entry;
    if (!reg || !reg->recipes || !recipe) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = production_recipe_find_index(reg, recipe->recipe_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->recipes[i] = reg->recipes[i - 1u];
    }
    entry = &reg->recipes[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *recipe;
    production_recipe_sort_items(entry->inputs, entry->input_count);
    production_recipe_sort_items(entry->outputs, entry->output_count);
    reg->count += 1u;
    return 0;
}

const production_recipe* production_recipe_find(const production_recipe_registry* reg,
                                                u64 recipe_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->recipes) {
        return 0;
    }
    idx = production_recipe_find_index(reg, recipe_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->recipes[idx];
}
