/*
FILE: source/dominium/setup/installers/macos_classic/gui/classic_installer_app/src/dialogs.h
MODULE: Dominium Setup (Classic GUI)
PURPOSE: Dialog flow interface for Classic installer UI.
*/
#ifndef DSU_CLASSIC_DIALOGS_H_INCLUDED
#define DSU_CLASSIC_DIALOGS_H_INCLUDED

#include "../../../core_legacy/include/dsu_legacy_core.h"

typedef struct dsu_classic_ui_result_t {
    dsu_legacy_u8 operation;
    dsu_legacy_u8 scope;
    char *install_root;
    char **selected_components;
    dsu_legacy_u32 selected_component_count;
    char **excluded_components;
    dsu_legacy_u32 excluded_component_count;
} dsu_classic_ui_result_t;

int dsu_classic_ui_collect(dsu_classic_ui_result_t *out);
void dsu_classic_ui_free(dsu_classic_ui_result_t *out);

#endif /* DSU_CLASSIC_DIALOGS_H_INCLUDED */
