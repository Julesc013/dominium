/*
Stub tools host entrypoint; replace with tool router once runtime is wired.
*/
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
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/readonly_adapter.h"
#include "dominium/app/readonly_format.h"
#include "dominium/app/ui_event_log.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

static void tools_print_help(void)
{
    printf("usage: tools [options] <command>\\n");
    printf("options:\\n");
    printf("  --help                      Show this help\\n");
    printf("  --version                   Show product version\\n");
    printf("  --build-info                Show build info\\n");
    printf("  --status                    Show tools status\\n");
    printf("  --smoke                     Run deterministic CLI smoke\\n");
    printf("  --selftest                  Alias for --smoke\\n");
    printf("  --ui=none|tui|gui           Select UI shell (optional)\\n");
    printf("  --tui                       Start tools terminal UI\\n");
    printf("  --ui-script <list>           Auto-run UI actions (comma-separated)\\n");
    printf("  --ui-frames <n>              Max UI frames before exit (headless friendly)\\n");
    printf("  --ui-log <path>              Write UI event log (deterministic)\\n");
    printf("  --headless                   Run GUI without a native window (null renderer)\\n");
    printf("  --format <text|json>         Output format for inspect/validate\\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\\n");
    printf("  --interactive               Use variable timestep (wall-clock)\\n");
    printf("  --frame-cap-ms <ms>         Frame cap for interactive loops (0 disables)\\n");
    printf("  --renderer <name>           Select renderer (explicit; no fallback)\\n");
    printf("  --ui-scale <pct>            UI scale percent (e.g. 100, 125, 150)\\n");
    printf("  --palette <name>            UI palette (default|high-contrast)\\n");
    printf("  --log-verbosity <level>     Logging verbosity (info|warn|error)\\n");
    printf("  --debug-ui                  Enable debug UI flags\\n");
    printf("  --expect-engine-version <v>  Require engine version match\\n");
    printf("  --expect-game-version <v>    Require game version match\\n");
    printf("  --expect-build-id <id>       Require build id match\\n");
    printf("  --expect-sim-schema <id>     Require sim schema id match\\n");
    printf("  --expect-build-info-abi <v>  Require build-info ABI match\\n");
    printf("  --expect-caps-abi <v>        Require caps ABI match\\n");
    printf("  --expect-gfx-api <v>         Require gfx API match\\n");
    printf("commands:\\n");
    printf("  inspect    Inspect read-only topology and metadata\\n");
    printf("  validate   Validate compatibility/portable metadata\\n");
    printf("  replay     Replay viewer (unsupported)\\n");
    printf("  start           Start (unavailable in tools)\\n");
    printf("  load-save       Load save (unavailable in tools)\\n");
    printf("  inspect-replay  Inspect replay (alias for replay)\\n");
    printf("  tools           Open tools menu (UI)\\n");
    printf("  settings        Show current UI settings\\n");
    printf("  world-inspector        World inspector (read-only)\\n");
    printf("  agent-inspector        Agent inspector (unavailable)\\n");
    printf("  institution-inspector  Institution inspector (unavailable)\\n");
    printf("  history-viewer         History/replay viewer (unsupported)\\n");
    printf("  pack-inspector         Pack/capability inspector (read-only)\\n");
    printf("  exit            Exit tools\\n");
}

static void tools_print_version(const char* product_version)
{
    printf("tools %s\\n", product_version);
}

static void tools_print_build_info(const char* product_name, const char* product_version)
{
    dom_app_build_info info;
    dom_app_build_info_init(&info, product_name, product_version);
    dom_app_print_build_info(&info);
}

static int tools_parse_frame_cap_ms(const char* text, uint32_t* out_value)
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

static int tools_parse_u32(const char* text, uint32_t* out_value)
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

static int tools_parse_u64(const char* text, uint64_t* out_value)
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

static int tools_parse_ui_scale(const char* text, int* out_value)
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

static int tools_parse_palette(const char* text, int* out_value)
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

static int tools_parse_log_level(const char* text, int* out_value)
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

typedef struct tools_ui_settings {
    char renderer[16];
    int ui_scale_percent;
    int palette;
    int log_level;
    int debug_ui;
} tools_ui_settings;

static const char* tools_palette_name(int palette)
{
    return palette ? "high-contrast" : "default";
}

static const char* tools_log_level_name(int level)
{
    switch (level) {
    case 1: return "warn";
    case 2: return "error";
    default: break;
    }
    return "info";
}

static void tools_ui_settings_init(tools_ui_settings* settings)
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

static void tools_ui_settings_format_lines(const tools_ui_settings* settings,
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
             "palette=%s", tools_palette_name(settings->palette));
    snprintf(line0 + (line_stride * count++), line_stride,
             "input_bindings=default");
    snprintf(line0 + (line_stride * count++), line_stride,
             "log_verbosity=%s", tools_log_level_name(settings->log_level));
    snprintf(line0 + (line_stride * count++), line_stride,
             "debug_ui=%s", settings->debug_ui ? "enabled" : "disabled");
    if (out_count) {
        *out_count = count;
    }
}

#define TOOLS_UI_MAIN_MENU_COUNT 6
#define TOOLS_UI_TOOLS_MENU_COUNT 6
#define TOOLS_UI_STATUS_MAX 160
#define TOOLS_UI_LABEL_MAX 96
#define TOOLS_UI_RENDERER_MAX 8
#define TOOLS_UI_TOOL_LINES 32

typedef enum tools_ui_screen {
    TOOLS_UI_LOADING = 0,
    TOOLS_UI_MAIN_MENU,
    TOOLS_UI_TOOLS_MENU,
    TOOLS_UI_SETTINGS,
    TOOLS_UI_TOOL_VIEW
} tools_ui_screen;

typedef enum tools_ui_tool {
    TOOLS_TOOL_NONE = 0,
    TOOLS_TOOL_WORLD,
    TOOLS_TOOL_AGENT,
    TOOLS_TOOL_INSTITUTION,
    TOOLS_TOOL_HISTORY,
    TOOLS_TOOL_PACK
} tools_ui_tool;

typedef enum tools_ui_action {
    TOOLS_ACTION_NONE = 0,
    TOOLS_ACTION_START,
    TOOLS_ACTION_LOAD_SAVE,
    TOOLS_ACTION_INSPECT_REPLAY,
    TOOLS_ACTION_TOOLS_MENU,
    TOOLS_ACTION_SETTINGS,
    TOOLS_ACTION_EXIT,
    TOOLS_ACTION_BACK,
    TOOLS_ACTION_WORLD_INSPECTOR,
    TOOLS_ACTION_AGENT_INSPECTOR,
    TOOLS_ACTION_INSTITUTION_INSPECTOR,
    TOOLS_ACTION_HISTORY_VIEWER,
    TOOLS_ACTION_PACK_INSPECTOR,
    TOOLS_ACTION_RENDERER_NEXT,
    TOOLS_ACTION_SCALE_UP,
    TOOLS_ACTION_SCALE_DOWN,
    TOOLS_ACTION_PALETTE_TOGGLE,
    TOOLS_ACTION_LOG_NEXT,
    TOOLS_ACTION_DEBUG_TOGGLE
} tools_ui_action;

typedef struct tools_renderer_entry {
    char name[16];
    int supported;
} tools_renderer_entry;

typedef struct tools_renderer_list {
    tools_renderer_entry entries[TOOLS_UI_RENDERER_MAX];
    uint32_t count;
} tools_renderer_list;

typedef struct tools_ui_state {
    tools_ui_screen screen;
    int exit_requested;
    int loading_ticks;
    int main_index;
    int tools_index;
    char action_status[TOOLS_UI_STATUS_MAX];
    char pack_status[TOOLS_UI_STATUS_MAX];
    uint32_t package_count;
    uint32_t instance_count;
    char testx_status[32];
    char seed_status[32];
    tools_ui_settings settings;
    tools_renderer_list renderers;
    tools_ui_tool tool;
    char tool_lines[TOOLS_UI_TOOL_LINES][TOOLS_UI_LABEL_MAX];
    int tool_line_count;
} tools_ui_state;

static const char* g_tools_main_menu_items[TOOLS_UI_MAIN_MENU_COUNT] = {
    "Start (procedural universe)",
    "Load Save",
    "Inspect Replay",
    "Tools",
    "Settings",
    "Exit"
};

static const char* g_tools_menu_items[TOOLS_UI_TOOLS_MENU_COUNT] = {
    "World Inspector",
    "Agent Inspector",
    "Institution Inspector",
    "History / Replay Viewer",
    "Pack / Capability Inspector",
    "Back"
};

typedef enum tools_tui_action {
    TOOLS_TUI_NONE = 0,
    TOOLS_TUI_INSPECT,
    TOOLS_TUI_VALIDATE,
    TOOLS_TUI_REPLAY,
    TOOLS_TUI_QUIT
} tools_tui_action;

typedef struct tools_tui_state {
    d_tui_context* ctx;
    d_tui_widget* status;
    tools_tui_action action;
} tools_tui_state;

static void tools_tui_action_inspect(d_tui_widget* self, void* user)
{
    tools_tui_state* state = (tools_tui_state*)user;
    (void)self;
    if (state) {
        state->action = TOOLS_TUI_INSPECT;
    }
    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
}

static void tools_tui_action_validate(d_tui_widget* self, void* user)
{
    tools_tui_state* state = (tools_tui_state*)user;
    (void)self;
    if (state) {
        state->action = TOOLS_TUI_VALIDATE;
    }
    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
}

static void tools_tui_action_replay(d_tui_widget* self, void* user)
{
    tools_tui_state* state = (tools_tui_state*)user;
    (void)self;
    if (state) {
        state->action = TOOLS_TUI_REPLAY;
    }
    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
}

static void tools_tui_action_quit(d_tui_widget* self, void* user)
{
    tools_tui_state* state = (tools_tui_state*)user;
    (void)self;
    if (state) {
        state->action = TOOLS_TUI_QUIT;
    }
    dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
}

static void tools_tui_update_status(tools_tui_state* state, d_app_timing_mode mode, uint64_t app_time_us)
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

static int tools_run_tui_legacy(d_app_timing_mode timing_mode,
                                uint32_t frame_cap_ms,
                                const dom_app_compat_expect* compat_expect)
{
    d_tui_context* tui = 0;
    d_tui_widget* root = 0;
    d_tui_widget* title = 0;
    d_tui_widget* status = 0;
    d_tui_widget* btn_inspect = 0;
    d_tui_widget* btn_validate = 0;
    d_tui_widget* btn_replay = 0;
    d_tui_widget* btn_quit = 0;
    tools_tui_state state;
    dom_app_clock clock;
    dsys_event ev;
    int dsys_ready = 0;
    int terminal_ready = 0;
    int lifecycle_ready = 0;
    int result = D_APP_EXIT_FAILURE;
    int normal_exit = 0;
    uint64_t frame_start_us = 0u;

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "tools: dsys_init failed (%s)\n", dsys_last_error_text());
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    if (!dsys_terminal_init()) {
        fprintf(stderr, "tools: terminal unavailable\n");
        goto cleanup;
    }
    terminal_ready = 1;
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

    memset(&state, 0, sizeof(state));
    tui = d_tui_create();
    if (!tui) {
        fprintf(stderr, "tools: tui init failed\n");
        goto cleanup;
    }
    root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
    title = d_tui_label(tui, "Dominium tools TUI");
    status = d_tui_label(tui, "mode=deterministic app_time_us=0");
    btn_inspect = d_tui_button(tui, "Inspect", tools_tui_action_inspect, &state);
    btn_validate = d_tui_button(tui, "Validate", tools_tui_action_validate, &state);
    btn_replay = d_tui_button(tui, "Replay", tools_tui_action_replay, &state);
    btn_quit = d_tui_button(tui, "Quit", tools_tui_action_quit, &state);
    if (!root || !title || !status || !btn_inspect || !btn_validate || !btn_replay || !btn_quit) {
        fprintf(stderr, "tools: tui widgets failed\n");
        goto cleanup;
    }
    d_tui_widget_add(root, title);
    d_tui_widget_add(root, status);
    d_tui_widget_add(root, btn_inspect);
    d_tui_widget_add(root, btn_validate);
    d_tui_widget_add(root, btn_replay);
    d_tui_widget_add(root, btn_quit);
    d_tui_set_root(tui, root);
    state.ctx = tui;
    state.status = status;

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
                    state.action = TOOLS_TUI_QUIT;
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
        tools_tui_update_status(&state, timing_mode, clock.app_time_us);
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
            fprintf(stderr, "tools: shutdown=%s\n",
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
    if (state.action == TOOLS_TUI_INSPECT) {
        return tools_run_inspect(DOM_APP_FORMAT_TEXT, compat_expect);
    }
    if (state.action == TOOLS_TUI_VALIDATE) {
        return tools_run_validate(DOM_APP_FORMAT_TEXT, compat_expect);
    }
    if (state.action == TOOLS_TUI_REPLAY) {
        return tools_run_replay();
    }
    return result;
}

static int tools_run_gui_legacy(void)
{
    fprintf(stderr, "tools: gui not implemented\n");
    return D_APP_EXIT_UNAVAILABLE;
}

static void tools_ui_set_status(tools_ui_state* state, const char* fmt, ...)
{
    va_list args;
    if (!state || !fmt) {
        return;
    }
    va_start(args, fmt);
    vsnprintf(state->action_status, sizeof(state->action_status), fmt, args);
    va_end(args);
}

static void tools_renderer_list_init(tools_renderer_list* list)
{
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    uint32_t count;
    uint32_t i;
    if (!list) {
        return;
    }
    memset(list, 0, sizeof(*list));
    count = d_gfx_detect_backends(infos, (uint32_t)(sizeof(infos) / sizeof(infos[0])));
    for (i = 0u; i < count && list->count < TOOLS_UI_RENDERER_MAX; ++i) {
        tools_renderer_entry* entry = &list->entries[list->count];
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

static const char* tools_renderer_default(const tools_renderer_list* list)
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

static void tools_settings_set_renderer(tools_ui_settings* settings, const char* name)
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

static const char* tools_env_or_default(const char* key, const char* fallback)
{
    const char* value = getenv(key);
    if (value && value[0]) {
        return value;
    }
    return fallback;
}

static void tools_ui_collect_loading(tools_ui_state* state,
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
    dom_app_compat_report_init(&report, "tools");
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
            tools_env_or_default("DOM_TESTX_STATUS", "unknown"),
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

static void tools_ui_state_init(tools_ui_state* state,
                                const tools_ui_settings* settings,
                                const dom_app_compat_expect* compat)
{
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    state->screen = TOOLS_UI_LOADING;
    state->main_index = 0;
    state->tools_index = 0;
    state->exit_requested = 0;
    state->loading_ticks = 0;
    state->action_status[0] = '\0';
    tools_renderer_list_init(&state->renderers);
    if (settings) {
        state->settings = *settings;
    } else {
        tools_ui_settings_init(&state->settings);
    }
    if (state->settings.renderer[0] == '\0') {
        tools_settings_set_renderer(&state->settings,
                                    tools_renderer_default(&state->renderers));
    }
    state->tool = TOOLS_TOOL_NONE;
    state->tool_line_count = 0;
    tools_ui_collect_loading(state, compat);
}

static void tools_ui_cycle_renderer(tools_ui_state* state)
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
            tools_settings_set_renderer(&state->settings,
                                        state->renderers.entries[next].name);
            return;
        }
    }
    tools_settings_set_renderer(&state->settings, state->renderers.entries[0].name);
}

static const char* tools_ui_tool_key(tools_ui_tool tool)
{
    switch (tool) {
    case TOOLS_TOOL_WORLD:
        return "tools_world_inspector";
    case TOOLS_TOOL_AGENT:
        return "tools_agent_inspector";
    case TOOLS_TOOL_INSTITUTION:
        return "tools_institution_inspector";
    case TOOLS_TOOL_HISTORY:
        return "tools_history_viewer";
    case TOOLS_TOOL_PACK:
        return "tools_pack_inspector";
    default:
        break;
    }
    return "tools_tool";
}

static void tools_ui_add_tool_line(tools_ui_state* state, const char* text)
{
    if (!state || !text) {
        return;
    }
    if (state->tool_line_count >= TOOLS_UI_TOOL_LINES) {
        return;
    }
    strncpy(state->tool_lines[state->tool_line_count],
            text,
            TOOLS_UI_LABEL_MAX - 1u);
    state->tool_lines[state->tool_line_count][TOOLS_UI_LABEL_MAX - 1u] = '\0';
    state->tool_line_count += 1;
}

static int tools_ui_build_tool_view(tools_ui_state* state,
                                    tools_ui_tool tool,
                                    const dom_app_compat_expect* compat)
{
    dom_app_readonly_adapter ro;
    dom_app_compat_report report;
    dom_app_ro_core_info core;
    char line[TOOLS_UI_LABEL_MAX];
    int ok = 0;

    if (!state) {
        return 0;
    }
    state->tool = tool;
    state->tool_line_count = 0;

    if (tool == TOOLS_TOOL_WORLD || tool == TOOLS_TOOL_PACK) {
        dom_app_ro_init(&ro);
        dom_app_compat_report_init(&report, "tools");
        if (dom_app_ro_open(&ro, compat, &report)) {
            ok = 1;
            snprintf(line, sizeof(line), "%s=ok", tools_ui_tool_key(tool));
            tools_ui_add_tool_line(state, line);
            if (dom_app_ro_get_core_info(&ro, &core) == DOM_APP_RO_OK) {
                snprintf(line, sizeof(line), "packages=%u instances=%u",
                         (unsigned int)core.package_count,
                         (unsigned int)core.instance_count);
                tools_ui_add_tool_line(state, line);
            } else {
                tools_ui_add_tool_line(state, "core_info=unavailable");
            }
            if (tool == TOOLS_TOOL_WORLD) {
                dom_app_ro_tree_node nodes[64];
                dom_app_ro_tree_info tree_info;
                uint32_t i;
                memset(nodes, 0, sizeof(nodes));
                memset(&tree_info, 0, sizeof(tree_info));
                if (dom_app_ro_get_tree(&ro,
                                        "packages_tree",
                                        nodes,
                                        (uint32_t)(sizeof(nodes) / sizeof(nodes[0])),
                                        &tree_info) == DOM_APP_RO_OK) {
                    snprintf(line, sizeof(line), "topology=packages_tree nodes=%u truncated=%u",
                             (unsigned int)tree_info.count,
                             (unsigned int)tree_info.truncated);
                    tools_ui_add_tool_line(state, line);
                    for (i = 0u; i < tree_info.count && state->tool_line_count < TOOLS_UI_TOOL_LINES; ++i) {
                        int indent = (int)(nodes[i].depth * 2u);
                        snprintf(line, sizeof(line), "%*s%s", indent, "", nodes[i].label);
                        tools_ui_add_tool_line(state, line);
                    }
                    if (tree_info.truncated && state->tool_line_count < TOOLS_UI_TOOL_LINES) {
                        tools_ui_add_tool_line(state, "topology_truncated=1");
                    }
                } else {
                    tools_ui_add_tool_line(state, "topology=unsupported");
                }
            } else {
                dom_table_meta meta;
                memset(&meta, 0, sizeof(meta));
                if (dom_app_ro_has_table(&ro, "packages_table") &&
                    dom_app_ro_table_meta(&ro, "packages_table", &meta) == DOM_APP_RO_OK) {
                    snprintf(line, sizeof(line), "packages_table=ok rows=%u cols=%u",
                             (unsigned int)meta.row_count,
                             (unsigned int)meta.col_count);
                    tools_ui_add_tool_line(state, line);
                } else {
                    tools_ui_add_tool_line(state, "packages_table=unsupported");
                }
            }
            dom_app_ro_close(&ro);
        } else {
            snprintf(line, sizeof(line), "%s=unavailable", tools_ui_tool_key(tool));
            tools_ui_add_tool_line(state, line);
            if (report.message[0]) {
                snprintf(line, sizeof(line), "reason=%s", report.message);
                tools_ui_add_tool_line(state, line);
            }
        }
    } else {
        snprintf(line, sizeof(line), "%s=unavailable", tools_ui_tool_key(tool));
        tools_ui_add_tool_line(state, line);
        tools_ui_add_tool_line(state, "reason=unsupported");
    }
    return ok;
}

static void tools_ui_apply_action(tools_ui_state* state,
                                  tools_ui_action action,
                                  dom_app_ui_event_log* log,
                                  const dom_app_compat_expect* compat)
{
    int ok;
    if (!state) {
        return;
    }
    switch (action) {
    case TOOLS_ACTION_START:
        tools_ui_set_status(state, "tools_start=unavailable");
        dom_app_ui_event_log_emit(log, "tools.start", "result=unavailable");
        break;
    case TOOLS_ACTION_LOAD_SAVE:
        tools_ui_set_status(state, "tools_load_save=unavailable");
        dom_app_ui_event_log_emit(log, "tools.load_save", "result=unavailable");
        break;
    case TOOLS_ACTION_INSPECT_REPLAY:
        tools_ui_set_status(state, "tools_inspect_replay=unavailable");
        dom_app_ui_event_log_emit(log, "tools.inspect_replay", "result=unavailable");
        break;
    case TOOLS_ACTION_TOOLS_MENU:
        state->screen = TOOLS_UI_TOOLS_MENU;
        tools_ui_set_status(state, "tools_tools=ok");
        dom_app_ui_event_log_emit(log, "tools.tools", "result=ok");
        break;
    case TOOLS_ACTION_SETTINGS:
        state->screen = TOOLS_UI_SETTINGS;
        tools_ui_set_status(state, "tools_settings=ok");
        dom_app_ui_event_log_emit(log, "tools.settings", "result=ok");
        break;
    case TOOLS_ACTION_EXIT:
        tools_ui_set_status(state, "tools_exit=ok");
        dom_app_ui_event_log_emit(log, "tools.exit", "result=ok");
        state->exit_requested = 1;
        break;
    case TOOLS_ACTION_BACK:
        if (state->screen == TOOLS_UI_TOOL_VIEW) {
            state->screen = TOOLS_UI_TOOLS_MENU;
        } else {
            state->screen = TOOLS_UI_MAIN_MENU;
        }
        break;
    case TOOLS_ACTION_WORLD_INSPECTOR:
        ok = tools_ui_build_tool_view(state, TOOLS_TOOL_WORLD, compat);
        state->screen = TOOLS_UI_TOOL_VIEW;
        tools_ui_set_status(state, "tools_world_inspector=%s", ok ? "ok" : "unavailable");
        dom_app_ui_event_log_emit(log, "tools.world_inspector",
                                  ok ? "result=ok" : "result=unavailable");
        break;
    case TOOLS_ACTION_AGENT_INSPECTOR:
        ok = tools_ui_build_tool_view(state, TOOLS_TOOL_AGENT, compat);
        state->screen = TOOLS_UI_TOOL_VIEW;
        tools_ui_set_status(state, "tools_agent_inspector=%s", ok ? "ok" : "unavailable");
        dom_app_ui_event_log_emit(log, "tools.agent_inspector",
                                  ok ? "result=ok" : "result=unavailable");
        break;
    case TOOLS_ACTION_INSTITUTION_INSPECTOR:
        ok = tools_ui_build_tool_view(state, TOOLS_TOOL_INSTITUTION, compat);
        state->screen = TOOLS_UI_TOOL_VIEW;
        tools_ui_set_status(state, "tools_institution_inspector=%s", ok ? "ok" : "unavailable");
        dom_app_ui_event_log_emit(log, "tools.institution_inspector",
                                  ok ? "result=ok" : "result=unavailable");
        break;
    case TOOLS_ACTION_HISTORY_VIEWER:
        ok = tools_ui_build_tool_view(state, TOOLS_TOOL_HISTORY, compat);
        state->screen = TOOLS_UI_TOOL_VIEW;
        tools_ui_set_status(state, "tools_history_viewer=%s", ok ? "ok" : "unavailable");
        dom_app_ui_event_log_emit(log, "tools.history_viewer",
                                  ok ? "result=ok" : "result=unavailable");
        break;
    case TOOLS_ACTION_PACK_INSPECTOR:
        ok = tools_ui_build_tool_view(state, TOOLS_TOOL_PACK, compat);
        state->screen = TOOLS_UI_TOOL_VIEW;
        tools_ui_set_status(state, "tools_pack_inspector=%s", ok ? "ok" : "unavailable");
        dom_app_ui_event_log_emit(log, "tools.pack_inspector",
                                  ok ? "result=ok" : "result=unavailable");
        break;
    case TOOLS_ACTION_RENDERER_NEXT:
        tools_ui_cycle_renderer(state);
        tools_ui_set_status(state, "settings_renderer=%s", state->settings.renderer);
        break;
    case TOOLS_ACTION_SCALE_UP:
        if (state->settings.ui_scale_percent < 150) {
            state->settings.ui_scale_percent += 25;
        }
        tools_ui_set_status(state, "settings_ui_scale=%d%%", state->settings.ui_scale_percent);
        break;
    case TOOLS_ACTION_SCALE_DOWN:
        if (state->settings.ui_scale_percent > 75) {
            state->settings.ui_scale_percent -= 25;
        }
        tools_ui_set_status(state, "settings_ui_scale=%d%%", state->settings.ui_scale_percent);
        break;
    case TOOLS_ACTION_PALETTE_TOGGLE:
        state->settings.palette = state->settings.palette ? 0 : 1;
        tools_ui_set_status(state, "settings_palette=%s", tools_palette_name(state->settings.palette));
        break;
    case TOOLS_ACTION_LOG_NEXT:
        state->settings.log_level = (state->settings.log_level + 1) % 3;
        tools_ui_set_status(state, "settings_log=%s", tools_log_level_name(state->settings.log_level));
        break;
    case TOOLS_ACTION_DEBUG_TOGGLE:
        state->settings.debug_ui = state->settings.debug_ui ? 0 : 1;
        tools_ui_set_status(state, "settings_debug=%s", state->settings.debug_ui ? "enabled" : "disabled");
        break;
    default:
        break;
    }
}

static tools_ui_action tools_ui_action_from_token(const char* token)
{
    if (!token || !token[0]) {
        return TOOLS_ACTION_NONE;
    }
    if (strcmp(token, "start") == 0) return TOOLS_ACTION_START;
    if (strcmp(token, "load") == 0 || strcmp(token, "load-save") == 0) return TOOLS_ACTION_LOAD_SAVE;
    if (strcmp(token, "replay") == 0 || strcmp(token, "inspect-replay") == 0) return TOOLS_ACTION_INSPECT_REPLAY;
    if (strcmp(token, "tools") == 0) return TOOLS_ACTION_TOOLS_MENU;
    if (strcmp(token, "settings") == 0) return TOOLS_ACTION_SETTINGS;
    if (strcmp(token, "exit") == 0 || strcmp(token, "quit") == 0) return TOOLS_ACTION_EXIT;
    if (strcmp(token, "back") == 0) return TOOLS_ACTION_BACK;
    if (strcmp(token, "world") == 0 || strcmp(token, "world-inspector") == 0) return TOOLS_ACTION_WORLD_INSPECTOR;
    if (strcmp(token, "agent") == 0 || strcmp(token, "agent-inspector") == 0) return TOOLS_ACTION_AGENT_INSPECTOR;
    if (strcmp(token, "institution") == 0 || strcmp(token, "institution-inspector") == 0) return TOOLS_ACTION_INSTITUTION_INSPECTOR;
    if (strcmp(token, "history") == 0 || strcmp(token, "history-viewer") == 0 || strcmp(token, "replay-viewer") == 0) {
        return TOOLS_ACTION_HISTORY_VIEWER;
    }
    if (strcmp(token, "pack") == 0 || strcmp(token, "pack-inspector") == 0) return TOOLS_ACTION_PACK_INSPECTOR;
    if (strcmp(token, "renderer-next") == 0) return TOOLS_ACTION_RENDERER_NEXT;
    if (strcmp(token, "scale-up") == 0) return TOOLS_ACTION_SCALE_UP;
    if (strcmp(token, "scale-down") == 0) return TOOLS_ACTION_SCALE_DOWN;
    if (strcmp(token, "palette") == 0) return TOOLS_ACTION_PALETTE_TOGGLE;
    if (strcmp(token, "log-next") == 0) return TOOLS_ACTION_LOG_NEXT;
    if (strcmp(token, "debug-toggle") == 0) return TOOLS_ACTION_DEBUG_TOGGLE;
    return TOOLS_ACTION_NONE;
}

static void tools_gui_draw_text(d_gfx_cmd_buffer* buf, int x, int y,
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

static void tools_gui_draw_menu(d_gfx_cmd_buffer* buf,
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
        tools_gui_draw_text(buf, x, line_y, items[i], text);
    }
}

static void tools_gui_render(const tools_ui_state* state,
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
    tools_gui_draw_text(buf, 20, y, "Dominium Tools", text);
    y += line_h;
    if (state->screen == TOOLS_UI_LOADING) {
        char line[TOOLS_UI_STATUS_MAX];
        const dom_build_info_v1* build = dom_build_info_v1_get();
        snprintf(line, sizeof(line), "engine=%s", DOMINO_VERSION_STRING);
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "game=%s", DOMINIUM_GAME_VERSION);
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "build_number=%u", (unsigned int)DOM_BUILD_NUMBER);
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "sim_schema_id=%llu", (unsigned long long)dom_sim_schema_id());
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        if (build) {
            snprintf(line, sizeof(line), "sim_schema_version=%u", (unsigned int)build->sim_schema_version);
            tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
            snprintf(line, sizeof(line), "content_schema_version=%u", (unsigned int)build->content_schema_version);
            tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        } else {
            tools_gui_draw_text(buf, 20, y, "sim_schema_version=unknown", text); y += line_h;
            tools_gui_draw_text(buf, 20, y, "content_schema_version=unknown", text); y += line_h;
        }
        tools_gui_draw_text(buf, 20, y, "protocol_law_targets=LAW_TARGETS@1.4.0", text); y += line_h;
        tools_gui_draw_text(buf, 20, y, "protocol_control_caps=CONTROL_CAPS@1.0.0", text); y += line_h;
        tools_gui_draw_text(buf, 20, y, "protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0", text); y += line_h;
        snprintf(line, sizeof(line), "testx=%s", state->testx_status);
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        tools_gui_draw_text(buf, 20, y, state->pack_status, text); y += line_h;
        snprintf(line, sizeof(line), "seed=%s", state->seed_status);
        tools_gui_draw_text(buf, 20, y, line, text); y += line_h;
        tools_gui_draw_text(buf, 20, y, "Loading complete. Press Enter to continue.", text);
        return;
    }
    if (state->screen == TOOLS_UI_MAIN_MENU) {
        y += line_h;
        tools_gui_draw_menu(buf, g_tools_main_menu_items, TOOLS_UI_MAIN_MENU_COUNT,
                            state->main_index, 20, y, line_h, text, highlight);
        y += (TOOLS_UI_MAIN_MENU_COUNT + 1) * line_h;
        if (state->action_status[0]) {
            tools_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == TOOLS_UI_TOOLS_MENU) {
        y += line_h;
        tools_gui_draw_menu(buf, g_tools_menu_items, TOOLS_UI_TOOLS_MENU_COUNT,
                            state->tools_index, 20, y, line_h, text, highlight);
        y += (TOOLS_UI_TOOLS_MENU_COUNT + 1) * line_h;
        if (state->action_status[0]) {
            tools_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == TOOLS_UI_SETTINGS) {
        char lines[TOOLS_UI_MAIN_MENU_COUNT][TOOLS_UI_LABEL_MAX];
        int count = 0;
        int i;
        y += line_h;
        tools_ui_settings_format_lines(&state->settings, (char*)lines,
                                       TOOLS_UI_MAIN_MENU_COUNT,
                                       TOOLS_UI_LABEL_MAX, &count);
        for (i = 0; i < count; ++i) {
            tools_gui_draw_text(buf, 20, y, lines[i], text);
            y += line_h;
        }
        y += line_h;
        tools_gui_draw_text(buf, 20, y, "Keys: R renderer, +/- scale, P palette, L log, D debug, B back", text);
        y += line_h;
        if (state->action_status[0]) {
            tools_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == TOOLS_UI_TOOL_VIEW) {
        int i;
        y += line_h;
        for (i = 0; i < state->tool_line_count; ++i) {
            tools_gui_draw_text(buf, 20, y, state->tool_lines[i], text);
            y += line_h;
        }
        y += line_h;
        tools_gui_draw_text(buf, 20, y, "Keys: B back, Q exit", text);
        if (state->action_status[0]) {
            y += line_h;
            tools_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
}

static int tools_run_tui(const dom_app_ui_run_config* run_cfg,
                         const tools_ui_settings* settings,
                         d_app_timing_mode timing_mode,
                         uint32_t frame_cap_ms,
                         const dom_app_compat_expect* compat_expect)
{
    d_tui_context* tui = 0;
    d_tui_widget* root = 0;
    tools_ui_state ui;
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

    tools_ui_state_init(&ui, settings, compat_expect);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "tools: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "tools: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ui_event_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    if (!dsys_terminal_init()) {
        fprintf(stderr, "tools: terminal unavailable\n");
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
        if (script_ready) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                tools_ui_apply_action(&ui, tools_ui_action_from_token(token), &log, compat_expect);
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
                    tools_ui_apply_action(&ui, TOOLS_ACTION_EXIT, &log, compat_expect);
                } else if (ui.screen == TOOLS_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = TOOLS_UI_MAIN_MENU;
                } else if (ui.screen == TOOLS_UI_MAIN_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.main_index = (ui.main_index > 0) ? (ui.main_index - 1) : (TOOLS_UI_MAIN_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.main_index = (ui.main_index + 1) % TOOLS_UI_MAIN_MENU_COUNT;
                    } else if (key == '\r' || key == '\n') {
                        tools_ui_apply_action(&ui, (tools_ui_action)(ui.main_index + 1), &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_TOOLS_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.tools_index = (ui.tools_index > 0) ? (ui.tools_index - 1) : (TOOLS_UI_TOOLS_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.tools_index = (ui.tools_index + 1) % TOOLS_UI_TOOLS_MENU_COUNT;
                    } else if (key == '\r' || key == '\n') {
                        tools_ui_action action = TOOLS_ACTION_BACK;
                        switch (ui.tools_index) {
                        case 0: action = TOOLS_ACTION_WORLD_INSPECTOR; break;
                        case 1: action = TOOLS_ACTION_AGENT_INSPECTOR; break;
                        case 2: action = TOOLS_ACTION_INSTITUTION_INSPECTOR; break;
                        case 3: action = TOOLS_ACTION_HISTORY_VIEWER; break;
                        case 4: action = TOOLS_ACTION_PACK_INSPECTOR; break;
                        default: action = TOOLS_ACTION_BACK; break;
                        }
                        tools_ui_apply_action(&ui, action, &log, compat_expect);
                    } else if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_RENDERER_NEXT, &log, compat_expect);
                    } else if (key == '+' || key == '=') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_SCALE_UP, &log, compat_expect);
                    } else if (key == '-' || key == '_') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_SCALE_DOWN, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_PALETTE_TOGGLE, &log, compat_expect);
                    } else if (key == 'l' || key == 'L') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_LOG_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_TOOL_VIEW) {
                    if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
                    }
                }
            }
        }
        if (ui.screen == TOOLS_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = TOOLS_UI_MAIN_MENU;
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
            fprintf(stderr, "tools: tui init failed\n");
            goto cleanup;
        }
        root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
        d_tui_widget_add(root, d_tui_label(tui, "Dominium Tools TUI"));
        if (ui.screen == TOOLS_UI_LOADING) {
            char line[TOOLS_UI_STATUS_MAX];
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
        } else if (ui.screen == TOOLS_UI_MAIN_MENU) {
            int i;
            char line[TOOLS_UI_LABEL_MAX];
            for (i = 0; i < TOOLS_UI_MAIN_MENU_COUNT; ++i) {
                snprintf(line, sizeof(line), "%c %s",
                         (i == ui.main_index) ? '>' : ' ',
                         g_tools_main_menu_items[i]);
                d_tui_widget_add(root, d_tui_label(tui, line));
            }
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == TOOLS_UI_TOOLS_MENU) {
            int i;
            char line[TOOLS_UI_LABEL_MAX];
            for (i = 0; i < TOOLS_UI_TOOLS_MENU_COUNT; ++i) {
                snprintf(line, sizeof(line), "%c %s",
                         (i == ui.tools_index) ? '>' : ' ',
                         g_tools_menu_items[i]);
                d_tui_widget_add(root, d_tui_label(tui, line));
            }
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == TOOLS_UI_SETTINGS) {
            char lines[TOOLS_UI_MAIN_MENU_COUNT][TOOLS_UI_LABEL_MAX];
            int count = 0;
            int i;
            tools_ui_settings_format_lines(&ui.settings, (char*)lines,
                                           TOOLS_UI_MAIN_MENU_COUNT,
                                           TOOLS_UI_LABEL_MAX, &count);
            for (i = 0; i < count; ++i) {
                d_tui_widget_add(root, d_tui_label(tui, lines[i]));
            }
            d_tui_widget_add(root, d_tui_label(tui, "R renderer, +/- scale, P palette, L log, D debug, B back"));
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == TOOLS_UI_TOOL_VIEW) {
            int i;
            for (i = 0; i < ui.tool_line_count; ++i) {
                d_tui_widget_add(root, d_tui_label(tui, ui.tool_lines[i]));
            }
            d_tui_widget_add(root, d_tui_label(tui, "B back, Q exit"));
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
            fprintf(stderr, "tools: shutdown=%s\n",
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

static int tools_run_gui(const dom_app_ui_run_config* run_cfg,
                         const tools_ui_settings* settings,
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
    dom_app_clock clock;
    uint64_t frame_start_us = 0u;
    tools_ui_state ui;
    dom_app_ui_script script;
    dom_app_ui_event_log log;
    int script_ready = 0;
    const char* renderer = 0;
    int headless = run_cfg && run_cfg->headless_set ? run_cfg->headless : 0;
    int max_frames = run_cfg && run_cfg->max_frames_set ? (int)run_cfg->max_frames : 0;
    int frame_count = 0;

    tools_ui_state_init(&ui, settings, compat_expect);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "tools: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    renderer = ui.settings.renderer[0] ? ui.settings.renderer : tools_renderer_default(&ui.renderers);
    if (headless && renderer && strcmp(renderer, "null") != 0) {
        fprintf(stderr, "tools: headless forces null renderer (requested %s)\n", renderer);
        renderer = "null";
        tools_settings_set_renderer(&ui.settings, renderer);
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "tools: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ui_event_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    dsys_lifecycle_init();
    lifecycle_ready = 1;
    dom_app_clock_init(&clock, timing_mode);

    if (!headless) {
        memset(&desc, 0, sizeof(desc));
        desc.x = 0;
        desc.y = 0;
        desc.width = 800;
        desc.height = 600;
        desc.mode = DWIN_MODE_WINDOWED;
        win = dsys_window_create(&desc);
        if (!win) {
            fprintf(stderr, "tools: window creation failed (%s)\n", dsys_last_error_text());
            goto cleanup;
        }
        dsys_window_show(win);
        d_system_set_native_window_handle(dsys_window_get_native_handle(win));
    } else {
        d_system_set_native_window_handle(0);
    }

    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "tools: renderer init failed\n");
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
        fb_w = 800;
        fb_h = 600;
        d_gfx_bind_surface(0, fb_w, fb_h);
    }

    while (!dsys_lifecycle_shutdown_requested()) {
        if (timing_mode == D_APP_TIMING_INTERACTIVE) {
            frame_start_us = dsys_time_now_us();
        }
        if (script_ready) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                tools_ui_apply_action(&ui, tools_ui_action_from_token(token), &log, compat_expect);
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
                    tools_ui_apply_action(&ui, TOOLS_ACTION_EXIT, &log, compat_expect);
                } else if (ui.screen == TOOLS_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = TOOLS_UI_MAIN_MENU;
                } else if (ui.screen == TOOLS_UI_MAIN_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.main_index = (ui.main_index > 0) ? (ui.main_index - 1) : (TOOLS_UI_MAIN_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.main_index = (ui.main_index + 1) % TOOLS_UI_MAIN_MENU_COUNT;
                    } else if (key == '\r' || key == '\n' || key == ' ') {
                        tools_ui_apply_action(&ui, (tools_ui_action)(ui.main_index + 1), &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_TOOLS_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.tools_index = (ui.tools_index > 0) ? (ui.tools_index - 1) : (TOOLS_UI_TOOLS_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.tools_index = (ui.tools_index + 1) % TOOLS_UI_TOOLS_MENU_COUNT;
                    } else if (key == '\r' || key == '\n' || key == ' ') {
                        tools_ui_action action = TOOLS_ACTION_BACK;
                        switch (ui.tools_index) {
                        case 0: action = TOOLS_ACTION_WORLD_INSPECTOR; break;
                        case 1: action = TOOLS_ACTION_AGENT_INSPECTOR; break;
                        case 2: action = TOOLS_ACTION_INSTITUTION_INSPECTOR; break;
                        case 3: action = TOOLS_ACTION_HISTORY_VIEWER; break;
                        case 4: action = TOOLS_ACTION_PACK_INSPECTOR; break;
                        default: action = TOOLS_ACTION_BACK; break;
                        }
                        tools_ui_apply_action(&ui, action, &log, compat_expect);
                    } else if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_RENDERER_NEXT, &log, compat_expect);
                    } else if (key == '+' || key == '=') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_SCALE_UP, &log, compat_expect);
                    } else if (key == '-' || key == '_') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_SCALE_DOWN, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_PALETTE_TOGGLE, &log, compat_expect);
                    } else if (key == 'l' || key == 'L') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_LOG_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                } else if (ui.screen == TOOLS_UI_TOOL_VIEW) {
                    if (key == 'b' || key == 'B') {
                        tools_ui_apply_action(&ui, TOOLS_ACTION_BACK, &log, compat_expect);
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
        if (ui.screen == TOOLS_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = TOOLS_UI_MAIN_MENU;
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
                tools_gui_render(&ui, buf, fb_w, fb_h);
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
            fprintf(stderr, "tools: shutdown=%s\n",
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

static int tools_open_readonly(dom_app_readonly_adapter* ro,
                               const dom_app_compat_expect* expect)
{
    dom_app_compat_report report;
    dom_app_compat_report_init(&report, "tools");
    dom_app_ro_init(ro);
    if (!dom_app_ro_open(ro, expect, &report)) {
        fprintf(stderr, "tools: compatibility failure: %s\n",
                report.message[0] ? report.message : "unknown");
        dom_app_compat_print_report(&report, stderr);
        return 0;
    }
    return 1;
}

static void tools_print_json_string(const char* s)
{
    const unsigned char* p = (const unsigned char*)(s ? s : "");
    putchar('\"');
    while (*p) {
        unsigned char c = *p++;
        switch (c) {
        case '\\\\': putchar('\\\\'); putchar('\\\\'); break;
        case '\"':  putchar('\\\\'); putchar('\"'); break;
        case '\\b': putchar('\\\\'); putchar('b'); break;
        case '\\f': putchar('\\\\'); putchar('f'); break;
        case '\\n': putchar('\\\\'); putchar('n'); break;
        case '\\r': putchar('\\\\'); putchar('r'); break;
        case '\\t': putchar('\\\\'); putchar('t'); break;
        default:
            if (c < 0x20) {
                printf("\\\\u%04x", (unsigned int)c);
            } else {
                putchar((int)c);
            }
            break;
        }
    }
    putchar('\"');
}

static void tools_print_compat_json(const dom_app_compat_report* report, int ok)
{
    printf("\"compat\":{");
    printf("\"status\":");
    tools_print_json_string(ok ? "ok" : "failed");
    printf(",\"engine_version\":");
    tools_print_json_string(report->engine_version ? report->engine_version : "");
    printf(",\"game_version\":");
    tools_print_json_string(report->game_version ? report->game_version : "");
    printf(",\"build_id\":");
    tools_print_json_string(report->build_id ? report->build_id : "");
    printf(",\"git_hash\":");
    tools_print_json_string(report->git_hash ? report->git_hash : "");
    printf(",\"toolchain_id\":");
    tools_print_json_string(report->toolchain_id ? report->toolchain_id : "");
    printf(",\"sim_schema_id\":%llu",
           (unsigned long long)report->sim_schema_id);
    printf(",\"build_info_abi\":%u",
           (unsigned int)report->build_info_abi);
    printf(",\"caps_abi\":%u",
           (unsigned int)report->caps_abi);
    printf(",\"gfx_api\":%u",
           (unsigned int)report->gfx_api);
    if (!ok && report->message[0]) {
        printf(",\"error\":");
        tools_print_json_string(report->message);
    }
    printf("}");
}

static int tools_run_inspect(dom_app_output_format format,
                             const dom_app_compat_expect* expect)
{
    dom_app_readonly_adapter ro;
    dom_app_ro_core_info core_info;
    dom_app_ro_tree_info tree_info;
    dom_app_ro_tree_node nodes[256];

    if (!tools_open_readonly(&ro, expect)) {
        return D_APP_EXIT_FAILURE;
    }
    memset(&core_info, 0, sizeof(core_info));
    if (dom_app_ro_get_core_info(&ro, &core_info) != DOM_APP_RO_OK) {
        fprintf(stderr, "tools: core info unavailable\n");
        dom_app_ro_close(&ro);
        return D_APP_EXIT_FAILURE;
    }
    memset(&tree_info, 0, sizeof(tree_info));
    if (dom_app_ro_get_tree(&ro,
                            "packages_tree",
                            nodes,
                            (uint32_t)(sizeof(nodes) / sizeof(nodes[0])),
                            &tree_info) != DOM_APP_RO_OK) {
        fprintf(stderr, "tools: topology unsupported\n");
        dom_app_ro_close(&ro);
        return D_APP_EXIT_UNAVAILABLE;
    }
    dom_app_ro_print_inspector_bundle(format,
                                      &core_info,
                                      "packages_tree",
                                      nodes,
                                      tree_info.count,
                                      tree_info.truncated,
                                      dom_app_ro_snapshots_supported(),
                                      dom_app_ro_events_supported(),
                                      dom_app_ro_replay_supported());
    dom_app_ro_close(&ro);
    return D_APP_EXIT_OK;
}

static int tools_run_validate(dom_app_output_format format,
                              const dom_app_compat_expect* expect)
{
    dom_app_compat_report report;
    int ok;
    dom_app_compat_report_init(&report, "tools");
    ok = dom_app_compat_check(expect, &report);

    if (format == DOM_APP_FORMAT_JSON) {
        printf("{\"validate_status\":");
        tools_print_json_string(ok ? "ok" : "failed");
        printf(",");
        tools_print_compat_json(&report, ok);
        printf("}\n");
    } else {
        printf("validate_status=%s\n", ok ? "ok" : "failed");
        dom_app_compat_print_report(&report, stdout);
    }
    if (!ok) {
        fprintf(stderr, "tools: compatibility failure: %s\n",
                report.message[0] ? report.message : "unknown");
        return D_APP_EXIT_FAILURE;
    }
    return D_APP_EXIT_OK;
}

static int tools_run_replay(void)
{
    fprintf(stderr, "tools: replay unsupported\n");
    return D_APP_EXIT_UNAVAILABLE;
}

static int tools_ui_execute_command(const char* cmd,
                                    const tools_ui_settings* settings,
                                    dom_app_ui_event_log* log,
                                    dom_app_output_format format,
                                    const dom_app_compat_expect* compat,
                                    char* status,
                                    size_t status_cap,
                                    int emit_text)
{
    int res;
    const char* result_text;
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!cmd || !cmd[0]) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools: missing command");
        }
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "start") == 0) {
        dom_app_ui_event_log_emit(log, "tools.start", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_start=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "tools: start unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "load-save") == 0) {
        dom_app_ui_event_log_emit(log, "tools.load_save", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_load_save=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "tools: load-save unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "inspect-replay") == 0) {
        res = tools_run_replay();
        result_text = (res == D_APP_EXIT_OK) ? "ok" :
                      (res == D_APP_EXIT_UNAVAILABLE) ? "unavailable" : "failed";
        dom_app_ui_event_log_emit(log, "tools.inspect_replay",
                                  (res == D_APP_EXIT_OK) ? "result=ok" :
                                  (res == D_APP_EXIT_UNAVAILABLE) ? "result=unavailable" : "result=failed");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_inspect_replay=%s", result_text);
        }
        if (emit_text) {
            printf("tools_inspect_replay=%s\n", result_text);
        }
        return res;
    }
    if (strcmp(cmd, "tools") == 0) {
        dom_app_ui_event_log_emit(log, "tools.tools", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_tools=ok");
        }
        if (emit_text) {
            printf("tools_tools=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "settings") == 0) {
        char lines[TOOLS_UI_MAIN_MENU_COUNT][TOOLS_UI_LABEL_MAX];
        int count = 0;
        int i;
        tools_ui_settings_format_lines(settings, (char*)lines,
                                       TOOLS_UI_MAIN_MENU_COUNT,
                                       TOOLS_UI_LABEL_MAX, &count);
        dom_app_ui_event_log_emit(log, "tools.settings", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_settings=ok");
        }
        if (emit_text) {
            printf("tools_settings=ok\n");
            for (i = 0; i < count; ++i) {
                printf("%s\n", lines[i]);
            }
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "exit") == 0) {
        dom_app_ui_event_log_emit(log, "tools.exit", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_exit=ok");
        }
        if (emit_text) {
            printf("tools_exit=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "world-inspector") == 0) {
        res = tools_run_inspect(format, compat);
        result_text = (res == D_APP_EXIT_OK) ? "ok" :
                      (res == D_APP_EXIT_UNAVAILABLE) ? "unavailable" : "failed";
        dom_app_ui_event_log_emit(log, "tools.world_inspector",
                                  (res == D_APP_EXIT_OK) ? "result=ok" :
                                  (res == D_APP_EXIT_UNAVAILABLE) ? "result=unavailable" : "result=failed");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_world_inspector=%s", result_text);
        }
        if (emit_text) {
            printf("tools_world_inspector=%s\n", result_text);
        }
        return res;
    }
    if (strcmp(cmd, "agent-inspector") == 0) {
        dom_app_ui_event_log_emit(log, "tools.agent_inspector", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_agent_inspector=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "tools: agent inspector unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "institution-inspector") == 0) {
        dom_app_ui_event_log_emit(log, "tools.institution_inspector", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_institution_inspector=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "tools: institution inspector unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "history-viewer") == 0) {
        res = tools_run_replay();
        result_text = (res == D_APP_EXIT_OK) ? "ok" :
                      (res == D_APP_EXIT_UNAVAILABLE) ? "unavailable" : "failed";
        dom_app_ui_event_log_emit(log, "tools.history_viewer",
                                  (res == D_APP_EXIT_OK) ? "result=ok" :
                                  (res == D_APP_EXIT_UNAVAILABLE) ? "result=unavailable" : "result=failed");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_history_viewer=%s", result_text);
        }
        if (emit_text) {
            printf("tools_history_viewer=%s\n", result_text);
        }
        return res;
    }
    if (strcmp(cmd, "pack-inspector") == 0) {
        res = tools_run_inspect(format, compat);
        result_text = (res == D_APP_EXIT_OK) ? "ok" :
                      (res == D_APP_EXIT_UNAVAILABLE) ? "unavailable" : "failed";
        dom_app_ui_event_log_emit(log, "tools.pack_inspector",
                                  (res == D_APP_EXIT_OK) ? "result=ok" :
                                  (res == D_APP_EXIT_UNAVAILABLE) ? "result=unavailable" : "result=failed");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "tools_pack_inspector=%s", result_text);
        }
        if (emit_text) {
            printf("tools_pack_inspector=%s\n", result_text);
        }
        return res;
    }
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "tools: unknown command '%s'", cmd);
    }
    return D_APP_EXIT_USAGE;
}

int tools_main(int argc, char** argv)
{
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    int timing_mode_set = 0;
    d_app_timing_mode timing_mode = D_APP_TIMING_DETERMINISTIC;
    uint32_t frame_cap_ms = 16u;
    dom_app_output_format output_format = DOM_APP_FORMAT_TEXT;
    int output_format_set = 0;
    dom_app_compat_expect compat_expect;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    dom_app_ui_run_config ui_run;
    tools_ui_settings ui_settings;
    dom_app_ui_event_log ui_log;
    int ui_log_open = 0;
    const char* cmd = 0;
    int i;
    dom_app_ui_request_init(&ui_req);
    dom_app_ui_run_config_init(&ui_run);
    dom_app_ui_event_log_init(&ui_log);
    tools_ui_settings_init(&ui_settings);
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
            fprintf(stderr, "tools: %s\n", ui_err);
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
                fprintf(stderr, "tools: %s\n", ui_err);
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
        if (strncmp(argv[i], "--format=", 9) == 0) {
            if (!dom_app_parse_output_format(argv[i] + 9, &output_format)) {
                fprintf(stderr, "tools: invalid --format value\n");
                return D_APP_EXIT_USAGE;
            }
            output_format_set = 1;
            continue;
        }
        if (strcmp(argv[i], "--format") == 0 && i + 1 < argc) {
            if (!dom_app_parse_output_format(argv[i + 1], &output_format)) {
                fprintf(stderr, "tools: invalid --format value\n");
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
        if (strncmp(argv[i], "--renderer=", 11) == 0) {
            strncpy(ui_settings.renderer, argv[i] + 11, sizeof(ui_settings.renderer) - 1u);
            ui_settings.renderer[sizeof(ui_settings.renderer) - 1u] = '\0';
            continue;
        }
        if (strcmp(argv[i], "--renderer") == 0 && i + 1 < argc) {
            strncpy(ui_settings.renderer, argv[i + 1], sizeof(ui_settings.renderer) - 1u);
            ui_settings.renderer[sizeof(ui_settings.renderer) - 1u] = '\0';
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--ui-scale=", 11) == 0) {
            int value = 0;
            if (!tools_parse_ui_scale(argv[i] + 11, &value)) {
                fprintf(stderr, "tools: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            continue;
        }
        if (strcmp(argv[i], "--ui-scale") == 0 && i + 1 < argc) {
            int value = 0;
            if (!tools_parse_ui_scale(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--palette=", 10) == 0) {
            int value = 0;
            if (!tools_parse_palette(argv[i] + 10, &value)) {
                fprintf(stderr, "tools: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            continue;
        }
        if (strcmp(argv[i], "--palette") == 0 && i + 1 < argc) {
            int value = 0;
            if (!tools_parse_palette(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-verbosity=", 16) == 0) {
            int value = 0;
            if (!tools_parse_log_level(argv[i] + 16, &value)) {
                fprintf(stderr, "tools: invalid --log-verbosity value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.log_level = value;
            continue;
        }
        if (strcmp(argv[i], "--log-verbosity") == 0 && i + 1 < argc) {
            int value = 0;
            if (!tools_parse_log_level(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --log-verbosity value\n");
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
        if (strncmp(argv[i], "--frame-cap-ms=", 15) == 0) {
            if (!tools_parse_frame_cap_ms(argv[i] + 15, &frame_cap_ms)) {
                fprintf(stderr, "tools: invalid --frame-cap-ms value\n");
                return D_APP_EXIT_USAGE;
            }
            continue;
        }
        if (strcmp(argv[i], "--frame-cap-ms") == 0 && i + 1 < argc) {
            if (!tools_parse_frame_cap_ms(argv[i + 1], &frame_cap_ms)) {
                fprintf(stderr, "tools: invalid --frame-cap-ms value\n");
                return D_APP_EXIT_USAGE;
            }
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
            if (!tools_parse_u64(argv[i] + 21, &value)) {
                fprintf(stderr, "tools: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-sim-schema") == 0 && i + 1 < argc) {
            uint64_t value = 0;
            if (!tools_parse_u64(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --expect-sim-schema value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.sim_schema_id = value;
            compat_expect.has_sim_schema_id = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-build-info-abi=", 25) == 0) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i] + 25, &value)) {
                fprintf(stderr, "tools: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-build-info-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --expect-build-info-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.build_info_abi = value;
            compat_expect.has_build_info_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-caps-abi=", 19) == 0) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i] + 19, &value)) {
                fprintf(stderr, "tools: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-caps-abi") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --expect-caps-abi value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.caps_abi = value;
            compat_expect.has_caps_abi = 1;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--expect-gfx-api=", 17) == 0) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i] + 17, &value)) {
                fprintf(stderr, "tools: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-gfx-api") == 0 && i + 1 < argc) {
            uint32_t value = 0;
            if (!tools_parse_u32(argv[i + 1], &value)) {
                fprintf(stderr, "tools: invalid --expect-gfx-api value\n");
                return D_APP_EXIT_USAGE;
            }
            compat_expect.gfx_api = value;
            compat_expect.has_gfx_api = 1;
            i += 1;
            continue;
        }
        if (argv[i][0] != '-') {
            if (!cmd) {
                cmd = argv[i];
                continue;
            }
            fprintf(stderr, "tools: unexpected argument '%s'\n", argv[i]);
            return D_APP_EXIT_USAGE;
        }
    }

    if (want_help) {
        tools_print_help();
        return D_APP_EXIT_OK;
    }
    if (want_version) {
        tools_print_version(DOMINIUM_TOOLS_VERSION);
        return D_APP_EXIT_OK;
    }
    ui_mode = dom_app_select_ui_mode(&ui_req, DOM_APP_UI_NONE);
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "tools: --deterministic and --interactive are mutually exclusive\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "tools: --smoke requires deterministic mode\n");
        return D_APP_EXIT_USAGE;
    }
    if (output_format_set &&
        (want_build_info || want_status || want_smoke || want_selftest)) {
        fprintf(stderr, "tools: --format only applies to inspect/validate/world-inspector/pack-inspector\n");
        return D_APP_EXIT_USAGE;
    }
    if ((ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI) &&
        (want_build_info || want_status || want_smoke || want_selftest || cmd)) {
        fprintf(stderr, "tools: --ui=%s cannot combine with CLI commands\n",
                dom_app_ui_mode_name(ui_mode));
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
        timing_mode = (ui_mode == DOM_APP_UI_TUI) ? D_APP_TIMING_INTERACTIVE
                                                  : D_APP_TIMING_DETERMINISTIC;
    }
    if (timing_mode == D_APP_TIMING_DETERMINISTIC) {
        frame_cap_ms = 0u;
    }
    if (want_smoke || want_selftest) {
        want_status = 1;
    }
    if (want_build_info) {
        tools_print_build_info("tools", DOMINIUM_TOOLS_VERSION);
    }
    if (want_status) {
        if (want_smoke || want_selftest) {
            printf("tools_smoke=ok\\n");
        } else {
            printf("tools_status=ok\\n");
        }
        if (!cmd) {
            return D_APP_EXIT_OK;
        }
    }
    if (ui_mode == DOM_APP_UI_TUI) {
        return tools_run_tui(&ui_run, &ui_settings, timing_mode, frame_cap_ms, &compat_expect);
    }
    if (ui_mode == DOM_APP_UI_GUI) {
        return tools_run_gui(&ui_run, &ui_settings, timing_mode, frame_cap_ms, &compat_expect);
    }
    if (!cmd) {
        tools_print_help();
        return D_APP_EXIT_USAGE;
    }

    if (output_format_set) {
        if (strcmp(cmd, "inspect") != 0 &&
            strcmp(cmd, "validate") != 0 &&
            strcmp(cmd, "world-inspector") != 0 &&
            strcmp(cmd, "pack-inspector") != 0) {
            fprintf(stderr, "tools: --format only applies to inspect/validate/world-inspector/pack-inspector\n");
            return D_APP_EXIT_USAGE;
        }
    }

    if (strcmp(cmd, "inspect") == 0) {
        return tools_run_inspect(output_format, &compat_expect);
    }
    if (strcmp(cmd, "validate") == 0) {
        return tools_run_validate(output_format, &compat_expect);
    }
    if (strcmp(cmd, "replay") == 0) {
        return tools_run_replay();
    }

    if (ui_run.log_set && !ui_log_open) {
        if (!dom_app_ui_event_log_open(&ui_log, ui_run.log_path)) {
            fprintf(stderr, "tools: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
        ui_log_open = 1;
    }
    {
        char status[160];
        int res = tools_ui_execute_command(cmd, &ui_settings, &ui_log,
                                           output_format, &compat_expect,
                                           status, sizeof(status), 1);
        if (ui_log_open) {
            dom_app_ui_event_log_close(&ui_log);
        }
        if (res != D_APP_EXIT_USAGE) {
            return res;
        }
    }

    printf("tools: unknown command '%s'\\n", cmd);
    tools_print_help();
    return D_APP_EXIT_USAGE;
}

int main(int argc, char** argv)
{
    return tools_main(argc, argv);
}
