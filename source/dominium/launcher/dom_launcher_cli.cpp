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

#include "dom_launcher_app.h"
#include "dom_profile_cli.h"

extern "C" {
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
}

namespace {

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
    dom::LauncherConfig cfg;
    dom::DomLauncherApp app;
    dom::ProfileCli profile_cli;
    std::string profile_err;
    int i;

    dom::init_default_profile_cli(profile_cli);
    if (!dom::parse_profile_cli_args(argc, argv, profile_cli, profile_err)) {
        std::fprintf(stderr, "Error: %s\n", profile_err.c_str());
        return 2;
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
            return run_launcher_smoke_gui(profile_cli);
        }
    }

    if (profile_cli.print_caps) {
        dom::print_caps(stdout);
        return 0;
    }
    if (profile_cli.print_selection) {
        dom::print_caps(stdout);
        return dom::print_selection(profile_cli.profile, stdout, stderr);
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

    if (!app.init_from_cli(cfg)) {
        std::printf("Launcher: failed to initialize.\n");
        return 1;
    }

    app.run();
    app.shutdown();
    return 0;
}
