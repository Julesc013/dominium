#include "dom_launcher_app.h"

#include <cstdio>
#include <cstring>

#include "dom_paths.h"
#include "dom_launcher_ui.h"
#include "dom_launcher_catalog.h"
#include "dom_launcher_actions.h"

extern "C" {
#include "domino/system/dsys.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
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
      m_selected_mode("gui"),
      m_connect_host("127.0.0.1"),
      m_net_port(7777u),
      m_edit_connect_host(false),
      m_connect_host_backup(""),
      m_status(""),
      m_show_tools(false),
      m_repo_mod_manifests(),
      m_repo_pack_manifests() {
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
    (void)scan_repo_content();

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
    d_gfx_shutdown();
    d_system_shutdown();
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

void DomLauncherApp::select_prev_instance() {
    if (m_instances.empty()) {
        m_selected_instance = -1;
        return;
    }
    if (m_selected_instance < 0) {
        m_selected_instance = (int)m_instances.size() - 1;
        return;
    }
    m_selected_instance -= 1;
    if (m_selected_instance < 0) {
        m_selected_instance = (int)m_instances.size() - 1;
    }
}

void DomLauncherApp::select_next_instance() {
    if (m_instances.empty()) {
        m_selected_instance = -1;
        return;
    }
    if (m_selected_instance < 0) {
        m_selected_instance = 0;
        return;
    }
    m_selected_instance += 1;
    if (m_selected_instance >= (int)m_instances.size()) {
        m_selected_instance = 0;
    }
}

void DomLauncherApp::cycle_selected_mode() {
    if (m_selected_mode == "gui") {
        m_selected_mode = "tui";
    } else if (m_selected_mode == "tui") {
        m_selected_mode = "headless";
    } else {
        m_selected_mode = "gui";
    }
}

void DomLauncherApp::toggle_connect_host_edit() {
    if (!m_edit_connect_host) {
        m_connect_host_backup = m_connect_host;
        m_edit_connect_host = true;
        m_status = "Editing connect host (digits, '.', Backspace, Enter/Esc)";
    } else {
        m_edit_connect_host = false;
        m_status = "Connect host updated.";
    }
}

void DomLauncherApp::adjust_net_port(int delta) {
    int v = (int)m_net_port;
    v += delta;
    if (v < 1) v = 1;
    if (v > 65535) v = 65535;
    m_net_port = (unsigned)v;
}

const InstanceInfo* DomLauncherApp::selected_instance() const {
    if (m_selected_instance < 0 || m_selected_instance >= (int)m_instances.size()) {
        return (const InstanceInfo *)0;
    }
    return &m_instances[(size_t)m_selected_instance];
}

static std::string dom_u32_arg(const char *prefix, unsigned v) {
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%s%u", prefix ? prefix : "", (unsigned)v);
    return std::string(buf);
}

bool DomLauncherApp::spawn_product_args(const std::string &product,
                                       const std::vector<std::string> &args,
                                       bool wait_for_exit) {
    ProductEntry *entry = find_product_entry(product);
    dsys_proc_result pr;
    dsys_process_handle handle;
    int exit_code = 0;
    std::vector<std::string> full;
    std::vector<const char *> argv;
    size_t i;

    if (!entry) {
        m_status = "Launch failed: product not found.";
        return false;
    }

    full.reserve(1u + args.size());
    full.push_back(entry->path);
    for (i = 0u; i < args.size(); ++i) {
        full.push_back(args[i]);
    }

    argv.resize(full.size() + 1u);
    for (i = 0u; i < full.size(); ++i) {
        argv[i] = full[i].c_str();
    }
    argv[full.size()] = 0;

    std::printf("Launcher: spawning %s (%s)\n",
                entry->path.c_str(), product.c_str());

    if (!wait_for_exit) {
        pr = dsys_proc_spawn(entry->path.c_str(), &argv[0], 1, (dsys_process_handle *)0);
        if (pr != DSYS_PROC_OK) {
            m_status = "Spawn failed.";
            return false;
        }
        m_status = "Spawned.";
        return true;
    }

    pr = dsys_proc_spawn(entry->path.c_str(), &argv[0], 1, &handle);
    if (pr != DSYS_PROC_OK) {
        m_status = "Spawn failed.";
        return false;
    }

    pr = dsys_proc_wait(&handle, &exit_code);
    if (pr != DSYS_PROC_OK) {
        m_status = "Wait failed.";
        return false;
    }

    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Process exited (%d).", exit_code);
        m_status = buf;
    }
    return exit_code == 0;
}

bool DomLauncherApp::launch_game_listen() {
    const InstanceInfo *inst = selected_instance();
    std::vector<std::string> args;
    if (!inst) {
        m_status = "Launch failed: no instance selected.";
        return false;
    }
    args.push_back(std::string("--mode=") + m_selected_mode);
    args.push_back(std::string("--instance=") + inst->id);
    args.push_back("--listen");
    args.push_back(dom_u32_arg("--port=", m_net_port));
    return spawn_product_args("game", args, false);
}

bool DomLauncherApp::launch_game_dedicated() {
    const InstanceInfo *inst = selected_instance();
    std::vector<std::string> args;
    if (!inst) {
        m_status = "Launch failed: no instance selected.";
        return false;
    }
    args.push_back("--mode=headless");
    args.push_back(std::string("--instance=") + inst->id);
    args.push_back("--server");
    args.push_back(dom_u32_arg("--port=", m_net_port));
    return spawn_product_args("game", args, false);
}

bool DomLauncherApp::launch_game_connect() {
    const InstanceInfo *inst = selected_instance();
    std::vector<std::string> args;
    if (!inst) {
        m_status = "Launch failed: no instance selected.";
        return false;
    }
    if (m_connect_host.empty()) {
        m_status = "Launch failed: connect host is empty.";
        return false;
    }
    args.push_back(std::string("--mode=") + m_selected_mode);
    args.push_back(std::string("--instance=") + inst->id);
    args.push_back(std::string("--connect=") + m_connect_host);
    args.push_back(dom_u32_arg("--port=", m_net_port));
    return spawn_product_args("game", args, false);
}

void DomLauncherApp::toggle_tools_view() {
    m_show_tools = !m_show_tools;
    if (m_edit_connect_host) {
        m_connect_host = m_connect_host_backup;
        m_edit_connect_host = false;
    }
    m_status = m_show_tools ? "Tools view." : "Game view.";
}

std::string DomLauncherApp::home_join(const std::string &rel) const {
    return join(m_paths.root, rel);
}

bool DomLauncherApp::launch_tool(const std::string &tool_id,
                                 const std::string &load_path,
                                 bool demo) {
    std::vector<std::string> args;

    if (tool_id.empty()) {
        m_status = "Launch failed: empty tool id.";
        return false;
    }

    args.push_back(std::string("--tool=") + tool_id);
    args.push_back(std::string("--home=") + m_paths.root);
    args.push_back("--sys=win32");
    args.push_back("--gfx=soft");
    if (demo) {
        args.push_back("--demo");
    }
    if (!load_path.empty()) {
        args.push_back(std::string("--load=") + load_path);
    }

    return spawn_product_args(tool_id, args, false);
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
    if (!dir_exists(m_paths.mods)) {
        std::printf("Launcher: '%s' missing, no mods available.\n",
                    m_paths.mods.c_str());
    }
    if (!dir_exists(m_paths.packs)) {
        std::printf("Launcher: '%s' missing, no packs available.\n",
                    m_paths.packs.c_str());
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

    /* Dev fallback: use in-tree build outputs when product catalog is absent. */
    if (!find_product_entry("game")) {
        std::string dbg = join(m_paths.root, "build/source/dominium/game/Debug/dominium_game.exe");
        std::string rel = join(m_paths.root, "build/source/dominium/game/Release/dominium_game.exe");
        ProductEntry p;
        if (file_exists(dbg)) {
            p.product = "game";
            p.version = "dev-debug";
            p.path = dbg;
            m_products.push_back(p);
        } else if (file_exists(rel)) {
            p.product = "game";
            p.version = "dev-release";
            p.path = rel;
            m_products.push_back(p);
        }
    }
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
    struct ToolExe {
        const char *id;
        const char *exe;
    };
    static const ToolExe k_tools[] = {
        { "world_editor",     "dominium-world-editor.exe" },
        { "blueprint_editor", "dominium-blueprint-editor.exe" },
        { "tech_editor",      "dominium-tech-editor.exe" },
        { "policy_editor",    "dominium-policy-editor.exe" },
        { "process_editor",   "dominium-process-editor.exe" },
        { "transport_editor", "dominium-transport-editor.exe" },
        { "struct_editor",    "dominium-struct-editor.exe" },
        { "item_editor",      "dominium-item-editor.exe" },
        { "pack_editor",      "dominium-pack-editor.exe" },
        { "mod_builder",      "dominium-mod-builder.exe" },
        { "save_inspector",   "dominium-save-inspector.exe" },
        { "replay_viewer",    "dominium-replay-viewer.exe" },
        { "net_inspector",    "dominium-net-inspector.exe" },
    };
    static const size_t k_tool_count = sizeof(k_tools) / sizeof(k_tools[0]);

    const std::string dbg_dir = join(m_paths.root, "build/source/dominium/tools/Debug");
    const std::string rel_dir = join(m_paths.root, "build/source/dominium/tools/Release");
    size_t i;

    for (i = 0u; i < k_tool_count; ++i) {
        ProductEntry tool;
        const std::string dbg = join(dbg_dir, k_tools[i].exe);
        const std::string rel = join(rel_dir, k_tools[i].exe);

        tool.product = k_tools[i].id;
        tool.version = "dev";
        tool.path.clear();

        if (file_exists(dbg)) {
            tool.version = "dev-debug";
            tool.path = dbg;
            m_products.push_back(tool);
        } else if (file_exists(rel)) {
            tool.version = "dev-release";
            tool.path = rel;
            m_products.push_back(tool);
        }
    }
    return true;
}

bool DomLauncherApp::scan_repo_content() {
    dsys_dir_iter *it;
    dsys_dir_entry entry;

    m_repo_mod_manifests.clear();
    it = dsys_dir_open(m_paths.mods.c_str());
    if (it) {
        while (dsys_dir_next(it, &entry)) {
            if (!entry.is_dir) {
                continue;
            }
            const std::string mod_id = entry.name;
            const std::string mod_root = join(m_paths.mods, mod_id);
            dsys_dir_iter *ver_it = dsys_dir_open(mod_root.c_str());
            dsys_dir_entry ver_entry;
            while (ver_it && dsys_dir_next(ver_it, &ver_entry)) {
                if (!ver_entry.is_dir) {
                    continue;
                }
                const std::string ver = ver_entry.name;
                const std::string man = join(join(mod_root, ver), "mod.tlv");
                if (file_exists(man)) {
                    m_repo_mod_manifests.push_back(man);
                }
            }
            if (ver_it) {
                dsys_dir_close(ver_it);
            }
        }
        dsys_dir_close(it);
    }

    m_repo_pack_manifests.clear();
    it = dsys_dir_open(m_paths.packs.c_str());
    if (it) {
        while (dsys_dir_next(it, &entry)) {
            if (!entry.is_dir) {
                continue;
            }
            const std::string pack_id = entry.name;
            const std::string pack_root = join(m_paths.packs, pack_id);
            dsys_dir_iter *ver_it = dsys_dir_open(pack_root.c_str());
            dsys_dir_entry ver_entry;
            while (ver_it && dsys_dir_next(ver_it, &ver_entry)) {
                if (!ver_entry.is_dir) {
                    continue;
                }
                const std::string ver = ver_entry.name;
                const std::string man = join(join(pack_root, ver), "pack.tlv");
                if (file_exists(man)) {
                    m_repo_pack_manifests.push_back(man);
                }
            }
            if (ver_it) {
                dsys_dir_close(ver_it);
            }
        }
        dsys_dir_close(it);
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
    d_view_desc vdesc;
    (void)cfg;

    if (!d_system_init("win32")) {
        return false;
    }
    if (!d_gfx_init("soft")) {
        return false;
    }

    std::memset(&vdesc, 0, sizeof(vdesc));
    vdesc.id = 1u;
    vdesc.vp_x = d_q16_16_from_int(0);
    vdesc.vp_y = d_q16_16_from_int(0);
    vdesc.vp_w = d_q16_16_from_int(1);
    vdesc.vp_h = d_q16_16_from_int(1);
    vdesc.camera.fov = d_q16_16_from_int(60);

    m_view = d_view_create(&vdesc);

    dui_init_context(&m_ui);
    dom_launcher_ui_build_root(m_ui, *this);
    dom_launcher_ui_update(m_ui, *this);

    m_running = true;
    return true;
}

void DomLauncherApp::gui_loop() {
    while (m_running) {
        d_gfx_cmd_buffer *buf;
        d_view_frame frame;
        dui_rect rect;
        i32 width = 800;
        i32 height = 480;

        if (d_system_pump_events() != 0) {
            m_running = false;
            break;
        }
        process_input_events();
        if (!m_running) {
            break;
        }
        dom_launcher_ui_update(m_ui, *this);

        buf = d_gfx_cmd_buffer_begin();
        frame.cmd_buffer = buf;
        frame.view = d_view_get(m_view);
        d_gfx_get_surface_size(&width, &height);

        if (frame.view) {
            (void)d_view_render((d_world *)0, frame.view, &frame);
            rect.x = frame.view->vp_x;
            rect.y = frame.view->vp_y;
            rect.w = d_q16_16_from_int(width);
            rect.h = d_q16_16_from_int(height);
        } else {
            rect.x = d_q16_16_from_int(0);
            rect.y = d_q16_16_from_int(0);
            rect.w = d_q16_16_from_int(width);
            rect.h = d_q16_16_from_int(height);
        }

        dui_layout(&m_ui, &rect);
        dui_render(&m_ui, &frame);

        d_gfx_cmd_buffer_end(buf);
        d_gfx_submit(buf);
        d_gfx_present();
        d_system_sleep_ms(16);
    }
}

void DomLauncherApp::process_input_events() {
    d_sys_event ev;
    while (d_system_poll_event(&ev) > 0) {
        if (ev.type == D_SYS_EVENT_QUIT) {
            m_running = false;
            return;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
            (void)dom_launcher_ui_try_click(m_ui, ev.u.mouse.x, ev.u.mouse.y);
        }
        if (ev.type == D_SYS_EVENT_KEY_DOWN) {
            handle_key_event(1, (int)ev.u.key.key);
        } else if (ev.type == D_SYS_EVENT_KEY_UP) {
            handle_key_event(0, (int)ev.u.key.key);
        }
    }
}

void DomLauncherApp::handle_key_event(int down, int key) {
    char c = '\0';
    if (!down) {
        return;
    }
    if (!m_edit_connect_host) {
        return;
    }

    if (key == (int)D_SYS_KEY_ENTER) {
        m_edit_connect_host = false;
        m_status = "Connect host updated.";
        return;
    }
    if (key == (int)D_SYS_KEY_ESCAPE) {
        m_connect_host = m_connect_host_backup;
        m_edit_connect_host = false;
        m_status = "Edit cancelled.";
        return;
    }
    if (key == (int)D_SYS_KEY_BACKSPACE) {
        if (!m_connect_host.empty()) {
            m_connect_host.resize(m_connect_host.size() - 1u);
        }
        return;
    }

    switch ((d_sys_key)key) {
    case D_SYS_KEY_0: c = '0'; break;
    case D_SYS_KEY_1: c = '1'; break;
    case D_SYS_KEY_2: c = '2'; break;
    case D_SYS_KEY_3: c = '3'; break;
    case D_SYS_KEY_4: c = '4'; break;
    case D_SYS_KEY_5: c = '5'; break;
    case D_SYS_KEY_6: c = '6'; break;
    case D_SYS_KEY_7: c = '7'; break;
    case D_SYS_KEY_8: c = '8'; break;
    case D_SYS_KEY_9: c = '9'; break;
    case D_SYS_KEY_PERIOD: c = '.'; break;
    default:
        break;
    }

    if (c != '\0') {
        if (m_connect_host.size() < 63u) {
            m_connect_host.push_back(c);
        }
    }
}

bool DomLauncherApp::launch_product(const std::string &product,
                                    const std::string &instance_id,
                                    const std::string &mode) {
    std::vector<std::string> args;
    args.push_back(std::string("--mode=") + (mode.empty() ? "gui" : mode));
    if (!instance_id.empty()) {
        args.push_back(std::string("--instance=") + instance_id);
    }
    return spawn_product_args(product, args, true);
}

} // namespace dom
