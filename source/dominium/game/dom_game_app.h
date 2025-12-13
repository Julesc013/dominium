#ifndef DOM_GAME_APP_H
#define DOM_GAME_APP_H

#include <string>
#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dom_compat.h"
#include "dom_game_states.h"
#include "dom_game_camera.h"

extern "C" {
#include "view/d_view.h"
#include "ui/d_ui.h"
#include "sim/d_sim.h"
#include "sim/d_sim_hash.h"
#include "struct/d_struct.h"
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
    bool        dev_mode;
    bool        deterministic_test;
    std::string replay_record_path;
    std::string replay_play_path;
};

class DomGameApp {
public:
    DomGameApp();
    ~DomGameApp();

    bool init_from_cli(const GameConfig &cfg);
    void run();
    void shutdown();

    void request_state_change(GameStateId next);
    void request_exit();
    void spawn_demo_blueprint();
    void update_demo_hud();

    DomSession&       session()       { return m_session; }
    const DomSession& session() const { return m_session; }
    const GameCamera& camera() const { return m_camera; }

    dui_context& ui_context() { return m_ui_ctx; }

    bool dev_mode() const { return m_dev_mode; }
    bool debug_panel_visible() const { return m_show_debug_panel; }
    void set_debug_panel_visible(bool v) { m_show_debug_panel = v; }
    void toggle_debug_panel() { m_show_debug_panel = !m_show_debug_panel; }
    u32 determinism_mode() const { return m_detmode; }

private:
    bool init_paths(const GameConfig &cfg);
    bool load_instance(const GameConfig &cfg);
    bool evaluate_compatibility(const GameConfig &cfg);
    bool init_session(const GameConfig &cfg);
    bool init_views_and_ui(const GameConfig &cfg);

    void main_loop();
    void tick_fixed();
    void render_frame();
    void process_input_events();
    void update_camera();
    void update_debug_panel();

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

    GameCamera   m_camera;
    int          m_mouse_x;
    int          m_mouse_y;
    d_struct_instance_id m_last_struct_id;
    bool         m_dev_mode;
    u32          m_detmode;
    d_world_hash m_last_hash;
    std::string  m_replay_record_path;
    std::string  m_replay_play_path;
    bool         m_show_debug_panel;

    char         m_hud_instance_text[128];
    char         m_hud_remaining_text[128];
    char         m_hud_inventory_text[128];
};

bool parse_game_cli_args(int argc, char **argv, GameConfig &cfg);
void init_default_game_config(GameConfig &cfg);

} // namespace dom

#endif
