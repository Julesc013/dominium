/*
Minimal client entrypoint with MP0 local-connect demo.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/system/d_system.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_help(void)
{
    printf("usage: client [options]\n");
    printf("options:\n");
    printf("  --help                      Show this help\n");
    printf("  --version                   Show product version\n");
    printf("  --build-info                Show build info + control capabilities\n");
    printf("  --status                    Show active control layers\n");
    printf("  --smoke                     Run deterministic CLI smoke\n");
    printf("  --selftest                  Alias for --smoke\n");
    printf("  --renderer <name>           Select renderer (explicit; no fallback)\n");
    printf("  --windowed                  Start a windowed client shell\n");
    printf("  --borderless                Start a borderless window\n");
    printf("  --fullscreen                Start a fullscreen window\n");
    printf("  --width <px>                Window width (default 800)\n");
    printf("  --height <px>               Window height (default 600)\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("  --mp0-connect=local          Run MP0 local client demo\n");
}

static void print_version(const char* product_version)
{
    printf("client %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\n", product_name);
    printf("product_version=%s\n", product_version);
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("git_hash=%s\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", 1u);
    printf("api_dgfx=%u\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

static void print_control_caps(const dom_control_caps* caps)
{
    const dom_registry* reg = dom_control_caps_registry(caps);
    u32 i;
    u32 enabled = dom_control_caps_enabled_count(caps);
#if DOM_CONTROL_HOOKS
    printf("control_hooks=enabled\n");
#else
    printf("control_hooks=removed\n");
#endif
    printf("control_caps_enabled=%u\n", (unsigned int)enabled);
    if (!reg) {
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(caps, entry->id)) {
            printf("control_cap=%s\n", entry->key);
        }
    }
}

static int enable_control_list(dom_control_caps* caps, const char* list)
{
    char buf[512];
    size_t len;
    char* token;
    if (!list || !caps) {
        return 0;
    }
    len = strlen(list);
    if (len >= sizeof(buf)) {
        return -1;
    }
    memcpy(buf, list, len + 1u);
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        if (*token) {
            if (dom_control_caps_enable_key(caps, token) != DOM_CONTROL_OK) {
                return -1;
            }
        }
        token = comma ? (comma + 1u) : (char*)0;
    }
    return 0;
}

typedef struct client_window_config {
    int enabled;
    int width;
    int height;
    dsys_window_mode mode;
} client_window_config;

static void client_window_defaults(client_window_config* cfg)
{
    if (!cfg) {
        return;
    }
    cfg->enabled = 0;
    cfg->width = 800;
    cfg->height = 600;
    cfg->mode = DWIN_MODE_WINDOWED;
}

static int client_parse_positive_int(const char* text, int* out_value)
{
    char* end = 0;
    long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtol(text, &end, 10);
    if (!end || *end != '\0' || value <= 0 || value > 8192) {
        return 0;
    }
    *out_value = (int)value;
    return 1;
}

static int client_run_windowed(const client_window_config* cfg, const char* renderer)
{
    dsys_window_desc desc;
    dsys_window* win = 0;
    int renderer_ready = 0;
    int result = 2;
    int32_t fb_w = 0;
    int32_t fb_h = 0;
    dsys_event ev;
    float dpi_scale = 1.0f;

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "client: dsys_init failed (%s)\n", dsys_last_error_text());
        return 2;
    }

    memset(&desc, 0, sizeof(desc));
    desc.x = 0;
    desc.y = 0;
    desc.width = cfg ? cfg->width : 800;
    desc.height = cfg ? cfg->height : 600;
    desc.mode = cfg ? cfg->mode : DWIN_MODE_WINDOWED;

    win = dsys_window_create(&desc);
    if (!win) {
        fprintf(stderr, "client: window creation failed (%s)\n", dsys_last_error_text());
        goto cleanup;
    }
    dsys_window_show(win);

    d_system_set_native_window_handle(dsys_window_get_native_handle(win));

    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "client: renderer init failed\n");
        goto cleanup;
    }
    renderer_ready = 1;

    dsys_window_get_framebuffer_size(win, &fb_w, &fb_h);
    if (fb_w <= 0 || fb_h <= 0) {
        dsys_window_get_size(win, &fb_w, &fb_h);
    }
    d_gfx_bind_surface(dsys_window_get_native_handle(win), fb_w, fb_h);

    dpi_scale = dsys_window_get_dpi_scale(win);
    fprintf(stderr, "client: dpi_scale=%.2f\n", (double)dpi_scale);

    while (!dsys_window_should_close(win)) {
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                goto cleanup;
            }
            if (ev.type == DSYS_EVENT_WINDOW_RESIZED) {
                dsys_window_get_framebuffer_size(win, &fb_w, &fb_h);
                if (fb_w <= 0 || fb_h <= 0) {
                    fb_w = ev.payload.window.width;
                    fb_h = ev.payload.window.height;
                }
                if (fb_w > 0 && fb_h > 0) {
                    d_gfx_resize(fb_w, fb_h);
                }
            }
            if (ev.type == DSYS_EVENT_DPI_CHANGED) {
                fprintf(stderr, "client: dpi_scale=%.2f\n", (double)ev.payload.dpi.scale);
            }
        }

        {
            d_gfx_cmd_buffer* buf = d_gfx_cmd_buffer_begin();
            if (buf) {
                d_gfx_viewport vp;
                d_gfx_draw_text_cmd text;
                d_gfx_color clear = { 0xff, 0x12, 0x12, 0x18 };
                d_gfx_color ink = { 0xff, 0xee, 0xee, 0xee };
                d_gfx_cmd_clear(buf, clear);
                vp.x = 0;
                vp.y = 0;
                vp.w = (fb_w > 0) ? fb_w : 800;
                vp.h = (fb_h > 0) ? fb_h : 600;
                d_gfx_cmd_set_viewport(buf, &vp);
                text.x = 16;
                text.y = 16;
                text.text = "Dominium client (windowed)";
                text.color = ink;
                d_gfx_cmd_draw_text(buf, &text);
                d_gfx_cmd_buffer_end(buf);
                d_gfx_submit(buf);
            }
        }
        d_gfx_present();
        dsys_sleep_ms(16);
    }
    result = 0;

cleanup:
    if (renderer_ready) {
        d_gfx_shutdown();
    }
    d_system_set_native_window_handle(0);
    if (win) {
        dsys_window_destroy(win);
    }
    dsys_shutdown();
    return result;
}

static int mp0_run_local_client(void)
{
    dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    survival_production_action_input gather;
    life_cmd_continuation_select cont;
    u64 hash_state;

    dom_mp0_command_queue_init(&queue, storage, DOM_MP0_MAX_COMMANDS);
    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    (void)dom_mp0_command_add_production(&queue, 0, &gather);
    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    (void)dom_mp0_command_add_continuation(&queue, 15, &cont);
    dom_mp0_command_sort(&queue);

    (void)dom_mp0_state_init(&state, 0);
    state.consumption.params.consumption_interval = 5;
    state.consumption.params.hunger_max = 2;
    state.consumption.params.thirst_max = 2;
    (void)dom_mp0_register_cohort(&state, 1u, 1u, 100u, 101u, 201u, 301u);
    (void)dom_mp0_register_cohort(&state, 2u, 1u, 100u, 102u, 202u, 302u);
    (void)dom_mp0_set_needs(&state, 1u, 0u, 0u, 1u);
    (void)dom_mp0_set_needs(&state, 2u, 5u, 5u, 1u);
    (void)dom_mp0_bind_controller(&state, 1u, 101u);
    (void)dom_mp0_run(&state, &queue, 30);
    hash_state = dom_mp0_hash_state(&state);
    printf("MP0 client local hash: %llu\n", (unsigned long long)hash_state);
    return 0;
}

static int client_validate_renderer(const char* renderer)
{
    if (!renderer || !renderer[0]) {
        return 1;
    }
    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "client: renderer '%s' unavailable\n", renderer);
        return 0;
    }
    d_gfx_shutdown();
    return 1;
}

int main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    const char* renderer = 0;
    client_window_config window_cfg;
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_mp0 = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    dom_control_caps control_caps;
    int control_loaded = 0;
    int i;
    client_window_defaults(&window_cfg);
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            want_help = 1;
            continue;
        }
        if (strcmp(argv[i], "--version") == 0) {
            want_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--build-info") == 0) {
            want_build_info = 1;
            continue;
        }
        if (strcmp(argv[i], "--status") == 0) {
            want_status = 1;
            continue;
        }
        if (strcmp(argv[i], "--smoke") == 0) {
            want_smoke = 1;
            continue;
        }
        if (strcmp(argv[i], "--selftest") == 0) {
            want_selftest = 1;
            continue;
        }
        if (strcmp(argv[i], "--windowed") == 0) {
            window_cfg.enabled = 1;
            window_cfg.mode = DWIN_MODE_WINDOWED;
            continue;
        }
        if (strcmp(argv[i], "--borderless") == 0) {
            window_cfg.enabled = 1;
            window_cfg.mode = DWIN_MODE_BORDERLESS;
            continue;
        }
        if (strcmp(argv[i], "--fullscreen") == 0) {
            window_cfg.enabled = 1;
            window_cfg.mode = DWIN_MODE_FULLSCREEN;
            continue;
        }
        if (strncmp(argv[i], "--width=", 8) == 0) {
            if (!client_parse_positive_int(argv[i] + 8, &window_cfg.width)) {
                fprintf(stderr, "client: invalid --width value\n");
                return 2;
            }
            continue;
        }
        if (strcmp(argv[i], "--width") == 0 && i + 1 < argc) {
            if (!client_parse_positive_int(argv[i + 1], &window_cfg.width)) {
                fprintf(stderr, "client: invalid --width value\n");
                return 2;
            }
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--height=", 9) == 0) {
            if (!client_parse_positive_int(argv[i] + 9, &window_cfg.height)) {
                fprintf(stderr, "client: invalid --height value\n");
                return 2;
            }
            continue;
        }
        if (strcmp(argv[i], "--height") == 0 && i + 1 < argc) {
            if (!client_parse_positive_int(argv[i + 1], &window_cfg.height)) {
                fprintf(stderr, "client: invalid --height value\n");
                return 2;
            }
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--renderer=", 11) == 0) {
            renderer = argv[i] + 11;
            continue;
        }
        if (strcmp(argv[i], "--renderer") == 0 && i + 1 < argc) {
            renderer = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--mp0-connect=local") == 0) {
            want_mp0 = 1;
        }
    }
    if (want_help) {
        print_help();
        return 0;
    }
    if (want_version) {
        print_version(DOMINIUM_GAME_VERSION);
        return 0;
    }
    if (want_smoke || want_selftest) {
        want_mp0 = 1;
    }
    if (want_mp0) {
        window_cfg.enabled = 0;
    }
    if (want_build_info || want_status || control_enable) {
        if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "client: failed to load control registry: %s\n", control_registry_path);
            return 2;
        }
        control_loaded = 1;
        if (enable_control_list(&control_caps, control_enable) != 0) {
            fprintf(stderr, "client: invalid control capability list\n");
            dom_control_caps_free(&control_caps);
            return 2;
        }
    }
    if (want_build_info) {
        print_build_info("client", DOMINIUM_GAME_VERSION);
        if (control_loaded) {
            print_control_caps(&control_caps);
            dom_control_caps_free(&control_caps);
        }
        return 0;
    }
    if (want_status) {
        if (!control_loaded) {
            if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
                fprintf(stderr, "client: failed to load control registry: %s\n", control_registry_path);
                return 2;
            }
            control_loaded = 1;
        }
        print_control_caps(&control_caps);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return 0;
    }
    if (window_cfg.enabled) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return client_run_windowed(&window_cfg, renderer);
    }
    if (want_mp0) {
        if (!client_validate_renderer(renderer)) {
            if (control_loaded) {
                dom_control_caps_free(&control_caps);
            }
            return 2;
        }
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return mp0_run_local_client();
    }
    printf("Dominium client stub. Use --help.\\n");
    if (control_loaded) {
        dom_control_caps_free(&control_caps);
    }
    return 0;
}
