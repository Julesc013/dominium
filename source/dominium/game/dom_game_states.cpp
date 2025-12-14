#include "dom_game_states.h"

#include <cstring>

#include "dom_game_app.h"
#include "dom_game_ui.h"

extern "C" {
#include "domino/core/fixed.h"
}

namespace dom {

namespace {

class BootState : public GameState {
public:
    void on_enter(DomGameApp &app) {
        app.request_state_change(GAME_STATE_MAIN_MENU);
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) { (void)app; }
};

class MainMenuState : public GameState {
public:
    void on_enter(DomGameApp &app) {
        dom_game_ui_build_main_menu(app.ui_context());
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) {
        (void)app;
    }
};

class LoadingState : public GameState {
public:
    LoadingState() : m_transitioned(false) {}

    void on_enter(DomGameApp &app) {
        m_transitioned = false;
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) {
        if (!m_transitioned && app.net().ready()) {
            app.request_state_change(GAME_STATE_RUNNING);
            m_transitioned = true;
        }
    }
private:
    bool m_transitioned;
};

class RunningState : public GameState {
public:
    RunningState() {}

    void on_enter(DomGameApp &app) {
        dom_game_ui_build_in_game(app.ui_context());
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) {
        (void)app;
    }
private:
};

class PausedState : public GameState {
public:
    void on_enter(DomGameApp &app) { (void)app; }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) { (void)app; }
};

class ExitingState : public GameState {
public:
    void on_enter(DomGameApp &app) {
        app.request_exit();
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) { (void)app; }
};

} // namespace

GameState *create_state(GameStateId id) {
    switch (id) {
    case GAME_STATE_BOOT:        return new BootState();
    case GAME_STATE_MAIN_MENU:   return new MainMenuState();
    case GAME_STATE_LOADING:     return new LoadingState();
    case GAME_STATE_RUNNING:     return new RunningState();
    case GAME_STATE_PAUSED:      return new PausedState();
    case GAME_STATE_EXITING:     return new ExitingState();
    default:
        break;
    }
    return 0;
}

void destroy_state(GameState *s) {
    delete s;
}

} // namespace dom
