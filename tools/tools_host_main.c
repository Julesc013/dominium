/*
Stub tools host entrypoint; replace with tool router once runtime is wired.
*/
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/app/runtime.h"
#include "domino/system/dsys.h"
#include "domino/tui/tui.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/readonly_adapter.h"
#include "dominium/app/readonly_format.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
    printf("  --format <text|json>         Output format for inspect/validate\\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\\n");
    printf("  --interactive               Use variable timestep (wall-clock)\\n");
    printf("  --frame-cap-ms <ms>         Frame cap for interactive loops (0 disables)\\n");
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

static int tools_run_tui(d_app_timing_mode timing_mode,
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

static int tools_run_gui(void)
{
    fprintf(stderr, "tools: gui not implemented\n");
    return D_APP_EXIT_UNAVAILABLE;
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
    const char* cmd = 0;
    int i;
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
            fprintf(stderr, "tools: %s\n", ui_err);
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
        fprintf(stderr, "tools: --format only applies to inspect/validate\n");
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
        return tools_run_tui(timing_mode, frame_cap_ms, &compat_expect);
    }
    if (ui_mode == DOM_APP_UI_GUI) {
        return tools_run_gui();
    }
    if (!cmd) {
        tools_print_help();
        return D_APP_EXIT_USAGE;
    }

    if (output_format_set) {
        if (strcmp(cmd, "inspect") != 0 && strcmp(cmd, "validate") != 0) {
            fprintf(stderr, "tools: --format only applies to inspect/validate\n");
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

    printf("tools: unknown command '%s'\\n", cmd);
    tools_print_help();
    return D_APP_EXIT_USAGE;
}

int main(int argc, char** argv)
{
    return tools_main(argc, argv);
}
