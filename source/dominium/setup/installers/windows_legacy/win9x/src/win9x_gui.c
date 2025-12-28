/*
FILE: source/dominium/setup/installers/windows_legacy/win9x/src/win9x_gui.c
MODULE: Dominium Setup (Win9x)
PURPOSE: Win9x GUI flow using standard dialogs and message boxes.
*/
#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <shlobj.h>

#include "../../legacy_core/include/dsu_legacy_core.h"

#include <stdlib.h>
#include <string.h>

#define DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED 0x00000002u

static int win9x_prompt_yesno(const char *title, const char *text, int default_yes) {
    UINT flags = MB_YESNO | MB_ICONQUESTION;
    flags |= default_yes ? MB_DEFBUTTON1 : MB_DEFBUTTON2;
    return MessageBoxA(NULL, text, title ? title : "Dominium Setup", flags) == IDYES;
}

static int win9x_prompt_maintenance(void) {
    UINT flags = MB_YESNOCANCEL | MB_ICONQUESTION | MB_DEFBUTTON1;
    int res = MessageBoxA(NULL,
                          "Existing installation detected.\n\nYes = Change/Upgrade\nNo = Repair\nCancel = Remove",
                          "Dominium Setup - Maintenance",
                          flags);
    if (res == IDYES) return 1;
    if (res == IDNO) return 2;
    return 3;
}

static int win9x_select_folder(const char *title, char *out, size_t cap) {
    BROWSEINFOA bi;
    LPITEMIDLIST pidl;
    char path[MAX_PATH];
    IMalloc *imalloc = NULL;
    memset(&bi, 0, sizeof(bi));
    bi.lpszTitle = title;
    bi.ulFlags = BIF_RETURNONLYFSDIRS;
    pidl = SHBrowseForFolderA(&bi);
    if (!pidl) return 0;
    if (!SHGetPathFromIDListA(pidl, path)) {
        if (SHGetMalloc(&imalloc) == S_OK && imalloc) {
            imalloc->lpVtbl->Free(imalloc, pidl);
            imalloc->lpVtbl->Release(imalloc);
        }
        return 0;
    }
    if (SHGetMalloc(&imalloc) == S_OK && imalloc) {
        imalloc->lpVtbl->Free(imalloc, pidl);
        imalloc->lpVtbl->Release(imalloc);
    }
    strncpy(out, path, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static const char *win9x_select_install_root(const dsu_legacy_manifest_t *m,
                                             dsu_legacy_u8 scope,
                                             const char *platform) {
    dsu_legacy_u32 i;
    if (!m) return NULL;
    for (i = 0u; i < m->install_root_count; ++i) {
        const dsu_legacy_manifest_install_root_t *r = &m->install_roots[i];
        if (r->scope != scope) continue;
        if (platform && r->platform && lstrcmpiA(platform, r->platform) != 0) {
            continue;
        }
        return r->path;
    }
    if (m->install_root_count > 0u) {
        return m->install_roots[0].path;
    }
    return NULL;
}

static int win9x_build_components(const dsu_legacy_manifest_t *m,
                                  int **out_selected,
                                  char ***out_ids,
                                  dsu_legacy_u32 *out_count) {
    dsu_legacy_u32 count;
    dsu_legacy_u32 i;
    int *selected;
    char **ids;
    int any_default = 0;
    if (!m || !out_selected || !out_ids || !out_count) return 0;
    count = m->component_count;
    if (count == 0u) return 0;
    selected = (int *)calloc(count, sizeof(int));
    ids = (char **)calloc(count, sizeof(char *));
    if (!selected || !ids) {
        free(selected);
        free(ids);
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        const char *id = m->components[i].id ? m->components[i].id : "";
        ids[i] = _strdup(id);
        if (!ids[i]) {
            dsu_legacy_u32 j;
            for (j = 0u; j < i; ++j) free(ids[j]);
            free(ids);
            free(selected);
            return 0;
        }
        if ((m->components[i].flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) != 0u) {
            selected[i] = 1;
            any_default = 1;
        }
    }
    if (!any_default) {
        for (i = 0u; i < count; ++i) {
            selected[i] = 1;
        }
    }
    *out_selected = selected;
    *out_ids = ids;
    *out_count = count;
    return 1;
}

static void win9x_free_components(char **ids, int *selected, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    if (ids) {
        for (i = 0u; i < count; ++i) {
            free(ids[i]);
        }
        free(ids);
    }
    free(selected);
}

static char *win9x_join_selected(char **ids, int *selected, dsu_legacy_u32 count) {
    dsu_legacy_u32 i;
    size_t total = 0u;
    char *buf;
    size_t pos = 0u;
    if (!ids || !selected || count == 0u) return NULL;
    for (i = 0u; i < count; ++i) {
        if (!selected[i]) continue;
        total += strlen(ids[i]) + 1u;
    }
    if (total == 0u) return NULL;
    buf = (char *)malloc(total + 1u);
    if (!buf) return NULL;
    for (i = 0u; i < count; ++i) {
        if (!selected[i]) continue;
        if (pos != 0u) buf[pos++] = ',';
        memcpy(buf + pos, ids[i], strlen(ids[i]));
        pos += strlen(ids[i]);
    }
    buf[pos] = '\0';
    return buf;
}

int dsu_win9x_run_gui(const char *manifest_path,
                      const char *payload_root,
                      const char *platform,
                      const char *frontend_id) {
    dsu_legacy_manifest_t *manifest = NULL;
    dsu_legacy_invocation_t inv;
    dsu_legacy_status_t st;
    int *selected = NULL;
    char **ids = NULL;
    dsu_legacy_u32 count = 0u;
    char install_root[MAX_PATH];
    char state_path[MAX_PATH];
    char log_path[MAX_PATH];
    int installed = 0;
    int op = 0; /* 0 install, 1 repair, 2 uninstall, 3 verify */
    int quick = 1;
    dsu_legacy_u8 scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
    int result = 1;

    if (!manifest_path || !payload_root) {
        MessageBoxA(NULL, "Installer payload missing.", "Dominium Setup", MB_ICONERROR);
        return 1;
    }
    if (dsu_legacy_manifest_load(manifest_path, &manifest) != DSU_LEGACY_STATUS_SUCCESS) {
        MessageBoxA(NULL, "Failed to load manifest.", "Dominium Setup", MB_ICONERROR);
        return 1;
    }

    {
        const char *root = win9x_select_install_root(manifest, scope, platform);
        if (!root || !root[0]) root = "C:\\Program Files\\Dominium";
        strncpy(install_root, root, sizeof(install_root) - 1u);
        install_root[sizeof(install_root) - 1u] = '\0';
        wsprintfA(state_path, "%s\\dominium_state.dsus", install_root);
        wsprintfA(log_path, "%s\\dominium_install.log", install_root);
        if (GetFileAttributesA(state_path) != INVALID_FILE_ATTRIBUTES) {
            installed = 1;
        }
    }

    if (installed) {
        int m = win9x_prompt_maintenance();
        if (m == 2) op = 1;
        else if (m == 3) op = 2;
        else op = 0;
        if (win9x_prompt_yesno("Dominium Setup", "Run verify only?", 0)) {
            op = 3;
        }
    }
    if (!installed || op == 0 || op == 1) {
        quick = win9x_prompt_yesno("Dominium Setup", "Use Quick Install?", 1);
    }

    if (win9x_prompt_yesno("Dominium Setup", "Install as portable?", 0)) {
        scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_PORTABLE;
    } else if (win9x_prompt_yesno("Dominium Setup", "Install for all users?", 0)) {
        scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_SYSTEM;
    } else {
        scope = (dsu_legacy_u8)DSU_LEGACY_SCOPE_USER;
    }

    {
        const char *root = win9x_select_install_root(manifest, scope, platform);
        if (root && root[0]) {
            strncpy(install_root, root, sizeof(install_root) - 1u);
            install_root[sizeof(install_root) - 1u] = '\0';
        }
        if (!quick && win9x_select_folder("Choose install folder", install_root, sizeof(install_root))) {
            wsprintfA(state_path, "%s\\dominium_state.dsus", install_root);
            wsprintfA(log_path, "%s\\dominium_install.log", install_root);
        }
    }

    if (!win9x_build_components(manifest, &selected, &ids, &count)) {
        MessageBoxA(NULL, "Failed to enumerate components.", "Dominium Setup", MB_ICONERROR);
        goto done;
    }

    if (!quick) {
        dsu_legacy_u32 i;
        for (i = 0u; i < count; ++i) {
            char msg[256];
            wsprintfA(msg, "Install component '%s'?", ids[i]);
            selected[i] = win9x_prompt_yesno("Dominium Setup", msg, selected[i]);
        }
    }

    if (!win9x_prompt_yesno("Dominium Setup", "Ready to continue?", 1)) {
        result = 1;
        goto done;
    }

    if (op == 3) {
        st = dsu_legacy_verify(state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
        goto done;
    }
    if (op == 2) {
        st = dsu_legacy_uninstall(state_path, log_path);
        result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;
        goto done;
    }

    memset(&inv, 0, sizeof(inv));
    inv.operation = (op == 1) ? (dsu_legacy_u8)DSU_LEGACY_OPERATION_REPAIR
                              : (dsu_legacy_u8)DSU_LEGACY_OPERATION_INSTALL;
    inv.scope = scope;
    inv.policy_flags = DSU_LEGACY_POLICY_OFFLINE |
                       DSU_LEGACY_POLICY_DETERMINISTIC |
                       DSU_LEGACY_POLICY_LEGACY_MODE;
    inv.platform_triple = _strdup(platform ? platform : "win32-9x-x86");
    inv.ui_mode = _strdup("gui");
    inv.frontend_id = _strdup(frontend_id ? frontend_id : "win9x-gui");
    if (!inv.platform_triple || !inv.ui_mode || !inv.frontend_id) {
        result = 2;
        goto done;
    }
    inv.install_roots = (char **)malloc(sizeof(char *));
    if (inv.install_roots) {
        inv.install_roots[0] = _strdup(install_root);
        if (inv.install_roots[0]) {
            inv.install_root_count = 1u;
            inv.install_root_cap = 1u;
        }
    }
    if (!quick) {
        char *csv = win9x_join_selected(ids, selected, count);
        if (csv) {
            char *p = csv;
            char *token = csv;
            while (token) {
                char *comma = strchr(token, ',');
                if (comma) *comma = '\0';
                if (token[0]) {
                    dsu_legacy_u32 cap = inv.selected_component_cap;
                    dsu_legacy_u32 cnt = inv.selected_component_count;
                    char **next = (char **)realloc(inv.selected_components,
                                                   (size_t)(cnt + 1u) * sizeof(char *));
                    if (next) {
                        inv.selected_components = next;
                        inv.selected_components[cnt] = _strdup(token);
                        if (inv.selected_components[cnt]) {
                            inv.selected_component_count = cnt + 1u;
                            inv.selected_component_cap = cap + 1u;
                        }
                    }
                }
                if (!comma) break;
                token = comma + 1;
            }
            free(p);
        }
    }

    st = dsu_legacy_apply(manifest, &inv, payload_root, state_path, log_path);
    result = (st == DSU_LEGACY_STATUS_SUCCESS) ? 0 : 2;

done:
    if (result == 0) {
        MessageBoxA(NULL, "Setup completed successfully.", "Dominium Setup", MB_ICONINFORMATION);
    } else if (result != 1) {
        MessageBoxA(NULL, "Setup failed. Check logs for details.", "Dominium Setup", MB_ICONERROR);
    }
    win9x_free_components(ids, selected, count);
    if (manifest) dsu_legacy_manifest_free(manifest);
    if (inv.install_roots) {
        free(inv.install_roots[0]);
        free(inv.install_roots);
    }
    if (inv.selected_components) {
        dsu_legacy_u32 i;
        for (i = 0u; i < inv.selected_component_count; ++i) {
            free(inv.selected_components[i]);
        }
        free(inv.selected_components);
    }
    free(inv.platform_triple);
    free(inv.ui_mode);
    free(inv.frontend_id);
    return result;
}
