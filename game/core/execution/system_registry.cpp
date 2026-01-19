/*
FILE: game/core/execution/system_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Deterministic system registry implementation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Stable ordering by system_id and deterministic emission order.
*/
#include "system_registry.h"
#include "work_graph_builder.h"
#include "access_set_builder.h"

static int dom_system_registry_find_index(const dom_system_registry* registry, u64 system_id, u32* out_index)
{
    u32 i;
    if (!registry) {
        return -1;
    }
    for (i = 0u; i < registry->count; ++i) {
        if (registry->entries[i].system_id == system_id) {
            if (out_index) {
                *out_index = i;
            }
            return 0;
        }
    }
    return -2;
}

void dom_system_registry_init(dom_system_registry* registry,
                              dom_system_entry* entry_storage,
                              u32 entry_capacity)
{
    if (!registry) {
        return;
    }
    registry->entries = entry_storage;
    registry->count = 0u;
    registry->capacity = entry_capacity;
}

void dom_system_registry_reset(dom_system_registry* registry)
{
    if (!registry) {
        return;
    }
    registry->count = 0u;
}

int dom_system_registry_register(dom_system_registry* registry, ISimSystem* system)
{
    u32 insert_at;
    u32 i;
    u64 system_id;
    if (!registry || !system) {
        return -1;
    }
    if (!registry->entries || registry->capacity == 0u) {
        return -2;
    }
    if (registry->count >= registry->capacity) {
        return -3;
    }
    system_id = system->system_id();
    if (dom_system_registry_find_index(registry, system_id, (u32*)0) == 0) {
        return -4;
    }
    insert_at = 0u;
    while (insert_at < registry->count &&
           registry->entries[insert_at].system_id < system_id) {
        ++insert_at;
    }
    for (i = registry->count; i > insert_at; --i) {
        registry->entries[i] = registry->entries[i - 1u];
    }
    registry->entries[insert_at].system = system;
    registry->entries[insert_at].system_id = system_id;
    registry->entries[insert_at].enabled = 1;
    registry->entries[insert_at].fidelity_tier = DOM_FIDELITY_MACRO;
    registry->entries[insert_at].budget_hint = 0u;
    registry->count += 1u;
    return 0;
}

int dom_system_registry_set_enabled(dom_system_registry* registry, u64 system_id, d_bool enabled)
{
    u32 index;
    if (dom_system_registry_find_index(registry, system_id, &index) != 0) {
        return -1;
    }
    registry->entries[index].enabled = enabled ? 1 : 0;
    return 0;
}

int dom_system_registry_set_fidelity(dom_system_registry* registry, u64 system_id, dom_fidelity_tier tier)
{
    u32 index;
    if (dom_system_registry_find_index(registry, system_id, &index) != 0) {
        return -1;
    }
    registry->entries[index].fidelity_tier = tier;
    return 0;
}

int dom_system_registry_set_budget_hint(dom_system_registry* registry, u64 system_id, u32 hint)
{
    u32 index;
    if (dom_system_registry_find_index(registry, system_id, &index) != 0) {
        return -1;
    }
    registry->entries[index].budget_hint = hint;
    return 0;
}

dom_act_time_t dom_system_registry_next_due_tick(const dom_system_registry* registry)
{
    u32 i;
    dom_act_time_t next_due = DOM_TIME_ACT_MAX;
    if (!registry) {
        return DOM_TIME_ACT_MAX;
    }
    for (i = 0u; i < registry->count; ++i) {
        dom_act_time_t due;
        if (!registry->entries[i].enabled || !registry->entries[i].system) {
            continue;
        }
        due = registry->entries[i].system->get_next_due_tick();
        if (due < next_due) {
            next_due = due;
        }
    }
    return next_due;
}

int dom_system_registry_emit(dom_system_registry* registry,
                             dom_act_time_t act_now,
                             dom_act_time_t act_target,
                             dom_work_graph_builder* graph_builder,
                             dom_access_set_builder* access_builder)
{
    u32 i;
    if (!registry || !graph_builder || !access_builder) {
        return -1;
    }
    for (i = 0u; i < registry->count; ++i) {
        dom_system_entry* entry = &registry->entries[i];
        if (!entry->enabled || !entry->system) {
            continue;
        }
        entry->system->set_budget_hint(entry->budget_hint);
        entry->system->degrade(entry->fidelity_tier, DOM_SYSTEM_DEGRADE_REGISTRY);
        if (entry->system->emit_tasks(act_now, act_target, graph_builder, access_builder) != 0) {
            return -2;
        }
    }
    return 0;
}

u32 dom_system_registry_count(const dom_system_registry* registry)
{
    if (!registry) {
        return 0u;
    }
    return registry->count;
}

u64 dom_system_registry_system_id_at(const dom_system_registry* registry, u32 index)
{
    if (!registry || index >= registry->count) {
        return 0u;
    }
    return registry->entries[index].system_id;
}
