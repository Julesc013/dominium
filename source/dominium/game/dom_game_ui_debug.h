/*
FILE: source/dominium/game/dom_game_ui_debug.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_ui_debug
RESPONSIBILITY: Implements `dom_game_ui_debug`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_UI_DEBUG_H
#define DOM_GAME_UI_DEBUG_H

#include "dom_game_app.h"

namespace dom {

void dom_game_ui_debug_update(dui_context &ctx, DomGameApp &app, d_world_hash hash);
void dom_game_ui_debug_reset(void);

} // namespace dom

#endif
