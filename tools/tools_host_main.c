/*
Stub tools host entrypoint; replace with tool router once runtime is wired.
*/
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/app/runtime.h"
#include "domino/tui/tui.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

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
    printf("  --tui                       Start tools terminal UI\\n");
    printf("  --deterministic             Use fixed timestep (no wall-clock sleep)\\n");
    printf("  --interactive               Use variable timestep (wall-clock)\\n");
    printf("  --frame-cap-ms <ms>         Frame cap for interactive loops (0 disables)\\n");
    printf("commands:\\n");
    printf("  inspect    Inspect artifacts (stub)\\n");
    printf("  validate   Validate artifacts (stub)\\n");
    printf("  replay     Replay viewer (stub)\\n");
}

static void tools_print_version(const char* product_version)
{
    printf("tools %s\\n", product_version);
}

static void tools_print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\\n", product_name);
    printf("product_version=%s\\n", product_version);
    printf("engine_version=%s\\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\\n", DOM_BUILD_ID);
    printf("git_hash=%s\\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\\n");
    printf("abi_dom_build_info=%u\\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\\n", 1u);
    printf("api_dgfx=%u\\n", (unsigned int)DGFX_PROTOCOL_VERSION);
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

typedef struct tools_clock {
    d_app_timing_mode mode;
    uint64_t app_time_us;
    uint64_t last_platform_us;
} tools_clock;

static void tools_clock_init(tools_clock* clock, d_app_timing_mode mode)
{
    if (!clock) {
        return;
    }
    clock->mode = mode;
    clock->app_time_us = 0u;
    clock->last_platform_us = dsys_time_now_us();
}

static void tools_clock_advance(tools_clock* clock)
{
    uint64_t now;
    uint64_t delta;
    if (!clock) {
        return;
    }
    if (clock->mode == D_APP_TIMING_DETERMINISTIC) {
        clock->app_time_us += (uint64_t)D_APP_FIXED_TIMESTEP_US;
        return;
    }
    now = dsys_time_now_us();
    delta = (now >= clock->last_platform_us) ? (now - clock->last_platform_us) : 0u;
    clock->last_platform_us = now;
    clock->app_time_us += delta;
}

static void tools_sleep_for_cap(d_app_timing_mode mode, uint32_t frame_cap_ms, uint64_t frame_start_us)
{
    uint64_t target_us;
    uint64_t elapsed;
    uint64_t remaining;
    uint32_t sleep_ms;
    if (mode != D_APP_TIMING_INTERACTIVE || frame_cap_ms == 0u) {
        return;
    }
    target_us = (uint64_t)frame_cap_ms * 1000u;
    elapsed = dsys_time_now_us() - frame_start_us;
    if (elapsed >= target_us) {
        return;
    }
    remaining = target_us - elapsed;
    sleep_ms = (uint32_t)((remaining + 999u) / 1000u);
    if (sleep_ms > 0u) {
        dsys_sleep_ms(sleep_ms);
    }
}

static void tools_pump_terminal_input(void)
{
    int key;
    dsys_event ev;
    while ((key = dsys_terminal_poll_key()) != 0) {
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_KEY_DOWN;
        ev.payload.key.key = (int32_t)key;
        ev.payload.key.repeat = false;
        (void)dsys_inject_event(&ev);
    }
}

static int tools_exit_code_for_shutdown(dsys_shutdown_reason reason)
{
    if (reason == DSYS_SHUTDOWN_SIGNAL || reason == DSYS_SHUTDOWN_CONSOLE) {
        return D_APP_EXIT_SIGNAL;
    }
    return D_APP_EXIT_OK;
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

static int tools_run_tui(d_app_timing_mode timing_mode, uint32_t frame_cap_ms)
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
    tools_clock clock;
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
    tools_clock_init(&clock, timing_mode);

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
        tools_pump_terminal_input();
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
        tools_clock_advance(&clock);
        tools_tui_update_status(&state, timing_mode, clock.app_time_us);
        d_tui_render(tui);
        tools_sleep_for_cap(timing_mode, frame_cap_ms, frame_start_us);
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
                result = tools_exit_code_for_shutdown(reason);
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
        printf("tools: inspect stub\n");
        return D_APP_EXIT_OK;
    }
    if (state.action == TOOLS_TUI_VALIDATE) {
        printf("tools: validate stub\n");
        return D_APP_EXIT_OK;
    }
    if (state.action == TOOLS_TUI_REPLAY) {
        printf("tools: replay stub\n");
        return D_APP_EXIT_OK;
    }
    return result;
}

int main(int argc, char** argv)
{
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    int want_tui = 0;
    int want_deterministic = 0;
    int want_interactive = 0;
    int timing_mode_set = 0;
    d_app_timing_mode timing_mode = D_APP_TIMING_DETERMINISTIC;
    uint32_t frame_cap_ms = 16u;
    const char* cmd = 0;
    int i;

    if (argc <= 1) {
        tools_print_help();
        return D_APP_EXIT_OK;
    }

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
        if (strcmp(argv[i], "--tui") == 0) {
            want_tui = 1;
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
        if (argv[i][0] != '-') {
            cmd = argv[i];
            break;
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
    if (want_deterministic && want_interactive) {
        fprintf(stderr, "tools: --deterministic and --interactive are mutually exclusive\n");
        return D_APP_EXIT_USAGE;
    }
    if ((want_smoke || want_selftest) && want_interactive) {
        fprintf(stderr, "tools: --smoke requires deterministic mode\n");
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
        timing_mode = want_tui ? D_APP_TIMING_INTERACTIVE : D_APP_TIMING_DETERMINISTIC;
    }
    if (timing_mode == D_APP_TIMING_DETERMINISTIC) {
        frame_cap_ms = 0u;
    }
    if (want_tui && (want_smoke || want_selftest)) {
        fprintf(stderr, "tools: --smoke cannot combine with tui mode\n");
        return D_APP_EXIT_USAGE;
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
    if (want_tui) {
        return tools_run_tui(timing_mode, frame_cap_ms);
    }
    if (!cmd) {
        tools_print_help();
        return D_APP_EXIT_USAGE;
    }

    if (strcmp(cmd, "inspect") == 0) {
        printf("tools: inspect stub\\n");
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "validate") == 0) {
        printf("tools: validate stub\\n");
        return D_APP_EXIT_OK;
    }
    if (strcmp(cmd, "replay") == 0) {
        printf("tools: replay stub\\n");
        return D_APP_EXIT_OK;
    }

    printf("tools: unknown command '%s'\\n", cmd);
    tools_print_help();
    return D_APP_EXIT_USAGE;
}
