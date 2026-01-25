/*
Minimal client entrypoint with MP0 local-connect demo.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/render/backend_detect.h"
#include "domino/sys.h"
#include "domino/app/runtime.h"
#include "domino/system/dsys.h"
#include "domino/system/d_system.h"
#include "domino/tui/tui.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/readonly_adapter.h"
#include "dominium/app/readonly_format.h"
#include "dominium/app/ui_event_log.h"
#include "dominium/session/mp0_session.h"
#include "client_input_bindings.h"
#include "readonly_view_model.h"
#include "client_ui_compositor.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

static void client_print_platform_caps(void);

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
    printf("  --topology                  Report packages topology summary\n");
    printf("  --snapshot                  Report snapshot metadata (if supported)\n");
    printf("  --events                    Report event stream summary (if supported)\n");
    printf("  --format <text|json>         Output format for observability\n");
    printf("  --renderer <name>           Select renderer (explicit; no fallback)\n");
    printf("  --ui=none|tui|gui           Select UI shell (gui maps to windowed)\n");
    printf("  --ui-script <list>           Auto-run UI actions (comma-separated)\n");
    printf("  --ui-frames <n>              Max UI frames before exit (headless friendly)\n");
    printf("  --ui-log <path>              Write UI event log (deterministic)\n");
    printf("  --headless                   Run GUI without a native window (null renderer)\n");
    printf("  --windowed                  Start a windowed client shell\n");
    printf("  --tui                       Start a terminal client shell\n");
    printf("  --borderless                Start a borderless window\n");
    printf("  --fullscreen                Start a fullscreen window\n");
    printf("  --width <px>                Window width (default 800)\n");
    printf("  --height <px>               Window height (default 600)\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\n");
    printf("  --interactive               Use variable timestep (wall-clock)\n");
    printf("  --frame-cap-ms <ms>         Frame cap for interactive loops (0 disables)\n");
    printf("  --ui-scale <pct>            UI scale percent (e.g. 100, 125, 150)\n");
    printf("  --palette <name>            UI palette (default|high-contrast)\n");
    printf("  --log-verbosity <level>     Logging verbosity (info|warn|error)\n");
    printf("  --debug-ui                  Enable debug UI flags\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("  --mp0-connect=local          Run MP0 local client demo\n");
    printf("  --expect-engine-version <v>  Require engine version match\n");
    printf("  --expect-game-version <v>    Require game version match\n");
    printf("  --expect-build-id <id>       Require build id match\n");
    printf("  --expect-sim-schema <id>     Require sim schema id match\n");
    printf("  --expect-build-info-abi <v>  Require build-info ABI match\n");
    printf("  --expect-caps-abi <v>        Require caps ABI match\n");
    printf("  --expect-gfx-api <v>         Require gfx API match\n");
    printf("commands:\n");
    printf("  start           Start (procedural universe)\n");
    printf("  load-save       Load save (may be unavailable)\n");
    printf("  inspect-replay  Inspect replay (may be unavailable)\n");
    printf("  tools           Open tools shell (handoff)\n");
    printf("  settings        Show current UI settings\n");
    printf("  exit            Exit client shell\n");
    printf("  survey-here     Submit survey intent\n");
    printf("  extract-here    Submit extract intent\n");
    printf("  fabricate       Submit fabricate intent\n");
    printf("  build           Submit build intent\n");
    printf("  connect-network Submit connect-network intent\n");
}

static void print_version(const char* product_version)
{
    printf("client %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    dom_app_build_info info;
    dom_app_build_info_init(&info, product_name, product_version);
    dom_app_print_build_info(&info);
    client_print_platform_caps();
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

static void client_print_platform_caps(void)
{
    dom_app_platform_caps caps;
    (void)dom_app_query_platform_caps(&caps);
    dom_app_print_platform_caps(&caps, 1, 0);
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

static int client_parse_frame_cap_ms(const char* text, uint32_t* out_value)
{
    char* end = 0;
    long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtol(text, &end, 10);
    if (!end || *end != '\0' || value < 0 || value > 1000) {
        return 0;
    }
    *out_value = (uint32_t)value;
    return 1;
}

static int client_parse_u32(const char* text, uint32_t* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 10);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (uint32_t)value;
    return 1;
}

static int client_parse_u64(const char* text, uint64_t* out_value)
{
    unsigned long long value = 0u;
    int base = 10;
    const char* p;
    if (!text || !out_value) {
        return 0;
    }
    p = text;
    if (p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) {
        base = 16;
        p += 2;
    }
    if (*p == '\0') {
        return 0;
    }
    while (*p) {
        int digit;
        char c = *p++;
        if (c >= '0' && c <= '9') {
            digit = c - '0';
        } else if (base == 16 && c >= 'a' && c <= 'f') {
            digit = 10 + (c - 'a');
        } else if (base == 16 && c >= 'A' && c <= 'F') {
            digit = 10 + (c - 'A');
        } else {
            return 0;
        }
        value = value * (unsigned long long)base + (unsigned long long)digit;
    }
    *out_value = (uint64_t)value;
    return 1;
}

static int client_parse_ui_scale(const char* text, int* out_value)
{
    char* end = 0;
    long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtol(text, &end, 10);
    if (!end || *end != '\0' || value < 50 || value > 200) {
        return 0;
    }
    *out_value = (int)value;
    return 1;
}

static int client_parse_palette(const char* text, int* out_value)
{
    if (!text || !out_value) {
        return 0;
    }
    if (strcmp(text, "default") == 0) {
        *out_value = 0;
        return 1;
    }
    if (strcmp(text, "high-contrast") == 0 || strcmp(text, "high_contrast") == 0) {
        *out_value = 1;
        return 1;
    }
    return 0;
}

static int client_parse_log_level(const char* text, int* out_value)
{
    if (!text || !out_value) {
        return 0;
    }
    if (strcmp(text, "info") == 0) {
        *out_value = 0;
        return 1;
    }
    if (strcmp(text, "warn") == 0 || strcmp(text, "warning") == 0) {
        *out_value = 1;
        return 1;
    }
    if (strcmp(text, "error") == 0) {
        *out_value = 2;
        return 1;
    }
    return 0;
}

typedef struct client_ui_settings {
    char renderer[16];
    int ui_scale_percent;
    int palette;
    int log_level;
    int debug_ui;
} client_ui_settings;

static const char* client_palette_name(int palette)
{
    return palette ? "high-contrast" : "default";
}

static const char* client_log_level_name(int level)
{
    switch (level) {
    case 1: return "warn";
    case 2: return "error";
    default: break;
    }
    return "info";
}

static void client_ui_settings_init(client_ui_settings* settings)
{
    if (!settings) {
        return;
    }
    memset(settings, 0, sizeof(*settings));
    settings->renderer[0] = '\0';
    settings->ui_scale_percent = 100;
    settings->palette = 0;
    settings->log_level = 0;
    settings->debug_ui = 0;
}

static void client_ui_settings_format_lines(const client_ui_settings* settings,
                                            char* lines,
                                            size_t line_cap,
                                            size_t line_stride,
                                            int* out_count)
{
    int count = 0;
    char* line0;
    if (out_count) {
        *out_count = 0;
    }
    if (!settings || !lines || line_cap == 0u || line_stride == 0u) {
        return;
    }
    line0 = lines;
    snprintf(line0 + (line_stride * count++), line_stride,
             "renderer=%s", settings->renderer[0] ? settings->renderer : "auto");
    snprintf(line0 + (line_stride * count++), line_stride,
             "ui_scale=%d%%", settings->ui_scale_percent);
    snprintf(line0 + (line_stride * count++), line_stride,
             "palette=%s", client_palette_name(settings->palette));
    snprintf(line0 + (line_stride * count++), line_stride,
             "input_bindings=default");
    snprintf(line0 + (line_stride * count++), line_stride,
             "log_verbosity=%s", client_log_level_name(settings->log_level));
    snprintf(line0 + (line_stride * count++), line_stride,
             "debug_ui=%s", settings->debug_ui ? "enabled" : "disabled");
    if (out_count) {
        *out_count = count;
    }
}

typedef struct client_tui_state {
    d_tui_context* ctx;
    d_tui_widget* status;
    d_tui_widget* meta;
    d_tui_widget* core;
    d_tui_widget* list;
    dom_app_ro_tree_node nodes[128];
    char node_text[128][160];
    const char* node_items[128];
    uint32_t node_count;
    int topology_supported;
    int quit;
} client_tui_state;

static void client_tui_quit(d_tui_widget* self, void* user)
{
    client_tui_state* state = (client_tui_state*)user;
    (void)self;
    if (state) {
        state->quit = 1;
    }
    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
}

static void client_tui_update_status(client_tui_state* state, d_app_timing_mode mode, uint64_t app_time_us)
{
    char buf[128];
    const char* mode_text = (mode == D_APP_TIMING_INTERACTIVE) ? "interactive" : "deterministic";
    if (!state || !state->status) {
        return;
    }
    snprintf(buf, sizeof(buf), "mode=%s app_time_us=%llu",
             mode_text, (unsigned long long)app_time_us);
    d_tui_widget_set_text(state->status, buf);
}

static void client_tui_build_tree(client_tui_state* state,
                                  const dom_client_ro_view_model* view)
{
    uint32_t i;
    if (!state || !view) {
        return;
    }
    state->node_count = 0u;
    state->topology_supported = 0;
    if (!view->has_tree) {
        return;
    }
    state->node_count = view->tree_info.count;
    state->topology_supported = 1;
    for (i = 0u; i < state->node_count; ++i) {
        const dom_app_ro_tree_node* node = &view->nodes[i];
        state->nodes[i] = *node;
        int indent = (int)(node->depth * 2u);
        snprintf(state->node_text[i], sizeof(state->node_text[i]),
                 "%*s%s", indent, "", node->label);
        state->node_items[i] = state->node_text[i];
    }
}

static void client_tui_update_meta(client_tui_state* state)
{
    char buf[160];
    int sel;
    if (!state || !state->meta) {
        return;
    }
    if (!state->topology_supported) {
        d_tui_widget_set_text(state->meta, "topology: unsupported");
        return;
    }
    if (!state->list) {
        d_tui_widget_set_text(state->meta, "topology: no list");
        return;
    }
    sel = d_tui_list_get_selection(state->list);
    if (sel < 0 || (uint32_t)sel >= state->node_count) {
        d_tui_widget_set_text(state->meta, "topology: no selection");
        return;
    }
    snprintf(buf, sizeof(buf),
             "node=%s depth=%u children=%u snapshot=unsupported",
             state->nodes[sel].label,
             (unsigned int)state->nodes[sel].depth,
             (unsigned int)state->nodes[sel].child_count);
    d_tui_widget_set_text(state->meta, buf);
}

static int client_run_windowed_legacy(const client_window_config* cfg, const char* renderer,
                                      d_app_timing_mode timing_mode, uint32_t frame_cap_ms,
                                      const dom_app_compat_expect* compat_expect)
{
    dsys_window_desc desc;
    dsys_window* win = 0;
    int renderer_ready = 0;
    int dsys_ready = 0;
    int lifecycle_ready = 0;
    int result = D_APP_EXIT_FAILURE;
    int normal_exit = 0;
    int32_t fb_w = 0;
    int32_t fb_h = 0;
    dsys_event ev;
    const dsys_window_mode_api_v1* window_mode_api = 0;
    dsys_window_mode current_mode = DWIN_MODE_WINDOWED;
    float dpi_scale = 1.0f;
    dom_app_clock clock;
    uint64_t frame_start_us = 0u;
    dom_client_ui_compositor ui;
    dom_app_readonly_adapter ro;
    dom_client_ro_view_model view;
    int ro_open = 0;

    dom_client_ui_compositor_init(&ui);
    if (!client_open_readonly(&ro, compat_expect)) {
        return D_APP_EXIT_FAILURE;
    }
    ro_open = 1;
    dom_client_ro_view_model_init(&view);
    if (!dom_client_ro_view_model_load(&view, &ro)) {
        fprintf(stderr, "client: core info unavailable\n");
        dom_app_ro_close(&ro);
        return D_APP_EXIT_FAILURE;
    }
    if (view.has_core) {
        dom_client_ui_compositor_set_summary(&ui,
                                             view.core_info.package_count,
                                             view.core_info.instance_count,
                                             view.has_tree,
                                             dom_app_ro_snapshots_supported(),
                                             dom_app_ro_events_supported());
    }
    dom_app_ro_close(&ro);
    ro_open = 0;

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "client: dsys_init failed (%s)\n", dsys_last_error_text());
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    window_mode_api = (const dsys_window_mode_api_v1*)dsys_query_extension(DSYS_EXTENSION_WINDOW_MODE, 1u);
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

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
    current_mode = desc.mode;
    if (window_mode_api) {
        if (window_mode_api->set_mode(win, current_mode) != DSYS_OK) {
            fprintf(stderr, "client: window mode set failed (%s)\n", dsys_last_error_text());
            goto cleanup;
        }
        current_mode = window_mode_api->get_mode(win);
    } else if (current_mode != DWIN_MODE_WINDOWED) {
        fprintf(stderr, "client: window mode extension unavailable\n");
        goto cleanup;
    }

    d_system_set_native_window_handle(dsys_window_get_native_handle(win));

    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "client: renderer init failed\n");
        result = D_APP_EXIT_UNAVAILABLE;
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
        if (timing_mode == D_APP_TIMING_INTERACTIVE) {
            frame_start_us = dsys_time_now_us();
        }
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_WINDOW);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                dom_client_action action = dom_client_input_translate(&ev);
                if (action == DOM_CLIENT_ACTION_TOGGLE_BORDERLESS) {
                    dsys_window_mode target = (current_mode == DWIN_MODE_BORDERLESS)
                        ? DWIN_MODE_WINDOWED
                        : DWIN_MODE_BORDERLESS;
                    if (!window_mode_api) {
                        fprintf(stderr, "client: window mode extension unavailable\n");
                    } else if (window_mode_api->set_mode(win, target) != DSYS_OK) {
                        fprintf(stderr, "client: window mode change failed (%s)\n", dsys_last_error_text());
                    } else {
                        current_mode = window_mode_api->get_mode(win);
                        fprintf(stderr, "client: window mode=%d\n", (int)current_mode);
                    }
                } else if (action == DOM_CLIENT_ACTION_TOGGLE_OVERLAY) {
                    dom_client_ui_compositor_toggle_overlay(&ui);
                }
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
        if (dsys_lifecycle_shutdown_requested()) {
            normal_exit = 1;
            break;
        }
        dom_app_clock_advance(&clock);

        {
            d_gfx_cmd_buffer* buf = d_gfx_cmd_buffer_begin();
            if (buf) {
                dom_client_ui_compositor_draw(&ui, buf, fb_w, fb_h);
                d_gfx_cmd_buffer_end(buf);
                d_gfx_submit(buf);
            }
        }
        d_gfx_present();
        dom_app_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
    }
    normal_exit = 1;

cleanup:
    if (renderer_ready) {
        d_gfx_shutdown();
    }
    if (ro_open) {
        dom_app_ro_close(&ro);
    }
    d_system_set_native_window_handle(0);
    if (win) {
        dsys_window_destroy(win);
    }
    if (lifecycle_ready) {
        if (dsys_lifecycle_shutdown_requested()) {
            dsys_shutdown_reason reason = dsys_lifecycle_shutdown_reason();
            fprintf(stderr, "client: shutdown=%s\n",
                    dsys_lifecycle_shutdown_reason_text(reason));
            if (normal_exit) {
                result = dom_app_exit_code_for_shutdown(reason);
            }
        } else if (normal_exit) {
            result = D_APP_EXIT_OK;
        }
        dsys_lifecycle_shutdown();
    }
    if (dsys_ready) {
        dsys_shutdown();
    }
    return result;
}

static int client_run_tui_legacy(d_app_timing_mode timing_mode,
                                 uint32_t frame_cap_ms,
                                 const char* renderer,
                                 const dom_app_compat_expect* compat_expect)
{
    d_tui_context* tui = 0;
    d_tui_widget* root = 0;
    d_tui_widget* title = 0;
    d_tui_widget* status = 0;
    d_tui_widget* core = 0;
    d_tui_widget* list = 0;
    d_tui_widget* meta = 0;
    d_tui_widget* quit_btn = 0;
    client_tui_state state;
    dom_app_clock clock;
    dsys_event ev;
    int dsys_ready = 0;
    int terminal_ready = 0;
    int lifecycle_ready = 0;
    int result = D_APP_EXIT_FAILURE;
    int normal_exit = 0;
    uint64_t frame_start_us = 0u;
    dom_app_readonly_adapter ro;
    dom_client_ro_view_model view;

    if (!client_validate_renderer(renderer)) {
        return D_APP_EXIT_UNAVAILABLE;
    }

    if (!client_open_readonly(&ro, compat_expect)) {
        return D_APP_EXIT_FAILURE;
    }
    dom_client_ro_view_model_init(&view);
    if (!dom_client_ro_view_model_load(&view, &ro)) {
        dom_app_ro_close(&ro);
        fprintf(stderr, "client: core info unavailable\n");
        return D_APP_EXIT_FAILURE;
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "client: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ro_close(&ro);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    if (!dsys_terminal_init()) {
        fprintf(stderr, "client: terminal unavailable\n");
        dom_app_ro_close(&ro);
        goto cleanup;
    }
    terminal_ready = 1;
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

    memset(&state, 0, sizeof(state));
    tui = d_tui_create();
    if (!tui) {
        fprintf(stderr, "client: tui init failed\n");
        dom_app_ro_close(&ro);
        goto cleanup;
    }
    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    title = d_tui_label(tui, "Dominium client TUI");
    status = d_tui_label(tui, "mode=deterministic app_time_us=0");
    core = d_tui_label(tui, "core: packages=0 instances=0");
    client_tui_build_tree(&state, &view);
    if (state.topology_supported && state.node_count > 0u) {
        list = d_tui_list(tui, state.node_items, (int)state.node_count);
    } else {
        static const char* empty_items[] = { "topology: unsupported" };
        list = d_tui_list(tui, empty_items, 1);
    }
    meta = d_tui_label(tui, "topology: ready");
    quit_btn = d_tui_button(tui, "Quit", client_tui_quit, &state);
    if (!root || !title || !status || !core || !list || !meta || !quit_btn) {
        fprintf(stderr, "client: tui widgets failed\n");
        dom_app_ro_close(&ro);
        goto cleanup;
    }
    d_tui_widget_add(root, title);
    d_tui_widget_add(root, status);
    d_tui_widget_add(root, core);
    d_tui_widget_add(root, list);
    d_tui_widget_add(root, meta);
    d_tui_widget_add(root, quit_btn);
    d_tui_set_root(tui, root);
    state.ctx = tui;
    state.status = status;
    state.core = core;
    state.list = list;
    state.meta = meta;

    {
        char core_buf[128];
        snprintf(core_buf, sizeof(core_buf),
                 "core: packages=%u instances=%u",
                 (unsigned int)view.core_info.package_count,
                 (unsigned int)view.core_info.instance_count);
        d_tui_widget_set_text(core, core_buf);
    }
    client_tui_update_meta(&state);
    dom_app_ro_close(&ro);

    while (!dsys_lifecycle_shutdown_requested()) {
        if (timing_mode == D_APP_TIMING_INTERACTIVE) {
            frame_start_us = dsys_time_now_us();
        }
        dom_app_pump_terminal_input();
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_CONSOLE);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                if (ev.payload.key.key == 'q' || ev.payload.key.key == 'Q') {
                    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
                } else {
                    d_tui_handle_key(tui, ev.payload.key.key);
                }
            }
        }
        if (dsys_lifecycle_shutdown_requested()) {
            normal_exit = 1;
            break;
        }
        dom_app_clock_advance(&clock);
        client_tui_update_status(&state, timing_mode, clock.app_time_us);
        client_tui_update_meta(&state);
        d_tui_render(tui);
        dom_app_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
    }
    normal_exit = 1;

cleanup:
    if (tui) {
        d_tui_destroy(tui);
    }
    if (terminal_ready) {
        dsys_terminal_shutdown();
    }
    if (lifecycle_ready) {
        if (dsys_lifecycle_shutdown_requested()) {
            dsys_shutdown_reason reason = dsys_lifecycle_shutdown_reason();
            fprintf(stderr, "client: shutdown=%s\n",
                    dsys_lifecycle_shutdown_reason_text(reason));
            if (normal_exit) {
                result = dom_app_exit_code_for_shutdown(reason);
            }
        } else if (normal_exit) {
            result = D_APP_EXIT_OK;
        }
        dsys_lifecycle_shutdown();
    }
    if (dsys_ready) {
        dsys_shutdown();
    }
    return result;
}

#define CLIENT_UI_MENU_COUNT 6
#define CLIENT_UI_STATUS_MAX 180
#define CLIENT_UI_LABEL_MAX 128
#define CLIENT_UI_RENDERER_MAX 8
#define CLIENT_UI_TOPOLOGY_LINES 32
#define CLIENT_UI_EVENT_LINES 12

typedef enum client_ui_screen {
    CLIENT_UI_LOADING = 0,
    CLIENT_UI_MAIN_MENU,
    CLIENT_UI_SETTINGS,
    CLIENT_UI_PLAYABLE
} client_ui_screen;

typedef enum client_ui_action {
    CLIENT_ACTION_NONE = 0,
    CLIENT_ACTION_START,
    CLIENT_ACTION_LOAD_SAVE,
    CLIENT_ACTION_INSPECT_REPLAY,
    CLIENT_ACTION_TOOLS,
    CLIENT_ACTION_SETTINGS,
    CLIENT_ACTION_EXIT,
    CLIENT_ACTION_BACK,
    CLIENT_ACTION_RENDERER_NEXT,
    CLIENT_ACTION_SCALE_UP,
    CLIENT_ACTION_SCALE_DOWN,
    CLIENT_ACTION_PALETTE_TOGGLE,
    CLIENT_ACTION_LOG_NEXT,
    CLIENT_ACTION_DEBUG_TOGGLE,
    CLIENT_ACTION_INTENT_SURVEY,
    CLIENT_ACTION_INTENT_EXTRACT,
    CLIENT_ACTION_INTENT_FABRICATE,
    CLIENT_ACTION_INTENT_BUILD,
    CLIENT_ACTION_INTENT_CONNECT
} client_ui_action;

typedef struct client_renderer_entry {
    char name[16];
    int supported;
} client_renderer_entry;

typedef struct client_renderer_list {
    client_renderer_entry entries[CLIENT_UI_RENDERER_MAX];
    uint32_t count;
} client_renderer_list;

typedef struct client_ui_state {
    client_ui_screen screen;
    int exit_requested;
    int loading_ticks;
    int menu_index;
    char action_status[CLIENT_UI_STATUS_MAX];
    char pack_status[CLIENT_UI_STATUS_MAX];
    uint32_t package_count;
    uint32_t instance_count;
    char testx_status[32];
    char seed_status[32];
    client_ui_settings settings;
    client_renderer_list renderers;
    char topology_lines[CLIENT_UI_TOPOLOGY_LINES][CLIENT_UI_LABEL_MAX];
    int topology_count;
    int topology_supported;
    char topology_status[CLIENT_UI_STATUS_MAX];
    char event_lines[CLIENT_UI_EVENT_LINES][CLIENT_UI_LABEL_MAX];
    int event_head;
    int event_count;
    uint32_t tick;
} client_ui_state;

static const char* g_client_menu_items[CLIENT_UI_MENU_COUNT] = {
    "Start (procedural universe)",
    "Load Save",
    "Inspect Replay",
    "Tools",
    "Settings",
    "Exit"
};

static void client_ui_set_status(client_ui_state* state, const char* fmt, ...)
{
    va_list args;
    if (!state || !fmt) {
        return;
    }
    va_start(args, fmt);
    vsnprintf(state->action_status, sizeof(state->action_status), fmt, args);
    va_end(args);
}

static void client_renderer_list_init(client_renderer_list* list)
{
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    uint32_t count;
    uint32_t i;
    if (!list) {
        return;
    }
    memset(list, 0, sizeof(*list));
    count = d_gfx_detect_backends(infos, (uint32_t)(sizeof(infos) / sizeof(infos[0])));
    for (i = 0u; i < count && list->count < CLIENT_UI_RENDERER_MAX; ++i) {
        client_renderer_entry* entry = &list->entries[list->count];
        entry->supported = infos[i].supported ? 1 : 0;
        entry->name[0] = '\0';
        if (infos[i].name[0]) {
            strncpy(entry->name, infos[i].name, sizeof(entry->name) - 1u);
            entry->name[sizeof(entry->name) - 1u] = '\0';
        }
        if (entry->name[0]) {
            list->count += 1u;
        }
    }
}

static const char* client_renderer_default(const client_renderer_list* list)
{
    uint32_t i;
    if (!list || list->count == 0u) {
        return "soft";
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->entries[i].supported && strcmp(list->entries[i].name, "soft") == 0) {
            return list->entries[i].name;
        }
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->entries[i].supported && strcmp(list->entries[i].name, "null") == 0) {
            return list->entries[i].name;
        }
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->entries[i].supported) {
            return list->entries[i].name;
        }
    }
    return list->entries[0].name;
}

static void client_settings_set_renderer(client_ui_settings* settings, const char* name)
{
    size_t len;
    if (!settings) {
        return;
    }
    settings->renderer[0] = '\0';
    if (!name || !name[0]) {
        return;
    }
    len = strlen(name);
    if (len >= sizeof(settings->renderer)) {
        len = sizeof(settings->renderer) - 1u;
    }
    memcpy(settings->renderer, name, len);
    settings->renderer[len] = '\0';
}

static const char* client_env_or_default(const char* key, const char* fallback)
{
    const char* value = getenv(key);
    if (value && value[0]) {
        return value;
    }
    return fallback;
}

static void client_ui_collect_loading(client_ui_state* state,
                                      const dom_app_compat_expect* compat)
{
    dom_app_readonly_adapter ro;
    dom_app_compat_report report;
    dom_app_ro_core_info core;
    if (!state) {
        return;
    }
    state->package_count = 0u;
    state->instance_count = 0u;
    snprintf(state->pack_status, sizeof(state->pack_status), "pack_status=unknown");
    dom_app_ro_init(&ro);
    dom_app_compat_report_init(&report, "client");
    if (dom_app_ro_open(&ro, compat, &report)) {
        if (dom_app_ro_get_core_info(&ro, &core) == DOM_APP_RO_OK) {
            state->package_count = core.package_count;
            state->instance_count = core.instance_count;
            snprintf(state->pack_status, sizeof(state->pack_status),
                     "pack_status=ok packages=%u instances=%u",
                     (unsigned int)core.package_count,
                     (unsigned int)core.instance_count);
        } else {
            snprintf(state->pack_status, sizeof(state->pack_status), "pack_status=failed");
        }
        dom_app_ro_close(&ro);
    } else {
        snprintf(state->pack_status, sizeof(state->pack_status),
                 "pack_status=failed %s",
                 report.message[0] ? report.message : "compatibility failure");
    }
    strncpy(state->testx_status,
            client_env_or_default("DOM_TESTX_STATUS", "unknown"),
            sizeof(state->testx_status) - 1u);
    state->testx_status[sizeof(state->testx_status) - 1u] = '\0';
    {
        const char* seed = getenv("DOM_DETERMINISTIC_SEED");
        if (!seed || !seed[0]) {
            seed = getenv("DOM_SEED");
        }
        if (!seed || !seed[0]) {
            seed = "unset";
        }
        strncpy(state->seed_status, seed, sizeof(state->seed_status) - 1u);
        state->seed_status[sizeof(state->seed_status) - 1u] = '\0';
    }
}

static void client_ui_state_init(client_ui_state* state,
                                 const client_ui_settings* settings,
                                 const dom_app_compat_expect* compat)
{
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    state->screen = CLIENT_UI_LOADING;
    state->menu_index = 0;
    state->exit_requested = 0;
    state->loading_ticks = 0;
    state->action_status[0] = '\0';
    state->topology_status[0] = '\0';
    client_renderer_list_init(&state->renderers);
    if (settings) {
        state->settings = *settings;
    } else {
        client_ui_settings_init(&state->settings);
    }
    if (state->settings.renderer[0] == '\0') {
        client_settings_set_renderer(&state->settings,
                                     client_renderer_default(&state->renderers));
    }
    state->topology_count = 0;
    state->topology_supported = 0;
    state->event_head = 0;
    state->event_count = 0;
    state->tick = 0u;
    client_ui_collect_loading(state, compat);
}

static void client_ui_cycle_renderer(client_ui_state* state)
{
    uint32_t i;
    uint32_t count;
    if (!state || state->renderers.count == 0u) {
        return;
    }
    count = state->renderers.count;
    for (i = 0u; i < count; ++i) {
        if (strcmp(state->renderers.entries[i].name, state->settings.renderer) == 0) {
            uint32_t next = (i + 1u) % count;
            client_settings_set_renderer(&state->settings,
                                         state->renderers.entries[next].name);
            return;
        }
    }
    client_settings_set_renderer(&state->settings, state->renderers.entries[0].name);
}

static void client_ui_add_event_line(client_ui_state* state, const char* text)
{
    int idx;
    if (!state || !text) {
        return;
    }
    if (state->event_count < CLIENT_UI_EVENT_LINES) {
        idx = (state->event_head + state->event_count) % CLIENT_UI_EVENT_LINES;
        state->event_count += 1;
    } else {
        idx = state->event_head;
        state->event_head = (state->event_head + 1) % CLIENT_UI_EVENT_LINES;
    }
    strncpy(state->event_lines[idx], text, CLIENT_UI_LABEL_MAX - 1u);
    state->event_lines[idx][CLIENT_UI_LABEL_MAX - 1u] = '\0';
}

static void client_ui_log_event(client_ui_state* state,
                                const char* event_name,
                                const char* detail)
{
    char line[CLIENT_UI_LABEL_MAX];
    size_t len = 0u;
    if (!state || !event_name || !event_name[0]) {
        return;
    }
    snprintf(line, sizeof(line), "tick=%u event=%s",
             (unsigned int)state->tick,
             event_name);
    len = strlen(line);
    if (detail && detail[0] && len + 1u < sizeof(line)) {
        snprintf(line + len, sizeof(line) - len, " %s", detail);
    }
    client_ui_add_event_line(state, line);
}

static void client_ui_add_topology_line(client_ui_state* state, const char* text)
{
    if (!state || !text) {
        return;
    }
    if (state->topology_count >= CLIENT_UI_TOPOLOGY_LINES) {
        return;
    }
    strncpy(state->topology_lines[state->topology_count],
            text,
            CLIENT_UI_LABEL_MAX - 1u);
    state->topology_lines[state->topology_count][CLIENT_UI_LABEL_MAX - 1u] = '\0';
    state->topology_count += 1;
}

static void client_ui_build_topology(client_ui_state* state,
                                     const dom_client_ro_view_model* view)
{
    char line[CLIENT_UI_LABEL_MAX];
    uint32_t i;
    if (!state || !view) {
        return;
    }
    state->topology_count = 0;
    state->topology_supported = 0;
    if (!view->has_tree) {
        client_ui_add_topology_line(state, "topology=unsupported");
        return;
    }
    state->topology_supported = 1;
    snprintf(line, sizeof(line), "topology=packages_tree nodes=%u truncated=%u",
             (unsigned int)view->tree_info.count,
             (unsigned int)view->tree_info.truncated);
    client_ui_add_topology_line(state, line);
    for (i = 0u; i < view->tree_info.count && state->topology_count < CLIENT_UI_TOPOLOGY_LINES; ++i) {
        int indent = (int)(view->nodes[i].depth * 2u);
        snprintf(line, sizeof(line), "%*s%s", indent, "", view->nodes[i].label);
        client_ui_add_topology_line(state, line);
    }
    if (view->tree_info.truncated && state->topology_count < CLIENT_UI_TOPOLOGY_LINES) {
        client_ui_add_topology_line(state, "topology_truncated=1");
    }
}

static void client_ui_refresh_playable(client_ui_state* state,
                                       const dom_app_compat_expect* compat)
{
    dom_app_readonly_adapter ro;
    dom_app_compat_report report;
    dom_client_ro_view_model view;
    if (!state) {
        return;
    }
    state->topology_status[0] = '\0';
    state->topology_count = 0;
    state->topology_supported = 0;
    dom_app_ro_init(&ro);
    dom_app_compat_report_init(&report, "client");
    if (dom_app_ro_open(&ro, compat, &report)) {
        dom_client_ro_view_model_init(&view);
        if (dom_client_ro_view_model_load(&view, &ro)) {
            client_ui_build_topology(state, &view);
            snprintf(state->topology_status, sizeof(state->topology_status), "topology=ok");
        } else {
            client_ui_add_topology_line(state, "topology=unavailable");
            snprintf(state->topology_status, sizeof(state->topology_status), "topology=unavailable");
        }
        dom_app_ro_close(&ro);
    } else {
        client_ui_add_topology_line(state, "topology=unavailable");
        snprintf(state->topology_status, sizeof(state->topology_status),
                 "topology=unavailable %s",
                 report.message[0] ? report.message : "compatibility failure");
    }
}

static void client_ui_emit_event(dom_app_ui_event_log* log,
                                 client_ui_state* ui_state,
                                 const char* event_name,
                                 const char* detail)
{
    dom_app_ui_event_log_emit(log, event_name, detail);
    if (ui_state) {
        client_ui_log_event(ui_state, event_name, detail);
    }
}

static int client_ui_execute_command(const char* cmd,
                                     const client_ui_settings* settings,
                                     dom_app_ui_event_log* log,
                                     client_ui_state* ui_state,
                                     char* status,
                                     size_t status_cap,
                                     int emit_text)
{
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!cmd || !cmd[0]) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client: missing command");
        }
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "start") == 0) {
        client_ui_emit_event(log, ui_state, "client.start", "mode=procedural");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_start=ok");
        }
        if (emit_text) {
            printf("client_start=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "load-save") == 0 || strcmp(cmd, "load") == 0) {
        client_ui_emit_event(log, ui_state, "client.load_save", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_load_save=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "client: load-save unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "inspect-replay") == 0 || strcmp(cmd, "replay") == 0) {
        client_ui_emit_event(log, ui_state, "client.inspect_replay", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_inspect_replay=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "client: inspect-replay unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "tools") == 0) {
        client_ui_emit_event(log, ui_state, "client.tools", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_tools=ok");
        }
        if (emit_text) {
            printf("client_tools=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "settings") == 0) {
        char lines[CLIENT_UI_MENU_COUNT][CLIENT_UI_LABEL_MAX];
        int count = 0;
        int i;
        client_ui_settings_format_lines(settings, (char*)lines,
                                        CLIENT_UI_MENU_COUNT,
                                        CLIENT_UI_LABEL_MAX, &count);
        client_ui_emit_event(log, ui_state, "client.settings", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_settings=ok");
        }
        if (emit_text) {
            printf("client_settings=ok\n");
            for (i = 0; i < count; ++i) {
                printf("%s\n", lines[i]);
            }
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "exit") == 0 || strcmp(cmd, "quit") == 0) {
        client_ui_emit_event(log, ui_state, "client.exit", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_exit=ok");
        }
        if (emit_text) {
            printf("client_exit=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "survey-here") == 0 || strcmp(cmd, "survey") == 0 ||
        strcmp(cmd, "intent-survey") == 0 || strcmp(cmd, "intent-survey-here") == 0) {
        client_ui_emit_event(log, ui_state, "client.intent_survey_here", "target=here result=queued");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_intent_survey_here=queued");
        }
        if (emit_text) {
            printf("client_intent_survey_here=queued\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "extract-here") == 0 || strcmp(cmd, "extract") == 0 ||
        strcmp(cmd, "intent-extract") == 0 || strcmp(cmd, "intent-extract-here") == 0) {
        client_ui_emit_event(log, ui_state, "client.intent_extract_here", "target=here result=queued");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_intent_extract_here=queued");
        }
        if (emit_text) {
            printf("client_intent_extract_here=queued\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "fabricate") == 0 || strcmp(cmd, "intent-fabricate") == 0) {
        client_ui_emit_event(log, ui_state, "client.intent_fabricate", "result=queued");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_intent_fabricate=queued");
        }
        if (emit_text) {
            printf("client_intent_fabricate=queued\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "build") == 0 || strcmp(cmd, "intent-build") == 0) {
        client_ui_emit_event(log, ui_state, "client.intent_build", "result=queued");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_intent_build=queued");
        }
        if (emit_text) {
            printf("client_intent_build=queued\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "connect-network") == 0 || strcmp(cmd, "connect") == 0 ||
        strcmp(cmd, "intent-connect") == 0 || strcmp(cmd, "intent-connect-network") == 0) {
        client_ui_emit_event(log, ui_state, "client.intent_connect_network", "result=queued");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_intent_connect_network=queued");
        }
        if (emit_text) {
            printf("client_intent_connect_network=queued\n");
        }
        return D_APP_EXIT_OK;
    }
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "client: unknown command '%s'", cmd);
    }
    return D_APP_EXIT_USAGE;
}

static void client_ui_apply_action(client_ui_state* state,
                                   client_ui_action action,
                                   dom_app_ui_event_log* log,
                                   const dom_app_compat_expect* compat)
{
    if (!state) {
        return;
    }
    switch (action) {
    case CLIENT_ACTION_START:
        client_ui_execute_command("start", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        state->screen = CLIENT_UI_PLAYABLE;
        client_ui_refresh_playable(state, compat);
        break;
    case CLIENT_ACTION_LOAD_SAVE:
        client_ui_execute_command("load-save", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_INSPECT_REPLAY:
        client_ui_execute_command("inspect-replay", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_TOOLS:
        client_ui_execute_command("tools", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_SETTINGS:
        client_ui_execute_command("settings", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        state->screen = CLIENT_UI_SETTINGS;
        break;
    case CLIENT_ACTION_EXIT:
        client_ui_execute_command("exit", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        state->exit_requested = 1;
        break;
    case CLIENT_ACTION_BACK:
        state->screen = CLIENT_UI_MAIN_MENU;
        break;
    case CLIENT_ACTION_RENDERER_NEXT:
        client_ui_cycle_renderer(state);
        client_ui_set_status(state, "settings_renderer=%s", state->settings.renderer);
        break;
    case CLIENT_ACTION_SCALE_UP:
        if (state->settings.ui_scale_percent < 150) {
            state->settings.ui_scale_percent += 25;
        }
        client_ui_set_status(state, "settings_ui_scale=%d%%", state->settings.ui_scale_percent);
        break;
    case CLIENT_ACTION_SCALE_DOWN:
        if (state->settings.ui_scale_percent > 75) {
            state->settings.ui_scale_percent -= 25;
        }
        client_ui_set_status(state, "settings_ui_scale=%d%%", state->settings.ui_scale_percent);
        break;
    case CLIENT_ACTION_PALETTE_TOGGLE:
        state->settings.palette = state->settings.palette ? 0 : 1;
        client_ui_set_status(state, "settings_palette=%s", client_palette_name(state->settings.palette));
        break;
    case CLIENT_ACTION_LOG_NEXT:
        state->settings.log_level = (state->settings.log_level + 1) % 3;
        client_ui_set_status(state, "settings_log=%s", client_log_level_name(state->settings.log_level));
        break;
    case CLIENT_ACTION_DEBUG_TOGGLE:
        state->settings.debug_ui = state->settings.debug_ui ? 0 : 1;
        client_ui_set_status(state, "settings_debug=%s", state->settings.debug_ui ? "enabled" : "disabled");
        break;
    case CLIENT_ACTION_INTENT_SURVEY:
        client_ui_execute_command("survey-here", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_INTENT_EXTRACT:
        client_ui_execute_command("extract-here", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_INTENT_FABRICATE:
        client_ui_execute_command("fabricate", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_INTENT_BUILD:
        client_ui_execute_command("build", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_INTENT_CONNECT:
        client_ui_execute_command("connect-network", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    default:
        break;
    }
}

static client_ui_action client_ui_action_from_token(const char* token)
{
    if (!token || !token[0]) {
        return CLIENT_ACTION_NONE;
    }
    if (strcmp(token, "start") == 0) return CLIENT_ACTION_START;
    if (strcmp(token, "load") == 0 || strcmp(token, "load-save") == 0) return CLIENT_ACTION_LOAD_SAVE;
    if (strcmp(token, "replay") == 0 || strcmp(token, "inspect-replay") == 0) return CLIENT_ACTION_INSPECT_REPLAY;
    if (strcmp(token, "tools") == 0) return CLIENT_ACTION_TOOLS;
    if (strcmp(token, "settings") == 0) return CLIENT_ACTION_SETTINGS;
    if (strcmp(token, "exit") == 0 || strcmp(token, "quit") == 0) return CLIENT_ACTION_EXIT;
    if (strcmp(token, "back") == 0) return CLIENT_ACTION_BACK;
    if (strcmp(token, "renderer-next") == 0) return CLIENT_ACTION_RENDERER_NEXT;
    if (strcmp(token, "scale-up") == 0) return CLIENT_ACTION_SCALE_UP;
    if (strcmp(token, "scale-down") == 0) return CLIENT_ACTION_SCALE_DOWN;
    if (strcmp(token, "palette") == 0) return CLIENT_ACTION_PALETTE_TOGGLE;
    if (strcmp(token, "log-next") == 0) return CLIENT_ACTION_LOG_NEXT;
    if (strcmp(token, "debug-toggle") == 0) return CLIENT_ACTION_DEBUG_TOGGLE;
    if (strcmp(token, "survey") == 0 || strcmp(token, "survey-here") == 0 ||
        strcmp(token, "intent-survey") == 0 || strcmp(token, "intent-survey-here") == 0) {
        return CLIENT_ACTION_INTENT_SURVEY;
    }
    if (strcmp(token, "extract") == 0 || strcmp(token, "extract-here") == 0 ||
        strcmp(token, "intent-extract") == 0 || strcmp(token, "intent-extract-here") == 0) {
        return CLIENT_ACTION_INTENT_EXTRACT;
    }
    if (strcmp(token, "fabricate") == 0 || strcmp(token, "intent-fabricate") == 0) {
        return CLIENT_ACTION_INTENT_FABRICATE;
    }
    if (strcmp(token, "build") == 0 || strcmp(token, "intent-build") == 0) {
        return CLIENT_ACTION_INTENT_BUILD;
    }
    if (strcmp(token, "connect") == 0 || strcmp(token, "connect-network") == 0 ||
        strcmp(token, "intent-connect") == 0 || strcmp(token, "intent-connect-network") == 0) {
        return CLIENT_ACTION_INTENT_CONNECT;
    }
    return CLIENT_ACTION_NONE;
}

static void client_gui_draw_text(d_gfx_cmd_buffer* buf, int x, int y,
                                 const char* text, d_gfx_color color)
{
    d_gfx_draw_text_cmd cmd;
    if (!buf || !text) {
        return;
    }
    cmd.x = x;
    cmd.y = y;
    cmd.text = text;
    cmd.color = color;
    d_gfx_cmd_draw_text(buf, &cmd);
}

static void client_gui_draw_menu(d_gfx_cmd_buffer* buf,
                                 const char* const* items,
                                 int count,
                                 int selected,
                                 int x,
                                 int y,
                                 int line_h,
                                 d_gfx_color text,
                                 d_gfx_color highlight)
{
    int i;
    d_gfx_draw_rect_cmd rect;
    if (!buf || !items) {
        return;
    }
    for (i = 0; i < count; ++i) {
        int line_y = y + i * line_h;
        if (i == selected) {
            rect.x = x - 8;
            rect.y = line_y - 2;
            rect.w = 380;
            rect.h = line_h;
            rect.color = highlight;
            d_gfx_cmd_draw_rect(buf, &rect);
        }
        client_gui_draw_text(buf, x, line_y, items[i], text);
    }
}

static void client_gui_render(const client_ui_state* state,
                              d_gfx_cmd_buffer* buf,
                              int fb_w,
                              int fb_h)
{
    d_gfx_viewport vp;
    d_gfx_color bg = { 0xff, 0x12, 0x12, 0x18 };
    d_gfx_color text = { 0xff, 0xee, 0xee, 0xee };
    d_gfx_color highlight = { 0xff, 0x2e, 0x2e, 0x3a };
    int width = (fb_w > 0) ? fb_w : 800;
    int height = (fb_h > 0) ? fb_h : 600;
    int y = 24;
    int line_h = 18;
    if (!buf) {
        return;
    }
    d_gfx_cmd_clear(buf, bg);
    vp.x = 0;
    vp.y = 0;
    vp.w = width;
    vp.h = height;
    d_gfx_cmd_set_viewport(buf, &vp);
    if (!state) {
        return;
    }
    client_gui_draw_text(buf, 20, y, "Dominium Client", text);
    y += line_h;
    if (state->screen == CLIENT_UI_LOADING) {
        char line[CLIENT_UI_STATUS_MAX];
        const dom_build_info_v1* build = dom_build_info_v1_get();
        snprintf(line, sizeof(line), "engine=%s", DOMINO_VERSION_STRING);
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "game=%s", DOMINIUM_GAME_VERSION);
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "build_number=%u", (unsigned int)DOM_BUILD_NUMBER);
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "sim_schema_id=%llu", (unsigned long long)dom_sim_schema_id());
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        if (build) {
            snprintf(line, sizeof(line), "sim_schema_version=%u", (unsigned int)build->sim_schema_version);
            client_gui_draw_text(buf, 20, y, line, text); y += line_h;
            snprintf(line, sizeof(line), "content_schema_version=%u", (unsigned int)build->content_schema_version);
            client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        } else {
            client_gui_draw_text(buf, 20, y, "sim_schema_version=unknown", text); y += line_h;
            client_gui_draw_text(buf, 20, y, "content_schema_version=unknown", text); y += line_h;
        }
        client_gui_draw_text(buf, 20, y, "protocol_law_targets=LAW_TARGETS@1.4.0", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "protocol_control_caps=CONTROL_CAPS@1.0.0", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0", text); y += line_h;
        snprintf(line, sizeof(line), "testx=%s", state->testx_status);
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        client_gui_draw_text(buf, 20, y, state->pack_status, text); y += line_h;
        snprintf(line, sizeof(line), "seed=%s", state->seed_status);
        client_gui_draw_text(buf, 20, y, line, text); y += line_h;
        client_gui_draw_text(buf, 20, y, "Loading complete. Press Enter to continue.", text);
        return;
    }
    if (state->screen == CLIENT_UI_MAIN_MENU) {
        y += line_h;
        client_gui_draw_menu(buf, g_client_menu_items, CLIENT_UI_MENU_COUNT,
                             state->menu_index, 20, y, line_h, text, highlight);
        y += (CLIENT_UI_MENU_COUNT + 1) * line_h;
        if (state->action_status[0]) {
            client_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == CLIENT_UI_SETTINGS) {
        char lines[CLIENT_UI_MENU_COUNT][CLIENT_UI_LABEL_MAX];
        int count = 0;
        int i;
        y += line_h;
        client_ui_settings_format_lines(&state->settings, (char*)lines,
                                        CLIENT_UI_MENU_COUNT,
                                        CLIENT_UI_LABEL_MAX, &count);
        for (i = 0; i < count; ++i) {
            client_gui_draw_text(buf, 20, y, lines[i], text);
            y += line_h;
        }
        y += line_h;
        client_gui_draw_text(buf, 20, y, "Keys: R renderer, +/- scale, P palette, L log, D debug, B back", text);
        y += line_h;
        if (state->action_status[0]) {
            client_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == CLIENT_UI_PLAYABLE) {
        int i;
        int idx;
        y += line_h;
        client_gui_draw_text(buf, 20, y, "Playable Slice 1", text);
        y += line_h * 2;

        client_gui_draw_text(buf, 20, y, "Topology", text);
        y += line_h;
        if (state->topology_count > 0) {
            for (i = 0; i < state->topology_count; ++i) {
                client_gui_draw_text(buf, 20, y, state->topology_lines[i], text);
                y += line_h;
            }
        } else if (state->topology_status[0]) {
            client_gui_draw_text(buf, 20, y, state->topology_status, text);
            y += line_h;
        } else {
            client_gui_draw_text(buf, 20, y, "topology=unknown", text);
            y += line_h;
        }
        y += line_h;

        client_gui_draw_text(buf, 20, y, "Patch Fields", text);
        y += line_h;
        client_gui_draw_text(buf, 20, y, "bearing=unknown", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "moisture=unknown", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "slope=unknown", text); y += line_h;
        y += line_h;

        client_gui_draw_text(buf, 20, y, "Agent", text);
        y += line_h;
        client_gui_draw_text(buf, 20, y, "goals=unavailable", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "plan=unavailable", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "beliefs=unavailable", text); y += line_h;
        y += line_h;

        client_gui_draw_text(buf, 20, y, "Event Log", text);
        y += line_h;
        if (state->event_count > 0) {
            idx = state->event_head;
            for (i = 0; i < state->event_count; ++i) {
                client_gui_draw_text(buf, 20, y, state->event_lines[idx], text);
                y += line_h;
                idx = (idx + 1) % CLIENT_UI_EVENT_LINES;
            }
        } else {
            client_gui_draw_text(buf, 20, y, "event_log=empty", text);
            y += line_h;
        }
        y += line_h;

        client_gui_draw_text(buf, 20, y, "Intents", text);
        y += line_h;
        client_gui_draw_text(buf, 20, y, "1) survey here", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "2) extract here", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "3) fabricate", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "4) build", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "5) connect network", text); y += line_h;
        client_gui_draw_text(buf, 20, y, "Keys: 1-5 intents, B back, Q exit", text); y += line_h;

        if (state->action_status[0]) {
            client_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
}

static int client_run_tui(const dom_app_ui_run_config* run_cfg,
                          const client_ui_settings* settings,
                          d_app_timing_mode timing_mode,
                          uint32_t frame_cap_ms,
                          const dom_app_compat_expect* compat_expect)
{
    d_tui_context* tui = 0;
    d_tui_widget* root = 0;
    client_ui_state ui;
    dom_app_clock clock;
    dsys_event ev;
    dom_app_ui_script script;
    dom_app_ui_event_log log;
    int script_ready = 0;
    int dsys_ready = 0;
    int terminal_ready = 0;
    int lifecycle_ready = 0;
    int result = D_APP_EXIT_FAILURE;
    int normal_exit = 0;
    uint64_t frame_start_us = 0u;
    int max_frames = run_cfg && run_cfg->max_frames_set ? (int)run_cfg->max_frames : 0;
    int frame_count = 0;

    client_ui_state_init(&ui, settings, compat_expect);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "client: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "client: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ui_event_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    if (!dsys_terminal_init()) {
        fprintf(stderr, "client: terminal unavailable\n");
        goto cleanup;
    }
    terminal_ready = 1;
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

    while (!dsys_lifecycle_shutdown_requested()) {
        if (timing_mode == D_APP_TIMING_INTERACTIVE) {
            frame_start_us = dsys_time_now_us();
        }
        ui.tick += 1u;
        if (script_ready) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                client_ui_apply_action(&ui, client_ui_action_from_token(token), &log, compat_expect);
            }
        }
        dom_app_pump_terminal_input();
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_CONSOLE);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                int key = ev.payload.key.key;
                if (key == 'q' || key == 'Q') {
                    client_ui_apply_action(&ui, CLIENT_ACTION_EXIT, &log, compat_expect);
                } else if (ui.screen == CLIENT_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = CLIENT_UI_MAIN_MENU;
                } else if (ui.screen == CLIENT_UI_MAIN_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.menu_index = (ui.menu_index > 0) ? (ui.menu_index - 1) : (CLIENT_UI_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.menu_index = (ui.menu_index + 1) % CLIENT_UI_MENU_COUNT;
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, (client_ui_action)(ui.menu_index + 1), &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_RENDERER_NEXT, &log, compat_expect);
                    } else if (key == '+' || key == '=') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SCALE_UP, &log, compat_expect);
                    } else if (key == '-' || key == '_') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SCALE_DOWN, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PALETTE_TOGGLE, &log, compat_expect);
                    } else if (key == 'l' || key == 'L') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_LOG_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_PLAYABLE) {
                    if (key == '1') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_SURVEY, &log, compat_expect);
                    } else if (key == '2') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_EXTRACT, &log, compat_expect);
                    } else if (key == '3') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_FABRICATE, &log, compat_expect);
                    } else if (key == '4') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_BUILD, &log, compat_expect);
                    } else if (key == '5') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_CONNECT, &log, compat_expect);
                    } else if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    }
                }
            }
        }
        if (ui.screen == CLIENT_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = CLIENT_UI_MAIN_MENU;
            }
        }
        if (ui.exit_requested) {
            normal_exit = 1;
            dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
        }
        dom_app_clock_advance(&clock);

        if (tui) {
            d_tui_destroy(tui);
        }
        tui = d_tui_create();
        if (!tui) {
            fprintf(stderr, "client: tui init failed\n");
            goto cleanup;
        }
        root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
        d_tui_widget_add(root, d_tui_label(tui, "Dominium Client TUI"));
        if (ui.screen == CLIENT_UI_LOADING) {
            char line[CLIENT_UI_STATUS_MAX];
            const dom_build_info_v1* build = dom_build_info_v1_get();
            d_tui_widget_add(root, d_tui_label(tui, "Loading..."));
            snprintf(line, sizeof(line), "engine=%s", DOMINO_VERSION_STRING);
            d_tui_widget_add(root, d_tui_label(tui, line));
            snprintf(line, sizeof(line), "game=%s", DOMINIUM_GAME_VERSION);
            d_tui_widget_add(root, d_tui_label(tui, line));
            snprintf(line, sizeof(line), "build_number=%u", (unsigned int)DOM_BUILD_NUMBER);
            d_tui_widget_add(root, d_tui_label(tui, line));
            snprintf(line, sizeof(line), "sim_schema_id=%llu", (unsigned long long)dom_sim_schema_id());
            d_tui_widget_add(root, d_tui_label(tui, line));
            if (build) {
                snprintf(line, sizeof(line), "sim_schema_version=%u", (unsigned int)build->sim_schema_version);
                d_tui_widget_add(root, d_tui_label(tui, line));
                snprintf(line, sizeof(line), "content_schema_version=%u", (unsigned int)build->content_schema_version);
                d_tui_widget_add(root, d_tui_label(tui, line));
            } else {
                d_tui_widget_add(root, d_tui_label(tui, "sim_schema_version=unknown"));
                d_tui_widget_add(root, d_tui_label(tui, "content_schema_version=unknown"));
            }
            d_tui_widget_add(root, d_tui_label(tui, "protocol_law_targets=LAW_TARGETS@1.4.0"));
            d_tui_widget_add(root, d_tui_label(tui, "protocol_control_caps=CONTROL_CAPS@1.0.0"));
            d_tui_widget_add(root, d_tui_label(tui, "protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0"));
            snprintf(line, sizeof(line), "testx=%s", ui.testx_status);
            d_tui_widget_add(root, d_tui_label(tui, line));
            d_tui_widget_add(root, d_tui_label(tui, ui.pack_status));
            snprintf(line, sizeof(line), "seed=%s", ui.seed_status);
            d_tui_widget_add(root, d_tui_label(tui, line));
            d_tui_widget_add(root, d_tui_label(tui, "Press Enter to continue"));
        } else if (ui.screen == CLIENT_UI_MAIN_MENU) {
            int i;
            char line[CLIENT_UI_LABEL_MAX];
            for (i = 0; i < CLIENT_UI_MENU_COUNT; ++i) {
                snprintf(line, sizeof(line), "%c %s",
                         (i == ui.menu_index) ? '>' : ' ',
                         g_client_menu_items[i]);
                d_tui_widget_add(root, d_tui_label(tui, line));
            }
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == CLIENT_UI_SETTINGS) {
            char lines[CLIENT_UI_MENU_COUNT][CLIENT_UI_LABEL_MAX];
            int count = 0;
            int i;
            client_ui_settings_format_lines(&ui.settings, (char*)lines,
                                            CLIENT_UI_MENU_COUNT,
                                            CLIENT_UI_LABEL_MAX, &count);
            for (i = 0; i < count; ++i) {
                d_tui_widget_add(root, d_tui_label(tui, lines[i]));
            }
            d_tui_widget_add(root, d_tui_label(tui, "R renderer, +/- scale, P palette, L log, D debug, B back"));
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == CLIENT_UI_PLAYABLE) {
            int i;
            int idx;
            d_tui_widget_add(root, d_tui_label(tui, "Playable Slice 1"));
            d_tui_widget_add(root, d_tui_label(tui, "Topology"));
            if (ui.topology_count > 0) {
                for (i = 0; i < ui.topology_count; ++i) {
                    d_tui_widget_add(root, d_tui_label(tui, ui.topology_lines[i]));
                }
            } else if (ui.topology_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.topology_status));
            } else {
                d_tui_widget_add(root, d_tui_label(tui, "topology=unknown"));
            }
            d_tui_widget_add(root, d_tui_label(tui, "Patch Fields"));
            d_tui_widget_add(root, d_tui_label(tui, "bearing=unknown"));
            d_tui_widget_add(root, d_tui_label(tui, "moisture=unknown"));
            d_tui_widget_add(root, d_tui_label(tui, "slope=unknown"));
            d_tui_widget_add(root, d_tui_label(tui, "Agent"));
            d_tui_widget_add(root, d_tui_label(tui, "goals=unavailable"));
            d_tui_widget_add(root, d_tui_label(tui, "plan=unavailable"));
            d_tui_widget_add(root, d_tui_label(tui, "beliefs=unavailable"));
            d_tui_widget_add(root, d_tui_label(tui, "Event Log"));
            if (ui.event_count > 0) {
                idx = ui.event_head;
                for (i = 0; i < ui.event_count; ++i) {
                    d_tui_widget_add(root, d_tui_label(tui, ui.event_lines[idx]));
                    idx = (idx + 1) % CLIENT_UI_EVENT_LINES;
                }
            } else {
                d_tui_widget_add(root, d_tui_label(tui, "event_log=empty"));
            }
            d_tui_widget_add(root, d_tui_label(tui, "Intents"));
            d_tui_widget_add(root, d_tui_label(tui, "1) survey here"));
            d_tui_widget_add(root, d_tui_label(tui, "2) extract here"));
            d_tui_widget_add(root, d_tui_label(tui, "3) fabricate"));
            d_tui_widget_add(root, d_tui_label(tui, "4) build"));
            d_tui_widget_add(root, d_tui_label(tui, "5) connect network"));
            d_tui_widget_add(root, d_tui_label(tui, "Keys: 1-5 intents, B back, Q exit"));
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        }
        d_tui_set_root(tui, root);
        d_tui_render(tui);

        dom_app_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
        frame_count += 1;
        if (max_frames > 0 && frame_count >= max_frames) {
            ui.exit_requested = 1;
        }
    }
    normal_exit = 1;

cleanup:
    if (tui) {
        d_tui_destroy(tui);
    }
    if (terminal_ready) {
        dsys_terminal_shutdown();
    }
    if (lifecycle_ready) {
        if (dsys_lifecycle_shutdown_requested()) {
            dsys_shutdown_reason reason = dsys_lifecycle_shutdown_reason();
            fprintf(stderr, "client: shutdown=%s\n",
                    dsys_lifecycle_shutdown_reason_text(reason));
            if (normal_exit) {
                result = dom_app_exit_code_for_shutdown(reason);
            }
        } else if (normal_exit) {
            result = D_APP_EXIT_OK;
        }
        dsys_lifecycle_shutdown();
    }
    if (dsys_ready) {
        dsys_shutdown();
    }
    dom_app_ui_event_log_close(&log);
    return result;
}

static int client_run_gui(const dom_app_ui_run_config* run_cfg,
                          const client_ui_settings* settings,
                          const client_window_config* window_cfg,
                          d_app_timing_mode timing_mode,
                          uint32_t frame_cap_ms,
                          const dom_app_compat_expect* compat_expect)
{
    dsys_window_desc desc;
    dsys_window* win = 0;
    int renderer_ready = 0;
    int dsys_ready = 0;
    int lifecycle_ready = 0;
    int result = D_APP_EXIT_FAILURE;
    int normal_exit = 0;
    int32_t fb_w = 0;
    int32_t fb_h = 0;
    dsys_event ev;
    const dsys_window_mode_api_v1* window_mode_api = 0;
    dsys_window_mode current_mode = DWIN_MODE_WINDOWED;
    dom_app_clock clock;
    uint64_t frame_start_us = 0u;
    client_ui_state ui;
    dom_app_ui_script script;
    dom_app_ui_event_log log;
    int script_ready = 0;
    const char* renderer = 0;
    int headless = run_cfg && run_cfg->headless_set ? run_cfg->headless : 0;
    int max_frames = run_cfg && run_cfg->max_frames_set ? (int)run_cfg->max_frames : 0;
    int frame_count = 0;

    client_ui_state_init(&ui, settings, compat_expect);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "client: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    renderer = ui.settings.renderer[0] ? ui.settings.renderer : client_renderer_default(&ui.renderers);
    if (headless && renderer && strcmp(renderer, "null") != 0) {
        fprintf(stderr, "client: headless forces null renderer (requested %s)\n", renderer);
        renderer = "null";
        client_settings_set_renderer(&ui.settings, renderer);
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "client: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ui_event_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    window_mode_api = (const dsys_window_mode_api_v1*)dsys_query_extension(DSYS_EXTENSION_WINDOW_MODE, 1u);
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

    if (!headless) {
        memset(&desc, 0, sizeof(desc));
        desc.x = 0;
        desc.y = 0;
        desc.width = window_cfg ? window_cfg->width : 800;
        desc.height = window_cfg ? window_cfg->height : 600;
        desc.mode = window_cfg ? window_cfg->mode : DWIN_MODE_WINDOWED;
        current_mode = desc.mode;
        win = dsys_window_create(&desc);
        if (!win) {
            fprintf(stderr, "client: window creation failed (%s)\n", dsys_last_error_text());
            goto cleanup;
        }
        dsys_window_show(win);
        if (window_mode_api) {
            if (window_mode_api->set_mode(win, current_mode) != DSYS_OK) {
                fprintf(stderr, "client: window mode set failed (%s)\n", dsys_last_error_text());
                goto cleanup;
            }
            current_mode = window_mode_api->get_mode(win);
        } else if (current_mode != DWIN_MODE_WINDOWED) {
            fprintf(stderr, "client: window mode extension unavailable\n");
            goto cleanup;
        }
        d_system_set_native_window_handle(dsys_window_get_native_handle(win));
    } else {
        d_system_set_native_window_handle(0);
    }

    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "client: renderer init failed\n");
        result = D_APP_EXIT_UNAVAILABLE;
        goto cleanup;
    }
    renderer_ready = 1;

    if (!headless && win) {
        dsys_window_get_framebuffer_size(win, &fb_w, &fb_h);
        if (fb_w <= 0 || fb_h <= 0) {
            dsys_window_get_size(win, &fb_w, &fb_h);
        }
        d_gfx_bind_surface(dsys_window_get_native_handle(win), fb_w, fb_h);
    } else {
        fb_w = window_cfg ? window_cfg->width : 800;
        fb_h = window_cfg ? window_cfg->height : 600;
        d_gfx_bind_surface(0, fb_w, fb_h);
    }

    while (!dsys_lifecycle_shutdown_requested()) {
        if (timing_mode == D_APP_TIMING_INTERACTIVE) {
            frame_start_us = dsys_time_now_us();
        }
        ui.tick += 1u;
        if (script_ready) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                client_ui_apply_action(&ui, client_ui_action_from_token(token), &log, compat_expect);
            }
        }
        while (!headless && dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_WINDOW);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                int key = ev.payload.key.key;
                if (key == 'q' || key == 'Q') {
                    client_ui_apply_action(&ui, CLIENT_ACTION_EXIT, &log, compat_expect);
                } else if (ui.screen == CLIENT_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = CLIENT_UI_MAIN_MENU;
                } else if (ui.screen == CLIENT_UI_MAIN_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.menu_index = (ui.menu_index > 0) ? (ui.menu_index - 1) : (CLIENT_UI_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.menu_index = (ui.menu_index + 1) % CLIENT_UI_MENU_COUNT;
                    } else if (key == '\r' || key == '\n' || key == ' ') {
                        client_ui_apply_action(&ui, (client_ui_action)(ui.menu_index + 1), &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_RENDERER_NEXT, &log, compat_expect);
                    } else if (key == '+' || key == '=') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SCALE_UP, &log, compat_expect);
                    } else if (key == '-' || key == '_') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SCALE_DOWN, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PALETTE_TOGGLE, &log, compat_expect);
                    } else if (key == 'l' || key == 'L') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_LOG_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_PLAYABLE) {
                    if (key == '1') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_SURVEY, &log, compat_expect);
                    } else if (key == '2') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_EXTRACT, &log, compat_expect);
                    } else if (key == '3') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_FABRICATE, &log, compat_expect);
                    } else if (key == '4') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_BUILD, &log, compat_expect);
                    } else if (key == '5') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INTENT_CONNECT, &log, compat_expect);
                    } else if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    }
                }
            }
            if (!headless && ev.type == DSYS_EVENT_WINDOW_RESIZED) {
                dsys_window_get_framebuffer_size(win, &fb_w, &fb_h);
                if (fb_w > 0 && fb_h > 0) {
                    d_gfx_resize(fb_w, fb_h);
                }
            }
        }
        if (ui.screen == CLIENT_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = CLIENT_UI_MAIN_MENU;
            }
        }
        if (ui.exit_requested) {
            normal_exit = 1;
            dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
        }
        dom_app_clock_advance(&clock);

        {
            d_gfx_cmd_buffer* buf = d_gfx_cmd_buffer_begin();
            if (buf) {
                client_gui_render(&ui, buf, fb_w, fb_h);
                d_gfx_cmd_buffer_end(buf);
                d_gfx_submit(buf);
            }
        }
        d_gfx_present();
        dom_app_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
        frame_count += 1;
        if (max_frames > 0 && frame_count >= max_frames) {
            ui.exit_requested = 1;
        }
    }
    normal_exit = 1;

cleanup:
    if (renderer_ready) {
        d_gfx_shutdown();
    }
    d_system_set_native_window_handle(0);
    if (win) {
        dsys_window_destroy(win);
    }
    if (lifecycle_ready) {
        if (dsys_lifecycle_shutdown_requested()) {
            dsys_shutdown_reason reason = dsys_lifecycle_shutdown_reason();
            fprintf(stderr, "client: shutdown=%s\n",
                    dsys_lifecycle_shutdown_reason_text(reason));
            if (normal_exit) {
                result = dom_app_exit_code_for_shutdown(reason);
            }
        } else if (normal_exit) {
            result = D_APP_EXIT_OK;
        }
        dsys_lifecycle_shutdown();
    }
    if (dsys_ready) {
        dsys_shutdown();
    }
    dom_app_ui_event_log_close(&log);
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

static int client_open_readonly(dom_app_readonly_adapter* ro,
                                const dom_app_compat_expect* expect)
{
    dom_app_compat_report report;
    dom_app_compat_report_init(&report, "client");
    dom_app_ro_init(ro);
    if (!dom_app_ro_open(ro, expect, &report)) {
        fprintf(stderr, "client: compatibility failure: %s\n",
                report.message[0] ? report.message : "unknown");
        dom_app_compat_print_report(&report, stderr);
        return 0;
    }
    return 1;
}

int client_main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    const char* renderer = 0;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    dom_app_ui_run_config ui_run;
    client_ui_settings ui_settings;
    dom_app_ui_event_log ui_log;
    int ui_log_open = 0;
    dom_app_output_format output_format = DOM_APP_FORMAT_TEXT;
    int output_format_set = 0;
    dom_app_compat_expect compat_expect;
    client_window_config window_cfg;
    d_app_timing_mode timing_mode = D_APP_TIMING_DETERMINISTIC;
    uint32_t frame_cap_ms = 16u;
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_topology = 0;
    int want_snapshot = 0;
    int want_events = 0;
    int want_mp0 = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    const char* cmd = 0;
    dom_control_caps control_caps;
    int control_loaded = 0;
    int timing_mode_set = 0;
    int i;
    client_window_defaults(&window_cfg);
    dom_app_ui_request_init(&ui_req);
    dom_app_ui_run_config_init(&ui_run);
    client_ui_settings_init(&ui_settings);
    dom_app_ui_event_log_init(&ui_log);
    dom_app_compat_expect_init(&compat_expect);
    for (i = 1; i < argc; ++i) {
        int ui_consumed = 0;
        char ui_err[96];
        int ui_res = dom_app_parse_ui_arg(&ui_req,
                                          argv[i],
                                          (i + 1 < argc) ? argv[i + 1] : 0,
                                          &ui_consumed,
                                          ui_err,
                                          sizeof(ui_err));
        if (ui_res < 0) {
            fprintf(stderr, "client: %s\n", ui_err);
            return D_APP_EXIT_USAGE;
        }
        if (ui_res > 0) {
            i += ui_consumed - 1;
            continue;
        }
        {
            int run_consumed = 0;
            int run_res = dom_app_parse_ui_run_arg(&ui_run,
                                                   argv[i],
                                                   (i + 1 < argc) ? argv[i + 1] : 0,
                                                   &run_consumed,
                                                   ui_err,
                                                   sizeof(ui_err));
            if (run_res < 0) {
                fprintf(stderr, "client: %s\n", ui_err);
                return D_APP_EXIT_USAGE;
            }
            if (run_res > 0) {
                i += run_consumed - 1;
                continue;
            }
        }
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
        if (strcmp(argv[i], "--topology") == 0) {
            want_topology = 1;
            continue;
        }
        if (strcmp(argv[i], "--snapshot") == 0) {
            want_snapshot = 1;
            continue;
        }
        if (strcmp(argv[i], "--events") == 0) {
            want_events = 1;
            continue;
        }
        if (strncmp(argv[i], "--format=", 9) == 0) {
            if (!dom_app_parse_output_format(argv[i] + 9, &output_format)) {
                fprintf(stderr, "client: invalid --format value\n");
                return D_APP_EXIT_USAGE;
            }
            output_format_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--format") == 0 && i + 1 < argc) {
            if (!dom_app_parse_output_format(argv[i + 1], &output_format)) {
                fprintf(stderr, "client: invalid --format value\n");
                return D_APP_EXIT_USAGE;
            }
            output_format_set = 1;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--deterministic") == 0) {
            want_deterministic = 1;
            continue;
        }
        if (strcmp(argv[i], "--interactive") == 0) {
            want_interactive = 1;
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
                return D_APP_EXIT_USAGE;
            }
            continue;
        }
        if (strcmp(argv[i], "--width") == 0 && i + 1 < argc) {
            if (!client_parse_positive_int(argv[i + 1], &window_cfg.width)) {
                fprintf(stderr, "client: invalid --width value\n");
                return D_APP_EXIT_USAGE;
            }
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--height=", 9) == 0) {
            if (!client_parse_positive_int(argv[i] + 9, &window_cfg.height)) {
                fprintf(stderr, "client: invalid --height value\n");
                return D_APP_EXIT_USAGE;
            }
            continue;
        }
        if (strcmp(argv[i], "--height") == 0 && i + 1 < argc) {
            if (!client_parse_positive_int(argv[i + 1], &window_cfg.height)) {
                fprintf(stderr, "client: invalid --height value\n");
                return D_APP_EXIT_USAGE;
            }
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--frame-cap-ms=", 15) == 0) {
            if (!client_parse_frame_cap_ms(argv[i] + 15, &frame_cap_ms)) {
                fprintf(stderr, "client: invalid --frame-cap-ms value\n");
                return D_APP_EXIT_USAGE;
            }
            continue;
        }
        if (strcmp(argv[i], "--frame-cap-ms") == 0 && i + 1 < argc) {
            if (!client_parse_frame_cap_ms(argv[i + 1], &frame_cap_ms)) {
                fprintf(stderr, "client: invalid --frame-cap-ms value\n");
                return D_APP_EXIT_USAGE;
            }
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--renderer=", 11) == 0) {
            strncpy(ui_settings.renderer, argv[i] + 11, sizeof(ui_settings.renderer) - 1u);
            ui_settings.renderer[sizeof(ui_settings.renderer) - 1u] = '\0';
            renderer = ui_settings.renderer;
            continue;
        }
        if (strcmp(argv[i], "--renderer") == 0 && i + 1 < argc) {
            strncpy(ui_settings.renderer, argv[i + 1], sizeof(ui_settings.renderer) - 1u);
            ui_settings.renderer[sizeof(ui_settings.renderer) - 1u] = '\0';
            renderer = ui_settings.renderer;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--ui-scale=", 11) == 0) {
            int value = 0;
            if (!client_parse_ui_scale(argv[i] + 11, &value)) {
                fprintf(stderr, "client: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            continue;
        }
        if (strcmp(argv[i], "--ui-scale") == 0 && i + 1 < argc) {
            int value = 0;
            if (!client_parse_ui_scale(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--palette=", 10) == 0) {
            int value = 0;
            if (!client_parse_palette(argv[i] + 10, &value)) {
                fprintf(stderr, "client: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            continue;
        }
        if (strcmp(argv[i], "--palette") == 0 && i + 1 < argc) {
            int value = 0;
            if (!client_parse_palette(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-verbosity=", 16) == 0) {
            int value = 0;
            if (!client_parse_log_level(argv[i] + 16, &value)) {
                fprintf(stderr, "client: invalid --log-verbosity value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.log_level = value;
            continue;
        }
        if (strcmp(argv[i], "--log-verbosity") == 0 && i + 1 < argc) {
            int value = 0;
            if (!client_parse_log_level(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --log-verbosity value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.log_level = value;
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--debug-ui") == 0) {
            ui_settings.debug_ui = 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-engine-version=", 24) == 0) {
            compat_expect.engine_version = argv[i] + 24;
            compat_expect.has_engine_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-engine-version") == 0 && i + 1 < argc) {
            compat_expect.engine_version = argv[i + 1];
            compat_expect.has_engine_version = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-game-version=", 22) == 0) {
            compat_expect.game_version = argv[i] + 22;
            compat_expect.has_game_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-game-version") == 0 && i + 1 < argc) {
            compat_expect.game_version = argv[i + 1];
            compat_expect.has_game_version = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-build-id=", 18) == 0) {
            compat_expect.build_id = argv[i] + 18;
            compat_expect.has_build_id = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-build-id") == 0 && i + 1 < argc) {
            compat_expect.build_id = argv[i + 1];
            compat_expect.has_build_id = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-sim-schema=", 21) == 0) {
            uint64_t value = 0;
            if (!client_parse_u64(argv[i] + 21, &value)) {
                fprintf(stderr, "client: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-sim-schema") == 0 && i + 1 < argc) {
            uint64_t value = 0;
            if (!client_parse_u64(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-build-info-abi=", 25) == 0) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i] + 25, &value)) {
                fprintf(stderr, "client: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-build-info-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-caps-abi=", 19) == 0) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i] + 19, &value)) {
                fprintf(stderr, "client: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-caps-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-gfx-api=", 17) == 0) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i] + 17, &value)) {
                fprintf(stderr, "client: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-gfx-api") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!client_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "client: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
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
            continue;
        }
        if (argv[i][0] != '-') {
            if (!cmd) {
                cmd = argv[i];
                continue;
            }
            fprintf(stderr, "client: unexpected argument '%s'\n", argv[i]);
            return D_APP_EXIT_USAGE;
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
    ui_mode = dom_app_select_ui_mode(&ui_req, DOM_APP_UI_NONE);
    if (window_cfg.enabled) {
        if (ui_req.mode_explicit && ui_mode != DOM_APP_UI_GUI) {
            fprintf(stderr, "client: windowed flags conflict with --ui=%s\n",
                    dom_app_ui_mode_name(ui_mode));
            return D_APP_EXIT_USAGE;
        }
        ui_mode = DOM_APP_UI_GUI;
    }
    if (ui_mode == DOM_APP_UI_GUI) {
        window_cfg.enabled = 1;
    } else if (ui_mode == DOM_APP_UI_TUI) {
        if (window_cfg.enabled) {
            fprintf(stderr, "client: --ui=tui conflicts with windowed flags\n");
            return D_APP_EXIT_USAGE;
        }
    } else if (ui_mode == DOM_APP_UI_NONE) {
        if (window_cfg.enabled && ui_req.mode_explicit) {
            fprintf(stderr, "client: --ui=none conflicts with ui flags\n");
            return D_APP_EXIT_USAGE;
        }
        window_cfg.enabled = 0;
    }
    if ((ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI) &&
        (want_build_info || want_status || want_smoke || want_selftest ||
         want_topology || want_snapshot || want_events || want_mp0 || cmd)) {
        fprintf(stderr, "client: --ui=%s cannot combine with CLI commands\n",
                dom_app_ui_mode_name(ui_mode));
        return D_APP_EXIT_USAGE;
    }
    if (cmd &&
        (want_build_info || want_status || want_smoke || want_selftest ||
         want_topology || want_snapshot || want_events || want_mp0)) {
        fprintf(stderr, "client: commands cannot combine with observability, status, or smoke paths\n");
        return D_APP_EXIT_USAGE;
    }
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "client: --deterministic and --interactive are mutually exclusive\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "client: --smoke requires deterministic mode\n");
        return D_APP_EXIT_USAGE;
    }
    if (want_smoke || want_selftest) {
        want_mp0 = 1;
    }
    {
        int observe_count = 0;
        int want_observe = 0;
        if (want_topology) {
            observe_count += 1;
        }
        if (want_snapshot) {
            observe_count += 1;
        }
        if (want_events) {
            observe_count += 1;
        }
        want_observe = (observe_count > 0);
        if (observe_count > 1) {
            fprintf(stderr, "client: choose only one of --topology, --snapshot, or --events\n");
            return D_APP_EXIT_USAGE;
        }
        if (output_format_set && !want_observe) {
            fprintf(stderr, "client: --format requires an observability command\n");
            return D_APP_EXIT_USAGE;
        }
        if (want_observe &&
            (want_build_info || want_status || want_smoke || want_selftest || want_mp0 ||
             window_cfg.enabled || ui_mode == DOM_APP_UI_TUI || cmd)) {
            fprintf(stderr, "client: observability commands cannot combine with UI or smoke paths\n");
            return D_APP_EXIT_USAGE;
        }
    }
    if (want_mp0 && (window_cfg.enabled || ui_mode == DOM_APP_UI_TUI || cmd)) {
        fprintf(stderr, "client: --smoke/mp0 cannot combine with windowed or tui modes\n");
        return D_APP_EXIT_USAGE;
    }
    if (want_deterministic) {
        timing_mode = D_APP_TIMING_DETERMINISTIC;
        timing_mode_set = 1;
    }
    if (want_interactive) {
        timing_mode = D_APP_TIMING_INTERACTIVE;
        timing_mode_set = 1;
    }
    if (!timing_mode_set) {
        timing_mode = (window_cfg.enabled || ui_mode == DOM_APP_UI_TUI)
                          ? D_APP_TIMING_INTERACTIVE
                          : D_APP_TIMING_DETERMINISTIC;
    }
    if (timing_mode == D_APP_TIMING_DETERMINISTIC) {
        frame_cap_ms = 0u;
    }
    if (want_build_info || want_status || control_enable) {
        if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "client: failed to load control registry: %s\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        control_loaded = 1;
        if (enable_control_list(&control_caps, control_enable) != 0) {
            fprintf(stderr, "client: invalid control capability list\n");
            dom_control_caps_free(&control_caps);
            return D_APP_EXIT_USAGE;
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
                return D_APP_EXIT_FAILURE;
            }
            control_loaded = 1;
        }
        print_control_caps(&control_caps);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return 0;
    }
    if (want_topology || want_snapshot || want_events) {
        dom_app_readonly_adapter ro;
        dom_client_ro_view_model view;
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        if (!client_open_readonly(&ro, &compat_expect)) {
            return D_APP_EXIT_FAILURE;
        }
        if (want_snapshot) {
            fprintf(stderr, "client: snapshot metadata unsupported\n");
            dom_app_ro_close(&ro);
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (want_events) {
            fprintf(stderr, "client: event stream unsupported\n");
            dom_app_ro_close(&ro);
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_client_ro_view_model_init(&view);
        if (!dom_client_ro_view_model_load(&view, &ro)) {
            fprintf(stderr, "client: core info unavailable\n");
            dom_app_ro_close(&ro);
            return D_APP_EXIT_FAILURE;
        }
        if (!view.has_tree) {
            fprintf(stderr, "client: topology unsupported\n");
            dom_app_ro_close(&ro);
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_app_ro_print_topology_bundle(output_format,
                                         &view.core_info,
                                         "packages_tree",
                                         view.nodes,
                                         view.tree_info.count,
                                         view.tree_info.truncated);
        dom_app_ro_close(&ro);
        return D_APP_EXIT_OK;
    }
    if (cmd) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
            control_loaded = 0;
        }
        if (ui_run.log_set && !ui_log_open) {
            if (!dom_app_ui_event_log_open(&ui_log, ui_run.log_path)) {
                fprintf(stderr, "client: failed to open ui log\n");
                return D_APP_EXIT_FAILURE;
            }
            ui_log_open = 1;
        }
        {
            char status[160];
            int res = client_ui_execute_command(cmd, &ui_settings, &ui_log, 0,
                                                status, sizeof(status), 1);
            if (ui_log_open) {
                dom_app_ui_event_log_close(&ui_log);
            }
            if (res != D_APP_EXIT_USAGE) {
                return res;
            }
        }
        printf("client: unknown command '%s'\\n", cmd);
        print_help();
        return D_APP_EXIT_USAGE;
    }
    if (ui_mode == DOM_APP_UI_TUI) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return client_run_tui(&ui_run, &ui_settings, timing_mode, frame_cap_ms, &compat_expect);
    }
    if (window_cfg.enabled) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return client_run_gui(&ui_run, &ui_settings, &window_cfg,
                              timing_mode, frame_cap_ms, &compat_expect);
    }
    if (want_mp0) {
        if (!client_validate_renderer(renderer)) {
            if (control_loaded) {
                dom_control_caps_free(&control_caps);
            }
            return D_APP_EXIT_UNAVAILABLE;
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

int main(int argc, char** argv)
{
    return client_main(argc, argv);
}
