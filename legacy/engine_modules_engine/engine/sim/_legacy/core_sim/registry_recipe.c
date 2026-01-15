/*
FILE: source/domino/sim/_legacy/core_sim/registry_recipe.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/registry_recipe
RESPONSIBILITY: Implements `registry_recipe`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "registry_recipe.h"

#include <stdlib.h>
#include <string.h>

void recipe_registry_init(RecipeRegistry *reg, u16 capacity)
{
    if (!reg) return;
    memset(reg, 0, sizeof(*reg));
    if (capacity > 0) {
        reg->recipes = (RecipeDesc *)malloc(sizeof(RecipeDesc) * capacity);
        if (reg->recipes) {
            reg->capacity = capacity;
        }
    }
}

void recipe_registry_free(RecipeRegistry *reg)
{
    if (!reg) return;
    if (reg->recipes) {
        free(reg->recipes);
        reg->recipes = NULL;
    }
    reg->capacity = 0;
    reg->count = 0;
}

RecipeId recipe_register(RecipeRegistry *reg, const RecipeDesc *desc)
{
    RecipeDesc *slot;
    if (!reg || !desc) return 0;
    if (reg->count >= reg->capacity) {
        u16 new_cap = (reg->capacity == 0) ? 4U : (u16)(reg->capacity * 2U);
        RecipeDesc *new_arr = (RecipeDesc *)realloc(reg->recipes, sizeof(RecipeDesc) * new_cap);
        if (!new_arr) {
            return 0;
        }
        reg->recipes = new_arr;
        reg->capacity = new_cap;
    }
    slot = &reg->recipes[reg->count];
    *slot = *desc;
    slot->id = reg->count;
    reg->count++;
    return slot->id;
}

const RecipeDesc *recipe_get(const RecipeRegistry *reg, RecipeId id)
{
    if (!reg) return NULL;
    if (id >= reg->count) return NULL;
    return &reg->recipes[id];
}
