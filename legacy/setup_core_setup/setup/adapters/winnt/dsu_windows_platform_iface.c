/*
FILE: source/dominium/setup/adapters/windows/dsu_windows_platform_iface.c
MODULE: Dominium Setup
PURPOSE: Windows platform adapter implementation for declarative registrations (Plan S-6).
*/
#if !defined(_WIN32)
#error "dsu_windows_platform_iface.c is Windows-only"
#endif

#include "dsu_windows_platform_iface.h"

#include "dsu/dsu_fs.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include <stdio.h>
#include <string.h>

static void dsu__win_slashes_to_backslashes(char *s) {
    dsu_u32 i;
    if (!s) return;
    for (i = 0u; s[i] != '\0'; ++i) {
        if (s[i] == '/') s[i] = '\\';
    }
}

static HKEY dsu__win_root_for_scope(dsu_u8 scope) {
    if (scope == (dsu_u8)DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        return HKEY_LOCAL_MACHINE;
    }
    return HKEY_CURRENT_USER;
}

static dsu_status_t dsu__win_reg_set_sz(HKEY root, const char *subkey, const char *name, const char *value) {
    HKEY h = NULL;
    DWORD disp = 0;
    LONG rc;
    const char *v = value ? value : "";

    if (!subkey || subkey[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    rc = RegCreateKeyExA(root, subkey, 0, NULL, 0, KEY_SET_VALUE, NULL, &h, &disp);
    if (rc != ERROR_SUCCESS) {
        return DSU_STATUS_IO_ERROR;
    }
    rc = RegSetValueExA(h,
                        (name && name[0] != '\0') ? name : NULL,
                        0,
                        REG_SZ,
                        (const BYTE *)v,
                        (DWORD)(strlen(v) + 1u));
    RegCloseKey(h);
    return (rc == ERROR_SUCCESS) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
}

static dsu_status_t dsu__win_reg_set_dword(HKEY root, const char *subkey, const char *name, DWORD value) {
    HKEY h = NULL;
    DWORD disp = 0;
    LONG rc;

    if (!subkey || subkey[0] == '\0' || !name || name[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }

    rc = RegCreateKeyExA(root, subkey, 0, NULL, 0, KEY_SET_VALUE, NULL, &h, &disp);
    if (rc != ERROR_SUCCESS) {
        return DSU_STATUS_IO_ERROR;
    }
    rc = RegSetValueExA(h, name, 0, REG_DWORD, (const BYTE *)&value, (DWORD)sizeof(DWORD));
    RegCloseKey(h);
    return (rc == ERROR_SUCCESS) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
}

static dsu_status_t dsu__win_reg_delete_tree(HKEY root, const char *subkey) {
    LONG rc;
    if (!subkey || subkey[0] == '\0') {
        return DSU_STATUS_INVALID_ARGS;
    }
    rc = RegDeleteTreeA(root, subkey);
    if (rc == ERROR_FILE_NOT_FOUND) {
        return DSU_STATUS_SUCCESS;
    }
    return (rc == ERROR_SUCCESS) ? DSU_STATUS_SUCCESS : DSU_STATUS_IO_ERROR;
}

static dsu_status_t dsu__win_build_abs_native(char *out_native, dsu_u32 out_cap, const char *install_root, const char *relpath) {
    dsu_status_t st;
    char tmp[1024];

    if (!out_native || out_cap == 0u || !install_root || !relpath) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_native[0] = '\0';
    tmp[0] = '\0';

    st = dsu_fs_path_join(install_root, relpath, tmp, (dsu_u32)sizeof(tmp));
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    st = dsu_fs_path_canonicalize(tmp, out_native, out_cap);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    dsu__win_slashes_to_backslashes(out_native);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_build_command(char *out_cmd, dsu_u32 out_cap, const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    dsu_status_t st;
    char exe_native[1024];
    const char *args;

    if (!out_cmd || out_cap == 0u || !state || !intent) {
        return DSU_STATUS_INVALID_ARGS;
    }
    out_cmd[0] = '\0';
    exe_native[0] = '\0';

    st = dsu__win_build_abs_native(exe_native, (dsu_u32)sizeof(exe_native), state->install_root, intent->exec_relpath ? intent->exec_relpath : "");
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    args = (intent->arguments && intent->arguments[0] != '\0') ? intent->arguments : NULL;

    if (args) {
        if ((dsu_u32)(strlen(exe_native) + strlen(args) + 4u) >= out_cap) {
            return DSU_STATUS_IO_ERROR;
        }
        sprintf(out_cmd, "\"%s\" %s", exe_native, args);
    } else {
        if ((dsu_u32)(strlen(exe_native) + 3u) >= out_cap) {
            return DSU_STATUS_IO_ERROR;
        }
        sprintf(out_cmd, "\"%s\"", exe_native);
    }
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_register_uninstall_entry(const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    HKEY root;
    char key[512];
    char cmd[2048];
    const char *app_id;
    dsu_status_t st;

    if (!state || !intent || !intent->display_name) {
        return DSU_STATUS_INVALID_ARGS;
    }

    app_id = (intent->app_id && intent->app_id[0] != '\0') ? intent->app_id : "dominium";
    root = dsu__win_root_for_scope(state->scope);
    sprintf(key, "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s", app_id);

    st = dsu__win_reg_set_sz(root, key, "DisplayName", intent->display_name);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__win_reg_set_sz(root, key, "DisplayVersion", state->product_version ? state->product_version : "");
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__win_reg_set_sz(root, key, "InstallLocation", state->install_root ? state->install_root : "");
    if (st != DSU_STATUS_SUCCESS) return st;
    if (intent->publisher && intent->publisher[0] != '\0') {
        st = dsu__win_reg_set_sz(root, key, "Publisher", intent->publisher);
        if (st != DSU_STATUS_SUCCESS) return st;
    }

    st = dsu__win_build_command(cmd, (dsu_u32)sizeof(cmd), state, intent);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__win_reg_set_sz(root, key, "UninstallString", cmd);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__win_reg_set_sz(root, key, "QuietUninstallString", cmd);
    if (st != DSU_STATUS_SUCCESS) return st;

    (void)dsu__win_reg_set_dword(root, key, "NoModify", 1u);
    (void)dsu__win_reg_set_dword(root, key, "NoRepair", 1u);
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_register_url_handler(const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    HKEY root;
    char key[512];
    char cmd[2048];
    const char *proto;
    dsu_status_t st;

    if (!state || !intent) {
        return DSU_STATUS_INVALID_ARGS;
    }
    proto = (intent->protocol && intent->protocol[0] != '\0') ? intent->protocol : NULL;
    if (!proto) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    root = dsu__win_root_for_scope(state->scope);
    sprintf(key, "Software\\Classes\\%s", proto);
    st = dsu__win_reg_set_sz(root, key, NULL, intent->display_name ? intent->display_name : proto);
    if (st != DSU_STATUS_SUCCESS) return st;
    st = dsu__win_reg_set_sz(root, key, "URL Protocol", "");
    if (st != DSU_STATUS_SUCCESS) return st;

    st = dsu__win_build_command(cmd, (dsu_u32)sizeof(cmd), state, intent);
    if (st != DSU_STATUS_SUCCESS) return st;
    sprintf(key, "Software\\Classes\\%s\\shell\\open\\command", proto);
    st = dsu__win_reg_set_sz(root, key, NULL, cmd);
    if (st != DSU_STATUS_SUCCESS) return st;

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_register_file_assoc(const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    HKEY root;
    char key[512];
    char prog_id[256];
    char cmd[2048];
    const char *ext;
    const char *app_id;
    dsu_status_t st;

    if (!state || !intent) {
        return DSU_STATUS_INVALID_ARGS;
    }
    ext = (intent->extension && intent->extension[0] != '\0') ? intent->extension : NULL;
    app_id = (intent->app_id && intent->app_id[0] != '\0') ? intent->app_id : NULL;
    if (!ext || !app_id) {
        return DSU_STATUS_INVALID_REQUEST;
    }

    root = dsu__win_root_for_scope(state->scope);
    sprintf(prog_id, "%s%s", app_id, ext);

    sprintf(key, "Software\\Classes\\%s", ext);
    st = dsu__win_reg_set_sz(root, key, NULL, prog_id);
    if (st != DSU_STATUS_SUCCESS) return st;

    sprintf(key, "Software\\Classes\\%s", prog_id);
    st = dsu__win_reg_set_sz(root, key, NULL, intent->display_name ? intent->display_name : prog_id);
    if (st != DSU_STATUS_SUCCESS) return st;

    st = dsu__win_build_command(cmd, (dsu_u32)sizeof(cmd), state, intent);
    if (st != DSU_STATUS_SUCCESS) return st;
    sprintf(key, "Software\\Classes\\%s\\shell\\open\\command", prog_id);
    st = dsu__win_reg_set_sz(root, key, NULL, cmd);
    if (st != DSU_STATUS_SUCCESS) return st;

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_register_app_entry(const dsu_platform_registrations_state_t *state, const dsu_platform_intent_t *intent) {
    HKEY root;
    char key[512];
    char exe_native[1024];
    char dir[512];
    char base[256];
    dsu_status_t st;

    if (!state || !intent || !intent->exec_relpath) {
        return DSU_STATUS_INVALID_ARGS;
    }

    dir[0] = '\0';
    base[0] = '\0';
    st = dsu_fs_path_split(intent->exec_relpath, dir, (dsu_u32)sizeof(dir), base, (dsu_u32)sizeof(base));
    if (st != DSU_STATUS_SUCCESS || base[0] == '\0') {
        return DSU_STATUS_INVALID_REQUEST;
    }

    exe_native[0] = '\0';
    st = dsu__win_build_abs_native(exe_native, (dsu_u32)sizeof(exe_native), state->install_root, intent->exec_relpath);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }

    root = dsu__win_root_for_scope(state->scope);
    sprintf(key, "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\%s", base);
    st = dsu__win_reg_set_sz(root, key, NULL, exe_native);
    if (st != DSU_STATUS_SUCCESS) return st;

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_plat_request_elevation(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__win_plat_register_app_entry(void *user,
                                                    dsu_ctx_t *ctx,
                                                    const dsu_platform_registrations_state_t *state,
                                                    const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    return dsu__win_register_app_entry(state, intent);
}

static dsu_status_t dsu__win_plat_register_file_assoc(void *user,
                                                     dsu_ctx_t *ctx,
                                                     const dsu_platform_registrations_state_t *state,
                                                     const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    return dsu__win_register_file_assoc(state, intent);
}

static dsu_status_t dsu__win_plat_register_url_handler(void *user,
                                                      dsu_ctx_t *ctx,
                                                      const dsu_platform_registrations_state_t *state,
                                                      const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    return dsu__win_register_url_handler(state, intent);
}

static dsu_status_t dsu__win_plat_register_uninstall_entry(void *user,
                                                          dsu_ctx_t *ctx,
                                                          const dsu_platform_registrations_state_t *state,
                                                          const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    return dsu__win_register_uninstall_entry(state, intent);
}

static dsu_status_t dsu__win_plat_declare_capability(void *user,
                                                    dsu_ctx_t *ctx,
                                                    const dsu_platform_registrations_state_t *state,
                                                    const dsu_platform_intent_t *intent) {
    (void)user;
    (void)ctx;
    (void)state;
    (void)intent;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_plat_remove_registrations(void *user, dsu_ctx_t *ctx, const dsu_platform_registrations_state_t *state) {
    dsu_u32 i;
    HKEY root;

    (void)user;
    (void)ctx;

    if (!state) {
        return DSU_STATUS_INVALID_ARGS;
    }

    root = dsu__win_root_for_scope(state->scope);

    for (i = 0u; i < state->intent_count; ++i) {
        const dsu_platform_intent_t *it = &state->intents[i];
        char key[512];
        const char *app_id = (it->app_id && it->app_id[0] != '\0') ? it->app_id : "dominium";

        if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_UNINSTALL_ENTRY) {
            sprintf(key, "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s", app_id);
            if (dsu__win_reg_delete_tree(root, key) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_URL_HANDLER) {
            if (it->protocol && it->protocol[0] != '\0') {
                sprintf(key, "Software\\Classes\\%s", it->protocol);
                if (dsu__win_reg_delete_tree(root, key) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
            }
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_FILE_ASSOC) {
            if (it->extension && it->extension[0] != '\0') {
                sprintf(key, "Software\\Classes\\%s%s", app_id, it->extension);
                if (dsu__win_reg_delete_tree(root, key) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
            }
        } else if (it->kind == (dsu_u8)DSU_PLATFORM_INTENT_REGISTER_APP_ENTRY) {
            char dir[512];
            char base[256];
            dir[0] = '\0';
            base[0] = '\0';
            if (it->exec_relpath &&
                dsu_fs_path_split(it->exec_relpath, dir, (dsu_u32)sizeof(dir), base, (dsu_u32)sizeof(base)) == DSU_STATUS_SUCCESS &&
                base[0] != '\0') {
                sprintf(key, "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\%s", base);
                if (dsu__win_reg_delete_tree(root, key) != DSU_STATUS_SUCCESS) return DSU_STATUS_IO_ERROR;
            }
        } else {
            /* ignore */
        }
    }

    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu__win_plat_atomic_dir_swap(void *user, dsu_ctx_t *ctx, const char *src_abs, const char *dst_abs) {
    (void)user;
    (void)ctx;
    (void)src_abs;
    (void)dst_abs;
    return DSU_STATUS_INVALID_REQUEST;
}

static dsu_status_t dsu__win_plat_flush_fs(void *user, dsu_ctx_t *ctx) {
    (void)user;
    (void)ctx;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu_windows_platform_iface_init(dsu_platform_iface_t *out_iface) {
    if (!out_iface) {
        return DSU_STATUS_INVALID_ARGS;
    }
    dsu_platform_iface_init(out_iface);
    out_iface->plat_request_elevation = dsu__win_plat_request_elevation;
    out_iface->plat_register_app_entry = dsu__win_plat_register_app_entry;
    out_iface->plat_register_file_assoc = dsu__win_plat_register_file_assoc;
    out_iface->plat_register_url_handler = dsu__win_plat_register_url_handler;
    out_iface->plat_register_uninstall_entry = dsu__win_plat_register_uninstall_entry;
    out_iface->plat_declare_capability = dsu__win_plat_declare_capability;
    out_iface->plat_remove_registrations = dsu__win_plat_remove_registrations;
    out_iface->plat_atomic_dir_swap = dsu__win_plat_atomic_dir_swap;
    out_iface->plat_flush_fs = dsu__win_plat_flush_fs;
    return DSU_STATUS_SUCCESS;
}

