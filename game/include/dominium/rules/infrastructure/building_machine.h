/*
FILE: include/dominium/rules/infrastructure/building_machine.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / infrastructure
RESPONSIBILITY: Defines building machines and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Machine ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_INFRA_BUILDING_MACHINE_H
#define DOMINIUM_RULES_INFRA_BUILDING_MACHINE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/infrastructure/maintenance_model.h"

#ifdef __cplusplus
extern "C" {
#endif

#define INFRA_MACHINE_MAX_STORES 4u

typedef enum building_machine_status {
    MACHINE_IDLE = 0,
    MACHINE_PRODUCING = 1,
    MACHINE_HALTED = 2
} building_machine_status;

typedef struct building_machine {
    u64 building_id;
    u64 type_id;
    u64 owner_ref;
    u64 input_stores[INFRA_MACHINE_MAX_STORES];
    u32 input_store_count;
    u64 output_stores[INFRA_MACHINE_MAX_STORES];
    u32 output_store_count;
    u64 production_recipe_ref;
    maintenance_state maintenance;
    dom_act_time_t next_due_tick;
    dom_act_time_t production_end_tick;
    u64 provenance_ref;
    building_machine_status status;
} building_machine;

typedef struct building_machine_registry {
    building_machine* machines;
    u32 count;
    u32 capacity;
} building_machine_registry;

void building_machine_registry_init(building_machine_registry* reg,
                                    building_machine* storage,
                                    u32 capacity);
int building_machine_register(building_machine_registry* reg,
                              u64 building_id,
                              u64 type_id,
                              u64 owner_ref);
building_machine* building_machine_find(building_machine_registry* reg,
                                        u64 building_id);
int building_machine_set_recipe(building_machine_registry* reg,
                                u64 building_id,
                                u64 recipe_id);
int building_machine_add_input_store(building_machine_registry* reg,
                                     u64 building_id,
                                     u64 store_id);
int building_machine_add_output_store(building_machine_registry* reg,
                                      u64 building_id,
                                      u64 store_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_INFRA_BUILDING_MACHINE_H */
