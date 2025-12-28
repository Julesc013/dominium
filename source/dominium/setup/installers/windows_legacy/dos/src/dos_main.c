/*
FILE: source/dominium/setup/installers/windows_legacy/dos/src/dos_main.c
MODULE: Dominium Setup (DOS)
PURPOSE: DOS entry point and CLI wrapper for legacy core.
*/
#include "dos_tui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int dsu_dos_extract_embedded_archive(const char *exe_path, const char *out_path);

static int dsu_dos_stricmp(const char *a, const char *b) {
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

static int dsu_dos_starts_with_ci(const char *s, const char *prefix) {
    if (!s || !prefix) return 0;
    while (*prefix) {
        unsigned char ca = (unsigned char)*s++;
        unsigned char cb = (unsigned char)*prefix++;
        if (ca >= 'A' && ca <= 'Z') ca = (unsigned char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (unsigned char)(cb - 'A' + 'a');
        if (ca != cb) return 0;
    }
    return 1;
}

static char *dsu_dos_strdup(const char *s) {
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

static int dsu_dos_list_push(char ***items, dsu_legacy_u32 *io_count, dsu_legacy_u32 *io_cap, const char *s) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char **p;
    char *dup;
    if (!items || !io_count || !io_cap || !s) return 0;
    dup = dsu_dos_strdup(s);
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

static void dsu_dos_free_list(char **items, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

static int dsu_dos_file_exists(const char *path) {
    FILE *f;
    if (!path) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static void dsu_dos_get_base_dir(const char *argv0, char *out, size_t cap) {
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

static void dsu_dos_print_usage(void) {
    printf("Dominium DOS Setup\n");
    printf("Usage:\n");
    printf("  INSTALL.EXE /E           Easy install (TUI)\n");
    printf("  INSTALL.EXE /C           Custom install (TUI)\n");
    printf("  INSTALL.EXE /U           Uninstall\n");
    printf("  INSTALL.EXE /V           Verify\n");
    printf("  INSTALL.EXE /R           Repair\n");
    printf("Options:\n");
    printf("  /DIR=PATH                Install directory\n");
    printf("  /MANIFEST=PATH           Manifest path\n");
    printf("  /PAYLOAD=PATH            Payload root\n");
    printf("  /STATE=PATH              Installed-state path\n");
    printf("  /LOG=PATH                Log path\n");
    printf("  --component <id>         Select component (repeat)\n");
    printf("  --exclude <id>           Exclude component (repeat)\n");
    printf("  --scope portable|user|system\n");
    printf("  --platform <triple>\n");
}

int main(int argc, char **argv) {
    int i;
    int use_tui = (argc <= 1);
    int do_detect = 0;
    int do_verify = 0;
    dsu_legacy_u8 operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    dsu_legacy_u8 scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
    char base_dir[260];
    char manifest_path[260];
    char payload_root[260];
    char install_root[260];
    char state_path[260];
    char log_path[260];
    const char *platform = "dos-x86";
    char **selected = NULL;
    dsu_legacy_u32 selected_count = 0u;
    dsu_legacy_u32 selected_cap = 0u;
    char **excluded = NULL;
    dsu_legacy_u32 excluded_count = 0u;
    dsu_legacy_u32 excluded_cap = 0u;

    dsu_dos_get_base_dir((argc > 0) ? argv[0] : NULL, base_dir, sizeof(base_dir));
    sprintf(manifest_path, "%s\\manifests\\dominium_legacy.dsumanifest", base_dir);
    sprintf(payload_root, "%s", base_dir);
    sprintf(install_root, "C:\\DOMINIUM");
    sprintf(state_path, "%s\\dominium_state.dsus", install_root);
    sprintf(log_path, "%s\\dominium_install.log", install_root);

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg || !arg[0]) continue;
        if (arg[0] == '/' || arg[0] == '-') {
            if (dsu_dos_stricmp(arg, "/E") == 0 || dsu_dos_stricmp(arg, "-E") == 0) {
                use_tui = 1;
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
            } else if (dsu_dos_stricmp(arg, "/C") == 0 || dsu_dos_stricmp(arg, "-C") == 0) {
                use_tui = 1;
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
            } else if (dsu_dos_stricmp(arg, "/U") == 0 || dsu_dos_stricmp(arg, "-U") == 0) {
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL;
            } else if (dsu_dos_stricmp(arg, "/V") == 0 || dsu_dos_stricmp(arg, "-V") == 0) {
                do_verify = 1;
            } else if (dsu_dos_stricmp(arg, "/R") == 0 || dsu_dos_stricmp(arg, "-R") == 0) {
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR;
            } else if (dsu_dos_starts_with_ci(arg, "/DIR=") || dsu_dos_starts_with_ci(arg, "-DIR=")) {
                strncpy(install_root, arg + 5, sizeof(install_root) - 1u);
                install_root[sizeof(install_root) - 1u] = '\0';
                sprintf(state_path, "%s\\dominium_state.dsus", install_root);
                sprintf(log_path, "%s\\dominium_install.log", install_root);
            } else if (dsu_dos_starts_with_ci(arg, "/MANIFEST=") || dsu_dos_starts_with_ci(arg, "-MANIFEST=")) {
                strncpy(manifest_path, arg + 10, sizeof(manifest_path) - 1u);
                manifest_path[sizeof(manifest_path) - 1u] = '\0';
            } else if (dsu_dos_starts_with_ci(arg, "/PAYLOAD=") || dsu_dos_starts_with_ci(arg, "-PAYLOAD=")) {
                strncpy(payload_root, arg + 9, sizeof(payload_root) - 1u);
                payload_root[sizeof(payload_root) - 1u] = '\0';
            } else if (dsu_dos_starts_with_ci(arg, "/STATE=") || dsu_dos_starts_with_ci(arg, "-STATE=")) {
                strncpy(state_path, arg + 7, sizeof(state_path) - 1u);
                state_path[sizeof(state_path) - 1u] = '\0';
            } else if (dsu_dos_starts_with_ci(arg, "/LOG=") || dsu_dos_starts_with_ci(arg, "-LOG=")) {
                strncpy(log_path, arg + 5, sizeof(log_path) - 1u);
                log_path[sizeof(log_path) - 1u] = '\0';
            } else if (dsu_dos_stricmp(arg, "--detect") == 0) {
                do_detect = 1;
            } else if (dsu_dos_stricmp(arg, "--install") == 0) {
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
            } else if (dsu_dos_stricmp(arg, "--repair") == 0) {
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR;
            } else if (dsu_dos_stricmp(arg, "--uninstall") == 0) {
                operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL;
            } else if (dsu_dos_stricmp(arg, "--verify") == 0) {
                do_verify = 1;
            } else if (dsu_dos_stricmp(arg, "--tui") == 0) {
                use_tui = 1;
            } else if (dsu_dos_stricmp(arg, "--cli") == 0) {
                use_tui = 0;
            } else if (dsu_dos_stricmp(arg, "--help") == 0 || dsu_dos_stricmp(arg, "-h") == 0) {
                dsu_dos_print_usage();
                dsu_dos_free_list(selected, selected_count);
                dsu_dos_free_list(excluded, excluded_count);
                return 0;
            } else if (dsu_dos_stricmp(arg, "--scope") == 0 && i + 1 < argc) {
                const char *s = argv[++i];
                if (dsu_dos_stricmp(s, "portable") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
                else if (dsu_dos_stricmp(s, "user") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
                else if (dsu_dos_stricmp(s, "system") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_SYSTEM;
            } else if (dsu_dos_stricmp(arg, "--platform") == 0 && i + 1 < argc) {
                platform = argv[++i];
            } else if (dsu_dos_stricmp(arg, "--component") == 0 && i + 1 < argc) {
                dsu_dos_list_push(&selected, &selected_count, &selected_cap, argv[++i]);
            } else if (dsu_dos_stricmp(arg, "--exclude") == 0 && i + 1 < argc) {
                dsu_dos_list_push(&excluded, &excluded_count, &excluded_cap, argv[++i]);
            }
        }
    }

    if (use_tui) {
        dsu_dos_ui_result_t ui;
        if (!dsu_dos_ui_collect(manifest_path, &ui)) {
            fprintf(stderr, "UI canceled or failed.\n");
            return 1;
        }
        operation = ui.operation;
        scope = ui.scope;
        if (ui.install_root && ui.install_root[0]) {
            strncpy(install_root, ui.install_root, sizeof(install_root) - 1u);
            install_root[sizeof(install_root) - 1u] = '\0';
            sprintf(state_path, "%s\\dominium_state.dsus", install_root);
            sprintf(log_path, "%s\\dominium_install.log", install_root);
        }
        dsu_dos_free_list(selected, selected_count);
        selected = ui.selected_components;
        selected_count = ui.selected_component_count;
        selected_cap = ui.selected_component_cap;
        ui.selected_components = NULL;
        ui.selected_component_count = 0u;
        ui.selected_component_cap = 0u;
        dsu_dos_free_list(excluded, excluded_count);
        excluded = ui.excluded_components;
        excluded_count = ui.excluded_component_count;
        excluded_cap = ui.excluded_component_cap;
        ui.excluded_components = NULL;
        ui.excluded_component_count = 0u;
        ui.excluded_component_cap = 0u;
        dsu_dos_ui_free(&ui);
    }

    if (do_detect) {
        int present = dsu_dos_file_exists(state_path);
        printf("installed=%s\n", present ? "yes" : "no");
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
        return present ? 0 : 1;
    }

    if (do_verify) {
        dsu_legacy_status_t st = dsu_legacy_verify(state_path, log_path);
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL) {
        dsu_legacy_status_t st = dsu_legacy_uninstall(state_path, log_path);
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR && !dsu_dos_file_exists(state_path)) {
        fprintf(stderr, "No installed state found.\n");
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
        return 2;
    }

    if (operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL && !dsu_dos_file_exists(manifest_path)) {
        fprintf(stderr, "Manifest not found: %s\n", manifest_path);
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
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
        inv.platform_triple = dsu_dos_strdup(platform);
        inv.ui_mode = dsu_dos_strdup(use_tui ? "tui" : "cli");
        inv.frontend_id = dsu_dos_strdup("dos-installer");
        if (install_root[0]) {
            dsu_dos_list_push(&inv.install_roots, &inv.install_root_count, &inv.install_root_cap, install_root);
        }
        for (j = 0u; j < selected_count; ++j) {
            dsu_dos_list_push(&inv.selected_components, &inv.selected_component_count, &inv.selected_component_cap, selected[j]);
        }
        for (j = 0u; j < excluded_count; ++j) {
            dsu_dos_list_push(&inv.excluded_components, &inv.excluded_component_count, &inv.excluded_component_cap, excluded[j]);
        }

        st = dsu_legacy_manifest_load(manifest_path, &manifest);
        if (st != DSU_LEGACY_STATUS_SUCCESS) {
            fprintf(stderr, "Failed to load manifest.\n");
            dsu_dos_free_list(inv.install_roots, inv.install_root_count);
            dsu_dos_free_list(inv.selected_components, inv.selected_component_count);
            dsu_dos_free_list(inv.excluded_components, inv.excluded_component_count);
            free(inv.platform_triple);
            free(inv.ui_mode);
            free(inv.frontend_id);
            dsu_dos_free_list(selected, selected_count);
            dsu_dos_free_list(excluded, excluded_count);
            return 2;
        }

        st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
        dsu_legacy_manifest_free(manifest);
        dsu_dos_free_list(inv.install_roots, inv.install_root_count);
        dsu_dos_free_list(inv.selected_components, inv.selected_component_count);
        dsu_dos_free_list(inv.excluded_components, inv.excluded_component_count);
        free(inv.platform_triple);
        free(inv.ui_mode);
        free(inv.frontend_id);
        dsu_dos_free_list(selected, selected_count);
        dsu_dos_free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }
}
