/*
FILE: include/dominium/game_content_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / game_content_api
RESPONSIBILITY: Defines the public contract for `game_content_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
