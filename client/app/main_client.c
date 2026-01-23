/*
Minimal client entrypoint with MP0 local-connect demo.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
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
#include "dominium/session/mp0_session.h"
#include "client_input_bindings.h"
#include "readonly_view_model.h"
#include "client_ui_compositor.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    printf("  --windowed                  Start a windowed client shell\n");
    printf("  --tui                       Start a terminal client shell\n");
    printf("  --borderless                Start a borderless window\n");
    printf("  --fullscreen                Start a fullscreen window\n");
    printf("  --width <px>                Window width (default 800)\n");
    printf("  --height <px>               Window height (default 600)\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\n");
    printf("  --interactive               Use variable timestep (wall-clock)\n");
    printf("  --frame-cap-ms <ms>         Frame cap for interactive loops (0 disables)\n");
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

static int client_run_windowed(const client_window_config* cfg, const char* renderer,
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

static int client_run_tui(d_app_timing_mode timing_mode,
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
    dom_control_caps control_caps;
    int control_loaded = 0;
    int timing_mode_set = 0;
    int i;
    client_window_defaults(&window_cfg);
    dom_app_ui_request_init(&ui_req);
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
             window_cfg.enabled || ui_mode == DOM_APP_UI_TUI)) {
            fprintf(stderr, "client: observability commands cannot combine with UI or smoke paths\n");
            return D_APP_EXIT_USAGE;
        }
    }
    if (want_mp0 && (window_cfg.enabled || ui_mode == DOM_APP_UI_TUI)) {
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
    if (ui_mode == DOM_APP_UI_TUI) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return client_run_tui(timing_mode, frame_cap_ms, renderer, &compat_expect);
    }
    if (window_cfg.enabled) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return client_run_windowed(&window_cfg, renderer, timing_mode, frame_cap_ms, &compat_expect);
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
