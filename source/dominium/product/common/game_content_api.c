#include "dominium/game_content_api.h"

MachineTypeId dom_game_register_machine_type(const MachineType *def)
{
    return dmachine_type_register(def);
}

RecipeId dom_game_register_recipe(const Recipe *def)
{
    return drecipe_register(def);
}

TechId dom_game_register_tech(const Tech *def)
{
    return dresearch_register_tech(def);
}

BlueprintId dom_game_create_blueprint(const char *name, U32 elem_capacity)
{
    return dblueprint_create(name, elem_capacity);
}

BlueprintElementId dom_game_blueprint_add_elem(BlueprintId id, const BlueprintElement *elem)
{
    return dblueprint_add_element(id, elem);
}

void dom_game_blueprint_generate_jobs(BlueprintId id)
{
    dblueprint_generate_jobs(id);
}
