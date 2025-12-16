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

#include "dominium/version.h"

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
        for (i = 1; i < argc; ++i) {
            const char* arg = argv[i];
            if (!arg) {
                continue;
            }
            if (std::strcmp(arg, "--smoke-gui") == 0) {
                smoke_gui = true;
                break;
            }
        }
        if (smoke_gui) {
            if (lc) {
                (void)launcher_core_add_reason(lc, "mode:smoke-gui");
            }
            exit_code = run_launcher_smoke_gui(profile_cli);
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

    cfg.home.clear();
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
