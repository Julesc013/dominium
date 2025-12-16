/*
FILE: source/dominium/launcher/dom_launcher_app.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_app
RESPONSIBILITY: Implements `dom_launcher_app`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_launcher_app.h"

#include <cstdio>
#include <cstring>

#include "dom_paths.h"
#include "dom_launcher_catalog.h"
#include "dom_launcher_actions.h"

#include "domino/caps.h"
#include "domino/io/container.h"
#include "domino/system/dsys.h"

namespace dom {

DomLauncherApp::DomLauncherApp()
    : m_mode(LAUNCHER_MODE_CLI),
      m_profile(),
      m_profile_valid(false),
      m_dui_api(0),
      m_dui_ctx(0),
      m_dui_win(0),
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
      m_repo_pack_manifests(),
      m_tool_sel_id(0u),
      m_mod_sel_id(0u),
      m_pack_sel_id(0u),
      m_ui_backend_selected(""),
      m_ui_caps_selected(0u),
      m_ui_fallback_note("") {
    std::memset(&m_profile, 0, sizeof(m_profile));
    m_profile.abi_version = DOM_PROFILE_ABI_VERSION;
    m_profile.struct_size = (u32)sizeof(dom_profile);
}

DomLauncherApp::~DomLauncherApp() {
    shutdown();
}

bool DomLauncherApp::init_from_cli(const LauncherConfig &cfg, const dom_profile* profile) {
    std::string home = cfg.home;

    m_profile_valid = false;
    std::memset(&m_profile, 0, sizeof(m_profile));
    m_profile.abi_version = DOM_PROFILE_ABI_VERSION;
    m_profile.struct_size = (u32)sizeof(dom_profile);
    if (profile &&
        profile->abi_version == DOM_PROFILE_ABI_VERSION &&
        profile->struct_size == (u32)sizeof(dom_profile)) {
        m_profile = *profile;
        m_profile_valid = true;
    }

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
    if (m_dui_api && m_dui_win) {
        m_dui_api->destroy_window(m_dui_win);
        m_dui_win = 0;
    }
    if (m_dui_api && m_dui_ctx) {
        m_dui_api->destroy_context(m_dui_ctx);
        m_dui_ctx = 0;
    }
    m_dui_api = 0;
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

namespace {

enum LauncherDuiWidgetId {
    DUI_W_ROOT = 100u,

    DUI_W_TITLE = 110u,
    DUI_W_SUMMARY = 111u,

    DUI_W_TOGGLE_VIEW = 120u,
    DUI_W_MODE = 121u,

    DUI_W_INSTANCE = 130u,
    DUI_W_PREV_INSTANCE = 131u,
    DUI_W_NEXT_INSTANCE = 132u,

    DUI_W_CONNECT_LABEL = 140u,
    DUI_W_CONNECT_FIELD = 141u,
    DUI_W_CONNECT_EDIT = 142u,

    DUI_W_PORT = 150u,
    DUI_W_PORT_DEC = 151u,
    DUI_W_PORT_INC = 152u,

    DUI_W_LAUNCH_LISTEN = 160u,
    DUI_W_LAUNCH_DEDICATED = 161u,
    DUI_W_LAUNCH_CONNECT = 162u,

    DUI_W_STATUS = 170u,

    DUI_W_TOOLS_LABEL = 180u,
    DUI_W_TOOLS_LIST = 181u,
    DUI_W_MODS_LABEL = 182u,
    DUI_W_MODS_LIST = 183u,
    DUI_W_PACKS_LABEL = 184u,
    DUI_W_PACKS_LIST = 185u,

    DUI_W_LAUNCH_TOOL_BTN = 186u,
    DUI_W_LAUNCH_MOD_BTN = 187u,
    DUI_W_LAUNCH_PACK_BTN = 188u,

    DUI_W_MAIN_STACK = 190u,
    DUI_W_MAIN_ROW = 191u,
    DUI_W_GAME_COL = 192u,
    DUI_W_TOOLS_COL = 193u,
    DUI_W_INST_LABEL = 194u
};

enum LauncherDuiActionId {
    DUI_ACT_NONE = 0u,
    DUI_ACT_TOGGLE_VIEW = 1u,
    DUI_ACT_CYCLE_MODE = 2u,
    DUI_ACT_PREV_INSTANCE = 3u,
    DUI_ACT_NEXT_INSTANCE = 4u,
    DUI_ACT_TOGGLE_CONNECT_EDIT = 5u,
    DUI_ACT_PORT_DEC = 6u,
    DUI_ACT_PORT_INC = 7u,
    DUI_ACT_LAUNCH_LISTEN = 8u,
    DUI_ACT_LAUNCH_DEDICATED = 9u,
    DUI_ACT_LAUNCH_CONNECT = 10u,
    DUI_ACT_LAUNCH_TOOL = 20u,
    DUI_ACT_LAUNCH_MOD = 21u,
    DUI_ACT_LAUNCH_PACK = 22u
};

static int ascii_tolower(int c) {
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 'a';
    }
    return c;
}

static bool str_ieq(const char* a, const char* b) {
    if (!a || !b) {
        return false;
    }
    while (*a && *b) {
        if (ascii_tolower((unsigned char)*a) != ascii_tolower((unsigned char)*b)) {
            return false;
        }
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

static u32 fnv1a32_bytes(const void* data, size_t len) {
    const unsigned char* p = (const unsigned char*)data;
    u32 h = 2166136261u;
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (u32)p[i];
        h *= 16777619u;
    }
    return h;
}

static u32 fnv1a32_str(const std::string& s) {
    return fnv1a32_bytes(s.data(), s.size());
}

static std::string repo_tail(const std::string& path, const char* marker) {
    if (!marker) {
        return path;
    }
    const std::string m(marker);
    const size_t pos = path.find(m);
    if (pos == std::string::npos) {
        return path;
    }
    return path.substr(pos + m.size());
}

static bool tlv_write_u32(unsigned char* dst, u32 cap, u32* io_off, u32 tag, u32 v) {
    unsigned char le[4];
    dtlv_le_write_u32(le, v);
    return dtlv_tlv_write(dst, cap, io_off, tag, le, 4u) == 0;
}

static bool tlv_write_u64(unsigned char* dst, u32 cap, u32* io_off, u32 tag, u64 v) {
    unsigned char le[8];
    dtlv_le_write_u32(le + 0u, (u32)(v & 0xffffffffu));
    dtlv_le_write_u32(le + 4u, (u32)((v >> 32u) & 0xffffffffu));
    return dtlv_tlv_write(dst, cap, io_off, tag, le, 8u) == 0;
}

static bool tlv_write_text(unsigned char* dst, u32 cap, u32* io_off, u32 tag, const std::string& s) {
    const u32 n = (u32)s.size();
    return dtlv_tlv_write(dst, cap, io_off, tag, s.data(), n) == 0;
}

static bool tlv_write_cstr(unsigned char* dst, u32 cap, u32* io_off, u32 tag, const char* s) {
    const u32 n = (u32)(s ? std::strlen(s) : 0u);
    return dtlv_tlv_write(dst, cap, io_off, tag, s ? s : "", n) == 0;
}

static bool tlv_write_raw(unsigned char* dst, u32 cap, u32* io_off, u32 tag, const void* payload, u32 payload_len) {
    return dtlv_tlv_write(dst, cap, io_off, tag, payload, payload_len) == 0;
}

static u32 stable_item_id(const std::string& s) {
    u32 id = fnv1a32_str(s);
    return (id == 0u) ? 1u : id;
}

struct LauncherToolDef {
    const char* tool_id;
    const char* label;
    u32 demo;
    const char* load_rel; /* optional; relative to DOMINIUM_HOME */
};

static const LauncherToolDef k_tool_defs[] = {
    { "world_editor",     "World Editor",     1u, "" },
    { "blueprint_editor", "Blueprint Editor", 1u, "" },
    { "tech_editor",      "Tech Tree Editor", 1u, "" },
    { "policy_editor",    "Policy Editor",    1u, "" },
    { "process_editor",   "Process Editor",   1u, "" },
    { "transport_editor", "Transport Editor", 1u, "" },
    { "struct_editor",    "Structure Editor", 1u, "" },
    { "item_editor",      "Item Editor",      1u, "" },
    { "pack_editor",      "Pack Editor",      1u, "" },
    { "mod_builder",      "Mod Builder",      1u, "" },
    { "save_inspector",   "Save Inspector",   0u, "data/tools_demo/world_demo.dwrl" },
    { "replay_viewer",    "Replay Viewer",    0u, "" },
    { "net_inspector",    "Net Inspector",    0u, "" }
};
static const u32 k_tool_def_count = (u32)(sizeof(k_tool_defs) / sizeof(k_tool_defs[0]));

static const dui_api_v1* lookup_dui_api_by_backend_name(const char* want_name, std::string& out_err) {
    u32 i;
    u32 count;
    dom_backend_desc desc;

    if (!want_name || !want_name[0]) {
        out_err = "ui backend name is empty";
        return 0;
    }

    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != DOM_SUBSYS_DUI) {
            continue;
        }
        if (!desc.backend_name || !desc.backend_name[0]) {
            continue;
        }
        if (!str_ieq(desc.backend_name, want_name)) {
            continue;
        }
        if (!desc.get_api) {
            out_err = "ui backend missing get_api";
            return 0;
        }

        {
            const dui_api_v1* api = (const dui_api_v1*)desc.get_api(DUI_API_ABI_VERSION);
            if (!api) {
                out_err = std::string("ui get_api returned null for backend '") + want_name + "'";
                return 0;
            }
            if (api->abi_version != DUI_API_ABI_VERSION || api->struct_size != (u32)sizeof(dui_api_v1)) {
                out_err = std::string("ui api abi mismatch for backend '") + want_name + "'";
                return 0;
            }
            if (!api->create_context || !api->destroy_context ||
                !api->create_window || !api->destroy_window ||
                !api->set_schema_tlv || !api->set_state_tlv ||
                !api->pump || !api->poll_event || !api->request_quit || !api->render) {
                out_err = std::string("ui api missing required functions for backend '") + want_name + "'";
                return 0;
            }
            return api;
        }
    }

    out_err = std::string("ui backend not found in registry: '") + want_name + "'";
    return 0;
}

} // namespace

bool DomLauncherApp::init_gui(const LauncherConfig &cfg) {
    std::string backend;
    std::string err;

    (void)cfg;

    shutdown();

    m_ui_backend_selected.clear();
    m_ui_caps_selected = 0u;
    m_ui_fallback_note.clear();

    m_dui_api = select_dui_api(backend, err);
    if (!m_dui_api) {
        std::printf("Launcher: DUI selection failed: %s\n", err.empty() ? "unknown" : err.c_str());
        return false;
    }

    {
        const char* initial_name;
        const char* candidates[3];
        u32 cand_count = 0u;
        u32 cand_i;

        initial_name = (m_dui_api->backend_name && m_dui_api->backend_name()) ? m_dui_api->backend_name() : backend.c_str();

        candidates[cand_count++] = initial_name;
        if (!str_ieq(initial_name, "null") && !str_ieq(initial_name, "dgfx")) {
            candidates[cand_count++] = "dgfx";
        }
        if (!str_ieq(initial_name, "null")) {
            candidates[cand_count++] = "null";
        }

        for (cand_i = 0u; cand_i < cand_count; ++cand_i) {
            const char* want = candidates[cand_i];
            const dui_api_v1* api = m_dui_api;
            std::string lookup_err;
            dui_result rc;
            dui_window_desc_v1 wdesc;

            if (cand_i != 0u) {
                api = lookup_dui_api_by_backend_name(want, lookup_err);
                if (!api) {
                    continue;
                }
            }

            if (api->create_context(&m_dui_ctx) != DUI_OK || !m_dui_ctx) {
                continue;
            }

            std::memset(&wdesc, 0, sizeof(wdesc));
            wdesc.abi_version = DUI_API_ABI_VERSION;
            wdesc.struct_size = (u32)sizeof(wdesc);
            wdesc.title = "Dominium Launcher";
            wdesc.width = 800;
            wdesc.height = 600;
            wdesc.flags = 0u;

            rc = api->create_window(m_dui_ctx, &wdesc, &m_dui_win);
            if (rc != DUI_OK || !m_dui_win) {
                api->destroy_context(m_dui_ctx);
                m_dui_ctx = 0;
                m_dui_win = 0;
                continue;
            }

            m_dui_api = api;
            m_ui_backend_selected = (m_dui_api->backend_name && m_dui_api->backend_name()) ? m_dui_api->backend_name() : want;
            m_ui_caps_selected = m_dui_api->get_caps ? m_dui_api->get_caps() : 0u;

            if (cand_i != 0u) {
                m_ui_fallback_note = std::string("ui_fallback=") + initial_name + "->" + m_ui_backend_selected;
            }
            break;
        }
    }

    if (!m_dui_api || !m_dui_ctx || !m_dui_win) {
        std::printf("Launcher: DUI init failed.\n");
        shutdown();
        return false;
    }

    if (m_tool_sel_id == 0u && k_tool_def_count > 0u) {
        m_tool_sel_id = stable_item_id(std::string(k_tool_defs[0].tool_id));
    }
    if (m_mod_sel_id == 0u && !m_repo_mod_manifests.empty()) {
        m_mod_sel_id = stable_item_id(m_repo_mod_manifests[0]);
    }
    if (m_pack_sel_id == 0u && !m_repo_pack_manifests.empty()) {
        m_pack_sel_id = stable_item_id(m_repo_pack_manifests[0]);
    }

    {
        unsigned char schema[8192];
        u32 schema_len = 0u;
        if (!build_dui_schema(schema, (u32)sizeof(schema), &schema_len)) {
            std::printf("Launcher: failed to build DUI schema.\n");
            shutdown();
            return false;
        }
        if (m_dui_api->set_schema_tlv(m_dui_win, schema, schema_len) != DUI_OK) {
            std::printf("Launcher: DUI set_schema_tlv failed.\n");
            shutdown();
            return false;
        }
    }

    {
        unsigned char state[16384];
        u32 state_len = 0u;
        if (!build_dui_state(state, (u32)sizeof(state), &state_len)) {
            std::printf("Launcher: failed to build DUI state.\n");
            shutdown();
            return false;
        }
        (void)m_dui_api->set_state_tlv(m_dui_win, state, state_len);
    }

    (void)m_dui_api->render(m_dui_win);

    if (m_ui_backend_selected == "null") {
        (void)m_dui_api->request_quit(m_dui_ctx);
    }

    m_running = true;
    return true;
}

void DomLauncherApp::gui_loop() {
    while (m_running) {
        unsigned char state[16384];
        u32 state_len = 0u;

        if (!m_dui_api || !m_dui_ctx) {
            m_running = false;
            break;
        }

        (void)m_dui_api->pump(m_dui_ctx);
        process_dui_events();
        if (!m_running) {
            break;
        }

        if (build_dui_state(state, (u32)sizeof(state), &state_len)) {
            (void)m_dui_api->set_state_tlv(m_dui_win, state, state_len);
        }
        (void)m_dui_api->render(m_dui_win);
        dsys_sleep_ms(16);
    }
}

void DomLauncherApp::process_dui_events() {
    dui_event_v1 ev;
    if (!m_dui_api || !m_dui_ctx) {
        return;
    }
    std::memset(&ev, 0, sizeof(ev));
    while (m_dui_api->poll_event(m_dui_ctx, &ev) > 0) {
        if (ev.type == (u32)DUI_EVENT_QUIT) {
            m_running = false;
            return;
        }
        if (ev.type == (u32)DUI_EVENT_ACTION) {
            const u32 act = ev.u.action.action_id;
            const u32 item = ev.u.action.item_id;

            if (act == (u32)DUI_ACT_CYCLE_MODE) {
                cycle_selected_mode();
            } else if (act == (u32)DUI_ACT_PREV_INSTANCE) {
                select_prev_instance();
            } else if (act == (u32)DUI_ACT_NEXT_INSTANCE) {
                select_next_instance();
            } else if (act == (u32)DUI_ACT_PORT_DEC) {
                adjust_net_port(-1);
            } else if (act == (u32)DUI_ACT_PORT_INC) {
                adjust_net_port(+1);
            } else if (act == (u32)DUI_ACT_LAUNCH_LISTEN) {
                (void)launch_game_listen();
            } else if (act == (u32)DUI_ACT_LAUNCH_DEDICATED) {
                (void)launch_game_dedicated();
            } else if (act == (u32)DUI_ACT_LAUNCH_CONNECT) {
                (void)launch_game_connect();
            } else if (act == (u32)DUI_ACT_LAUNCH_TOOL) {
                const u32 sel_id = (item != 0u) ? item : m_tool_sel_id;
                u32 i;
                for (i = 0u; i < k_tool_def_count; ++i) {
                    if (stable_item_id(std::string(k_tool_defs[i].tool_id)) == sel_id) {
                        std::string load_path;
                        if (k_tool_defs[i].load_rel && k_tool_defs[i].load_rel[0]) {
                            load_path = home_join(k_tool_defs[i].load_rel);
                        }
                        (void)launch_tool(k_tool_defs[i].tool_id, load_path, k_tool_defs[i].demo != 0u);
                        break;
                    }
                }
            } else if (act == (u32)DUI_ACT_LAUNCH_MOD) {
                const u32 sel_id = (item != 0u) ? item : m_mod_sel_id;
                size_t i;
                for (i = 0u; i < m_repo_mod_manifests.size(); ++i) {
                    if (stable_item_id(m_repo_mod_manifests[i]) == sel_id) {
                        (void)launch_tool("mod_builder", m_repo_mod_manifests[i], false);
                        break;
                    }
                }
            } else if (act == (u32)DUI_ACT_LAUNCH_PACK) {
                const u32 sel_id = (item != 0u) ? item : m_pack_sel_id;
                size_t i;
                for (i = 0u; i < m_repo_pack_manifests.size(); ++i) {
                    if (stable_item_id(m_repo_pack_manifests[i]) == sel_id) {
                        (void)launch_tool("pack_editor", m_repo_pack_manifests[i], false);
                        break;
                    }
                }
            }
        } else if (ev.type == (u32)DUI_EVENT_VALUE_CHANGED) {
            const u32 wid = ev.u.value.widget_id;
            const u32 vt = ev.u.value.value_type;

            if (wid == (u32)DUI_W_CONNECT_FIELD && vt == (u32)DUI_VALUE_TEXT) {
                std::string next;
                u32 i;
                for (i = 0u; i < ev.u.value.text_len; ++i) {
                    const char c = ev.u.value.text[i];
                    if ((c >= '0' && c <= '9') || c == '.') {
                        if (next.size() < 63u) {
                            next.push_back(c);
                        }
                    }
                }
                m_connect_host = next;
                m_status = "Connect host updated.";
            } else if (wid == (u32)DUI_W_TOGGLE_VIEW && vt == (u32)DUI_VALUE_BOOL) {
                const u32 want = ev.u.value.v_u32 ? 1u : 0u;
                if ((m_show_tools ? 1u : 0u) != want) {
                    toggle_tools_view();
                }
            } else if (vt == (u32)DUI_VALUE_LIST) {
                const u32 item_id = ev.u.value.item_id;
                if (wid == (u32)DUI_W_INSTANCE) {
                    int idx = -1;
                    size_t i;
                    for (i = 0u; i < m_instances.size(); ++i) {
                        if (stable_item_id(m_instances[i].id) == item_id) {
                            idx = (int)i;
                            break;
                        }
                    }
                    if (idx >= 0) {
                        set_selected_instance(idx);
                    }
                } else if (wid == (u32)DUI_W_TOOLS_LIST) {
                    m_tool_sel_id = item_id;
                } else if (wid == (u32)DUI_W_MODS_LIST) {
                    m_mod_sel_id = item_id;
                } else if (wid == (u32)DUI_W_PACKS_LIST) {
                    m_pack_sel_id = item_id;
                }
            }
        }

        std::memset(&ev, 0, sizeof(ev));
    }
}

static bool schema_emit_node(unsigned char* dst,
                             u32 cap,
                             u32* io_off,
                             u32 id,
                             u32 kind,
                             const char* text,
                             u32 action_id,
                             u32 bind_id,
                             u32 flags,
                             u64 required_caps,
                             const unsigned char* children,
                             u32 children_len)
{
    unsigned char payload[1024];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return false;
    }
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_ID_U32, id)) return false;
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_KIND_U32, kind)) return false;
    if (text && text[0]) {
        if (!tlv_write_cstr(payload, (u32)sizeof(payload), &poff, DUI_TLV_TEXT_UTF8, text)) return false;
    }
    if (action_id != 0u) {
        if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_ACTION_U32, action_id)) return false;
    }
    if (bind_id != 0u) {
        if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id)) return false;
    }
    if (flags != 0u) {
        if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_FLAGS_U32, flags)) return false;
    }
    if (required_caps != 0u) {
        if (!tlv_write_u64(payload, (u32)sizeof(payload), &poff, DUI_TLV_REQUIRED_CAPS_U64, required_caps)) return false;
    }
    if (children && children_len != 0u) {
        if (!tlv_write_raw(payload, (u32)sizeof(payload), &poff, DUI_TLV_CHILDREN_V1, children, children_len)) return false;
    }
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_NODE_V1, payload, poff);
}

bool DomLauncherApp::build_dui_schema(unsigned char* out_buf, u32 cap, u32* out_len) const {
    unsigned char game_children[4096];
    unsigned char tools_children[4096];
    unsigned char row_children[4096];
    unsigned char stack_children[4096];
    unsigned char root_children[4096];
    unsigned char form_payload[4096];
    unsigned char schema_payload[4096];
    u32 game_off = 0u;
    u32 tools_off = 0u;
    u32 row_off = 0u;
    u32 stack_off = 0u;
    u32 root_off = 0u;
    u32 form_off = 0u;
    u32 schema_off = 0u;
    u32 out_off = 0u;

    if (!out_buf || cap == 0u || !out_len) {
        return false;
    }
    *out_len = 0u;

    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_INST_LABEL, (u32)DUI_NODE_LABEL,
                          "Instances", 0u, 0u, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_INSTANCE, (u32)DUI_NODE_LIST,
                          0, 0u, (u32)DUI_W_INSTANCE, (u32)(DUI_NODE_FLAG_FOCUSABLE | DUI_NODE_FLAG_FLEX),
                          (u64)DUI_CAP_LIST, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_PREV_INSTANCE, (u32)DUI_NODE_BUTTON,
                          "Prev Instance", (u32)DUI_ACT_PREV_INSTANCE, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_NEXT_INSTANCE, (u32)DUI_NODE_BUTTON,
                          "Next Instance", (u32)DUI_ACT_NEXT_INSTANCE, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_MODE, (u32)DUI_NODE_BUTTON,
                          0, (u32)DUI_ACT_CYCLE_MODE, (u32)DUI_W_MODE, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_CONNECT_LABEL, (u32)DUI_NODE_LABEL,
                          "Connect host:", 0u, 0u, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_CONNECT_FIELD, (u32)DUI_NODE_TEXT_FIELD,
                          0, 0u, (u32)DUI_W_CONNECT_FIELD, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_TEXT_FIELD, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_PORT, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_PORT, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_PORT_DEC, (u32)DUI_NODE_BUTTON,
                          "Port -", (u32)DUI_ACT_PORT_DEC, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_PORT_INC, (u32)DUI_NODE_BUTTON,
                          "Port +", (u32)DUI_ACT_PORT_INC, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_LAUNCH_LISTEN, (u32)DUI_NODE_BUTTON,
                          "Start Local Host", (u32)DUI_ACT_LAUNCH_LISTEN, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_LAUNCH_DEDICATED, (u32)DUI_NODE_BUTTON,
                          "Start Dedicated Host", (u32)DUI_ACT_LAUNCH_DEDICATED, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_LAUNCH_CONNECT, (u32)DUI_NODE_BUTTON,
                          "Connect To Host", (u32)DUI_ACT_LAUNCH_CONNECT, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(game_children, (u32)sizeof(game_children), &game_off,
                          (u32)DUI_W_STATUS, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_STATUS, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }

    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_TOGGLE_VIEW, (u32)DUI_NODE_CHECKBOX,
                          "Tools view", 0u, (u32)DUI_W_TOGGLE_VIEW, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_CHECKBOX, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_TOOLS_LABEL, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_TOOLS_LABEL, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_TOOLS_LIST, (u32)DUI_NODE_LIST,
                          0, 0u, (u32)DUI_W_TOOLS_LIST, (u32)(DUI_NODE_FLAG_FOCUSABLE | DUI_NODE_FLAG_FLEX),
                          (u64)DUI_CAP_LIST, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_LAUNCH_TOOL_BTN, (u32)DUI_NODE_BUTTON,
                          "Launch Tool", (u32)DUI_ACT_LAUNCH_TOOL, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_MODS_LABEL, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_MODS_LABEL, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_MODS_LIST, (u32)DUI_NODE_LIST,
                          0, 0u, (u32)DUI_W_MODS_LIST, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_LIST, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_LAUNCH_MOD_BTN, (u32)DUI_NODE_BUTTON,
                          "Launch Mod Builder", (u32)DUI_ACT_LAUNCH_MOD, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_PACKS_LABEL, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_PACKS_LABEL, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_PACKS_LIST, (u32)DUI_NODE_LIST,
                          0, 0u, (u32)DUI_W_PACKS_LIST, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_LIST, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(tools_children, (u32)sizeof(tools_children), &tools_off,
                          (u32)DUI_W_LAUNCH_PACK_BTN, (u32)DUI_NODE_BUTTON,
                          "Launch Pack Editor", (u32)DUI_ACT_LAUNCH_PACK, 0u, (u32)DUI_NODE_FLAG_FOCUSABLE,
                          (u64)DUI_CAP_BUTTON, 0, 0u)) {
        return false;
    }

    if (!schema_emit_node(row_children, (u32)sizeof(row_children), &row_off,
                          (u32)DUI_W_GAME_COL, (u32)DUI_NODE_COLUMN,
                          0, 0u, 0u, 0u, (u64)DUI_CAP_LAYOUT_COLUMN,
                          game_children, game_off)) {
        return false;
    }
    if (!schema_emit_node(row_children, (u32)sizeof(row_children), &row_off,
                          (u32)DUI_W_TOOLS_COL, (u32)DUI_NODE_COLUMN,
                          0, 0u, 0u, 0u, (u64)DUI_CAP_LAYOUT_COLUMN,
                          tools_children, tools_off)) {
        return false;
    }

    if (!schema_emit_node(stack_children, (u32)sizeof(stack_children), &stack_off,
                          (u32)DUI_W_MAIN_ROW, (u32)DUI_NODE_ROW,
                          0, 0u, 0u, 0u, (u64)DUI_CAP_LAYOUT_ROW,
                          row_children, row_off)) {
        return false;
    }

    if (!schema_emit_node(root_children, (u32)sizeof(root_children), &root_off,
                          (u32)DUI_W_TITLE, (u32)DUI_NODE_LABEL,
                          "Dominium Launcher", 0u, 0u, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(root_children, (u32)sizeof(root_children), &root_off,
                          (u32)DUI_W_SUMMARY, (u32)DUI_NODE_LABEL,
                          0, 0u, (u32)DUI_W_SUMMARY, 0u,
                          (u64)DUI_CAP_LABEL, 0, 0u)) {
        return false;
    }
    if (!schema_emit_node(root_children, (u32)sizeof(root_children), &root_off,
                          (u32)DUI_W_MAIN_STACK, (u32)DUI_NODE_STACK,
                          0, 0u, 0u, 0u, (u64)DUI_CAP_LAYOUT_STACK,
                          stack_children, stack_off)) {
        return false;
    }

    if (!schema_emit_node(form_payload, (u32)sizeof(form_payload), &form_off,
                          (u32)DUI_W_ROOT, (u32)DUI_NODE_COLUMN,
                          0, 0u, 0u, 0u, (u64)DUI_CAP_LAYOUT_COLUMN,
                          root_children, root_off)) {
        return false;
    }

    if (!tlv_write_raw(schema_payload, (u32)sizeof(schema_payload), &schema_off, DUI_TLV_FORM_V1, form_payload, form_off)) {
        return false;
    }
    if (!tlv_write_raw(out_buf, cap, &out_off, DUI_TLV_SCHEMA_V1, schema_payload, schema_off)) {
        return false;
    }

    *out_len = out_off;
    return true;
}

static bool state_emit_text(unsigned char* dst, u32 cap, u32* io_off, u32 bind_id, const std::string& s)
{
    unsigned char payload[512];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return false;
    }
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id)) return false;
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_TEXT)) return false;
    if (!tlv_write_text(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_UTF8, s)) return false;
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, payload, poff);
}

static bool state_emit_u32(unsigned char* dst, u32 cap, u32* io_off, u32 bind_id, u32 v)
{
    unsigned char payload[256];
    u32 poff = 0u;
    if (!dst || !io_off) {
        return false;
    }
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_BIND_U32, bind_id)) return false;
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_U32)) return false;
    if (!tlv_write_u32(payload, (u32)sizeof(payload), &poff, DUI_TLV_VALUE_U32, v)) return false;
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, payload, poff);
}

static bool state_emit_list_record(unsigned char* dst,
                                   u32 cap,
                                   u32* io_off,
                                   u32 bind_id,
                                   const unsigned char* list_payload,
                                   u32 list_len)
{
    unsigned char value_payload[8192];
    u32 voff = 0u;
    if (!dst || !io_off || (!list_payload && list_len != 0u)) {
        return false;
    }
    if (!tlv_write_u32(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_BIND_U32, bind_id)) return false;
    if (!tlv_write_u32(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_VALUE_TYPE_U32, (u32)DUI_VALUE_LIST)) return false;
    if (!tlv_write_raw(value_payload, (u32)sizeof(value_payload), &voff, DUI_TLV_LIST_V1, list_payload, list_len)) return false;
    return tlv_write_raw(dst, cap, io_off, DUI_TLV_VALUE_V1, value_payload, voff);
}

bool DomLauncherApp::build_dui_state(unsigned char* out_buf, u32 cap, u32* out_len) const {
    unsigned char inner[16384];
    u32 inner_off = 0u;
    u32 out_off = 0u;

    if (!out_buf || cap == 0u || !out_len) {
        return false;
    }
    *out_len = 0u;

    {
        char buf[256];
        std::snprintf(buf, sizeof(buf), "Products: %u  Instances: %u  Mods: %u  Packs: %u",
                      (unsigned)m_products.size(),
                      (unsigned)m_instances.size(),
                      (unsigned)m_repo_mod_manifests.size(),
                      (unsigned)m_repo_pack_manifests.size());
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_SUMMARY, std::string(buf))) return false;
    }
    if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_MODE, std::string("Mode: ") + m_selected_mode)) return false;
    if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_CONNECT_FIELD, m_connect_host)) return false;
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Port: %u", (unsigned)m_net_port);
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_PORT, std::string(buf))) return false;
    }
    {
        std::string s = std::string("Status: ") + (m_status.empty() ? "(none)" : m_status);
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_STATUS, s)) return false;
    }
    if (!state_emit_u32(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_TOGGLE_VIEW, m_show_tools ? 1u : 0u)) return false;
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Tools: %u", (unsigned)(m_show_tools ? k_tool_def_count : 0u));
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_TOOLS_LABEL, std::string(buf))) return false;
    }
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Repo Mods: %u", (unsigned)(m_show_tools ? m_repo_mod_manifests.size() : 0u));
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_MODS_LABEL, std::string(buf))) return false;
    }
    {
        char buf[64];
        std::snprintf(buf, sizeof(buf), "Repo Packs: %u", (unsigned)(m_show_tools ? m_repo_pack_manifests.size() : 0u));
        if (!state_emit_text(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_PACKS_LABEL, std::string(buf))) return false;
    }

    /* Instances list */
    {
        unsigned char list_payload[8192];
        u32 list_off = 0u;
        u32 selected_id = 0u;
        size_t i;

        if (m_selected_instance >= 0 && m_selected_instance < (int)m_instances.size()) {
            selected_id = stable_item_id(m_instances[(size_t)m_selected_instance].id);
        }
        if (!tlv_write_u32(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_SELECTED_U32, selected_id)) return false;
        for (i = 0u; i < m_instances.size(); ++i) {
            unsigned char item_payload[512];
            u32 item_off = 0u;
            const u32 item_id = stable_item_id(m_instances[i].id);
            if (!tlv_write_u32(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_ID_U32, item_id)) return false;
            if (!tlv_write_text(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_TEXT_UTF8, m_instances[i].id)) return false;
            if (!tlv_write_raw(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_ITEM_V1, item_payload, item_off)) return false;
        }
        if (!state_emit_list_record(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_INSTANCE, list_payload, list_off)) return false;
    }

    /* Tools list */
    {
        unsigned char list_payload[8192];
        u32 list_off = 0u;
        u32 selected_id = m_show_tools ? m_tool_sel_id : 0u;
        u32 i;

        if (!tlv_write_u32(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_SELECTED_U32, selected_id)) return false;
        if (m_show_tools) {
            for (i = 0u; i < k_tool_def_count; ++i) {
                unsigned char item_payload[512];
                u32 item_off = 0u;
                const u32 item_id = stable_item_id(std::string(k_tool_defs[i].tool_id));
                if (!tlv_write_u32(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_ID_U32, item_id)) return false;
                if (!tlv_write_cstr(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_TEXT_UTF8, k_tool_defs[i].label)) return false;
                if (!tlv_write_raw(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_ITEM_V1, item_payload, item_off)) return false;
            }
        }
        if (!state_emit_list_record(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_TOOLS_LIST, list_payload, list_off)) return false;
    }

    /* Mods list */
    {
        unsigned char list_payload[8192];
        u32 list_off = 0u;
        u32 selected_id = m_show_tools ? m_mod_sel_id : 0u;
        size_t i;

        if (!tlv_write_u32(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_SELECTED_U32, selected_id)) return false;
        if (m_show_tools) {
            for (i = 0u; i < m_repo_mod_manifests.size(); ++i) {
                unsigned char item_payload[512];
                u32 item_off = 0u;
                const u32 item_id = stable_item_id(m_repo_mod_manifests[i]);
                const std::string label = std::string("Mod: ") + repo_tail(m_repo_mod_manifests[i], "repo/mods/");
                if (!tlv_write_u32(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_ID_U32, item_id)) return false;
                if (!tlv_write_text(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_TEXT_UTF8, label)) return false;
                if (!tlv_write_raw(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_ITEM_V1, item_payload, item_off)) return false;
            }
        }
        if (!state_emit_list_record(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_MODS_LIST, list_payload, list_off)) return false;
    }

    /* Packs list */
    {
        unsigned char list_payload[8192];
        u32 list_off = 0u;
        u32 selected_id = m_show_tools ? m_pack_sel_id : 0u;
        size_t i;

        if (!tlv_write_u32(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_SELECTED_U32, selected_id)) return false;
        if (m_show_tools) {
            for (i = 0u; i < m_repo_pack_manifests.size(); ++i) {
                unsigned char item_payload[512];
                u32 item_off = 0u;
                const u32 item_id = stable_item_id(m_repo_pack_manifests[i]);
                const std::string label = std::string("Pack: ") + repo_tail(m_repo_pack_manifests[i], "repo/packs/");
                if (!tlv_write_u32(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_ID_U32, item_id)) return false;
                if (!tlv_write_text(item_payload, (u32)sizeof(item_payload), &item_off, DUI_TLV_ITEM_TEXT_UTF8, label)) return false;
                if (!tlv_write_raw(list_payload, (u32)sizeof(list_payload), &list_off, DUI_TLV_LIST_ITEM_V1, item_payload, item_off)) return false;
            }
        }
        if (!state_emit_list_record(inner, (u32)sizeof(inner), &inner_off, (u32)DUI_W_PACKS_LIST, list_payload, list_off)) return false;
    }

    if (!tlv_write_raw(out_buf, cap, &out_off, DUI_TLV_STATE_V1, inner, inner_off)) {
        return false;
    }
    *out_len = out_off;
    return true;
}

const dui_api_v1* DomLauncherApp::select_dui_api(std::string& out_backend_name, std::string& out_err) {
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    u32 i;
    const char* chosen = (const char*)0;

    out_backend_name.clear();
    out_err.clear();

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);

    sel_rc = dom_caps_select(m_profile_valid ? &m_profile : (const dom_profile*)0, &hw, &sel);
    if (sel_rc != DOM_CAPS_OK) {
        out_err = "caps selection failed";
        return (const dui_api_v1*)0;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (e->subsystem_id == DOM_SUBSYS_DUI) {
            chosen = e->backend_name;
            break;
        }
    }
    if (!chosen || !chosen[0]) {
        out_err = "caps selection produced empty ui backend";
        return (const dui_api_v1*)0;
    }

    out_backend_name = chosen;
    return lookup_dui_api_by_backend_name(chosen, out_err);
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
