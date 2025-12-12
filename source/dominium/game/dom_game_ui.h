#ifndef DOM_GAME_UI_H
#define DOM_GAME_UI_H

#include "d_ui.h"
#include "dom_game_app.h"

namespace dom {

void dom_game_ui_build_root(dui_context &ctx, GameMode mode);

void dom_game_ui_build_main_menu(dui_context &ctx);
void dom_game_ui_build_in_game_hud(dui_context &ctx);

} // namespace dom

#endif
