/*
FILE: source/dominium/setup/installers/windows/exe/win32/src/win32_entry.c
MODULE: Dominium Setup EXE (Win32/Win64 entry)
PURPOSE: Shared entrypoint and CLI dispatcher for Windows EXE installers.
*/
#include "dsu_exe_win32.h"

#include "dsu_exe_archive.h"
#include "dsu_exe_args.h"
#include "dsu_exe_bridge.h"
#include "dsu_exe_invocation.h"
#include "dsu_exe_log.h"
#include "dsu_exe_capability.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_invocation.h"
#include "dsu/dsu_manifest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

#define DSU_EXE_DEFAULT_MANIFEST "setup\\manifests\\product.dsumanifest"
#define DSU_EXE_FALLBACK_MANIFEST "setup\\manifests\\dominium_full.dsumanifest"
#define DSU_EXE_DEFAULT_CORE "setup\\dominium-setup.exe"
#define DSU_EXE_FALLBACK_CORE "setup\\tool_setup.exe"

#if defined(_MSC_VER)
#define dsu_exe_snprintf _snprintf
#else
#define dsu_exe_snprintf snprintf
#endif

static int dsu_exe_file_exists(const char *path) {
    DWORD attrs;
    if (!path || !path[0]) return 0;
    attrs = GetFileAttributesA(path);
    if (attrs == INVALID_FILE_ATTRIBUTES) return 0;
    return 1;
}

static void dsu_exe_print_help(void) {
    fprintf(stdout,
            "Dominium Setup EXE (Windows)\\n"
            "\\n"
            "Usage:\\n"
            "  setup.exe [--gui|--tui] [--help] [--version]\\n"
            "  setup.exe --cli <command> [options]\\n"
            "\\n"
            "CLI commands:\\n"
            "  install | upgrade | repair | uninstall\\n"
            "  detect | verify | plan | apply | export-invocation | apply-invocation\\n"
            "\\n"
            "Common CLI options:\\n"
            "  --manifest <file>          Manifest path (required for most commands)\\n"
            "  --state <file>             Installed state path\\n"
            "  --invocation <file>        Invocation payload path\\n"
            "  --plan <file>              Plan file path\\n"
            "  --out <file>               Output path (invocation/plan)\\n"
            "  --install-root <path>      Install root override\\n"
            "  --components <csv>         Selected components\\n"
            "  --exclude <csv>            Excluded components\\n"
            "  --scope <portable|user|system>\\n"
            "  --op <install|upgrade|repair|uninstall>\\n"
            "  --platform <triple>        Default platform triple\\n"
            "  --ui-mode <gui|tui|cli>     UI mode in invocation\\n"
            "  --frontend-id <id>         Frontend id in invocation\\n"
            "  --deterministic <0|1>       Default: 1\\n"
            "  --dry-run                   Plan/apply without mutation\\n"
            "  --json                      JSON output where supported\\n"
            "  --quiet                     Reduce output\\n"
            "  --offline | --allow-prerelease | --legacy\\n"
            "  --shortcuts | --file-assoc | --url-handlers\\n");
}

static void dsu_exe_print_version(void) {
    fprintf(stdout, "dominium-setup exe 0.0.0\\n");
}

static int dsu_exe_get_module_path(char *out, size_t cap) {
    DWORD n;
    if (!out || cap == 0u) return 0;
    out[0] = '\\0';
    n = GetModuleFileNameA(NULL, out, (DWORD)cap);
    if (n == 0u || n >= cap) {
        out[0] = '\\0';
        return 0;
    }
    return 1;
}

static int dsu_exe_make_temp_dir(char *out, size_t cap) {
    char base[MAX_PATH];
    char temp[MAX_PATH];
    DWORD n;
    if (!out || cap == 0u) return 0;
    n = GetTempPathA((DWORD)sizeof(base), base);
    if (n == 0u || n >= sizeof(base)) return 0;
    if (!GetTempFileNameA(base, "DSU", 0, temp)) return 0;
    DeleteFileA(temp);
    if (!CreateDirectoryA(temp, NULL)) return 0;
    strncpy(out, temp, cap - 1u);
    out[cap - 1u] = '\\0';
    return 1;
}

static int dsu_exe_remove_tree(const char *root) {
    char search[MAX_PATH];
    WIN32_FIND_DATAA fd;
    HANDLE h;
    size_t len;
    if (!root || !root[0]) return 0;
    len = strlen(root);
    if (len + 3 >= sizeof(search)) return 0;
    strcpy(search, root);
    if (search[len - 1] != '\\' && search[len - 1] != '/') {
        search[len++] = '\\';
    }
    search[len++] = '*';
    search[len] = '\\0';

    h = FindFirstFileA(search, &fd);
    if (h == INVALID_HANDLE_VALUE) {
        RemoveDirectoryA(root);
        return 1;
    }
    do {
        const char *name = fd.cFileName;
        char path[MAX_PATH];
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) {
            continue;
        }
        if (dsu_exe_snprintf(path, sizeof(path), "%s\\%s", root, name) <= 0) {
            continue;
        }
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            dsu_exe_remove_tree(path);
        } else {
            DeleteFileA(path);
        }
    } while (FindNextFileA(h, &fd));
    FindClose(h);
    RemoveDirectoryA(root);
    return 1;
}

static int dsu_exe_extract_archive(const char *exe_path, char *out_stage, size_t cap) {
    dsu_exe_archive_t *arch = NULL;
    char stage[MAX_PATH];
    int ok;
    if (!exe_path || !out_stage || cap == 0u) return 0;
    if (!dsu_exe_make_temp_dir(stage, sizeof(stage))) {
        return 0;
    }
    if (!dsu_exe_archive_open(exe_path, &arch)) {
        dsu_exe_remove_tree(stage);
        return 0;
    }
    ok = dsu_exe_archive_extract(arch, stage);
    dsu_exe_archive_close(arch);
    if (!ok) {
        dsu_exe_remove_tree(stage);
        return 0;
    }
    strncpy(out_stage, stage, cap - 1u);
    out_stage[cap - 1u] = '\\0';
    return 1;
}

static void dsu_exe_build_paths(const char *stage_root, dsu_exe_bridge_paths_t *out_paths) {
    static char manifest_path[MAX_PATH];
    static char core_path[MAX_PATH];
    if (!out_paths) return;
    out_paths->staging_root = stage_root;
    manifest_path[0] = '\\0';
    core_path[0] = '\\0';
    if (stage_root && stage_root[0]) {
        dsu_exe_snprintf(manifest_path, sizeof(manifest_path), "%s\\%s", stage_root, DSU_EXE_DEFAULT_MANIFEST);
        if (!dsu_exe_file_exists(manifest_path)) {
            dsu_exe_snprintf(manifest_path, sizeof(manifest_path), "%s\\%s", stage_root, DSU_EXE_FALLBACK_MANIFEST);
        }
        dsu_exe_snprintf(core_path, sizeof(core_path), "%s\\%s", stage_root, DSU_EXE_DEFAULT_CORE);
        if (!dsu_exe_file_exists(core_path)) {
            dsu_exe_snprintf(core_path, sizeof(core_path), "%s\\%s", stage_root, DSU_EXE_FALLBACK_CORE);
        }
    }
    out_paths->manifest_path = manifest_path[0] ? manifest_path : NULL;
    out_paths->core_exe_path = core_path[0] ? core_path : NULL;
}

static int dsu_exe_state_path_from_root(const char *install_root, char *out, size_t cap) {
    if (!install_root || !install_root[0] || !out || cap == 0u) return 0;
    if (dsu_exe_snprintf(out, cap, "%s\\.dsu\\installed_state.dsustate", install_root) <= 0) {
        return 0;
    }
    return 1;
}

static const char *dsu_exe_manifest_path(const dsu_exe_bridge_paths_t *paths, const dsu_exe_cli_args_t *cli) {
    const char *env = getenv("DSU_EXE_MANIFEST");
    if (cli && cli->manifest_path && cli->manifest_path[0]) return cli->manifest_path;
    if (env && env[0]) return env;
    if (paths && paths->manifest_path) return paths->manifest_path;
    return NULL;
}

static int dsu_exe_load_manifest(const char *path, dsu_ctx_t **out_ctx, dsu_manifest_t **out_manifest) {
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

static const char *dsu_exe_default_platform(const dsu_manifest_t *manifest, const char *fallback) {
    if (manifest) {
        dsu_u32 count = dsu_manifest_platform_target_count(manifest);
        if (count > 0u) {
            const char *p = dsu_manifest_platform_target(manifest, 0u);
            if (p && p[0]) return p;
        }
    }
    return fallback;
}

static int dsu_exe_scope_from_str(const char *s, dsu_manifest_install_scope_t *out_scope) {
    if (!s || !out_scope) return 0;
    if (_stricmp(s, "portable") == 0) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        return 1;
    }
    if (_stricmp(s, "user") == 0) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
        return 1;
    }
    if (_stricmp(s, "system") == 0) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
        return 1;
    }
    return 0;
}

static int dsu_exe_select_install_root(const dsu_manifest_t *manifest,
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
    out[cap - 1u] = '\\0';
    return 1;
}

static int dsu_exe_build_invocation_from_cli(const dsu_exe_cli_args_t *cli,
                                             const char *platform_default,
                                             const char *frontend_id,
                                             dsu_invocation_t *out_inv,
                                             char *out_install_root,
                                             size_t install_root_cap,
                                             const char *manifest_path) {
    dsu_exe_cli_args_t tmp;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    const char *platform = platform_default;
    int ok;

    if (!cli || !out_inv) return 0;
    tmp = *cli;

    if (manifest_path && (!tmp.install_root || !tmp.platform)) {
        if (dsu_exe_load_manifest(manifest_path, &ctx, &manifest)) {
            platform = dsu_exe_default_platform(manifest, platform_default);
            if (!tmp.platform) {
                tmp.platform = platform;
            }
            if (!tmp.install_root && out_install_root && install_root_cap > 0u) {
                dsu_manifest_install_scope_t scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
                if (tmp.scope) {
                    (void)dsu_exe_scope_from_str(tmp.scope, &scope);
                }
                if (dsu_exe_select_install_root(manifest, scope, platform, out_install_root, install_root_cap)) {
                    tmp.install_root = out_install_root;
                }
            }
        }
    }

    ok = dsu_exe_build_invocation(&tmp, platform_default, "cli", frontend_id, out_inv);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return ok;
}

static void dsu_exe_json_put_escaped(FILE *out, const char *s) {
    const unsigned char *p = (const unsigned char *)(s ? s : "");
    unsigned char c;
    fputc('"', out);
    while ((c = *p++) != 0u) {
        if (c == '\\\\' || c == '\"') {
            fputc('\\\\', out);
            fputc((int)c, out);
        } else if (c == '\\n') {
            fputs("\\\\n", out);
        } else if (c == '\\r') {
            fputs("\\\\r", out);
        } else if (c == '\\t') {
            fputs("\\\\t", out);
        } else if (c < 0x20u) {
            static const char hex[] = "0123456789abcdef";
            fputs("\\\\u00", out);
            fputc(hex[(c >> 4) & 0xFu], out);
            fputc(hex[c & 0xFu], out);
        } else {
            fputc((int)c, out);
        }
    }
    fputc('\"', out);
}

static void dsu_exe_json_put_path(FILE *out, const char *path) {
    const unsigned char *p = (const unsigned char *)(path ? path : "");
    unsigned char c;
    fputc('\"', out);
    while ((c = *p++) != 0u) {
        if (c == '\\\\') c = '/';
        if (c == '\\\\' || c == '\"') {
            fputc('\\\\', out);
            fputc((int)c, out);
        } else if (c == '\\n') {
            fputs("\\\\n", out);
        } else if (c == '\\r') {
            fputs("\\\\r", out);
        } else if (c == '\\t') {
            fputs("\\\\t", out);
        } else if (c < 0x20u) {
            static const char hex[] = "0123456789abcdef";
            fputs("\\\\u00", out);
            fputc(hex[(c >> 4) & 0xFu], out);
            fputc(hex[c & 0xFu], out);
        } else {
            fputc((int)c, out);
        }
    }
    fputc('\"', out);
}

static void dsu_exe_json_begin(const char *command, int status_code) {
    fputc('{', stdout);
    fputs("\"command\":", stdout); dsu_exe_json_put_escaped(stdout, command ? command : ""); fputc(',', stdout);
    fputs("\"status_code\":", stdout); fprintf(stdout, "%d", status_code); fputc(',', stdout);
    fputs("\"status\":", stdout); dsu_exe_json_put_escaped(stdout, status_code == 0 ? "ok" : "error"); fputc(',', stdout);
    fputs("\"details\":{", stdout);
}

static void dsu_exe_json_end(void) {
    fputs("}}\\n", stdout);
}

static int dsu_exe_cli_export_invocation(const dsu_exe_cli_args_t *cli,
                                         const dsu_exe_bridge_paths_t *paths,
                                         const char *platform,
                                         const char *frontend_id) {
    dsu_invocation_t inv;
    char install_root[512];
    const char *manifest_path;
    dsu_u64 digest = 0u;
    int ok;

    if (!cli || !cli->out_path) {
        return 3;
    }
    manifest_path = dsu_exe_manifest_path(paths, cli);
    install_root[0] = '\\0';
    memset(&inv, 0, sizeof(inv));
    ok = dsu_exe_build_invocation_from_cli(cli, platform, frontend_id, &inv,
                                           install_root, sizeof(install_root),
                                           manifest_path);
    if (!ok) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    if (dsu_invocation_validate(&inv) != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    ok = dsu_exe_write_invocation(&inv, cli->out_path, &digest);
    if (!ok) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    if (cli->want_json) {
        dsu_exe_json_begin("export-invocation", 0);
        fputs("\"invocation_file\":", stdout); dsu_exe_json_put_path(stdout, cli->out_path); fputc(',', stdout);
        fputs("\"invocation_digest64\":\"0x", stdout); fprintf(stdout, "%016llx", (unsigned long long)digest); fputc('"', stdout);
        dsu_exe_json_end();
    } else if (!cli->quiet) {
        fprintf(stdout, "invocation_digest64=0x%016llx\\n", (unsigned long long)digest);
    }
    dsu_invocation_destroy(NULL, &inv);
    return 0;
}

static int dsu_exe_cli_detect(const dsu_exe_cli_args_t *cli,
                              const dsu_exe_bridge_paths_t *paths,
                              const char *platform) {
    char install_root[512];
    char state_path[1024];
    const char *manifest_path;
    int detected = 0;

    if (cli && cli->state_path && cli->state_path[0]) {
        detected = dsu_exe_file_exists(cli->state_path);
    } else if (cli && cli->install_root && cli->install_root[0]) {
        if (dsu_exe_state_path_from_root(cli->install_root, state_path, sizeof(state_path))) {
            detected = dsu_exe_file_exists(state_path);
        }
    } else {
        dsu_ctx_t *ctx = NULL;
        dsu_manifest_t *manifest = NULL;
        manifest_path = dsu_exe_manifest_path(paths, cli);
        if (manifest_path && dsu_exe_load_manifest(manifest_path, &ctx, &manifest)) {
            dsu_manifest_install_scope_t scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
            if (cli && cli->scope) {
                (void)dsu_exe_scope_from_str(cli->scope, &scope);
            }
            if (dsu_exe_select_install_root(manifest, scope, platform, install_root, sizeof(install_root))) {
                if (dsu_exe_state_path_from_root(install_root, state_path, sizeof(state_path))) {
                    detected = dsu_exe_file_exists(state_path);
                }
            }
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
        }
    }

    if (cli && cli->want_json) {
        dsu_exe_json_begin("detect", detected ? 0 : 1);
        fputs("\"detected\":", stdout); fputs(detected ? "true" : "false", stdout);
        dsu_exe_json_end();
    } else if (!cli || !cli->quiet) {
        fprintf(stdout, "detected=%s\\n", detected ? "true" : "false");
    }
    return detected ? 0 : 1;
}

static int dsu_exe_cli_apply_invocation(const dsu_exe_cli_args_t *cli,
                                        const dsu_exe_bridge_paths_t *paths) {
    const char *manifest_path;
    const char *inv_path;
    const char *plan_path;
    char cmd[2048];
    int n;

    if (!cli) return 3;
    manifest_path = dsu_exe_manifest_path(paths, cli);
    inv_path = cli->invocation_path;
    plan_path = cli->out_path ? cli->out_path : cli->plan_path;
    if (!manifest_path || !inv_path || !plan_path) {
        return 3;
    }
    n = dsu_exe_snprintf(cmd, sizeof(cmd),
                 "\"%s\" apply-invocation --manifest \"%s\" --invocation \"%s\" --out \"%s\"%s%s%s%s",
                 paths->core_exe_path,
                 manifest_path,
                 inv_path,
                 plan_path,
                 cli->dry_run ? " --dry-run" : "",
                 cli->want_json ? " --json" : "",
                 cli->quiet ? " --quiet" : "",
                 cli->deterministic ? " --deterministic 1" : " --deterministic 0");
    if (n <= 0 || n >= (int)sizeof(cmd)) {
        return 1;
    }
    return dsu_exe_bridge_spawn(cmd, cli->quiet);
}

static int dsu_exe_cli_apply_plan(const dsu_exe_cli_args_t *cli,
                                  const dsu_exe_bridge_paths_t *paths) {
    char cmd[2048];
    int n;
    if (!cli || !cli->plan_path) return 3;
    n = dsu_exe_snprintf(cmd, sizeof(cmd),
                 "\"%s\" apply --plan \"%s\"%s%s%s%s",
                 paths->core_exe_path,
                 cli->plan_path,
                 cli->dry_run ? " --dry-run" : "",
                 cli->want_json ? " --json" : "",
                 cli->quiet ? " --quiet" : "",
                 cli->deterministic ? " --deterministic 1" : " --deterministic 0");
    if (n <= 0 || n >= (int)sizeof(cmd)) {
        return 1;
    }
    return dsu_exe_bridge_spawn(cmd, cli->quiet);
}

static int dsu_exe_cli_verify(const dsu_exe_cli_args_t *cli,
                              const dsu_exe_bridge_paths_t *paths,
                              const char *platform) {
    char install_root[512];
    char state_path[1024];
    const char *manifest_path;
    char cmd[2048];
    int n;

    if (!cli) return 3;
    if (cli->state_path && cli->state_path[0]) {
        strncpy(state_path, cli->state_path, sizeof(state_path) - 1u);
        state_path[sizeof(state_path) - 1u] = '\\0';
    } else if (cli->install_root && cli->install_root[0]) {
        if (!dsu_exe_state_path_from_root(cli->install_root, state_path, sizeof(state_path))) {
            return 3;
        }
    } else {
        dsu_ctx_t *ctx = NULL;
        dsu_manifest_t *manifest = NULL;
        manifest_path = dsu_exe_manifest_path(paths, cli);
        if (manifest_path && dsu_exe_load_manifest(manifest_path, &ctx, &manifest)) {
            dsu_manifest_install_scope_t scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
            if (cli->scope) {
                (void)dsu_exe_scope_from_str(cli->scope, &scope);
            }
            if (!dsu_exe_select_install_root(manifest, scope, platform, install_root, sizeof(install_root))) {
                dsu_manifest_destroy(ctx, manifest);
                dsu_ctx_destroy(ctx);
                return 3;
            }
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            if (!dsu_exe_state_path_from_root(install_root, state_path, sizeof(state_path))) {
                return 3;
            }
        } else {
            return 3;
        }
    }
    n = dsu_exe_snprintf(cmd, sizeof(cmd),
                 "\"%s\" verify --state \"%s\"%s%s%s%s",
                 paths->core_exe_path,
                 state_path,
                 cli->want_json ? " --json" : "",
                 cli->quiet ? " --quiet" : "",
                 cli->deterministic ? " --deterministic 1" : " --deterministic 0",
                 "");
    if (n <= 0 || n >= (int)sizeof(cmd)) {
        return 1;
    }
    return dsu_exe_bridge_spawn(cmd, cli->quiet);
}

static int dsu_exe_cli_plan(const dsu_exe_cli_args_t *cli,
                            const dsu_exe_bridge_paths_t *paths,
                            const char *platform,
                            const char *frontend_id) {
    dsu_invocation_t inv;
    char install_root[512];
    char inv_path[MAX_PATH];
    const char *manifest_path;
    const char *plan_path;
    dsu_u64 digest = 0u;
    int ok;
    int code;

    if (!cli) return 3;
    plan_path = cli->out_path ? cli->out_path : cli->plan_path;
    if (!plan_path) return 3;

    if (cli->invocation_path) {
        dsu_exe_bridge_paths_t plan_paths = *paths;
        if (cli->manifest_path && cli->manifest_path[0]) {
            plan_paths.manifest_path = cli->manifest_path;
        }
        return dsu_exe_bridge_plan(&plan_paths, cli->invocation_path, plan_path,
                                   cli->deterministic, cli->quiet, cli->want_json);
    }

    manifest_path = dsu_exe_manifest_path(paths, cli);
    install_root[0] = '\\0';
    memset(&inv, 0, sizeof(inv));
    ok = dsu_exe_build_invocation_from_cli(cli, platform, frontend_id, &inv,
                                           install_root, sizeof(install_root),
                                           manifest_path);
    if (!ok) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    if (dsu_invocation_validate(&inv) != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    if (!GetTempPathA((DWORD)sizeof(inv_path), inv_path)) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    strncat(inv_path, "dominium-invocation.tlv", sizeof(inv_path) - strlen(inv_path) - 1u);
    ok = dsu_exe_write_invocation(&inv, inv_path, &digest);
    dsu_invocation_destroy(NULL, &inv);
    if (!ok) {
        return 1;
    }
    code = dsu_exe_bridge_plan(paths, inv_path, plan_path,
                               cli->deterministic, cli->quiet, cli->want_json);
    return code;
}

static int dsu_exe_cli_apply_from_cli(const dsu_exe_cli_args_t *cli,
                                      const dsu_exe_bridge_paths_t *paths,
                                      const char *platform,
                                      const char *frontend_id) {
    dsu_invocation_t inv;
    char install_root[512];
    char inv_path[MAX_PATH];
    const char *manifest_path;
    dsu_u64 digest = 0u;
    int ok;
    int code;

    if (!cli) return 3;

    if (cli->plan_path) {
        return dsu_exe_cli_apply_plan(cli, paths);
    }
    if (cli->invocation_path) {
        return dsu_exe_bridge_apply_invocation(paths, cli->invocation_path,
                                               cli->deterministic, cli->dry_run,
                                               cli->quiet, cli->want_json);
    }

    manifest_path = dsu_exe_manifest_path(paths, cli);
    install_root[0] = '\\0';
    memset(&inv, 0, sizeof(inv));
    ok = dsu_exe_build_invocation_from_cli(cli, platform, frontend_id, &inv,
                                           install_root, sizeof(install_root),
                                           manifest_path);
    if (!ok) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    if (dsu_invocation_validate(&inv) != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(NULL, &inv);
        return 3;
    }
    if (!GetTempPathA((DWORD)sizeof(inv_path), inv_path)) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    strncat(inv_path, "dominium-invocation.tlv", sizeof(inv_path) - strlen(inv_path) - 1u);
    ok = dsu_exe_write_invocation(&inv, inv_path, &digest);
    dsu_invocation_destroy(NULL, &inv);
    if (!ok) {
        return 1;
    }
    code = dsu_exe_bridge_apply_invocation(paths, inv_path,
                                           cli->deterministic, cli->dry_run,
                                           cli->quiet, cli->want_json);
    return code;
}

int dsu_exe_apply_from_state(const dsu_exe_bridge_paths_t *paths,
                             const char *platform,
                             const char *frontend_id,
                             const dsu_ui_state_t *state,
                             const char *components_csv,
                             const char *exclude_csv,
                             const char *ui_mode,
                             int quiet) {
    dsu_exe_cli_args_t args;
    dsu_invocation_t inv;
    char install_root[512];
    char inv_path[MAX_PATH];
    dsu_u64 digest = 0u;
    int ok;

    if (!paths || !state) return 1;
    memset(&args, 0, sizeof(args));
    args.deterministic = 1;
    args.quiet = quiet;

    switch (state->operation) {
        case 1: args.operation = "upgrade"; break;
        case 2: args.operation = "repair"; break;
        case 3: args.operation = "uninstall"; break;
        default: args.operation = "install"; break;
    }

    switch (state->scope) {
        case DSU_MANIFEST_INSTALL_SCOPE_PORTABLE: args.scope = "portable"; break;
        case DSU_MANIFEST_INSTALL_SCOPE_SYSTEM: args.scope = "system"; break;
        default: args.scope = "user"; break;
    }

    args.install_root = state->install_root[0] ? state->install_root : NULL;
    args.components_csv = components_csv;
    args.exclude_csv = exclude_csv;
    args.ui_mode = ui_mode ? ui_mode : "gui";
    args.frontend_id = frontend_id;
    args.policy_shortcuts = state->enable_shortcuts;
    args.policy_file_assoc = state->enable_file_assoc;
    args.policy_url_handlers = state->enable_url_handlers;

    install_root[0] = '\\0';
    memset(&inv, 0, sizeof(inv));
    ok = dsu_exe_build_invocation(&args, platform, args.ui_mode, frontend_id, &inv);
    if (!ok) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    if (dsu_invocation_validate(&inv) != DSU_STATUS_SUCCESS) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    if (!GetTempPathA((DWORD)sizeof(inv_path), inv_path)) {
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    strncat(inv_path, "dominium-invocation.tlv", sizeof(inv_path) - strlen(inv_path) - 1u);
    ok = dsu_exe_write_invocation(&inv, inv_path, &digest);
    if (ok) {
        dsu_exe_log_info("invocation_digest64=0x%016llx", (unsigned long long)digest);
    }
    dsu_invocation_destroy(NULL, &inv);
    if (!ok) {
        return 1;
    }
    return dsu_exe_bridge_apply_invocation(paths, inv_path, 1, 0, quiet, 0);
}

int dsu_exe_entry_run(int argc, char **argv, const char *platform, const char *frontend_id) {
    dsu_exe_mode_t mode;
    dsu_exe_cli_args_t cli;
    dsu_exe_bridge_paths_t paths;
    dsu_exe_capabilities_t caps;
    char exe_path[MAX_PATH];
    char stage_root[MAX_PATH];
    int have_stage = 0;
    int extracted = 0;
    int code = 0;

    dsu_exe_args_parse(argc, argv, &mode, &cli);
    if (cli.want_help) {
        dsu_exe_print_help();
        return 0;
    }
    if (cli.want_version) {
        dsu_exe_print_version();
        return 0;
    }

    dsu_exe_detect_capabilities(&caps);
    if (!dsu_exe_get_module_path(exe_path, sizeof(exe_path))) {
        exe_path[0] = '\\0';
    }

    stage_root[0] = '\\0';
    if (exe_path[0] && dsu_exe_extract_archive(exe_path, stage_root, sizeof(stage_root))) {
        have_stage = 1;
        extracted = 1;
    } else {
        const char *env_stage = getenv("DSU_EXE_STAGE");
        if (env_stage && env_stage[0]) {
            strncpy(stage_root, env_stage, sizeof(stage_root) - 1u);
            stage_root[sizeof(stage_root) - 1u] = '\\0';
            have_stage = 1;
        }
    }

    memset(&paths, 0, sizeof(paths));
    if (have_stage) {
        dsu_exe_build_paths(stage_root, &paths);
    }

    if (mode == DSU_EXE_MODE_CLI) {
        switch (cli.command) {
            case DSU_EXE_CMD_EXPORT_INVOCATION:
                code = dsu_exe_cli_export_invocation(&cli, &paths, platform, frontend_id);
                break;
            case DSU_EXE_CMD_DETECT:
                code = dsu_exe_cli_detect(&cli, &paths, platform);
                break;
            case DSU_EXE_CMD_VERIFY:
                if (!paths.core_exe_path) {
                    return 3;
                }
                code = dsu_exe_cli_verify(&cli, &paths, platform);
                break;
            case DSU_EXE_CMD_PLAN:
                if (!paths.core_exe_path) {
                    return 3;
                }
                code = dsu_exe_cli_plan(&cli, &paths, platform, frontend_id);
                break;
            case DSU_EXE_CMD_APPLY:
                if (!paths.core_exe_path) {
                    return 3;
                }
                code = dsu_exe_cli_apply_from_cli(&cli, &paths, platform, frontend_id);
                break;
            case DSU_EXE_CMD_APPLY_INVOCATION:
                if (!paths.core_exe_path) {
                    return 3;
                }
                code = dsu_exe_cli_apply_invocation(&cli, &paths);
                break;
            case DSU_EXE_CMD_INSTALL:
            case DSU_EXE_CMD_UPGRADE:
            case DSU_EXE_CMD_REPAIR:
            case DSU_EXE_CMD_UNINSTALL: {
                dsu_exe_cli_args_t tmp = cli;
                if (cli.command == DSU_EXE_CMD_INSTALL) tmp.operation = "install";
                if (cli.command == DSU_EXE_CMD_UPGRADE) tmp.operation = "upgrade";
                if (cli.command == DSU_EXE_CMD_REPAIR) tmp.operation = "repair";
                if (cli.command == DSU_EXE_CMD_UNINSTALL) tmp.operation = "uninstall";
                code = dsu_exe_cli_apply_from_cli(&tmp, &paths, platform, frontend_id);
                break;
            }
            default:
                dsu_exe_print_help();
                code = 3;
                break;
        }
        if (extracted && code == 0) {
            dsu_exe_remove_tree(stage_root);
        }
        return code;
    }

    if (!paths.core_exe_path || !paths.manifest_path) {
        fprintf(stderr, "error: installer payload missing (no embedded archive)\\n");
        return 1;
    }

    if (mode == DSU_EXE_MODE_TUI) {
        if (caps.has_console) {
            code = dsu_exe_run_tui(&paths, platform, frontend_id, 0);
        } else {
            code = dsu_exe_run_gui(&paths, platform, frontend_id, 0);
        }
    } else {
        code = dsu_exe_run_gui(&paths, platform, frontend_id, 0);
    }

    if (extracted && code == 0) {
        dsu_exe_remove_tree(stage_root);
    }
    return code;
}
