/*
FILE: game/rules/infrastructure/building_machine.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / infrastructure
RESPONSIBILITY: Implements building machines and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Machine ordering is deterministic.
*/
#include "dominium/rules/infrastructure/building_machine.h"

#include <string.h>

void building_machine_registry_init(building_machine_registry* reg,
                                    building_machine* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->machines = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(building_machine) * (size_t)capacity);
    }
}

static u32 building_machine_find_index(const building_machine_registry* reg,
                                       u64 building_id,
                                       int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->machines) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->machines[i].building_id == building_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->machines[i].building_id > building_id) {
            break;
        }
    }
    return i;
}

int building_machine_register(building_machine_registry* reg,
                              u64 building_id,
                              u64 type_id,
                              u64 owner_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    building_machine* entry;
    if (!reg || !reg->machines) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = building_machine_find_index(reg, building_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->machines[i] = reg->machines[i - 1u];
    }
    entry = &reg->machines[idx];
    memset(entry, 0, sizeof(*entry));
    entry->building_id = building_id;
    entry->type_id = type_id;
    entry->owner_ref = owner_ref;
    entry->production_recipe_ref = 0u;
    entry->status = MACHINE_IDLE;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    entry->production_end_tick = DOM_TIME_ACT_MAX;
    maintenance_state_init(&entry->maintenance, 100u, 20u);
    reg->count += 1u;
    return 0;
}

building_machine* building_machine_find(building_machine_registry* reg,
                                        u64 building_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->machines) {
        return 0;
    }
    idx = building_machine_find_index(reg, building_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->machines[idx];
}

int building_machine_set_recipe(building_machine_registry* reg,
                                u64 building_id,
                                u64 recipe_id)
{
    building_machine* machine = building_machine_find(reg, building_id);
    if (!machine) {
        return -1;
    }
    machine->production_recipe_ref = recipe_id;
    return 0;
}

static int building_machine_insert_store(u64* stores,
                                         u32* count,
                                         u32 max_count,
                                         u64 store_id)
{
    u32 i;
    if (!stores || !count) {
        return -1;
    }
    if (*count >= max_count) {
        return -2;
    }
    for (i = 0u; i < *count; ++i) {
        if (stores[i] == store_id) {
            return 0;
        }
        if (stores[i] > store_id) {
            break;
        }
    }
    if (i < *count) {
        u32 j;
        for (j = *count; j > i; --j) {
            stores[j] = stores[j - 1u];
        }
    }
    stores[i] = store_id;
    *count += 1u;
    return 0;
}

int building_machine_add_input_store(building_machine_registry* reg,
                                     u64 building_id,
                                     u64 store_id)
{
    building_machine* machine = building_machine_find(reg, building_id);
    if (!machine) {
        return -1;
    }
    return building_machine_insert_store(machine->input_stores,
                                         &machine->input_store_count,
                                         INFRA_MACHINE_MAX_STORES,
                                         store_id);
}

int building_machine_add_output_store(building_machine_registry* reg,
                                      u64 building_id,
                                      u64 store_id)
{
    building_machine* machine = building_machine_find(reg, building_id);
    if (!machine) {
        return -1;
    }
    return building_machine_insert_store(machine->output_stores,
                                         &machine->output_store_count,
                                         INFRA_MACHINE_MAX_STORES,
                                         store_id);
}
