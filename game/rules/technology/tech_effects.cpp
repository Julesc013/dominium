/*
FILE: game/rules/technology/tech_effects.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / technology
RESPONSIBILITY: Implements technology effects and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Effect ordering is deterministic.
*/
#include "dominium/rules/technology/tech_effects.h"

#include <string.h>

void tech_effect_registry_init(tech_effect_registry* reg,
                               tech_effect* storage,
                               u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->effects = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(tech_effect) * (size_t)capacity);
    }
}

static u32 tech_effect_find_index(const tech_effect_registry* reg,
                                  u64 tech_id,
                                  u64 target_id,
                                  int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->effects) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        const tech_effect* entry = &reg->effects[i];
        if (entry->tech_id == tech_id && entry->target_id == target_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (entry->tech_id > tech_id ||
            (entry->tech_id == tech_id && entry->target_id > target_id)) {
            break;
        }
    }
    return i;
}

int tech_effect_register(tech_effect_registry* reg,
                         u64 tech_id,
                         tech_effect_type type,
                         u64 target_id,
                         u32 flags)
{
    int found = 0;
    u32 idx;
    u32 i;
    tech_effect* entry;
    if (!reg || !reg->effects) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = tech_effect_find_index(reg, tech_id, target_id, &found);
    if (found) {
        reg->effects[idx].type = type;
        reg->effects[idx].flags = flags;
        return 0;
    }
    for (i = reg->count; i > idx; --i) {
        reg->effects[i] = reg->effects[i - 1u];
    }
    entry = &reg->effects[idx];
    entry->tech_id = tech_id;
    entry->type = type;
    entry->target_id = target_id;
    entry->flags = flags;
    reg->count += 1u;
    return 0;
}

tech_effect* tech_effect_find(tech_effect_registry* reg,
                              u64 tech_id,
                              u64 target_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->effects) {
        return 0;
    }
    idx = tech_effect_find_index(reg, tech_id, target_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->effects[idx];
}
