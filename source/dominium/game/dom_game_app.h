/*
FILE: source/dominium/game/dom_game_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_app
RESPONSIBILITY: Defines internal contract for `dom_game_app`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_GAME_APP_H
#define DOM_GAME_APP_H

#include <string>
#include <vector>
#include "dom_game_cli.h"
#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dom_compat.h"
#include "dom_game_phase.h"
#include "dom_game_camera.h"
#include "dom_game_tools_build.h"
#include "dom_game_net.h"
#include "runtime/dom_game_session.h"
#include "runtime/dom_game_net_driver.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_derived_jobs.h"
#include "runtime/dom_snapshot.h"
#include "runtime/dom_fidelity.h"

extern "C" {
#include "view/d_view.h"
#include "ui/d_ui.h"
#include "sim/d_sim.h"
#include "sim/d_sim_hash.h"
#include "core/d_org.h"
#include "struct/d_struct.h"
}

struct dom_game_replay_record;
struct dom_game_replay_play;

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

class DomGameApp {
public:
    DomGameApp();
    ~DomGameApp();

    bool init_from_cli(const dom_game_config &cfg);
    void run();
    void shutdown();
    int exit_code() const { return m_exit_code; }

    void request_exit();
    void request_phase_action(DomGamePhaseAction action);
    void spawn_demo_blueprint();
    void update_demo_hud(const dom_game_snapshot *snapshot);
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

    dom_game_runtime*       runtime()       { return m_runtime; }
    const dom_game_runtime* runtime() const { return m_runtime; }
    d_world*                world()         { return dom_game_runtime_world(m_runtime); }
    d_sim_context*          sim()           { return dom_game_runtime_sim(m_runtime); }

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
    bool init_paths(const dom_game_config &cfg);
    bool init_io_paths(void);
    bool load_instance(const dom_game_config &cfg);
    bool evaluate_compatibility(const dom_game_config &cfg);
    bool init_session(const dom_game_config &cfg);
    bool init_views_and_ui(const dom_game_config &cfg);
    bool start_session(DomGamePhaseAction action, std::string &out_error);
    void handle_phase_enter(DomGamePhaseId prev_phase, DomGamePhaseId next_phase);
    void update_phase(u32 dt_ms);
    void update_menu_labels();
    void handle_universe_action(DomGamePhaseAction action);

    void main_loop();
    void tick_fixed();
    void render_frame();
    void process_input_events();
    void update_camera();
    void update_debug_panel(const dom_game_snapshot *snapshot);
    void ensure_demo_agents();

private:
    DomGamePaths m_fs_paths;
    Paths        m_paths;
    InstanceInfo m_instance;
    DomSession   m_session;
    DomGameNet   m_net;
    DomNetDriver *m_net_driver;
    dom_game_runtime *m_runtime;
    dom_derived_queue *m_derived_queue;
    dom_game_config m_cfg;

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

    DomGamePhaseCtx m_phase;
    DomGamePhaseAction m_phase_action;
    DomGamePhaseAction m_universe_pending_action;
    bool         m_bootstrap_started;
    bool         m_bootstrap_failed;
    bool         m_session_start_attempted;
    bool         m_session_start_ok;
    bool         m_session_start_failed;
    std::string  m_session_start_error;

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
    std::string  m_save_path;
    std::string  m_load_path;
    std::string  m_universe_import_path;
    std::string  m_universe_export_path;
    u32          m_replay_last_tick;
    dom_game_replay_record *m_replay_record;
    dom_game_replay_play *m_replay_play;
    void        *m_net_replay_user;
    u64          m_last_wall_us;
    dom_fidelity_state m_fidelity;
    u32          m_derived_budget_ms;
    u32          m_derived_budget_io_bytes;
    u32          m_derived_budget_jobs;
    bool         m_show_debug_panel;
    bool         m_ui_transparent_loading;
    bool         m_debug_probe_set;
    q32_32       m_debug_probe_x;
    q32_32       m_debug_probe_y;
    q32_32       m_debug_probe_z;

    bool         m_launcher_mode;
    bool         m_dev_allow_ad_hoc_paths;
    bool         m_allow_missing_content;
    bool         m_headless_local;
    bool         m_headless_reached_session;
    bool         m_headless_abort_on_error;
    u32          m_headless_tick_limit;
    u32          m_headless_ticks;
    u32          m_headless_elapsed_ms;
    u32          m_headless_timeout_ms;
    int          m_exit_code;
    u64          m_run_id;
    u32          m_refusal_code;
    std::string  m_refusal_detail;
    std::vector<unsigned char> m_instance_manifest_hash;

    bool         m_show_overlay_hydro;
    bool         m_show_overlay_temp;
    bool         m_show_overlay_pressure;
    bool         m_show_overlay_volumes;

    char         m_hud_instance_text[128];
    char         m_hud_remaining_text[128];
    char         m_hud_inventory_text[128];
    char         m_menu_player_text[128];
    char         m_menu_server_text[128];
    char         m_menu_error_text[256];

    DomGameBuildTool m_build_tool;
};

} // namespace dom

#endif
