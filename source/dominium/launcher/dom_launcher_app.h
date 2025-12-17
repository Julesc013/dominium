/*
FILE: source/dominium/launcher/dom_launcher_app.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_app
RESPONSIBILITY: Defines internal contract for `dom_launcher_app`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_LAUNCHER_APP_H
#define DOM_LAUNCHER_APP_H

#include <string>
#include <vector>

#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_compat.h"

#include "dui/dui_api_v1.h"

extern "C" {
#include "domino/sys.h"
#include "domino/profile.h"
}

namespace dom {

enum LauncherMode {
    LAUNCHER_MODE_GUI = 0,
    LAUNCHER_MODE_TUI,
    LAUNCHER_MODE_CLI
};

struct LauncherConfig {
    std::string argv0;
    std::string home;
    LauncherMode mode;
    std::string action;
    std::string instance_id;
    std::string product;
    std::string product_mode; /* gui/tui/headless */
};

struct ProductEntry {
    std::string product; /* "game", "launcher", "setup", "tool" */
    std::string version;
    std::string path;    /* full path to executable */
};

struct DomLauncherUiState; /* defined in dom_launcher_app.cpp */

class DomLauncherApp {
public:
    DomLauncherApp();
    ~DomLauncherApp();

    bool init_from_cli(const LauncherConfig &cfg, const dom_profile* profile);
    void run();
    void shutdown();

    const std::vector<ProductEntry>& products() const { return m_products; }
    const std::vector<InstanceInfo>& instances() const { return m_instances; }

    int selected_product_index() const { return m_selected_product; }
    int selected_instance_index() const { return m_selected_instance; }
    const std::string& selected_mode() const { return m_selected_mode; }

    void set_selected_product(int idx);
    void set_selected_instance(int idx);
    void set_selected_mode(const std::string &mode);

    void select_prev_instance();
    void select_next_instance();
    void cycle_selected_mode();

    std::string home_join(const std::string &rel) const;

    bool launch_product(const std::string &product,
                        const std::string &instance_id,
                        const std::string &mode);

    const std::string& ui_backend_selected() const { return m_ui_backend_selected; }
    u64                ui_caps_selected() const { return m_ui_caps_selected; }
    const std::string& ui_fallback_note() const { return m_ui_fallback_note; }

private:
    bool scan_products();
    bool scan_instances();
    bool scan_repo();

    bool perform_cli_action(const LauncherConfig &cfg);

    bool init_gui(const LauncherConfig &cfg);
    void gui_loop();
    void process_dui_events();
    void process_ui_task();
    bool load_dui_schema(std::vector<unsigned char>& out_schema, std::string& out_loaded_path, std::string& out_error) const;
    bool build_dui_state(std::vector<unsigned char>& out_state) const;
    const dui_api_v1* select_dui_api(std::string& out_backend_name, std::string& out_err);

    ProductEntry* find_product_entry(const std::string &product);
    const InstanceInfo* selected_instance() const;

    bool spawn_product_args(const std::string &product,
                            const std::vector<std::string> &args,
                            bool wait_for_exit);

private:
    Paths            m_paths;
    LauncherMode     m_mode;
    std::string      m_argv0;

    std::vector<ProductEntry> m_products;
    std::vector<InstanceInfo> m_instances;

    dom_profile       m_profile;
    bool              m_profile_valid;

    const dui_api_v1* m_dui_api;
    dui_context*      m_dui_ctx;
    dui_window*       m_dui_win;

    bool             m_running;

    int              m_selected_product;
    int              m_selected_instance;
    std::string      m_selected_mode;

    std::string      m_ui_backend_selected;
    u64              m_ui_caps_selected;
    std::string      m_ui_fallback_note;

    DomLauncherUiState* m_ui; /* UI-only state (schema-driven DUI) */
};

} // namespace dom

#endif
