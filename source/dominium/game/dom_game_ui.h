#ifndef DOM_GAME_UI_H
#define DOM_GAME_UI_H

#include "ui/d_ui.h"
#include "dom_game_app.h"

namespace dom {

class DomGameApp;

void dom_game_ui_set_app(DomGameApp *app);

void dom_game_ui_build_root(dui_context &ctx, GameMode mode);

void dom_game_ui_build_main_menu(dui_context &ctx);
void dom_game_ui_build_in_game(dui_context &ctx);
void dom_game_ui_set_status(dui_context &ctx, const char *text);

dui_widget *dom_game_ui_get_start_button(void);
dui_widget *dom_game_ui_get_place_button(void);
dui_widget *dom_game_ui_get_instance_label(void);
dui_widget *dom_game_ui_get_remaining_label(void);
dui_widget *dom_game_ui_get_inventory_label(void);

int dom_game_ui_try_click(dui_context &ctx, int x, int y);

} // namespace dom

#endif
