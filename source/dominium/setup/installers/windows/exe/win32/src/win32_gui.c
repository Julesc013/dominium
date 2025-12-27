/*
FILE: source/dominium/setup/installers/windows/exe/win32/src/win32_gui.c
MODULE: Dominium Setup EXE (Win32)
PURPOSE: Minimal native GUI flow using standard dialogs.
*/
#include "dsu_exe_win32.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shlobj.h>
#endif

#if defined(_MSC_VER)
#define dsu_exe_snprintf _snprintf
#else
#define dsu_exe_snprintf snprintf
#endif

static int gui_prompt_yesno(const char *title, const char *text, int default_yes) {
    UINT flags = MB_YESNO | MB_ICONQUESTION;
    flags |= default_yes ? MB_DEFBUTTON1 : MB_DEFBUTTON2;
    return MessageBoxA(NULL, text, title ? title : "Dominium Setup", flags) == IDYES;
}

static int gui_prompt_maintenance(void) {
    UINT flags = MB_YESNOCANCEL | MB_ICONQUESTION | MB_DEFBUTTON1;
    int res = MessageBoxA(NULL,
                          "Existing installation detected.\n\nYes = Change/Upgrade\nNo = Repair\nCancel = Remove",
                          "Dominium Setup - Maintenance",
                          flags);
    if (res == IDYES) return 1; /* upgrade/change */
    if (res == IDNO) return 2;  /* repair */
    return 3; /* uninstall */
}

static int gui_select_folder(const char *title, char *out, size_t cap) {
    BROWSEINFOA bi;
    LPITEMIDLIST pidl;
    char path[MAX_PATH];
    memset(&bi, 0, sizeof(bi));
    bi.lpszTitle = title;
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_USENEWUI;
    pidl = SHBrowseForFolderA(&bi);
    if (!pidl) return 0;
    if (!SHGetPathFromIDListA(pidl, path)) {
        CoTaskMemFree(pidl);
        return 0;
    }
    CoTaskMemFree(pidl);
    strncpy(out, path, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int gui_load_manifest(const char *path, dsu_ctx_t **out_ctx, dsu_manifest_t **out_manifest) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_status_t st;
    if (!path || !out_ctx || !out_manifest) return 0;
    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) return 0;
    st = dsu_manifest_load_file(ctx, path, &manifest);
    if (st != DSU_STATUS_SUCCESS || !manifest) {
        dsu_ctx_destroy(ctx);
        return 0;
    }
    *out_ctx = ctx;
    *out_manifest = manifest;
    return 1;
}

static int gui_select_install_root(const dsu_manifest_t *manifest,
                                   dsu_manifest_install_scope_t scope,
                                   const char *platform,
                                   char *out,
                                   size_t cap) {
    dsu_u32 i;
    dsu_u32 count;
    const char *fallback = NULL;
    if (!manifest || !out || cap == 0u) return 0;
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        if (dsu_manifest_install_root_scope(manifest, i) != scope) {
            continue;
        }
        if (!fallback) {
            fallback = dsu_manifest_install_root_path(manifest, i);
        }
        if (platform) {
            const char *p = dsu_manifest_install_root_platform(manifest, i);
            if (p && _stricmp(p, platform) == 0) {
                fallback = dsu_manifest_install_root_path(manifest, i);
                break;
            }
        }
    }
    if (!fallback || !fallback[0]) return 0;
    strncpy(out, fallback, cap - 1u);
    out[cap - 1u] = '\0';
    return 1;
}

static int gui_detect_installed(const dsu_manifest_t *manifest,
                                const char *platform,
                                dsu_ui_state_t *state) {
    dsu_u32 count;
    dsu_u32 i;
    if (!manifest || !state) return 0;
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        const char *root = dsu_manifest_install_root_path(manifest, i);
        const char *plat = dsu_manifest_install_root_platform(manifest, i);
        char state_path[1024];
        if (!root || !root[0]) continue;
        if (platform && plat && _stricmp(platform, plat) != 0) continue;
        if (dsu_exe_snprintf(state_path, sizeof(state_path), "%s\\.dsu\\installed_state.dsustate", root) <= 0) {
            continue;
        }
        if (GetFileAttributesA(state_path) != INVALID_FILE_ATTRIBUTES) {
            state->installed_detected = 1;
            state->scope = dsu_manifest_install_root_scope(manifest, i);
            strncpy(state->install_root, root, sizeof(state->install_root) - 1u);
            state->install_root[sizeof(state->install_root) - 1u] = '\0';
            return 1;
        }
    }
    return 0;
}

static int gui_build_components(const dsu_manifest_t *manifest,
                                int **out_selected,
                                char ***out_ids,
                                dsu_u32 *out_count) {
    dsu_u32 count;
    dsu_u32 i;
    int *selected;
    char **ids;
    int any_default = 0;

    if (!manifest || !out_selected || !out_ids || !out_count) return 0;
    count = dsu_manifest_component_count(manifest);
    if (count == 0u) return 0;
    selected = (int *)calloc(count, sizeof(int));
    ids = (char **)calloc(count, sizeof(char *));
    if (!selected || !ids) {
        free(selected);
        free(ids);
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        const char *id = dsu_manifest_component_id(manifest, i);
        dsu_u32 flags = dsu_manifest_component_flags(manifest, i);
        ids[i] = _strdup(id ? id : "");
        if (!ids[i]) {
            dsu_u32 j;
            for (j = 0u; j < i; ++j) free(ids[j]);
            free(ids);
            free(selected);
            return 0;
        }
        if (flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) {
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

static void gui_free_components(char **ids, int *selected, dsu_u32 count) {
    dsu_u32 i;
    if (ids) {
        for (i = 0u; i < count; ++i) {
            free(ids[i]);
        }
        free(ids);
    }
    if (selected) {
        free(selected);
    }
}

static char *gui_join_selected(char **ids, int *selected, dsu_u32 count) {
    dsu_u32 i;
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

int dsu_exe_run_gui(const dsu_exe_bridge_paths_t *paths,
                    const char *platform,
                    const char *frontend_id,
                    int quiet) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_ui_state_t state;
    int *selected = NULL;
    char **ids = NULL;
    dsu_u32 count = 0u;
    int ok = 0;
    int result = 1;

    if (!paths || !paths->manifest_path) {
        MessageBoxA(NULL, "Installer payload missing.", "Dominium Setup", MB_ICONERROR);
        return 1;
    }
    if (!gui_load_manifest(paths->manifest_path, &ctx, &manifest)) {
        MessageBoxA(NULL, "Failed to load manifest.", "Dominium Setup", MB_ICONERROR);
        return 1;
    }

    dsu_ui_state_init(&state);
    gui_detect_installed(manifest, platform, &state);

    if (state.installed_detected) {
        int op = gui_prompt_maintenance();
        state.operation = (dsu_u8)op;
    }

    if (state.operation != 3) {
        int quick = gui_prompt_yesno("Dominium Setup", "Use Quick Install?", 1);
        state.install_mode = quick ? DSU_UI_INSTALL_MODE_QUICK : DSU_UI_INSTALL_MODE_CUSTOM;
    }

    if (gui_prompt_yesno("Dominium Setup", "Install as portable?", 0)) {
        state.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    } else if (gui_prompt_yesno("Dominium Setup", "Install for all users (per-machine)?", 0)) {
        state.scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    } else {
        state.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    }

    if (!state.install_root[0]) {
        gui_select_install_root(manifest, state.scope, platform, state.install_root, sizeof(state.install_root));
    }

    if (state.install_mode == DSU_UI_INSTALL_MODE_CUSTOM) {
        char chosen[MAX_PATH];
        if (gui_select_folder("Choose install folder", chosen, sizeof(chosen))) {
            strncpy(state.install_root, chosen, sizeof(state.install_root) - 1u);
            state.install_root[sizeof(state.install_root) - 1u] = '\0';
        }
    }

    ok = gui_build_components(manifest, &selected, &ids, &count);
    if (!ok) {
        MessageBoxA(NULL, "Failed to enumerate components.", "Dominium Setup", MB_ICONERROR);
        goto done;
    }

    if (state.install_mode == DSU_UI_INSTALL_MODE_CUSTOM) {
        dsu_u32 i;
        for (i = 0u; i < count; ++i) {
            char msg[256];
            dsu_exe_snprintf(msg, sizeof(msg), "Install component '%s'?", ids[i]);
            selected[i] = gui_prompt_yesno("Dominium Setup", msg, selected[i]);
        }
    }

    state.enable_shortcuts = gui_prompt_yesno("Dominium Setup", "Create shortcuts?", 1);
    state.enable_file_assoc = gui_prompt_yesno("Dominium Setup", "Enable file associations?", 1);
    state.enable_url_handlers = gui_prompt_yesno("Dominium Setup", "Enable URL handlers?", 1);

    if (!gui_prompt_yesno("Dominium Setup", "Ready to install. Continue?", 1)) {
        result = 1;
        goto done;
    }

    {
        char *components_csv = gui_join_selected(ids, selected, count);
        result = dsu_exe_apply_from_state(paths, platform, frontend_id, &state, components_csv, NULL, "gui", quiet);
        if (components_csv) free(components_csv);
    }
    if (result == 0) {
        MessageBoxA(NULL, "Setup completed successfully.", "Dominium Setup", MB_ICONINFORMATION);
    } else {
        MessageBoxA(NULL, "Setup failed. Check logs for details.", "Dominium Setup", MB_ICONERROR);
    }

done:
    gui_free_components(ids, selected, count);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return result;
}
