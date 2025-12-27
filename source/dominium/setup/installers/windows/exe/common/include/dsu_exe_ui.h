#ifndef DSU_EXE_UI_H_INCLUDED
#define DSU_EXE_UI_H_INCLUDED

#include "dsu/dsu_manifest.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_ui_step_t {
    DSU_UI_STEP_DETECT = 0,
    DSU_UI_STEP_OPERATION,
    DSU_UI_STEP_MODE,
    DSU_UI_STEP_SCOPE,
    DSU_UI_STEP_PATHS,
    DSU_UI_STEP_COMPONENTS,
    DSU_UI_STEP_SUMMARY,
    DSU_UI_STEP_EXECUTE,
    DSU_UI_STEP_COMPLETE
} dsu_ui_step_t;

typedef enum dsu_ui_install_mode_t {
    DSU_UI_INSTALL_MODE_QUICK = 0,
    DSU_UI_INSTALL_MODE_CUSTOM = 1
} dsu_ui_install_mode_t;

typedef struct dsu_ui_state_t {
    dsu_ui_step_t step;
    dsu_ui_install_mode_t install_mode;
    dsu_manifest_install_scope_t scope;
    dsu_u8 operation;
    int installed_detected;

    char install_root[512];
    char **selected_components;
    unsigned long selected_count;
    char **excluded_components;
    unsigned long excluded_count;

    int enable_shortcuts;
    int enable_file_assoc;
    int enable_url_handlers;
} dsu_ui_state_t;

void dsu_ui_state_init(dsu_ui_state_t *state);
const char *dsu_ui_step_label(dsu_ui_step_t step);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_UI_H_INCLUDED */
