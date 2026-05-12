/*
FILE: source/dominium/game/dom_game_ui.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_ui
RESPONSIBILITY: Defines internal contract for `dom_game_ui`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_UI_H
#define DOM_GAME_UI_H

#include "ui/d_ui.h"
#include "dom_game_app.h"

namespace dom {

class DomGameApp;

void dom_game_ui_set_app(DomGameApp *app);

void dom_game_ui_build_root(dui_context &ctx, GameMode mode);

void dom_game_ui_build_main_menu(dui_context &ctx);
void dom_game_ui_build_splash(dui_context &ctx);
void dom_game_ui_build_loading(dui_context &ctx);
void dom_game_ui_build_session_loading(dui_context &ctx);
void dom_game_ui_build_in_game(dui_context &ctx);
void dom_game_ui_set_status(dui_context &ctx, const char *text);
void dom_game_ui_set_menu_player(dui_context &ctx, const char *text);
void dom_game_ui_set_menu_server(dui_context &ctx, const char *text);
void dom_game_ui_set_menu_error(dui_context &ctx, const char *text);
void dom_game_ui_set_loading_status(dui_context &ctx, const char *text);
void dom_game_ui_set_loading_progress(dui_context &ctx, const char *text);
void dom_game_ui_set_loading_detail_content(dui_context &ctx, const char *text);
void dom_game_ui_set_loading_detail_net(dui_context &ctx, const char *text);
void dom_game_ui_set_loading_detail_world(dui_context &ctx, const char *text);

dui_widget *dom_game_ui_get_start_button(void);
dui_widget *dom_game_ui_get_place_button(void);
dui_widget *dom_game_ui_get_instance_label(void);
dui_widget *dom_game_ui_get_remaining_label(void);
dui_widget *dom_game_ui_get_inventory_label(void);

int dom_game_ui_try_click(dui_context &ctx, int x, int y);

} // namespace dom

#endif
