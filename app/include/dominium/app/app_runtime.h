/*
FILE: include/dominium/app/app_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium app/runtime
RESPONSIBILITY: Shared app-layer helpers for UI mode selection, timing, logging, and build info.
ALLOWED DEPENDENCIES: engine public headers, C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: engine private headers, game internals.
*/
#ifndef DOMINIUM_APP_RUNTIME_H
#define DOMINIUM_APP_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

#include "domino/app/runtime.h"
#include "domino/system/dsys.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_APP_UI_ENV "DOM_UI"
#define DOM_APP_UI_ENV_FALLBACK "DOM_UI_MODE"

typedef enum dom_app_ui_mode {
    DOM_APP_UI_NONE = 0,
    DOM_APP_UI_TUI,
    DOM_APP_UI_GUI
} dom_app_ui_mode;

typedef struct dom_app_ui_request {
    dom_app_ui_mode mode;
    int mode_explicit;
} dom_app_ui_request;

void        dom_app_ui_request_init(dom_app_ui_request* req);
const char* dom_app_ui_mode_name(dom_app_ui_mode mode);
int         dom_app_parse_ui_arg(dom_app_ui_request* req,
                                 const char* arg,
                                 const char* next,
                                 int* consumed,
                                 char* err,
                                 size_t err_cap);
dom_app_ui_mode dom_app_ui_mode_from_env(void);
dom_app_ui_mode dom_app_select_ui_mode(const dom_app_ui_request* req,
                                       dom_app_ui_mode default_mode);

typedef struct dom_app_clock {
    d_app_timing_mode mode;
    uint64_t app_time_us;
    uint64_t last_platform_us;
} dom_app_clock;

void     dom_app_clock_init(dom_app_clock* clock, d_app_timing_mode mode);
void     dom_app_clock_advance(dom_app_clock* clock);
uint64_t dom_app_time_now_us(void);
void     dom_app_sleep_for_cap(d_app_timing_mode mode,
                               uint32_t frame_cap_ms,
                               uint64_t frame_start_us);
void     dom_app_pump_terminal_input(void);
int      dom_app_exit_code_for_shutdown(dsys_shutdown_reason reason);

typedef enum dom_app_log_level {
    DOM_APP_LOG_INFO = 0,
    DOM_APP_LOG_WARN,
    DOM_APP_LOG_ERROR
} dom_app_log_level;

typedef enum dom_app_log_category {
    DOM_APP_LOG_APP = 0,
    DOM_APP_LOG_UI,
    DOM_APP_LOG_PLATFORM,
    DOM_APP_LOG_RENDER
} dom_app_log_category;

void dom_app_log(dom_app_log_level level,
                 dom_app_log_category category,
                 const char* fmt,
                 ...);

typedef struct dom_app_build_info {
    const char* product_name;
    const char* product_version;
} dom_app_build_info;

void dom_app_build_info_init(dom_app_build_info* info,
                             const char* product_name,
                             const char* product_version);
void dom_app_print_build_info(const dom_app_build_info* info);

typedef struct dom_app_platform_caps {
    dsys_caps caps;
    int ext_dpi;
    int ext_window_mode;
    int ext_cursor;
    int ext_cliptext;
    int ext_text_input;
    int dsys_ok;
    const char* error_text;
} dom_app_platform_caps;

int  dom_app_query_platform_caps(dom_app_platform_caps* out);
void dom_app_print_platform_caps(const dom_app_platform_caps* caps,
                                 int include_defaults,
                                 int print_on_failure);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_RUNTIME_H */
