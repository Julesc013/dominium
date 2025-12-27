/*
FILE: source/dominium/setup/installers/linux/common/src/ui_flow.c
MODULE: Dominium Setup Linux
PURPOSE: Shared UI state defaults for Linux frontends.
*/
#include "dsu_linux_ui.h"

#include <string.h>

void dsu_linux_ui_state_init(dsu_linux_ui_state_t *state) {
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    state->step = DSU_LINUX_UI_STEP_DETECT;
    state->install_mode = DSU_LINUX_UI_INSTALL_MODE_QUICK;
    state->scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    state->operation = 0;
    state->installed_detected = 0;
    state->enable_shortcuts = 1;
    state->enable_file_assoc = 0;
    state->enable_url_handlers = 0;
}

const char *dsu_linux_ui_step_label(dsu_linux_ui_step_t step) {
    switch (step) {
        case DSU_LINUX_UI_STEP_DETECT: return "Detect";
        case DSU_LINUX_UI_STEP_OPERATION: return "Operation";
        case DSU_LINUX_UI_STEP_MODE: return "Install Mode";
        case DSU_LINUX_UI_STEP_SCOPE: return "Scope";
        case DSU_LINUX_UI_STEP_PATHS: return "Install Path";
        case DSU_LINUX_UI_STEP_COMPONENTS: return "Components";
        case DSU_LINUX_UI_STEP_SUMMARY: return "Summary";
        case DSU_LINUX_UI_STEP_EXECUTE: return "Execute";
        case DSU_LINUX_UI_STEP_COMPLETE: return "Complete";
        default: return "";
    }
}
