/*
FILE: source/dominium/setup/installers/windows_legacy/dos/src/dos_tui.c
MODULE: Dominium Setup (DOS)
PURPOSE: Text-mode wizard for DOS legacy installer.
*/
#include "dos_tui.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void dsu_dos_ui_init(dsu_dos_ui_result_t *out) {
    if (!out) return;
    memset(out, 0, sizeof(*out));
    out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    out->scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
    out->quick_mode = 1;
}

static void dsu_dos_ui_free_list(char **items, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

void dsu_dos_ui_free(dsu_dos_ui_result_t *out) {
    if (!out) return;
    free(out->install_root);
    dsu_dos_ui_free_list(out->selected_components, out->selected_component_count);
    dsu_dos_ui_free_list(out->excluded_components, out->excluded_component_count);
    dsu_dos_ui_init(out);
}

static int dsu_dos_ui_list_push(char ***items, dsu_legacy_u32 *io_count, dsu_legacy_u32 *io_cap, const char *s) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 cap;
    char **p;
    char *dup;
    if (!items || !io_count || !io_cap || !s) return 0;
    dup = (char *)malloc(strlen(s) + 1u);
    if (!dup) return 0;
    strcpy(dup, s);
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

static int dsu_dos_ui_read_line(char *buf, size_t cap) {
    if (!buf || cap == 0u) return 0;
    if (!fgets(buf, (int)cap, stdin)) return 0;
    buf[cap - 1u] = '\0';
    {
        size_t n = strlen(buf);
        while (n > 0u && (buf[n - 1u] == '\n' || buf[n - 1u] == '\r')) {
            buf[n - 1u] = '\0';
            --n;
        }
    }
    return 1;
}

static int dsu_dos_ui_prompt_number(const char *prompt, int min, int max, int def_value) {
    char buf[64];
    int v;
    for (;;) {
        printf("%s [%d]: ", prompt, def_value);
        if (!dsu_dos_ui_read_line(buf, sizeof(buf))) return def_value;
        if (buf[0] == '\0') return def_value;
        v = atoi(buf);
        if (v >= min && v <= max) return v;
        printf("Invalid choice.\n");
    }
}

static int dsu_dos_ui_prompt_yesno(const char *prompt, int def_yes) {
    char buf[16];
    for (;;) {
        printf("%s [%s]: ", prompt, def_yes ? "Y" : "N");
        if (!dsu_dos_ui_read_line(buf, sizeof(buf))) return def_yes;
        if (buf[0] == '\0') return def_yes;
        if (buf[0] == 'y' || buf[0] == 'Y') return 1;
        if (buf[0] == 'n' || buf[0] == 'N') return 0;
        printf("Please answer Y or N.\n");
    }
}

static void dsu_dos_ui_prompt_path(const char *prompt, const char *def_path, char *out, size_t cap) {
    char buf[260];
    printf("%s [%s]: ", prompt, def_path ? def_path : "");
    if (dsu_dos_ui_read_line(buf, sizeof(buf)) && buf[0] != '\0') {
        strncpy(out, buf, cap - 1u);
        out[cap - 1u] = '\0';
    } else if (def_path) {
        strncpy(out, def_path, cap - 1u);
        out[cap - 1u] = '\0';
    } else if (cap > 0u) {
        out[0] = '\0';
    }
}

static void dsu_dos_ui_select_components(const dsu_legacy_manifest_t *m,
                                         dsu_dos_ui_result_t *out) {
    dsu_legacy_u32 i;
    char buf[256];
    if (!m || !out) return;
    if (m->component_count == 0u) return;
    printf("\nComponents:\n");
    for (i = 0u; i < m->component_count; ++i) {
        printf("  %u) %s\n", (unsigned int)(i + 1u), m->components[i].id ? m->components[i].id : "(unnamed)");
    }
    printf("Enter component numbers separated by commas (Enter for defaults): ");
    if (!dsu_dos_ui_read_line(buf, sizeof(buf)) || buf[0] == '\0') {
        return;
    }
    {
        char *p = buf;
        while (*p) {
            char *end;
            int idx;
            while (*p == ' ' || *p == '\t' || *p == ',') ++p;
            if (!*p) break;
            end = p;
            while (*end && *end != ',') ++end;
            if (*end) *end++ = '\0';
            idx = atoi(p);
            if (idx > 0 && (dsu_legacy_u32)idx <= m->component_count) {
                const char *id = m->components[idx - 1u].id;
                if (id && id[0]) {
                    dsu_dos_ui_list_push(&out->selected_components,
                                         &out->selected_component_count,
                                         &out->selected_component_cap,
                                         id);
                }
            }
            p = end;
        }
    }
}

int dsu_dos_ui_collect(const char *manifest_path, dsu_dos_ui_result_t *out) {
    int choice;
    dsu_legacy_manifest_t *manifest = NULL;
    if (!out) return 0;
    dsu_dos_ui_init(out);

    printf("Dominium DOS Setup\n");
    printf("==================\n\n");
    printf("1) Install/Upgrade\n");
    printf("2) Repair\n");
    printf("3) Uninstall\n");
    printf("4) Verify\n");
    choice = dsu_dos_ui_prompt_number("Select operation", 1, 4, 1);
    if (choice == 2) out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR;
    else if (choice == 3) out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_UNINSTALL;
    else if (choice == 4) out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    else out->operation = (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;

    if (choice == 4) {
        return 1;
    }

    out->quick_mode = dsu_dos_ui_prompt_yesno("Use Quick Install", 1);
    out->scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;

    {
        char path_buf[260];
        dsu_dos_ui_prompt_path("Install path", "C:\\DOMINIUM", path_buf, sizeof(path_buf));
        out->install_root = (char *)malloc(strlen(path_buf) + 1u);
        if (!out->install_root) {
            dsu_dos_ui_free(out);
            return 0;
        }
        strcpy(out->install_root, path_buf);
    }

    if (!out->quick_mode && manifest_path && manifest_path[0]) {
        if (dsu_legacy_manifest_load(manifest_path, &manifest) == DSU_LEGACY_STATUS_SUCCESS) {
            dsu_dos_ui_select_components(manifest, out);
            dsu_legacy_manifest_free(manifest);
        }
    }

    return 1;
}
