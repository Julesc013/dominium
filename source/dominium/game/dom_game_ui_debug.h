#ifndef DOM_GAME_UI_DEBUG_H
#define DOM_GAME_UI_DEBUG_H

#include "dom_game_app.h"

namespace dom {

void dom_game_ui_debug_update(dui_context &ctx, DomGameApp &app, d_world_hash hash);
void dom_game_ui_debug_reset(void);

} // namespace dom

#endif
