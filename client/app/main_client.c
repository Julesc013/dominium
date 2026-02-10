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
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/readonly_adapter.h"
#include "dominium/app/readonly_format.h"
#include "dominium/app/ui_event_log.h"
#include "dominium/app/ui_presentation.h"
#include "dominium/session/mp0_session.h"
#include "client_input_bindings.h"
#include "client_shell.h"
#include "readonly_view_model.h"
#include "client_ui_compositor.h"
#include "client_command_bridge.h"
#include "client_models_options.h"
#include "client_models_server.h"
#include "client_models_world.h"
#include "client_mode_cli.h"
#include "client_mode_tui.h"
#include "client_mode_gui.h"
#include "client_fs_adapter.h"
#include "client_network_adapter.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <ctype.h>
#include <math.h>
#include <errno.h>
#if defined(_WIN32)
#include <direct.h>
#endif
#if defined(_WIN32)
#include <io.h>
#else
#include <dirent.h>
#endif

#if !defined(_WIN32)
int mkdir(const char* path, int mode);
#endif

#define CLIENT_UI_DEFAULT_SCENARIO_PATH "data/scenarios/default.scenario"
#define CLIENT_UI_DEFAULT_VARIANT_PATH "data/variants/default.variant"

static void client_print_platform_caps(void);
static void client_ui_copy_string(char* out, size_t cap, const char* value);

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
    printf("  --accessibility-preset <path> Apply accessibility preset (data-only)\n");
    printf("  --locale <id>               Select localization id (e.g. en_US)\n");
    printf("  --locale-pack <path>        Add localization pack root (can repeat)\n");
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
    printf("  client.*        Canonical command namespace (bridged to CLI handlers)\n");
    printf("  client.session.begin    Explicitly transition SessionReady -> SessionRunning\n");
    printf("  client.session.resume   Deterministic session resume path\n");
    printf("  client.session.abort    Abort active transition/run and tear down\n");
    printf("  client.session.inspect  Inspect fogged world state at SessionReady\n");
    printf("  client.session.map.open Open map panel at SessionReady\n");
    printf("  client.session.stats    Open stats panel at SessionReady\n");
    printf("  client.session.replay.toggle Toggle replay recording at SessionReady\n");
    printf("  new-world       Create a new world (use built-in templates)\n");
    printf("  create-world    Create + save world (auto path if omitted)\n");
    printf("  load-world      Load a world save (default path or path=...)\n");
    printf("  scenario-load   Load a scenario file (path=... variant=...)\n");
    printf("  inspect-replay  Inspect a replay or save (path=...)\n");
    printf("  save            Save current world (default path or path=...)\n");
    printf("  replay-save     Save replay event stream (default path or path=...)\n");
    printf("  profile-next    Cycle world creation profile\n");
    printf("  profile-prev    Cycle world creation profile (reverse)\n");
    printf("  preset-next     Cycle meta-law preset\n");
    printf("  preset-prev     Cycle meta-law preset (reverse)\n");
    printf("  accessibility-next Cycle accessibility preset\n");
    printf("  keybind-next    Cycle keybind profile\n");
    printf("  settings-reset  Reset local presentation settings to defaults\n");
    printf("  replay-step     Step one replay event (UI only)\n");
    printf("  replay-rewind   Rewind replay cursor (UI only)\n");
    printf("  replay-pause    Toggle replay pause (UI only)\n");
    printf("  templates       List available templates\n");
    printf("  mode            Set navigation mode (policy.mode.*)\n");
    printf("  move            Move (dx= dy= dz= or move-forward/back/left/right/up/down)\n");
    printf("  spawn           Reset to spawn position\n");
    printf("  camera          Set camera mode (camera.*)\n");
    printf("  camera-next     Cycle camera modes\n");
    printf("  inspect-toggle  Toggle inspect overlay\n");
    printf("  hud-toggle      Toggle HUD\n");
    printf("  domain          Focus a node id for inspection\n");
    printf("  where           Show current world status\n");
    printf("  simulate        Advance simulation tick (agent planning)\n");
    printf("  agents          List agents\n");
    printf("  agent-add       Add an agent (caps/auth/knowledge)\n");
    printf("  goals           List goals\n");
    printf("  goal-add        Add a goal for an agent\n");
    printf("  delegate        Create a delegation\n");
    printf("  delegations     List delegations\n");
    printf("  authority-grant Grant authority\n");
    printf("  authority-list  List authority grants\n");
    printf("  constraint-add  Add a constraint\n");
    printf("  constraint-list List constraints\n");
    printf("  institution-create Create an institution\n");
    printf("  institution-list   List institutions\n");
    printf("  network-create  Create a network\n");
    printf("  network-list    List networks\n");
    printf("  tools           Open tools shell (handoff)\n");
    printf("  settings        Show current UI settings\n");
    printf("  exit            Exit client shell\n");
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

static u32 client_collect_capabilities(const char* env_text,
                                       char* storage,
                                       size_t storage_cap,
                                       const char** out_caps,
                                       u32 out_caps_cap)
{
    u32 count = 0u;
    char* cursor = 0;
    if (!env_text || !env_text[0] || !storage || storage_cap == 0u || !out_caps || out_caps_cap == 0u) {
        return 0u;
    }
    strncpy(storage, env_text, storage_cap - 1u);
    storage[storage_cap - 1u] = '\0';
    cursor = storage;
    while (*cursor && count < out_caps_cap) {
        char* comma = strchr(cursor, ',');
        while (*cursor && isspace((unsigned char)*cursor)) {
            cursor++;
        }
        if (comma) {
            *comma = '\0';
        }
        {
            char* end = cursor + strlen(cursor);
            while (end > cursor && isspace((unsigned char)end[-1])) {
                end--;
            }
            *end = '\0';
        }
        if (*cursor) {
            out_caps[count++] = cursor;
        }
        if (!comma) {
            break;
        }
        cursor = comma + 1;
    }
    return count;
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
    char ui_density[24];
    char verbosity[24];
    char keybind_profile_id[64];
    char accessibility_preset_id[64];
    int reduced_motion;
    int keyboard_only;
    int screen_reader;
    int low_cognitive_load;
    const dom_app_ui_locale_table* locale;
} client_ui_settings;

static void client_apply_accessibility(client_ui_settings* settings,
                                       const dom_app_ui_accessibility_preset* preset)
{
    if (!settings || !preset) {
        return;
    }
    if (preset->has_ui_scale) {
        settings->ui_scale_percent = preset->ui_scale_percent;
    }
    if (preset->has_palette) {
        settings->palette = preset->palette;
    }
    if (preset->has_log_level) {
        settings->log_level = preset->log_level;
    }
    if (preset->ui_density[0]) {
        strncpy(settings->ui_density, preset->ui_density, sizeof(settings->ui_density) - 1u);
        settings->ui_density[sizeof(settings->ui_density) - 1u] = '\0';
    }
    if (preset->verbosity[0]) {
        strncpy(settings->verbosity, preset->verbosity, sizeof(settings->verbosity) - 1u);
        settings->verbosity[sizeof(settings->verbosity) - 1u] = '\0';
    }
    if (preset->keybind_profile_id[0]) {
        strncpy(settings->keybind_profile_id, preset->keybind_profile_id,
                sizeof(settings->keybind_profile_id) - 1u);
        settings->keybind_profile_id[sizeof(settings->keybind_profile_id) - 1u] = '\0';
    }
    if (preset->preset_id[0]) {
        strncpy(settings->accessibility_preset_id, preset->preset_id,
                sizeof(settings->accessibility_preset_id) - 1u);
        settings->accessibility_preset_id[sizeof(settings->accessibility_preset_id) - 1u] = '\0';
    }
    settings->reduced_motion = preset->reduced_motion ? 1 : 0;
    settings->keyboard_only = preset->keyboard_only ? 1 : 0;
    settings->screen_reader = preset->screen_reader ? 1 : 0;
    settings->low_cognitive_load = preset->low_cognitive_load ? 1 : 0;
}

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
    strncpy(settings->ui_density, "standard", sizeof(settings->ui_density) - 1u);
    settings->ui_density[sizeof(settings->ui_density) - 1u] = '\0';
    strncpy(settings->verbosity, "normal", sizeof(settings->verbosity) - 1u);
    settings->verbosity[sizeof(settings->verbosity) - 1u] = '\0';
    strncpy(settings->keybind_profile_id, "default", sizeof(settings->keybind_profile_id) - 1u);
    settings->keybind_profile_id[sizeof(settings->keybind_profile_id) - 1u] = '\0';
    strncpy(settings->accessibility_preset_id, "default",
            sizeof(settings->accessibility_preset_id) - 1u);
    settings->accessibility_preset_id[sizeof(settings->accessibility_preset_id) - 1u] = '\0';
    settings->reduced_motion = 0;
    settings->keyboard_only = 0;
    settings->screen_reader = 0;
    settings->low_cognitive_load = 0;
    settings->locale = NULL;
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
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride, "[presentation]");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "renderer=%s", settings->renderer[0] ? settings->renderer : "auto");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "ui_scale=%d%%", settings->ui_scale_percent);
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "palette=%s", client_palette_name(settings->palette));
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "ui_density=%s", settings->ui_density[0] ? settings->ui_density : "standard");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "verbosity=%s", settings->verbosity[0] ? settings->verbosity : "normal");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride, "[input]");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "keybind_profile=%s",
                 settings->keybind_profile_id[0] ? settings->keybind_profile_id : "default");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "input_mode=%s", settings->keyboard_only ? "keyboard_only" : "standard");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride, "[accessibility]");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "accessibility_preset=%s",
                 settings->accessibility_preset_id[0] ? settings->accessibility_preset_id : "default");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "reduced_motion=%s", settings->reduced_motion ? "enabled" : "disabled");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "screen_reader=%s", settings->screen_reader ? "enabled" : "disabled");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "keyboard_only=%s", settings->keyboard_only ? "enabled" : "disabled");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "low_cognitive_load=%s", settings->low_cognitive_load ? "enabled" : "disabled");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride, "[debug]");
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "log_verbosity=%s", client_log_level_name(settings->log_level));
        count += 1;
    }
    if ((size_t)count < line_cap) {
        snprintf(line0 + (line_stride * count), line_stride,
                 "debug_ui=%s", settings->debug_ui ? "enabled" : "disabled");
        count += 1;
    }
    if (out_count) {
        *out_count = count;
    }
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

#define CLIENT_UI_MENU_COUNT 6
#define CLIENT_UI_SETTINGS_LINES 20
#define CLIENT_UI_STATUS_MAX 180
#define CLIENT_UI_LABEL_MAX 128
#define CLIENT_UI_RENDERER_MAX 8
#define CLIENT_UI_EVENT_LINES 16
#define CLIENT_UI_CONSOLE_MAX 196
#define CLIENT_UI_MAX_LINES 64
#define CLIENT_UI_PATH_MAX 260
#define CLIENT_UI_PACK_MAX 8
#define CLIENT_UI_PACK_NAME_MAX 64
#define CLIENT_UI_WORLD_MAX 16
#define CLIENT_UI_REPLAY_MAX 16
#define CLIENT_UI_REPLAY_EVENTS_MAX 128

typedef enum client_ui_screen {
    CLIENT_UI_LOADING = 0,
    CLIENT_UI_MAIN_MENU,
    CLIENT_UI_WORLD_LOAD,
    CLIENT_UI_WORLD_CREATE,
    CLIENT_UI_WORLD_VIEW,
    CLIENT_UI_REPLAY,
    CLIENT_UI_TOOLS,
    CLIENT_UI_SETTINGS
} client_ui_screen;

typedef enum client_ui_action {
    CLIENT_ACTION_NONE = 0,
    CLIENT_ACTION_NEW_WORLD,
    CLIENT_ACTION_LOAD_WORLD,
    CLIENT_ACTION_INSPECT_REPLAY,
    CLIENT_ACTION_TOOLS,
    CLIENT_ACTION_SETTINGS,
    CLIENT_ACTION_EXIT,
    CLIENT_ACTION_BACK,
    CLIENT_ACTION_CREATE_WORLD,
    CLIENT_ACTION_SAVE_WORLD,
    CLIENT_ACTION_SCENARIO_LOAD,
    CLIENT_ACTION_VARIANT_APPLY,
    CLIENT_ACTION_REPLAY_SAVE,
    CLIENT_ACTION_RENDERER_NEXT,
    CLIENT_ACTION_SCALE_UP,
    CLIENT_ACTION_SCALE_DOWN,
    CLIENT_ACTION_PALETTE_TOGGLE,
    CLIENT_ACTION_LOG_NEXT,
    CLIENT_ACTION_DEBUG_TOGGLE,
    CLIENT_ACTION_MODE_FREE,
    CLIENT_ACTION_MODE_ORBIT,
    CLIENT_ACTION_MODE_SURFACE,
    CLIENT_ACTION_MOVE_FORWARD,
    CLIENT_ACTION_MOVE_BACK,
    CLIENT_ACTION_MOVE_LEFT,
    CLIENT_ACTION_MOVE_RIGHT,
    CLIENT_ACTION_MOVE_UP,
    CLIENT_ACTION_MOVE_DOWN,
    CLIENT_ACTION_CAMERA_NEXT,
    CLIENT_ACTION_INSPECT_TOGGLE,
    CLIENT_ACTION_HUD_TOGGLE,
    CLIENT_ACTION_SPAWN,
    CLIENT_ACTION_INTERACTION_SELECT_MARKER,
    CLIENT_ACTION_INTERACTION_SELECT_BEACON,
    CLIENT_ACTION_INTERACTION_SELECT_INDICATOR,
    CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_BUTTON,
    CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LEVER,
    CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_WIRE,
    CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LAMP,
    CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_COUNTER,
    CLIENT_ACTION_INTERACTION_PLACE_PREVIEW,
    CLIENT_ACTION_INTERACTION_PLACE_CONFIRM,
    CLIENT_ACTION_INTERACTION_PLACE,
    CLIENT_ACTION_INTERACTION_REMOVE,
    CLIENT_ACTION_INTERACTION_SIGNAL,
    CLIENT_ACTION_INTERACTION_MEASURE,
    CLIENT_ACTION_INTERACTION_INSPECT,
    CLIENT_ACTION_SIGNAL_LIST,
    CLIENT_ACTION_SIGNAL_PREVIEW,
    CLIENT_ACTION_SIGNAL_CONNECT,
    CLIENT_ACTION_SIGNAL_THRESHOLD,
    CLIENT_ACTION_SIGNAL_SET,
    CLIENT_ACTION_PROFILE_NEXT,
    CLIENT_ACTION_PROFILE_PREV,
    CLIENT_ACTION_PRESET_NEXT,
    CLIENT_ACTION_PRESET_PREV,
    CLIENT_ACTION_ACCESSIBILITY_NEXT,
    CLIENT_ACTION_KEYBIND_NEXT,
    CLIENT_ACTION_REPLAY_STEP,
    CLIENT_ACTION_REPLAY_REWIND,
    CLIENT_ACTION_REPLAY_TOGGLE_PAUSE
} client_ui_action;

typedef struct client_renderer_entry {
    char name[16];
    int supported;
} client_renderer_entry;

typedef struct client_renderer_list {
    client_renderer_entry entries[CLIENT_UI_RENDERER_MAX];
    uint32_t count;
} client_renderer_list;

typedef struct client_ui_world_entry {
    char path[CLIENT_UI_PATH_MAX];
    char name[CLIENT_UI_LABEL_MAX];
    char created_at[32];
    char required_caps[CLIENT_UI_LABEL_MAX];
    char compat_summary[CLIENT_UI_LABEL_MAX];
    char status[32];
} client_ui_world_entry;

typedef struct client_ui_replay_entry {
    char path[CLIENT_UI_PATH_MAX];
    char source[CLIENT_UI_LABEL_MAX];
    char duration[32];
    char determinism[32];
    int event_count;
    char status[32];
} client_ui_replay_entry;

typedef struct client_ui_profile {
    const char* id;
    const char* label;
    const char* description;
    const char* ui_density;
    const char* verbosity;
    int debug_ui;
} client_ui_profile;

typedef struct client_ui_policy_preset {
    const char* id;
    const char* label;
    const char* description;
    const char* authority_csv;
    const char* mode_csv;
    const char* debug_csv;
    const char* playtest_csv;
} client_ui_policy_preset;

typedef struct client_ui_accessibility_preset {
    const char* id;
    const char* description;
    int ui_scale_percent;
    int palette;
    int reduced_motion;
    int screen_reader;
    int keyboard_only;
    int low_cognitive_load;
} client_ui_accessibility_preset;

typedef struct client_ui_state {
    client_ui_screen screen;
    int exit_requested;
    int loading_ticks;
    int menu_index;
    char action_status[CLIENT_UI_STATUS_MAX];
    char pack_status[CLIENT_UI_STATUS_MAX];
    char template_status[CLIENT_UI_STATUS_MAX];
    char compat_status[CLIENT_UI_STATUS_MAX];
    char determinism_status[32];
    uint32_t package_count;
    uint32_t instance_count;
    char testx_status[32];
    char seed_status[32];
    char install_root[CLIENT_UI_PATH_MAX];
    char instance_root[CLIENT_UI_PATH_MAX];
    char data_root[CLIENT_UI_PATH_MAX];
    char pack_names[CLIENT_UI_PACK_MAX][CLIENT_UI_PACK_NAME_MAX];
    uint32_t pack_name_count;
    client_ui_world_entry worlds[CLIENT_UI_WORLD_MAX];
    int world_count;
    int world_index;
    client_ui_replay_entry replays[CLIENT_UI_REPLAY_MAX];
    int replay_count;
    int replay_index;
    int replay_loaded;
    int replay_paused;
    int replay_cursor;
    int replay_event_count;
    char replay_events[CLIENT_UI_REPLAY_EVENTS_MAX][CLIENT_UI_LABEL_MAX];
    int create_profile_index;
    int create_preset_index;
    client_ui_settings settings;
    client_renderer_list renderers;
    char event_lines[CLIENT_UI_EVENT_LINES][CLIENT_UI_LABEL_MAX];
    int event_head;
    int event_count;
    int console_active;
    char console_input[CLIENT_UI_CONSOLE_MAX];
    size_t console_len;
    dom_client_shell shell;
    uint32_t tick;
} client_ui_state;

typedef struct client_ui_menu_item {
    const char* id;
    const char* fallback;
} client_ui_menu_item;

static const client_ui_menu_item g_client_menu_items[CLIENT_UI_MENU_COUNT] = {
    { "ui.client.menu.new_world", "New World" },
    { "ui.client.menu.load_world", "Load World" },
    { "ui.client.menu.replay", "Replay" },
    { "ui.client.menu.tools", "Tools" },
    { "ui.client.menu.settings", "Settings" },
    { "ui.client.menu.exit", "Exit" }
};

static const client_ui_profile g_client_profiles[] = {
    { "casual", "Casual", "Gentle prompts, standard UI density.", "standard", "normal", 0 },
    { "hardcore", "Hardcore", "Minimal prompts, compact UI density.", "compact", "minimal", 0 },
    { "creator", "Creator", "Verbose hints, debug overlays available.", "expanded", "verbose", 1 }
};

static const client_ui_policy_preset g_client_policy_presets[] = {
    { "baseline", "Baseline", "Default authority + free navigation.",
      DOM_SHELL_AUTH_POLICY, DOM_SHELL_MODE_FREE, "", DOM_SHELL_PLAYTEST_SANDBOX },
    { "strict", "Strict", "Tighter navigation + hardened playtest.",
      DOM_SHELL_AUTH_POLICY, DOM_SHELL_MODE_ORBIT, "", DOM_SHELL_PLAYTEST_HARDCORE },
    { "creator", "Creator", "Free nav + debug + accelerated time.",
      DOM_SHELL_AUTH_POLICY, DOM_SHELL_MODE_FREE, "policy.debug.readonly", DOM_SHELL_PLAYTEST_ACCELERATED }
};

static const client_ui_accessibility_preset g_client_accessibility_presets[] = {
    { "default", "Defaults, no extra constraints.", 100, 0, 0, 0, 0, 0 },
    { "high-contrast", "High contrast palette + larger text.", 125, 1, 0, 0, 0, 0 },
    { "screen-reader", "Screen reader mode with reduced motion.", 125, 1, 1, 1, 1, 0 },
    { "low-motion", "Reduced motion and simplified UI.", 110, 0, 1, 0, 0, 1 }
};

static const char* g_client_keybind_profiles[] = {
    "default",
    "compact",
    "vim"
};

#define CLIENT_UI_PROFILE_COUNT ((int)(sizeof(g_client_profiles) / sizeof(g_client_profiles[0])))
#define CLIENT_UI_POLICY_PRESET_COUNT ((int)(sizeof(g_client_policy_presets) / sizeof(g_client_policy_presets[0])))
#define CLIENT_UI_ACCESSIBILITY_PRESET_COUNT \
    ((int)(sizeof(g_client_accessibility_presets) / sizeof(g_client_accessibility_presets[0])))
#define CLIENT_UI_KEYBIND_PROFILE_COUNT \
    ((int)(sizeof(g_client_keybind_profiles) / sizeof(g_client_keybind_profiles[0])))

static const char* client_ui_text(const client_ui_state* state,
                                  const char* id,
                                  const char* fallback)
{
    const dom_app_ui_locale_table* locale = state ? state->settings.locale : NULL;
    return dom_app_ui_locale_text(locale, id, fallback);
}

static const char* client_ui_menu_text(const client_ui_state* state, int index)
{
    if (!state || index < 0 || index >= CLIENT_UI_MENU_COUNT) {
        return "";
    }
    return client_ui_text(state,
                          g_client_menu_items[index].id,
                          g_client_menu_items[index].fallback);
}

static const client_ui_profile* client_ui_profile_at(int index)
{
    if (index < 0 || index >= CLIENT_UI_PROFILE_COUNT) {
        return 0;
    }
    return &g_client_profiles[index];
}

static const client_ui_policy_preset* client_ui_preset_at(int index)
{
    if (index < 0 || index >= CLIENT_UI_POLICY_PRESET_COUNT) {
        return 0;
    }
    return &g_client_policy_presets[index];
}

static void client_ui_apply_profile_settings(client_ui_settings* settings,
                                             const client_ui_profile* profile)
{
    if (!settings || !profile) {
        return;
    }
    if (profile->ui_density && profile->ui_density[0]) {
        strncpy(settings->ui_density, profile->ui_density, sizeof(settings->ui_density) - 1u);
        settings->ui_density[sizeof(settings->ui_density) - 1u] = '\0';
    }
    if (profile->verbosity && profile->verbosity[0]) {
        strncpy(settings->verbosity, profile->verbosity, sizeof(settings->verbosity) - 1u);
        settings->verbosity[sizeof(settings->verbosity) - 1u] = '\0';
    }
    settings->debug_ui = profile->debug_ui ? 1 : 0;
}

static void client_ui_apply_accessibility_settings(client_ui_settings* settings,
                                                   const client_ui_accessibility_preset* preset)
{
    if (!settings || !preset) {
        return;
    }
    if (preset->id && preset->id[0]) {
        strncpy(settings->accessibility_preset_id,
                preset->id,
                sizeof(settings->accessibility_preset_id) - 1u);
        settings->accessibility_preset_id[sizeof(settings->accessibility_preset_id) - 1u] = '\0';
    }
    settings->ui_scale_percent = preset->ui_scale_percent;
    settings->palette = preset->palette;
    settings->reduced_motion = preset->reduced_motion ? 1 : 0;
    settings->screen_reader = preset->screen_reader ? 1 : 0;
    settings->keyboard_only = preset->keyboard_only ? 1 : 0;
    settings->low_cognitive_load = preset->low_cognitive_load ? 1 : 0;
}

static void client_ui_apply_profile(client_ui_state* state, int index)
{
    const client_ui_profile* profile = client_ui_profile_at(index);
    if (!state || !profile) {
        return;
    }
    state->create_profile_index = index;
    client_ui_apply_profile_settings(&state->settings, profile);
}

static void client_ui_apply_preset(client_ui_state* state, int index)
{
    const client_ui_policy_preset* preset = client_ui_preset_at(index);
    if (!state || !preset) {
        return;
    }
    state->create_preset_index = index;
    (void)dom_client_shell_set_create_policy(&state->shell, "authority", preset->authority_csv);
    (void)dom_client_shell_set_create_policy(&state->shell, "mode", preset->mode_csv);
    (void)dom_client_shell_set_create_policy(&state->shell, "debug", preset->debug_csv);
    (void)dom_client_shell_set_create_policy(&state->shell, "playtest", preset->playtest_csv);
}

static const client_ui_accessibility_preset* client_ui_accessibility_preset_at(int index)
{
    if (index < 0 || index >= CLIENT_UI_ACCESSIBILITY_PRESET_COUNT) {
        return 0;
    }
    return &g_client_accessibility_presets[index];
}

static void client_ui_apply_accessibility_preset(client_ui_state* state, int index)
{
    const client_ui_accessibility_preset* preset = client_ui_accessibility_preset_at(index);
    if (!state || !preset) {
        return;
    }
    client_ui_apply_accessibility_settings(&state->settings, preset);
}

static void client_ui_cycle_keybind_profile(client_ui_state* state)
{
    int i;
    const char* current;
    if (!state) {
        return;
    }
    current = state->settings.keybind_profile_id;
    for (i = 0; i < CLIENT_UI_KEYBIND_PROFILE_COUNT; ++i) {
        if (strcmp(current, g_client_keybind_profiles[i]) == 0) {
            int next = (i + 1) % CLIENT_UI_KEYBIND_PROFILE_COUNT;
            client_ui_copy_string(state->settings.keybind_profile_id,
                                  sizeof(state->settings.keybind_profile_id),
                                  g_client_keybind_profiles[next]);
            return;
        }
    }
    client_ui_copy_string(state->settings.keybind_profile_id,
                          sizeof(state->settings.keybind_profile_id),
                          g_client_keybind_profiles[0]);
}

static void client_ui_format_pack_list(const client_ui_state* state, char* out, size_t cap)
{
    uint32_t i;
    size_t len;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!state || state->pack_name_count == 0u) {
        client_ui_copy_string(out, cap, "packs=none");
        return;
    }
    client_ui_copy_string(out, cap, "packs=");
    len = strlen(out);
    for (i = 0u; i < state->pack_name_count; ++i) {
        const char* name = state->pack_names[i];
        size_t name_len = strlen(name);
        if (len + name_len + 2u >= cap) {
            if (len + 4u < cap) {
                strncat(out, "...", cap - len - 1u);
            }
            break;
        }
        strncat(out, name, cap - len - 1u);
        len += name_len;
        if (i + 1u < state->pack_name_count) {
            strncat(out, ",", cap - len - 1u);
            len += 1u;
        }
    }
}

static int client_ui_menu_item_enabled(const client_ui_state* state, int index, const char** out_reason)
{
    const char* reason = 0;
    int enabled = 1;
    if (!state) {
        if (out_reason) {
            *out_reason = "state missing";
        }
        return 0;
    }
    if (index == 0) {
        if (state->shell.registry.count == 0u) {
            enabled = 0;
            reason = "no templates";
        }
    } else if (index == 1) {
        if (state->world_count <= 0) {
            enabled = 0;
            reason = "no saves found";
        }
    } else if (index == 2) {
        if (state->replay_count <= 0) {
            enabled = 0;
            reason = "no replays found";
        }
    }
    if (out_reason) {
        *out_reason = reason;
    }
    return enabled;
}

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

static int client_renderer_supported(const client_renderer_list* list, const char* name)
{
    uint32_t i;
    if (!list || !name || !name[0]) {
        return 0;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->entries[i].supported && strcmp(list->entries[i].name, name) == 0) {
            return 1;
        }
    }
    return 0;
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

static void client_ui_copy_string(char* out, size_t cap, const char* value)
{
    if (!out || cap == 0u) {
        return;
    }
    if (!value) {
        out[0] = '\0';
        return;
    }
    strncpy(out, value, cap - 1u);
    out[cap - 1u] = '\0';
}

static void client_ui_join_path(char* out, size_t cap, const char* base, const char* leaf)
{
    size_t len;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!base || !base[0]) {
        client_ui_copy_string(out, cap, leaf ? leaf : "");
        return;
    }
    client_ui_copy_string(out, cap, base);
    len = strlen(out);
    if (len + 1u >= cap) {
        return;
    }
    if (len > 0u && out[len - 1u] != '/' && out[len - 1u] != '\\') {
        out[len++] = '/';
        out[len] = '\0';
    }
    if (leaf && leaf[0] && len + strlen(leaf) < cap) {
        strncat(out, leaf, cap - len - 1u);
    }
}

static int client_ui_path_has_suffix(const char* text, const char* suffix)
{
    size_t text_len;
    size_t suffix_len;
    if (!text || !suffix) {
        return 0;
    }
    text_len = strlen(text);
    suffix_len = strlen(suffix);
    if (suffix_len > text_len) {
        return 0;
    }
    return strcmp(text + (text_len - suffix_len), suffix) == 0;
}

static void client_ui_extract_stem(const char* path, char* out, size_t cap)
{
    const char* name = path;
    const char* dot = 0;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!path) {
        return;
    }
    {
        const char* p = path;
        while (*p) {
            if (*p == '/' || *p == '\\') {
                name = p + 1;
            }
            p += 1;
        }
    }
    dot = strrchr(name, '.');
    if (!dot) {
        client_ui_copy_string(out, cap, name);
        return;
    }
    {
        size_t len = (size_t)(dot - name);
        if (len >= cap) {
            len = cap - 1u;
        }
        memcpy(out, name, len);
        out[len] = '\0';
    }
}

static void client_ui_sort_paths(char items[][CLIENT_UI_PATH_MAX], uint32_t count)
{
    uint32_t i;
    uint32_t j;
    for (i = 0u; i + 1u < count; ++i) {
        for (j = i + 1u; j < count; ++j) {
            if (strcmp(items[i], items[j]) > 0) {
                char tmp[CLIENT_UI_PATH_MAX];
                memcpy(tmp, items[i], sizeof(tmp));
                memcpy(items[i], items[j], sizeof(tmp));
                memcpy(items[j], tmp, sizeof(tmp));
            }
        }
    }
}

static uint32_t client_ui_list_files(const char* root,
                                     const char* suffix,
                                     char items[][CLIENT_UI_PATH_MAX],
                                     uint32_t cap)
{
    uint32_t count = 0u;
    if (!root || !root[0] || !items || cap == 0u) {
        return 0u;
    }
#if defined(_WIN32)
    {
        struct _finddata_t data;
        intptr_t handle;
        char pattern[CLIENT_UI_PATH_MAX];
        snprintf(pattern, sizeof(pattern), "%s\\*", root);
        handle = _findfirst(pattern, &data);
        if (handle == -1) {
            return 0u;
        }
        do {
            if ((data.attrib & _A_SUBDIR) != 0) {
                continue;
            }
            if (suffix && suffix[0] && !client_ui_path_has_suffix(data.name, suffix)) {
                continue;
            }
            if (count < cap) {
                client_ui_copy_string(items[count], CLIENT_UI_PATH_MAX, data.name);
            }
            count += 1u;
        } while (_findnext(handle, &data) == 0);
        _findclose(handle);
    }
#else
    {
        DIR* dir = opendir(root);
        struct dirent* entry;
        if (!dir) {
            return 0u;
        }
        while ((entry = readdir(dir)) != 0) {
            char path[CLIENT_UI_PATH_MAX];
            FILE* f;
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }
            if (suffix && suffix[0] && !client_ui_path_has_suffix(entry->d_name, suffix)) {
                continue;
            }
            snprintf(path, sizeof(path), "%s/%s", root, entry->d_name);
            f = fopen(path, "rb");
            if (!f) {
                continue;
            }
            fclose(f);
            if (count < cap) {
                client_ui_copy_string(items[count], CLIENT_UI_PATH_MAX, entry->d_name);
            }
            count += 1u;
        }
        closedir(dir);
    }
#endif
    if (count > cap) {
        count = cap;
    }
    client_ui_sort_paths(items, count);
    return count;
}

static int client_ui_ensure_dir(const char* path)
{
    if (!path || !path[0]) {
        return 0;
    }
#if defined(_WIN32)
    if (_mkdir(path) == 0) {
        return 1;
    }
    if (errno == EEXIST) {
        return 1;
    }
#else
    if (mkdir(path, 0755) == 0) {
        return 1;
    }
    if (errno == EEXIST) {
        return 1;
    }
#endif
    return 0;
}

static int client_ui_file_exists(const char* path)
{
    FILE* f;
    if (!path || !path[0]) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f) {
        fclose(f);
        return 1;
    }
    return 0;
}

static void client_ui_build_world_save_path_for_seed(const char* data_root,
                                                     unsigned long long seed,
                                                     char* out,
                                                     size_t cap)
{
    char root[CLIENT_UI_PATH_MAX];
    char saves_root[CLIENT_UI_PATH_MAX];
    int attempt = 0;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    client_ui_copy_string(root, sizeof(root), (data_root && data_root[0]) ? data_root : "data");
    client_ui_join_path(saves_root, sizeof(saves_root), root, "saves");
    (void)client_ui_ensure_dir(root);
    (void)client_ui_ensure_dir(saves_root);
    while (attempt < 100) {
        if (attempt == 0) {
            snprintf(out, cap, "%s/world_%llu.save", saves_root, seed);
        } else {
            snprintf(out, cap, "%s/world_%llu_%d.save", saves_root, seed, attempt);
        }
        if (!client_ui_file_exists(out)) {
            return;
        }
        attempt += 1;
    }
    snprintf(out, cap, "%s/world_%llu.save", saves_root, seed);
}

static void client_ui_build_world_save_path(const client_ui_state* state,
                                            char* out,
                                            size_t cap)
{
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!state) {
        return;
    }
    client_ui_build_world_save_path_for_seed(state->data_root[0] ? state->data_root : "data",
                                             (unsigned long long)state->shell.create_seed,
                                             out,
                                             cap);
}

static uint32_t client_count_pack_manifests(const char* root,
                                            char names[][CLIENT_UI_PACK_NAME_MAX],
                                            uint32_t name_cap,
                                            uint32_t* out_names)
{
    uint32_t count = 0u;
    uint32_t name_count = 0u;
    if (!root || !root[0]) {
        return 0u;
    }
#if defined(_WIN32)
    {
        struct _finddata_t data;
        intptr_t handle;
        char pattern[260];
        snprintf(pattern, sizeof(pattern), "%s\\*", root);
        handle = _findfirst(pattern, &data);
        if (handle == -1) {
            return 0u;
        }
        do {
            if ((data.attrib & _A_SUBDIR) != 0) {
                char manifest[260];
                FILE* f = 0;
                if (strcmp(data.name, ".") == 0 || strcmp(data.name, "..") == 0) {
                    continue;
                }
                snprintf(manifest, sizeof(manifest), "%s\\%s\\pack_manifest.json", root, data.name);
                f = fopen(manifest, "r");
                if (f) {
                    fclose(f);
                    count += 1u;
                    if (names && name_count < name_cap) {
                        client_ui_copy_string(names[name_count], CLIENT_UI_PACK_NAME_MAX, data.name);
                        name_count += 1u;
                    }
                }
            }
        } while (_findnext(handle, &data) == 0);
        _findclose(handle);
    }
#else
    {
        DIR* dir = opendir(root);
        struct dirent* entry;
        if (!dir) {
            return 0u;
        }
        while ((entry = readdir(dir)) != 0) {
            char manifest[260];
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }
            snprintf(manifest, sizeof(manifest), "%s/%s/pack_manifest.json", root, entry->d_name);
            {
                FILE* f = fopen(manifest, "r");
                if (f) {
                    fclose(f);
                    count += 1u;
                    if (names && name_count < name_cap) {
                        client_ui_copy_string(names[name_count], CLIENT_UI_PACK_NAME_MAX, entry->d_name);
                        name_count += 1u;
                    }
                }
            }
        }
        closedir(dir);
    }
#endif
    if (out_names) {
        *out_names = name_count;
    }
    if (names && name_count > 1u) {
        uint32_t i;
        uint32_t j;
        for (i = 0u; i + 1u < name_count; ++i) {
            for (j = i + 1u; j < name_count; ++j) {
                if (strcmp(names[i], names[j]) > 0) {
                    char tmp[CLIENT_UI_PACK_NAME_MAX];
                    memcpy(tmp, names[i], sizeof(tmp));
                    memcpy(names[i], names[j], sizeof(tmp));
                    memcpy(names[j], tmp, sizeof(tmp));
                }
            }
        }
    }
    return count;
}

static void client_ui_default_data_root(char* out, size_t cap)
{
    const char* instance_root = client_env_or_default("DOM_INSTANCE_ROOT", "");
    const char* data_root = client_env_or_default("DOM_DATA_ROOT", "");
    if (!data_root || !data_root[0]) {
        data_root = (instance_root && instance_root[0]) ? instance_root : "data";
    }
    client_ui_copy_string(out, cap, data_root);
}

static void client_ui_collect_roots(client_ui_state* state)
{
    const char* install_root;
    const char* instance_root;
    char data_root[CLIENT_UI_PATH_MAX];
    if (!state) {
        return;
    }
    install_root = client_env_or_default("DOM_INSTALL_ROOT", "");
    instance_root = client_env_or_default("DOM_INSTANCE_ROOT", "");
    client_ui_default_data_root(data_root, sizeof(data_root));
    if (!instance_root || !instance_root[0]) {
        instance_root = data_root;
    }
    client_ui_copy_string(state->install_root, sizeof(state->install_root), install_root);
    client_ui_copy_string(state->instance_root, sizeof(state->instance_root), instance_root);
    client_ui_copy_string(state->data_root, sizeof(state->data_root), data_root);
}

static void client_ui_world_entry_init(client_ui_world_entry* entry)
{
    if (!entry) {
        return;
    }
    memset(entry, 0, sizeof(*entry));
    strncpy(entry->status, "ok", sizeof(entry->status) - 1u);
    entry->status[sizeof(entry->status) - 1u] = '\0';
    strncpy(entry->created_at, "unknown", sizeof(entry->created_at) - 1u);
    entry->created_at[sizeof(entry->created_at) - 1u] = '\0';
}

static void client_ui_replay_entry_init(client_ui_replay_entry* entry)
{
    if (!entry) {
        return;
    }
    memset(entry, 0, sizeof(*entry));
    strncpy(entry->status, "ok", sizeof(entry->status) - 1u);
    entry->status[sizeof(entry->status) - 1u] = '\0';
}

static int client_ui_world_meta_from_save(const char* path, client_ui_world_entry* entry)
{
    FILE* f;
    char line[DOM_SHELL_WORLDDEF_MAX];
    int have_header = 0;
    int in_summary = 0;
    char worlddef_id[DOM_SHELL_MAX_TEMPLATE_ID] = { 0 };
    char template_id[DOM_SHELL_MAX_TEMPLATE_ID] = { 0 };
    char movement[DOM_SHELL_POLICY_ID_MAX * 2] = { 0 };
    char authority[DOM_SHELL_POLICY_ID_MAX * 2] = { 0 };
    char mode[DOM_SHELL_POLICY_ID_MAX * 2] = { 0 };
    char debug[DOM_SHELL_POLICY_ID_MAX * 2] = { 0 };
    char playtest[DOM_SHELL_POLICY_ID_MAX * 2] = { 0 };
    char created_at[32] = { 0 };
    if (!path || !entry) {
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        strncpy(entry->status, "unreadable", sizeof(entry->status) - 1u);
        entry->status[sizeof(entry->status) - 1u] = '\0';
        return 0;
    }
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!have_header) {
            have_header = 1;
            if (strcmp(line, DOM_SHELL_SAVE_HEADER) != 0) {
                fclose(f);
                strncpy(entry->status, "invalid", sizeof(entry->status) - 1u);
                entry->status[sizeof(entry->status) - 1u] = '\0';
                return 0;
            }
            continue;
        }
        if (strcmp(line, "summary_begin") == 0) {
            in_summary = 1;
            continue;
        }
        if (strcmp(line, "summary_end") == 0) {
            in_summary = 0;
            continue;
        }
        if (!in_summary) {
            continue;
        }
        if (strncmp(line, "worlddef_id=", 12) == 0) {
            client_ui_copy_string(worlddef_id, sizeof(worlddef_id), line + 12);
        } else if (strncmp(line, "template_id=", 12) == 0) {
            client_ui_copy_string(template_id, sizeof(template_id), line + 12);
        } else if (strncmp(line, "policy.movement=", 16) == 0) {
            client_ui_copy_string(movement, sizeof(movement), line + 16);
        } else if (strncmp(line, "policy.authority=", 17) == 0) {
            client_ui_copy_string(authority, sizeof(authority), line + 17);
        } else if (strncmp(line, "policy.mode=", 12) == 0) {
            client_ui_copy_string(mode, sizeof(mode), line + 12);
        } else if (strncmp(line, "policy.debug=", 13) == 0) {
            client_ui_copy_string(debug, sizeof(debug), line + 13);
        } else if (strncmp(line, "policy.playtest=", 16) == 0) {
            client_ui_copy_string(playtest, sizeof(playtest), line + 16);
        } else if (strncmp(line, "created_at=", 11) == 0) {
            client_ui_copy_string(created_at, sizeof(created_at), line + 11);
        }
    }
    fclose(f);
    if (worlddef_id[0]) {
        client_ui_copy_string(entry->name, sizeof(entry->name), worlddef_id);
    } else if (template_id[0]) {
        client_ui_copy_string(entry->name, sizeof(entry->name), template_id);
    }
    if (!entry->name[0]) {
        client_ui_extract_stem(path, entry->name, sizeof(entry->name));
    }
    {
        char caps[CLIENT_UI_LABEL_MAX];
        snprintf(caps, sizeof(caps),
                 "authority=%s mode=%s playtest=%s debug=%s",
                 authority[0] ? authority : "none",
                 mode[0] ? mode : "none",
                 playtest[0] ? playtest : "none",
                 debug[0] ? debug : "none");
        client_ui_copy_string(entry->required_caps, sizeof(entry->required_caps), caps);
    }
    if (created_at[0]) {
        client_ui_copy_string(entry->created_at, sizeof(entry->created_at), created_at);
    }
    return 1;
}

static int client_ui_replay_meta_from_file(const char* path, client_ui_replay_entry* entry)
{
    FILE* f;
    char line[DOM_SHELL_EVENT_MAX];
    int header_checked = 0;
    int in_meta = 0;
    int in_events = 0;
    int saw_events = 0;
    char scenario_id[DOM_SHELL_SCENARIO_ID_MAX] = { 0 };
    char determinism[32] = { 0 };
    int event_count = 0;
    if (!path || !entry) {
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        strncpy(entry->status, "unreadable", sizeof(entry->status) - 1u);
        entry->status[sizeof(entry->status) - 1u] = '\0';
        return 0;
    }
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!header_checked) {
            header_checked = 1;
            if (strcmp(line, DOM_SHELL_REPLAY_HEADER) != 0 && strcmp(line, DOM_SHELL_SAVE_HEADER) != 0) {
                fclose(f);
                strncpy(entry->status, "invalid", sizeof(entry->status) - 1u);
                entry->status[sizeof(entry->status) - 1u] = '\0';
                return 0;
            }
            continue;
        }
        if (strcmp(line, "meta_begin") == 0) {
            in_meta = 1;
            continue;
        }
        if (strcmp(line, "meta_end") == 0) {
            in_meta = 0;
            continue;
        }
        if (strcmp(line, "events_begin") == 0) {
            in_events = 1;
            saw_events = 1;
            continue;
        }
        if (strcmp(line, "events_end") == 0) {
            in_events = 0;
            continue;
        }
        if (in_meta) {
            if (strncmp(line, "scenario_id=", 12) == 0) {
                client_ui_copy_string(scenario_id, sizeof(scenario_id), line + 12);
            } else if (strncmp(line, "determinism=", 12) == 0) {
                client_ui_copy_string(determinism, sizeof(determinism), line + 12);
            }
            continue;
        }
        if ((saw_events && in_events) || (!saw_events && line[0])) {
            event_count += 1;
        }
    }
    fclose(f);
    entry->event_count = event_count;
    if (scenario_id[0]) {
        client_ui_copy_string(entry->source, sizeof(entry->source), scenario_id);
    }
    if (!entry->source[0]) {
        client_ui_extract_stem(path, entry->source, sizeof(entry->source));
    }
    if (determinism[0]) {
        client_ui_copy_string(entry->determinism, sizeof(entry->determinism), determinism);
    } else {
        client_ui_copy_string(entry->determinism, sizeof(entry->determinism), "unknown");
    }
    {
        char duration[32];
        snprintf(duration, sizeof(duration), "events=%d", event_count);
        client_ui_copy_string(entry->duration, sizeof(entry->duration), duration);
    }
    return 1;
}

static void client_ui_refresh_worlds(client_ui_state* state)
{
    char root[CLIENT_UI_PATH_MAX];
    char saves_root[CLIENT_UI_PATH_MAX];
    char files[CLIENT_UI_WORLD_MAX][CLIENT_UI_PATH_MAX];
    uint32_t count;
    uint32_t i;
    if (!state) {
        return;
    }
    client_ui_copy_string(root, sizeof(root), state->data_root[0] ? state->data_root : "data");
    client_ui_join_path(saves_root, sizeof(saves_root), root, "saves");
    count = client_ui_list_files(saves_root, ".save", files, CLIENT_UI_WORLD_MAX);
    state->world_count = (int)count;
    for (i = 0u; i < CLIENT_UI_WORLD_MAX; ++i) {
        client_ui_world_entry_init(&state->worlds[i]);
    }
    for (i = 0u; i < count && i < CLIENT_UI_WORLD_MAX; ++i) {
        char path[CLIENT_UI_PATH_MAX];
        client_ui_join_path(path, sizeof(path), saves_root, files[i]);
        client_ui_copy_string(state->worlds[i].path, sizeof(state->worlds[i].path), path);
        (void)client_ui_world_meta_from_save(path, &state->worlds[i]);
        client_ui_copy_string(state->worlds[i].compat_summary,
                              sizeof(state->worlds[i].compat_summary),
                              state->compat_status);
    }
    if (state->world_index < 0 || state->world_index >= state->world_count) {
        state->world_index = 0;
    }
}

static void client_ui_refresh_replays(client_ui_state* state)
{
    char root[CLIENT_UI_PATH_MAX];
    char replays_root[CLIENT_UI_PATH_MAX];
    char files[CLIENT_UI_REPLAY_MAX][CLIENT_UI_PATH_MAX];
    uint32_t count;
    uint32_t i;
    if (!state) {
        return;
    }
    client_ui_copy_string(root, sizeof(root), state->data_root[0] ? state->data_root : "data");
    client_ui_join_path(replays_root, sizeof(replays_root), root, "replays");
    count = client_ui_list_files(replays_root, ".replay", files, CLIENT_UI_REPLAY_MAX);
    state->replay_count = (int)count;
    for (i = 0u; i < CLIENT_UI_REPLAY_MAX; ++i) {
        client_ui_replay_entry_init(&state->replays[i]);
    }
    for (i = 0u; i < count && i < CLIENT_UI_REPLAY_MAX; ++i) {
        char path[CLIENT_UI_PATH_MAX];
        client_ui_join_path(path, sizeof(path), replays_root, files[i]);
        client_ui_copy_string(state->replays[i].path, sizeof(state->replays[i].path), path);
        (void)client_ui_replay_meta_from_file(path, &state->replays[i]);
    }
    if (state->replay_index < 0 || state->replay_index >= state->replay_count) {
        state->replay_index = 0;
    }
}

static void client_ui_collect_loading(client_ui_state* state,
                                      const dom_app_compat_expect* compat)
{
    dom_app_readonly_adapter ro;
    dom_app_compat_report report;
    dom_app_ro_core_info core;
    uint32_t pack_count = 0u;
    if (!state) {
        return;
    }
    client_ui_collect_roots(state);
    state->package_count = 0u;
    state->instance_count = 0u;
    state->pack_name_count = 0u;
    pack_count = client_count_pack_manifests("data/packs",
                                             state->pack_names,
                                             CLIENT_UI_PACK_MAX,
                                             &state->pack_name_count);
    snprintf(state->pack_status, sizeof(state->pack_status),
             "pack_discovery=ok packs=%u", (unsigned int)pack_count);
    dom_app_ro_init(&ro);
    dom_app_compat_report_init(&report, "client");
    if (dom_app_ro_open(&ro, compat, &report)) {
        if (dom_app_ro_get_core_info(&ro, &core) == DOM_APP_RO_OK) {
            state->package_count = core.package_count;
            state->instance_count = core.instance_count;
            snprintf(state->pack_status, sizeof(state->pack_status),
                     "pack_discovery=ok packs=%u packages=%u instances=%u",
                     (unsigned int)pack_count,
                     (unsigned int)core.package_count,
                     (unsigned int)core.instance_count);
        } else {
            snprintf(state->pack_status, sizeof(state->pack_status),
                     "pack_discovery=ok packs=%u core=unavailable",
                     (unsigned int)pack_count);
        }
        dom_app_ro_close(&ro);
    } else {
        snprintf(state->pack_status, sizeof(state->pack_status),
                 "pack_discovery=ok packs=%u core=unavailable %s",
                 (unsigned int)pack_count,
                 report.message[0] ? report.message : "compatibility failure");
    }
    snprintf(state->compat_status, sizeof(state->compat_status),
             "compat_status=%s %s",
             report.ok ? "ok" : "failed",
             report.message[0] ? report.message : "unknown");
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
    client_ui_refresh_worlds(state);
    client_ui_refresh_replays(state);
}

static void client_ui_state_init(client_ui_state* state,
                                 const client_ui_settings* settings,
                                 const dom_app_compat_expect* compat,
                                 d_app_timing_mode timing_mode)
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
    state->compat_status[0] = '\0';
    state->console_input[0] = '\0';
    state->console_len = 0u;
    state->console_active = 0;
    state->install_root[0] = '\0';
    state->instance_root[0] = '\0';
    state->data_root[0] = '\0';
    state->pack_name_count = 0u;
    state->world_count = 0;
    state->world_index = 0;
    state->replay_count = 0;
    state->replay_index = 0;
    state->replay_loaded = 0;
    state->replay_paused = 1;
    state->replay_cursor = 0;
    state->replay_event_count = 0;
    state->create_profile_index = 0;
    state->create_preset_index = 0;
    memset(state->pack_names, 0, sizeof(state->pack_names));
    memset(state->replay_events, 0, sizeof(state->replay_events));
    {
        uint32_t i;
        for (i = 0u; i < CLIENT_UI_WORLD_MAX; ++i) {
            client_ui_world_entry_init(&state->worlds[i]);
        }
        for (i = 0u; i < CLIENT_UI_REPLAY_MAX; ++i) {
            client_ui_replay_entry_init(&state->replays[i]);
        }
    }
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
    state->event_head = 0;
    state->event_count = 0;
    state->tick = 0u;
    dom_client_shell_init(&state->shell);
    client_ui_apply_profile(state, state->create_profile_index);
    client_ui_apply_preset(state, state->create_preset_index);
    snprintf(state->template_status, sizeof(state->template_status),
             "template_registry=built_in=%u pack_templates=0 total=%u",
             (unsigned int)state->shell.registry.count,
             (unsigned int)state->shell.registry.count);
    snprintf(state->determinism_status, sizeof(state->determinism_status),
             "determinism=%s",
             (timing_mode == D_APP_TIMING_INTERACTIVE) ? "interactive" : "deterministic");
    client_ui_collect_loading(state, compat);
}

static void client_ui_sync_events(client_ui_state* state)
{
    if (!state) {
        return;
    }
    dom_client_shell_event_lines(dom_client_shell_events(&state->shell),
                                 (char*)state->event_lines,
                                 CLIENT_UI_EVENT_LINES,
                                 CLIENT_UI_LABEL_MAX,
                                 &state->event_count);
    state->event_head = 0;
}

static void client_ui_replay_reset(client_ui_state* state)
{
    if (!state) {
        return;
    }
    state->replay_loaded = 0;
    state->replay_paused = 1;
    state->replay_cursor = 0;
    state->replay_event_count = 0;
    memset(state->replay_events, 0, sizeof(state->replay_events));
}

static int client_ui_replay_load_events(client_ui_state* state,
                                        const char* path,
                                        char* status,
                                        size_t status_cap)
{
    FILE* f;
    char line[DOM_SHELL_EVENT_MAX];
    int header_checked = 0;
    int in_events = 0;
    int saw_events = 0;
    int count = 0;
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!state || !path || !path[0]) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "replay_load=refused reason=missing_path");
        }
        return 0;
    }
    f = fopen(path, "r");
    if (!f) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "replay_load=refused reason=open_failed");
        }
        return 0;
    }
    client_ui_replay_reset(state);
    while (fgets(line, sizeof(line), f)) {
        size_t len = strlen(line);
        while (len > 0u && (line[len - 1u] == '\n' || line[len - 1u] == '\r')) {
            line[--len] = '\0';
        }
        if (!header_checked) {
            header_checked = 1;
            if (strcmp(line, DOM_SHELL_REPLAY_HEADER) != 0 &&
                strcmp(line, DOM_SHELL_SAVE_HEADER) != 0) {
                fclose(f);
                if (status && status_cap > 0u) {
                    snprintf(status, status_cap, "replay_load=refused reason=invalid_header");
                }
                return 0;
            }
            continue;
        }
        if (strcmp(line, "events_begin") == 0) {
            in_events = 1;
            saw_events = 1;
            continue;
        }
        if (strcmp(line, "events_end") == 0) {
            in_events = 0;
            continue;
        }
        if ((saw_events && in_events) || (!saw_events && line[0])) {
            if (count < CLIENT_UI_REPLAY_EVENTS_MAX) {
                client_ui_copy_string(state->replay_events[count],
                                      sizeof(state->replay_events[count]),
                                      line);
            }
            count += 1;
        }
    }
    fclose(f);
    if (count == 0) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "replay_load=refused reason=empty");
        }
        return 0;
    }
    state->replay_event_count = (count > CLIENT_UI_REPLAY_EVENTS_MAX)
                                    ? CLIENT_UI_REPLAY_EVENTS_MAX
                                    : count;
    state->replay_loaded = 1;
    state->replay_paused = 1;
    state->replay_cursor = 0;
    if (status && status_cap > 0u) {
        if (count > CLIENT_UI_REPLAY_EVENTS_MAX) {
            snprintf(status, status_cap, "replay_load=ok truncated=%d",
                     (int)(count - CLIENT_UI_REPLAY_EVENTS_MAX));
        } else {
            snprintf(status, status_cap, "replay_load=ok events=%d", count);
        }
    }
    return 1;
}

static void client_ui_add_line(char lines[][CLIENT_UI_LABEL_MAX],
                               int* count,
                               int max_lines,
                               const char* fmt,
                               ...)
{
    va_list args;
    if (!lines || !count || !fmt) {
        return;
    }
    if (*count >= max_lines) {
        return;
    }
    va_start(args, fmt);
    vsnprintf(lines[*count], CLIENT_UI_LABEL_MAX, fmt, args);
    va_end(args);
    *count += 1;
}

static void client_ui_format_q16(char* out, size_t cap, i32 value)
{
    if (!out || cap == 0u) {
        return;
    }
    if (value == DOM_FIELD_VALUE_UNKNOWN) {
        snprintf(out, cap, "unknown");
        return;
    }
    snprintf(out, cap, "%.3f", (double)value / 65536.0);
}

static int client_ui_geo_from_position(const dom_shell_world_state* world,
                                       double* out_lat_deg,
                                       double* out_lon_deg,
                                       double* out_alt_m)
{
    const double pi = 3.14159265358979323846;
    double x;
    double y;
    double z;
    double r;
    if (!world || world->summary.earth_radius_m <= 0.0) {
        return 0;
    }
    x = world->position[0];
    y = world->position[1];
    z = world->position[2];
    r = sqrt(x * x + y * y + z * z);
    if (r <= 0.0) {
        return 0;
    }
    if (out_lat_deg) {
        *out_lat_deg = asin(z / r) * (180.0 / pi);
    }
    if (out_lon_deg) {
        *out_lon_deg = atan2(y, x) * (180.0 / pi);
    }
    if (out_alt_m) {
        *out_alt_m = r - world->summary.earth_radius_m;
    }
    return 1;
}

static const char* client_ui_goal_type_name(u32 type)
{
    switch (type) {
        case AGENT_GOAL_SURVEY: return "survey";
        case AGENT_GOAL_MAINTAIN: return "maintain";
        case AGENT_GOAL_STABILIZE: return "stabilize";
        case AGENT_GOAL_SURVIVE: return "survive";
        case AGENT_GOAL_ACQUIRE: return "acquire";
        case AGENT_GOAL_DEFEND: return "defend";
        case AGENT_GOAL_MIGRATE: return "migrate";
        case AGENT_GOAL_RESEARCH: return "research";
        case AGENT_GOAL_TRADE: return "trade";
        default: break;
    }
    return "unknown";
}

static const char* client_ui_network_type_name(u32 type)
{
    switch (type) {
        case DOM_NETWORK_ELECTRICAL: return "electrical";
        case DOM_NETWORK_THERMAL: return "thermal";
        case DOM_NETWORK_FLUID: return "fluid";
        case DOM_NETWORK_LOGISTICS: return "logistics";
        case DOM_NETWORK_DATA: return "data";
        default: break;
    }
    return "unknown";
}

static const char* client_ui_network_status_name(u32 status)
{
    return (status == DOM_NETWORK_FAILED) ? "failed" : "ok";
}

static int client_policy_has(const dom_shell_policy_set* set, const char* id)
{
    uint32_t i;
    if (!set || !id || !id[0]) {
        return 0;
    }
    for (i = 0u; i < set->count; ++i) {
        if (strcmp(set->items[i], id) == 0) {
            return 1;
        }
    }
    return 0;
}

static void client_policy_toggle(dom_shell_policy_set* set, const char* id)
{
    uint32_t i;
    if (!set || !id || !id[0]) {
        return;
    }
    for (i = 0u; i < set->count; ++i) {
        if (strcmp(set->items[i], id) == 0) {
            uint32_t j;
            for (j = i + 1u; j < set->count; ++j) {
                memcpy(set->items[j - 1u], set->items[j], DOM_SHELL_POLICY_ID_MAX);
            }
            set->count -= 1u;
            return;
        }
    }
    if (set->count < DOM_SHELL_MAX_POLICIES) {
        strncpy(set->items[set->count], id, DOM_SHELL_POLICY_ID_MAX - 1u);
        set->items[set->count][DOM_SHELL_POLICY_ID_MAX - 1u] = '\0';
        set->count += 1u;
    }
}

static void client_ui_build_lines(const client_ui_state* state,
                                  char lines[][CLIENT_UI_LABEL_MAX],
                                  int* out_count)
{
    int count = 0;
    char csv[256];
    char packs_line[CLIENT_UI_LABEL_MAX];
    if (out_count) {
        *out_count = 0;
    }
    if (!state || !lines) {
        return;
    }
    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                       client_ui_text(state, "ui.client.title", "Dominium Client"));
    if (state->screen == CLIENT_UI_LOADING) {
        const dom_build_info_v1* build = dom_build_info_v1_get();
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "engine=%s", DOMINO_VERSION_STRING);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "game=%s", DOMINIUM_GAME_VERSION);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "build_number=%u", (unsigned int)DOM_BUILD_NUMBER);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "install_root=%s",
                           state->install_root[0] ? state->install_root : "(unset)");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "instance_root=%s",
                           state->instance_root[0] ? state->instance_root : "(unset)");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "data_root=%s",
                           state->data_root[0] ? state->data_root : "data");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "sim_schema_id=unknown");
        if (build) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "sim_schema_version=%u",
                               (unsigned int)build->sim_schema_version);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "content_schema_version=%u",
                               (unsigned int)build->content_schema_version);
        } else {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "sim_schema_version=unknown");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "content_schema_version=unknown");
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "protocol_law_targets=LAW_TARGETS@1.4.0");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "protocol_control_caps=CONTROL_CAPS@1.0.0");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "worlddef_schema_version=%u",
                           (unsigned int)DOM_SHELL_WORLDDEF_SCHEMA_VERSION);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->determinism_status);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           state->compat_status[0] ? state->compat_status : "compat_status=unknown");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->pack_status);
        client_ui_format_pack_list(state, packs_line, sizeof(packs_line));
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", packs_line);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->template_status);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "testx=%s", state->testx_status);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "seed=%s", state->seed_status);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state,
                                          "ui.client.loading.ready",
                                          "Loading complete. Press Enter to continue."));
    } else if (state->screen == CLIENT_UI_MAIN_MENU) {
        int i;
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.menu.title", "Main Menu"));
        for (i = 0; i < CLIENT_UI_MENU_COUNT; ++i) {
            const char* reason = 0;
            const char* label = client_ui_menu_text(state, i);
            char entry[CLIENT_UI_LABEL_MAX];
            int enabled = client_ui_menu_item_enabled(state, i, &reason);
            if (!enabled && reason && reason[0]) {
                snprintf(entry, sizeof(entry), "%s (%s)", label, reason);
                label = entry;
            }
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s %s",
                               (i == state->menu_index) ? ">" : " ",
                               label);
        }
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_WORLD_LOAD) {
        int i;
        char saves_root[CLIENT_UI_PATH_MAX];
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.load_world.title", "Load World"));
        client_ui_join_path(saves_root, sizeof(saves_root),
                            state->data_root[0] ? state->data_root : "data",
                            "saves");
        if (state->world_count <= 0) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "worlds=none path=%s", saves_root);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "Create a world to generate a save.");
        } else {
            for (i = 0; i < state->world_count && count < CLIENT_UI_MAX_LINES; ++i) {
                const client_ui_world_entry* entry = &state->worlds[i];
                const char* name = entry->name[0] ? entry->name : "(unnamed)";
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "%s %s", (i == state->world_index) ? ">" : " ", name);
            }
            if (state->world_index >= 0 && state->world_index < state->world_count) {
                const client_ui_world_entry* selected = &state->worlds[state->world_index];
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "selected=%s",
                                   selected->name[0] ? selected->name : "(unnamed)");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "created_at=%s",
                                   selected->created_at[0] ? selected->created_at : "unknown");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "required_caps=%s",
                                   selected->required_caps[0] ? selected->required_caps : "none");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                                   selected->compat_summary[0] ? selected->compat_summary
                                                              : "compat_status=unknown");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "path=%s",
                                   selected->path[0] ? selected->path : "unknown");
                if (selected->status[0] && strcmp(selected->status, "ok") != 0) {
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "status=%s",
                                       selected->status);
                }
            }
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           "Keys: W/S select, Enter=load, R=refresh, B=back");
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_WORLD_CREATE) {
        const dom_shell_registry* reg = dom_client_shell_registry(&state->shell);
        const dom_shell_template* tmpl = 0;
        const client_ui_profile* profile = client_ui_profile_at(state->create_profile_index);
        const client_ui_policy_preset* preset = client_ui_preset_at(state->create_preset_index);
        if (reg && reg->count > 0u && state->shell.create_template_index < reg->count) {
            tmpl = &reg->templates[state->shell.create_template_index];
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.new_world.title", "New World"));
        if (tmpl) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "template=%s", tmpl->template_id);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "description=%s", tmpl->description);
        } else {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "template=none");
        }
        if (profile) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "profile=%s",
                               profile->label);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "profile_note=%s",
                               profile->description);
        }
        if (preset) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "meta_preset=%s",
                               preset->label);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "preset_note=%s",
                               preset->description);
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "seed=%llu (+/- to edit)",
                           (unsigned long long)state->shell.create_seed);
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.new_world.policies", "policies:"));
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           " [1] free=%s",
                           client_policy_has(&state->shell.create_mode, DOM_SHELL_MODE_FREE) ? "on" : "off");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           " [2] orbit=%s",
                           client_policy_has(&state->shell.create_mode, DOM_SHELL_MODE_ORBIT) ? "on" : "off");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           " [3] surface=%s",
                           client_policy_has(&state->shell.create_mode, DOM_SHELL_MODE_SURFACE) ? "on" : "off");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           " [A] authority=%s",
                           client_policy_has(&state->shell.create_authority, DOM_SHELL_AUTH_POLICY) ? "on" : "off");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           " [D] debug=%s",
                           state->shell.create_debug.count > 0u ? "on" : "off");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state,
                                          "ui.client.new_world.keys",
                                          "Enter=create  B=back  T=template  P=profile  M=meta-law"));
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_WORLD_VIEW) {
        const dom_shell_world_state* world = dom_client_shell_world(&state->shell);
        double lat = 0.0;
        double lon = 0.0;
        double alt = 0.0;
        int has_geo = 0;
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.world_view.title", "World View"));
        if (!world || !world->active) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "world=inactive");
        } else {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "worlddef_id=%s", world->summary.worlddef_id);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "template_id=%s", world->summary.template_id);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "entity=world id=%s",
                               world->summary.worlddef_id);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "provenance=template:%s source=%s",
                               world->summary.template_id[0] ? world->summary.template_id : "unknown",
                               world->summary.template_id[0] ? "built_in" : "unknown");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "node=%s frame=%s",
                               world->current_node_id, world->summary.spawn_frame_id);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "position=%.2f,%.2f,%.2f",
                               world->position[0], world->position[1], world->position[2]);
            has_geo = client_ui_geo_from_position(world, &lat, &lon, &alt);
            if (has_geo) {
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "geo_lat_lon_alt=%.3f,%.3f,%.3f", lat, lon, alt);
            }
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "orientation=%.2f,%.2f,%.2f",
                               world->orientation[0], world->orientation[1], world->orientation[2]);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "mode=%s",
                               world->active_mode[0] ? world->active_mode : "none");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "camera=%s",
                               world->camera_mode[0] ? world->camera_mode : "none");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "inspect=%s hud=%s",
                               world->inspect_enabled ? "on" : "off",
                               world->hud_enabled ? "on" : "off");
            dom_client_shell_policy_to_csv(&world->summary.authority, csv, sizeof(csv));
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "authority=%s", csv[0] ? csv : "none");
            dom_client_shell_policy_to_csv(&world->summary.movement, csv, sizeof(csv));
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "movement=%s", csv[0] ? csv : "none");
            dom_client_shell_policy_to_csv(&world->summary.mode, csv, sizeof(csv));
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "modes=%s", csv[0] ? csv : "none");
            dom_client_shell_policy_to_csv(&world->summary.debug, csv, sizeof(csv));
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "debug=%s", csv[0] ? csv : "none");
            dom_client_shell_policy_to_csv(&world->summary.camera, csv, sizeof(csv));
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "camera_modes=%s", csv[0] ? csv : "none");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "tick=%u", (unsigned int)state->tick);
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "intent=%s",
                               state->shell.last_intent[0] ? state->shell.last_intent : "none");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "plan=%s",
                               state->shell.last_plan[0] ? state->shell.last_plan : "none");
            if (state->shell.last_refusal_code[0] &&
                (strstr(state->shell.last_status, "refused") || strstr(state->shell.last_status, "failed"))) {
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "refusal=%s detail=%s",
                                   state->shell.last_refusal_code,
                                   state->shell.last_refusal_detail[0] ? state->shell.last_refusal_detail : "none");
            } else {
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "refusal=none");
            }
            {
                const dom_shell_field_state* fields = &state->shell.fields;
                char conf_buf[32];
                char unc_buf[32];
                u32 i;
                client_ui_format_q16(conf_buf, sizeof(conf_buf), (i32)fields->confidence_q16);
                client_ui_format_q16(unc_buf, sizeof(unc_buf), (i32)fields->uncertainty_q16);
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "fields=%u knowledge=0x%08x confidence=%s uncertainty=%s",
                                   (unsigned int)fields->field_count,
                                   (unsigned int)fields->knowledge_mask,
                                   conf_buf,
                                   unc_buf);
                for (i = 0u; i < fields->field_count && count < CLIENT_UI_MAX_LINES; ++i) {
                    u32 field_id = fields->field_ids[i];
                    i32 obj = DOM_FIELD_VALUE_UNKNOWN;
                    i32 subj = DOM_FIELD_VALUE_UNKNOWN;
                    char obj_buf[32];
                    char subj_buf[32];
                    const dom_physical_field_desc* desc = dom_physical_field_desc_get(field_id);
                    const char* name = desc && desc->name ? desc->name : "field";
                    (void)dom_field_get_value(&fields->objective, field_id, 0u, 0u, &obj);
                    (void)dom_field_get_value(&fields->subjective, field_id, 0u, 0u, &subj);
                    client_ui_format_q16(obj_buf, sizeof(obj_buf), obj);
                    client_ui_format_q16(subj_buf, sizeof(subj_buf), subj);
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                       "field %s objective=%s subjective=%s known=%u",
                                       name,
                                       obj_buf,
                                       subj_buf,
                                       (fields->knowledge_mask & DOM_FIELD_BIT(field_id)) ? 1u : 0u);
                }
            }
            if (state->shell.agent_count > 0u && count < CLIENT_UI_MAX_LINES) {
                u32 i;
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "agents=%u possessed=%llu",
                                   (unsigned int)state->shell.agent_count,
                                   (unsigned long long)state->shell.possessed_agent_id);
                for (i = 0u; i < state->shell.agent_count && count < CLIENT_UI_MAX_LINES; ++i) {
                    const dom_shell_agent_record* record = &state->shell.agents[i];
                    const dom_agent_belief* belief = &state->shell.beliefs[i];
                    const dom_agent_capability* cap = &state->shell.caps[i];
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                       "agent id=%llu goal=%s refusal=%s know=0x%08x caps=0x%08x auth=0x%08x",
                                       (unsigned long long)record->agent_id,
                                       client_ui_goal_type_name(record->last_goal_type),
                                       agent_refusal_to_string((agent_refusal_code)record->last_refusal),
                                       (unsigned int)belief->knowledge_mask,
                                       (unsigned int)cap->capability_mask,
                                       (unsigned int)cap->authority_mask);
                }
            }
            if (state->shell.delegation_registry.count > 0u && count < CLIENT_UI_MAX_LINES) {
                u32 i;
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "delegations=%u",
                                   (unsigned int)state->shell.delegation_registry.count);
                for (i = 0u; i < state->shell.delegation_registry.count && count < CLIENT_UI_MAX_LINES; ++i) {
                    const agent_delegation* del = &state->shell.delegations[i];
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                       "delegation id=%llu delegator=%llu delegatee=%llu revoked=%u",
                                       (unsigned long long)del->delegation_id,
                                       (unsigned long long)del->delegator_ref,
                                       (unsigned long long)del->delegatee_ref,
                                       (unsigned int)del->revoked);
                }
            }
            if (state->shell.network_count > 0u && count < CLIENT_UI_MAX_LINES) {
                u32 i;
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "networks=%u",
                                   (unsigned int)state->shell.network_count);
                for (i = 0u; i < state->shell.network_count && count < CLIENT_UI_MAX_LINES; ++i) {
                    const dom_shell_network_state* net = &state->shell.networks[i];
                    u32 n;
                    u32 e;
                    u32 failed_nodes = 0u;
                    u32 failed_edges = 0u;
                    for (n = 0u; n < net->graph.node_count; ++n) {
                        if (net->nodes[n].status == DOM_NETWORK_FAILED) {
                            failed_nodes += 1u;
                        }
                    }
                    for (e = 0u; e < net->graph.edge_count; ++e) {
                        if (net->edges[e].status == DOM_NETWORK_FAILED) {
                            failed_edges += 1u;
                        }
                    }
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                       "network id=%llu type=%s nodes=%u edges=%u failed_nodes=%u failed_edges=%u",
                                       (unsigned long long)net->network_id,
                                       client_ui_network_type_name(net->graph.type),
                                       (unsigned int)net->graph.node_count,
                                       (unsigned int)net->graph.edge_count,
                                       (unsigned int)failed_nodes,
                                       (unsigned int)failed_edges);
                    for (n = 0u; n < net->graph.node_count && n < 2u && count < CLIENT_UI_MAX_LINES; ++n) {
                        char stored_buf[32];
                        char cap_buf[32];
                        client_ui_format_q16(stored_buf, sizeof(stored_buf), net->nodes[n].stored_q16);
                        client_ui_format_q16(cap_buf, sizeof(cap_buf), net->nodes[n].capacity_q16);
                        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                           "node id=%llu stored=%s/%s status=%s",
                                           (unsigned long long)net->nodes[n].node_id,
                                           stored_buf,
                                           cap_buf,
                                           client_ui_network_status_name(net->nodes[n].status));
                    }
                    for (n = 0u; n < net->graph.node_count && count < CLIENT_UI_MAX_LINES; ++n) {
                        if (net->nodes[n].status == DOM_NETWORK_FAILED) {
                            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                               "bottleneck node=%llu status=failed",
                                               (unsigned long long)net->nodes[n].node_id);
                            break;
                        }
                    }
                    for (e = 0u; e < net->graph.edge_count && count < CLIENT_UI_MAX_LINES; ++e) {
                        if (net->edges[e].status == DOM_NETWORK_FAILED) {
                            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                               "bottleneck edge=%llu status=failed",
                                               (unsigned long long)net->edges[e].edge_id);
                            break;
                        }
                    }
                }
            }
            if (state->event_count > 0) {
                int i;
                int start = state->event_count > 3 ? (state->event_count - 3) : 0;
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                                   client_ui_text(state, "ui.client.events.tail", "event_tail:"));
                for (i = start; i < state->event_count && count < CLIENT_UI_MAX_LINES; ++i) {
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->event_lines[i]);
                }
            }
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           "Keys: WASD move, R/F up/down, 1-3 modes, ` console, B back");
        if (state->console_active) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "> %s", state->console_input);
        }
        if (state->settings.debug_ui) {
            int i;
            int idx = state->event_head;
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                               client_ui_text(state, "ui.client.debug.event_tail", "Debug: event_tail"));
            for (i = 0; i < state->event_count && count < CLIENT_UI_MAX_LINES; ++i) {
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                                   state->event_lines[idx]);
                idx = (idx + 1) % CLIENT_UI_EVENT_LINES;
            }
        }
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_REPLAY) {
        int i;
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.replay.title", "Replay"));
        if (state->replay_count <= 0) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "replays=none path=%s/replays",
                               state->data_root[0] ? state->data_root : "data");
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "Create a replay to inspect.");
        } else {
            for (i = 0; i < state->replay_count && count < CLIENT_UI_MAX_LINES; ++i) {
                const client_ui_replay_entry* entry = &state->replays[i];
                const char* name = entry->source[0] ? entry->source : "(unnamed)";
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                                   "%s %s", (i == state->replay_index) ? ">" : " ", name);
            }
            if (state->replay_index >= 0 && state->replay_index < state->replay_count) {
                const client_ui_replay_entry* selected = &state->replays[state->replay_index];
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "selected=%s",
                                   selected->source[0] ? selected->source : "(unnamed)");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "duration=%s",
                                   selected->duration[0] ? selected->duration : "unknown");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "determinism=%s",
                                   selected->determinism[0] ? selected->determinism : "unknown");
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "path=%s",
                                   selected->path[0] ? selected->path : "unknown");
                if (selected->status[0] && strcmp(selected->status, "ok") != 0) {
                    client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "status=%s",
                                       selected->status);
                }
            }
        }
        if (state->replay_loaded) {
            int end = state->replay_cursor;
            int start;
            if (end > state->replay_event_count) {
                end = state->replay_event_count;
            }
            start = (end > 5) ? (end - 5) : 0;
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "inspect_only=on cursor=%d/%d paused=%s",
                               end,
                               state->replay_event_count,
                               state->replay_paused ? "yes" : "no");
            for (i = start; i < end && count < CLIENT_UI_MAX_LINES; ++i) {
                client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                                   state->replay_events[i]);
            }
        } else {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                               "inspect_only=on (load a replay to step)");
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES,
                           "Keys: W/S select, Enter=load, Space=step, P=pause, R=rewind, B=back");
        if (state->console_active) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "> %s", state->console_input);
        }
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_TOOLS) {
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.tools.title", "Tools"));
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state,
                                          "ui.client.tools.hint",
                                          "Use tools host: tools_host --help"));
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state, "ui.client.back", "B=back"));
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    } else if (state->screen == CLIENT_UI_SETTINGS) {
        char setting_lines[CLIENT_UI_SETTINGS_LINES][CLIENT_UI_LABEL_MAX];
        int count_settings = 0;
        int i;
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "");
        client_ui_settings_format_lines(&state->settings, (char*)setting_lines,
                                        CLIENT_UI_SETTINGS_LINES,
                                        CLIENT_UI_LABEL_MAX, &count_settings);
        for (i = 0; i < count_settings && count < CLIENT_UI_MAX_LINES; ++i) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", setting_lines[i]);
        }
        client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s",
                           client_ui_text(state,
                                          "ui.client.settings.keys",
                                          "Keys: R renderer, +/- scale, P palette, L log, A accessibility, K keybind, D debug, B back"));
        if (state->action_status[0]) {
            client_ui_add_line(lines, &count, CLIENT_UI_MAX_LINES, "%s", state->action_status);
        }
    }
    if (out_count) {
        *out_count = count;
    }
}

static void client_console_clear(client_ui_state* state)
{
    if (!state) {
        return;
    }
    state->console_len = 0u;
    state->console_input[0] = '\0';
}

static void client_console_append_text(client_ui_state* state, const char* text)
{
    const char* p;
    if (!state || !text) {
        return;
    }
    p = text;
    while (*p) {
        char c = *p++;
        if (c == '\r' || c == '\n') {
            continue;
        }
        if (state->console_len + 1u >= sizeof(state->console_input)) {
            break;
        }
        if ((unsigned char)c < 32u) {
            continue;
        }
        state->console_input[state->console_len++] = c;
        state->console_input[state->console_len] = '\0';
    }
}

static void client_console_backspace(client_ui_state* state)
{
    if (!state || state->console_len == 0u) {
        return;
    }
    state->console_len -= 1u;
    state->console_input[state->console_len] = '\0';
}

static void client_console_submit(client_ui_state* state, dom_app_ui_event_log* log)
{
    if (!state) {
        return;
    }
    if (state->console_len == 0u) {
        return;
    }
    client_ui_execute_command(state->console_input, &state->settings, log, state,
                              state->action_status, sizeof(state->action_status), 0);
    client_console_clear(state);
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

static int client_ui_execute_command(const char* cmd,
                                     client_ui_settings* settings,
                                     dom_app_ui_event_log* log,
                                     client_ui_state* ui_state,
                                     char* status,
                                     size_t status_cap,
                                     int emit_text)
{
    static dom_client_shell cli_shell;
    static int cli_shell_ready = 0;
    static int cli_profile_index = 0;
    static int cli_preset_index = 0;
    static client_ui_settings fallback_settings;
    static int fallback_settings_ready = 0;
    static client_options_model options_model;
    static client_world_model world_model;
    static client_server_model server_model;
    static int models_ready = 0;
    dom_client_shell* shell = 0;
    client_state_machine state_machine;
    char cmd_buf[512];
    char bridged_cmd[512];
    char bridge_message[CLIENT_UI_STATUS_MAX];
    char capabilities_storage[512];
    const char* capability_ids[32];
    u32 capability_count = 0u;
    const char* effective_cmd = cmd;
    client_command_bridge_result bridge_result = CLIENT_COMMAND_BRIDGE_NOT_CANONICAL;
    const char* provider_refusal = 0;
    client_discovery_provider_status lan_status;
    char* token;
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!cmd || !cmd[0]) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client: missing command");
        }
        return D_APP_EXIT_USAGE;
    }
    if (!settings) {
        if (!fallback_settings_ready) {
            client_ui_settings_init(&fallback_settings);
            fallback_settings_ready = 1;
        }
        settings = &fallback_settings;
    }
    if (!ui_state) {
        if (!cli_shell_ready) {
            dom_client_shell_init(&cli_shell);
            cli_shell_ready = 1;
        }
        shell = &cli_shell;
    } else {
        shell = &ui_state->shell;
    }
    if (!models_ready) {
        client_options_model_init(&options_model);
        client_world_model_init(&world_model);
        client_server_model_init(&server_model);
        models_ready = 1;
    }
    client_state_machine_init(&state_machine);
    capability_count = client_collect_capabilities(getenv("DOM_CLIENT_CAPABILITIES"),
                                                   capabilities_storage,
                                                   sizeof(capabilities_storage),
                                                   capability_ids,
                                                   32u);
    bridge_result = client_command_bridge_prepare(cmd,
                                                  bridged_cmd,
                                                  sizeof(bridged_cmd),
                                                  bridge_message,
                                                  sizeof(bridge_message),
                                                  capability_ids,
                                                  capability_count,
                                                  &state_machine);
    if (bridge_result == CLIENT_COMMAND_BRIDGE_REFUSED) {
        if (log) {
            dom_app_ui_event_log_emit(log,
                                      client_state_machine_last_command(&state_machine),
                                      bridge_message);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", bridge_message);
        }
        if (emit_text) {
            printf("%s\n", bridge_message);
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (bridge_result == CLIENT_COMMAND_BRIDGE_SYNTHETIC_OK) {
        if (log) {
            dom_app_ui_event_log_emit(log,
                                      client_state_machine_last_command(&state_machine),
                                      bridge_message);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", bridge_message);
        }
        if (emit_text) {
            printf("%s\n", bridge_message);
        }
        return D_APP_EXIT_OK;
    }
    if (bridge_result == CLIENT_COMMAND_BRIDGE_REWRITTEN) {
        effective_cmd = bridged_cmd;
    }

    strncpy(cmd_buf, effective_cmd, sizeof(cmd_buf) - 1u);
    cmd_buf[sizeof(cmd_buf) - 1u] = '\0';
    token = strtok(cmd_buf, " \t");
    if (!token) {
        return D_APP_EXIT_USAGE;
    }
    lan_status = client_network_provider_lan();
    provider_refusal = client_network_provider_refusal_code(lan_status);
    if (strcmp(token, "server-list") == 0 || strcmp(token, "server-connect") == 0) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "refusal=%s command=%s", provider_refusal, token);
        }
        if (emit_text) {
            printf("refusal=%s command=%s\n", provider_refusal, token);
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(token, "tools") == 0) {
        if (log) {
            dom_app_ui_event_log_emit(log, "client.tools", "result=ok");
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_tools=ok");
        }
        if (emit_text) {
            printf("client_tools=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "settings") == 0) {
        char lines[CLIENT_UI_SETTINGS_LINES][CLIENT_UI_LABEL_MAX];
        int count = 0;
        int i;
        client_ui_settings_format_lines(settings, (char*)lines,
                                        CLIENT_UI_SETTINGS_LINES,
                                        CLIENT_UI_LABEL_MAX, &count);
        if (log) {
            dom_app_ui_event_log_emit(log, "client.settings", "result=ok");
        }
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
    if (strcmp(token, "settings-reset") == 0) {
        client_ui_settings_init(settings);
        if (log) {
            dom_app_ui_event_log_emit(log, "client.settings", "result=reset");
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_settings=reset");
        }
        if (emit_text) {
            printf("client_settings=reset\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "exit") == 0 || strcmp(token, "quit") == 0) {
        if (log) {
            dom_app_ui_event_log_emit(log, "client.exit", "result=ok");
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "client_exit=ok");
        }
        if (emit_text) {
            printf("client_exit=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "create-world") == 0 || strcmp(token, "create") == 0) {
        const char* path = 0;
        const char* args = cmd;
        char new_cmd[512];
        char create_status[CLIENT_UI_STATUS_MAX];
        char save_status[CLIENT_UI_STATUS_MAX];
        char save_path[CLIENT_UI_PATH_MAX];
        char* next = 0;
        int create_res;
        while (*args && isspace((unsigned char)*args)) {
            args++;
        }
        if (strncmp(args, token, strlen(token)) == 0) {
            args += strlen(token);
        }
        while (*args && isspace((unsigned char)*args)) {
            args++;
        }
        while ((next = strtok(0, " \t")) != 0) {
            if (strncmp(next, "path=", 5) == 0) {
                path = next + 5;
            } else if (!path && !strchr(next, '=')) {
                path = next;
            }
        }
        if (args && args[0]) {
            snprintf(new_cmd, sizeof(new_cmd), "new-world %s persist=1", args);
        } else {
            snprintf(new_cmd, sizeof(new_cmd), "new-world persist=1");
        }
        create_status[0] = '\0';
        create_res = dom_client_shell_execute(shell,
                                              new_cmd,
                                              log,
                                              create_status,
                                              sizeof(create_status),
                                              emit_text);
        if (create_res != D_APP_EXIT_OK || !shell->world.active) {
            if (status && status_cap > 0u) {
                if (create_status[0]) {
                    snprintf(status, status_cap, "%s", create_status);
                } else {
                    snprintf(status, status_cap, "world_create=refused");
                }
            }
            return create_res;
        }
        if (create_status[0] && strstr(create_status, "world_save=")) {
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "%s", create_status);
            }
            return create_res;
        }
        if (!path || !path[0]) {
            if (ui_state) {
                client_ui_build_world_save_path(ui_state, save_path, sizeof(save_path));
            } else {
                char data_root[CLIENT_UI_PATH_MAX];
                client_ui_default_data_root(data_root, sizeof(data_root));
                client_ui_build_world_save_path_for_seed(data_root,
                                                         (unsigned long long)shell->create_seed,
                                                         save_path,
                                                         sizeof(save_path));
            }
            path = save_path;
        }
        save_status[0] = '\0';
        {
            int save_res = dom_client_shell_save_world(shell,
                                                       path,
                                                       log,
                                                       save_status,
                                                       sizeof(save_status),
                                                       emit_text);
            if (status && status_cap > 0u) {
                if (save_res == D_APP_EXIT_OK) {
                    snprintf(status, status_cap, "world_create=ok world_save=ok path=%s", path);
                } else {
                    snprintf(status, status_cap, "world_create=ok world_save=refused path=%s", path);
                }
            }
            return save_res;
        }
    }
    if (strcmp(token, "profile-next") == 0 || strcmp(token, "profile-prev") == 0) {
        int next_index = ui_state ? ui_state->create_profile_index : cli_profile_index;
        int dir = (strcmp(token, "profile-prev") == 0) ? -1 : 1;
        const client_ui_profile* profile;
        next_index += dir;
        if (next_index < 0) {
            next_index = CLIENT_UI_PROFILE_COUNT - 1;
        } else if (next_index >= CLIENT_UI_PROFILE_COUNT) {
            next_index = 0;
        }
        profile = client_ui_profile_at(next_index);
        if (!profile) {
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (ui_state) {
            client_ui_apply_profile(ui_state, next_index);
        } else {
            cli_profile_index = next_index;
            client_ui_apply_profile_settings(settings, profile);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "profile=%s", profile->id);
        }
        if (emit_text) {
            printf("profile=%s\n", profile->id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "preset-next") == 0 || strcmp(token, "preset-prev") == 0 ||
        strcmp(token, "meta-law-next") == 0 || strcmp(token, "meta-law-prev") == 0) {
        int next_index = ui_state ? ui_state->create_preset_index : cli_preset_index;
        int dir = (strcmp(token, "preset-prev") == 0 || strcmp(token, "meta-law-prev") == 0) ? -1 : 1;
        const client_ui_policy_preset* preset;
        next_index += dir;
        if (next_index < 0) {
            next_index = CLIENT_UI_POLICY_PRESET_COUNT - 1;
        } else if (next_index >= CLIENT_UI_POLICY_PRESET_COUNT) {
            next_index = 0;
        }
        preset = client_ui_preset_at(next_index);
        if (!preset) {
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (ui_state) {
            client_ui_apply_preset(ui_state, next_index);
        } else {
            cli_preset_index = next_index;
            (void)dom_client_shell_set_create_policy(shell, "authority", preset->authority_csv);
            (void)dom_client_shell_set_create_policy(shell, "mode", preset->mode_csv);
            (void)dom_client_shell_set_create_policy(shell, "debug", preset->debug_csv);
            (void)dom_client_shell_set_create_policy(shell, "playtest", preset->playtest_csv);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "meta_preset=%s", preset->id);
        }
        if (emit_text) {
            printf("meta_preset=%s\n", preset->id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "accessibility-next") == 0) {
        int next_index = 0;
        int i;
        for (i = 0; i < CLIENT_UI_ACCESSIBILITY_PRESET_COUNT; ++i) {
            if (strcmp(settings->accessibility_preset_id,
                       g_client_accessibility_presets[i].id) == 0) {
                next_index = (i + 1) % CLIENT_UI_ACCESSIBILITY_PRESET_COUNT;
                break;
            }
        }
        if (ui_state) {
            client_ui_apply_accessibility_preset(ui_state, next_index);
        } else {
            client_ui_apply_accessibility_settings(settings, &g_client_accessibility_presets[next_index]);
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "accessibility=%s", g_client_accessibility_presets[next_index].id);
        }
        if (emit_text) {
            printf("accessibility=%s\n", g_client_accessibility_presets[next_index].id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "keybind-next") == 0) {
        if (ui_state) {
            client_ui_cycle_keybind_profile(ui_state);
        } else {
            int i;
            const char* current = settings->keybind_profile_id;
            for (i = 0; i < CLIENT_UI_KEYBIND_PROFILE_COUNT; ++i) {
                if (strcmp(current, g_client_keybind_profiles[i]) == 0) {
                    int next = (i + 1) % CLIENT_UI_KEYBIND_PROFILE_COUNT;
                    strncpy(settings->keybind_profile_id,
                            g_client_keybind_profiles[next],
                            sizeof(settings->keybind_profile_id) - 1u);
                    settings->keybind_profile_id[sizeof(settings->keybind_profile_id) - 1u] = '\0';
                    break;
                }
            }
            if (i >= CLIENT_UI_KEYBIND_PROFILE_COUNT) {
                strncpy(settings->keybind_profile_id,
                        g_client_keybind_profiles[0],
                        sizeof(settings->keybind_profile_id) - 1u);
                settings->keybind_profile_id[sizeof(settings->keybind_profile_id) - 1u] = '\0';
            }
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "keybind_profile=%s", settings->keybind_profile_id);
        }
        if (emit_text) {
            printf("keybind_profile=%s\n", settings->keybind_profile_id);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(token, "replay-step") == 0 ||
        strcmp(token, "replay-rewind") == 0 ||
        strcmp(token, "replay-pause") == 0) {
        if (!ui_state) {
            if (status && status_cap > 0u) {
                snprintf(status, status_cap, "replay_control=refused reason=ui_required");
            }
            if (emit_text) {
                printf("replay_control=refused reason=ui_required\n");
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (strcmp(token, "replay-step") == 0) {
            if (ui_state->replay_loaded) {
                if (ui_state->replay_cursor < ui_state->replay_event_count) {
                    ui_state->replay_cursor += 1;
                    client_ui_set_status(ui_state, "replay_step=ok cursor=%d", ui_state->replay_cursor);
                } else {
                    client_ui_set_status(ui_state, "replay_step=refused reason=end");
                }
            } else {
                client_ui_set_status(ui_state, "replay_step=refused reason=not_loaded");
            }
        } else if (strcmp(token, "replay-rewind") == 0) {
            if (ui_state->replay_loaded) {
                ui_state->replay_cursor = 0;
                client_ui_set_status(ui_state, "replay_rewind=ok");
            } else {
                client_ui_set_status(ui_state, "replay_rewind=refused reason=not_loaded");
            }
        } else {
            if (ui_state->replay_loaded) {
                ui_state->replay_paused = ui_state->replay_paused ? 0 : 1;
                client_ui_set_status(ui_state,
                                     "replay_pause=%s",
                                     ui_state->replay_paused ? "on" : "off");
            } else {
                client_ui_set_status(ui_state, "replay_pause=refused reason=not_loaded");
            }
        }
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "%s", ui_state->action_status);
        }
        if (emit_text && ui_state->action_status[0]) {
            printf("%s\n", ui_state->action_status);
        }
        return D_APP_EXIT_OK;
    }
    return dom_client_shell_execute(shell, effective_cmd, log, status, status_cap, emit_text);
}

static void client_ui_apply_action(client_ui_state* state,
                                   client_ui_action action,
                                   dom_app_ui_event_log* log,
                                   const dom_app_compat_expect* compat)
{
    if (!state) {
        return;
    }
    (void)compat;
    switch (action) {
    case CLIENT_ACTION_NEW_WORLD:
    {
        const client_ui_profile* profile = client_ui_profile_at(state->create_profile_index);
        const client_ui_policy_preset* preset = client_ui_preset_at(state->create_preset_index);
        client_ui_apply_profile(state, state->create_profile_index);
        client_ui_apply_preset(state, state->create_preset_index);
        snprintf(state->action_status, sizeof(state->action_status),
                 "world_create=ready profile=%s preset=%s",
                 profile ? profile->id : "unknown",
                 preset ? preset->id : "unknown");
        state->screen = CLIENT_UI_WORLD_CREATE;
        break;
    }
    case CLIENT_ACTION_CREATE_WORLD:
    {
        if (state->compat_status[0] && strstr(state->compat_status, "compat_status=failed")) {
            client_ui_set_status(state, "world_create=refused compat_failed");
            break;
        }
        client_ui_execute_command("create-world",
                                  &state->settings,
                                  log,
                                  state,
                                  state->action_status,
                                  sizeof(state->action_status),
                                  0);
        if (state->shell.world.active) {
            if (strstr(state->action_status, "world_save=ok")) {
                client_ui_refresh_worlds(state);
            }
            state->screen = CLIENT_UI_WORLD_VIEW;
        }
        break;
    }
    case CLIENT_ACTION_LOAD_WORLD:
        if (state->screen == CLIENT_UI_MAIN_MENU) {
            if (state->world_count <= 0) {
                client_ui_set_status(state, "world_load=refused reason=no_saves");
                if (log) {
                    dom_app_ui_event_log_emit(log, "client.world.load", "result=refused");
                }
            } else {
                client_ui_refresh_worlds(state);
                state->screen = CLIENT_UI_WORLD_LOAD;
            }
            break;
        }
        if (state->screen == CLIENT_UI_WORLD_LOAD) {
            if (state->world_count <= 0 ||
                state->world_index < 0 ||
                state->world_index >= state->world_count) {
                client_ui_set_status(state, "world_load=refused reason=selection_missing");
                if (log) {
                    dom_app_ui_event_log_emit(log, "client.world.load", "result=refused");
                }
                break;
            }
            dom_client_shell_load_world(&state->shell,
                                        state->worlds[state->world_index].path,
                                        log,
                                        state->action_status, sizeof(state->action_status), 0);
            if (state->shell.world.active) {
                state->screen = CLIENT_UI_WORLD_VIEW;
            }
        }
        break;
    case CLIENT_ACTION_SAVE_WORLD:
        dom_client_shell_save_world(&state->shell, 0, log,
                                    state->action_status, sizeof(state->action_status), 0);
        break;
    case CLIENT_ACTION_SCENARIO_LOAD: {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "scenario-load path=%s", CLIENT_UI_DEFAULT_SCENARIO_PATH);
        client_ui_execute_command(cmd, &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        if (state->shell.world.active) {
            state->screen = CLIENT_UI_WORLD_VIEW;
        }
        break;
    }
    case CLIENT_ACTION_VARIANT_APPLY: {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "variant-apply path=%s", CLIENT_UI_DEFAULT_VARIANT_PATH);
        client_ui_execute_command(cmd, &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        break;
    }
    case CLIENT_ACTION_REPLAY_SAVE:
        client_ui_execute_command("replay-save", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        client_ui_refresh_replays(state);
        break;
    case CLIENT_ACTION_INSPECT_REPLAY:
        if (state->screen == CLIENT_UI_MAIN_MENU) {
            if (state->replay_count <= 0) {
                client_ui_set_status(state, "replay_inspect=refused reason=no_replays");
                if (log) {
                    dom_app_ui_event_log_emit(log, "client.replay.inspect", "result=refused");
                }
            } else {
                client_ui_refresh_replays(state);
                client_ui_replay_reset(state);
                snprintf(state->action_status, sizeof(state->action_status), "replay_inspect=ready");
                state->screen = CLIENT_UI_REPLAY;
            }
        } else if (state->screen == CLIENT_UI_REPLAY) {
            if (state->replay_count <= 0 ||
                state->replay_index < 0 ||
                state->replay_index >= state->replay_count) {
                client_ui_set_status(state, "replay_inspect=refused reason=selection_missing");
                if (log) {
                    dom_app_ui_event_log_emit(log, "client.replay.inspect", "result=refused");
                }
                break;
            }
            {
                char cmd[CLIENT_UI_PATH_MAX + 32];
                int inspect_res;
                snprintf(cmd, sizeof(cmd), "inspect-replay path=%s",
                         state->replays[state->replay_index].path);
                inspect_res = client_ui_execute_command(cmd, &state->settings, log, state,
                                                       state->action_status,
                                                       sizeof(state->action_status), 0);
                if (inspect_res == D_APP_EXIT_OK) {
                    (void)client_ui_replay_load_events(state,
                                                       state->replays[state->replay_index].path,
                                                       state->action_status,
                                                       sizeof(state->action_status));
                }
            }
        }
        break;
    case CLIENT_ACTION_TOOLS:
        client_ui_execute_command("tools", &state->settings, log, state,
                                  state->action_status, sizeof(state->action_status), 0);
        state->screen = CLIENT_UI_TOOLS;
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
        if (state->screen == CLIENT_UI_REPLAY) {
            client_ui_replay_reset(state);
        }
        state->screen = CLIENT_UI_MAIN_MENU;
        client_ui_refresh_worlds(state);
        client_ui_refresh_replays(state);
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
    case CLIENT_ACTION_MODE_FREE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_set_mode(&state->shell, DOM_SHELL_MODE_FREE, log,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "mode_set=ignored");
        }
        break;
    case CLIENT_ACTION_MODE_ORBIT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_set_mode(&state->shell, DOM_SHELL_MODE_ORBIT, log,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "mode_set=ignored");
        }
        break;
    case CLIENT_ACTION_MODE_SURFACE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_set_mode(&state->shell, DOM_SHELL_MODE_SURFACE, log,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "mode_set=ignored");
        }
        break;
    case CLIENT_ACTION_MOVE_FORWARD:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, 0.0, 1.0, 0.0, log);
        }
        break;
    case CLIENT_ACTION_MOVE_BACK:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, 0.0, -1.0, 0.0, log);
        }
        break;
    case CLIENT_ACTION_MOVE_LEFT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, -1.0, 0.0, 0.0, log);
        }
        break;
    case CLIENT_ACTION_MOVE_RIGHT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, 1.0, 0.0, 0.0, log);
        }
        break;
    case CLIENT_ACTION_MOVE_UP:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, 0.0, 0.0, 1.0, log);
        }
        break;
    case CLIENT_ACTION_MOVE_DOWN:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            dom_client_shell_move(&state->shell, 0.0, 0.0, -1.0, log);
        }
        break;
    case CLIENT_ACTION_CAMERA_NEXT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("camera-next", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "camera_set=ignored");
        }
        break;
    case CLIENT_ACTION_INSPECT_TOGGLE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("inspect-toggle", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "inspect=ignored");
        }
        break;
    case CLIENT_ACTION_HUD_TOGGLE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("hud-toggle", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "hud=ignored");
        }
        break;
    case CLIENT_ACTION_SPAWN:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("spawn", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "spawn=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_MARKER:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.interaction.marker",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_BEACON:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.interaction.beacon",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_INDICATOR:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.interaction.indicator",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_BUTTON:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.signal.button",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LEVER:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.signal.lever",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_WIRE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.signal.wire",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LAMP:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.signal.lamp",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_COUNTER:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-select type=org.dominium.core.signal.counter",
                                      &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_select=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_PLACE_PREVIEW:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("place-preview", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_preview=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_PLACE_CONFIRM:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("place-confirm", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_confirm=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_PLACE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("place", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_place=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_REMOVE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("remove", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_remove=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_SIGNAL:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-toggle", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_signal=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_MEASURE:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("measure", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_measure=ignored");
        }
        break;
    case CLIENT_ACTION_INTERACTION_INSPECT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("object-inspect", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "interaction_inspect=ignored");
        }
        break;
    case CLIENT_ACTION_SIGNAL_LIST:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-list", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "signal_list=ignored");
        }
        break;
    case CLIENT_ACTION_SIGNAL_PREVIEW:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-preview", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "signal_preview=ignored");
        }
        break;
    case CLIENT_ACTION_SIGNAL_CONNECT:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-connect", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "signal_connect=ignored");
        }
        break;
    case CLIENT_ACTION_SIGNAL_THRESHOLD:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-threshold", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "signal_threshold=ignored");
        }
        break;
    case CLIENT_ACTION_SIGNAL_SET:
        if (state->screen == CLIENT_UI_WORLD_VIEW) {
            client_ui_execute_command("signal-set value=1", &state->settings, log, state,
                                      state->action_status, sizeof(state->action_status), 0);
        } else {
            client_ui_set_status(state, "signal_set=ignored");
        }
        break;
    case CLIENT_ACTION_PROFILE_NEXT: {
        int next = (state->create_profile_index + 1) % CLIENT_UI_PROFILE_COUNT;
        client_ui_apply_profile(state, next);
        client_ui_set_status(state, "profile=%s", g_client_profiles[next].id);
        break;
    }
    case CLIENT_ACTION_PROFILE_PREV: {
        int next = state->create_profile_index - 1;
        if (next < 0) {
            next = CLIENT_UI_PROFILE_COUNT - 1;
        }
        client_ui_apply_profile(state, next);
        client_ui_set_status(state, "profile=%s", g_client_profiles[next].id);
        break;
    }
    case CLIENT_ACTION_PRESET_NEXT: {
        int next = (state->create_preset_index + 1) % CLIENT_UI_POLICY_PRESET_COUNT;
        client_ui_apply_preset(state, next);
        client_ui_set_status(state, "meta_preset=%s", g_client_policy_presets[next].id);
        break;
    }
    case CLIENT_ACTION_PRESET_PREV: {
        int next = state->create_preset_index - 1;
        if (next < 0) {
            next = CLIENT_UI_POLICY_PRESET_COUNT - 1;
        }
        client_ui_apply_preset(state, next);
        client_ui_set_status(state, "meta_preset=%s", g_client_policy_presets[next].id);
        break;
    }
    case CLIENT_ACTION_ACCESSIBILITY_NEXT: {
        int next = 0;
        int i;
        for (i = 0; i < CLIENT_UI_ACCESSIBILITY_PRESET_COUNT; ++i) {
            if (strcmp(state->settings.accessibility_preset_id,
                       g_client_accessibility_presets[i].id) == 0) {
                next = (i + 1) % CLIENT_UI_ACCESSIBILITY_PRESET_COUNT;
                break;
            }
        }
        client_ui_apply_accessibility_preset(state, next);
        client_ui_set_status(state, "accessibility=%s", g_client_accessibility_presets[next].id);
        break;
    }
    case CLIENT_ACTION_KEYBIND_NEXT:
        client_ui_cycle_keybind_profile(state);
        client_ui_set_status(state, "keybind_profile=%s", state->settings.keybind_profile_id);
        break;
    case CLIENT_ACTION_REPLAY_STEP:
        if (state->replay_loaded) {
            if (state->replay_cursor < state->replay_event_count) {
                state->replay_cursor += 1;
                client_ui_set_status(state, "replay_step=ok cursor=%d", state->replay_cursor);
            } else {
                client_ui_set_status(state, "replay_step=refused reason=end");
            }
        } else {
            client_ui_set_status(state, "replay_step=refused reason=not_loaded");
        }
        break;
    case CLIENT_ACTION_REPLAY_REWIND:
        if (state->replay_loaded) {
            state->replay_cursor = 0;
            client_ui_set_status(state, "replay_rewind=ok");
        } else {
            client_ui_set_status(state, "replay_rewind=refused reason=not_loaded");
        }
        break;
    case CLIENT_ACTION_REPLAY_TOGGLE_PAUSE:
        if (state->replay_loaded) {
            state->replay_paused = state->replay_paused ? 0 : 1;
            client_ui_set_status(state, "replay_pause=%s", state->replay_paused ? "on" : "off");
        } else {
            client_ui_set_status(state, "replay_pause=refused reason=not_loaded");
        }
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
    if (strcmp(token, "new-world") == 0 || strcmp(token, "new") == 0) return CLIENT_ACTION_NEW_WORLD;
    if (strcmp(token, "create-world") == 0 || strcmp(token, "create") == 0) return CLIENT_ACTION_CREATE_WORLD;
    if (strcmp(token, "load-world") == 0 || strcmp(token, "load-save") == 0 || strcmp(token, "load") == 0) {
        return CLIENT_ACTION_LOAD_WORLD;
    }
    if (strcmp(token, "scenario-load") == 0 || strcmp(token, "load-scenario") == 0) {
        return CLIENT_ACTION_SCENARIO_LOAD;
    }
    if (strcmp(token, "replay") == 0 || strcmp(token, "inspect-replay") == 0) return CLIENT_ACTION_INSPECT_REPLAY;
    if (strcmp(token, "save") == 0) return CLIENT_ACTION_SAVE_WORLD;
    if (strcmp(token, "replay-save") == 0 || strcmp(token, "save-replay") == 0) {
        return CLIENT_ACTION_REPLAY_SAVE;
    }
    if (strcmp(token, "variant-apply") == 0 || strcmp(token, "variant-load") == 0) {
        return CLIENT_ACTION_VARIANT_APPLY;
    }
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
    if (strcmp(token, "mode-free") == 0) return CLIENT_ACTION_MODE_FREE;
    if (strcmp(token, "mode-orbit") == 0) return CLIENT_ACTION_MODE_ORBIT;
    if (strcmp(token, "mode-surface") == 0) return CLIENT_ACTION_MODE_SURFACE;
    if (strcmp(token, "move-forward") == 0) return CLIENT_ACTION_MOVE_FORWARD;
    if (strcmp(token, "move-back") == 0) return CLIENT_ACTION_MOVE_BACK;
    if (strcmp(token, "move-left") == 0) return CLIENT_ACTION_MOVE_LEFT;
    if (strcmp(token, "move-right") == 0) return CLIENT_ACTION_MOVE_RIGHT;
    if (strcmp(token, "move-up") == 0) return CLIENT_ACTION_MOVE_UP;
    if (strcmp(token, "move-down") == 0) return CLIENT_ACTION_MOVE_DOWN;
    if (strcmp(token, "camera-next") == 0) return CLIENT_ACTION_CAMERA_NEXT;
    if (strcmp(token, "inspect-toggle") == 0 || strcmp(token, "inspect") == 0) {
        return CLIENT_ACTION_INSPECT_TOGGLE;
    }
    if (strcmp(token, "hud-toggle") == 0 || strcmp(token, "hud") == 0) {
        return CLIENT_ACTION_HUD_TOGGLE;
    }
    if (strcmp(token, "spawn") == 0) return CLIENT_ACTION_SPAWN;
    if (strcmp(token, "interaction-select-marker") == 0) return CLIENT_ACTION_INTERACTION_SELECT_MARKER;
    if (strcmp(token, "interaction-select-beacon") == 0) return CLIENT_ACTION_INTERACTION_SELECT_BEACON;
    if (strcmp(token, "interaction-select-indicator") == 0) return CLIENT_ACTION_INTERACTION_SELECT_INDICATOR;
    if (strcmp(token, "interaction-select-signal-button") == 0 ||
        strcmp(token, "interaction-select-button") == 0) {
        return CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_BUTTON;
    }
    if (strcmp(token, "interaction-select-signal-lever") == 0 ||
        strcmp(token, "interaction-select-lever") == 0) {
        return CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LEVER;
    }
    if (strcmp(token, "interaction-select-signal-wire") == 0 ||
        strcmp(token, "interaction-select-wire") == 0) {
        return CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_WIRE;
    }
    if (strcmp(token, "interaction-select-signal-lamp") == 0 ||
        strcmp(token, "interaction-select-lamp") == 0) {
        return CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_LAMP;
    }
    if (strcmp(token, "interaction-select-signal-counter") == 0 ||
        strcmp(token, "interaction-select-counter") == 0) {
        return CLIENT_ACTION_INTERACTION_SELECT_SIGNAL_COUNTER;
    }
    if (strcmp(token, "interaction-preview") == 0 || strcmp(token, "place-preview") == 0) {
        return CLIENT_ACTION_INTERACTION_PLACE_PREVIEW;
    }
    if (strcmp(token, "interaction-confirm") == 0 || strcmp(token, "place-confirm") == 0) {
        return CLIENT_ACTION_INTERACTION_PLACE_CONFIRM;
    }
    if (strcmp(token, "interaction-place") == 0 || strcmp(token, "place") == 0) {
        return CLIENT_ACTION_INTERACTION_PLACE;
    }
    if (strcmp(token, "interaction-remove") == 0 || strcmp(token, "remove") == 0) {
        return CLIENT_ACTION_INTERACTION_REMOVE;
    }
    if (strcmp(token, "interaction-signal") == 0 || strcmp(token, "signal-toggle") == 0) {
        return CLIENT_ACTION_INTERACTION_SIGNAL;
    }
    if (strcmp(token, "interaction-measure") == 0 || strcmp(token, "measure") == 0) {
        return CLIENT_ACTION_INTERACTION_MEASURE;
    }
    if (strcmp(token, "interaction-inspect") == 0 || strcmp(token, "object-inspect") == 0) {
        return CLIENT_ACTION_INTERACTION_INSPECT;
    }
    if (strcmp(token, "signal-list") == 0 || strcmp(token, "signals") == 0) {
        return CLIENT_ACTION_SIGNAL_LIST;
    }
    if (strcmp(token, "signal-preview") == 0 || strcmp(token, "signal-connect-preview") == 0) {
        return CLIENT_ACTION_SIGNAL_PREVIEW;
    }
    if (strcmp(token, "signal-connect") == 0) return CLIENT_ACTION_SIGNAL_CONNECT;
    if (strcmp(token, "signal-threshold") == 0) return CLIENT_ACTION_SIGNAL_THRESHOLD;
    if (strcmp(token, "signal-set") == 0 || strcmp(token, "signal-emit") == 0) {
        return CLIENT_ACTION_SIGNAL_SET;
    }
    if (strcmp(token, "profile-next") == 0) return CLIENT_ACTION_PROFILE_NEXT;
    if (strcmp(token, "profile-prev") == 0) return CLIENT_ACTION_PROFILE_PREV;
    if (strcmp(token, "preset-next") == 0 || strcmp(token, "meta-law-next") == 0) {
        return CLIENT_ACTION_PRESET_NEXT;
    }
    if (strcmp(token, "preset-prev") == 0 || strcmp(token, "meta-law-prev") == 0) {
        return CLIENT_ACTION_PRESET_PREV;
    }
    if (strcmp(token, "accessibility-next") == 0) return CLIENT_ACTION_ACCESSIBILITY_NEXT;
    if (strcmp(token, "keybind-next") == 0) return CLIENT_ACTION_KEYBIND_NEXT;
    if (strcmp(token, "replay-step") == 0) return CLIENT_ACTION_REPLAY_STEP;
    if (strcmp(token, "replay-rewind") == 0) return CLIENT_ACTION_REPLAY_REWIND;
    if (strcmp(token, "replay-pause") == 0) return CLIENT_ACTION_REPLAY_TOGGLE_PAUSE;
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

static void client_gui_render(const client_ui_state* state,
                              d_gfx_cmd_buffer* buf,
                              int fb_w,
                              int fb_h)
{
    d_gfx_viewport vp;
    d_gfx_color bg = { 0xff, 0x12, 0x12, 0x18 };
    d_gfx_color text = { 0xff, 0xee, 0xee, 0xee };
    int width = (fb_w > 0) ? fb_w : 800;
    int height = (fb_h > 0) ? fb_h : 600;
    int y = 24;
    int line_h = 18;
    int i;
    char lines[CLIENT_UI_MAX_LINES][CLIENT_UI_LABEL_MAX];
    int count = 0;
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
    client_ui_build_lines(state, lines, &count);
    for (i = 0; i < count; ++i) {
        client_gui_draw_text(buf, 20, y, lines[i], text);
        y += line_h;
    }
}

static int client_run_tui(const dom_app_ui_run_config* run_cfg,
                          const client_ui_settings* settings,
                          d_app_timing_mode timing_mode,
                          uint32_t frame_cap_ms,
                          const dom_app_compat_expect* compat_expect)
{
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
    char lines[CLIENT_UI_MAX_LINES][CLIENT_UI_LABEL_MAX];
    int line_count = 0;
    int i;

    client_ui_state_init(&ui, settings, compat_expect, timing_mode);
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
    if (dsys_terminal_init() != 0) {
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
        dom_client_shell_tick(&ui.shell);
        dom_app_pump_terminal_input();
        while (dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_CONSOLE);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                int key = ev.payload.key.key;
                if (ui.console_active) {
                    if (key == 27) {
                        ui.console_active = 0;
                    } else if (key == 8 || key == 127) {
                        client_console_backspace(&ui);
                    } else if (key == '\r' || key == '\n') {
                        client_console_submit(&ui, &log);
                    }
                    continue;
                }
                if (key == '`' || key == '~') {
                    ui.console_active = ui.console_active ? 0 : 1;
                    if (ui.console_active) {
                        client_console_clear(&ui);
                    }
                    continue;
                }
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
                } else if (ui.screen == CLIENT_UI_WORLD_LOAD) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_refresh_worlds(&ui);
                    } else if (key == 'w' || key == 'W') {
                        if (ui.world_count > 0) {
                            ui.world_index = (ui.world_index > 0) ? (ui.world_index - 1) : (ui.world_count - 1);
                        }
                    } else if (key == 's' || key == 'S') {
                        if (ui.world_count > 0) {
                            ui.world_index = (ui.world_index + 1) % ui.world_count;
                        }
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_LOAD_WORLD, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_WORLD_CREATE) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 't' || key == 'T' || key == 's' || key == 'S') {
                        if (ui.shell.registry.count > 0u) {
                            ui.shell.create_template_index =
                                (ui.shell.create_template_index + 1u) % ui.shell.registry.count;
                        }
                    } else if (key == 'w' || key == 'W') {
                        if (ui.shell.registry.count > 0u) {
                            if (ui.shell.create_template_index == 0u) {
                                ui.shell.create_template_index = ui.shell.registry.count - 1u;
                            } else {
                                ui.shell.create_template_index -= 1u;
                            }
                        }
                    } else if (key == '+' || key == '=') {
                        ui.shell.create_seed += 1u;
                        client_ui_set_status(&ui, "seed=%llu", (unsigned long long)ui.shell.create_seed);
                    } else if (key == '-' || key == '_') {
                        if (ui.shell.create_seed > 0u) {
                            ui.shell.create_seed -= 1u;
                            client_ui_set_status(&ui, "seed=%llu", (unsigned long long)ui.shell.create_seed);
                        }
                    } else if (key == '1') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_FREE);
                    } else if (key == '2') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_ORBIT);
                    } else if (key == '3') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_SURFACE);
                    } else if (key == 'a' || key == 'A') {
                        client_policy_toggle(&ui.shell.create_authority, DOM_SHELL_AUTH_POLICY);
                    } else if (key == 'd' || key == 'D') {
                        if (ui.shell.create_debug.count > 0u) {
                            ui.shell.create_debug.count = 0u;
                        } else {
                            client_policy_toggle(&ui.shell.create_debug, "policy.debug.readonly");
                        }
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PROFILE_NEXT, &log, compat_expect);
                    } else if (key == 'm' || key == 'M') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PRESET_NEXT, &log, compat_expect);
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_CREATE_WORLD, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_WORLD_VIEW) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == '1') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_FREE, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == '2') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_ORBIT, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == '3') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_SURFACE, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == 'w' || key == 'W') {
                        dom_client_shell_move(&ui.shell, 0.0, 1.0, 0.0, &log);
                    } else if (key == 's' || key == 'S') {
                        dom_client_shell_move(&ui.shell, 0.0, -1.0, 0.0, &log);
                    } else if (key == 'a' || key == 'A') {
                        dom_client_shell_move(&ui.shell, -1.0, 0.0, 0.0, &log);
                    } else if (key == 'd' || key == 'D') {
                        dom_client_shell_move(&ui.shell, 1.0, 0.0, 0.0, &log);
                    } else if (key == 'r' || key == 'R') {
                        dom_client_shell_move(&ui.shell, 0.0, 0.0, 1.0, &log);
                    } else if (key == 'f' || key == 'F') {
                        dom_client_shell_move(&ui.shell, 0.0, 0.0, -1.0, &log);
                    } else if (key == 'c' || key == 'C') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_CAMERA_NEXT, &log, compat_expect);
                    } else if (key == 'i' || key == 'I') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INSPECT_TOGGLE, &log, compat_expect);
                    } else if (key == 'h' || key == 'H') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_HUD_TOGGLE, &log, compat_expect);
                    } else if (key == 'x' || key == 'X') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SPAWN, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_REPLAY) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'w' || key == 'W') {
                        if (ui.replay_count > 0) {
                            ui.replay_index = (ui.replay_index > 0) ? (ui.replay_index - 1) : (ui.replay_count - 1);
                        }
                    } else if (key == 's' || key == 'S') {
                        if (ui.replay_count > 0) {
                            ui.replay_index = (ui.replay_index + 1) % ui.replay_count;
                        }
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INSPECT_REPLAY, &log, compat_expect);
                    } else if (key == ' ') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_STEP, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_TOGGLE_PAUSE, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_REWIND, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_TOOLS) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
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
                    } else if (key == 'a' || key == 'A') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_ACCESSIBILITY_NEXT, &log, compat_expect);
                    } else if (key == 'k' || key == 'K') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_KEYBIND_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                }
            }
            if (ev.type == DSYS_EVENT_TEXT_INPUT) {
                if (ui.console_active) {
                    client_console_append_text(&ui, ev.payload.text.text);
                }
            }
        }
        client_ui_sync_events(&ui);
        if (ui.screen == CLIENT_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = CLIENT_UI_MAIN_MENU;
            }
        }
        if (script_ready && ui.screen != CLIENT_UI_LOADING) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                client_ui_apply_action(&ui, client_ui_action_from_token(token), &log, compat_expect);
            }
        }
        if (ui.exit_requested) {
            normal_exit = 1;
            dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_APP_REQUEST);
        }
        dom_app_clock_advance(&clock);
        dsys_terminal_clear();
        client_ui_build_lines(&ui, lines, &line_count);
        for (i = 0; i < line_count; ++i) {
            dsys_terminal_draw_text(i, 0, lines[i]);
        }
        dom_app_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
        frame_count += 1;
        if (max_frames > 0 && frame_count >= max_frames) {
            ui.exit_requested = 1;
        }
    }
    normal_exit = 1;

cleanup:
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

    client_ui_state_init(&ui, settings, compat_expect, timing_mode);
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
    if (headless) {
        if (client_renderer_supported(&ui.renderers, "null")) {
            if (renderer && renderer[0] && strcmp(renderer, "null") != 0) {
                fprintf(stderr, "client: headless forces null renderer (requested %s)\n", renderer);
            }
            renderer = "null";
            client_settings_set_renderer(&ui.settings, renderer);
        } else {
            if (renderer && renderer[0] && strcmp(renderer, "null") == 0) {
                renderer = client_renderer_default(&ui.renderers);
                client_settings_set_renderer(&ui.settings, renderer);
            }
            if (renderer && renderer[0]) {
                fprintf(stderr, "client: headless null renderer unavailable; using %s\n", renderer);
            }
        }
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
        while (!headless && dsys_poll_event(&ev)) {
            if (ev.type == DSYS_EVENT_QUIT) {
                dsys_lifecycle_request_shutdown(DSYS_SHUTDOWN_WINDOW);
                break;
            }
            if (ev.type == DSYS_EVENT_KEY_DOWN) {
                int key = ev.payload.key.key;
                if (ui.console_active) {
                    if (key == 27) {
                        ui.console_active = 0;
                    } else if (key == 8 || key == 127) {
                        client_console_backspace(&ui);
                    } else if (key == '\r' || key == '\n') {
                        client_console_submit(&ui, &log);
                    }
                    continue;
                }
                if (key == '`' || key == '~') {
                    ui.console_active = ui.console_active ? 0 : 1;
                    if (ui.console_active) {
                        client_console_clear(&ui);
                    }
                    continue;
                }
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
                } else if (ui.screen == CLIENT_UI_WORLD_LOAD) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_refresh_worlds(&ui);
                    } else if (key == 'w' || key == 'W') {
                        if (ui.world_count > 0) {
                            ui.world_index = (ui.world_index > 0) ? (ui.world_index - 1) : (ui.world_count - 1);
                        }
                    } else if (key == 's' || key == 'S') {
                        if (ui.world_count > 0) {
                            ui.world_index = (ui.world_index + 1) % ui.world_count;
                        }
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_LOAD_WORLD, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_WORLD_CREATE) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 't' || key == 'T' || key == 's' || key == 'S') {
                        if (ui.shell.registry.count > 0u) {
                            ui.shell.create_template_index =
                                (ui.shell.create_template_index + 1u) % ui.shell.registry.count;
                        }
                    } else if (key == 'w' || key == 'W') {
                        if (ui.shell.registry.count > 0u) {
                            if (ui.shell.create_template_index == 0u) {
                                ui.shell.create_template_index = ui.shell.registry.count - 1u;
                            } else {
                                ui.shell.create_template_index -= 1u;
                            }
                        }
                    } else if (key == '+' || key == '=') {
                        ui.shell.create_seed += 1u;
                        client_ui_set_status(&ui, "seed=%llu", (unsigned long long)ui.shell.create_seed);
                    } else if (key == '-' || key == '_') {
                        if (ui.shell.create_seed > 0u) {
                            ui.shell.create_seed -= 1u;
                            client_ui_set_status(&ui, "seed=%llu", (unsigned long long)ui.shell.create_seed);
                        }
                    } else if (key == '1') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_FREE);
                    } else if (key == '2') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_ORBIT);
                    } else if (key == '3') {
                        client_policy_toggle(&ui.shell.create_mode, DOM_SHELL_MODE_SURFACE);
                    } else if (key == 'a' || key == 'A') {
                        client_policy_toggle(&ui.shell.create_authority, DOM_SHELL_AUTH_POLICY);
                    } else if (key == 'd' || key == 'D') {
                        if (ui.shell.create_debug.count > 0u) {
                            ui.shell.create_debug.count = 0u;
                        } else {
                            client_policy_toggle(&ui.shell.create_debug, "policy.debug.readonly");
                        }
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PROFILE_NEXT, &log, compat_expect);
                    } else if (key == 'm' || key == 'M') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_PRESET_NEXT, &log, compat_expect);
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_CREATE_WORLD, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_WORLD_VIEW) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == '1') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_FREE, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == '2') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_ORBIT, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == '3') {
                        dom_client_shell_set_mode(&ui.shell, DOM_SHELL_MODE_SURFACE, &log,
                                                  ui.action_status, sizeof(ui.action_status), 0);
                    } else if (key == 'w' || key == 'W') {
                        dom_client_shell_move(&ui.shell, 0.0, 1.0, 0.0, &log);
                    } else if (key == 's' || key == 'S') {
                        dom_client_shell_move(&ui.shell, 0.0, -1.0, 0.0, &log);
                    } else if (key == 'a' || key == 'A') {
                        dom_client_shell_move(&ui.shell, -1.0, 0.0, 0.0, &log);
                    } else if (key == 'd' || key == 'D') {
                        dom_client_shell_move(&ui.shell, 1.0, 0.0, 0.0, &log);
                    } else if (key == 'r' || key == 'R') {
                        dom_client_shell_move(&ui.shell, 0.0, 0.0, 1.0, &log);
                    } else if (key == 'f' || key == 'F') {
                        dom_client_shell_move(&ui.shell, 0.0, 0.0, -1.0, &log);
                    } else if (key == 'c' || key == 'C') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_CAMERA_NEXT, &log, compat_expect);
                    } else if (key == 'i' || key == 'I') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INSPECT_TOGGLE, &log, compat_expect);
                    } else if (key == 'h' || key == 'H') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_HUD_TOGGLE, &log, compat_expect);
                    } else if (key == 'x' || key == 'X') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_SPAWN, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_REPLAY) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
                    } else if (key == 'w' || key == 'W') {
                        if (ui.replay_count > 0) {
                            ui.replay_index = (ui.replay_index > 0) ? (ui.replay_index - 1) : (ui.replay_count - 1);
                        }
                    } else if (key == 's' || key == 'S') {
                        if (ui.replay_count > 0) {
                            ui.replay_index = (ui.replay_index + 1) % ui.replay_count;
                        }
                    } else if (key == '\r' || key == '\n') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_INSPECT_REPLAY, &log, compat_expect);
                    } else if (key == ' ') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_STEP, &log, compat_expect);
                    } else if (key == 'p' || key == 'P') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_TOGGLE_PAUSE, &log, compat_expect);
                    } else if (key == 'r' || key == 'R') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_REPLAY_REWIND, &log, compat_expect);
                    }
                } else if (ui.screen == CLIENT_UI_TOOLS) {
                    if (key == 'b' || key == 'B') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_BACK, &log, compat_expect);
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
                    } else if (key == 'a' || key == 'A') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_ACCESSIBILITY_NEXT, &log, compat_expect);
                    } else if (key == 'k' || key == 'K') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_KEYBIND_NEXT, &log, compat_expect);
                    } else if (key == 'd' || key == 'D') {
                        client_ui_apply_action(&ui, CLIENT_ACTION_DEBUG_TOGGLE, &log, compat_expect);
                    }
                }
            }
            if (ev.type == DSYS_EVENT_TEXT_INPUT) {
                if (ui.console_active) {
                    client_console_append_text(&ui, ev.payload.text.text);
                }
            }
            if (!headless && ev.type == DSYS_EVENT_WINDOW_RESIZED) {
                dsys_window_get_framebuffer_size(win, &fb_w, &fb_h);
                if (fb_w > 0 && fb_h > 0) {
                    d_gfx_resize(fb_w, fb_h);
                }
            }
        }
        client_ui_sync_events(&ui);
        if (ui.screen == CLIENT_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = CLIENT_UI_MAIN_MENU;
            }
        }
        if (script_ready && ui.screen != CLIENT_UI_LOADING) {
            const char* token = dom_app_ui_script_next(&script);
            if (token) {
                client_ui_apply_action(&ui, client_ui_action_from_token(token), &log, compat_expect);
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
    static dom_mp0_state state;
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
    const char* accessibility_preset_path = 0;
    const char* locale_id = 0;
    const char* locale_packs[16];
    int locale_pack_count = 0;
    const char* renderer = 0;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    dom_app_ui_run_config ui_run;
    client_ui_settings ui_settings;
    dom_app_ui_event_log ui_log;
    int ui_log_open = 0;
    dom_app_ui_locale_table locale_table;
    int locale_active = 0;
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
    dom_app_ui_locale_table_init(&locale_table);
    locale_active = 0;
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
        if (strncmp(argv[i], "--accessibility-preset=", 24) == 0) {
            accessibility_preset_path = argv[i] + 24;
            continue;
        }
        if (strcmp(argv[i], "--accessibility-preset") == 0 && i + 1 < argc) {
            accessibility_preset_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--locale=", 9) == 0) {
            locale_id = argv[i] + 9;
            continue;
        }
        if (strcmp(argv[i], "--locale") == 0 && i + 1 < argc) {
            locale_id = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--locale-pack=", 14) == 0) {
            if (locale_pack_count >= (int)(sizeof(locale_packs) / sizeof(locale_packs[0]))) {
                fprintf(stderr, "client: too many --locale-pack entries\n");
                return D_APP_EXIT_USAGE;
            }
            locale_packs[locale_pack_count++] = argv[i] + 14;
            continue;
        }
        if (strcmp(argv[i], "--locale-pack") == 0 && i + 1 < argc) {
            if (locale_pack_count >= (int)(sizeof(locale_packs) / sizeof(locale_packs[0]))) {
                fprintf(stderr, "client: too many --locale-pack entries\n");
                return D_APP_EXIT_USAGE;
            }
            locale_packs[locale_pack_count++] = argv[i + 1];
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

    if (accessibility_preset_path) {
        dom_app_ui_accessibility_preset preset;
        char err[128];
        dom_app_ui_accessibility_preset_init(&preset);
        if (!dom_app_ui_accessibility_load_file(&preset, accessibility_preset_path,
                                                err, sizeof(err))) {
            fprintf(stderr, "client: %s\n", err[0] ? err : "invalid accessibility preset");
            return D_APP_EXIT_USAGE;
        }
        client_apply_accessibility(&ui_settings, &preset);
    }
    if (locale_pack_count > 0) {
        int p;
        char err[128];
        if (!locale_id || !locale_id[0]) {
            fprintf(stderr, "client: --locale is required with --locale-pack\n");
            return D_APP_EXIT_USAGE;
        }
        for (p = 0; p < locale_pack_count; ++p) {
            if (!dom_app_ui_locale_table_load_pack(&locale_table,
                                                   locale_packs[p],
                                                   locale_id,
                                                   err,
                                                   sizeof(err))) {
                fprintf(stderr, "client: %s\n", err[0] ? err : "locale load failed");
                return D_APP_EXIT_USAGE;
            }
        }
        ui_settings.locale = &locale_table;
        locale_active = 1;
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
    if (want_status || control_enable) {
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
        if (!control_loaded && !control_enable) {
            if (dom_control_caps_init(&control_caps, control_registry_path) == DOM_CONTROL_OK) {
                control_loaded = 1;
            }
        }
        print_build_info("client", DOMINIUM_GAME_VERSION);
        if (control_loaded) {
            print_control_caps(&control_caps);
            dom_control_caps_free(&control_caps);
        }
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return 0;
    }
    if (want_status) {
        if (!control_loaded) {
            if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
                fprintf(stderr, "client: failed to load control registry: %s\n", control_registry_path);
                if (locale_active) {
                    dom_app_ui_locale_table_free(&locale_table);
                }
                return D_APP_EXIT_FAILURE;
            }
            control_loaded = 1;
        }
        print_control_caps(&control_caps);
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
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
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_FAILURE;
        }
        if (want_snapshot) {
            fprintf(stderr, "client: snapshot metadata unsupported\n");
            dom_app_ro_close(&ro);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (want_events) {
            fprintf(stderr, "client: event stream unsupported\n");
            dom_app_ro_close(&ro);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_client_ro_view_model_init(&view);
        if (!dom_client_ro_view_model_load(&view, &ro)) {
            fprintf(stderr, "client: core info unavailable\n");
            dom_app_ro_close(&ro);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_FAILURE;
        }
        if (!view.has_tree) {
            fprintf(stderr, "client: topology unsupported\n");
            dom_app_ro_close(&ro);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        dom_app_ro_print_topology_bundle(output_format,
                                         &view.core_info,
                                         "packages_tree",
                                         view.nodes,
                                         view.tree_info.count,
                                         view.tree_info.truncated);
        dom_app_ro_close(&ro);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
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
                if (locale_active) {
                    dom_app_ui_locale_table_free(&locale_table);
                }
                return res;
            }
        }
        printf("client: unknown command '%s'\\n", cmd);
        print_help();
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return D_APP_EXIT_USAGE;
    }
    if (ui_mode == DOM_APP_UI_TUI) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        {
            int res = client_run_tui(&ui_run, &ui_settings, timing_mode, frame_cap_ms, &compat_expect);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return res;
        }
    }
    if (window_cfg.enabled) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        {
            int res = client_run_gui(&ui_run, &ui_settings, &window_cfg,
                                     timing_mode, frame_cap_ms, &compat_expect);
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return res;
        }
    }
    if (want_mp0) {
        if (!client_validate_renderer(renderer)) {
            if (control_loaded) {
                dom_control_caps_free(&control_caps);
            }
            if (locale_active) {
                dom_app_ui_locale_table_free(&locale_table);
            }
            return D_APP_EXIT_UNAVAILABLE;
        }
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return mp0_run_local_client();
    }
    printf("Dominium client stub. Use --help.\\n");
    if (control_loaded) {
        dom_control_caps_free(&control_caps);
    }
    if (locale_active) {
        dom_app_ui_locale_table_free(&locale_table);
    }
    return 0;
}

int main(int argc, char** argv)
{
    return client_main(argc, argv);
}
