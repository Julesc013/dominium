/*
FILE: source/dominium/game/dom_game_states.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_states
RESPONSIBILITY: Defines internal contract for `dom_game_states`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_STATES_H
#define DOM_GAME_STATES_H

#include <string>

namespace dom {

class DomGameApp;

enum GameStateId {
    GAME_STATE_BOOT = 0,
    GAME_STATE_MAIN_MENU,
    GAME_STATE_LOADING,
    GAME_STATE_RUNNING,
    GAME_STATE_PAUSED,
    GAME_STATE_EXITING
};

class GameState {
public:
    virtual ~GameState() {}
    virtual void on_enter(DomGameApp &app) = 0;
    virtual void on_exit(DomGameApp &app) = 0;
    virtual void tick(DomGameApp &app) = 0;
};

GameState *create_state(GameStateId id);
void destroy_state(GameState *s);

} // namespace dom

#endif
