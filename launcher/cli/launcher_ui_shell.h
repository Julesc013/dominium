/*
Launcher UI shell helpers (CLI/TUI/GUI parity).
*/
#ifndef DOMINIUM_LAUNCHER_UI_SHELL_H
#define DOMINIUM_LAUNCHER_UI_SHELL_H

#include <stddef.h>
#include <stdint.h>

#include "domino/app/runtime.h"
#include "dominium/app/app_runtime.h"
#include "dominium/app/ui_event_log.h"
#include "dominium/app/ui_presentation.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_ui_settings {
    char renderer[16];
    int ui_scale_percent;
    int palette;
    int log_level;
    int debug_ui;
    char ui_density[24];
    char verbosity[24];
    char keybind_profile_id[64];
    int reduced_motion;
    int keyboard_only;
    int screen_reader;
    int low_cognitive_load;
    const dom_app_ui_locale_table* locale;
} launcher_ui_settings;

void launcher_ui_settings_init(launcher_ui_settings* settings);
void launcher_ui_settings_format_lines(const launcher_ui_settings* settings,
                                       char* lines,
                                       size_t line_cap,
                                       size_t line_stride,
                                       int* out_count);

/* @repox:infrastructure_only Settings command dispatcher for UI parity only. */
int launcher_ui_execute_command(const char* cmd,
                                launcher_ui_settings* settings,
                                dom_app_ui_event_log* log,
                                char* status,
                                size_t status_cap,
                                int emit_text);

int launcher_ui_run_tui(const dom_app_ui_run_config* run_cfg,
                        const launcher_ui_settings* settings,
                        d_app_timing_mode timing_mode,
                        uint32_t frame_cap_ms);

int launcher_ui_run_gui(const dom_app_ui_run_config* run_cfg,
                        const launcher_ui_settings* settings,
                        d_app_timing_mode timing_mode,
                        uint32_t frame_cap_ms);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LAUNCHER_UI_SHELL_H */
