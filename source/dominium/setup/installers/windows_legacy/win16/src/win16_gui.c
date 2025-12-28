/*
FILE: source/dominium/setup/installers/windows_legacy/win16/src/win16_gui.c
MODULE: Dominium Setup (Win16)
PURPOSE: Win16 dialog UI for legacy installer.
*/
#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>

#include "../../legacy_core/include/dsu_legacy_core.h"

#include <stdlib.h>
#include <string.h>

#define IDD_MAIN        100
#define IDC_EASY        200
#define IDC_CUSTOM      201
#define IDC_PATH        202
#define IDC_COMPONENTS  203
#define IDC_INSTALL     210
#define IDC_REPAIR      211
#define IDC_VERIFY      212
#define IDC_UNINSTALL   213

#define DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED 0x00000002u

static dsu_legacy_manifest_t *g_manifest = NULL;
static char g_install_root[260] = "C:\\DOMINIUM";
static int g_action = 0;
static int g_custom = 0;
static char **g_selected = NULL;
static dsu_legacy_u32 g_selected_count = 0u;
static dsu_legacy_u32 g_selected_cap = 0u;

static void win16_free_selected(void) {
    dsu_legacy_u32 i;
    for (i = 0u; i < g_selected_count; ++i) {
        free(g_selected[i]);
    }
    free(g_selected);
    g_selected = NULL;
    g_selected_count = 0u;
    g_selected_cap = 0u;
}

static int win16_list_push(const char *s) {
    dsu_legacy_u32 count = g_selected_count;
    dsu_legacy_u32 cap = g_selected_cap;
    char **p;
    char *dup;
    if (!s) return 0;
    dup = (char *)malloc(strlen(s) + 1u);
    if (!dup) return 0;
    strcpy(dup, s);
    if (count == cap) {
        dsu_legacy_u32 new_cap = (cap == 0u) ? 4u : (cap * 2u);
        p = (char **)realloc(g_selected, (size_t)new_cap * sizeof(*p));
        if (!p) {
            free(dup);
            return 0;
        }
        g_selected = p;
        g_selected_cap = new_cap;
    }
    g_selected[count] = dup;
    g_selected_count = count + 1u;
    return 1;
}

static void win16_free_list(char **items, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (!items) return;
    for (i = 0u; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

static void win16_populate_components(HWND hDlg) {
    dsu_legacy_u32 i;
    if (!g_manifest) return;
    for (i = 0u; i < g_manifest->component_count; ++i) {
        const char *id = g_manifest->components[i].id ? g_manifest->components[i].id : "";
        LRESULT idx = SendDlgItemMessage(hDlg, IDC_COMPONENTS, LB_ADDSTRING, 0, (LPARAM)id);
        if (idx >= 0) {
            if ((g_manifest->components[i].flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) != 0u) {
                SendDlgItemMessage(hDlg, IDC_COMPONENTS, LB_SETSEL, TRUE, idx);
            }
        }
    }
}

static void win16_capture_selection(HWND hDlg) {
    LRESULT count;
    int i;
    char buf[128];
    win16_free_selected();
    count = SendDlgItemMessage(hDlg, IDC_COMPONENTS, LB_GETCOUNT, 0, 0);
    if (count <= 0) return;
    for (i = 0; i < (int)count; ++i) {
        LRESULT sel = SendDlgItemMessage(hDlg, IDC_COMPONENTS, LB_GETSEL, (WPARAM)i, 0);
        if (sel > 0) {
            SendDlgItemMessage(hDlg, IDC_COMPONENTS, LB_GETTEXT, (WPARAM)i, (LPARAM)buf);
            buf[sizeof(buf) - 1u] = '\0';
            win16_list_push(buf);
        }
    }
}

static void win16_set_custom(HWND hDlg, int custom) {
    g_custom = custom ? 1 : 0;
    EnableWindow(GetDlgItem(hDlg, IDC_COMPONENTS), g_custom ? TRUE : FALSE);
}

static BOOL CALLBACK win16_main_dlgproc(HWND hDlg, UINT msg, WPARAM wParam, LPARAM lParam) {
    (void)lParam;
    switch (msg) {
    case WM_INITDIALOG:
        SetDlgItemText(hDlg, IDC_PATH, g_install_root);
        CheckRadioButton(hDlg, IDC_EASY, IDC_CUSTOM, IDC_EASY);
        win16_set_custom(hDlg, 0);
        win16_populate_components(hDlg);
        return TRUE;
    case WM_COMMAND:
        switch (wParam) {
        case IDC_EASY:
            CheckRadioButton(hDlg, IDC_EASY, IDC_CUSTOM, IDC_EASY);
            win16_set_custom(hDlg, 0);
            return TRUE;
        case IDC_CUSTOM:
            CheckRadioButton(hDlg, IDC_EASY, IDC_CUSTOM, IDC_CUSTOM);
            win16_set_custom(hDlg, 1);
            return TRUE;
        case IDC_INSTALL:
            g_action = 1;
            GetDlgItemText(hDlg, IDC_PATH, g_install_root, sizeof(g_install_root) - 1u);
            g_install_root[sizeof(g_install_root) - 1u] = '\0';
            win16_capture_selection(hDlg);
            EndDialog(hDlg, 1);
            return TRUE;
        case IDC_REPAIR:
            g_action = 2;
            GetDlgItemText(hDlg, IDC_PATH, g_install_root, sizeof(g_install_root) - 1u);
            g_install_root[sizeof(g_install_root) - 1u] = '\0';
            win16_capture_selection(hDlg);
            EndDialog(hDlg, 1);
            return TRUE;
        case IDC_VERIFY:
            g_action = 3;
            EndDialog(hDlg, 1);
            return TRUE;
        case IDC_UNINSTALL:
            g_action = 4;
            EndDialog(hDlg, 1);
            return TRUE;
        case IDCANCEL:
            g_action = 0;
            EndDialog(hDlg, 0);
            return TRUE;
        default:
            break;
        }
        break;
    default:
        break;
    }
    return FALSE;
}

int dsu_win16_gui_run(const char *manifest_path,
                      const char *payload_root,
                      const char *state_path,
                      const char *log_path) {
    dsu_legacy_status_t st;
    dsu_legacy_manifest_t *manifest = NULL;
    dsu_legacy_invocation_t inv;
    int result = 1;

    if (!manifest_path || !payload_root || !state_path) {
        return 1;
    }

    if (dsu_legacy_manifest_load(manifest_path, &manifest) == DSU_LEGACY_STATUS_SUCCESS) {
        g_manifest = manifest;
    }

    g_action = 0;
    DialogBox(GetModuleHandle(NULL), MAKEINTRESOURCE(IDD_MAIN), NULL, win16_main_dlgproc);

    if (g_action == 3) {
        st = dsu_legacy_verify(state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
        goto done;
    }
    if (g_action == 4) {
        st = dsu_legacy_uninstall(state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
        goto done;
    }
    if (g_action == 0) {
        result = 1;
        goto done;
    }

    memset(&inv, 0, sizeof(inv));
    inv.operation = (g_action == 2) ? (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR
                                   : (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    inv.scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
    inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                       DSU_LEGACY_POLICY_DETERMINISTIC |
                       DSU_LEGACY_POLICY_LEGACY_MODE;
    inv.platform_triple = (char *)malloc(strlen("win16-x86") + 1u);
    inv.ui_mode = (char *)malloc(strlen("gui") + 1u);
    inv.frontend_id = (char *)malloc(strlen("win16-gui") + 1u);
    if (!inv.platform_triple || !inv.ui_mode || !inv.frontend_id) {
        result = 2;
        goto done;
    }
    strcpy(inv.platform_triple, "win16-x86");
    strcpy(inv.ui_mode, "gui");
    strcpy(inv.frontend_id, "win16-gui");

    if (g_install_root[0]) {
        inv.install_roots = (char **)malloc(sizeof(char *));
        if (!inv.install_roots) {
            result = 2;
            goto done;
        }
        inv.install_roots[0] = (char *)malloc(strlen(g_install_root) + 1u);
        if (!inv.install_roots[0]) {
            free(inv.install_roots);
            result = 2;
            goto done;
        }
        strcpy(inv.install_roots[0], g_install_root);
        inv.install_root_count = 1u;
        inv.install_root_cap = 1u;
    }

    if (g_custom && g_selected_count > 0u) {
        inv.selected_components = g_selected;
        inv.selected_component_count = g_selected_count;
        inv.selected_component_cap = g_selected_cap;
        g_selected = NULL;
        g_selected_count = 0u;
        g_selected_cap = 0u;
    }

    if (g_manifest) {
        st = dsu_legacy_apply(g_manifest, &inv, payload_root, state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
    } else {
        result = 2;
    }

    win16_free_list(inv.install_roots, inv.install_root_count);
    win16_free_list(inv.selected_components, inv.selected_component_count);
    free(inv.platform_triple);
    free(inv.ui_mode);
    free(inv.frontend_id);

done:
    win16_free_selected();
    if (manifest) dsu_legacy_manifest_free(manifest);
    g_manifest = NULL;
    return result;
}
