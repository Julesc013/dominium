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
