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

    void set_selected_product(int idx);
    void set_selected_instance(int idx);
    void set_selected_mode(const std::string &mode);

    bool launch_product(const std::string &product,
                        const std::string &instance_id,
                        const std::string &mode);

private:
    bool scan_products();
    bool scan_instances();
    bool scan_tools();
    bool scan_repo();

    bool perform_cli_action(const LauncherConfig &cfg);

    bool init_gui(const LauncherConfig &cfg);
    void gui_loop();

    ProductEntry* find_product_entry(const std::string &product);

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
};

} // namespace dom

#endif
