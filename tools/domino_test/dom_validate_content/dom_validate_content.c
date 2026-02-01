/*
FILE: tools/domino_test/dom_validate_content/dom_validate_content.c
MODULE: Repository
LAYER / SUBSYSTEM: tools/domino_test/dom_validate_content
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "registry_material.h"
#include "registry_recipe.h"

int main(int argc, char **argv)
{
    MaterialRegistry mats;
    RecipeRegistry recipes;
    MaterialDesc test_mat;
    RecipeDesc test_recipe;
    (void)argc;
    (void)argv;

    material_registry_init(&mats, 2);
    recipe_registry_init(&recipes, 2);

    test_mat.name = "probe";
    test_mat.density = fix32_from_int(1000);
    test_mat.hardness = fix32_from_int(1);
    test_mat.melting_point = fix32_from_int(500);
    test_mat.boiling_point = fix32_from_int(900);
    material_register(&mats, &test_mat);

    test_recipe.name = "validate_default";
    test_recipe.base_height_m = 10;
    test_recipe.height_range_m = 5;
    recipe_register(&recipes, &test_recipe);

    printf("Validation stubs loaded %u material(s), %u recipe(s)\n",
           (unsigned int)mats.count,
           (unsigned int)recipes.count);

    material_registry_free(&mats);
    recipe_registry_free(&recipes);
    return 0;
}
