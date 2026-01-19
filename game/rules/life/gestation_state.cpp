/*
FILE: game/core/life/gestation_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements gestation state registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Gestation ordering is deterministic.
*/
#include "dominium/life/gestation_state.h"

#include <string.h>

void life_gestation_registry_init(life_gestation_registry* reg,
                                  life_gestation_state* storage,
                                  u32 capacity,
                                  u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_gestation_state) * (size_t)capacity);
    }
}

static int life_parent_sets_equal(const life_gestation_state* state,
                                  const u64* parent_ids,
                                  u32 parent_count)
{
    u32 i;
    if (!state || !parent_ids) {
        return 0;
    }
    if (state->parent_count != parent_count) {
        return 0;
    }
    for (i = 0u; i < parent_count; ++i) {
        if (state->parent_ids[i] != parent_ids[i]) {
            return 0;
        }
    }
    return 1;
}

life_gestation_state* life_gestation_find_active(life_gestation_registry* reg,
                                                 const u64* parent_ids,
                                                 u32 parent_count)
{
    u32 i;
    if (!reg || !reg->states) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        life_gestation_state* state = &reg->states[i];
        if (state->status != LIFE_GESTATION_ACTIVE) {
            continue;
        }
        if (life_parent_sets_equal(state, parent_ids, parent_count)) {
            return state;
        }
    }
    return 0;
}

int life_gestation_append(life_gestation_registry* reg,
                          const life_gestation_state* state,
                          u64* out_id)
{
    life_gestation_state* slot;
    if (!reg || !state || !reg->states) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    slot = &reg->states[reg->count++];
    *slot = *state;
    slot->gestation_id = reg->next_id++;
    if (out_id) {
        *out_id = slot->gestation_id;
    }
    return 0;
}

life_gestation_state* life_gestation_find_by_id(life_gestation_registry* reg,
                                                u64 gestation_id)
{
    u32 i;
    if (!reg || !reg->states) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->states[i].gestation_id == gestation_id) {
            return &reg->states[i];
        }
    }
    return 0;
}
