/*
FILE: source/dominium/setup/installers/windows/msi/InvokeSetupCore.c
MODULE: Dominium Setup (MSI)
PURPOSE: MSI custom action bridge that writes a DSU invocation payload and runs Setup Core.
*/
#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <msi.h>
#include <msiquery.h>
#endif

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_invocation.h"

typedef struct dsu_msi_data_t {
    const char *install_dir;
    const char *operation;
    const char *scope;
    const char *platform;
    const char *deterministic;
    const char *offline;
    const char *allow_prerelease;
    const char *legacy_mode;
    const char *ui_mode;
    const char *frontend_id;
    const char *invocation_path;
    const char *addlocal;
    const char *remove;
    const char *uilevel;
    const char *reinstall;
    const char *upgrade_code;
    const char *allusers;
    const char *peruser;
} dsu_msi_data_t;

static void dsu_msi_log(MSIHANDLE hInstall, const char *fmt, ...) {
    char buf[1024];
    va_list args;
    PMSIHANDLE rec;
    if (!fmt) {
        return;
    }
    va_start(args, fmt);
    vsnprintf(buf, sizeof(buf), fmt, args);
    buf[sizeof(buf) - 1] = '\0';
    va_end(args);
    rec = MsiCreateRecord(1);
    if (rec) {
        MsiRecordSetStringA(rec, 0, buf);
        MsiProcessMessage(hInstall, INSTALLMESSAGE_INFO, rec);
    }
}

static char *dsu_msi_strdup(const char *s) {
    size_t n;
    char *p;
    if (!s) s = "";
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) return NULL;
    if (n) memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

static int dsu_msi_parse_bool(const char *s) {
    if (!s || !s[0]) return 0;
    if (strcmp(s, "1") == 0) return 1;
    if (_stricmp(s, "true") == 0) return 1;
    if (_stricmp(s, "yes") == 0) return 1;
    return 0;
}

static int dsu_msi_parse_uilevel(const char *s) {
    if (!s || !s[0]) return 5;
    return atoi(s);
}

static dsu_u8 dsu_msi_parse_operation(const char *s, const dsu_msi_data_t *data) {
    if (s && s[0]) {
        if (_stricmp(s, "install") == 0) return (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
        if (_stricmp(s, "upgrade") == 0) return (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE;
        if (_stricmp(s, "repair") == 0) return (dsu_u8)DSU_INVOCATION_OPERATION_REPAIR;
        if (_stricmp(s, "uninstall") == 0) return (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL;
    }
    if (data && data->remove && _stricmp(data->remove, "ALL") == 0) {
        return (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL;
    }
    if (data && data->reinstall && data->reinstall[0]) {
        return (dsu_u8)DSU_INVOCATION_OPERATION_REPAIR;
    }
    if (data && data->upgrade_code && data->upgrade_code[0]) {
        return (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE;
    }
    return (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
}

static dsu_u8 dsu_msi_parse_scope(const char *s, const dsu_msi_data_t *data) {
    if (s && s[0]) {
        if (_stricmp(s, "portable") == 0) return (dsu_u8)DSU_INVOCATION_SCOPE_PORTABLE;
        if (_stricmp(s, "user") == 0) return (dsu_u8)DSU_INVOCATION_SCOPE_USER;
        if (_stricmp(s, "system") == 0) return (dsu_u8)DSU_INVOCATION_SCOPE_SYSTEM;
    }
    if (data && data->allusers && strcmp(data->allusers, "1") == 0) {
        return (dsu_u8)DSU_INVOCATION_SCOPE_SYSTEM;
    }
    if (data && data->peruser && strcmp(data->peruser, "1") == 0) {
        return (dsu_u8)DSU_INVOCATION_SCOPE_USER;
    }
    return (dsu_u8)DSU_INVOCATION_SCOPE_USER;
}

static int dsu_msi_csv_split(const char *csv, char ***out_items, dsu_u32 *out_count) {
    char *tmp;
    char *p;
    dsu_u32 cap = 0u;
    dsu_u32 count = 0u;
    char **items = NULL;
    if (!out_items || !out_count) return 0;
    *out_items = NULL;
    *out_count = 0u;
    if (!csv || !csv[0]) return 1;
    if (_stricmp(csv, "ALL") == 0) return 1;
    tmp = dsu_msi_strdup(csv);
    if (!tmp) return 0;
    p = tmp;
    while (p && *p) {
        char *end;
        char *token = p;
        while (*token == ' ' || *token == '\t') token++;
        end = token;
        while (*end && *end != ',') end++;
        if (*end == ',') {
            *end = '\0';
            p = end + 1;
        } else {
            p = NULL;
        }
        while (end > token && (end[-1] == ' ' || end[-1] == '\t')) {
            end[-1] = '\0';
            --end;
        }
        if (token[0]) {
            char *dup = dsu_msi_strdup(token);
            char **new_items;
            if (!dup) {
                free(tmp);
                return 0;
            }
            if (count == cap) {
                dsu_u32 new_cap = (cap == 0u) ? 8u : (cap * 2u);
                new_items = (char **)realloc(items, new_cap * sizeof(*items));
                if (!new_items) {
                    free(dup);
                    free(tmp);
                    return 0;
                }
                items = new_items;
                cap = new_cap;
            }
            items[count++] = dup;
        }
    }
    free(tmp);
    *out_items = items;
    *out_count = count;
    return 1;
}

static int dsu_msi_path_join(char *out, size_t cap, const char *a, const char *b) {
    size_t na;
    size_t nb;
    if (!out || cap == 0) return 0;
    if (!a) a = "";
    if (!b) b = "";
    na = strlen(a);
    nb = strlen(b);
    if (na + nb + 2u > cap) return 0;
    if (na) memcpy(out, a, na);
    if (na && a[na - 1u] != '\\' && a[na - 1u] != '/') {
        out[na++] = '\\';
    }
    if (nb) memcpy(out + na, b, nb);
    out[na + nb] = '\0';
    return 1;
}

static int dsu_msi_get_temp_path(char *out, size_t cap) {
    DWORD len;
    if (!out || cap == 0) return 0;
    len = GetTempPathA((DWORD)cap, out);
    if (len == 0 || len >= cap) return 0;
    return 1;
}

static char *dsu_msi_get_custom_action_data(MSIHANDLE hInstall) {
    DWORD len = 0;
    UINT rc;
    char *buf;
    rc = MsiGetPropertyA(hInstall, "CustomActionData", "", &len);
    if (rc != ERROR_MORE_DATA && rc != ERROR_SUCCESS) {
        return NULL;
    }
    len += 1;
    buf = (char *)malloc(len + 1u);
    if (!buf) return NULL;
    rc = MsiGetPropertyA(hInstall, "CustomActionData", buf, &len);
    if (rc != ERROR_SUCCESS) {
        free(buf);
        return NULL;
    }
    buf[len] = '\0';
    return buf;
}

static void dsu_msi_parse_kv(char *data, dsu_msi_data_t *out) {
    char *p;
    if (!data || !out) return;
    memset(out, 0, sizeof(*out));
    p = data;
    while (*p) {
        char *key = p;
        char *eq = strchr(p, '=');
        char *val;
        char *sep;
        if (!eq) break;
        *eq = '\0';
        val = eq + 1;
        sep = strchr(val, ';');
        if (sep) {
            *sep = '\0';
            p = sep + 1;
        } else {
            p = val + strlen(val);
        }
        if (_stricmp(key, "INSTALLDIR") == 0) out->install_dir = val;
        else if (_stricmp(key, "DSU_OPERATION") == 0) out->operation = val;
        else if (_stricmp(key, "DSU_SCOPE") == 0) out->scope = val;
        else if (_stricmp(key, "DSU_PLATFORM") == 0) out->platform = val;
        else if (_stricmp(key, "DSU_DETERMINISTIC") == 0) out->deterministic = val;
        else if (_stricmp(key, "DSU_OFFLINE") == 0) out->offline = val;
        else if (_stricmp(key, "DSU_ALLOW_PRERELEASE") == 0) out->allow_prerelease = val;
        else if (_stricmp(key, "DSU_LEGACY_MODE") == 0) out->legacy_mode = val;
        else if (_stricmp(key, "DSU_UI_MODE") == 0) out->ui_mode = val;
        else if (_stricmp(key, "DSU_FRONTEND_ID") == 0) out->frontend_id = val;
        else if (_stricmp(key, "DSU_INVOCATION_PATH") == 0) out->invocation_path = val;
        else if (_stricmp(key, "ADDLOCAL") == 0) out->addlocal = val;
        else if (_stricmp(key, "REMOVE") == 0) out->remove = val;
        else if (_stricmp(key, "UILEVEL") == 0) out->uilevel = val;
        else if (_stricmp(key, "REINSTALL") == 0) out->reinstall = val;
        else if (_stricmp(key, "UPGRADINGPRODUCTCODE") == 0) out->upgrade_code = val;
        else if (_stricmp(key, "ALLUSERS") == 0) out->allusers = val;
        else if (_stricmp(key, "MSIINSTALLPERUSER") == 0) out->peruser = val;
    }
}

static int dsu_msi_run_setup_core(const char *exe_path,
                                  const char *invocation_path,
                                  int deterministic,
                                  int quiet) {
    char cmd[2048];
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    DWORD exit_code = 1;
    const char *quiet_flag = quiet ? " --quiet" : "";
    if (!exe_path || !invocation_path) return 0;
    snprintf(cmd,
             sizeof(cmd),
             "\"%s\" --deterministic %d%s apply --invocation \"%s\"",
             exe_path,
             deterministic ? 1 : 0,
             quiet_flag,
             invocation_path);

    memset(&si, 0, sizeof(si));
    memset(&pi, 0, sizeof(pi));
    si.cb = sizeof(si);
    if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        return 0;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    GetExitCodeProcess(pi.hProcess, &exit_code);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return (exit_code == 0);
}

UINT __stdcall InvokeSetupCore(MSIHANDLE hInstall) {
    char *data_raw = NULL;
    dsu_msi_data_t data;
    dsu_ctx_t *ctx = NULL;
    dsu_invocation_t inv;
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_u32 flags = 0u;
    dsu_u64 digest = 0u;
    char invocation_path[1024];
    char setup_exe[1024];
    int ok = 0;
    int quiet = 0;
    dsu_u8 op;
    dsu_u8 scope;

    data_raw = dsu_msi_get_custom_action_data(hInstall);
    if (!data_raw) {
        dsu_msi_log(hInstall, "InvokeSetupCore: CustomActionData missing");
        return ERROR_INSTALL_FAILURE;
    }
    dsu_msi_parse_kv(data_raw, &data);

    op = dsu_msi_parse_operation(data.operation, &data);
    scope = dsu_msi_parse_scope(data.scope, &data);
    quiet = (dsu_msi_parse_uilevel(data.uilevel) < 5);

    dsu_invocation_init(&inv);
    inv.operation = op;
    inv.scope = scope;

    flags = 0u;
    if (dsu_msi_parse_bool(data.offline)) flags |= DSU_INVOCATION_POLICY_OFFLINE;
    if (dsu_msi_parse_bool(data.deterministic)) flags |= DSU_INVOCATION_POLICY_DETERMINISTIC;
    if (dsu_msi_parse_bool(data.allow_prerelease)) flags |= DSU_INVOCATION_POLICY_ALLOW_PRERELEASE;
    if (dsu_msi_parse_bool(data.legacy_mode)) flags |= DSU_INVOCATION_POLICY_LEGACY_MODE;
    inv.policy_flags = flags;

    inv.platform_triple = dsu_msi_strdup(data.platform ? data.platform : "win32-x86");
    inv.ui_mode = dsu_msi_strdup(quiet ? "cli" : (data.ui_mode && data.ui_mode[0] ? data.ui_mode : "gui"));
    inv.frontend_id = dsu_msi_strdup(data.frontend_id && data.frontend_id[0] ? data.frontend_id : "msi");
    if (!inv.platform_triple || !inv.ui_mode || !inv.frontend_id) {
        dsu_msi_log(hInstall, "InvokeSetupCore: failed to allocate invocation strings");
        goto done;
    }

    if (data.install_dir && data.install_dir[0]) {
        inv.install_roots = (char **)malloc(sizeof(char *));
        if (!inv.install_roots) goto done;
        inv.install_roots[0] = dsu_msi_strdup(data.install_dir);
        if (!inv.install_roots[0]) goto done;
        inv.install_root_count = 1u;
    }

    if (op == (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL) {
        if (!dsu_msi_csv_split(data.remove, &inv.selected_components, &inv.selected_component_count)) {
            goto done;
        }
    } else {
        if (!dsu_msi_csv_split(data.addlocal, &inv.selected_components, &inv.selected_component_count)) {
            goto done;
        }
        if (!dsu_msi_csv_split(data.remove, &inv.excluded_components, &inv.excluded_component_count)) {
            goto done;
        }
    }

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    if (flags & DSU_INVOCATION_POLICY_DETERMINISTIC) {
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    }
    if (dsu_ctx_create(&cfg, &cbs, NULL, &ctx) != DSU_STATUS_SUCCESS) {
        dsu_msi_log(hInstall, "InvokeSetupCore: ctx create failed");
        goto done;
    }

    if (data.invocation_path && data.invocation_path[0]) {
        strncpy(invocation_path, data.invocation_path, sizeof(invocation_path) - 1u);
        invocation_path[sizeof(invocation_path) - 1u] = '\0';
    } else {
        char temp_dir[512];
        if (!dsu_msi_get_temp_path(temp_dir, sizeof(temp_dir))) {
            dsu_msi_log(hInstall, "InvokeSetupCore: temp path missing");
            goto done;
        }
        if (!dsu_msi_path_join(invocation_path, sizeof(invocation_path), temp_dir, "dominium-invocation.tlv")) {
            dsu_msi_log(hInstall, "InvokeSetupCore: invocation path overflow");
            goto done;
        }
    }

    if (dsu_invocation_write_file(ctx, &inv, invocation_path) != DSU_STATUS_SUCCESS) {
        dsu_msi_log(hInstall, "InvokeSetupCore: failed to write invocation");
        goto done;
    }
    digest = dsu_invocation_digest(&inv);
    dsu_msi_log(hInstall, "InvokeSetupCore: invocation=%s digest=0x%08lx%08lx",
                invocation_path,
                (unsigned long)((digest >> 32) & 0xFFFFFFFFu),
                (unsigned long)(digest & 0xFFFFFFFFu));

    if (!data.install_dir || !data.install_dir[0]) {
        dsu_msi_log(hInstall, "InvokeSetupCore: INSTALLDIR missing");
        goto done;
    }
    if (!dsu_msi_path_join(setup_exe, sizeof(setup_exe), data.install_dir, ".dsu\\artifact_root\\setup\\dominium-setup.exe")) {
        dsu_msi_log(hInstall, "InvokeSetupCore: setup core path overflow");
        goto done;
    }

    ok = dsu_msi_run_setup_core(setup_exe, invocation_path, dsu_msi_parse_bool(data.deterministic), quiet);
    if (!ok) {
        dsu_msi_log(hInstall, "InvokeSetupCore: Setup Core failed");
        goto done;
    }
    ok = 1;

done:
    if (ctx) dsu_ctx_destroy(ctx);
    dsu_invocation_destroy(NULL, &inv);
    if (data_raw) free(data_raw);
    return ok ? ERROR_SUCCESS : ERROR_INSTALL_FAILURE;
}
