/*
FILE: source/dominium/launcher/dom_launcher_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/dom_launcher_cli
RESPONSIBILITY: Implements `dom_launcher_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>

#include "core/include/launcher_core_api.h"
#include "dom_launcher_app.h"
#include "dom_profile_cli.h"
#include "launcher_control_plane.h"
#include "launcher_tui.h"
#include "dom_shared/os_paths.h"

#include "dominium/version.h"

extern "C" {
#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_state.h"
}

extern "C" {
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
}

namespace {

struct LauncherAuditGuard {
    launcher_core* core;
    int* exit_code;

    LauncherAuditGuard(launcher_core* c, int* ec) : core(c), exit_code(ec) {}

    ~LauncherAuditGuard() {
        if (!core) {
            return;
        }
        if (exit_code) {
            (void)launcher_core_emit_audit(core, *exit_code);
        } else {
            (void)launcher_core_emit_audit(core, 0);
        }
        launcher_core_destroy(core);
        core = 0;
    }
};

struct DsuStateHandle {
    dsu_ctx_t* ctx;
    dsu_state_t* state;

    DsuStateHandle() : ctx(0), state(0) {}

    ~DsuStateHandle() {
        if (state) {
            dsu_state_destroy(ctx, state);
            state = 0;
        }
        if (ctx) {
            dsu_ctx_destroy(ctx);
            ctx = 0;
        }
    }
};

static const char* dsu_status_name(dsu_status_t st) {
    switch (st) {
    case DSU_STATUS_SUCCESS: return "success";
    case DSU_STATUS_INVALID_ARGS: return "invalid_args";
    case DSU_STATUS_IO_ERROR: return "io_error";
    case DSU_STATUS_PARSE_ERROR: return "parse_error";
    case DSU_STATUS_UNSUPPORTED_VERSION: return "unsupported_version";
    case DSU_STATUS_INTEGRITY_ERROR: return "integrity_error";
    case DSU_STATUS_INTERNAL_ERROR: return "internal_error";
    case DSU_STATUS_MISSING_COMPONENT: return "missing_component";
    case DSU_STATUS_UNSATISFIED_DEPENDENCY: return "unsatisfied_dependency";
    case DSU_STATUS_VERSION_CONFLICT: return "version_conflict";
    case DSU_STATUS_EXPLICIT_CONFLICT: return "explicit_conflict";
    case DSU_STATUS_PLATFORM_INCOMPATIBLE: return "platform_incompatible";
    case DSU_STATUS_ILLEGAL_DOWNGRADE: return "illegal_downgrade";
    case DSU_STATUS_INVALID_REQUEST: return "invalid_request";
    default: return "unknown";
    }
}

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        char c = path[i - 1u];
        if (c == '/' || c == '\\') {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static std::string state_path_for_root(const std::string& root) {
    return dom_shared::os_path_join(dom_shared::os_path_join(root, ".dsu"), "installed_state.dsustate");
}

static bool find_state_path_from_exe(std::string& out_state_path,
                                     std::string& out_root,
                                     std::string& out_expected_path) {
    std::string exe_dir = dom_shared::os_get_executable_directory();
    std::string root = exe_dir;
    int i;

    out_state_path.clear();
    out_root.clear();
    out_expected_path.clear();

    for (i = 0; i < 3; ++i) {
        if (!root.empty()) {
            std::string cand = state_path_for_root(root);
            if (out_expected_path.empty()) {
                out_expected_path = cand;
            }
            if (dom_shared::os_file_exists(cand)) {
                out_state_path = cand;
                out_root = root;
                return true;
            }
        }
        root = dirname_of(root);
    }

    return false;
}

static bool load_installed_state(const std::string& state_path,
                                 DsuStateHandle& out_handle,
                                 std::string& out_error) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t* ctx = 0;
    dsu_state_t* state = 0;
    dsu_status_t st;

    out_error.clear();

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);

    st = dsu_ctx_create(&cfg, &cbs, 0, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        out_error = std::string("ctx_create_failed:") + dsu_status_name(st);
        return false;
    }

    st = dsu_state_load(ctx, state_path.c_str(), &state);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_ctx_destroy(ctx);
        out_error = std::string("state_load_failed:") + dsu_status_name(st);
        return false;
    }

    st = dsu_state_validate(state);
    if (st != DSU_STATUS_SUCCESS) {
        dsu_state_destroy(ctx, state);
        dsu_ctx_destroy(ctx);
        out_error = std::string("state_invalid:") + dsu_status_name(st);
        return false;
    }

    out_handle.ctx = ctx;
    out_handle.state = state;
    return true;
}

static void print_state_recovery(const std::string& state_path, const std::string& detail) {
    const char* path = state_path.empty() ? "<state-file>" : state_path.c_str();
    std::fprintf(stderr, "Launcher error: installed state missing or invalid.\n");
    std::fprintf(stderr, "State file: %s\n", path);
    if (!detail.empty()) {
        std::fprintf(stderr, "Detail: %s\n", detail.c_str());
    }
    std::fprintf(stderr, "Recovery:\n");
    std::fprintf(stderr, "  1) dominium-setup verify --state \"%s\" --format json\n", path);
    std::fprintf(stderr, "  2) If verify reports issues, run:\n");
    std::fprintf(stderr, "     dominium-setup plan --manifest <manifest> --state \"%s\" --op repair --out repair.dsuplan\n", path);
    std::fprintf(stderr, "     dominium-setup apply --plan repair.dsuplan\n");
}

static bool ensure_installed_state(std::string& out_state_path,
                                   std::string& out_install_root,
                                   std::string& out_error) {
    std::string expected;
    DsuStateHandle handle;

    out_state_path.clear();
    out_install_root.clear();
    out_error.clear();

    if (!find_state_path_from_exe(out_state_path, out_install_root, expected)) {
        out_state_path = expected;
        out_error = "state_not_found";
        return false;
    }

    if (!load_installed_state(out_state_path, handle, out_error)) {
        return false;
    }

    {
        const char* root = dsu_state_primary_install_root(handle.state);
        if (!root || !root[0]) {
            out_error = "state_missing_install_root";
            return false;
        }
        out_install_root = root;
    }

    if (!dom_shared::os_directory_exists(out_install_root)) {
        out_error = "install_root_missing";
        return false;
    }

    return true;
}

static std::string add_exe_suffix(const std::string& base) {
#if defined(_WIN32) || defined(_WIN64)
    if (base.size() >= 4u) {
        const std::string tail = base.substr(base.size() - 4u);
        if (tail == ".exe" || tail == ".EXE") {
            return base;
        }
    }
    return base + ".exe";
#else
    return base;
#endif
}

static int run_state_smoke_test(const char* state_arg) {
    std::string state_path;
    std::string install_root;
    std::string expected;
    std::string err;
    DsuStateHandle handle;
    dsu_u32 component_count = 0u;
    dsu_u32 pack_count = 0u;
    dsu_u32 i;

    if (state_arg && state_arg[0]) {
        state_path = state_arg;
    } else {
        if (!find_state_path_from_exe(state_path, install_root, expected)) {
            state_path = expected;
        }
    }

    if (state_path.empty() || !dom_shared::os_file_exists(state_path)) {
        print_state_recovery(state_path, "state_not_found");
        return 3;
    }

    if (!load_installed_state(state_path, handle, err)) {
        print_state_recovery(state_path, err);
        return 3;
    }

    {
        const char* root = dsu_state_primary_install_root(handle.state);
        if (!root || !root[0]) {
            print_state_recovery(state_path, "state_missing_install_root");
            return 3;
        }
        install_root = root;
    }

    if (!dom_shared::os_directory_exists(install_root)) {
        print_state_recovery(state_path, "install_root_missing");
        return 3;
    }

    component_count = dsu_state_component_count(handle.state);
    for (i = 0u; i < component_count; ++i) {
        if (dsu_state_component_kind(handle.state, i) == DSU_MANIFEST_COMPONENT_KIND_PACK) {
            pack_count += 1u;
        }
    }

    if (component_count == 0u) {
        std::fprintf(stderr, "Launcher smoke: no components in installed state.\n");
        return 4;
    }

    {
        const std::string bin_dir = dom_shared::os_path_join(install_root, "bin");
        const std::string launcher_bin = dom_shared::os_path_join(bin_dir, add_exe_suffix("dominium-launcher"));
        const std::string game_bin = dom_shared::os_path_join(bin_dir, add_exe_suffix("dominium_game"));

        if (!dom_shared::os_file_exists(launcher_bin)) {
            std::fprintf(stderr, "Launcher smoke: missing %s\n", launcher_bin.c_str());
            return 5;
        }
        if (!dom_shared::os_file_exists(game_bin)) {
            std::fprintf(stderr, "Launcher smoke: missing %s\n", game_bin.c_str());
            return 5;
        }
    }

    std::printf("launcher_smoke: state=%s\n", state_path.c_str());
    std::printf("launcher_smoke: install_root=%s\n", install_root.c_str());
    std::printf("launcher_smoke: components=%u packs=%u\n", (unsigned)component_count, (unsigned)pack_count);
    std::printf("launcher_smoke: critical_paths=ok\n");
    return 0;
}

static const char* profile_id_from_dom_profile(const dom_profile& p) {
    const bool lockstep = (p.lockstep_strict != 0u);
    switch (p.kind) {
    case DOM_PROFILE_COMPAT:   return lockstep ? "compat.lockstep" : "compat";
    case DOM_PROFILE_BASELINE: return lockstep ? "baseline.lockstep" : "baseline";
    case DOM_PROFILE_PERF:     return lockstep ? "perf.lockstep" : "perf";
    default:                   return lockstep ? "unknown.lockstep" : "unknown";
    }
}

static void audit_record_caps_selection(launcher_core* core, const dom_profile* profile) {
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    char audit_buf[DOM_CAPS_AUDIT_LOG_MAX_BYTES];
    u32 audit_len;
    u32 i;

    if (!core || !profile) {
        return;
    }

    (void)launcher_core_add_reason(core, "caps_select:begin");

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);
    sel_rc = dom_caps_select(profile, &hw, &sel);
    if (sel_rc != DOM_CAPS_OK) {
        (void)launcher_core_add_reason(core, "caps_select:failed");
    } else {
        (void)launcher_core_add_reason(core, "caps_select:ok");
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (e->subsystem_id == DOM_SUBSYS_DUI) {
            /* UI backends may fall back at runtime; record the final selection after init. */
            continue;
        }
        (void)launcher_core_add_selected_backend(core,
                                                 e->subsystem_id,
                                                 e->subsystem_name ? e->subsystem_name : "",
                                                 e->backend_name ? e->backend_name : "",
                                                 (u32)e->determinism,
                                                 (u32)e->perf_class,
                                                 e->backend_priority,
                                                 e->chosen_by_override);
    }

    std::memset(audit_buf, 0, sizeof(audit_buf));
    audit_len = (u32)(sizeof(audit_buf) - 1u);
    if (dom_caps_get_audit_log(&sel, audit_buf, &audit_len) == DOM_CAPS_OK) {
        audit_buf[(audit_len < (u32)sizeof(audit_buf)) ? audit_len : ((u32)sizeof(audit_buf) - 1u)] = '\0';
        (void)launcher_core_add_reason(core, audit_buf);
    }
}

dom::LauncherMode parse_mode(const char *text, dom::LauncherMode def_mode) {
    if (!text) {
        return def_mode;
    }
    if (std::strcmp(text, "gui") == 0) return dom::LAUNCHER_MODE_GUI;
    if (std::strcmp(text, "tui") == 0) return dom::LAUNCHER_MODE_TUI;
    if (std::strcmp(text, "cli") == 0) return dom::LAUNCHER_MODE_CLI;
    return def_mode;
}

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

static const char* selection_backend_name(const dom_selection& sel, dom_subsystem_id subsystem_id) {
    u32 i;
    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (e->subsystem_id == subsystem_id) {
            return e->backend_name ? e->backend_name : "";
        }
    }
    return "";
}

static dgfx_backend_t dgfx_backend_from_name(const char* backend_name) {
    if (str_ieq(backend_name, "soft")) return DGFX_BACKEND_SOFT;
    if (str_ieq(backend_name, "dx9")) return DGFX_BACKEND_DX9;
    if (str_ieq(backend_name, "dx11")) return DGFX_BACKEND_DX11;
    if (str_ieq(backend_name, "gl2")) return DGFX_BACKEND_GL2;
    if (str_ieq(backend_name, "vk1")) return DGFX_BACKEND_VK1;
    if (str_ieq(backend_name, "metal")) return DGFX_BACKEND_METAL;
    if (str_ieq(backend_name, "gdi")) return DGFX_BACKEND_GDI;
    if (str_ieq(backend_name, "null")) return DGFX_BACKEND_NULL;
    return DGFX_BACKEND_SOFT;
}

static bool copy_cstr_bounded(char* dst, size_t cap, const char* src) {
    size_t n;
    if (!dst || cap == 0u) {
        return false;
    }
    if (!src) {
        dst[0] = '\0';
        return true;
    }
    n = std::strlen(src);
    if (n >= cap) {
        return false;
    }
    std::memcpy(dst, src, n);
    dst[n] = '\0';
    return true;
}

static void force_profile_gfx_backend(dom_profile& profile, const char* backend_name) {
    u32 i;

    (void)copy_cstr_bounded(profile.preferred_gfx_backend,
                            sizeof(profile.preferred_gfx_backend),
                            backend_name);

    for (i = 0u; i < profile.override_count; ++i) {
        dom_profile_override* ov = &profile.overrides[i];
        if (std::strcmp(ov->subsystem_key, "gfx") == 0) {
            (void)copy_cstr_bounded(ov->backend_name, sizeof(ov->backend_name), backend_name);
            return;
        }
    }

    if (profile.override_count < (u32)(sizeof(profile.overrides) / sizeof(profile.overrides[0]))) {
        dom_profile_override* ov = &profile.overrides[profile.override_count];
        std::memset(ov, 0, sizeof(*ov));
        (void)copy_cstr_bounded(ov->subsystem_key, sizeof(ov->subsystem_key), "gfx");
        (void)copy_cstr_bounded(ov->backend_name, sizeof(ov->backend_name), backend_name);
        profile.override_count += 1u;
    }
}

static const char* profile_override_backend(const dom_profile& profile, const char* subsystem_key) {
    u32 i;
    if (!subsystem_key || !subsystem_key[0]) {
        return "";
    }
    for (i = 0u; i < profile.override_count; ++i) {
        const dom_profile_override* ov = &profile.overrides[i];
        if (std::strcmp(ov->subsystem_key, subsystem_key) == 0) {
            return ov->backend_name;
        }
    }
    return "";
}

static void remove_profile_override(dom_profile& profile, const char* subsystem_key) {
    u32 i;
    if (!subsystem_key || !subsystem_key[0]) {
        return;
    }
    for (i = 0u; i < profile.override_count; ++i) {
        dom_profile_override* ov = &profile.overrides[i];
        if (std::strcmp(ov->subsystem_key, subsystem_key) == 0) {
            u32 j;
            for (j = i; (j + 1u) < profile.override_count; ++j) {
                profile.overrides[j] = profile.overrides[j + 1u];
            }
            if (profile.override_count > 0u) {
                std::memset(&profile.overrides[profile.override_count - 1u], 0, sizeof(profile.overrides[0]));
                profile.override_count -= 1u;
            }
            return;
        }
    }
}

static void force_profile_ui_backend(dom_profile& profile, const char* backend_name) {
    u32 i;

    for (i = 0u; i < profile.override_count; ++i) {
        dom_profile_override* ov = &profile.overrides[i];
        if (std::strcmp(ov->subsystem_key, "ui") == 0) {
            (void)copy_cstr_bounded(ov->backend_name, sizeof(ov->backend_name), backend_name);
            return;
        }
    }

    if (profile.override_count < (u32)(sizeof(profile.overrides) / sizeof(profile.overrides[0]))) {
        dom_profile_override* ov = &profile.overrides[profile.override_count];
        std::memset(ov, 0, sizeof(*ov));
        (void)copy_cstr_bounded(ov->subsystem_key, sizeof(ov->subsystem_key), "ui");
        (void)copy_cstr_bounded(ov->backend_name, sizeof(ov->backend_name), backend_name);
        profile.override_count += 1u;
    }
}

static bool find_backend_desc(dom_subsystem_id subsystem_id, const char* backend_name, dom_backend_desc& out_desc) {
    u32 i;
    u32 count;
    dom_backend_desc desc;
    if (!backend_name || !backend_name[0]) {
        return false;
    }
    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != subsystem_id) {
            continue;
        }
        if (!desc.backend_name) {
            continue;
        }
        if (!str_ieq(desc.backend_name, backend_name)) {
            continue;
        }
        out_desc = desc;
        return true;
    }
    return false;
}

static void audit_record_ui_backend(launcher_core* core, const dom_profile* profile, const dom::DomLauncherApp& app) {
    dom_backend_desc desc;
    const std::string& backend = app.ui_backend_selected();
    const std::string& fallback = app.ui_fallback_note();
    const u64 caps = app.ui_caps_selected();
    const u32 caps_lo = (u32)(caps & 0xffffffffu);
    const u32 caps_hi = (u32)((caps >> 32u) & 0xffffffffu);
    char buf[128];
    u32 chosen_by_override = 0u;

    if (!core) {
        return;
    }
    if (backend.empty()) {
        return;
    }

    (void)launcher_core_add_reason(core, (std::string("ui_backend=") + backend).c_str());
    std::snprintf(buf, sizeof(buf), "ui_caps_hi=0x%08X ui_caps_lo=0x%08X", (unsigned)caps_hi, (unsigned)caps_lo);
    (void)launcher_core_add_reason(core, buf);
    if (!fallback.empty()) {
        (void)launcher_core_add_reason(core, fallback.c_str());
    }

    if (profile && fallback.empty()) {
        const char* ov = profile_override_backend(*profile, "ui");
        if (ov && ov[0] && str_ieq(ov, backend.c_str())) {
            chosen_by_override = 1u;
        }
    }

    if (find_backend_desc(DOM_SUBSYS_DUI, backend.c_str(), desc)) {
        (void)launcher_core_add_selected_backend(core,
                                                 desc.subsystem_id,
                                                 desc.subsystem_name ? desc.subsystem_name : "",
                                                 desc.backend_name ? desc.backend_name : "",
                                                 (u32)desc.determinism,
                                                 (u32)desc.perf_class,
                                                 desc.backend_priority,
                                                 chosen_by_override);
    }
}

static int run_launcher_smoke_gui(const dom::ProfileCli& profile_cli) {
    const u32 max_frames = 120u;
    const u64 max_us = 2000000ull;

    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    const char* gfx_backend_name;
    dom_profile smoke_profile;
    const dom_profile* effective_profile = &profile_cli.profile;

    smoke_profile = profile_cli.profile;
    if (profile_cli.profile.lockstep_strict != 0u) {
        force_profile_gfx_backend(smoke_profile, "soft");
        effective_profile = &smoke_profile;
    }

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    if (dom_hw_caps_probe_host(&hw) != 0) {
        std::memset(&hw, 0, sizeof(hw));
    }

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(dom_selection);

    sel_rc = dom_caps_select(effective_profile, &hw, &sel);

    /* Required smoke output (selection audit implied). */
    dom::print_caps(stdout);
    (void)dom::print_selection(*effective_profile, stdout, stderr);
    std::fprintf(stdout, "schema: sim_id=0x%016llx\n", (unsigned long long)dom_sim_schema_id());

    if (sel_rc != DOM_CAPS_OK) {
        return 1;
    }

    gfx_backend_name = selection_backend_name(sel, DOM_SUBSYS_DGFX);
    if (!gfx_backend_name || !gfx_backend_name[0]) {
        gfx_backend_name = "soft";
    }

    if (!d_system_init("win32")) {
        std::fprintf(stderr, "Launcher smoke: d_system_init failed.\n");
        return 3;
    }

    {
        dgfx_desc desc;
        std::memset(&desc, 0, sizeof(desc));
        desc.backend = dgfx_backend_from_name(gfx_backend_name);
        desc.native_window = d_system_get_native_window_handle();
        desc.width = 800;
        desc.height = 600;
        desc.fullscreen = 0;
        desc.vsync = 0;

        if (!desc.native_window) {
            std::fprintf(stderr, "Launcher smoke: no native window handle.\n");
            d_system_shutdown();
            return 3;
        }
        if (!dgfx_init(&desc)) {
            std::fprintf(stderr, "Launcher smoke: dgfx_init failed (gfx=%s).\n", gfx_backend_name);
            d_system_shutdown();
            return 4;
        }
    }

    {
        u64 start_us = dsys_time_now_us();
        u32 frame = 0u;
        int running = 1;

        while (running) {
            d_sys_event ev;
            d_gfx_cmd_buffer* buf;
            d_gfx_viewport vp;
            d_gfx_draw_text_cmd title;
            d_gfx_draw_rect_cmd r;
            i32 w = 800;
            i32 h = 600;
            u32 select_idx;
            i32 x0;
            i32 y0;
            i32 bw;
            i32 bh;
            i32 gap;

            if (frame >= max_frames) {
                break;
            }
            if ((dsys_time_now_us() - start_us) >= max_us) {
                break;
            }

            if (d_system_pump_events() != 0) {
                break;
            }

            while (d_system_poll_event(&ev) > 0) {
                if (ev.type == D_SYS_EVENT_QUIT) {
                    running = 0;
                    break;
                }
                if (ev.type == D_SYS_EVENT_KEY_DOWN && ev.u.key.key == D_SYS_KEY_ESCAPE) {
                    running = 0;
                    break;
                }
            }
            if (!running) {
                break;
            }

            buf = d_gfx_cmd_buffer_begin();
            if (!buf) {
                break;
            }

            d_gfx_get_surface_size(&w, &h);

            vp.x = 0;
            vp.y = 0;
            vp.w = w;
            vp.h = h;
            d_gfx_cmd_set_viewport(buf, &vp);

            {
                d_gfx_color bg;
                bg.a = 255; bg.r = 18; bg.g = 18; bg.b = 22;
                d_gfx_cmd_clear(buf, bg);
            }

            std::memset(&title, 0, sizeof(title));
            title.x = 24;
            title.y = 18;
            title.text = "Dominium Launcher Smoke GUI";
            title.color.a = 255; title.color.r = 230; title.color.g = 230; title.color.b = 230;
            d_gfx_cmd_draw_text(buf, &title);

            x0 = (w / 2) - 160;
            y0 = 90;
            bw = 320;
            bh = 56;
            gap = 18;

            std::memset(&r, 0, sizeof(r));
            r.w = bw;
            r.h = bh;
            r.color.a = 255; r.color.r = 52; r.color.g = 56; r.color.b = 64;

            r.x = x0;
            r.y = y0 + (bh + gap) * 0;
            d_gfx_cmd_draw_rect(buf, &r);
            r.y = y0 + (bh + gap) * 1;
            d_gfx_cmd_draw_rect(buf, &r);
            r.y = y0 + (bh + gap) * 2;
            d_gfx_cmd_draw_rect(buf, &r);

            select_idx = (frame / 20u) % 3u;
            r.x = x0 - 6;
            r.y = y0 + (bh + gap) * (i32)select_idx - 6;
            r.w = bw + 12;
            r.h = bh + 12;
            r.color.a = 255; r.color.r = 232; r.color.g = 196; r.color.b = 64;
            d_gfx_cmd_draw_rect(buf, &r);

            r.x = 18 + ((i32)(frame % 60u) * 6);
            r.y = h - 36;
            r.w = 48;
            r.h = 10;
            r.color.a = 255; r.color.r = 92; r.color.g = 164; r.color.b = 220;
            d_gfx_cmd_draw_rect(buf, &r);

            d_gfx_cmd_buffer_end(buf);
            d_gfx_submit(buf);
            d_gfx_present();
            d_system_sleep_ms(16);
            frame += 1u;
        }
    }

    dgfx_shutdown();
    d_system_shutdown();
    return 0;
}

} // namespace

int main(int argc, char **argv) {
    int exit_code = 0;
    dom::LauncherConfig cfg;
    dom::DomLauncherApp app;
    dom::ProfileCli profile_cli;
    std::string profile_err;
    int i;

    launcher_core_desc_v1 lc_desc;
    launcher_core* lc = 0;
    std::memset(&lc_desc, 0, sizeof(lc_desc));
    lc_desc.struct_size = (u32)sizeof(lc_desc);
    lc_desc.struct_version = LAUNCHER_CORE_DESC_VERSION;
    lc_desc.services = launcher_services_null_v1();
    lc_desc.audit_output_path = 0; /* core generates a unique per-run name in CWD */
    lc_desc.selected_profile_id = 0;
    lc_desc.argv = (const char* const*)argv;
    lc_desc.argv_count = (u32)((argc > 0) ? argc : 0);
    lc = launcher_core_create(&lc_desc);
    LauncherAuditGuard audit_guard(lc, &exit_code);

    if (lc) {
        (void)launcher_core_set_version_string(lc, DOMINIUM_LAUNCHER_VERSION);
        {
            const char* build_id = dom_build_id();
            if (build_id) {
                (void)launcher_core_set_build_id(lc, build_id);
            }
        }
        {
            const char* git_hash = dom_git_hash();
            if (git_hash) {
                (void)launcher_core_set_git_hash(lc, git_hash);
            }
        }
        {
            const char* toolchain_id = dom_toolchain_id();
            if (toolchain_id) {
                std::string why = std::string("toolchain_id=") + toolchain_id;
                (void)launcher_core_add_reason(lc, why.c_str());
            }
        }
    }

    dom::init_default_profile_cli(profile_cli);
    if (!dom::parse_profile_cli_args(argc, argv, profile_cli, profile_err)) {
        std::fprintf(stderr, "Error: %s\n", profile_err.c_str());
        if (lc) {
            std::string why = std::string("profile_cli_parse_failed:") + profile_err;
            (void)launcher_core_add_reason(lc, why.c_str());
        }
        exit_code = 2;
        return exit_code;
    }

    {
        const char* ui_val = 0;
        for (i = 1; i < argc; ++i) {
            const char* arg = argv[i];
            if (!arg) {
                continue;
            }
            if (std::strncmp(arg, "--ui=", 5) == 0) {
                ui_val = arg + 5;
                break;
            }
        }
        if (ui_val && ui_val[0]) {
            if (str_ieq(ui_val, "native")) {
                remove_profile_override(profile_cli.profile, "ui");
            } else if (str_ieq(ui_val, "dgfx")) {
                force_profile_ui_backend(profile_cli.profile, "dgfx");
            } else if (str_ieq(ui_val, "null")) {
                force_profile_ui_backend(profile_cli.profile, "null");
            } else {
                std::fprintf(stderr, "Error: unknown --ui value; expected native|dgfx|null.\n");
                if (lc) {
                    (void)launcher_core_add_reason(lc, "ui_flag_invalid");
                }
                exit_code = 2;
                return exit_code;
            }
            if (lc) {
                std::string why = std::string("ui_request=") + ui_val;
                (void)launcher_core_add_reason(lc, why.c_str());
            }
        }
    }

    if (lc) {
        (void)launcher_core_select_profile_id(lc, profile_id_from_dom_profile(profile_cli.profile), "dom_profile_cli");
        (void)launcher_core_add_reason(lc, (profile_cli.profile.lockstep_strict != 0u) ? "lockstep_strict=1" : "lockstep_strict=0");
        audit_record_caps_selection(lc, &profile_cli.profile);
    }

    {
        bool smoke_gui = false;
        bool smoke_tui = false;
        bool smoke_state = false;
        const char* home_val = 0;
        const char* state_val = 0;
        for (i = 1; i < argc; ++i) {
            const char* arg = argv[i];
            if (!arg) {
                continue;
            }
            if (std::strncmp(arg, "--home=", 7) == 0) {
                home_val = arg + 7;
            }
            if (std::strncmp(arg, "--state=", 8) == 0) {
                state_val = arg + 8;
                continue;
            }
            if (std::strcmp(arg, "--state") == 0 && (i + 1) < argc) {
                state_val = argv[++i];
                continue;
            }
            if (std::strcmp(arg, "--smoke-test") == 0) {
                smoke_state = true;
                continue;
            }
            if (std::strcmp(arg, "--smoke-gui") == 0) {
                smoke_gui = true;
                continue;
            }
            if (std::strcmp(arg, "--smoke-tui") == 0) {
                smoke_tui = true;
                continue;
            }
        }
        if (smoke_state) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "mode:smoke-state");
            }
            exit_code = run_state_smoke_test(state_val);
            return exit_code;
        }
        if (smoke_gui) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "mode:smoke-gui");
            }
            exit_code = run_launcher_smoke_gui(profile_cli);
            return exit_code;
        }
        if (smoke_tui) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "mode:smoke-tui");
            }
            const std::string home = (home_val && home_val[0]) ? std::string(home_val) : std::string(".");
            const std::string argv0 = (argc > 0 && argv && argv[0]) ? std::string(argv[0]) : std::string("dominium-launcher");
            exit_code = dom::launcher_run_tui(argv0, home, lc, &profile_cli.profile, 1);
            return exit_code;
        }
    }

    if (profile_cli.print_caps) {
        if (lc) {
            (void)launcher_core_add_reason(lc, "action:print_caps");
        }
        dom::print_caps(stdout);
        exit_code = 0;
        return exit_code;
    }
    if (profile_cli.print_selection) {
        if (lc) {
            (void)launcher_core_add_reason(lc, "action:print_selection");
        }
        dom::print_caps(stdout);
        exit_code = dom::print_selection(profile_cli.profile, stdout, stderr);
        return exit_code;
    }

    {
        std::string state_path;
        std::string install_root;
        std::string state_err;
        if (!ensure_installed_state(state_path, install_root, state_err)) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "state_invalid");
            }
            print_state_recovery(state_path, state_err);
            exit_code = 3;
            return exit_code;
        }
        if (lc) {
            (void)launcher_core_add_reason(lc, (std::string("state_path=") + state_path).c_str());
            (void)launcher_core_add_reason(lc, (std::string("install_root=") + install_root).c_str());
        }
    }

    /* Command-style control plane (no UI required). */
    {
        dom::ControlPlaneRunResult cpr = dom::launcher_control_plane_try_run(argc,
                                                                             argv,
                                                                             lc,
                                                                             &profile_cli.profile,
                                                                             stdout,
                                                                             stderr);
        if (cpr.handled) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "mode:control_plane");
            }
            exit_code = cpr.exit_code;
            return exit_code;
        }
    }

    cfg.home.clear();
    cfg.argv0 = (argc > 0 && argv && argv[0]) ? std::string(argv[0]) : std::string();
    cfg.mode = dom::LAUNCHER_MODE_GUI;
    cfg.action.clear();
    cfg.instance_id.clear();
    cfg.product.clear();
    cfg.product_mode = "gui";

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }
        if (std::strncmp(arg, "--home=", 7) == 0) {
            cfg.home = arg + 7;
        } else if (std::strncmp(arg, "--mode=", 7) == 0) {
            cfg.mode = parse_mode(arg + 7, cfg.mode);
        } else if (std::strncmp(arg, "--front=", 8) == 0) {
            cfg.mode = parse_mode(arg + 8, cfg.mode);
        } else if (std::strncmp(arg, "--product-mode=", 16) == 0) {
            cfg.product_mode = arg + 16;
        } else if (std::strncmp(arg, "--action=", 9) == 0) {
            cfg.action = arg + 9;
        } else if (std::strncmp(arg, "--instance=", 11) == 0) {
            cfg.instance_id = arg + 11;
        } else if (std::strncmp(arg, "--product=", 10) == 0) {
            cfg.product = arg + 10;
        }
    }

    if (cfg.mode == dom::LAUNCHER_MODE_TUI) {
        if (lc) {
            (void)launcher_core_add_reason(lc, "front=tui");
        }
        exit_code = dom::launcher_run_tui(cfg.argv0, cfg.home, lc, &profile_cli.profile, 0);
        return exit_code;
    }

    if (!app.init_from_cli(cfg, &profile_cli.profile)) {
        std::printf("Launcher: failed to initialize.\n");
        if (lc) {
            (void)launcher_core_add_reason(lc, "launcher_init_failed");
        }
        exit_code = 1;
        return exit_code;
    }
    if (lc) {
        audit_record_ui_backend(lc, &profile_cli.profile, app);
    }

    app.run();
    app.shutdown();
    exit_code = 0;
    return exit_code;
}
