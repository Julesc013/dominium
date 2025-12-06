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
