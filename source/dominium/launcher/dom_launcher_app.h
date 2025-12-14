#ifndef DOM_LAUNCHER_APP_H
#define DOM_LAUNCHER_APP_H

#include <string>
#include <vector>

#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_compat.h"

extern "C" {
#include "domino/sys.h"
#include "view/d_view.h"
#include "ui/d_ui.h"
}

namespace dom {

enum LauncherMode {
    LAUNCHER_MODE_GUI = 0,
    LAUNCHER_MODE_TUI,
    LAUNCHER_MODE_CLI
};

struct LauncherConfig {
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

class DomLauncherApp {
public:
    DomLauncherApp();
    ~DomLauncherApp();

    bool init_from_cli(const LauncherConfig &cfg);
    void run();
    void shutdown();

    const std::vector<ProductEntry>& products() const { return m_products; }
    const std::vector<InstanceInfo>& instances() const { return m_instances; }

    int selected_product_index() const { return m_selected_product; }
    int selected_instance_index() const { return m_selected_instance; }
    const std::string& selected_mode() const { return m_selected_mode; }

    const std::string& connect_host() const { return m_connect_host; }
    unsigned net_port() const { return m_net_port; }
    bool editing_connect_host() const { return m_edit_connect_host; }
    const std::string& status_text() const { return m_status; }

    void set_selected_product(int idx);
    void set_selected_instance(int idx);
    void set_selected_mode(const std::string &mode);

    void select_prev_instance();
    void select_next_instance();
    void cycle_selected_mode();

    void toggle_connect_host_edit();
    void adjust_net_port(int delta);

    bool launch_game_listen();
    bool launch_game_dedicated();
    bool launch_game_connect();

    bool showing_tools() const { return m_show_tools; }
    void toggle_tools_view();

    bool launch_tool(const std::string &tool_id,
                     const std::string &load_path,
                     bool demo);

    const std::vector<std::string>& repo_mod_manifests() const { return m_repo_mod_manifests; }
    const std::vector<std::string>& repo_pack_manifests() const { return m_repo_pack_manifests; }

    std::string home_join(const std::string &rel) const;

    bool launch_product(const std::string &product,
                        const std::string &instance_id,
                        const std::string &mode);

private:
    bool scan_products();
    bool scan_instances();
    bool scan_tools();
    bool scan_repo();
    bool scan_repo_content();

    bool perform_cli_action(const LauncherConfig &cfg);

    bool init_gui(const LauncherConfig &cfg);
    void gui_loop();
    void process_input_events();
    void handle_key_event(int down, int key);

    ProductEntry* find_product_entry(const std::string &product);
    const InstanceInfo* selected_instance() const;

    bool spawn_product_args(const std::string &product,
                            const std::vector<std::string> &args,
                            bool wait_for_exit);

private:
    Paths            m_paths;
    LauncherMode     m_mode;

    std::vector<ProductEntry> m_products;
    std::vector<InstanceInfo> m_instances;

    d_view_id        m_view;
    dui_context      m_ui;

    bool             m_running;

    int              m_selected_product;
    int              m_selected_instance;
    std::string      m_selected_mode;

    std::string      m_connect_host;
    unsigned         m_net_port;
    bool             m_edit_connect_host;
    std::string      m_connect_host_backup;
    std::string      m_status;

    bool             m_show_tools;
    std::vector<std::string> m_repo_mod_manifests;
    std::vector<std::string> m_repo_pack_manifests;
};

} // namespace dom

#endif
