#ifndef DOMINIUM_GAME_EDIT_API_H_INCLUDED
#define DOMINIUM_GAME_EDIT_API_H_INCLUDED

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_game_edit_ctx_t dom_game_edit_ctx;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    const char *def_root; /* root path to game definition data/packs/mods */
} dom_game_edit_desc;

dom_game_edit_ctx *dom_game_edit_open(const dom_game_edit_desc *desc);
void               dom_game_edit_close(dom_game_edit_ctx *ctx);

/* editable entities: recipes, items, machines. For now, just list + get JSON */
int dom_game_edit_list_entities(dom_game_edit_ctx *ctx,
                                const char *kind, /* "recipe", "item", "machine" */
                                char *buf,
                                uint32_t buf_size);

int dom_game_edit_get_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  char *buf,
                                  uint32_t buf_size);

int dom_game_edit_set_entity_json(dom_game_edit_ctx *ctx,
                                  const char *kind,
                                  const char *id,
                                  const char *json);

int dom_game_edit_save(dom_game_edit_ctx *ctx);

#ifdef __cplusplus
}
#endif

#endif
