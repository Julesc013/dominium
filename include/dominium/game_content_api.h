#ifndef DOMINIUM_GAME_CONTENT_API_H
#define DOMINIUM_GAME_CONTENT_API_H

#include "domino/dmachine.h"
#include "domino/drecipe.h"
#include "domino/dresearch.h"
#include "domino/dblueprint.h"
#include "domino/dmatter.h"

#ifdef __cplusplus
extern "C" {
#endif

MachineTypeId dom_game_register_machine_type(const MachineType *def);
RecipeId      dom_game_register_recipe(const Recipe *def);
TechId        dom_game_register_tech(const Tech *def);

BlueprintId   dom_game_create_blueprint(const char *name, U32 elem_capacity);
BlueprintElementId dom_game_blueprint_add_elem(BlueprintId id, const BlueprintElement *elem);
void          dom_game_blueprint_generate_jobs(BlueprintId id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_GAME_CONTENT_API_H */
