#ifndef DOM_GAME_APP_H
#define DOM_GAME_APP_H

#include <string>
#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dom_compat.h"

extern "C" {
#include "d_view.h"
#include "d_ui.h"
#include "d_sim.h"
}

namespace dom {

enum GameMode {
    GAME_MODE_GUI = 0,
    GAME_MODE_TUI,
    GAME_MODE_HEADLESS
};

enum ServerMode {
    SERVER_OFF = 0,
    SERVER_LISTEN,
    SERVER_DEDICATED
};

struct GameConfig {
    std::string dominium_home;
    std::string instance_id;

    GameMode    mode;
    ServerMode  server_mode;

    bool        demo_mode;

    std::string platform_backend;
    std::string gfx_backend;

    unsigned    tick_rate_hz;   /* e.g. 60; 0 = default */
};

enum GameStateId;
class GameState;

class DomGameApp {
public:
    DomGameApp();
    ~DomGameApp();

    bool init_from_cli(const GameConfig &cfg);
    void run();
    void shutdown();

    void request_state_change(GameStateId next);
    void request_exit();

    DomSession&       session()       { return m_session; }
    const DomSession& session() const { return m_session; }

    dui_context& ui_context() { return m_ui_ctx; }

private:
    bool init_paths(const GameConfig &cfg);
    bool load_instance(const GameConfig &cfg);
    bool evaluate_compatibility(const GameConfig &cfg);
    bool init_session(const GameConfig &cfg);
    bool init_views_and_ui(const GameConfig &cfg);

    void main_loop();
    void tick_fixed();
    void render_frame();

    void change_state(GameStateId next);

private:
    Paths        m_paths;
    InstanceInfo m_instance;
    DomSession   m_session;

    GameMode     m_mode;
    ServerMode   m_server_mode;
    bool         m_demo_mode;

    bool         m_compat_read_only;
    bool         m_compat_limited;
    unsigned     m_tick_rate_hz;

    d_view_id    m_main_view_id;
    dui_context  m_ui_ctx;

    GameStateId  m_state_id;
    GameState   *m_state;

    bool         m_running;
};

bool parse_game_cli_args(int argc, char **argv, GameConfig &cfg);
void init_default_game_config(GameConfig &cfg);

} // namespace dom

#endif
