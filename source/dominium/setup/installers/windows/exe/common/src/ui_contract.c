/*
FILE: source/dominium/setup/installers/windows/exe/common/src/ui_contract.c
MODULE: Dominium Setup EXE
PURPOSE: Shared UI state machine defaults.
*/
#include "dsu_exe_ui.h"

#include <string.h>

void dsu_ui_state_init(dsu_ui_state_t *state) {
    if (!state) {
        return;
    }
    memset(state, 0, sizeof(*state));
    state->step = DSU_UI_STEP_DETECT;
    state->install_mode = DSU_UI_INSTALL_MODE_QUICK;
    state->scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    state->operation = 0;
    state->installed_detected = 0;
    state->enable_shortcuts = 1;
    state->enable_file_assoc = 1;
    state->enable_url_handlers = 1;
}
