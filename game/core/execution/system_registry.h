/*
FILE: game/core/execution/system_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Deterministic system registry for Work IR emission.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Stable system ordering by system_id.
*/
#ifndef DOMINIUM_CORE_EXECUTION_SYSTEM_REGISTRY_H
#define DOMINIUM_CORE_EXECUTION_SYSTEM_REGISTRY_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/fidelity.h"
#include "system_iface.h"

enum dom_system_degrade_reason {
    DOM_SYSTEM_DEGRADE_REGISTRY = 1,
    DOM_SYSTEM_DEGRADE_LAW = 2,
    DOM_SYSTEM_DEGRADE_BUDGET = 3
};

typedef struct dom_system_entry {
    ISimSystem*      system;
    u64              system_id;
    d_bool           enabled;
    dom_fidelity_tier fidelity_tier;
    u32              budget_hint;
} dom_system_entry;

typedef struct dom_system_registry {
    dom_system_entry* entries;
    u32               count;
    u32               capacity;
} dom_system_registry;

void dom_system_registry_init(dom_system_registry* registry,
                              dom_system_entry* entry_storage,
                              u32 entry_capacity);

void dom_system_registry_reset(dom_system_registry* registry);

int dom_system_registry_register(dom_system_registry* registry, ISimSystem* system);
int dom_system_registry_set_enabled(dom_system_registry* registry, u64 system_id, d_bool enabled);
int dom_system_registry_set_fidelity(dom_system_registry* registry, u64 system_id, dom_fidelity_tier tier);
int dom_system_registry_set_budget_hint(dom_system_registry* registry, u64 system_id, u32 hint);

dom_act_time_t dom_system_registry_next_due_tick(const dom_system_registry* registry);

int dom_system_registry_emit(dom_system_registry* registry,
                             dom_act_time_t act_now,
                             dom_act_time_t act_target,
                             struct dom_work_graph_builder* graph_builder,
                             struct dom_access_set_builder* access_builder);

u32 dom_system_registry_count(const dom_system_registry* registry);
u64 dom_system_registry_system_id_at(const dom_system_registry* registry, u32 index);

#endif /* DOMINIUM_CORE_EXECUTION_SYSTEM_REGISTRY_H */
