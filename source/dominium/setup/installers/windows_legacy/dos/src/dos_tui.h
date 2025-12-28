/*
FILE: source/dominium/setup/installers/windows_legacy/dos/src/dos_tui.h
MODULE: Dominium Setup (DOS)
PURPOSE: Text-mode UI helpers for DOS installer.
*/
#ifndef DSU_DOS_TUI_H_INCLUDED
#define DSU_DOS_TUI_H_INCLUDED

#include "../../legacy_core/include/dsu_legacy_core.h"

typedef struct dsu_dos_ui_result_t {
    dsu_legacy_u8 operation;
    dsu_legacy_u8 scope;
    int quick_mode;
    char *install_root;
    char **selected_components;
    dsu_legacy_u32 selected_component_count;
    dsu_legacy_u32 selected_component_cap;
    char **excluded_components;
    dsu_legacy_u32 excluded_component_count;
    dsu_legacy_u32 excluded_component_cap;
} dsu_dos_ui_result_t;

int dsu_dos_ui_collect(const char *manifest_path, dsu_dos_ui_result_t *out);
void dsu_dos_ui_free(dsu_dos_ui_result_t *out);

#endif /* DSU_DOS_TUI_H_INCLUDED */
