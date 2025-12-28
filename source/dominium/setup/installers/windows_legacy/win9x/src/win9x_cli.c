/*
FILE: source/dominium/setup/installers/windows_legacy/win9x/src/win9x_cli.c
MODULE: Dominium Setup (Win9x)
PURPOSE: CLI entry helpers for Win9x legacy installer.
*/
#include "win9x_tui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

static char *win9x_strdup(const char *s) {
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

static int win9x_file_exists(const char *path) {
    FILE *f;
    if (!path) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static void win9x_free_list(char **items, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

static int win9x_list_push(char ***items, dsu_legacy_u32 *io_count, dsu_legacy_u32 *io_cap, const char *s) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char **p;
    char *dup;
    if (!items || !io_count || !io_cap || !s) return 0;
    dup = win9x_strdup(s);
    if (!dup) return 0;
    count = *io_count;
    cap = *io_cap;
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (char **)realloc(*items, (size_t)new_cap * sizeof(*p));
        if (!p) {
            free(dup);
            return 0;
        }
        *items = p;
        *io_cap = new_cap;
    }
    (*items)[count] = dup;
    *io_count = count + 1u;
    return 1;
}

int dsu_win9x_run_cli(int argc, char **argv) {
    int i;
    dsu_legacy_u8 operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    int do_verify = 0;
    int do_detect = 0;
    dsu_legacy_u8 scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
    const char *manifest_path = "manifests\\dominium_legacy.dsumanifest";
    const char *payload_root = ".";
    const char *install_root = "C:\\Program Files\\Dominium";
    const char *state_path = "C:\\Program Files\\Dominium\\dominium_state.dsus";
    const char *log_path = "C:\\Program Files\\Dominium\\dominium_install.log";
    const char *platform = "win32-9x-x86";
    char **selected = NULL;
    dsu_legacy_u32 selected_count = 0u;
    dsu_legacy_u32 selected_cap = 0u;
    char **excluded = NULL;
    dsu_legacy_u32 excluded_count = 0u;
    dsu_legacy_u32 excluded_cap = 0u;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (win9x_stricmp(arg, "--install") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
        } else if (win9x_stricmp(arg, "--repair") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR;
        } else if (win9x_stricmp(arg, "--uninstall") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL;
        } else if (win9x_stricmp(arg, "--verify") == 0) {
            do_verify = 1;
        } else if (win9x_stricmp(arg, "--detect") == 0) {
            do_detect = 1;
        } else if (win9x_stricmp(arg, "--manifest") == 0 && i + 1 < argc) {
            manifest_path = argv[++i];
        } else if (win9x_stricmp(arg, "--payload-root") == 0 && i + 1 < argc) {
            payload_root = argv[++i];
        } else if (win9x_stricmp(arg, "--install-root") == 0 && i + 1 < argc) {
            install_root = argv[++i];
        } else if (win9x_stricmp(arg, "--state") == 0 && i + 1 < argc) {
            state_path = argv[++i];
        } else if (win9x_stricmp(arg, "--log") == 0 && i + 1 < argc) {
            log_path = argv[++i];
        } else if (win9x_stricmp(arg, "--component") == 0 && i + 1 < argc) {
            win9x_list_push(&selected, &selected_count, &selected_cap, argv[++i]);
        } else if (win9x_stricmp(arg, "--exclude") == 0 && i + 1 < argc) {
            win9x_list_push(&excluded, &excluded_count, &excluded_cap, argv[++i]);
        } else if (win9x_stricmp(arg, "--scope") == 0 && i + 1 < argc) {
            const char *s = argv[++i];
            if (win9x_stricmp(s, "portable") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
            else if (win9x_stricmp(s, "user") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
            else if (win9x_stricmp(s, "system") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_SYSTEM;
        } else if (win9x_stricmp(arg, "--platform") == 0 && i + 1 < argc) {
            platform = argv[++i];
        }
    }

    if (do_verify) {
        dsu_legacy_status_t st = dsu_legacy_verify(state_path, log_path);
        win9x_free_list(selected, selected_count);
        win9x_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (do_detect) {
        int present = win9x_file_exists(state_path);
        printf("installed=%s\n", present ? "yes" : "no");
        win9x_free_list(selected, selected_count);
        win9x_free_list(excluded, excluded_count);
        return present ? 0 : 1;
    }

    if (operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL) {
        dsu_legacy_status_t st = dsu_legacy_uninstall(state_path, log_path);
        win9x_free_list(selected, selected_count);
        win9x_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (!win9x_file_exists(manifest_path)) {
        fprintf(stderr, "Manifest not found: %s\n", manifest_path);
        win9x_free_list(selected, selected_count);
        win9x_free_list(excluded, excluded_count);
        return 2;
    }

    {
        dsu_legacy_manifest_t *manifest = NULL;
        dsu_legacy_invocation_t inv;
        dsu_legacy_status_t st;
        dsu_legacy_u32 j;
        memset(&inv, 0, sizeof(inv));
        inv.operation = operation;
        inv.scope = scope;
        inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                           DSU_LEGACY_POLICY_DETERMINISTIC |
                           DSU_LEGACY_POLICY_LEGACY_MODE;
        inv.platform_triple = win9x_strdup(platform);
        inv.ui_mode = win9x_strdup("cli");
        inv.frontend_id = win9x_strdup("win9x-cli");
        if (install_root && install_root[0]) {
            win9x_list_push(&inv.install_roots, &inv.install_root_count, &inv.install_root_cap, install_root);
        }
        for (j = 0u; j < selected_count; ++j) {
            win9x_list_push(&inv.selected_components, &inv.selected_component_count, &inv.selected_component_cap, selected[j]);
        }
        for (j = 0u; j < excluded_count; ++j) {
            win9x_list_push(&inv.excluded_components, &inv.excluded_component_count, &inv.excluded_component_cap, excluded[j]);
        }

        st = dsu_legacy_manifest_load(manifest_path, &manifest);
        if (st != DSU_LEGACY_STATUS_SUCCESS) {
            fprintf(stderr, "manifest load failed\n");
            win9x_free_list(inv.install_roots, inv.install_root_count);
            win9x_free_list(inv.selected_components, inv.selected_component_count);
            win9x_free_list(inv.excluded_components, inv.excluded_component_count);
            free(inv.platform_triple);
            free(inv.ui_mode);
            free(inv.frontend_id);
            win9x_free_list(selected, selected_count);
            win9x_free_list(excluded, excluded_count);
            return 2;
        }

        st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
        dsu_legacy_manifest_free(manifest);
        win9x_free_list(inv.install_roots, inv.install_root_count);
        win9x_free_list(inv.selected_components, inv.selected_component_count);
        win9x_free_list(inv.excluded_components, inv.excluded_component_count);
        free(inv.platform_triple);
        free(inv.ui_mode);
        free(inv.frontend_id);
        win9x_free_list(selected, selected_count);
        win9x_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }
}
