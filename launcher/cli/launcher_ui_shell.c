/*
Launcher UI shell implementation.
*/
#include "launcher_ui_shell.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <io.h>
#include <sys/stat.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#endif

#include "domino/build_info.h"
#include "domino/gfx.h"
#include "domino/render/backend_detect.h"
#include "domino/system/dsys.h"
#include "domino/system/d_system.h"
#include "domino/tui/tui.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/readonly_adapter.h"

#define LAUNCHER_UI_MENU_COUNT 6
#define LAUNCHER_UI_STATUS_MAX 160
#define LAUNCHER_UI_LABEL_MAX 96
#define LAUNCHER_UI_RENDERER_MAX 8

typedef enum launcher_ui_screen {
    LAUNCHER_UI_LOADING = 0,
    LAUNCHER_UI_MENU,
    LAUNCHER_UI_SETTINGS
} launcher_ui_screen;

typedef enum launcher_ui_action {
    LAUNCHER_ACTION_NONE = 0,
    LAUNCHER_ACTION_NEW_WORLD,
    LAUNCHER_ACTION_LOAD_WORLD,
    LAUNCHER_ACTION_INSPECT_REPLAY,
    LAUNCHER_ACTION_TOOLS,
    LAUNCHER_ACTION_SETTINGS,
    LAUNCHER_ACTION_EXIT,
    LAUNCHER_ACTION_BACK,
    LAUNCHER_ACTION_RENDERER_NEXT,
    LAUNCHER_ACTION_SCALE_UP,
    LAUNCHER_ACTION_SCALE_DOWN,
    LAUNCHER_ACTION_PALETTE_TOGGLE,
    LAUNCHER_ACTION_LOG_NEXT,
    LAUNCHER_ACTION_DEBUG_TOGGLE
} launcher_ui_action;

typedef struct launcher_renderer_entry {
    char name[16];
    int supported;
} launcher_renderer_entry;

typedef struct launcher_renderer_list {
    launcher_renderer_entry entries[LAUNCHER_UI_RENDERER_MAX];
    uint32_t count;
} launcher_renderer_list;

typedef struct launcher_ui_state {
    launcher_ui_screen screen;
    int exit_requested;
    int loading_ticks;
    int menu_index;
    char action_status[LAUNCHER_UI_STATUS_MAX];
    char pack_status[LAUNCHER_UI_STATUS_MAX];
    char template_status[LAUNCHER_UI_STATUS_MAX];
    char determinism_status[32];
    uint32_t package_count;
    uint32_t instance_count;
    char testx_status[32];
    char seed_status[32];
    launcher_ui_settings settings;
    launcher_renderer_list renderers;
} launcher_ui_state;

static const char* g_launcher_menu_items[LAUNCHER_UI_MENU_COUNT] = {
    "New World",
    "Load World",
    "Inspect Replay",
    "Tools",
    "Settings",
    "Exit"
};

static const char* launcher_palette_name(int palette)
{
    return palette ? "high-contrast" : "default";
}

static const char* launcher_log_level_name(int level)
{
    switch (level) {
    case 1: return "warn";
    case 2: return "error";
    default: break;
    }
    return "info";
}

void launcher_ui_settings_init(launcher_ui_settings* settings)
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

void launcher_ui_settings_format_lines(const launcher_ui_settings* settings,
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
             "palette=%s", launcher_palette_name(settings->palette));
    snprintf(line0 + (line_stride * count++), line_stride,
             "input_bindings=default");
    snprintf(line0 + (line_stride * count++), line_stride,
             "log_verbosity=%s", launcher_log_level_name(settings->log_level));
    snprintf(line0 + (line_stride * count++), line_stride,
             "debug_ui=%s", settings->debug_ui ? "enabled" : "disabled");
    if (out_count) {
        *out_count = count;
    }
}

int launcher_ui_execute_command(const char* cmd,
                                const launcher_ui_settings* settings,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text)
{
    (void)settings;
    if (status && status_cap > 0u) {
        status[0] = '\0';
    }
    if (!cmd || !cmd[0]) {
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher: missing command");
        }
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "new-world") == 0 || strcmp(cmd, "start") == 0) {
        dom_app_ui_event_log_emit(log, "launcher.new_world", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_new_world=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "launcher: new-world unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "load-world") == 0 || strcmp(cmd, "load-save") == 0) {
        dom_app_ui_event_log_emit(log, "launcher.load_world", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_load_world=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "launcher: load-world unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "inspect-replay") == 0) {
        dom_app_ui_event_log_emit(log, "launcher.inspect_replay", "result=unavailable");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_inspect_replay=unavailable");
        }
        if (emit_text) {
            fprintf(stderr, "launcher: inspect-replay unavailable\n");
        }
        return D_APP_EXIT_UNAVAILABLE;
    }
    if (strcmp(cmd, "tools") == 0) {
        dom_app_ui_event_log_emit(log, "launcher.tools", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_tools=ok");
        }
        if (emit_text) {
            printf("launcher_tools=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "settings") == 0) {
        char lines[LAUNCHER_UI_MENU_COUNT][LAUNCHER_UI_LABEL_MAX];
        int count = 0;
        int i;
        launcher_ui_settings_format_lines(settings, (char*)lines,
                                          LAUNCHER_UI_MENU_COUNT,
                                          LAUNCHER_UI_LABEL_MAX, &count);
        dom_app_ui_event_log_emit(log, "launcher.settings", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_settings=ok");
        }
        if (emit_text) {
            printf("launcher_settings=ok\n");
            for (i = 0; i < count; ++i) {
                printf("%s\n", lines[i]);
            }
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "exit") == 0) {
        dom_app_ui_event_log_emit(log, "launcher.exit", "result=ok");
        if (status && status_cap > 0u) {
            snprintf(status, status_cap, "launcher_exit=ok");
        }
        if (emit_text) {
            printf("launcher_exit=ok\n");
        }
        return D_APP_EXIT_OK;
    }
    if (status && status_cap > 0u) {
        snprintf(status, status_cap, "launcher: unknown command '%s'", cmd);
    }
    return D_APP_EXIT_USAGE;
}

static void launcher_renderer_list_init(launcher_renderer_list* list)
{
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    uint32_t count;
    uint32_t i;
    if (!list) {
        return;
    }
    memset(list, 0, sizeof(*list));
    count = d_gfx_detect_backends(infos, (uint32_t)(sizeof(infos) / sizeof(infos[0])));
    for (i = 0u; i < count && list->count < LAUNCHER_UI_RENDERER_MAX; ++i) {
        launcher_renderer_entry* entry = &list->entries[list->count];
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

static const char* launcher_renderer_default(const launcher_renderer_list* list)
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

static void launcher_settings_set_renderer(launcher_ui_settings* settings, const char* name)
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

static const char* launcher_env_or_default(const char* key, const char* fallback)
{
    const char* value = getenv(key);
    if (value && value[0]) {
        return value;
    }
    return fallback;
}

static uint32_t launcher_count_pack_manifests(const char* root)
{
    uint32_t count = 0u;
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
            char path[260];
            char manifest[260];
            struct stat st;
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }
            snprintf(path, sizeof(path), "%s/%s", root, entry->d_name);
            if (stat(path, &st) != 0) {
                continue;
            }
            if (!S_ISDIR(st.st_mode)) {
                continue;
            }
            snprintf(manifest, sizeof(manifest), "%s/pack_manifest.json", path);
            {
                FILE* f = fopen(manifest, "r");
                if (f) {
                    fclose(f);
                    count += 1u;
                }
            }
        }
        closedir(dir);
    }
#endif
    return count;
}

static void launcher_ui_collect_loading(launcher_ui_state* state)
{
    dom_app_readonly_adapter ro;
    dom_app_compat_report report;
    dom_app_ro_core_info core;
    uint32_t pack_count = 0u;
    if (!state) {
        return;
    }
    state->package_count = 0u;
    state->instance_count = 0u;
    pack_count = launcher_count_pack_manifests("data/packs");
    snprintf(state->pack_status, sizeof(state->pack_status),
             "pack_discovery=ok packs=%u", (unsigned int)pack_count);
    dom_app_ro_init(&ro);
    dom_app_compat_report_init(&report, "launcher");
    if (dom_app_ro_open(&ro, 0, &report)) {
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
    strncpy(state->testx_status,
            launcher_env_or_default("DOM_TESTX_STATUS", "unknown"),
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

static void launcher_ui_state_init(launcher_ui_state* state,
                                   const launcher_ui_settings* settings,
                                   d_app_timing_mode timing_mode)
{
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    state->screen = LAUNCHER_UI_LOADING;
    state->menu_index = 0;
    state->exit_requested = 0;
    state->loading_ticks = 0;
    state->action_status[0] = '\0';
    launcher_renderer_list_init(&state->renderers);
    if (settings) {
        state->settings = *settings;
    } else {
        launcher_ui_settings_init(&state->settings);
    }
    if (state->settings.renderer[0] == '\0') {
        launcher_settings_set_renderer(&state->settings,
                                       launcher_renderer_default(&state->renderers));
    }
    snprintf(state->template_status, sizeof(state->template_status),
             "template_registry=unavailable");
    snprintf(state->determinism_status, sizeof(state->determinism_status),
             "determinism=%s",
             (timing_mode == D_APP_TIMING_INTERACTIVE) ? "interactive" : "deterministic");
    launcher_ui_collect_loading(state);
}

static void launcher_ui_cycle_renderer(launcher_ui_state* state)
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
            launcher_settings_set_renderer(&state->settings,
                                           state->renderers.entries[next].name);
            return;
        }
    }
    launcher_settings_set_renderer(&state->settings, state->renderers.entries[0].name);
}

static void launcher_ui_apply_action(launcher_ui_state* state,
                                     launcher_ui_action action,
                                     dom_app_ui_event_log* log)
{
    int res;
    if (!state) {
        return;
    }
    switch (action) {
    case LAUNCHER_ACTION_NEW_WORLD:
        res = launcher_ui_execute_command("new-world", &state->settings, log,
                                          state->action_status, sizeof(state->action_status), 0);
        (void)res;
        break;
    case LAUNCHER_ACTION_LOAD_WORLD:
        res = launcher_ui_execute_command("load-world", &state->settings, log,
                                          state->action_status, sizeof(state->action_status), 0);
        (void)res;
        break;
    case LAUNCHER_ACTION_INSPECT_REPLAY:
        res = launcher_ui_execute_command("inspect-replay", &state->settings, log,
                                          state->action_status, sizeof(state->action_status), 0);
        (void)res;
        break;
    case LAUNCHER_ACTION_TOOLS:
        res = launcher_ui_execute_command("tools", &state->settings, log,
                                          state->action_status, sizeof(state->action_status), 0);
        (void)res;
        break;
    case LAUNCHER_ACTION_SETTINGS:
        state->screen = LAUNCHER_UI_SETTINGS;
        launcher_ui_execute_command("settings", &state->settings, log,
                                    state->action_status, sizeof(state->action_status), 0);
        break;
    case LAUNCHER_ACTION_EXIT:
        launcher_ui_execute_command("exit", &state->settings, log,
                                    state->action_status, sizeof(state->action_status), 0);
        state->exit_requested = 1;
        break;
    case LAUNCHER_ACTION_BACK:
        state->screen = LAUNCHER_UI_MENU;
        break;
    case LAUNCHER_ACTION_RENDERER_NEXT:
        launcher_ui_cycle_renderer(state);
        snprintf(state->action_status, sizeof(state->action_status), "settings_renderer=%s",
                 state->settings.renderer);
        break;
    case LAUNCHER_ACTION_SCALE_UP:
        if (state->settings.ui_scale_percent < 150) {
            state->settings.ui_scale_percent += 25;
        }
        snprintf(state->action_status, sizeof(state->action_status), "settings_ui_scale=%d%%",
                 state->settings.ui_scale_percent);
        break;
    case LAUNCHER_ACTION_SCALE_DOWN:
        if (state->settings.ui_scale_percent > 75) {
            state->settings.ui_scale_percent -= 25;
        }
        snprintf(state->action_status, sizeof(state->action_status), "settings_ui_scale=%d%%",
                 state->settings.ui_scale_percent);
        break;
    case LAUNCHER_ACTION_PALETTE_TOGGLE:
        state->settings.palette = state->settings.palette ? 0 : 1;
        snprintf(state->action_status, sizeof(state->action_status), "settings_palette=%s",
                 launcher_palette_name(state->settings.palette));
        break;
    case LAUNCHER_ACTION_LOG_NEXT:
        state->settings.log_level = (state->settings.log_level + 1) % 3;
        snprintf(state->action_status, sizeof(state->action_status), "settings_log=%s",
                 launcher_log_level_name(state->settings.log_level));
        break;
    case LAUNCHER_ACTION_DEBUG_TOGGLE:
        state->settings.debug_ui = state->settings.debug_ui ? 0 : 1;
        snprintf(state->action_status, sizeof(state->action_status), "settings_debug=%s",
                 state->settings.debug_ui ? "enabled" : "disabled");
        break;
    default:
        break;
    }
}

static launcher_ui_action launcher_ui_action_from_token(const char* token)
{
    if (!token || !token[0]) {
        return LAUNCHER_ACTION_NONE;
    }
    if (strcmp(token, "new-world") == 0 || strcmp(token, "start") == 0) return LAUNCHER_ACTION_NEW_WORLD;
    if (strcmp(token, "load-world") == 0 || strcmp(token, "load") == 0 || strcmp(token, "load-save") == 0) {
        return LAUNCHER_ACTION_LOAD_WORLD;
    }
    if (strcmp(token, "replay") == 0 || strcmp(token, "inspect-replay") == 0) return LAUNCHER_ACTION_INSPECT_REPLAY;
    if (strcmp(token, "tools") == 0) return LAUNCHER_ACTION_TOOLS;
    if (strcmp(token, "settings") == 0) return LAUNCHER_ACTION_SETTINGS;
    if (strcmp(token, "exit") == 0 || strcmp(token, "quit") == 0) return LAUNCHER_ACTION_EXIT;
    if (strcmp(token, "back") == 0) return LAUNCHER_ACTION_BACK;
    if (strcmp(token, "renderer-next") == 0) return LAUNCHER_ACTION_RENDERER_NEXT;
    if (strcmp(token, "scale-up") == 0) return LAUNCHER_ACTION_SCALE_UP;
    if (strcmp(token, "scale-down") == 0) return LAUNCHER_ACTION_SCALE_DOWN;
    if (strcmp(token, "palette") == 0) return LAUNCHER_ACTION_PALETTE_TOGGLE;
    if (strcmp(token, "log-next") == 0) return LAUNCHER_ACTION_LOG_NEXT;
    if (strcmp(token, "debug-toggle") == 0) return LAUNCHER_ACTION_DEBUG_TOGGLE;
    return LAUNCHER_ACTION_NONE;
}

static void launcher_gui_draw_text(d_gfx_cmd_buffer* buf, int x, int y,
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

static void launcher_gui_draw_menu(d_gfx_cmd_buffer* buf,
                                   const launcher_ui_state* state,
                                   int x,
                                   int y,
                                   int line_h,
                                   d_gfx_color text,
                                   d_gfx_color highlight)
{
    int i;
    d_gfx_draw_rect_cmd rect;
    if (!buf || !state) {
        return;
    }
    for (i = 0; i < LAUNCHER_UI_MENU_COUNT; ++i) {
        int line_y = y + i * line_h;
        if (i == state->menu_index) {
            rect.x = x - 8;
            rect.y = line_y - 2;
            rect.w = 360;
            rect.h = line_h;
            rect.color = highlight;
            d_gfx_cmd_draw_rect(buf, &rect);
        }
        launcher_gui_draw_text(buf, x, line_y, g_launcher_menu_items[i], text);
    }
}

static void launcher_gui_render(const launcher_ui_state* state,
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
    launcher_gui_draw_text(buf, 20, y, "Dominium Launcher", text);
    y += line_h;
    if (state->screen == LAUNCHER_UI_LOADING) {
        char line[LAUNCHER_UI_STATUS_MAX];
        const dom_build_info_v1* build = dom_build_info_v1_get();
        snprintf(line, sizeof(line), "engine=%s", DOMINO_VERSION_STRING);
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "game=%s", DOMINIUM_GAME_VERSION);
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "build_number=%u", (unsigned int)DOM_BUILD_NUMBER);
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        snprintf(line, sizeof(line), "sim_schema_id=%llu", (unsigned long long)dom_sim_schema_id());
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        if (build) {
            snprintf(line, sizeof(line), "sim_schema_version=%u", (unsigned int)build->sim_schema_version);
            launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
            snprintf(line, sizeof(line), "content_schema_version=%u", (unsigned int)build->content_schema_version);
            launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        } else {
            launcher_gui_draw_text(buf, 20, y, "sim_schema_version=unknown", text); y += line_h;
            launcher_gui_draw_text(buf, 20, y, "content_schema_version=unknown", text); y += line_h;
        }
        launcher_gui_draw_text(buf, 20, y, "protocol_law_targets=LAW_TARGETS@1.4.0", text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, "protocol_control_caps=CONTROL_CAPS@1.0.0", text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, "protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0", text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, state->determinism_status, text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, state->template_status, text); y += line_h;
        snprintf(line, sizeof(line), "testx=%s", state->testx_status);
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, state->pack_status, text); y += line_h;
        snprintf(line, sizeof(line), "seed=%s", state->seed_status);
        launcher_gui_draw_text(buf, 20, y, line, text); y += line_h;
        launcher_gui_draw_text(buf, 20, y, "Loading complete. Press Enter to continue.", text);
        return;
    }
    if (state->screen == LAUNCHER_UI_MENU) {
        y += line_h;
        launcher_gui_draw_menu(buf, state, 20, y, line_h, text, highlight);
        y += (LAUNCHER_UI_MENU_COUNT + 1) * line_h;
        if (state->action_status[0]) {
            launcher_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
    if (state->screen == LAUNCHER_UI_SETTINGS) {
        char lines[LAUNCHER_UI_MENU_COUNT][LAUNCHER_UI_LABEL_MAX];
        int count = 0;
        int i;
        y += line_h;
        launcher_ui_settings_format_lines(&state->settings, (char*)lines,
                                          LAUNCHER_UI_MENU_COUNT,
                                          LAUNCHER_UI_LABEL_MAX, &count);
        for (i = 0; i < count; ++i) {
            launcher_gui_draw_text(buf, 20, y, lines[i], text);
            y += line_h;
        }
        y += line_h;
        launcher_gui_draw_text(buf, 20, y, "Keys: R renderer, +/- scale, P palette, L log, D debug, B back", text);
        y += line_h;
        if (state->action_status[0]) {
            launcher_gui_draw_text(buf, 20, y, state->action_status, text);
        }
        return;
    }
}

int launcher_ui_run_tui(const dom_app_ui_run_config* run_cfg,
                        const launcher_ui_settings* settings,
                        d_app_timing_mode timing_mode,
                        uint32_t frame_cap_ms)
{
    d_tui_context* tui = 0;
    d_tui_widget* root = 0;
    d_tui_widget* title = 0;
    launcher_ui_state ui;
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

    launcher_ui_state_init(&ui, settings, timing_mode);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "launcher: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "launcher: dsys_init failed (%s)\n", dsys_last_error_text());
        dom_app_ui_event_log_close(&log);
        return D_APP_EXIT_FAILURE;
    }
    dsys_ready = 1;
    if (dsys_terminal_init() != 0) {
        fprintf(stderr, "launcher: terminal unavailable\n");
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
                launcher_ui_apply_action(&ui, launcher_ui_action_from_token(token), &log);
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
                    launcher_ui_apply_action(&ui, LAUNCHER_ACTION_EXIT, &log);
                } else if (ui.screen == LAUNCHER_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = LAUNCHER_UI_MENU;
                } else if (ui.screen == LAUNCHER_UI_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.menu_index = (ui.menu_index > 0) ? (ui.menu_index - 1) : (LAUNCHER_UI_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.menu_index = (ui.menu_index + 1) % LAUNCHER_UI_MENU_COUNT;
                    } else if (key == '\r' || key == '\n') {
                        launcher_ui_apply_action(&ui, (launcher_ui_action)(ui.menu_index + 1), &log);
                    }
                } else if (ui.screen == LAUNCHER_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_BACK, &log);
                    } else if (key == 'r' || key == 'R') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_RENDERER_NEXT, &log);
                    } else if (key == '+' || key == '=') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_SCALE_UP, &log);
                    } else if (key == '-' || key == '_') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_SCALE_DOWN, &log);
                    } else if (key == 'p' || key == 'P') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_PALETTE_TOGGLE, &log);
                    } else if (key == 'l' || key == 'L') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_LOG_NEXT, &log);
                    } else if (key == 'd' || key == 'D') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_DEBUG_TOGGLE, &log);
                    }
                }
            }
        }
        if (ui.screen == LAUNCHER_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = LAUNCHER_UI_MENU;
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
            fprintf(stderr, "launcher: tui init failed\n");
            goto cleanup;
        }
        root = d_tui_panel(tui, D_TUI_LAYOUT_VERTICAL);
        title = d_tui_label(tui, "Dominium Launcher TUI");
        d_tui_widget_add(root, title);
        if (ui.screen == LAUNCHER_UI_LOADING) {
            char line[LAUNCHER_UI_STATUS_MAX];
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
            d_tui_widget_add(root, d_tui_label(tui, ui.determinism_status));
            d_tui_widget_add(root, d_tui_label(tui, ui.template_status));
            snprintf(line, sizeof(line), "testx=%s", ui.testx_status);
            d_tui_widget_add(root, d_tui_label(tui, line));
            d_tui_widget_add(root, d_tui_label(tui, ui.pack_status));
            snprintf(line, sizeof(line), "seed=%s", ui.seed_status);
            d_tui_widget_add(root, d_tui_label(tui, line));
            d_tui_widget_add(root, d_tui_label(tui, "Press Enter to continue"));
        } else if (ui.screen == LAUNCHER_UI_MENU) {
            int i;
            for (i = 0; i < LAUNCHER_UI_MENU_COUNT; ++i) {
                d_tui_widget* btn = d_tui_button(tui, g_launcher_menu_items[i], 0, 0);
                if (btn) {
                    d_tui_widget_add(root, btn);
                }
            }
            if (ui.action_status[0]) {
                d_tui_widget_add(root, d_tui_label(tui, ui.action_status));
            }
        } else if (ui.screen == LAUNCHER_UI_SETTINGS) {
            char lines[LAUNCHER_UI_MENU_COUNT][LAUNCHER_UI_LABEL_MAX];
            int count = 0;
            int i;
            launcher_ui_settings_format_lines(&ui.settings, (char*)lines,
                                              LAUNCHER_UI_MENU_COUNT,
                                              LAUNCHER_UI_LABEL_MAX, &count);
            for (i = 0; i < count; ++i) {
                d_tui_widget_add(root, d_tui_label(tui, lines[i]));
            }
            d_tui_widget_add(root, d_tui_label(tui, "R renderer, +/- scale, P palette, L log, D debug, B back"));
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
            fprintf(stderr, "launcher: shutdown=%s\n",
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

int launcher_ui_run_gui(const dom_app_ui_run_config* run_cfg,
                        const launcher_ui_settings* settings,
                        d_app_timing_mode timing_mode,
                        uint32_t frame_cap_ms)
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
    launcher_ui_state ui;
    dom_app_ui_script script;
    dom_app_ui_event_log log;
    int script_ready = 0;
    const char* renderer = 0;
    int headless = run_cfg && run_cfg->headless_set ? run_cfg->headless : 0;
    int max_frames = run_cfg && run_cfg->max_frames_set ? (int)run_cfg->max_frames : 0;
    int frame_count = 0;

    launcher_ui_state_init(&ui, settings, timing_mode);
    dom_app_ui_event_log_init(&log);
    if (run_cfg && run_cfg->log_set) {
        if (!dom_app_ui_event_log_open(&log, run_cfg->log_path)) {
            fprintf(stderr, "launcher: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    if (run_cfg && run_cfg->script_set) {
        dom_app_ui_script_init(&script, run_cfg->script);
        script_ready = 1;
    }

    renderer = ui.settings.renderer[0] ? ui.settings.renderer : launcher_renderer_default(&ui.renderers);
    if (headless && renderer && strcmp(renderer, "null") != 0) {
        fprintf(stderr, "launcher: headless forces null renderer (requested %s)\n", renderer);
        renderer = "null";
        launcher_settings_set_renderer(&ui.settings, renderer);
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "launcher: dsys_init failed (%s)\n", dsys_last_error_text());
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
            fprintf(stderr, "launcher: window creation failed (%s)\n", dsys_last_error_text());
            goto cleanup;
        }
        dsys_window_show(win);
        d_system_set_native_window_handle(dsys_window_get_native_handle(win));
    } else {
        d_system_set_native_window_handle(0);
    }

    if (!d_gfx_init(renderer)) {
        fprintf(stderr, "launcher: renderer init failed\n");
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
                launcher_ui_apply_action(&ui, launcher_ui_action_from_token(token), &log);
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
                    launcher_ui_apply_action(&ui, LAUNCHER_ACTION_EXIT, &log);
                } else if (ui.screen == LAUNCHER_UI_LOADING && (key == '\r' || key == '\n')) {
                    ui.screen = LAUNCHER_UI_MENU;
                } else if (ui.screen == LAUNCHER_UI_MENU) {
                    if (key == 'w' || key == 'W') {
                        ui.menu_index = (ui.menu_index > 0) ? (ui.menu_index - 1) : (LAUNCHER_UI_MENU_COUNT - 1);
                    } else if (key == 's' || key == 'S') {
                        ui.menu_index = (ui.menu_index + 1) % LAUNCHER_UI_MENU_COUNT;
                    } else if (key == '\r' || key == '\n' || key == ' ') {
                        launcher_ui_apply_action(&ui, (launcher_ui_action)(ui.menu_index + 1), &log);
                    }
                } else if (ui.screen == LAUNCHER_UI_SETTINGS) {
                    if (key == 'b' || key == 'B') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_BACK, &log);
                    } else if (key == 'r' || key == 'R') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_RENDERER_NEXT, &log);
                    } else if (key == '+' || key == '=') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_SCALE_UP, &log);
                    } else if (key == '-' || key == '_') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_SCALE_DOWN, &log);
                    } else if (key == 'p' || key == 'P') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_PALETTE_TOGGLE, &log);
                    } else if (key == 'l' || key == 'L') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_LOG_NEXT, &log);
                    } else if (key == 'd' || key == 'D') {
                        launcher_ui_apply_action(&ui, LAUNCHER_ACTION_DEBUG_TOGGLE, &log);
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
        if (ui.screen == LAUNCHER_UI_LOADING) {
            ui.loading_ticks += 1;
            if (ui.loading_ticks > 1) {
                ui.screen = LAUNCHER_UI_MENU;
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
                launcher_gui_render(&ui, buf, fb_w, fb_h);
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
            fprintf(stderr, "launcher: shutdown=%s\n",
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
