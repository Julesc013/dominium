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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    printf("  --debug-ui                  Enable debug UI flags\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("commands:\n");
    printf("  version         Show launcher version\n");
    printf("  list-profiles   List known profiles\n");
    printf("  capabilities    Report platform + renderer availability\n");
    printf("  start           Start (procedural universe)\n");
    printf("  load-save       Load save (may be unavailable)\n");
    printf("  inspect-replay  Inspect replay (may be unavailable)\n");
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
    const char* control_enable = 0;
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
    const char* cmd = 0;
    int i;
    dom_app_ui_request_init(&ui_req);
    dom_app_ui_run_config_init(&ui_run);
    launcher_ui_settings_init(&ui_settings);
    dom_app_ui_event_log_init(&ui_log);

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
            break;
        }
        if (strcmp(argv[i], "--version") == 0) {
            cmd = argv[i];
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
    if (ui_mode == DOM_APP_UI_TUI && !cmd && !want_build_info && !want_status) {
        return launcher_ui_run_tui(&ui_run, &ui_settings, timing_mode, frame_cap_ms);
    }
    if (ui_mode == DOM_APP_UI_GUI && !cmd && !want_build_info && !want_status) {
        return launcher_ui_run_gui(&ui_run, &ui_settings, timing_mode, frame_cap_ms);
    }
    if (want_build_info || want_status) {
        dom_control_caps caps;
        if (dom_control_caps_init(&caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "launcher: failed to load control registry: %s\n", control_registry_path);
            return D_APP_EXIT_FAILURE;
        }
        if (enable_control_list(&caps, control_enable) != 0) {
            fprintf(stderr, "launcher: invalid control capability list\n");
            dom_control_caps_free(&caps);
            return D_APP_EXIT_USAGE;
        }
        if (want_build_info) {
            print_build_info("launcher", DOMINIUM_LAUNCHER_VERSION);
        }
        print_control_caps(&caps);
        dom_control_caps_free(&caps);
        return D_APP_EXIT_OK;
    }
    if (!cmd) {
        launcher_print_help();
        return D_APP_EXIT_USAGE;
    }
    if (strcmp(cmd, "--version") == 0 || strcmp(cmd, "version") == 0) {
        print_version(DOMINIUM_LAUNCHER_VERSION);
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "list-profiles") == 0) {
        launcher_print_profiles();
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "capabilities") == 0) {
        return launcher_print_capabilities();
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
