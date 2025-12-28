/*
FILE: source/dominium/setup/installers/windows_legacy/win9x/src/win9x_main.c
MODULE: Dominium Setup (Win9x)
PURPOSE: Win9x entry point with GUI/TUI/CLI modes.
*/
#include "win9x_tui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int dsu_win9x_run_cli(int argc, char **argv);
int dsu_win9x_run_gui(const char *manifest_path,
                      const char *payload_root,
                      const char *platform,
                      const char *frontend_id);

static int win9x_stricmp(const char *a, const char *b) {
    unsigned char ca;
    unsigned char cb;
    if (!a || !b) return (a == b) ? 0 : (a ? 1 : -1);
    while (*a && *b) {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
        if (ca >= 'A' && ca <= 'Z') ca = (unsigned char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (unsigned char)(cb - 'A' + 'a');
        if (ca != cb) return (int)ca - (int)cb;
    }
    return (int)(unsigned char)*a - (int)(unsigned char)*b;
}

static void win9x_get_base_dir(const char *argv0, char *out, size_t cap) {
    const char *p;
    size_t n = 0u;
    if (!out || cap == 0u) return;
    if (!argv0 || argv0[0] == '\0') {
        out[0] = '.';
        out[1] = '\0';
        return;
    }
    p = argv0 + strlen(argv0);
    while (p > argv0 && p[-1] != '\\' && p[-1] != '/') --p;
    n = (size_t)(p - argv0);
    if (n == 0u || n >= cap) {
        out[0] = '.';
        out[1] = '\0';
        return;
    }
    memcpy(out, argv0, n);
    out[n] = '\0';
}

int main(int argc, char **argv) {
    int i;
    int use_cli = 0;
    int use_tui = (argc <= 1);
    char base_dir[260];
    char manifest_path[260];
    char payload_root[260];

    for (i = 1; i < argc; ++i) {
        if (win9x_stricmp(argv[i], "--cli") == 0) {
            use_cli = 1;
        } else if (win9x_stricmp(argv[i], "--tui") == 0) {
            use_tui = 1;
        } else if (win9x_stricmp(argv[i], "--gui") == 0) {
            use_tui = 0;
        }
    }

    if (use_cli) {
        return dsu_win9x_run_cli(argc, argv);
    }

    win9x_get_base_dir((argc > 0) ? argv[0] : NULL, base_dir, sizeof(base_dir));
    sprintf(manifest_path, "%s\\manifests\\dominium_legacy.dsumanifest", base_dir);
    sprintf(payload_root, "%s", base_dir);

    if (!use_tui) {
        return dsu_win9x_run_gui(manifest_path, payload_root, "win32-9x-x86", "win9x-gui");
    }

    {
        dsu_win9x_ui_result_t ui;
        dsu_legacy_manifest_t *manifest = NULL;
        dsu_legacy_invocation_t inv;
        dsu_legacy_status_t st;
        char state_path[260];
        char log_path[260];
        int result = 1;

        if (!dsu_win9x_ui_collect(manifest_path, &ui)) {
            fprintf(stderr, "UI canceled or failed.\n");
            return 1;
        }

        sprintf(state_path, "%s\\dominium_state.dsus", ui.install_root ? ui.install_root : "C:\\Program Files\\Dominium");
        sprintf(log_path, "%s\\dominium_install.log", ui.install_root ? ui.install_root : "C:\\Program Files\\Dominium");

        if (dsu_legacy_manifest_load(manifest_path, &manifest) != DSU_LEGACY_STATUS_SUCCESS) {
            fprintf(stderr, "Failed to load manifest.\n");
            dsu_win9x_ui_free(&ui);
            return 2;
        }

        memset(&inv, 0, sizeof(inv));
        inv.operation = ui.operation;
        inv.scope = ui.scope;
        inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                           DSU_LEGACY_POLICY_DETERMINISTIC |
                           DSU_LEGACY_POLICY_LEGACY_MODE;
        inv.platform_triple = _strdup("win32-9x-x86");
        inv.ui_mode = _strdup("tui");
        inv.frontend_id = _strdup("win9x-tui");
        if (ui.install_root) {
            inv.install_roots = (char **)malloc(sizeof(char *));
            if (inv.install_roots) {
                inv.install_roots[0] = _strdup(ui.install_root);
                if (inv.install_roots[0]) {
                    inv.install_root_count = 1u;
                    inv.install_root_cap = 1u;
                }
            }
        }
        inv.selected_components = ui.selected_components;
        inv.selected_component_count = ui.selected_component_count;
        inv.selected_component_cap = ui.selected_component_cap;
        ui.selected_components = NULL;
        ui.selected_component_count = 0u;
        ui.selected_component_cap = 0u;

        st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;

        dsu_legacy_manifest_free(manifest);
        if (inv.install_roots) {
            free(inv.install_roots[0]);
            free(inv.install_roots);
        }
        if (inv.selected_components) {
            dsu_legacy_u32 j;
            for (j = 0u; j < inv.selected_component_count; ++j) {
                free(inv.selected_components[j]);
            }
            free(inv.selected_components);
        }
        free(inv.platform_triple);
        free(inv.ui_mode);
        free(inv.frontend_id);
        dsu_win9x_ui_free(&ui);
        return result;
    }
}
