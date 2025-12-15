#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_app.h"
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

static int run_game_smoke_gui(const dom::ProfileCli& profile_cli) {
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
        std::fprintf(stderr, "Game smoke: d_system_init failed.\n");
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
            std::fprintf(stderr, "Game smoke: no native window handle.\n");
            d_system_shutdown();
            return 3;
        }
        if (!dgfx_init(&desc)) {
            std::fprintf(stderr, "Game smoke: dgfx_init failed (gfx=%s).\n", gfx_backend_name);
            d_system_shutdown();
            return 4;
        }
    }

    {
        u64 start_us = dsys_time_now_us();
        u32 frame = 0u;
        u32 tick = 0u;
        int running = 1;

        while (running) {
            d_sys_event ev;
            d_gfx_cmd_buffer* buf;
            d_gfx_viewport vp;
            d_gfx_draw_text_cmd title;
            d_gfx_draw_rect_cmd r;
            i32 w = 800;
            i32 h = 600;
            i32 hud_w;
            i32 hud_h;
            i32 sq;
            i32 x;
            i32 y;

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
                bg.a = 255; bg.r = 10; bg.g = 14; bg.b = 18;
                d_gfx_cmd_clear(buf, bg);
            }

            std::memset(&title, 0, sizeof(title));
            title.x = 20;
            title.y = 18;
            title.text = "Dominium Game Smoke GUI";
            title.color.a = 255; title.color.r = 230; title.color.g = 230; title.color.b = 230;
            d_gfx_cmd_draw_text(buf, &title);

            hud_w = (w > 420) ? 420 : (w - 40);
            if (hud_w < 220) hud_w = (w > 60) ? (w - 40) : w;
            hud_h = 110;
            if (hud_h > h - 40) hud_h = (h > 40) ? (h - 40) : h;

            std::memset(&r, 0, sizeof(r));
            r.x = 20;
            r.y = 54;
            r.w = hud_w;
            r.h = hud_h;
            r.color.a = 255; r.color.r = 34; r.color.g = 38; r.color.b = 46;
            d_gfx_cmd_draw_rect(buf, &r);

            r.x = 20;
            r.y = 54 + hud_h + 14;
            r.w = hud_w;
            r.h = 28;
            r.color.a = 255; r.color.r = 52; r.color.g = 56; r.color.b = 64;
            d_gfx_cmd_draw_rect(buf, &r);

            sq = 18;
            if (w < 80) w = 80;
            if (h < 80) h = 80;

            x = 40 + (i32)((tick * 5u) % (u32)(w - 80 - sq));
            y = 210 + (i32)((tick * 3u) % 140u);
            if (y + sq > h - 24) {
                y = h - 24 - sq;
            }

            r.x = x;
            r.y = y;
            r.w = sq;
            r.h = sq;
            r.color.a = 255; r.color.r = 92; r.color.g = 164; r.color.b = 220;
            d_gfx_cmd_draw_rect(buf, &r);

            d_gfx_cmd_buffer_end(buf);
            d_gfx_submit(buf);
            d_gfx_present();

            d_system_sleep_ms(16);
            frame += 1u;
            tick += 1u;
        }
    }

    dgfx_shutdown();
    d_system_shutdown();
    return 0;
}

} // namespace

namespace dom {

void init_default_game_config(GameConfig &cfg) {
    cfg.dominium_home.clear();
    cfg.instance_id = "demo";
    cfg.connect_addr.clear();
    cfg.net_port = 7777u;
    cfg.mode = GAME_MODE_GUI;
    cfg.server_mode = SERVER_OFF;
    cfg.demo_mode = false;
    cfg.platform_backend.clear();
    cfg.gfx_backend.clear();
    cfg.tick_rate_hz = 60u;
    cfg.dev_mode = false;
    cfg.deterministic_test = false;
    cfg.replay_record_path.clear();
    cfg.replay_play_path.clear();
}

static int str_ieq(const char *a, const char *b) {
    size_t i;
    size_t len_a;
    size_t len_b;
    if (!a || !b) {
        return 0;
    }
    len_a = std::strlen(a);
    len_b = std::strlen(b);
    if (len_a != len_b) {
        return 0;
    }
    for (i = 0u; i < len_a; ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = static_cast<char>(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = static_cast<char>(cb - 'A' + 'a');
        if (ca != cb) {
            return 0;
        }
    }
    return 1;
}

static bool parse_tick_rate(const char *val, unsigned &out_rate) {
    char *endp = 0;
    unsigned long v;
    if (!val) {
        return false;
    }
    v = std::strtoul(val, &endp, 10);
    if (val == endp) {
        return false;
    }
    out_rate = static_cast<unsigned>(v);
    return true;
}

bool parse_game_cli_args(int argc, char **argv, GameConfig &cfg) {
    int i;
    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }

        if (std::strncmp(arg, "--mode=", 7) == 0) {
            const char *val = arg + 7;
            if (str_ieq(val, "gui")) cfg.mode = GAME_MODE_GUI;
            else if (str_ieq(val, "tui")) cfg.mode = GAME_MODE_TUI;
            else if (str_ieq(val, "headless")) cfg.mode = GAME_MODE_HEADLESS;
            else {
                std::printf("Unknown mode '%s'\n", val);
                return false;
            }
            continue;
        }
        if (str_ieq(arg, "--server")) {
            cfg.server_mode = SERVER_DEDICATED;
            if (cfg.mode == GAME_MODE_GUI) {
                cfg.mode = GAME_MODE_HEADLESS;
            }
            continue;
        }
        if (str_ieq(arg, "--listen")) {
            cfg.server_mode = SERVER_LISTEN;
            continue;
        }
        if (std::strncmp(arg, "--server=", 9) == 0) {
            const char *val = arg + 9;
            if (str_ieq(val, "off")) cfg.server_mode = SERVER_OFF;
            else if (str_ieq(val, "listen")) cfg.server_mode = SERVER_LISTEN;
            else if (str_ieq(val, "dedicated")) cfg.server_mode = SERVER_DEDICATED;
            else {
                std::printf("Unknown server mode '%s'\n", val);
                return false;
            }
            continue;
        }
        if (std::strncmp(arg, "--connect=", 10) == 0) {
            cfg.connect_addr = std::string(arg + 10);
            continue;
        }
        if (std::strncmp(arg, "--port=", 7) == 0) {
            unsigned rate = 0u;
            if (!parse_tick_rate(arg + 7, rate) || rate == 0u || rate > 65535u) {
                std::printf("Invalid port '%s'\n", arg + 7);
                return false;
            }
            cfg.net_port = rate;
            continue;
        }
        if (std::strncmp(arg, "--instance=", 11) == 0) {
            cfg.instance_id = std::string(arg + 11);
            continue;
        }
        if (std::strncmp(arg, "--platform=", 11) == 0) {
            cfg.platform_backend = std::string(arg + 11);
            continue;
        }
        if (std::strncmp(arg, "--gfx=", 6) == 0) {
            cfg.gfx_backend = std::string(arg + 6);
            continue;
        }
        if (std::strncmp(arg, "--tickrate=", 11) == 0) {
            unsigned rate = cfg.tick_rate_hz;
            if (!parse_tick_rate(arg + 11, rate)) {
                std::printf("Invalid tickrate '%s'\n", arg + 11);
                return false;
            }
            cfg.tick_rate_hz = rate;
            continue;
        }
        if (std::strncmp(arg, "--home=", 7) == 0) {
            cfg.dominium_home = std::string(arg + 7);
            continue;
        }
        if (str_ieq(arg, "--demo")) {
            cfg.demo_mode = true;
            continue;
        }
        if (str_ieq(arg, "--devmode")) {
            cfg.dev_mode = true;
            cfg.deterministic_test = true;
            continue;
        }
        if (str_ieq(arg, "--deterministic-test")) {
            cfg.deterministic_test = true;
            continue;
        }
        if (std::strncmp(arg, "--record-replay=", 16) == 0) {
            cfg.replay_record_path = std::string(arg + 16);
            continue;
        }
        if (std::strncmp(arg, "--play-replay=", 14) == 0) {
            cfg.replay_play_path = std::string(arg + 14);
            continue;
        }
    }
    return true;
}

} // namespace dom

int main(int argc, char **argv) {
    dom::GameConfig cfg;
    dom::DomGameApp app;
    dom::ProfileCli profile_cli;
    std::string profile_err;

    dom::init_default_profile_cli(profile_cli);
    if (!dom::parse_profile_cli_args(argc, argv, profile_cli, profile_err)) {
        std::printf("Error: %s\n", profile_err.c_str());
        return 2;
    }

    {
        bool smoke_gui = false;
        int i;
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
            return run_game_smoke_gui(profile_cli);
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

    dom::init_default_game_config(cfg);
    if (!dom::parse_game_cli_args(argc, argv, cfg)) {
        return 1;
    }

    if (!app.init_from_cli(cfg)) {
        return 1;
    }

    app.run();
    app.shutdown();
    return 0;
}
