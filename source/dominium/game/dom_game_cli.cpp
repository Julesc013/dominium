/*
FILE: source/dominium/game/dom_game_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/dom_game_cli
RESPONSIBILITY: Implements `dom_game_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_cli.h"
#include "dom_game_app.h"
#include "dom_profile_cli.h"

extern "C" {
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
#include "dominium/product_info.h"
#include "dominium/version.h"
}

namespace {

static const u32 DEFAULT_DERIVED_BUDGET_MS = 2u;
static const u32 DEFAULT_DERIVED_BUDGET_IO_BYTES = 256u * 1024u;
static const u32 DEFAULT_DERIVED_BUDGET_JOBS = 4u;
static const u32 DEFAULT_NET_INPUT_DELAY_TICKS = 2u;

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

static int run_game_smoke_gui(const dom_profile& profile) {
    const u32 max_frames = 120u;
    const u64 max_us = 2000000ull;

    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    const char* gfx_backend_name;
    dom_profile smoke_profile;
    const dom_profile* effective_profile = &profile;

    smoke_profile = profile;
    if (profile.lockstep_strict != 0u) {
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

            frame += 1u;
            tick += 1u;
        }
    }

    dgfx_shutdown();
    d_system_shutdown();
    return 0;
}

} // namespace

static bool parse_u32_range(const char *val, u32 min_v, u32 max_v, u32 &out_v) {
    char *endp = 0;
    unsigned long v;
    if (!val) {
        return false;
    }
    v = std::strtoul(val, &endp, 10);
    if (val == endp) {
        return false;
    }
    if (v < min_v || v > max_v) {
        return false;
    }
    out_v = static_cast<u32>(v);
    return true;
}

static void set_error(dom_game_cli_result *out_result, const char *msg) {
    if (!out_result) {
        return;
    }
    out_result->exit_code = 2;
    if (msg && msg[0]) {
        (void)copy_cstr_bounded(out_result->error, sizeof(out_result->error), msg);
    }
}

static void init_profile_defaults(dom_profile &profile) {
    std::memset(&profile, 0, sizeof(profile));
    profile.abi_version = DOM_PROFILE_ABI_VERSION;
    profile.struct_size = static_cast<u32>(sizeof(dom_profile));
    profile.kind = DOM_PROFILE_BASELINE;
    profile.lockstep_strict = 0u;
}

static bool parse_mode(const char *val, dom_game_mode &mode) {
    if (!val) {
        return false;
    }
    if (str_ieq(val, "gui")) {
        mode = DOM_GAME_MODE_GUI;
        return true;
    }
    if (str_ieq(val, "tui")) {
        mode = DOM_GAME_MODE_TUI;
        return true;
    }
    if (str_ieq(val, "headless")) {
        mode = DOM_GAME_MODE_HEADLESS;
        return true;
    }
    return false;
}

static bool parse_server_mode(const char *val, dom_game_server_mode &mode) {
    if (!val) {
        return false;
    }
    if (str_ieq(val, "off")) {
        mode = DOM_GAME_SERVER_OFF;
        return true;
    }
    if (str_ieq(val, "listen")) {
        mode = DOM_GAME_SERVER_LISTEN;
        return true;
    }
    if (str_ieq(val, "dedicated")) {
        mode = DOM_GAME_SERVER_DEDICATED;
        return true;
    }
    return false;
}

static bool parse_session_role(const char *val, dom_game_session_role &role) {
    if (!val) {
        return false;
    }
    if (str_ieq(val, "single")) {
        role = DOM_GAME_SESSION_ROLE_SINGLE;
        return true;
    }
    if (str_ieq(val, "host")) {
        role = DOM_GAME_SESSION_ROLE_HOST;
        return true;
    }
    if (str_ieq(val, "server") || str_ieq(val, "dedicated")) {
        role = DOM_GAME_SESSION_ROLE_DEDICATED_SERVER;
        return true;
    }
    if (str_ieq(val, "client")) {
        role = DOM_GAME_SESSION_ROLE_CLIENT;
        return true;
    }
    return false;
}

static bool parse_session_authority(const char *val, dom_game_session_authority &auth) {
    if (!val) {
        return false;
    }
    if (str_ieq(val, "server") || str_ieq(val, "server-auth") || str_ieq(val, "server_auth")) {
        auth = DOM_GAME_SESSION_AUTH_SERVER;
        return true;
    }
    if (str_ieq(val, "lockstep")) {
        auth = DOM_GAME_SESSION_AUTH_LOCKSTEP;
        return true;
    }
    return false;
}

static bool parse_sys_override(const char *arg, char *out_key, size_t key_cap, const char **out_val) {
    const char *eq;
    size_t key_len;
    if (!arg || !out_key || !out_val) {
        return false;
    }
    if (std::strncmp(arg, "--sys.", 6) != 0) {
        return false;
    }
    eq = std::strchr(arg, '=');
    if (!eq || eq == arg) {
        return false;
    }
    key_len = static_cast<size_t>(eq - (arg + 6));
    if (key_len == 0u || key_len + 1u > key_cap) {
        return false;
    }
    std::memcpy(out_key, arg + 6, key_len);
    out_key[key_len] = '\0';
    *out_val = eq + 1;
    return true;
}

extern "C" {

void dom_game_cli_init_defaults(dom_game_config *out_cfg) {
    if (!out_cfg) {
        return;
    }
    std::memset(out_cfg, 0, sizeof(*out_cfg));
    out_cfg->mode = DOM_GAME_MODE_GUI;
    out_cfg->server_mode = DOM_GAME_SERVER_OFF;
    out_cfg->session_role_set = 0u;
    out_cfg->session_authority_set = 0u;
    out_cfg->session_role = DOM_GAME_SESSION_ROLE_SINGLE;
    out_cfg->session_authority = DOM_GAME_SESSION_AUTH_SERVER;
    out_cfg->session_input_delay = DEFAULT_NET_INPUT_DELAY_TICKS;
    out_cfg->net_port = 7777u;
    out_cfg->tick_rate_hz = 60u;
    out_cfg->deterministic_test = 0u;
    out_cfg->dev_mode = 0u;
    out_cfg->demo_mode = 0u;
    out_cfg->replay_strict_content = 1u;
    out_cfg->dev_allow_ad_hoc_paths = 0u;
    out_cfg->ui_transparent_loading = 0u;
    out_cfg->dev_allow_missing_content = 0u;
    out_cfg->auto_host = 0u;
    out_cfg->headless_ticks = 0u;
    out_cfg->headless_local = 0u;
    out_cfg->derived_budget_ms = DEFAULT_DERIVED_BUDGET_MS;
    out_cfg->derived_budget_io_bytes = DEFAULT_DERIVED_BUDGET_IO_BYTES;
    out_cfg->derived_budget_jobs = DEFAULT_DERIVED_BUDGET_JOBS;
    (void)copy_cstr_bounded(out_cfg->instance_id, sizeof(out_cfg->instance_id), "demo");
    init_profile_defaults(out_cfg->profile);
    out_cfg->handshake_path[0] = '\0';
}

void dom_game_cli_init_result(dom_game_cli_result *out_result) {
    if (!out_result) {
        return;
    }
    std::memset(out_result, 0, sizeof(*out_result));
    out_result->exit_code = 0;
}

int dom_game_cli_parse(int argc, char **argv, dom_game_config *out_cfg, dom_game_cli_result *out_result) {
    dom::ProfileCli profile_cli;
    std::string profile_err;
    int i;

    if (!out_cfg || !out_result) {
        return -1;
    }
    dom_game_cli_init_defaults(out_cfg);
    dom_game_cli_init_result(out_result);

    dom::init_default_profile_cli(profile_cli);
    if (!dom::parse_profile_cli_args(argc, argv, profile_cli, profile_err)) {
        set_error(out_result, profile_err.c_str());
        return -1;
    }
    out_cfg->profile = profile_cli.profile;
    out_result->want_print_caps = profile_cli.print_caps ? 1 : 0;
    out_result->want_print_selection = profile_cli.print_selection ? 1 : 0;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }

        if (std::strcmp(arg, "--help") == 0 || std::strcmp(arg, "-h") == 0) {
            out_result->want_help = 1;
            continue;
        }
        if (std::strcmp(arg, "--capabilities") == 0) {
            out_result->want_capabilities = 1;
            continue;
        }
        if (std::strcmp(arg, "--introspect-json") == 0) {
            out_result->want_introspect_json = 1;
            continue;
        }
        if (std::strcmp(arg, "--version") == 0) {
            out_result->want_version = 1;
            continue;
        }
        if (std::strcmp(arg, "--smoke-gui") == 0) {
            out_result->want_smoke_gui = 1;
            continue;
        }

        if (std::strncmp(arg, "--mode=", 7) == 0) {
            dom_game_mode mode = out_cfg->mode;
            if (!parse_mode(arg + 7, mode)) {
                set_error(out_result, "Unknown --mode value; expected gui|tui|headless.");
                return -1;
            }
            out_cfg->mode = mode;
            continue;
        }
        if (std::strncmp(arg, "--role=", 7) == 0) {
            dom_game_session_role role = out_cfg->session_role;
            if (!parse_session_role(arg + 7, role)) {
                set_error(out_result, "Unknown --role value; expected single|host|server|client.");
                return -1;
            }
            out_cfg->session_role = role;
            out_cfg->session_role_set = 1u;
            continue;
        }
        if (std::strncmp(arg, "--auth=", 7) == 0) {
            dom_game_session_authority auth = out_cfg->session_authority;
            if (!parse_session_authority(arg + 7, auth)) {
                set_error(out_result, "Unknown --auth value; expected server|lockstep.");
                return -1;
            }
            out_cfg->session_authority = auth;
            out_cfg->session_authority_set = 1u;
            continue;
        }
        if (std::strncmp(arg, "--input-delay=", 14) == 0) {
            u32 delay = 0u;
            if (!parse_u32_range(arg + 14, 1u, 256u, delay)) {
                set_error(out_result, "Invalid --input-delay value; expected 1..256.");
                return -1;
            }
            out_cfg->session_input_delay = delay;
            continue;
        }
        if (std::strcmp(arg, "--auto-host") == 0) {
            out_cfg->auto_host = 1u;
            continue;
        }
        if (std::strcmp(arg, "--server") == 0) {
            out_cfg->server_mode = DOM_GAME_SERVER_DEDICATED;
            continue;
        }
        if (std::strcmp(arg, "--listen") == 0) {
            out_cfg->server_mode = DOM_GAME_SERVER_LISTEN;
            continue;
        }
        if (std::strncmp(arg, "--server=", 9) == 0) {
            dom_game_server_mode mode = out_cfg->server_mode;
            if (!parse_server_mode(arg + 9, mode)) {
                set_error(out_result, "Unknown --server value; expected off|listen|dedicated.");
                return -1;
            }
            out_cfg->server_mode = mode;
            continue;
        }
        if (std::strncmp(arg, "--connect=", 10) == 0) {
            if (!copy_cstr_bounded(out_cfg->connect_addr, sizeof(out_cfg->connect_addr), arg + 10)) {
                set_error(out_result, "Connect address too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--port=", 7) == 0) {
            u32 port = 0u;
            if (!parse_u32_range(arg + 7, 1u, 65535u, port)) {
                set_error(out_result, "Invalid --port value; expected 1..65535.");
                return -1;
            }
            out_cfg->net_port = port;
            continue;
        }
        if (std::strncmp(arg, "--headless-ticks=", 17) == 0) {
            u32 ticks = 0u;
            if (!parse_u32_range(arg + 17, 0u, 1000000u, ticks)) {
                set_error(out_result, "Invalid --headless-ticks value; expected 0..1000000.");
                return -1;
            }
            out_cfg->headless_ticks = ticks;
            continue;
        }
        if (std::strncmp(arg, "--headless-local=", 17) == 0) {
            u32 flag = 0u;
            if (!parse_u32_range(arg + 17, 0u, 1u, flag)) {
                set_error(out_result, "Invalid --headless-local value; expected 0|1.");
                return -1;
            }
            out_cfg->headless_local = flag;
            continue;
        }
        if (std::strncmp(arg, "--instance=", 11) == 0) {
            if (!copy_cstr_bounded(out_cfg->instance_id, sizeof(out_cfg->instance_id), arg + 11)) {
                set_error(out_result, "Instance id too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--handshake=", 12) == 0) {
            if (!copy_cstr_bounded(out_cfg->handshake_path, sizeof(out_cfg->handshake_path), arg + 12)) {
                set_error(out_result, "Handshake path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--keep_last_runs=", 17) == 0) {
            /* Launcher integration; ignored by game CLI. */
            continue;
        }
        if (std::strncmp(arg, "--home=", 7) == 0) {
            if (!copy_cstr_bounded(out_cfg->dominium_home, sizeof(out_cfg->dominium_home), arg + 7)) {
                set_error(out_result, "DOMINIUM_HOME path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--gfx=", 6) == 0) {
            if (!copy_cstr_bounded(out_cfg->gfx_backend, sizeof(out_cfg->gfx_backend), arg + 6)) {
                set_error(out_result, "Gfx backend name too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--renderer=", 11) == 0) {
            if (!out_result->warned_renderer_alias) {
                std::fprintf(stderr, "Warning: --renderer is deprecated; use --gfx.\n");
                out_result->warned_renderer_alias = 1;
            }
            if (out_cfg->gfx_backend[0] == '\0') {
                if (!copy_cstr_bounded(out_cfg->gfx_backend, sizeof(out_cfg->gfx_backend), arg + 11)) {
                    set_error(out_result, "Renderer backend name too long.");
                    return -1;
                }
            }
            force_profile_gfx_backend(out_cfg->profile, arg + 11);
            continue;
        }
        if (std::strncmp(arg, "--platform=", 11) == 0) {
            if (!copy_cstr_bounded(out_cfg->platform_backend, sizeof(out_cfg->platform_backend), arg + 11)) {
                set_error(out_result, "Platform backend name too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--tickrate=", 11) == 0) {
            u32 rate = 0u;
            if (!parse_u32_range(arg + 11, 0u, 1000000u, rate)) {
                set_error(out_result, "Invalid --tickrate value.");
                return -1;
            }
            out_cfg->tick_rate_hz = rate;
            continue;
        }
        if (std::strcmp(arg, "--demo") == 0) {
            out_cfg->demo_mode = 1u;
            continue;
        }
        if (std::strcmp(arg, "--devmode") == 0) {
            out_cfg->dev_mode = 1u;
            out_cfg->deterministic_test = 1u;
            continue;
        }
        if (std::strcmp(arg, "--deterministic-test") == 0) {
            out_cfg->deterministic_test = 1u;
            continue;
        }
        if (std::strncmp(arg, "--dev-allow-ad-hoc-paths=", 25) == 0) {
            u32 flag = 0u;
            if (!parse_u32_range(arg + 25, 0u, 1u, flag)) {
                set_error(out_result, "Invalid --dev-allow-ad-hoc-paths value; expected 0|1.");
                return -1;
            }
            out_cfg->dev_allow_ad_hoc_paths = flag;
            continue;
        }
        if (std::strncmp(arg, "--dev-allow-missing-content=", 28) == 0) {
            u32 flag = 0u;
            if (!parse_u32_range(arg + 28, 0u, 1u, flag)) {
                set_error(out_result, "Invalid --dev-allow-missing-content value; expected 0|1.");
                return -1;
            }
            out_cfg->dev_allow_missing_content = flag;
            continue;
        }
        if (std::strncmp(arg, "--ui.transparent-loading=", 25) == 0) {
            u32 flag = 0u;
            if (!parse_u32_range(arg + 25, 0u, 1u, flag)) {
                set_error(out_result, "Invalid --ui.transparent-loading value; expected 0|1.");
                return -1;
            }
            out_cfg->ui_transparent_loading = flag;
            continue;
        }
        if (std::strncmp(arg, "--record-replay=", 16) == 0) {
            if (!copy_cstr_bounded(out_cfg->replay_record_path, sizeof(out_cfg->replay_record_path), arg + 16)) {
                set_error(out_result, "Replay record path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--play-replay=", 14) == 0) {
            if (!copy_cstr_bounded(out_cfg->replay_play_path, sizeof(out_cfg->replay_play_path), arg + 14)) {
                set_error(out_result, "Replay playback path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--replay-strict-content=", 24) == 0) {
            u32 flag = 0u;
            if (!parse_u32_range(arg + 24, 0u, 1u, flag)) {
                set_error(out_result, "Invalid --replay-strict-content value; expected 0|1.");
                return -1;
            }
            out_cfg->replay_strict_content = flag;
            continue;
        }
        if (std::strncmp(arg, "--save=", 7) == 0) {
            if (!copy_cstr_bounded(out_cfg->save_path, sizeof(out_cfg->save_path), arg + 7)) {
                set_error(out_result, "Save path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--load=", 7) == 0) {
            if (!copy_cstr_bounded(out_cfg->load_path, sizeof(out_cfg->load_path), arg + 7)) {
                set_error(out_result, "Load path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--import-universe=", 18) == 0) {
            if (!copy_cstr_bounded(out_cfg->universe_import_path,
                                   sizeof(out_cfg->universe_import_path),
                                   arg + 18)) {
                set_error(out_result, "Import universe path too long.");
                return -1;
            }
            continue;
        }
        if (std::strncmp(arg, "--export-universe=", 18) == 0) {
            if (!copy_cstr_bounded(out_cfg->universe_export_path,
                                   sizeof(out_cfg->universe_export_path),
                                   arg + 18)) {
                set_error(out_result, "Export universe path too long.");
                return -1;
            }
            continue;
        }

        {
            char key[DOM_GAME_BACKEND_MAX];
            const char *val = 0;
            if (parse_sys_override(arg, key, sizeof(key), &val)) {
                if (!val || !val[0]) {
                    set_error(out_result, "Invalid --sys.* override; backend name required.");
                    return -1;
                }
                if (str_ieq(key, "gfx")) {
                    if (!copy_cstr_bounded(out_cfg->gfx_backend, sizeof(out_cfg->gfx_backend), val)) {
                        set_error(out_result, "Gfx backend name too long.");
                        return -1;
                    }
                } else if (str_ieq(key, "dsys") || str_ieq(key, "platform")) {
                    if (!copy_cstr_bounded(out_cfg->platform_backend, sizeof(out_cfg->platform_backend), val)) {
                        set_error(out_result, "Platform backend name too long.");
                        return -1;
                    }
                }
                continue;
            }
        }

        if (std::strncmp(arg, "--launcher-", 11) == 0) {
            continue;
        }
        if (std::strncmp(arg, "--display=", 10) == 0 ||
            std::strncmp(arg, "--universe=", 11) == 0) {
            continue;
        }

        if (std::strcmp(arg, "--print-caps") == 0 ||
            std::strcmp(arg, "--print-selection") == 0 ||
            std::strncmp(arg, "--profile=", 10) == 0 ||
            std::strncmp(arg, "--lockstep-strict=", 18) == 0 ||
            std::strncmp(arg, "--sys.", 6) == 0) {
            continue;
        }

        {
            char buf[128];
            std::snprintf(buf, sizeof(buf), "Unknown argument '%s'.", arg);
            set_error(out_result, buf);
            return -1;
        }
    }

    if (out_cfg->replay_record_path[0] && out_cfg->replay_play_path[0]) {
        set_error(out_result, "Cannot use --record-replay and --play-replay together.");
        return -1;
    }
    if (out_cfg->universe_import_path[0] && out_cfg->universe_export_path[0]) {
        set_error(out_result, "Cannot use --import-universe and --export-universe together.");
        return -1;
    }

    if (out_cfg->server_mode == DOM_GAME_SERVER_DEDICATED) {
        out_cfg->mode = DOM_GAME_MODE_HEADLESS;
    }
    if (out_cfg->session_role_set &&
        out_cfg->session_role == DOM_GAME_SESSION_ROLE_DEDICATED_SERVER) {
        out_cfg->mode = DOM_GAME_MODE_HEADLESS;
    }

    return 0;
}

void dom_game_cli_print_help(FILE *out) {
    if (!out) {
        out = stdout;
    }
    std::fprintf(out, "Dominium game CLI\n");
    std::fprintf(out, "Usage: game_dominium [options]\n");
    std::fprintf(out, "  --mode=gui|tui|headless  --role=single|host|server|client  --auth=server|lockstep\n");
    std::fprintf(out, "  --server=off|listen|dedicated  --auto-host  --input-delay=<u32>\n");
    std::fprintf(out, "  --headless-ticks=<u32>  --headless-local=0|1  --ui.transparent-loading=0|1\n");
    std::fprintf(out, "  --connect=<addr[:port]>  --port=<u16>\n");
    std::fprintf(out, "  --home=<path>  --instance=<id>  --profile=compat|baseline|perf\n");
    std::fprintf(out, "  --handshake=<relpath>  --dev-allow-ad-hoc-paths=0|1  --dev-allow-missing-content=0|1\n");
    std::fprintf(out, "  --gfx=<backend>  --sys.<subsystem>=<backend>  --tickrate=<ups>\n");
    std::fprintf(out, "  --lockstep-strict=0|1  --deterministic-test\n");
    std::fprintf(out, "  --record-replay=<path>  --play-replay=<path>  --replay-strict-content=0|1\n");
    std::fprintf(out, "  --save=<path>  --load=<path>\n");
    std::fprintf(out, "  --import-universe=<relpath>  --export-universe=<relpath>\n");
    std::fprintf(out, "  --capabilities  --print-caps  --print-selection  --introspect-json\n");
    std::fprintf(out, "  --help  --version\n");
}

int dom_game_cli_print_caps(FILE *out) {
    dom::print_caps(out ? out : stdout);
    return 0;
}

int dom_game_cli_print_selection(const dom_profile *profile, FILE *out, FILE *err) {
    if (!profile) {
        return 2;
    }
    dom::print_caps(out ? out : stdout);
    return dom::print_selection(*profile, out, err);
}

int dom_game_cli_print_capabilities(FILE *out) {
    const char *ver = dominium_get_game_version_string();
    if (!out) {
        out = stdout;
    }
    std::fprintf(out, "{\n");
    std::fprintf(out, "  \"schema_version\": 1,\n");
    std::fprintf(out, "  \"product\": \"dominium.game\",\n");
    std::fprintf(out, "  \"version\": \"%s\",\n", ver ? ver : DOMINIUM_GAME_VERSION);
    std::fprintf(out, "  \"modes\": [\"gui\", \"tui\", \"headless\"],\n");
    std::fprintf(out, "  \"save_versions\": [1],\n");
    std::fprintf(out, "  \"replay_versions\": [1],\n");
    std::fprintf(out, "  \"content_pack_versions\": [1]\n");
    std::fprintf(out, "}\n");
    return 0;
}

int dom_game_cli_print_version(FILE *out) {
    const char *ver = dominium_get_game_version_string();
    if (!out) {
        out = stdout;
    }
    std::fprintf(out, "%s\n", ver ? ver : DOMINIUM_GAME_VERSION);
    return 0;
}

int dom_game_cli_print_introspect_json(FILE *out) {
    if (!out) {
        out = stdout;
    }
    dominium_print_product_info_json(dom_get_product_info_game(), out);
    return 0;
}

int dom_game_run_config(const dom_game_config *cfg) {
    dom::DomGameApp app;
    if (!cfg) {
        return 1;
    }
    if (!app.init_from_cli(*cfg)) {
        return 1;
    }
    app.run();
    app.shutdown();
    return app.exit_code();
}

int dom_game_cli_dispatch(int argc, char **argv) {
    dom_game_config cfg;
    dom_game_cli_result res;

    if (dom_game_cli_parse(argc, argv, &cfg, &res) != 0) {
        if (res.error[0]) {
            std::fprintf(stderr, "Error: %s\n", res.error);
        }
        return res.exit_code ? res.exit_code : 2;
    }

    if (res.want_help) {
        dom_game_cli_print_help(stdout);
        return 0;
    }
    if (res.want_version) {
        return dom_game_cli_print_version(stdout);
    }
    if (res.want_capabilities) {
        return dom_game_cli_print_capabilities(stdout);
    }
    if (res.want_introspect_json) {
        return dom_game_cli_print_introspect_json(stdout);
    }
    if (res.want_print_caps) {
        return dom_game_cli_print_caps(stdout);
    }
    if (res.want_print_selection) {
        const int rc = dom_game_cli_print_selection(&cfg.profile, stdout, stderr);
        return (rc == 0) ? 0 : 2;
    }
    if (res.want_smoke_gui) {
        return run_game_smoke_gui(cfg.profile);
    }

    return dom_game_run_config(&cfg);
}

} /* extern "C" */

int main(int argc, char **argv) {
    return dom_game_cli_dispatch(argc, argv);
}
