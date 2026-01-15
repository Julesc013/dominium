/*
FILE: source/dominium/game/dom_game_states.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_states
RESPONSIBILITY: Implements `dom_game_states`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_game_states.h"

#include <cstdio>
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
    BootState() : m_ticks(0u), m_min_ticks(60u) {
        std::memset(m_status_text, 0, sizeof(m_status_text));
    }
    void on_enter(DomGameApp &app) {
        m_ticks = 0u;
        dom_game_ui_build_loading(app.ui_context());
        std::sprintf(m_status_text, "Loading... 0%%");
        dom_game_ui_set_loading_status(app.ui_context(), m_status_text);
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) {
        unsigned pct;
        if (m_ticks < m_min_ticks) {
            m_ticks += 1u;
        }
        pct = (m_min_ticks > 0u) ? (m_ticks * 100u / m_min_ticks) : 100u;
        if (pct > 100u) {
            pct = 100u;
        }
        std::sprintf(m_status_text, "Loading... %u%%", pct);
        if (m_ticks >= m_min_ticks) {
            app.request_state_change(GAME_STATE_MAIN_MENU);
        }
    }
private:
    u32 m_ticks;
    u32 m_min_ticks;
    char m_status_text[64];
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
    LoadingState() : m_transitioned(false), m_ticks(0u), m_min_ticks(30u) {
        std::memset(m_status_text, 0, sizeof(m_status_text));
    }

    void on_enter(DomGameApp &app) {
        m_transitioned = false;
        m_ticks = 0u;
        dom_game_ui_build_loading(app.ui_context());
        std::sprintf(m_status_text, "Loading... 0%%");
        dom_game_ui_set_loading_status(app.ui_context(), m_status_text);
    }
    void on_exit(DomGameApp &app) { (void)app; }
    void tick(DomGameApp &app) {
        unsigned pct;
        const char *phase = app.net().ready() ? "Finalizing" : "Connecting";

        if (m_transitioned) {
            return;
        }
        if (m_ticks < m_min_ticks) {
            m_ticks += 1u;
        }
        pct = (m_min_ticks > 0u) ? (m_ticks * 100u / m_min_ticks) : 100u;
        if (pct > 100u) {
            pct = 100u;
        }
        std::sprintf(m_status_text, "%s... %u%%", phase, pct);
        if (app.net().ready() && m_ticks >= m_min_ticks) {
            app.request_state_change(GAME_STATE_RUNNING);
            m_transitioned = true;
        }
    }
private:
    bool m_transitioned;
    u32 m_ticks;
    u32 m_min_ticks;
    char m_status_text[64];
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
