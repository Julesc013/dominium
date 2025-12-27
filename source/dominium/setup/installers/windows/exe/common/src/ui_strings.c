/*
FILE: source/dominium/setup/installers/windows/exe/common/src/ui_strings.c
MODULE: Dominium Setup EXE
PURPOSE: Shared UI strings for step labels.
*/
#include "dsu_exe_ui.h"

const char *dsu_ui_step_label(dsu_ui_step_t step) {
    switch (step) {
        case DSU_UI_STEP_DETECT: return "Detect";
        case DSU_UI_STEP_OPERATION: return "Operation";
        case DSU_UI_STEP_MODE: return "Install Mode";
        case DSU_UI_STEP_SCOPE: return "Scope";
        case DSU_UI_STEP_PATHS: return "Install Path";
        case DSU_UI_STEP_COMPONENTS: return "Components";
        case DSU_UI_STEP_SUMMARY: return "Summary";
        case DSU_UI_STEP_EXECUTE: return "Execute";
        case DSU_UI_STEP_COMPLETE: return "Complete";
        default: return "";
    }
}
