/*
FILE: source/domino/sim/_legacy/core_sim/registry_recipe.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/registry_recipe
RESPONSIBILITY: Defines internal contract for `registry_recipe`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_REGISTRY_RECIPE_H
#define DOM_REGISTRY_RECIPE_H

#include "core_types.h"
#include "core_ids.h"

typedef struct RecipeDesc {
    RecipeId     id;
    const char  *name;
    i32          base_height_m;
    i32          height_range_m;
} RecipeDesc;

typedef struct RecipeRegistry {
    RecipeDesc *recipes;
    u16         count;
    u16         capacity;
} RecipeRegistry;

void recipe_registry_init(RecipeRegistry *reg, u16 capacity);
void recipe_registry_free(RecipeRegistry *reg);
RecipeId recipe_register(RecipeRegistry *reg, const RecipeDesc *desc);
const RecipeDesc *recipe_get(const RecipeRegistry *reg, RecipeId id);

#endif /* DOM_REGISTRY_RECIPE_H */
