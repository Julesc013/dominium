/*
FILE: source/dominium/setup/installers/macos_classic/gui/classic_installer_app/src/main.c
MODULE: Dominium Setup (Classic GUI)
PURPOSE: Classic installer entry point (GUI + minimal CLI).
*/
#include "dialogs.h"

#include "../../../core_legacy/include/dsu_legacy_core.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(void) {
    printf("Dominium Classic Setup\n");
    printf("Usage:\n");
    printf("  Dominium Installer (GUI): run without arguments\n");
    printf("  CLI:\n");
    printf("    --install | --repair | --uninstall | --verify | --detect\n");
    printf("    --manifest <path>\n");
    printf("    --payload-root <path>\n");
    printf("    --install-root <path>\n");
    printf("    --state <path>\n");
    printf("    --log <path>\n");
    printf("    --component <id> (repeatable)\n");
    printf("    --exclude <id> (repeatable)\n");
    printf("    --scope portable|user|system\n");
    printf("    --platform <triple>\n");
}

static char *dup_str(const char *s) {
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

static int file_exists(const char *path) {
    FILE *f;
    if (!path) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static void ascii_lower_inplace(char *s) {
    unsigned char *p;
    if (!s) return;
    p = (unsigned char *)s;
    while (*p) {
        if (*p >= 'A' && *p <= 'Z') {
            *p = (unsigned char)(*p - 'A' + 'a');
        }
        ++p;
    }
}

static int list_push(char ***items, dsu_legacy_u32 *io_count, dsu_legacy_u32 *io_cap, const char *s) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char **p;
    char *dup;
    if (!items || !io_count || !io_cap || !s) return 0;
    dup = dup_str(s);
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

static void free_list(char **items, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

static int run_cli(int argc, char **argv) {
    int i;
    dsu_legacy_u8 operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    int do_verify = 0;
    int do_detect = 0;
    dsu_legacy_u8 scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
    const char *manifest_path = NULL;
    const char *payload_root = ".";
    const char *install_root = NULL;
    const char *state_path = "dominium_state.dsus";
    const char *log_path = "dominium_install.log";
    const char *platform = "macos-x86";
    char **selected = NULL;
    dsu_legacy_u32 selected_count = 0u;
    dsu_legacy_u32 selected_cap = 0u;
    char **excluded = NULL;
    dsu_legacy_u32 excluded_count = 0u;
    dsu_legacy_u32 excluded_cap = 0u;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (strcmp(arg, "--install") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
        } else if (strcmp(arg, "--repair") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR;
        } else if (strcmp(arg, "--uninstall") == 0) {
            operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL;
        } else if (strcmp(arg, "--verify") == 0) {
            do_verify = 1;
        } else if (strcmp(arg, "--detect") == 0) {
            do_detect = 1;
        } else if (strcmp(arg, "--manifest") == 0 && i + 1 < argc) {
            manifest_path = argv[++i];
        } else if (strcmp(arg, "--payload-root") == 0 && i + 1 < argc) {
            payload_root = argv[++i];
        } else if (strcmp(arg, "--install-root") == 0 && i + 1 < argc) {
            install_root = argv[++i];
        } else if (strcmp(arg, "--state") == 0 && i + 1 < argc) {
            state_path = argv[++i];
        } else if (strcmp(arg, "--log") == 0 && i + 1 < argc) {
            log_path = argv[++i];
        } else if (strcmp(arg, "--component") == 0 && i + 1 < argc) {
            if (!list_push(&selected, &selected_count, &selected_cap, argv[++i])) {
                fprintf(stderr, "out of memory\n");
                free_list(selected, selected_count);
                free_list(excluded, excluded_count);
                return 1;
            }
            ascii_lower_inplace(selected[selected_count - 1u]);
        } else if (strcmp(arg, "--exclude") == 0 && i + 1 < argc) {
            if (!list_push(&excluded, &excluded_count, &excluded_cap, argv[++i])) {
                fprintf(stderr, "out of memory\n");
                free_list(selected, selected_count);
                free_list(excluded, excluded_count);
                return 1;
            }
            ascii_lower_inplace(excluded[excluded_count - 1u]);
        } else if (strcmp(arg, "--scope") == 0 && i + 1 < argc) {
            const char *s = argv[++i];
            if (strcmp(s, "portable") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
            else if (strcmp(s, "user") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
            else if (strcmp(s, "system") == 0) scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_SYSTEM;
        } else if (strcmp(arg, "--platform") == 0 && i + 1 < argc) {
            platform = argv[++i];
        } else if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            print_usage();
            free_list(selected, selected_count);
            free_list(excluded, excluded_count);
            return 0;
        } else {
            fprintf(stderr, "unknown arg: %s\n", arg);
            print_usage();
            free_list(selected, selected_count);
            free_list(excluded, excluded_count);
            return 1;
        }
    }

    if (do_verify) {
        dsu_legacy_status_t st = dsu_legacy_verify(state_path, log_path);
        free_list(selected, selected_count);
        free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (do_detect) {
        int present = file_exists(state_path);
        printf("installed=%s\n", present ? "yes" : "no");
        free_list(selected, selected_count);
        free_list(excluded, excluded_count);
        return present ? 0 : 1;
    }

    if (operation == (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL) {
        dsu_legacy_status_t st = dsu_legacy_uninstall(state_path, log_path);
        free_list(selected, selected_count);
        free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }

    if (!manifest_path) {
        manifest_path = "Manifests/dominium_full.dsumanifest";
    }

    {
        dsu_legacy_manifest_t *manifest = NULL;
        dsu_legacy_invocation_t inv;
        dsu_legacy_status_t st;
        dsu_legacy_u32 i2;
        memset(&inv, 0, sizeof(inv));
        inv.operation = operation;
        inv.scope = scope;
        inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                           DSU_LEGACY_POLICY_DETERMINISTIC |
                           DSU_LEGACY_POLICY_LEGACY_MODE;
        inv.platform_triple = dup_str(platform);
        inv.ui_mode = dup_str("cli");
        inv.frontend_id = dup_str("classic-cli");
        if (install_root && install_root[0] != '\0') {
            list_push(&inv.install_roots, &inv.install_root_count, &inv.install_root_cap, install_root);
        }
        for (i2 = 0u; i2 < selected_count; ++i2) {
            list_push(&inv.selected_components, &inv.selected_component_count, &inv.selected_component_cap, selected[i2]);
        }
        for (i2 = 0u; i2 < excluded_count; ++i2) {
            list_push(&inv.excluded_components, &inv.excluded_component_count, &inv.excluded_component_cap, excluded[i2]);
        }

        st = dsu_legacy_manifest_load(manifest_path, &manifest);
        if (st != DSU_LEGACY_STATUS_SUCCESS) {
            fprintf(stderr, "manifest load failed\n");
            free_list(inv.install_roots, inv.install_root_count);
            free_list(inv.selected_components, inv.selected_component_count);
            free_list(inv.excluded_components, inv.excluded_component_count);
            free(inv.platform_triple);
            free(inv.ui_mode);
            free(inv.frontend_id);
            free_list(selected, selected_count);
            free_list(excluded, excluded_count);
            return 2;
        }

        st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
        dsu_legacy_manifest_free(manifest);
        free_list(inv.install_roots, inv.install_root_count);
        free_list(inv.selected_components, inv.selected_component_count);
        free_list(inv.excluded_components, inv.excluded_component_count);
        free(inv.platform_triple);
        free(inv.ui_mode);
        free(inv.frontend_id);
        free_list(selected, selected_count);
        free_list(excluded, excluded_count);
        return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    }
}

static int run_gui(void) {
    dsu_classic_ui_result_t ui;
    dsu_legacy_manifest_t *manifest = NULL;
    dsu_legacy_invocation_t inv;
    dsu_legacy_status_t st;
    const char *manifest_path = "Manifests/dominium_full.dsumanifest";
    const char *payload_root = "Payloads";
    const char *state_path = "Preferences:Dominium:dominium_state.dsus";
    const char *log_path = "Preferences:Dominium:dominium_install.log";

    if (!dsu_classic_ui_collect(&ui)) {
        return 1;
    }

    st = dsu_legacy_manifest_load(manifest_path, &manifest);
    if (st != DSU_LEGACY_STATUS_SUCCESS) {
        dsu_classic_ui_free(&ui);
        return 2;
    }

    memset(&inv, 0, sizeof(inv));
    inv.operation = ui.operation;
    inv.scope = ui.scope;
    inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                       DSU_LEGACY_POLICY_DETERMINISTIC |
                       DSU_LEGACY_POLICY_LEGACY_MODE;
    inv.platform_triple = dup_str("macos-x86");
    inv.ui_mode = dup_str("gui");
    inv.frontend_id = dup_str("classic-gui");
    if (ui.install_root) {
        list_push(&inv.install_roots, &inv.install_root_count, &inv.install_root_cap, ui.install_root);
    }
    if (ui.selected_component_count) {
        dsu_legacy_u32 i;
        for (i = 0u; i < ui.selected_component_count; ++i) {
            list_push(&inv.selected_components, &inv.selected_component_count, &inv.selected_component_cap, ui.selected_components[i]);
            ascii_lower_inplace(inv.selected_components[inv.selected_component_count - 1u]);
        }
    }
    if (ui.excluded_component_count) {
        dsu_legacy_u32 i;
        for (i = 0u; i < ui.excluded_component_count; ++i) {
            list_push(&inv.excluded_components, &inv.excluded_component_count, &inv.excluded_component_cap, ui.excluded_components[i]);
            ascii_lower_inplace(inv.excluded_components[inv.excluded_component_count - 1u]);
        }
    }

    st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
    dsu_legacy_manifest_free(manifest);
    dsu_classic_ui_free(&ui);
    free_list(inv.install_roots, inv.install_root_count);
    free_list(inv.selected_components, inv.selected_component_count);
    free_list(inv.excluded_components, inv.excluded_component_count);
    free(inv.platform_triple);
    free(inv.ui_mode);
    free(inv.frontend_id);
    return (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
}

int main(int argc, char **argv) {
    if (argc > 1) {
        return run_cli(argc, argv);
    }
    return run_gui();
}
