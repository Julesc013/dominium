/*
FILE: source/dominium/launcher/launcher_tui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher / tui
RESPONSIBILITY: Implements the keyboard-only TUI front-end for dominium-launcher.
ALLOWED DEPENDENCIES: `include/dominium/**`, `include/domino/**`, launcher core headers, and C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS headers, GUI toolkit headers, and any Plan 8 contract changes.
THREADING MODEL: Single-threaded event loop; no internal synchronization.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: UI only dispatches core operations; ordering is explicit and stable.
*/
#include "launcher_tui.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <vector>

extern "C" {
#include "domino/sys.h"
#include "domino/system/dsys.h"
#include "domino/tui/tui.h"
}

#include "launcher_control_plane.h"

#include "core/include/launcher_audit.h"
#include "core/include/launcher_instance.h"
#include "core/include/launcher_instance_config.h"
#include "core/include/launcher_instance_ops.h"
#include "core/include/launcher_instance_tx.h"
#include "core/include/launcher_pack_resolver.h"
#include "core/include/launcher_safety.h"
#include "core/include/launcher_tools_registry.h"

namespace dom {

namespace {

static bool str_lt(const std::string& a, const std::string& b) { return a < b; }

static void sort_strings(std::vector<std::string>& v) {
    std::sort(v.begin(), v.end(), str_lt);
}

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool file_exists(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool read_file_all(const std::string& path, std::vector<unsigned char>& out_bytes) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        return false;
    }
    if (sz == 0) {
        std::fclose(f);
        return true;
    }
    out_bytes.resize((size_t)sz);
    got = std::fread(out_bytes.empty() ? (void*)0 : &out_bytes[0], 1u, (size_t)sz, f);
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        return false;
    }
    return true;
}

static bool list_instances(const std::string& state_root, std::vector<std::string>& out_ids) {
    std::string instances_root;
    dsys_dir_iter* it;
    dsys_dir_entry e;

    out_ids.clear();
    instances_root = path_join(state_root, "instances");
    it = dsys_dir_open(instances_root.c_str());
    if (!it) {
        return true;
    }

    std::memset(&e, 0, sizeof(e));
    while (dsys_dir_next(it, &e)) {
        std::string id;
        std::string manifest_path;
        if (!e.is_dir) continue;
        id = std::string(e.name ? e.name : "");
        if (!dom::launcher_core::launcher_is_safe_id_component(id)) continue;
        manifest_path = path_join(path_join(instances_root, id), "manifest.tlv");
        if (!file_exists(manifest_path)) continue;
        out_ids.push_back(id);
    }
    dsys_dir_close(it);
    sort_strings(out_ids);
    return true;
}

static bool list_runs(const std::string& state_root,
                      const std::string& instance_id,
                      std::vector<std::string>& out_run_ids) {
    dom::launcher_core::LauncherInstancePaths paths;
    std::string runs_root;
    dsys_dir_iter* it;
    dsys_dir_entry e;

    out_run_ids.clear();
    if (state_root.empty() || instance_id.empty()) {
        return false;
    }
    paths = dom::launcher_core::launcher_instance_paths_make(state_root, instance_id);
    runs_root = path_join(paths.logs_root, "runs");
    it = dsys_dir_open(runs_root.c_str());
    if (!it) {
        return true;
    }
    std::memset(&e, 0, sizeof(e));
    while (dsys_dir_next(it, &e)) {
        if (!e.is_dir) continue;
        if (!e.name || !e.name[0]) continue;
        out_run_ids.push_back(std::string(e.name));
    }
    dsys_dir_close(it);
    sort_strings(out_run_ids);
    return true;
}

static bool is_pack_like(u32 content_type) {
    return content_type == (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK ||
           content_type == (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD ||
           content_type == (u32)dom::launcher_core::LAUNCHER_CONTENT_RUNTIME;
}

static const char* content_type_to_short(u32 t) {
    switch (t) {
    case (u32)dom::launcher_core::LAUNCHER_CONTENT_PACK: return "pack";
    case (u32)dom::launcher_core::LAUNCHER_CONTENT_MOD: return "mod";
    case (u32)dom::launcher_core::LAUNCHER_CONTENT_RUNTIME: return "runtime";
    default: break;
    }
    return "content";
}

static std::string pack_key(u32 content_type, const std::string& id) {
    return std::string(content_type_to_short(content_type)) + ":" + id;
}

static const char* update_policy_to_string(u32 p) {
    switch (p) {
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT: return "prompt";
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO: return "auto";
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER:
    default:
        return "never";
    }
}

static u32 cycle_update_policy(u32 p) {
    switch (p) {
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER: return (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT;
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_PROMPT: return (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO;
    case (u32)dom::launcher_core::LAUNCHER_UPDATE_AUTO:
    default:
        return (u32)dom::launcher_core::LAUNCHER_UPDATE_NEVER;
    }
}

static const char* window_mode_to_string(u32 mode) {
    switch (mode) {
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED: return "windowed";
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_FULLSCREEN: return "fullscreen";
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_BORDERLESS: return "borderless";
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_AUTO:
    default:
        return "auto";
    }
}

static u32 cycle_window_mode(u32 mode) {
    switch (mode) {
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_AUTO: return (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED;
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_WINDOWED: return (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_FULLSCREEN;
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_FULLSCREEN: return (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_BORDERLESS;
    case (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_BORDERLESS:
    default:
        return (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_AUTO;
    }
}

static bool prompt_line(const char* prompt, std::string& out_line) {
    char buf[512];
    out_line.clear();

    dsys_terminal_shutdown();
    std::fputs(prompt ? prompt : "", stdout);
    std::fflush(stdout);

    if (!std::fgets(buf, (int)sizeof(buf), stdin)) {
        (void)dsys_terminal_init();
        return false;
    }
    {
        size_t n = std::strlen(buf);
        while (n > 0u && (buf[n - 1u] == '\n' || buf[n - 1u] == '\r')) {
            buf[n - 1u] = '\0';
            n -= 1u;
        }
    }

    out_line = std::string(buf);
    (void)dsys_terminal_init();
    return true;
}

static bool prompt_yes_no(const char* prompt, int& out_yes) {
    std::string line;
    out_yes = 0;
    if (!prompt_line(prompt, line)) {
        return false;
    }
    if (line == "y" || line == "Y" || line == "yes" || line == "YES") {
        out_yes = 1;
    }
    return true;
}

static bool parse_u32_dec(const std::string& s, u32& out_v) {
    const unsigned char* p;
    u64 v;
    if (s.empty()) {
        return false;
    }
    v = 0ull;
    p = (const unsigned char*)s.c_str();
    while (*p) {
        if (*p < (unsigned char)'0' || *p > (unsigned char)'9') {
            return false;
        }
        v = (v * 10ull) + (u64)(*p - (unsigned char)'0');
        if (v > 0xFFFFFFFFull) {
            return false;
        }
        ++p;
    }
    out_v = (u32)v;
    return true;
}

static std::string file_read_all_text(FILE* f) {
    std::string out;
    long sz;
    std::vector<char> buf;
    if (!f) return out;
    if (std::fseek(f, 0, SEEK_END) != 0) return out;
    sz = std::ftell(f);
    if (sz < 0) return out;
    if (std::fseek(f, 0, SEEK_SET) != 0) return out;
    buf.resize((size_t)sz);
    if (sz > 0) {
        (void)std::fread(buf.empty() ? (void*)0 : &buf[0], 1u, (size_t)sz, f);
        out.assign(buf.begin(), buf.end());
    }
    return out;
}

static std::string kv_get(const std::string& text, const std::string& key) {
    const std::string prefix = key + "=";
    size_t pos = 0u;
    while (pos < text.size()) {
        size_t end = text.find('\n', pos);
        if (end == std::string::npos) end = text.size();
        if (end > pos && text.compare(pos, prefix.size(), prefix) == 0) {
            return text.substr(pos + prefix.size(), end - (pos + prefix.size()));
        }
        pos = end + 1u;
    }
    return std::string();
}

static int run_control_plane_capture(::launcher_core* audit_core,
                                     const dom_profile* profile,
                                     const std::vector<std::string>& argv_in,
                                     std::string& out_text) {
    std::vector<char*> cargv;
    std::vector<std::string> argv = argv_in;
    FILE* out = std::tmpfile();
    FILE* err = std::tmpfile();
    size_t i;
    ControlPlaneRunResult r;

    out_text.clear();
    if (!out) {
        if (err) std::fclose(err);
        return 1;
    }
    if (!err) {
        std::fclose(out);
        return 1;
    }

    cargv.reserve(argv.size());
    for (i = 0u; i < argv.size(); ++i) {
        cargv.push_back(argv[i].empty() ? (char*)"" : (char*)argv[i].c_str());
    }

    r = dom::launcher_control_plane_try_run((int)cargv.size(), &cargv[0], audit_core, profile, out, err);
    out_text = file_read_all_text(out);

    std::fclose(out);
    std::fclose(err);

    if (!r.handled) {
        return 2;
    }
    return r.exit_code;
}

} /* namespace */

namespace {

struct StagedPackChange {
    u32 has_enabled;
    u32 enabled;
    u32 has_update_policy;
    u32 update_policy;
    StagedPackChange() : has_enabled(0u), enabled(0u), has_update_policy(0u), update_policy(0u) {}
};

enum TuiTab {
    TUI_TAB_PLAY = 0,
    TUI_TAB_INSTANCES = 1,
    TUI_TAB_PACKS = 2,
    TUI_TAB_OPTIONS = 3,
    TUI_TAB_DIAGNOSTICS = 4
};

enum TuiAction {
    TUI_ACTION_NONE = 0,
    TUI_ACTION_TAB_PLAY,
    TUI_ACTION_TAB_INSTANCES,
    TUI_ACTION_TAB_PACKS,
    TUI_ACTION_TAB_OPTIONS,
    TUI_ACTION_TAB_DIAGNOSTICS,
    TUI_ACTION_QUIT,

    TUI_ACTION_PLAY_TOGGLE_TARGET,
    TUI_ACTION_PLAY_TOGGLE_OFFLINE,
    TUI_ACTION_PLAY_VERIFY,
    TUI_ACTION_PLAY_LAUNCH,
    TUI_ACTION_PLAY_SAFE_LAUNCH,
    TUI_ACTION_PLAY_AUDIT_LAST,

    TUI_ACTION_INST_REFRESH,
    TUI_ACTION_INST_CREATE_EMPTY,
    TUI_ACTION_INST_CREATE_TEMPLATE,
    TUI_ACTION_INST_CLONE,
    TUI_ACTION_INST_DELETE,
    TUI_ACTION_INST_EXPORT_DEF,
    TUI_ACTION_INST_EXPORT_BUNDLE,
    TUI_ACTION_INST_IMPORT,
    TUI_ACTION_INST_MARK_KG,

    TUI_ACTION_PACK_TOGGLE_ENABLED,
    TUI_ACTION_PACK_CYCLE_POLICY,
    TUI_ACTION_PACK_APPLY,
    TUI_ACTION_PACK_DISCARD,

    TUI_ACTION_OPT_TOGGLE_OFFLINE,
    TUI_ACTION_OPT_SET_GFX_BACKEND,
    TUI_ACTION_OPT_SET_RENDERER_API,
    TUI_ACTION_OPT_CYCLE_WINDOW_MODE,
    TUI_ACTION_OPT_SET_WIDTH,
    TUI_ACTION_OPT_SET_HEIGHT,
    TUI_ACTION_OPT_RESET_GRAPHICS,

    TUI_ACTION_DIAG_REFRESH,
    TUI_ACTION_DIAG_AUDIT_LAST,
    TUI_ACTION_DIAG_BUNDLE
};

struct TuiUi {
    d_tui_context* ctx;
    d_tui_widget* instances_list;
    d_tui_widget* packs_list;
    d_tui_widget* runs_list;

    std::vector<std::string> instance_items;
    std::vector<const char*> instance_cstrs;

    std::vector<std::string> pack_items;
    std::vector<const char*> pack_cstrs;
    std::vector<std::string> pack_keys;

    std::vector<std::string> run_items;
    std::vector<const char*> run_cstrs;

    TuiUi()
        : ctx(0),
          instances_list(0),
          packs_list(0),
          runs_list(0),
          instance_items(),
          instance_cstrs(),
          pack_items(),
          pack_cstrs(),
          pack_keys(),
          run_items(),
          run_cstrs() {}
};

struct LauncherTuiApp;

struct TuiActionCtx {
    LauncherTuiApp* app;
    TuiAction action;
    TuiActionCtx(LauncherTuiApp* a, TuiAction act) : app(a), action(act) {}
};

struct LauncherTuiApp {
    std::string argv0;
    std::string state_root;
    ::launcher_core* audit_core;
    const dom_profile* profile;
    const ::launcher_services_api_v1* services;

    TuiTab tab;
    TuiAction pending_action;
    std::vector<TuiActionCtx*> action_ctxs;

    std::vector<std::string> instance_ids;
    int selected_instance_index;

    dom::launcher_core::LauncherInstanceManifest manifest;
    dom::launcher_core::LauncherInstanceConfig config;

    dom::launcher_core::LauncherToolsRegistry tools_reg;
    std::vector<dom::launcher_core::LauncherToolEntry> tools_for_instance;
    int selected_tool_index; /* -1 means game */

    std::vector<std::string> run_ids;
    int selected_pack_index;

    std::map<std::string, StagedPackChange> staged_packs;

    std::string status;
    TuiUi ui;

    LauncherTuiApp()
        : argv0(),
          state_root(),
          audit_core(0),
          profile(0),
          services(::launcher_services_null_v1()),
          tab(TUI_TAB_PLAY),
          pending_action(TUI_ACTION_NONE),
          action_ctxs(),
          instance_ids(),
          selected_instance_index(-1),
          manifest(),
          config(),
          tools_reg(),
          tools_for_instance(),
          selected_tool_index(-1),
          run_ids(),
          selected_pack_index(-1),
          staged_packs(),
          status("Ready."),
          ui() {}
};

static void tui_on_activate(d_tui_widget* self, void* user) {
    TuiActionCtx* ctx = (TuiActionCtx*)user;
    (void)self;
    if (!ctx || !ctx->app) return;
    ctx->app->pending_action = ctx->action;
}

static void tui_free_actions(LauncherTuiApp& app) {
    size_t i;
    for (i = 0u; i < app.action_ctxs.size(); ++i) {
        delete app.action_ctxs[i];
    }
    app.action_ctxs.clear();
}

static void tui_destroy_ui(LauncherTuiApp& app) {
    if (app.ui.ctx) {
        d_tui_destroy(app.ui.ctx);
        app.ui.ctx = 0;
    }
    app.ui.instances_list = 0;
    app.ui.packs_list = 0;
    app.ui.runs_list = 0;
    app.ui.instance_items.clear();
    app.ui.instance_cstrs.clear();
    app.ui.pack_items.clear();
    app.ui.pack_cstrs.clear();
    app.ui.pack_keys.clear();
    app.ui.run_items.clear();
    app.ui.run_cstrs.clear();
    tui_free_actions(app);
}

static void* tui_alloc_action(LauncherTuiApp& app, TuiAction a) {
    TuiActionCtx* ctx = new TuiActionCtx(&app, a);
    app.action_ctxs.push_back(ctx);
    return (void*)ctx;
}

static std::string selected_instance_id(const LauncherTuiApp& app) {
    if (app.selected_instance_index < 0 || app.selected_instance_index >= (int)app.instance_ids.size()) {
        return std::string();
    }
    return app.instance_ids[(size_t)app.selected_instance_index];
}

static void reload_instance_cache(LauncherTuiApp& app) {
    const std::string instance_id = selected_instance_id(app);

    app.manifest = dom::launcher_core::LauncherInstanceManifest();
    app.config = dom::launcher_core::LauncherInstanceConfig();
    app.tools_for_instance.clear();
    app.selected_tool_index = -1;
    app.run_ids.clear();
    app.selected_pack_index = -1;

    if (instance_id.empty()) {
        return;
    }

    (void)dom::launcher_core::launcher_instance_load_manifest(app.services, instance_id, app.state_root, app.manifest);
    {
        dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(app.state_root, instance_id);
        dom::launcher_core::LauncherInstanceConfig cfg = dom::launcher_core::launcher_instance_config_make_default(instance_id);
        (void)dom::launcher_core::launcher_instance_config_load(app.services, paths, cfg);
        app.config = cfg;
    }

    {
        std::string loaded;
        std::string err;
        if (dom::launcher_core::launcher_tools_registry_load(app.services, app.state_root, app.tools_reg, &loaded, &err)) {
            dom::launcher_core::launcher_tools_registry_enumerate_for_instance(app.tools_reg, app.manifest, app.tools_for_instance);
        }
    }

    (void)list_runs(app.state_root, instance_id, app.run_ids);
}

static bool store_config(const LauncherTuiApp& app, const dom::launcher_core::LauncherInstanceConfig& cfg) {
    const std::string instance_id = selected_instance_id(app);
    if (instance_id.empty()) {
        return false;
    }
    dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(app.state_root, instance_id);
    return dom::launcher_core::launcher_instance_config_store(app.services, paths, cfg);
}

static std::string target_to_string(const LauncherTuiApp& app) {
    if (app.selected_tool_index >= 0 && app.selected_tool_index < (int)app.tools_for_instance.size()) {
        return std::string("tool:") + app.tools_for_instance[(size_t)app.selected_tool_index].tool_id;
    }
    return std::string("game");
}

static bool apply_packs_transaction(LauncherTuiApp& app, std::string& out_err) {
    dom::launcher_core::LauncherAuditLog audit;
    dom::launcher_core::LauncherInstanceTx tx;
    std::vector<dom::launcher_core::LauncherResolvedPack> resolved;
    std::string resolve_err;
    size_t i;

    out_err.clear();
    if (app.staged_packs.empty()) {
        out_err = "no_changes";
        return false;
    }

    if (!dom::launcher_core::launcher_instance_tx_prepare(app.services,
                                                          selected_instance_id(app),
                                                          app.state_root,
                                                          (u32)dom::launcher_core::LAUNCHER_INSTANCE_TX_OP_UPDATE,
                                                          tx,
                                                          &audit)) {
        out_err = "tx_prepare_failed";
        return false;
    }

    tx.after_manifest = tx.before_manifest;
    for (i = 0u; i < tx.after_manifest.content_entries.size(); ++i) {
        dom::launcher_core::LauncherContentEntry& e = tx.after_manifest.content_entries[i];
        if (!is_pack_like(e.type)) continue;
        {
            const std::string key = pack_key(e.type, e.id);
            std::map<std::string, StagedPackChange>::const_iterator it = app.staged_packs.find(key);
            if (it == app.staged_packs.end()) continue;
            if (it->second.has_enabled) e.enabled = it->second.enabled ? 1u : 0u;
            if (it->second.has_update_policy) e.update_policy = it->second.update_policy;
        }
    }

    if (!dom::launcher_core::launcher_pack_resolve_enabled(app.services, tx.after_manifest, app.state_root, resolved, &resolve_err)) {
        (void)dom::launcher_core::launcher_instance_tx_rollback(app.services, tx, &audit);
        out_err = std::string("pack_resolve_failed;") + resolve_err;
        return false;
    }

    if (!dom::launcher_core::launcher_instance_tx_stage(app.services, tx, &audit)) {
        (void)dom::launcher_core::launcher_instance_tx_rollback(app.services, tx, &audit);
        out_err = "tx_stage_failed";
        return false;
    }
    if (!dom::launcher_core::launcher_instance_tx_verify(app.services, tx, &audit)) {
        (void)dom::launcher_core::launcher_instance_tx_rollback(app.services, tx, &audit);
        out_err = "tx_verify_failed";
        return false;
    }
    if (!dom::launcher_core::launcher_instance_tx_commit(app.services, tx, &audit)) {
        (void)dom::launcher_core::launcher_instance_tx_rollback(app.services, tx, &audit);
        out_err = "tx_commit_failed";
        return false;
    }

    app.staged_packs.clear();
    reload_instance_cache(app);
    return true;
}

static void build_ui(LauncherTuiApp& app) {
    size_t i;
    d_tui_widget* root;
    d_tui_widget* tabs;
    d_tui_widget* body;
    d_tui_widget* left;
    d_tui_widget* center;
    d_tui_widget* right;

    tui_destroy_ui(app);

    app.ui.ctx = d_tui_create();
    if (!app.ui.ctx) {
        app.status = "TUI: failed to create context.";
        return;
    }

    root = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_VERTICAL);

    tabs = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_HORIZONTAL);
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Play", tui_on_activate, tui_alloc_action(app, TUI_ACTION_TAB_PLAY)));
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Instances", tui_on_activate, tui_alloc_action(app, TUI_ACTION_TAB_INSTANCES)));
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Packs", tui_on_activate, tui_alloc_action(app, TUI_ACTION_TAB_PACKS)));
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Options", tui_on_activate, tui_alloc_action(app, TUI_ACTION_TAB_OPTIONS)));
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Diagnostics", tui_on_activate, tui_alloc_action(app, TUI_ACTION_TAB_DIAGNOSTICS)));
    d_tui_widget_add(tabs, d_tui_button(app.ui.ctx, "Quit", tui_on_activate, tui_alloc_action(app, TUI_ACTION_QUIT)));
    d_tui_widget_add(root, tabs);

    body = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_HORIZONTAL);

    /* Left: instances list */
    left = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_VERTICAL);
    d_tui_widget_add(left, d_tui_label(app.ui.ctx, "Instances"));

    app.ui.instance_items.clear();
    for (i = 0u; i < app.instance_ids.size(); ++i) {
        app.ui.instance_items.push_back(app.instance_ids[i]);
    }
    if (app.ui.instance_items.empty()) {
        app.ui.instance_items.push_back("(none)");
    }
    app.ui.instance_cstrs.clear();
    for (i = 0u; i < app.ui.instance_items.size(); ++i) {
        app.ui.instance_cstrs.push_back(app.ui.instance_items[i].c_str());
    }

    app.ui.instances_list = d_tui_list(app.ui.ctx, &app.ui.instance_cstrs[0], (int)app.ui.instance_cstrs.size());
    if (app.ui.instances_list) {
        d_tui_list_set_selection(app.ui.instances_list, (app.selected_instance_index >= 0) ? app.selected_instance_index : 0);
        d_tui_widget_add(left, app.ui.instances_list);
    }
    d_tui_widget_add(body, left);

    center = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_VERTICAL);
    right = d_tui_panel(app.ui.ctx, D_TUI_LAYOUT_VERTICAL);

    {
        const std::string iid = selected_instance_id(app);

        if (app.tab == TUI_TAB_PLAY) {
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Play"));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, iid.empty() ? "instance=(none)" : (std::string("instance=") + iid).c_str()));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("target=") + target_to_string(app)).c_str()));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("offline=") + (app.config.allow_network ? "0" : "1")).c_str()));

            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Toggle Target", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_TOGGLE_TARGET)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Toggle Offline", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_TOGGLE_OFFLINE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Verify", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_VERIFY)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Launch", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_LAUNCH)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Safe Launch", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_SAFE_LAUNCH)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Audit Last", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PLAY_AUDIT_LAST)));
        } else if (app.tab == TUI_TAB_INSTANCES) {
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Instances"));
            if (!iid.empty()) {
                const dom::launcher_core::LauncherInstancePaths paths = dom::launcher_core::launcher_instance_paths_make(app.state_root, iid);
                d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("root=") + paths.instance_root).c_str()));
                d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("manifest=") + paths.manifest_path).c_str()));
                d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("logs=") + paths.logs_root).c_str()));
            } else {
                d_tui_widget_add(center, d_tui_label(app.ui.ctx, "No instance selected."));
            }
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Refresh", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_REFRESH)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Create Empty", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_CREATE_EMPTY)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Create Template", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_CREATE_TEMPLATE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Clone", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_CLONE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Delete", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_DELETE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Import", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_IMPORT)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Export Def", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_EXPORT_DEF)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Export Bundle", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_EXPORT_BUNDLE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Mark Known-Good", tui_on_activate, tui_alloc_action(app, TUI_ACTION_INST_MARK_KG)));
        } else if (app.tab == TUI_TAB_PACKS) {
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Packs"));

            app.ui.pack_items.clear();
            app.ui.pack_keys.clear();
            for (i = 0u; i < app.manifest.content_entries.size(); ++i) {
                const dom::launcher_core::LauncherContentEntry& e = app.manifest.content_entries[i];
                if (!is_pack_like(e.type)) continue;
                const std::string key = pack_key(e.type, e.id);
                const std::map<std::string, StagedPackChange>::const_iterator it = app.staged_packs.find(key);
                const bool staged = (it != app.staged_packs.end());
                u32 eff_enabled = e.enabled ? 1u : 0u;
                u32 eff_policy = e.update_policy;
                if (staged) {
                    if (it->second.has_enabled) eff_enabled = it->second.enabled ? 1u : 0u;
                    if (it->second.has_update_policy) eff_policy = it->second.update_policy;
                }
                std::string line;
                if (staged) line += "* ";
                line += std::string(content_type_to_short(e.type)) + ":" + e.id + " v" + e.version;
                line += std::string(" enabled=") + (eff_enabled ? "1" : "0");
                line += std::string(" policy=") + update_policy_to_string(eff_policy);
                app.ui.pack_items.push_back(line);
                app.ui.pack_keys.push_back(key);
            }
            if (app.ui.pack_items.empty()) {
                app.ui.pack_items.push_back("(no packs/mods)");
            }
            app.ui.pack_cstrs.clear();
            for (i = 0u; i < app.ui.pack_items.size(); ++i) {
                app.ui.pack_cstrs.push_back(app.ui.pack_items[i].c_str());
            }
            app.ui.packs_list = d_tui_list(app.ui.ctx, &app.ui.pack_cstrs[0], (int)app.ui.pack_cstrs.size());
            if (app.ui.packs_list) {
                d_tui_list_set_selection(app.ui.packs_list, (app.selected_pack_index >= 0) ? app.selected_pack_index : 0);
                d_tui_widget_add(center, app.ui.packs_list);
            }

            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Toggle Enabled", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PACK_TOGGLE_ENABLED)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Cycle Policy", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PACK_CYCLE_POLICY)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Apply", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PACK_APPLY)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Discard", tui_on_activate, tui_alloc_action(app, TUI_ACTION_PACK_DISCARD)));
        } else if (app.tab == TUI_TAB_OPTIONS) {
            char buf[64];
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Options"));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("allow_network=") + (app.config.allow_network ? "1" : "0")).c_str()));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("gfx_backend=") + (app.config.gfx_backend.empty() ? "(auto)" : app.config.gfx_backend)).c_str()));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("renderer_api=") + (app.config.renderer_api.empty() ? "(auto)" : app.config.renderer_api)).c_str()));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, (std::string("window_mode=") + window_mode_to_string(app.config.window_mode)).c_str()));
            std::snprintf(buf, sizeof(buf), "width=%u", (unsigned)app.config.window_width);
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, buf));
            std::snprintf(buf, sizeof(buf), "height=%u", (unsigned)app.config.window_height);
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, buf));

            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Toggle Offline", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_TOGGLE_OFFLINE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Set Gfx Backend", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_SET_GFX_BACKEND)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Set Renderer API", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_SET_RENDERER_API)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Cycle Window Mode", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_CYCLE_WINDOW_MODE)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Set Width", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_SET_WIDTH)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Set Height", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_SET_HEIGHT)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Reset Graphics", tui_on_activate, tui_alloc_action(app, TUI_ACTION_OPT_RESET_GRAPHICS)));
        } else if (app.tab == TUI_TAB_DIAGNOSTICS) {
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Diagnostics"));
            d_tui_widget_add(center, d_tui_label(app.ui.ctx, "Runs"));
            app.ui.run_items.clear();
            for (i = 0u; i < app.run_ids.size(); ++i) {
                app.ui.run_items.push_back(app.run_ids[i]);
            }
            if (app.ui.run_items.empty()) {
                app.ui.run_items.push_back("(none)");
            }
            app.ui.run_cstrs.clear();
            for (i = 0u; i < app.ui.run_items.size(); ++i) {
                app.ui.run_cstrs.push_back(app.ui.run_items[i].c_str());
            }
            app.ui.runs_list = d_tui_list(app.ui.ctx, &app.ui.run_cstrs[0], (int)app.ui.run_cstrs.size());
            if (app.ui.runs_list) {
                d_tui_widget_add(center, app.ui.runs_list);
            }
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Refresh", tui_on_activate, tui_alloc_action(app, TUI_ACTION_DIAG_REFRESH)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Audit Last", tui_on_activate, tui_alloc_action(app, TUI_ACTION_DIAG_AUDIT_LAST)));
            d_tui_widget_add(right, d_tui_button(app.ui.ctx, "Diag Bundle", tui_on_activate, tui_alloc_action(app, TUI_ACTION_DIAG_BUNDLE)));
        }
    }

    d_tui_widget_add(body, center);
    d_tui_widget_add(body, right);
    d_tui_widget_add(root, body);

    d_tui_widget_add(root, d_tui_label(app.ui.ctx, app.status.c_str()));
    d_tui_set_root(app.ui.ctx, root);
}

static void refresh_lists_from_ui(LauncherTuiApp& app) {
    if (app.ui.instances_list && !app.instance_ids.empty()) {
        const int sel = d_tui_list_get_selection(app.ui.instances_list);
        if (sel >= 0 && sel < (int)app.instance_ids.size() && sel != app.selected_instance_index) {
            app.selected_instance_index = sel;
            app.staged_packs.clear();
            reload_instance_cache(app);
        }
    }
    if (app.ui.packs_list && !app.ui.pack_keys.empty()) {
        const int sel = d_tui_list_get_selection(app.ui.packs_list);
        if (sel >= 0 && sel < (int)app.ui.pack_keys.size()) {
            app.selected_pack_index = sel;
        }
    }
}

static void handle_action(LauncherTuiApp& app, TuiAction action, int& io_running) {
    const std::string instance_id = selected_instance_id(app);
    std::string out_text;

    if (action == TUI_ACTION_QUIT) {
        io_running = 0;
        return;
    }
    if (action == TUI_ACTION_TAB_PLAY) { app.tab = TUI_TAB_PLAY; return; }
    if (action == TUI_ACTION_TAB_INSTANCES) { app.tab = TUI_TAB_INSTANCES; return; }
    if (action == TUI_ACTION_TAB_PACKS) { app.tab = TUI_TAB_PACKS; return; }
    if (action == TUI_ACTION_TAB_OPTIONS) { app.tab = TUI_TAB_OPTIONS; return; }
    if (action == TUI_ACTION_TAB_DIAGNOSTICS) { app.tab = TUI_TAB_DIAGNOSTICS; return; }

    if (action == TUI_ACTION_INST_REFRESH || action == TUI_ACTION_DIAG_REFRESH) {
        (void)list_instances(app.state_root, app.instance_ids);
        if (!app.instance_ids.empty()) {
            if (app.selected_instance_index < 0 || app.selected_instance_index >= (int)app.instance_ids.size()) {
                app.selected_instance_index = 0;
            }
        } else {
            app.selected_instance_index = -1;
        }
        reload_instance_cache(app);
        app.status = "Refreshed.";
        return;
    }

    if (action == TUI_ACTION_PLAY_TOGGLE_TARGET) {
        if (app.tools_for_instance.empty()) {
            app.selected_tool_index = -1;
        } else if (app.selected_tool_index < 0) {
            app.selected_tool_index = 0;
        } else {
            app.selected_tool_index += 1;
            if (app.selected_tool_index >= (int)app.tools_for_instance.size()) {
                app.selected_tool_index = -1;
            }
        }
        app.status = std::string("target=") + target_to_string(app);
        return;
    }

    if (action == TUI_ACTION_PLAY_TOGGLE_OFFLINE || action == TUI_ACTION_OPT_TOGGLE_OFFLINE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            dom::launcher_core::LauncherInstanceConfig next = app.config;
            next.allow_network = next.allow_network ? 0u : 1u;
            if (!store_config(app, next)) {
                app.status = "Failed to store config.";
                return;
            }
            app.config = next;
            app.status = std::string("offline=") + (app.config.allow_network ? "0" : "1");
        }
        return;
    }

    if (action == TUI_ACTION_PLAY_VERIFY) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("verify-instance");
            argv.push_back(instance_id);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("verify: ") + kv_get(out_text, "result");
        }
        return;
    }

    if (action == TUI_ACTION_PLAY_LAUNCH || action == TUI_ACTION_PLAY_SAFE_LAUNCH) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back((action == TUI_ACTION_PLAY_SAFE_LAUNCH) ? "safe-mode" : "launch");
            argv.push_back(instance_id);
            argv.push_back(std::string("--target=") + target_to_string(app));
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            if (kv_get(out_text, "refused") == "1") {
                app.status = std::string("refused: ") + kv_get(out_text, "refusal_detail");
            } else {
                app.status = std::string("launch: ") + kv_get(out_text, "result");
            }
        }
        reload_instance_cache(app);
        return;
    }

    if (action == TUI_ACTION_PLAY_AUDIT_LAST || action == TUI_ACTION_DIAG_AUDIT_LAST) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("audit-last");
            argv.push_back(instance_id);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            {
                const std::string line = kv_get(out_text, "selection_summary.line");
                app.status = line.empty() ? "audit-last: ok" : (std::string("last: ") + line);
            }
        }
        return;
    }

    if (action == TUI_ACTION_DIAG_BUNDLE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::string out_root;
            if (!prompt_line("Diag bundle out dir: ", out_root) || out_root.empty()) {
                app.status = "Canceled.";
                return;
            }
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("diag-bundle");
            argv.push_back(instance_id);
            argv.push_back(std::string("--out=") + out_root);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("diag-bundle: ") + kv_get(out_text, "result");
        }
        return;
    }

    if (action == TUI_ACTION_PACK_DISCARD) {
        app.staged_packs.clear();
        app.status = "Discarded staged changes.";
        return;
    }

    if (action == TUI_ACTION_PACK_TOGGLE_ENABLED || action == TUI_ACTION_PACK_CYCLE_POLICY) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        if (app.selected_pack_index < 0 || app.selected_pack_index >= (int)app.ui.pack_keys.size()) {
            app.status = "No pack selected.";
            return;
        }
        {
            const std::string key = app.ui.pack_keys[(size_t)app.selected_pack_index];
            const dom::launcher_core::LauncherContentEntry* base = (const dom::launcher_core::LauncherContentEntry*)0;
            size_t i;
            for (i = 0u; i < app.manifest.content_entries.size(); ++i) {
                const dom::launcher_core::LauncherContentEntry& e = app.manifest.content_entries[i];
                if (!is_pack_like(e.type)) continue;
                if (pack_key(e.type, e.id) == key) { base = &app.manifest.content_entries[i]; break; }
            }
            if (!base) {
                app.status = "Selected entry missing.";
                return;
            }
            StagedPackChange& sc = app.staged_packs[key];
            if (action == TUI_ACTION_PACK_TOGGLE_ENABLED) {
                const u32 cur = base->enabled ? 1u : 0u;
                u32 eff = cur;
                if (sc.has_enabled) eff = sc.enabled ? 1u : 0u;
                sc.has_enabled = 1u;
                sc.enabled = eff ? 0u : 1u;
                if (sc.has_enabled && sc.enabled == cur) sc.has_enabled = 0u;
            } else {
                const u32 curp = base->update_policy;
                u32 effp = curp;
                if (sc.has_update_policy) effp = sc.update_policy;
                sc.has_update_policy = 1u;
                sc.update_policy = cycle_update_policy(effp);
                if (sc.has_update_policy && sc.update_policy == curp) sc.has_update_policy = 0u;
            }
            if (!sc.has_enabled && !sc.has_update_policy) {
                app.staged_packs.erase(key);
            }
        }
        app.status = "Staged.";
        return;
    }

    if (action == TUI_ACTION_PACK_APPLY) {
        std::string apply_err;
        if (!apply_packs_transaction(app, apply_err)) {
            app.status = std::string("Apply failed: ") + apply_err;
        } else {
            app.status = "Applied.";
        }
        return;
    }

    if (action == TUI_ACTION_OPT_CYCLE_WINDOW_MODE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        dom::launcher_core::LauncherInstanceConfig next = app.config;
        next.window_mode = cycle_window_mode(next.window_mode);
        if (!store_config(app, next)) {
            app.status = "Failed to store config.";
            return;
        }
        app.config = next;
        app.status = std::string("window_mode=") + window_mode_to_string(app.config.window_mode);
        return;
    }

    if (action == TUI_ACTION_OPT_SET_GFX_BACKEND) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        std::string val;
        if (!prompt_line("Set gfx backend (empty=auto): ", val)) {
            app.status = "Canceled.";
            return;
        }
        dom::launcher_core::LauncherInstanceConfig next = app.config;
        next.gfx_backend = val;
        if (val.empty()) next.gfx_backend.clear();
        if (!store_config(app, next)) {
            app.status = "Failed to store config.";
            return;
        }
        app.config = next;
        app.status = "Updated gfx backend.";
        return;
    }

    if (action == TUI_ACTION_OPT_SET_RENDERER_API) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        std::string val;
        if (!prompt_line("Set renderer API (empty=auto): ", val)) {
            app.status = "Canceled.";
            return;
        }
        dom::launcher_core::LauncherInstanceConfig next = app.config;
        next.renderer_api = val;
        if (val.empty()) next.renderer_api.clear();
        if (!store_config(app, next)) {
            app.status = "Failed to store config.";
            return;
        }
        app.config = next;
        app.status = "Updated renderer API.";
        return;
    }

    if (action == TUI_ACTION_OPT_SET_WIDTH || action == TUI_ACTION_OPT_SET_HEIGHT) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        std::string line;
        u32 v = 0u;
        if (!prompt_line((action == TUI_ACTION_OPT_SET_WIDTH) ? "Set width (0=auto): " : "Set height (0=auto): ", line)) {
            app.status = "Canceled.";
            return;
        }
        if (!line.empty() && !parse_u32_dec(line, v)) {
            app.status = "Invalid number.";
            return;
        }
        dom::launcher_core::LauncherInstanceConfig next = app.config;
        if (action == TUI_ACTION_OPT_SET_WIDTH) next.window_width = v;
        else next.window_height = v;
        if (!store_config(app, next)) {
            app.status = "Failed to store config.";
            return;
        }
        app.config = next;
        app.status = "Updated.";
        return;
    }

    if (action == TUI_ACTION_OPT_RESET_GRAPHICS) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            int yes = 0;
            if (!prompt_yes_no("Reset graphics overrides? (y/N): ", yes) || !yes) {
                app.status = "Canceled.";
                return;
            }
        }
        {
            dom::launcher_core::LauncherInstanceConfig next = app.config;
            next.gfx_backend.clear();
            next.renderer_api.clear();
            next.window_mode = (u32)dom::launcher_core::LAUNCHER_WINDOW_MODE_AUTO;
            next.window_width = 0u;
            next.window_height = 0u;
            if (!store_config(app, next)) {
                app.status = "Failed to store config.";
                return;
            }
            app.config = next;
            app.status = "Graphics overrides reset.";
        }
        return;
    }

    if (action == TUI_ACTION_INST_CREATE_EMPTY) {
        std::string new_id;
        if (!prompt_line("New instance id: ", new_id) || new_id.empty()) {
            app.status = "Canceled.";
            return;
        }
        if (!dom::launcher_core::launcher_is_safe_id_component(new_id)) {
            app.status = "Unsafe instance id.";
            return;
        }
        {
            dom::launcher_core::LauncherAuditLog audit;
            dom::launcher_core::LauncherInstanceManifest created;
            const dom::launcher_core::LauncherInstanceManifest desired = dom::launcher_core::launcher_instance_manifest_make_empty(new_id);
            if (!dom::launcher_core::launcher_instance_create_instance(app.services, desired, app.state_root, created, &audit)) {
                app.status = "Create failed.";
                return;
            }
        }
        (void)list_instances(app.state_root, app.instance_ids);
        app.status = std::string("Created: ") + new_id;
        return;
    }

    if (action == TUI_ACTION_INST_CREATE_TEMPLATE) {
        std::string templ;
        if (!prompt_line("Template instance id: ", templ) || templ.empty()) {
            app.status = "Canceled.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("create-instance");
            argv.push_back(std::string("--template=") + templ);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("create-instance: ") + kv_get(out_text, "result");
        }
        (void)list_instances(app.state_root, app.instance_ids);
        return;
    }

    if (action == TUI_ACTION_INST_CLONE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("clone-instance");
            argv.push_back(instance_id);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("clone-instance: ") + kv_get(out_text, "result");
        }
        (void)list_instances(app.state_root, app.instance_ids);
        return;
    }

    if (action == TUI_ACTION_INST_DELETE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            int yes = 0;
            if (!prompt_yes_no("Soft-delete selected instance? (y/N): ", yes) || !yes) {
                app.status = "Canceled.";
                return;
            }
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("delete-instance");
            argv.push_back(instance_id);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("delete-instance: ") + kv_get(out_text, "result");
        }
        (void)list_instances(app.state_root, app.instance_ids);
        if (app.selected_instance_index >= (int)app.instance_ids.size()) {
            app.selected_instance_index = app.instance_ids.empty() ? -1 : 0;
        }
        reload_instance_cache(app);
        return;
    }

    if (action == TUI_ACTION_INST_EXPORT_DEF || action == TUI_ACTION_INST_EXPORT_BUNDLE) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("export-instance");
            argv.push_back(instance_id);
            argv.push_back((action == TUI_ACTION_INST_EXPORT_DEF) ? "--mode=definition" : "--mode=bundle");
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("export-instance: ") + kv_get(out_text, "result");
        }
        return;
    }

    if (action == TUI_ACTION_INST_IMPORT) {
        std::string import_root;
        if (!prompt_line("Import dir: ", import_root) || import_root.empty()) {
            app.status = "Canceled.";
            return;
        }
        {
            std::vector<std::string> argv;
            argv.push_back(app.argv0.empty() ? std::string("dominium-launcher") : app.argv0);
            argv.push_back(std::string("--home=") + app.state_root);
            argv.push_back("import-instance");
            argv.push_back(import_root);
            (void)run_control_plane_capture(app.audit_core, app.profile, argv, out_text);
            app.status = std::string("import-instance: ") + kv_get(out_text, "result");
        }
        (void)list_instances(app.state_root, app.instance_ids);
        reload_instance_cache(app);
        return;
    }

    if (action == TUI_ACTION_INST_MARK_KG) {
        if (instance_id.empty()) {
            app.status = "No instance selected.";
            return;
        }
        {
            dom::launcher_core::LauncherAuditLog audit;
            dom::launcher_core::LauncherInstanceManifest updated;
            if (!dom::launcher_core::launcher_instance_mark_known_good(app.services, instance_id, app.state_root, updated, &audit)) {
                app.status = "Mark known-good failed.";
                return;
            }
            app.manifest = updated;
        }
        app.status = "Marked known-good.";
        return;
    }
}

} /* namespace */

int launcher_run_tui(const std::string& argv0,
                     const std::string& state_root,
                     ::launcher_core* audit_core,
                     const dom_profile* profile,
                     int smoke) {
    LauncherTuiApp app;
    int running;

    app.argv0 = argv0;
    app.state_root = state_root.empty() ? std::string(".") : state_root;
    app.audit_core = audit_core;
    app.profile = profile;

    if (audit_core) {
        (void)launcher_core_add_reason(audit_core, "front=tui");
        (void)launcher_core_add_reason(audit_core, smoke ? "tui_smoke=1" : "tui_smoke=0");
    }

    if (smoke) {
        (void)list_instances(app.state_root, app.instance_ids);
        return 0;
    }

    if (dsys_terminal_init() != 0) {
        std::fprintf(stderr, "Error: terminal init failed.\n");
        return 1;
    }

    (void)list_instances(app.state_root, app.instance_ids);
    app.selected_instance_index = app.instance_ids.empty() ? -1 : 0;
    reload_instance_cache(app);
    build_ui(app);

    running = 1;
    while (running) {
        int key;
        const int old_inst = app.selected_instance_index;

        if (app.ui.ctx) {
            d_tui_render(app.ui.ctx);
        }

        key = dsys_terminal_poll_key();
        if (key == 0) {
            dsys_sleep_ms(16);
        } else {
            if (key == 'q' || key == 27) {
                app.pending_action = TUI_ACTION_QUIT;
            } else if (app.ui.ctx) {
                d_tui_handle_key(app.ui.ctx, key);
            }
        }

        refresh_lists_from_ui(app);
        if (old_inst != app.selected_instance_index) {
            build_ui(app);
        }

        if (app.pending_action != TUI_ACTION_NONE) {
            const TuiAction a = app.pending_action;
            app.pending_action = TUI_ACTION_NONE;
            handle_action(app, a, running);
            build_ui(app);
        }
    }

    dsys_terminal_shutdown();
    tui_destroy_ui(app);
    return 0;
}

} /* namespace dom */
