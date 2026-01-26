/*
Shared app-layer runtime helpers.
*/
#include "dominium/app/app_runtime.h"

#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dom_contracts/_internal/dom_build_version.h"
#include "dom_contracts/version.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/sys.h"
#include "domino/version.h"

static dom_app_ui_mode dom_app_parse_ui_value(const char* value, int* ok)
{
    char buf[16];
    size_t len;
    size_t i;
    if (!value) {
        if (ok) {
            *ok = 0;
        }
        return DOM_APP_UI_NONE;
    }
    len = strlen(value);
    if (len == 0u || len >= sizeof(buf)) {
        if (ok) {
            *ok = 0;
        }
        return DOM_APP_UI_NONE;
    }
    for (i = 0u; i < len; ++i) {
        buf[i] = (char)tolower((unsigned char)value[i]);
    }
    buf[len] = '\0';
    if (strcmp(buf, "none") == 0 || strcmp(buf, "cli") == 0 || strcmp(buf, "off") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_NONE;
    }
    if (strcmp(buf, "tui") == 0 || strcmp(buf, "terminal") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_TUI;
    }
    if (strcmp(buf, "gui") == 0 || strcmp(buf, "native") == 0) {
        if (ok) {
            *ok = 1;
        }
        return DOM_APP_UI_GUI;
    }
    if (ok) {
        *ok = 0;
    }
    return DOM_APP_UI_NONE;
}

void dom_app_ui_request_init(dom_app_ui_request* req)
{
    if (!req) {
        return;
    }
    req->mode = DOM_APP_UI_NONE;
    req->mode_explicit = 0;
}

const char* dom_app_ui_mode_name(dom_app_ui_mode mode)
{
    switch (mode) {
    case DOM_APP_UI_NONE:
        return "none";
    case DOM_APP_UI_TUI:
        return "tui";
    case DOM_APP_UI_GUI:
        return "gui";
    default:
        break;
    }
    return "unknown";
}

static int dom_app_ui_set(dom_app_ui_request* req,
                          dom_app_ui_mode mode,
                          char* err,
                          size_t err_cap)
{
    if (!req) {
        return 0;
    }
    if (req->mode_explicit && req->mode != mode) {
        if (err && err_cap > 0u) {
            snprintf(err, err_cap, "ui mode already set to %s", dom_app_ui_mode_name(req->mode));
        }
        return 0;
    }
    req->mode = mode;
    req->mode_explicit = 1;
    return 1;
}

int dom_app_parse_ui_arg(dom_app_ui_request* req,
                         const char* arg,
                         const char* next,
                         int* consumed,
                         char* err,
                         size_t err_cap)
{
    int ok = 0;
    dom_app_ui_mode mode;
    if (consumed) {
        *consumed = 0;
    }
    if (!arg || !req) {
        return 0;
    }
    if (strncmp(arg, "--ui=", 5) == 0) {
        mode = dom_app_parse_ui_value(arg + 5, &ok);
        if (!ok) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui value (use none|tui|gui)");
            }
            return -1;
        }
        if (!dom_app_ui_set(req, mode, err, err_cap)) {
            return -1;
        }
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    if (strcmp(arg, "--ui") == 0) {
        if (!next || !next[0]) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "missing --ui value (use none|tui|gui)");
            }
            return -1;
        }
        mode = dom_app_parse_ui_value(next, &ok);
        if (!ok) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui value (use none|tui|gui)");
            }
            return -1;
        }
        if (!dom_app_ui_set(req, mode, err, err_cap)) {
            return -1;
        }
        if (consumed) {
            *consumed = 2;
        }
        return 1;
    }
    if (strcmp(arg, "--tui") == 0) {
        if (!dom_app_ui_set(req, DOM_APP_UI_TUI, err, err_cap)) {
            return -1;
        }
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    return 0;
}

dom_app_ui_mode dom_app_ui_mode_from_env(void)
{
    const char* value = getenv(DOM_APP_UI_ENV);
    int ok = 0;
    dom_app_ui_mode mode;
    if (!value || !value[0]) {
        value = getenv(DOM_APP_UI_ENV_FALLBACK);
    }
    if (!value || !value[0]) {
        return DOM_APP_UI_NONE;
    }
    mode = dom_app_parse_ui_value(value, &ok);
    return ok ? mode : DOM_APP_UI_NONE;
}

dom_app_ui_mode dom_app_select_ui_mode(const dom_app_ui_request* req,
                                       dom_app_ui_mode default_mode)
{
    dom_app_ui_mode env_mode;
    if (req && req->mode_explicit) {
        return req->mode;
    }
    env_mode = dom_app_ui_mode_from_env();
    if (env_mode != DOM_APP_UI_NONE) {
        return env_mode;
    }
    return default_mode;
}

static int dom_app_ui_is_sep(char c)
{
    return (c == ' ' || c == '\\t' || c == ',' || c == ';' || c == '|' || c == '>');
}

void dom_app_ui_script_init(dom_app_ui_script* script, const char* text)
{
    size_t len;
    size_t i;
    char* p;
    char* end;
    if (!script) {
        return;
    }
    memset(script, 0, sizeof(*script));
    if (!text || !text[0]) {
        return;
    }
    len = strlen(text);
    if (len >= sizeof(script->buffer)) {
        len = sizeof(script->buffer) - 1u;
    }
    memcpy(script->buffer, text, len);
    script->buffer[len] = '\0';

    p = script->buffer;
    end = script->buffer + len;
    while (p < end) {
        while (p < end && dom_app_ui_is_sep(*p)) {
            *p = '\0';
            ++p;
        }
        if (p >= end || *p == '\0') {
            break;
        }
        if (script->count >= DOM_APP_UI_SCRIPT_MAX_ACTIONS) {
            break;
        }
        script->actions[script->count++] = p;
        while (p < end && *p && !dom_app_ui_is_sep(*p)) {
            ++p;
        }
        if (p < end) {
            *p = '\0';
            ++p;
        }
    }
    for (i = 0u; i < script->count; ++i) {
        if (script->actions[i] && script->actions[i][0] != '\0') {
            continue;
        }
        script->actions[i] = 0;
    }
}

const char* dom_app_ui_script_next(dom_app_ui_script* script)
{
    if (!script || script->index >= script->count) {
        return 0;
    }
    return script->actions[script->index++];
}

static int dom_app_parse_u32(const char* text, uint32_t* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    while (*text && isspace((unsigned char)*text)) {
        text++;
    }
    if (!text[0]) {
        return 0;
    }
    value = strtoul(text, &end, 10);
    if (!end || end == text) {
        return 0;
    }
    while (*end && isspace((unsigned char)*end)) {
        end++;
    }
    if (*end != '\0') {
        return 0;
    }
    *out_value = (uint32_t)value;
    return 1;
}

void dom_app_ui_run_config_init(dom_app_ui_run_config* cfg)
{
    if (!cfg) {
        return;
    }
    memset(cfg, 0, sizeof(*cfg));
}

int dom_app_parse_ui_run_arg(dom_app_ui_run_config* cfg,
                             const char* arg,
                             const char* next,
                             int* consumed,
                             char* err,
                             size_t err_cap)
{
    if (consumed) {
        *consumed = 0;
    }
    if (!cfg || !arg) {
        return 0;
    }
    if (strcmp(arg, "--headless") == 0 || strcmp(arg, "--ui-headless") == 0) {
        cfg->headless = 1;
        cfg->headless_set = 1;
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    if (strncmp(arg, "--ui-frames=", 12) == 0) {
        uint32_t value = 0u;
        if (!dom_app_parse_u32(arg + 12, &value) || value == 0u) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-frames value");
            }
            return -1;
        }
        cfg->max_frames = value;
        cfg->max_frames_set = 1;
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    if (strcmp(arg, "--ui-frames") == 0) {
        uint32_t value = 0u;
        if (!next || !next[0] || !dom_app_parse_u32(next, &value) || value == 0u) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-frames value");
            }
            return -1;
        }
        cfg->max_frames = value;
        cfg->max_frames_set = 1;
        if (consumed) {
            *consumed = 2;
        }
        return 1;
    }
    if (strncmp(arg, "--ui-script=", 12) == 0) {
        const char* value = arg + 12;
        size_t len = value ? strlen(value) : 0u;
        if (!value || len == 0u || len >= sizeof(cfg->script)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-script value");
            }
            return -1;
        }
        memcpy(cfg->script, value, len);
        cfg->script[len] = '\0';
        cfg->script_set = 1;
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    if (strcmp(arg, "--ui-script") == 0) {
        size_t len;
        if (!next || !next[0]) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "missing --ui-script value");
            }
            return -1;
        }
        len = strlen(next);
        if (len == 0u || len >= sizeof(cfg->script)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-script value");
            }
            return -1;
        }
        memcpy(cfg->script, next, len);
        cfg->script[len] = '\0';
        cfg->script_set = 1;
        if (consumed) {
            *consumed = 2;
        }
        return 1;
    }
    if (strncmp(arg, "--ui-log=", 9) == 0 || strncmp(arg, "--ui-event-log=", 15) == 0) {
        const char* value = (arg[5] == 'l') ? (arg + 9) : (arg + 15);
        size_t len = value ? strlen(value) : 0u;
        if (!value || len == 0u || len >= sizeof(cfg->log_path)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-log value");
            }
            return -1;
        }
        memcpy(cfg->log_path, value, len);
        cfg->log_path[len] = '\0';
        cfg->log_set = 1;
        if (consumed) {
            *consumed = 1;
        }
        return 1;
    }
    if (strcmp(arg, "--ui-log") == 0 || strcmp(arg, "--ui-event-log") == 0) {
        size_t len;
        if (!next || !next[0]) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "missing --ui-log value");
            }
            return -1;
        }
        len = strlen(next);
        if (len == 0u || len >= sizeof(cfg->log_path)) {
            if (err && err_cap > 0u) {
                snprintf(err, err_cap, "invalid --ui-log value");
            }
            return -1;
        }
        memcpy(cfg->log_path, next, len);
        cfg->log_path[len] = '\0';
        cfg->log_set = 1;
        if (consumed) {
            *consumed = 2;
        }
        return 1;
    }
    return 0;
}

void dom_app_clock_init(dom_app_clock* clock, d_app_timing_mode mode)
{
    if (!clock) {
        return;
    }
    clock->mode = mode;
    clock->app_time_us = 0u;
    clock->last_platform_us = dsys_time_now_us();
}

void dom_app_clock_advance(dom_app_clock* clock)
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

uint64_t dom_app_time_now_us(void)
{
    return dsys_time_now_us();
}

void dom_app_sleep_for_cap(d_app_timing_mode mode,
                           uint32_t frame_cap_ms,
                           uint64_t frame_start_us)
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

void dom_app_pump_terminal_input(void)
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

int dom_app_exit_code_for_shutdown(dsys_shutdown_reason reason)
{
    if (reason == DSYS_SHUTDOWN_SIGNAL || reason == DSYS_SHUTDOWN_CONSOLE) {
        return D_APP_EXIT_SIGNAL;
    }
    return D_APP_EXIT_OK;
}

static const char* dom_app_log_level_name(dom_app_log_level level)
{
    switch (level) {
    case DOM_APP_LOG_INFO:
        return "info";
    case DOM_APP_LOG_WARN:
        return "warn";
    case DOM_APP_LOG_ERROR:
        return "error";
    default:
        break;
    }
    return "log";
}

static const char* dom_app_log_category_name(dom_app_log_category category)
{
    switch (category) {
    case DOM_APP_LOG_APP:
        return "app";
    case DOM_APP_LOG_UI:
        return "ui";
    case DOM_APP_LOG_PLATFORM:
        return "platform";
    case DOM_APP_LOG_RENDER:
        return "render";
    default:
        break;
    }
    return "app";
}

void dom_app_log(dom_app_log_level level,
                 dom_app_log_category category,
                 const char* fmt,
                 ...)
{
    va_list args;
    if (!fmt) {
        return;
    }
    fprintf(stderr, "[%s/%s] ",
            dom_app_log_level_name(level),
            dom_app_log_category_name(category));
    va_start(args, fmt);
    vfprintf(stderr, fmt, args);
    va_end(args);
    fprintf(stderr, "\n");
}

static const char* dom_app_default_sku_for_product(const char* product_name)
{
    if (!product_name || !product_name[0]) {
        return "unspecified";
    }
    if (strcmp(product_name, "client") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "server") == 0) {
        return "headless_server";
    }
    if (strcmp(product_name, "launcher") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "setup") == 0) {
        return "modern_desktop";
    }
    if (strcmp(product_name, "tools") == 0) {
        return "devtools";
    }
    return "unspecified";
}

static const char* dom_app_build_sku_value(const dom_app_build_info* info)
{
    const char* override = DOM_BUILD_SKU;
    if (override && override[0] && strcmp(override, "auto") != 0) {
        return override;
    }
    return dom_app_default_sku_for_product(info ? info->product_name : "");
}

void dom_app_build_info_init(dom_app_build_info* info,
                             const char* product_name,
                             const char* product_version)
{
    if (!info) {
        return;
    }
    info->product_name = product_name;
    info->product_version = product_version;
}

void dom_app_print_build_info(const dom_app_build_info* info)
{
    const char* product_name = info ? info->product_name : "";
    const char* product_version = info ? info->product_version : "";
    printf("product=%s\n", product_name ? product_name : "");
    printf("product_version=%s\n", product_version ? product_version : "");
    printf("sku=%s\n", dom_app_build_sku_value(info));
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("git_hash=%s\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("toolchain_family=%s\n", DOM_TOOLCHAIN_FAMILY);
    printf("toolchain_version=%s\n", DOM_TOOLCHAIN_VERSION);
    printf("toolchain_stdlib=%s\n", DOM_TOOLCHAIN_STDLIB);
    printf("toolchain_runtime=%s\n", DOM_TOOLCHAIN_RUNTIME);
    printf("toolchain_link=%s\n", DOM_TOOLCHAIN_LINK);
    printf("toolchain_target=%s\n", DOM_TOOLCHAIN_TARGET);
    printf("toolchain_os=%s\n", DOM_TOOLCHAIN_OS);
    printf("toolchain_arch=%s\n", DOM_TOOLCHAIN_ARCH);
    printf("toolchain_os_floor=%s\n", DOM_TOOLCHAIN_OS_FLOOR);
    printf("toolchain_config=%s\n", DOM_TOOLCHAIN_CONFIG);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", (unsigned int)DSYS_PROTOCOL_VERSION);
    printf("platform_ext_window_ex_api=%u\n", (unsigned int)DSYS_EXTENSION_WINDOW_EX_VERSION);
    printf("platform_ext_error_api=%u\n", (unsigned int)DSYS_EXTENSION_ERROR_VERSION);
    printf("platform_ext_cliptext_api=%u\n", (unsigned int)DSYS_EXTENSION_CLIPTEXT_VERSION);
    printf("platform_ext_cursor_api=%u\n", (unsigned int)DSYS_EXTENSION_CURSOR_VERSION);
    printf("platform_ext_dragdrop_api=%u\n", (unsigned int)DSYS_EXTENSION_DRAGDROP_VERSION);
    printf("platform_ext_gamepad_api=%u\n", (unsigned int)DSYS_EXTENSION_GAMEPAD_VERSION);
    printf("platform_ext_power_api=%u\n", (unsigned int)DSYS_EXTENSION_POWER_VERSION);
    printf("platform_ext_text_input_api=%u\n", (unsigned int)DSYS_EXTENSION_TEXT_INPUT_VERSION);
    printf("platform_ext_window_mode_api=%u\n", (unsigned int)DSYS_EXTENSION_WINDOW_MODE_VERSION);
    printf("platform_ext_dpi_api=%u\n", (unsigned int)DSYS_EXTENSION_DPI_VERSION);
    printf("api_dgfx=%u\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

int dom_app_query_platform_caps(dom_app_platform_caps* out)
{
    if (!out) {
        return 0;
    }
    memset(out, 0, sizeof(*out));
    out->caps.name = "unknown";
    if (dsys_init() != DSYS_OK) {
        out->dsys_ok = 0;
        out->error_text = dsys_last_error_text();
        return 0;
    }
    out->dsys_ok = 1;
    out->caps = dsys_get_caps();
    out->ext_dpi = dsys_query_extension(DSYS_EXTENSION_DPI, 1u) ? 1 : 0;
    out->ext_window_mode = dsys_query_extension(DSYS_EXTENSION_WINDOW_MODE, 1u) ? 1 : 0;
    out->ext_cursor = dsys_query_extension(DSYS_EXTENSION_CURSOR, 1u) ? 1 : 0;
    out->ext_cliptext = dsys_query_extension(DSYS_EXTENSION_CLIPTEXT, 1u) ? 1 : 0;
    out->ext_text_input = dsys_query_extension(DSYS_EXTENSION_TEXT_INPUT, 1u) ? 1 : 0;
    dsys_shutdown();
    return 1;
}

void dom_app_print_platform_caps(const dom_app_platform_caps* caps,
                                 int include_defaults,
                                 int print_on_failure)
{
    if (!caps) {
        return;
    }
    if (!caps->dsys_ok) {
        printf("platform_init=failed\n");
        if (caps->error_text) {
            printf("platform_error=%s\n", caps->error_text);
        }
        if (!print_on_failure) {
            return;
        }
    }
    printf("platform_backend=%s\n", caps->caps.name ? caps->caps.name : "unknown");
    printf("platform_ui_modes=%u\n", (unsigned int)caps->caps.ui_modes);
    printf("platform_has_windows=%u\n", caps->caps.has_windows ? 1u : 0u);
    printf("platform_has_mouse=%u\n", caps->caps.has_mouse ? 1u : 0u);
    printf("platform_has_gamepad=%u\n", caps->caps.has_gamepad ? 1u : 0u);
    printf("platform_has_high_res_timer=%u\n", caps->caps.has_high_res_timer ? 1u : 0u);
    printf("platform_ext_dpi=%s\n",
           (caps->ext_dpi && caps->caps.has_windows) ? "available" : "missing");
    printf("platform_ext_window_mode=%s\n",
           (caps->ext_window_mode && caps->caps.has_windows) ? "available" : "missing");
    printf("platform_ext_cursor=%s\n",
           (caps->ext_cursor && caps->caps.has_windows) ? "available" : "missing");
    printf("platform_ext_cliptext=%s\n",
           (caps->ext_cliptext && caps->caps.has_windows) ? "available" : "missing");
    printf("platform_ext_text_input=%s\n",
           (caps->ext_text_input && caps->caps.has_windows) ? "available" : "missing");
    if (include_defaults) {
        printf("window_default_width=800\n");
        printf("window_default_height=600\n");
        printf("framebuffer_default_width=800\n");
        printf("framebuffer_default_height=600\n");
        printf("dpi_scale_default=1.0\n");
    }
}
