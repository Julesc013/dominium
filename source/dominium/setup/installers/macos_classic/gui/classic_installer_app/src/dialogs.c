/*
FILE: source/dominium/setup/installers/macos_classic/gui/classic_installer_app/src/dialogs.c
MODULE: Dominium Setup (Classic GUI)
PURPOSE: Period-correct dialog flow (stubbed defaults for host builds).
*/
#include "dialogs.h"

#include <stdlib.h>
#include <string.h>

#if defined(DSU_CLASSIC_MAC)
/* Classic Mac OS headers (Dialog Manager) */
#include <Dialogs.h>
#include <Resources.h>
#include <Windows.h>
#endif

static char *dsu_classic_strdup(const char *s) {
    size_t n;
    char *p;
    if (!s) return NULL;
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) return NULL;
    memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

int dsu_classic_ui_collect(dsu_classic_ui_result_t *out) {
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    out->scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_SYSTEM;
    out->install_root = dsu_classic_strdup("Applications:Dominium");

#if defined(DSU_CLASSIC_MAC)
    /* TODO: Implement full dialog wizard using resources.r */
    /* Placeholder: show a welcome alert and accept defaults */
    (void)StopAlert(128, NULL);
#endif

    return out->install_root != NULL;
}

void dsu_classic_ui_free(dsu_classic_ui_result_t *out) {
    dsu_legacy_u32 i;
    if (!out) return;
    free(out->install_root);
    for (i = 0u; i < out->selected_component_count; ++i) {
        free(out->selected_components[i]);
    }
    free(out->selected_components);
    for (i = 0u; i < out->excluded_component_count; ++i) {
        free(out->excluded_components[i]);
    }
    free(out->excluded_components);
    memset(out, 0, sizeof(*out));
}
