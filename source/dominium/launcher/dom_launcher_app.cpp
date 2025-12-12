#include "dom_launcher_app.h"

#include <cstdio>
#include <cstring>

#include "dom_paths.h"
#include "dom_launcher_ui.h"
#include "dom_launcher_catalog.h"
#include "dom_launcher_actions.h"

extern "C" {
#include "domino/system/dsys.h"
#include "domino/gfx.h"
#include "domino/core/fixed.h"
}

namespace dom {

DomLauncherApp::DomLauncherApp()
    : m_mode(LAUNCHER_MODE_CLI),
      m_view(0),
      m_running(false),
      m_selected_product(-1),
      m_selected_instance(-1),
      m_selected_mode("gui") {
    std::memset(&m_ui, 0, sizeof(m_ui));
}

DomLauncherApp::~DomLauncherApp() {
    shutdown();
}

bool DomLauncherApp::init_from_cli(const LauncherConfig &cfg) {
    std::string home = cfg.home;

    if (home.empty()) {
        char buf[260];
        if (dsys_get_path(DSYS_PATH_USER_DATA, buf, sizeof(buf))) {
            home = buf;
        } else {
            home = ".";
        }
    }

    if (!resolve_paths(m_paths, home)) {
        std::printf("Launcher: failed to resolve DOMINIUM_HOME from '%s'.\n", home.c_str());
        return false;
    }

    m_mode = cfg.mode;
    m_selected_mode = cfg.product_mode.empty() ? "gui" : cfg.product_mode;

    if (!scan_repo()) {
        return false;
    }
    (void)scan_products();
    (void)scan_instances();
    (void)scan_tools();

    if (m_selected_product < 0 && !m_products.empty()) {
        m_selected_product = 0;
    }
    if (m_selected_instance < 0 && !m_instances.empty()) {
        m_selected_instance = 0;
    }

    if (m_mode == LAUNCHER_MODE_CLI) {
        return perform_cli_action(cfg);
    }

    if (!init_gui(cfg)) {
        std::printf("Launcher: failed to initialize GUI/TUI front-end.\n");
        return false;
    }
    return true;
}

void DomLauncherApp::run() {
    if (m_mode == LAUNCHER_MODE_CLI) {
        return;
    }
    if (m_running) {
        gui_loop();
    }
}

void DomLauncherApp::shutdown() {
    if (m_view != 0) {
        d_view_destroy(m_view);
        m_view = 0;
    }
    if (m_ui.root) {
        dui_shutdown_context(&m_ui);
        std::memset(&m_ui, 0, sizeof(m_ui));
    }
    dgfx_shutdown();
    dsys_shutdown();
    m_running = false;
}

void DomLauncherApp::set_selected_product(int idx) {
    if (idx < 0 || idx >= (int)m_products.size()) {
        return;
    }
    m_selected_product = idx;
}

void DomLauncherApp::set_selected_instance(int idx) {
    if (idx < 0 || idx >= (int)m_instances.size()) {
        return;
    }
    m_selected_instance = idx;
}

void DomLauncherApp::set_selected_mode(const std::string &mode) {
    if (!mode.empty()) {
        m_selected_mode = mode;
    }
}

bool DomLauncherApp::scan_repo() {
    if (!dir_exists(m_paths.root)) {
        std::printf("Launcher: DOMINIUM_HOME '%s' does not exist.\n", m_paths.root.c_str());
        return false;
    }
    if (!dir_exists(m_paths.products)) {
        std::printf("Launcher: '%s' missing, continuing with empty product catalog.\n",
                    m_paths.products.c_str());
    }
    if (!dir_exists(m_paths.instances)) {
        std::printf("Launcher: '%s' missing, no instances available.\n",
                    m_paths.instances.c_str());
    }
    return true;
}

bool DomLauncherApp::scan_products() {
    dsys_dir_iter *prod_it;
    dsys_dir_entry entry;

    m_products.clear();

    prod_it = dsys_dir_open(m_paths.products.c_str());
    if (!prod_it) {
        return true; /* No products directory is not fatal. */
    }

    while (dsys_dir_next(prod_it, &entry)) {
        if (!entry.is_dir) {
            continue;
        }
        std::string product_id = entry.name;
        std::string product_root = join(m_paths.products, product_id);
        dsys_dir_iter *ver_it = dsys_dir_open(product_root.c_str());
        dsys_dir_entry ver_entry;
        while (ver_it && dsys_dir_next(ver_it, &ver_entry)) {
            if (!ver_entry.is_dir) {
                continue;
            }
            std::string version = ver_entry.name;
            std::string bin_dir = join(join(product_root, version), "bin");
            dsys_dir_iter *bin_it = dsys_dir_open(bin_dir.c_str());
            dsys_dir_entry bin_entry;
            while (bin_it && dsys_dir_next(bin_it, &bin_entry)) {
                if (bin_entry.is_dir) {
                    continue;
                }
                ProductEntry p;
                p.product = product_id;
                p.version = version;
                p.path = join(bin_dir, bin_entry.name);
                m_products.push_back(p);
            }
            if (bin_it) {
                dsys_dir_close(bin_it);
            }
        }
        if (ver_it) {
            dsys_dir_close(ver_it);
        }
    }

    dsys_dir_close(prod_it);
    return true;
}

bool DomLauncherApp::scan_instances() {
    dsys_dir_iter *inst_it;
    dsys_dir_entry entry;

    m_instances.clear();
    inst_it = dsys_dir_open(m_paths.instances.c_str());
    if (!inst_it) {
        return true;
    }

    while (dsys_dir_next(inst_it, &entry)) {
        if (!entry.is_dir) {
            continue;
        }
        InstanceInfo inst;
        inst.id = entry.name;
        if (inst.load(m_paths)) {
            m_instances.push_back(inst);
        }
    }

    dsys_dir_close(inst_it);
    if (m_selected_instance < 0 && !m_instances.empty()) {
        m_selected_instance = 0;
    }
    return true;
}

bool DomLauncherApp::scan_tools() {
    /* Manual registration for now. */
    ProductEntry tool;
    tool.product = "tool";
    tool.version = "current";
    tool.path = join(m_paths.root, "tools/modcheck");
    if (file_exists(tool.path)) {
        m_products.push_back(tool);
    }
    return true;
}

bool DomLauncherApp::perform_cli_action(const LauncherConfig &cfg) {
    if (cfg.action == "list-instances") {
        return launcher_action_list_instances(m_instances);
    }
    if (cfg.action == "list-products") {
        return launcher_action_list_products(m_products);
    }
    if (cfg.action == "launch") {
        return launcher_action_launch(*this, cfg);
    }
    if (!cfg.action.empty()) {
        std::printf("Launcher: unknown action '%s'.\n", cfg.action.c_str());
        return false;
    }
    /* No action: nothing to do in CLI mode. */
    return true;
}

ProductEntry* DomLauncherApp::find_product_entry(const std::string &product) {
    size_t i;
    for (i = 0u; i < m_products.size(); ++i) {
        if (m_products[i].product == product) {
            return &m_products[i];
        }
    }
    return (ProductEntry *)0;
}

bool DomLauncherApp::init_gui(const LauncherConfig &cfg) {
    dsys_result sys_rc;
    dgfx_desc gdesc;
    d_view_desc vdesc;

    (void)cfg;

    sys_rc = dsys_init();
    if (sys_rc != DSYS_OK) {
        return false;
    }

    std::memset(&gdesc, 0, sizeof(gdesc));
    gdesc.backend = (m_mode == LAUNCHER_MODE_TUI) ? DGFX_BACKEND_NULL : DGFX_BACKEND_SOFT;
    gdesc.width = 800;
    gdesc.height = 480;
    gdesc.fullscreen = 0;
    gdesc.vsync = 0;

    if (!dgfx_init(&gdesc)) {
        return false;
    }

    std::memset(&vdesc, 0, sizeof(vdesc));
    vdesc.id = 1u;
    vdesc.vp_x = d_q16_16_from_int(0);
    vdesc.vp_y = d_q16_16_from_int(0);
    vdesc.vp_w = d_q16_16_from_int(gdesc.width ? gdesc.width : 800);
    vdesc.vp_h = d_q16_16_from_int(gdesc.height ? gdesc.height : 480);
    vdesc.camera.fov = d_q16_16_from_int(60);

    m_view = d_view_create(&vdesc);

    dui_init_context(&m_ui);
    dom_launcher_ui_build_root(m_ui, *this);

    m_running = true;
    return true;
}

void DomLauncherApp::gui_loop() {
    while (m_running) {
        dsys_event ev;
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                m_running = false;
            }
        }

        dgfx_cmd_buffer *buf = dgfx_get_frame_cmd_buffer();
        d_view_frame frame;
        dui_rect rect;

        frame.cmd_buffer = buf;
        frame.view = d_view_get(m_view);
        if (frame.view) {
            (void)d_view_render((d_world *)0, frame.view, &frame);
            rect.x = frame.view->vp_x;
            rect.y = frame.view->vp_y;
            rect.w = frame.view->vp_w;
            rect.h = frame.view->vp_h;
        } else {
            rect.x = d_q16_16_from_int(0);
            rect.y = d_q16_16_from_int(0);
            rect.w = d_q16_16_from_int(800);
            rect.h = d_q16_16_from_int(480);
        }

        dui_layout(&m_ui, &rect);
        dui_render(&m_ui, &frame);

        dgfx_begin_frame();
        dgfx_execute(buf);
        dgfx_end_frame();
    }
}

bool DomLauncherApp::launch_product(const std::string &product,
                                    const std::string &instance_id,
                                    const std::string &mode) {
    ProductEntry *entry = find_product_entry(product);
    dsys_process_handle handle;
    const char *argv[4];
    std::string mode_arg = std::string("--mode=") + (mode.empty() ? "gui" : mode);
    std::string inst_arg;
    dsys_proc_result pr;
    int exit_code = 0;
    int argi = 0;

    if (!entry) {
        std::printf("Launcher: unknown product '%s'.\n", product.c_str());
        return false;
    }

    argv[argi++] = entry->path.c_str();
    argv[argi++] = mode_arg.c_str();
    if (!instance_id.empty()) {
        inst_arg = std::string("--instance=") + instance_id;
        argv[argi++] = inst_arg.c_str();
    }
    argv[argi] = 0;

    std::printf("Launcher: spawning %s (%s)\n",
                entry->path.c_str(), product.c_str());

    pr = dsys_proc_spawn(entry->path.c_str(), argv, 1, &handle);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: spawn failed for %s\n", entry->path.c_str());
        return false;
    }

    pr = dsys_proc_wait(&handle, &exit_code);
    if (pr != DSYS_PROC_OK) {
        std::printf("Launcher: wait failed for %s\n", entry->path.c_str());
        return false;
    }

    std::printf("Launcher: process exited with code %d\n", exit_code);
    return exit_code == 0;
}

} // namespace dom
