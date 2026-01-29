/*
Stub launcher CLI entrypoint.
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
#include "dominium/app/ui_event_log.h"
#include "dominium/app/ui_presentation.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#if defined(_WIN32)
#include <direct.h>
#else
#include <unistd.h>
#endif

#include "launcher/launcher.h"
#include "launcher/launcher_profile.h"
#include "launcher_ui_shell.h"

static void print_version(const char* product_version)
{
    printf("launcher %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    dom_app_build_info info;
    dom_app_build_info_init(&info, product_name, product_version);
    dom_app_print_build_info(&info);
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

static void launcher_print_help(void)
{
    printf("usage: launcher [--help] [--version] [--build-info] [--status] [--smoke] [--selftest] <command>\n");
    printf("options:\n");
    printf("  --build-info                 Show build info + control capabilities\n");
    printf("  --status                     Show active control layers\n");
    printf("  --smoke                      Run deterministic CLI smoke\n");
    printf("  --selftest                   Alias for --smoke\n");
    printf("  --ui=none|tui|gui            Select UI shell (optional)\n");
    printf("  --ui-script <list>           Auto-run UI actions (comma-separated)\n");
    printf("  --ui-frames <n>              Max UI frames before exit (headless friendly)\n");
    printf("  --ui-log <path>              Write UI event log (deterministic)\n");
    printf("  --headless                   Run GUI without a native window (null renderer)\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\n");
    printf("  --interactive               Use variable timestep (wall-clock)\n");
    printf("  --renderer <name>           Select renderer (explicit; no fallback)\n");
    printf("  --ui-scale <pct>            UI scale percent (e.g. 100, 125, 150)\n");
    printf("  --palette <name>            UI palette (default|high-contrast)\n");
    printf("  --log-verbosity <level>     Logging verbosity (info|warn|error)\n");
    printf("  --accessibility-preset <path> Apply accessibility preset (data-only)\n");
    printf("  --locale <id>               Select localization id (e.g. en_US)\n");
    printf("  --locale-pack <path>        Add localization pack root (can repeat)\n");
    printf("  --debug-ui                  Enable debug UI flags\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("commands:\n");
    printf("  version         Show launcher version\n");
    printf("  list-profiles   List known profiles\n");
    printf("  capabilities    Report platform + renderer availability\n");
    printf("  new-world       Create a new world (templates; may be unavailable)\n");
    printf("  load-world      Load a world save (may be unavailable)\n");
    printf("  inspect-replay  Inspect replay (may be unavailable)\n");
    printf("  ops <args>      Install/instance operations (delegates to ops_cli)\n");
    printf("  share <args>    Bundle export/import/inspect (delegates to share_cli)\n");
    printf("  bugreport <args> Bundle reproducible bug reports (delegates to bugreport_cli)\n");
    printf("  tools           Open tools shell (handoff)\n");
    printf("  settings        Show current UI settings\n");
    printf("  exit            Exit launcher\n");
}

static void launcher_print_profiles(void)
{
    int count;
    int i;

    launcher_profile_load_all();
    count = launcher_profile_count();
    if (count <= 0) {
        printf("profiles: none\n");
        return;
    }

    for (i = 0; i < count; ++i) {
        const launcher_profile* p = launcher_profile_get(i);
        if (!p) {
            continue;
        }
        printf("%s\t%s\n", p->id, p->name);
    }
}

static int launcher_is_abs_path(const char* path)
{
    if (!path || !path[0]) {
        return 0;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return 1;
    }
    if (isalpha((unsigned char)path[0]) && path[1] == ':' &&
        (path[2] == '/' || path[2] == '\\')) {
        return 1;
    }
    return 0;
}

static int launcher_file_exists(const char* path)
{
    FILE* f = 0;
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

static int launcher_get_cwd(char* buf, size_t cap)
{
#if defined(_WIN32)
    return (_getcwd(buf, (int)cap) != NULL);
#else
    return (getcwd(buf, cap) != NULL);
#endif
}

static void launcher_normalize_path(char* path)
{
    char* p;
    if (!path) {
        return;
    }
    for (p = path; *p; ++p) {
        if (*p == '\\') {
            *p = '/';
        }
    }
}

static int launcher_pop_dir(char* path)
{
    size_t len;
    char* slash;
    if (!path || !path[0]) {
        return 0;
    }
    len = strlen(path);
    while (len > 0 && path[len - 1] == '/') {
        path[--len] = '\0';
    }
    if (len == 0) {
        return 0;
    }
    if (len == 1 && path[0] == '/') {
        return 0;
    }
    if (len == 3 && path[1] == ':' && path[2] == '/') {
        return 0;
    }
    slash = strrchr(path, '/');
    if (!slash) {
        return 0;
    }
    if (slash == path) {
        path[1] = '\0';
        return 1;
    }
    if (slash == path + 2 && path[1] == ':') {
        slash[1] = '\0';
        return 1;
    }
    *slash = '\0';
    return 1;
}

static int launcher_join_path(char* out, size_t cap, const char* base, const char* rel)
{
    size_t blen;
    int written;
    if (!out || cap == 0u || !base || !rel) {
        return 0;
    }
    blen = strlen(base);
    if (blen > 0 && base[blen - 1] == '/') {
        written = snprintf(out, cap, "%s%s", base, rel);
    } else {
        written = snprintf(out, cap, "%s/%s", base, rel);
    }
    return written > 0 && (size_t)written < cap;
}

static int launcher_find_upward(char* out, size_t cap, const char* rel)
{
    char cwd[512];
    char probe[512];
    if (!launcher_get_cwd(cwd, sizeof(cwd))) {
        return 0;
    }
    launcher_normalize_path(cwd);
    while (1) {
        if (!launcher_join_path(probe, sizeof(probe), cwd, rel)) {
            return 0;
        }
        if (launcher_file_exists(probe)) {
            strncpy(out, probe, cap - 1u);
            out[cap - 1u] = '\0';
            return 1;
        }
        if (!launcher_pop_dir(cwd)) {
            break;
        }
    }
    return 0;
}

static void launcher_resolve_control_registry(char* out, size_t cap, const char* requested)
{
    const char* fallback = "data/registries/control_capabilities.registry";
    const char* path = (requested && requested[0]) ? requested : fallback;
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (launcher_is_abs_path(path)) {
        strncpy(out, path, cap - 1u);
        out[cap - 1u] = '\0';
        return;
    }
    if (launcher_file_exists(path)) {
        strncpy(out, path, cap - 1u);
        out[cap - 1u] = '\0';
        return;
    }
    if (launcher_find_upward(out, cap, path)) {
        return;
    }
    strncpy(out, path, cap - 1u);
    out[cap - 1u] = '\0';
}

static int launcher_parse_ui_scale(const char* text, int* out_value)
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

static int launcher_parse_palette(const char* text, int* out_value)
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

static int launcher_parse_log_level(const char* text, int* out_value)
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

static int launcher_append_quoted(char* buf, size_t cap, const char* arg)
{
    size_t len;
    size_t pos;
    size_t i;
    if (!buf || cap == 0u || !arg) {
        return 0;
    }
    len = strlen(buf);
    if (len + 3u >= cap) {
        return 0;
    }
    pos = len;
    buf[pos++] = ' ';
    buf[pos++] = '"';
    for (i = 0u; arg[i]; ++i) {
        char c = arg[i];
        if (c == '"') {
            if (pos + 2u >= cap) {
                return 0;
            }
            buf[pos++] = '\\';
            buf[pos++] = '"';
            continue;
        }
        if (pos + 1u >= cap) {
            return 0;
        }
        buf[pos++] = c;
    }
    if (pos + 2u >= cap) {
        return 0;
    }
    buf[pos++] = '"';
    buf[pos] = '\0';
    return 1;
}

static int launcher_resolve_ops_script(char* out, size_t cap)
{
    const char* rel = "tools/ops/ops_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (launcher_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, rel, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int launcher_run_ops(int argc, char** argv, int cmd_index)
{
    char script_path[512];
    char cmd[2048];
    int i;
    int rc;
    if (cmd_index < 0 || argc <= cmd_index) {
        return D_APP_EXIT_USAGE;
    }
    if (!launcher_resolve_ops_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "launcher: unable to resolve ops cli path\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "launcher: failed to build ops command\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!launcher_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "launcher: ops command too long\n");
        return D_APP_EXIT_FAILURE;
    }
    for (i = cmd_index + 1; i < argc; ++i) {
        if (!launcher_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "launcher: ops command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "launcher: failed to run ops cli\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static int launcher_resolve_share_script(char* out, size_t cap)
{
    const char* rel = "tools/share/share_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (launcher_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, rel, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int launcher_run_share(int argc, char** argv, int cmd_index)
{
    char script_path[512];
    char cmd[2048];
    int i;
    int rc;
    if (cmd_index < 0 || argc <= cmd_index) {
        return D_APP_EXIT_USAGE;
    }
    if (!launcher_resolve_share_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "launcher: unable to resolve share cli path\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "launcher: failed to build share command\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!launcher_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "launcher: share command too long\n");
        return D_APP_EXIT_FAILURE;
    }
    for (i = cmd_index + 1; i < argc; ++i) {
        if (!launcher_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "launcher: share command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "launcher: failed to run share cli\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static int launcher_resolve_bugreport_script(char* out, size_t cap)
{
    const char* rel = "tools/bugreport/bugreport_cli.py";
    if (!out || cap == 0u) {
        return 0;
    }
    out[0] = '\0';
    if (launcher_find_upward(out, cap, rel)) {
        return 1;
    }
    strncpy(out, rel, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int launcher_run_bugreport(int argc, char** argv, int cmd_index)
{
    char script_path[512];
    char cmd[2048];
    int i;
    int rc;
    if (cmd_index < 0 || argc <= cmd_index) {
        return D_APP_EXIT_USAGE;
    }
    if (!launcher_resolve_bugreport_script(script_path, sizeof(script_path))) {
        fprintf(stderr, "launcher: unable to resolve bugreport cli path\n");
        return D_APP_EXIT_FAILURE;
    }
    if (snprintf(cmd, sizeof(cmd), "python") <= 0) {
        fprintf(stderr, "launcher: failed to build bugreport command\n");
        return D_APP_EXIT_FAILURE;
    }
    if (!launcher_append_quoted(cmd, sizeof(cmd), script_path)) {
        fprintf(stderr, "launcher: bugreport command too long\n");
        return D_APP_EXIT_FAILURE;
    }
    for (i = cmd_index + 1; i < argc; ++i) {
        if (!launcher_append_quoted(cmd, sizeof(cmd), argv[i])) {
            fprintf(stderr, "launcher: bugreport command too long\n");
            return D_APP_EXIT_FAILURE;
        }
    }
    rc = system(cmd);
    if (rc == -1) {
        fprintf(stderr, "launcher: failed to run bugreport cli\n");
        return D_APP_EXIT_FAILURE;
    }
    return rc;
}

static void launcher_apply_accessibility(launcher_ui_settings* settings,
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
    settings->reduced_motion = preset->reduced_motion ? 1 : 0;
    settings->keyboard_only = preset->keyboard_only ? 1 : 0;
    settings->screen_reader = preset->screen_reader ? 1 : 0;
    settings->low_cognitive_load = preset->low_cognitive_load ? 1 : 0;
}

/* UI shell implementations live in launcher_ui_shell.c */

static const char* launcher_backend_name_for(d_gfx_backend_type backend,
                                             const d_gfx_backend_info* infos,
                                             u32 count)
{
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (infos[i].backend == backend) {
            return infos[i].name;
        }
    }
    return "unknown";
}

static int launcher_print_capabilities(void)
{
    dom_app_platform_caps caps;
    d_gfx_backend_info infos[D_GFX_BACKEND_MAX];
    u32 count;
    d_gfx_backend_type auto_backend;
    const char* auto_name;
    int dsys_ok;
    u32 i;
    dom_app_readonly_adapter ro;
    dom_app_compat_report compat;

    dsys_ok = dom_app_query_platform_caps(&caps);
    if (!dsys_ok) {
        fprintf(stderr, "launcher: dsys_init failed (%s)\n",
                caps.error_text ? caps.error_text : "unknown");
    }
    dom_app_print_platform_caps(&caps, 0, 1);

    count = d_gfx_detect_backends(infos, (u32)(sizeof(infos) / sizeof(infos[0])));
    auto_backend = d_gfx_select_backend();
    auto_name = launcher_backend_name_for(auto_backend, infos, count);
    printf("renderer_auto=%s\n", auto_name ? auto_name : "unknown");
    for (i = 0u; i < count; ++i) {
        printf("renderer=%s supported=%u detail=%s\n",
               infos[i].name,
               infos[i].supported ? 1u : 0u,
               infos[i].detail);
    }

    dom_app_ro_init(&ro);
    dom_app_compat_report_init(&compat, "launcher");
    if (dom_app_ro_open(&ro, 0, &compat)) {
        printf("readonly_topology=%s\n",
               dom_app_ro_has_packages_tree(&ro) ? "packages_tree" : "unsupported");
        printf("readonly_snapshot=unsupported\n");
        printf("readonly_events=unsupported\n");
        printf("readonly_replay=unsupported\n");
        dom_app_ro_close(&ro);
    } else {
        printf("readonly_init=failed\n");
        if (compat.message[0]) {
            printf("readonly_error=%s\n", compat.message);
        }
    }

    return dsys_ok ? D_APP_EXIT_OK : D_APP_EXIT_FAILURE;
}

int launcher_main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    char control_registry_buf[512];
    const char* control_enable = 0;
    const char* accessibility_preset_path = 0;
    const char* locale_id = 0;
    const char* locale_packs[16];
    int locale_pack_count = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    int timing_mode_set = 0;
    d_app_timing_mode timing_mode = D_APP_TIMING_DETERMINISTIC;
    uint32_t frame_cap_ms = 16u;
    dom_app_ui_request ui_req;
    dom_app_ui_mode ui_mode = DOM_APP_UI_NONE;
    dom_app_ui_run_config ui_run;
    launcher_ui_settings ui_settings;
    dom_app_ui_event_log ui_log;
    int ui_log_open = 0;
    dom_app_ui_locale_table locale_table;
    int locale_active = 0;
    dom_control_caps control_caps;
    int control_loaded = 0;
    const char* cmd = 0;
    int cmd_index = -1;
    int i;
    dom_app_ui_request_init(&ui_req);
    dom_app_ui_run_config_init(&ui_run);
    launcher_ui_settings_init(&ui_settings);
    dom_app_ui_event_log_init(&ui_log);
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
            fprintf(stderr, "launcher: %s\n", ui_err);
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
                fprintf(stderr, "launcher: %s\n", ui_err);
                return D_APP_EXIT_USAGE;
            }
            if (run_res > 0) {
                i += run_consumed - 1;
                continue;
            }
        }
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            cmd = argv[i];
            cmd_index = i;
            break;
        }
        if (strcmp(argv[i], "--version") == 0) {
            cmd = argv[i];
            cmd_index = i;
            break;
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
            if (!launcher_parse_ui_scale(argv[i] + 11, &value)) {
                fprintf(stderr, "launcher: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            continue;
        }
        if (strcmp(argv[i], "--ui-scale") == 0 && i + 1 < argc) {
            int value = 0;
            if (!launcher_parse_ui_scale(argv[i + 1], &value)) {
                fprintf(stderr, "launcher: invalid --ui-scale value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.ui_scale_percent = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--palette=", 10) == 0) {
            int value = 0;
            if (!launcher_parse_palette(argv[i] + 10, &value)) {
                fprintf(stderr, "launcher: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            continue;
        }
        if (strcmp(argv[i], "--palette") == 0 && i + 1 < argc) {
            int value = 0;
            if (!launcher_parse_palette(argv[i + 1], &value)) {
                fprintf(stderr, "launcher: invalid --palette value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.palette = value;
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--log-verbosity=", 16) == 0) {
            int value = 0;
            if (!launcher_parse_log_level(argv[i] + 16, &value)) {
                fprintf(stderr, "launcher: invalid --log-verbosity value\n");
                return D_APP_EXIT_USAGE;
            }
            ui_settings.log_level = value;
            continue;
        }
        if (strcmp(argv[i], "--log-verbosity") == 0 && i + 1 < argc) {
            int value = 0;
            if (!launcher_parse_log_level(argv[i + 1], &value)) {
                fprintf(stderr, "launcher: invalid --log-verbosity value\n");
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
                fprintf(stderr, "launcher: too many --locale-pack entries\n");
                return D_APP_EXIT_USAGE;
            }
            locale_packs[locale_pack_count++] = argv[i] + 14;
            continue;
        }
        if (strcmp(argv[i], "--locale-pack") == 0 && i + 1 < argc) {
            if (locale_pack_count >= (int)(sizeof(locale_packs) / sizeof(locale_packs[0]))) {
                fprintf(stderr, "launcher: too many --locale-pack entries\n");
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
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (argv[i][0] != '-') {
            cmd = argv[i];
            cmd_index = i;
            break;
        }
    }
    if (want_smoke || want_selftest) {
        want_status = 1;
    }
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "launcher: --deterministic and --interactive are mutually exclusive\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "launcher: --smoke requires deterministic mode\n");
        return D_APP_EXIT_USAGE;
    }
    ui_mode = dom_app_select_ui_mode(&ui_req, DOM_APP_UI_NONE);
    if (want_deterministic) {
        timing_mode = D_APP_TIMING_DETERMINISTIC;
        timing_mode_set = 1;
    }
    if (want_interactive) {
        timing_mode = D_APP_TIMING_INTERACTIVE;
        timing_mode_set = 1;
    }
    if (!timing_mode_set) {
        timing_mode = (ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI)
                          ? D_APP_TIMING_INTERACTIVE
                          : D_APP_TIMING_DETERMINISTIC;
    }
    if (timing_mode == D_APP_TIMING_DETERMINISTIC) {
        frame_cap_ms = 0u;
    }
    if ((ui_mode == DOM_APP_UI_TUI || ui_mode == DOM_APP_UI_GUI) &&
        (want_build_info || want_status || want_smoke || want_selftest ||
         (cmd && strcmp(cmd, "--help") != 0 && strcmp(cmd, "-h") != 0 &&
          strcmp(cmd, "--version") != 0))) {
        fprintf(stderr, "launcher: --ui=%s cannot combine with CLI commands\n",
                dom_app_ui_mode_name(ui_mode));
        return D_APP_EXIT_USAGE;
    }
    if (!cmd && !want_build_info && !want_status && ui_mode == DOM_APP_UI_NONE) {
        launcher_print_help();
        return (argc <= 1) ? D_APP_EXIT_OK : D_APP_EXIT_USAGE;
    }

    if (cmd && (strcmp(cmd, "--help") == 0 || strcmp(cmd, "-h") == 0)) {
        launcher_print_help();
        return D_APP_EXIT_OK;
    }

    if (accessibility_preset_path) {
        dom_app_ui_accessibility_preset preset;
        char err[128];
        dom_app_ui_accessibility_preset_init(&preset);
        if (!dom_app_ui_accessibility_load_file(&preset, accessibility_preset_path,
                                                err, sizeof(err))) {
            fprintf(stderr, "launcher: %s\n", err[0] ? err : "invalid accessibility preset");
            return D_APP_EXIT_USAGE;
        }
        launcher_apply_accessibility(&ui_settings, &preset);
    }
    if (locale_pack_count > 0) {
        int p;
        char err[128];
        if (!locale_id || !locale_id[0]) {
            fprintf(stderr, "launcher: --locale is required with --locale-pack\n");
            return D_APP_EXIT_USAGE;
        }
        for (p = 0; p < locale_pack_count; ++p) {
            if (!dom_app_ui_locale_table_load_pack(&locale_table,
                                                   locale_packs[p],
                                                   locale_id,
                                                   err,
                                                   sizeof(err))) {
                fprintf(stderr, "launcher: %s\n", err[0] ? err : "locale load failed");
                return D_APP_EXIT_USAGE;
            }
        }
        ui_settings.locale = &locale_table;
        locale_active = 1;
    }

    if (ui_mode == DOM_APP_UI_TUI && !cmd && !want_build_info && !want_status) {
        int res = launcher_ui_run_tui(&ui_run, &ui_settings, timing_mode, frame_cap_ms);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }
    if (ui_mode == DOM_APP_UI_GUI && !cmd && !want_build_info && !want_status) {
        int res = launcher_ui_run_gui(&ui_run, &ui_settings, timing_mode, frame_cap_ms);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }

    launcher_resolve_control_registry(control_registry_buf,
                                      sizeof(control_registry_buf),
                                      control_registry_path);
    control_registry_path = control_registry_buf;

    if (want_status || control_enable) {
        if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "launcher: failed to load control registry: %s\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        control_loaded = 1;
        if (enable_control_list(&control_caps, control_enable) != 0) {
            fprintf(stderr, "launcher: invalid control capability list\n");
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
        print_build_info("launcher", DOMINIUM_LAUNCHER_VERSION);
        if (control_loaded) {
            print_control_caps(&control_caps);
            dom_control_caps_free(&control_caps);
        }
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return D_APP_EXIT_OK;
    }
    if (want_status) {
        if (!control_loaded) {
            if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
                fprintf(stderr, "launcher: failed to load control registry: %s\n", control_registry_path);
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
        return D_APP_EXIT_OK;
    }
    if (!cmd) {
        launcher_print_help();
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        print_version(DOMINIUM_LAUNCHER_VERSION);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "list-profiles") == 0) {
        launcher_print_profiles();
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "capabilities") == 0) {
        int res = launcher_print_capabilities();
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }
    if (strcmp(cmd, "ops") == 0) {
        int res = launcher_run_ops(argc, argv, cmd_index);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }
    if (strcmp(cmd, "share") == 0) {
        int res = launcher_run_share(argc, argv, cmd_index);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }
    if (strcmp(cmd, "bugreport") == 0) {
        int res = launcher_run_bugreport(argc, argv, cmd_index);
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        return res;
    }

    if (ui_run.log_set && !ui_log_open) {
        if (!dom_app_ui_event_log_open(&ui_log, ui_run.log_path)) {
            fprintf(stderr, "launcher: failed to open ui log\n");
            return D_APP_EXIT_FAILURE;
        }
        ui_log_open = 1;
    }
    {
        char status[160];
        int res = launcher_ui_execute_command(cmd, &ui_settings, &ui_log,
                                              status, sizeof(status), 1);
        if (ui_log_open) {
            dom_app_ui_event_log_close(&ui_log);
        }
        if (locale_active) {
            dom_app_ui_locale_table_free(&locale_table);
        }
        if (res != D_APP_EXIT_USAGE) {
            return res;
        }
    }

    printf("launcher: unknown command '%s'\n", cmd);
    launcher_print_help();
    return D_APP_EXIT_USAGE;
}

int main(int argc, char** argv)
{
    return launcher_main(argc, argv);
}
