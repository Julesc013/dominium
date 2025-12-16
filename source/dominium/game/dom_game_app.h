/*
FILE: source/dominium/game/dom_game_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_app
RESPONSIBILITY: Implements `dom_game_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_APP_H
#define DOM_GAME_APP_H

#include <string>
#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dom_compat.h"
#include "dom_game_states.h"
#include "dom_game_camera.h"
#include "dom_game_tools_build.h"
#include "dom_game_net.h"

extern "C" {
#include "view/d_view.h"
#include "ui/d_ui.h"
#include "sim/d_sim.h"
#include "sim/d_sim_hash.h"
#include "core/d_org.h"
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
    std::string connect_addr;    /* client: addr[:port] */
    unsigned    net_port;        /* host/listen port */

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
    void set_last_struct_id(d_struct_instance_id id) { m_last_struct_id = id; }

    void build_tool_select_extractor();
    void build_tool_select_refiner();
    void build_tool_select_assembler();
    void build_tool_select_bin();
    void build_tool_select_source();
    void build_tool_select_sink();
    void build_tool_select_spline();
    void build_tool_cancel();

    DomSession&       session()       { return m_session; }
    const DomSession& session() const { return m_session; }
    const GameCamera& camera() const { return m_camera; }
    DomGameNet&       net()           { return m_net; }
    const DomGameNet& net()     const { return m_net; }

    dui_context& ui_context() { return m_ui_ctx; }

    bool dev_mode() const { return m_dev_mode; }
    bool debug_panel_visible() const { return m_show_debug_panel; }
    void set_debug_panel_visible(bool v) { m_show_debug_panel = v; }
    void toggle_debug_panel() { m_show_debug_panel = !m_show_debug_panel; }
    u32 determinism_mode() const { return m_detmode; }

    bool debug_probe_is_set() const { return m_debug_probe_set; }
    void clear_debug_probe();
    void set_debug_probe(q32_32 x, q32_32 y, q32_32 z);
    void debug_probe_world_coords(q32_32 *out_x, q32_32 *out_y, q32_32 *out_z) const;

    bool overlay_hydrology() const { return m_show_overlay_hydro; }
    bool overlay_temperature() const { return m_show_overlay_temp; }
    bool overlay_pressure() const { return m_show_overlay_pressure; }
    bool overlay_volumes() const { return m_show_overlay_volumes; }

    d_org_id player_org_id() const { return m_player_org_id; }

    void toggle_overlay_hydrology();
    void toggle_overlay_temperature();
    void toggle_overlay_pressure();
    void toggle_overlay_volumes();

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
    void ensure_demo_agents();

    void change_state(GameStateId next);

private:
    Paths        m_paths;
    InstanceInfo m_instance;
    DomSession   m_session;
    DomGameNet   m_net;

    GameMode     m_mode;
    ServerMode   m_server_mode;
    bool         m_demo_mode;
    std::string  m_connect_addr;
    unsigned     m_net_port;

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
    d_org_id      m_player_org_id;
    bool         m_dev_mode;
    u32          m_detmode;
    d_world_hash m_last_hash;
    std::string  m_replay_record_path;
    std::string  m_replay_play_path;
    u32          m_replay_last_tick;
    void        *m_net_replay_user;
    bool         m_show_debug_panel;
    bool         m_debug_probe_set;
    q32_32       m_debug_probe_x;
    q32_32       m_debug_probe_y;
    q32_32       m_debug_probe_z;

    bool         m_show_overlay_hydro;
    bool         m_show_overlay_temp;
    bool         m_show_overlay_pressure;
    bool         m_show_overlay_volumes;

    char         m_hud_instance_text[128];
    char         m_hud_remaining_text[128];
    char         m_hud_inventory_text[128];

    DomGameBuildTool m_build_tool;
};

bool parse_game_cli_args(int argc, char **argv, GameConfig &cfg);
void init_default_game_config(GameConfig &cfg);

} // namespace dom

#endif
