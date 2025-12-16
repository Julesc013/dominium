/*
FILE: include/dominium/game_edit_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / game_edit_api
RESPONSIBILITY: Defines the public contract for `game_edit_api` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_GAME_EDIT_API_H_INCLUDED
#define DOMINIUM_GAME_EDIT_API_H_INCLUDED

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_game_edit_ctx: Public type used by `game_edit_api`. */
typedef struct dom_game_edit_ctx_t dom_game_edit_ctx;

/* dom_game_edit_desc: Public type used by `game_edit_api`. */
typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *def_root; /* root path to game definition data/packs/mods */
} dom_game_edit_desc;

/* Purpose: Open game edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dom_game_edit_ctx *dom_game_edit_open(const dom_game_edit_desc *desc);
/* Purpose: Close game edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void               dom_game_edit_close(dom_game_edit_ctx *ctx);

/* editable entities: recipes, items, machines. For now, just list + get JSON */
int dom_game_edit_list_entities(dom_game_edit_ctx *ctx,
                                const char *kind, /* "recipe", "item", "machine" */
                                char *buf,
                                uint32_t buf_size);

/* Purpose: Json dom game edit get entity.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_edit_get_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  char *buf,
                                  uint32_t buf_size);

/* Purpose: Json dom game edit set entity.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_edit_set_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  const char *json);

/* Purpose: Save game edit.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int dom_game_edit_save(dom_game_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
