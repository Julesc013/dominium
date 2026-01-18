/*
FILE: include/dominium/rules/infrastructure/production_chain.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / infrastructure
RESPONSIBILITY: Defines deterministic production recipes and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Recipe ordering is deterministic.
*/
#ifndef DOMINIUM_RULES_INFRA_PRODUCTION_CHAIN_H
#define DOMINIUM_RULES_INFRA_PRODUCTION_CHAIN_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define INFRA_RECIPE_MAX_INPUTS 8u
#define INFRA_RECIPE_MAX_OUTPUTS 8u

typedef struct production_recipe_item {
    u64 asset_id;
    u32 qty;
} production_recipe_item;

typedef struct production_recipe {
    u64 recipe_id;
    production_recipe_item inputs[INFRA_RECIPE_MAX_INPUTS];
    u32 input_count;
    production_recipe_item outputs[INFRA_RECIPE_MAX_OUTPUTS];
    u32 output_count;
    u32 duration_act;
} production_recipe;

typedef struct production_recipe_registry {
    production_recipe* recipes;
    u32 count;
    u32 capacity;
} production_recipe_registry;

void production_recipe_registry_init(production_recipe_registry* reg,
                                     production_recipe* storage,
                                     u32 capacity);
int production_recipe_register(production_recipe_registry* reg,
                               const production_recipe* recipe);
const production_recipe* production_recipe_find(const production_recipe_registry* reg,
                                                u64 recipe_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_INFRA_PRODUCTION_CHAIN_H */
