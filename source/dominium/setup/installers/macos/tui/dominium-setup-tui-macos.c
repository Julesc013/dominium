/*
FILE: source/dominium/setup/installers/macos/tui/dominium-setup-tui-macos.c
MODULE: Dominium Setup macOS
PURPOSE: Text-mode installer frontend (wizard + non-interactive).
*/
#include "dsu_macos_args.h"
#include "dsu_macos_bridge.h"
#include "dsu_macos_invocation.h"
#include "dsu_macos_log.h"
#include "dsu_macos_tui.h"
#include "dsu_macos_ui.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_state.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/stat.h>
#include <unistd.h>
#endif

#define DSU_MACOS_TUI_NAME "dominium-setup-tui"
#define DSU_MACOS_TUI_VERSION "0.0.0"

static void dsu__usage(FILE *out) {
    fprintf(out,
            "%s %s\n"
            "\n"
            "Usage:\n"
            "  %s [--manifest <path>] [--non-interactive] [--defaults]\n"
            "     [--op install|upgrade|repair|uninstall]\n"
            "     [--scope portable|user|system]\n"
            "     [--components <csv>] [--exclude <csv>]\n"
            "     [--install-root <path>] [--platform <triple>]\n"
            "     [--export-invocation --out <path>]\n"
            "     [--plan --out <plan>] [--apply] [--dry-run]\n",
            DSU_MACOS_TUI_NAME, DSU_MACOS_TUI_VERSION,
            DSU_MACOS_TUI_NAME);
}

static int dsu__streq(const char *a, const char *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    return strcmp(a, b) == 0;
}

static int dsu__streq_nocase(const char *a, const char *b) {
    unsigned char ca;
    unsigned char cb;
    if (a == b) return 1;
    if (!a || !b) return 0;
    for (;;) {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
        if (ca >= 'A' && ca <= 'Z') ca = (unsigned char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (unsigned char)(cb - 'A' + 'a');
        if (ca != cb) return 0;
        if (ca == 0u) return 1;
    }
}

static int dsu__file_exists(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    struct stat st;
    if (!path || !path[0]) return 0;
    return stat(path, &st) == 0;
#else
    (void)path;
    return 0;
#endif
}

static int dsu__file_is_exec(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    return (path && path[0] && access(path, X_OK) == 0);
#else
    (void)path;
    return 0;
#endif
}

static int dsu__find_in_path(const char *name, char *out, size_t cap) {
    const char *path = getenv("PATH");
    const char *p;
    const char *next;
    char buf[512];
    size_t len;

    if (!name || !out || cap == 0u) return 0;
    out[0] = '\0';

    if (dsu__file_is_exec(name)) {
        strncpy(out, name, cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }

    if (!path || !path[0]) return 0;
    p = path;
    while (p && *p) {
        next = strchr(p, ':');
        len = next ? (size_t)(next - p) : strlen(p);
        if (len > 0 && len < sizeof(buf)) {
            memcpy(buf, p, len);
            buf[len] = '\0';
            snprintf(out, cap, "%s/%s", buf, name);
            if (dsu__file_is_exec(out)) {
                return 1;
            }
        }
        if (!next) break;
        p = next + 1;
    }
    out[0] = '\0';
    return 0;
}

static const char *dsu__resolve_exe_path(const char *argv0, const char *name, char *out, size_t cap) {
    const char *slash = NULL;
    if (!name) return "";
    if (out && cap) out[0] = '\0';
    if (argv0) {
        const char *s1 = strrchr(argv0, '/');
        const char *s2 = strrchr(argv0, '\\');
        slash = s1;
        if (s2 && (!slash || s2 > slash)) slash = s2;
        if (slash && out && cap) {
            size_t len = (size_t)(slash - argv0);
            char dir[512];
            if (len >= sizeof(dir)) len = sizeof(dir) - 1u;
            memcpy(dir, argv0, len);
            dir[len] = '\0';
            snprintf(out, cap, "%s/%s", dir, name);
            if (dsu__file_is_exec(out)) {
                return out;
            }
        }
    }
    if (out && cap && dsu__find_in_path(name, out, cap)) {
        return out;
    }
    return name;
}

static const char *dsu__resolve_core_path(const char *argv0, char *out, size_t cap) {
    const char *candidate = dsu__resolve_exe_path(argv0, "dominium-setup", out, cap);
    if (candidate && dsu__file_is_exec(candidate)) {
        return candidate;
    }
    candidate = dsu__resolve_exe_path(argv0, "tool_setup", out, cap);
    if (candidate && dsu__file_is_exec(candidate)) {
        return candidate;
    }
    return "dominium-setup";
}

static const char *dsu__default_platform(void) {
#if defined(__aarch64__) || defined(__arm64__)
    return "macos-arm64";
#elif defined(__x86_64__) || defined(__amd64__)
    return "macos-x64";
#else
    return "macos-x64";
#endif
}

static const char *dsu__default_manifest_path(const char *argv0, char *out_path, size_t cap) {
    const char *fallback = "setup/manifests/product.dsumanifest";
    const char *slash = NULL;
    char dir[512];
    if (!out_path || cap == 0u) return fallback;
    out_path[0] = '\0';

    if (dsu__file_exists(fallback)) {
        strncpy(out_path, fallback, cap - 1u);
        out_path[cap - 1u] = '\0';
        return out_path;
    }

    if (argv0) {
        const char *s1 = strrchr(argv0, '/');
        const char *s2 = strrchr(argv0, '\\');
        slash = s1;
        if (s2 && (!slash || s2 > slash)) slash = s2;
    }
    if (slash) {
        size_t len = (size_t)(slash - argv0);
        if (len >= sizeof(dir)) len = sizeof(dir) - 1u;
        memcpy(dir, argv0, len);
        dir[len] = '\0';
        if (snprintf(out_path, cap, "%s/manifests/product.dsumanifest", dir) > 0 && dsu__file_exists(out_path)) {
            return out_path;
        }
        if (snprintf(out_path, cap, "%s/../setup/manifests/product.dsumanifest", dir) > 0 && dsu__file_exists(out_path)) {
            return out_path;
        }
    }

    strncpy(out_path, fallback, cap - 1u);
    out_path[cap - 1u] = '\0';
    return out_path;
}

static dsu_manifest_install_scope_t dsu__scope_from_str(const char *s, dsu_manifest_install_scope_t fallback) {
    if (!s || !s[0]) return fallback;
    if (dsu__streq_nocase(s, "system")) return DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    if (dsu__streq_nocase(s, "portable")) return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    if (dsu__streq_nocase(s, "user")) return DSU_MANIFEST_INSTALL_SCOPE_USER;
    return fallback;
}

static int dsu__operation_needs_state(const char *op) {
    if (!op || !op[0]) return 0;
    return dsu__streq_nocase(op, "upgrade") ||
           dsu__streq_nocase(op, "repair") ||
           dsu__streq_nocase(op, "uninstall");
}

static const char *dsu__default_temp_path(const char *name, char *out_path, size_t cap) {
    const char *tmp = getenv("TMPDIR");
    if (!tmp || !tmp[0]) tmp = "/tmp";
    if (!out_path || cap == 0u) return name;
    out_path[0] = '\0';
    snprintf(out_path, cap, "%s/%s", tmp, name);
    return out_path;
}

static int dsu__find_manifest_install_root(const dsu_manifest_t *manifest,
                                           dsu_manifest_install_scope_t scope,
                                           const char *platform,
                                           char *out_root,
                                           size_t out_cap) {
    dsu_u32 count;
    dsu_u32 i;
    const char *found = NULL;
    dsu_u32 found_count = 0u;
    if (!manifest || !platform || !out_root || out_cap == 0u) {
        return 0;
    }
    out_root[0] = '\0';
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        dsu_manifest_install_scope_t s = dsu_manifest_install_root_scope(manifest, i);
        const char *p = dsu_manifest_install_root_platform(manifest, i);
        const char *path = dsu_manifest_install_root_path(manifest, i);
        if ((dsu_u8)s != (dsu_u8)scope) {
            continue;
        }
        if (!p || strcmp(p, platform) != 0) {
            continue;
        }
        found = path;
        ++found_count;
    }
    if (!found || found_count != 1u) {
        return 0;
    }
    strncpy(out_root, found, out_cap - 1u);
    out_root[out_cap - 1u] = '\0';
    return 1;
}

static int dsu__build_state_path(const char *install_root, char *out_state, size_t cap) {
    if (!install_root || !install_root[0] || !out_state || cap == 0u) {
        return 0;
    }
    snprintf(out_state, cap, "%s/.dsu/installed_state.dsustate", install_root);
    return 1;
}

static int dsu__detect_installed_state(const dsu_manifest_t *manifest,
                                       const char *platform,
                                       char *out_state,
                                       size_t out_cap,
                                       dsu_manifest_install_scope_t *out_scope) {
    dsu_manifest_install_scope_t scopes[3];
    size_t i;
    char root[512];
    char state[512];

    scopes[0] = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    scopes[1] = DSU_MANIFEST_INSTALL_SCOPE_USER;
    scopes[2] = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;

    for (i = 0u; i < 3u; ++i) {
        if (!dsu__find_manifest_install_root(manifest, scopes[i], platform, root, sizeof(root))) {
            continue;
        }
        if (!dsu__build_state_path(root, state, sizeof(state))) {
            continue;
        }
        if (dsu__file_exists(state)) {
            if (out_state && out_cap) {
                strncpy(out_state, state, out_cap - 1u);
                out_state[out_cap - 1u] = '\0';
            }
            if (out_scope) {
                *out_scope = scopes[i];
            }
            return 1;
        }
    }
    return 0;
}

static int dsu__prompt_menu(const char *title,
                            const char *const *options,
                            int option_count,
                            int default_index) {
    char buf[64];
    int choice = default_index;
    int parsed = 0;
    int i;
    if (!options || option_count <= 0) return -1;
    fprintf(stdout, "\n%s\n", title ? title : "");
    for (i = 0; i < option_count; ++i) {
        fprintf(stdout, "  %d) %s\n", i + 1, options[i] ? options[i] : "");
    }
    fprintf(stdout, "Select [default %d]: ", default_index + 1);
    dsu_macos_tui_flush();
    if (!dsu_macos_tui_read_line(buf, sizeof(buf))) {
        return choice;
    }
    dsu_macos_tui_trim(buf);
    if (buf[0] == '\0') {
        return choice;
    }
    parsed = atoi(buf);
    if (parsed >= 1 && parsed <= option_count) {
        choice = parsed - 1;
    }
    return choice;
}

static int dsu__prompt_yes_no(const char *label, int default_yes) {
    char buf[16];
    fprintf(stdout, "%s [%s]: ", label ? label : "", default_yes ? "Y/n" : "y/N");
    dsu_macos_tui_flush();
    if (!dsu_macos_tui_read_line(buf, sizeof(buf))) {
        return default_yes;
    }
    dsu_macos_tui_trim(buf);
    if (buf[0] == '\0') {
        return default_yes;
    }
    if (buf[0] == 'y' || buf[0] == 'Y') return 1;
    if (buf[0] == 'n' || buf[0] == 'N') return 0;
    return default_yes;
}

static char *dsu__dup_str(const char *s) {
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

static int dsu__list_add(char ***items, unsigned long *count, unsigned long *cap, const char *value) {
    char **next;
    char *dup;
    unsigned long new_cap;
    if (!items || !count || !cap || !value) return 0;
    if (*count == *cap) {
        new_cap = (*cap == 0u) ? 8u : (*cap * 2u);
        next = (char **)realloc(*items, new_cap * sizeof(*next));
        if (!next) return 0;
        *items = next;
        *cap = new_cap;
    }
    dup = dsu__dup_str(value);
    if (!dup) return 0;
    (*items)[(*count)++] = dup;
    return 1;
}

static void dsu__list_free(char **items, unsigned long count) {
    unsigned long i;
    if (!items) return;
    for (i = 0; i < count; ++i) {
        free(items[i]);
    }
    free(items);
}

static char *dsu__csv_from_list(char **items, unsigned long count) {
    size_t total = 1u;
    unsigned long i;
    char *out;
    size_t pos = 0u;
    if (!items || count == 0u) {
        return NULL;
    }
    for (i = 0; i < count; ++i) {
        const char *s = items[i] ? items[i] : "";
        total += strlen(s) + 1u;
    }
    out = (char *)malloc(total);
    if (!out) return NULL;
    out[0] = '\0';
    for (i = 0; i < count; ++i) {
        const char *s = items[i] ? items[i] : "";
        size_t n = strlen(s);
        if (i != 0u) {
            out[pos++] = ',';
        }
        memcpy(out + pos, s, n);
        pos += n;
        out[pos] = '\0';
    }
    return out;
}

static void dsu__parse_index_list(const char *buf, unsigned char *selected, dsu_u32 count) {
    const char *p = buf;
    if (!buf || !selected || count == 0u) return;
    while (*p) {
        unsigned long v = 0ul;
        int any = 0;
        while (*p == ' ' || *p == '\t' || *p == ',' || *p == ';') ++p;
        while (*p >= '0' && *p <= '9') {
            v = (v * 10ul) + (unsigned long)(*p - '0');
            any = 1;
            ++p;
        }
        if (any && v >= 1ul && v <= (unsigned long)count) {
            selected[v - 1ul] = 1u;
        }
        while (*p && *p != ',' && *p != ';') ++p;
    }
}

static int dsu__select_components(const dsu_manifest_t *manifest,
                                  char ***out_selected,
                                  unsigned long *out_selected_count) {
    dsu_u32 count;
    dsu_u32 i;
    unsigned long cap = 0u;
    char **selected = NULL;
    const char **ids = NULL;
    unsigned char *optional = NULL;
    unsigned char *default_on = NULL;
    unsigned char *picked = NULL;
    char buf[128];

    if (!manifest || !out_selected || !out_selected_count) {
        return 0;
    }
    *out_selected = NULL;
    *out_selected_count = 0u;

    count = dsu_manifest_component_count(manifest);
    if (count == 0u) {
        return 1;
    }

    ids = (const char **)malloc(sizeof(*ids) * count);
    optional = (unsigned char *)malloc(sizeof(*optional) * count);
    default_on = (unsigned char *)malloc(sizeof(*default_on) * count);
    picked = (unsigned char *)malloc(sizeof(*picked) * count);
    if (!ids || !optional || !default_on || !picked) {
        free(ids);
        free(optional);
        free(default_on);
        free(picked);
        return 0;
    }
    memset(picked, 0, count * sizeof(*picked));

    fprintf(stdout, "\nComponents\n");
    for (i = 0u; i < count; ++i) {
        const char *id = dsu_manifest_component_id(manifest, i);
        dsu_u32 flags = dsu_manifest_component_flags(manifest, i);
        int is_optional = (flags & DSU_MANIFEST_COMPONENT_FLAG_OPTIONAL) != 0u;
        int is_default = (flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) != 0u;

        ids[i] = id ? id : "";
        optional[i] = (unsigned char)(is_optional ? 1u : 0u);
        default_on[i] = (unsigned char)(is_default ? 1u : 0u);

        if (!is_optional) {
            fprintf(stdout, "  %lu) %s [required]\n", (unsigned long)(i + 1u), ids[i]);
        } else if (is_default) {
            fprintf(stdout, "  %lu) %s [default]\n", (unsigned long)(i + 1u), ids[i]);
        } else {
            fprintf(stdout, "  %lu) %s\n", (unsigned long)(i + 1u), ids[i]);
        }
    }
    fprintf(stdout, "Select components (comma-separated numbers, empty=defaults): ");
    dsu_macos_tui_flush();
    if (dsu_macos_tui_read_line(buf, sizeof(buf))) {
        dsu_macos_tui_trim(buf);
    } else {
        buf[0] = '\0';
    }

    if (buf[0] == '\0') {
        for (i = 0u; i < count; ++i) {
            if (!optional[i] || default_on[i]) {
                picked[i] = 1u;
            }
        }
    } else {
        dsu__parse_index_list(buf, picked, count);
        for (i = 0u; i < count; ++i) {
            if (!optional[i]) {
                picked[i] = 1u;
            }
        }
    }

    for (i = 0u; i < count; ++i) {
        if (picked[i] && ids[i] && ids[i][0]) {
            if (!dsu__list_add(&selected, out_selected_count, &cap, ids[i])) {
                dsu__list_free(selected, *out_selected_count);
                free(ids);
                free(optional);
                free(default_on);
                free(picked);
                *out_selected = NULL;
                *out_selected_count = 0u;
                return 0;
            }
        }
    }

    free(ids);
    free(optional);
    free(default_on);
    free(picked);
    *out_selected = selected;
    return 1;
}

static int dsu__run_platform_register(const dsu_macos_bridge_paths_t *paths,
                                      const char *state_path,
                                      int deterministic,
                                      int quiet) {
    char cmd[1024];
    if (!paths || !paths->adapter_exe_path || !state_path) {
        return 0;
    }
    snprintf(cmd,
             sizeof(cmd),
             "\"%s\" platform-register --state \"%s\"%s",
             paths->adapter_exe_path,
             state_path,
             deterministic ? " --deterministic" : "");
    return (dsu_macos_bridge_spawn(cmd, quiet) == 0);
}

static int dsu__run_platform_unregister(const dsu_macos_bridge_paths_t *paths,
                                        const char *state_path,
                                        int deterministic,
                                        int quiet) {
    char cmd[1024];
    if (!paths || !paths->adapter_exe_path || !state_path) {
        return 0;
    }
    snprintf(cmd,
             sizeof(cmd),
             "\"%s\" platform-unregister --state \"%s\"%s",
             paths->adapter_exe_path,
             state_path,
             deterministic ? " --deterministic" : "");
    return (dsu_macos_bridge_spawn(cmd, quiet) == 0);
}

static int dsu__run_non_interactive(const dsu_macos_cli_args_t *args,
                                    const dsu_macos_bridge_paths_t *paths,
                                    const char *platform,
                                    const char *manifest_path) {
    dsu_invocation_t inv;
    char inv_path[512];
    char plan_path[512];
    char state_path[512];
    dsu_u64 digest = 0u;
    int ok;
    const char *out_inv;
    const char *out_plan;
    dsu_macos_cli_args_t tmp_args = *args;

    if (!args || !paths || !platform || !manifest_path) {
        return 1;
    }

    dsu_invocation_init(&inv);

    if (!tmp_args.ui_mode) tmp_args.ui_mode = "tui";
    if (!tmp_args.frontend_id) tmp_args.frontend_id = "tui-macos";
    if (!tmp_args.operation) tmp_args.operation = "install";
    if (!tmp_args.scope) tmp_args.scope = "user";

    out_inv = tmp_args.out_path ? tmp_args.out_path : tmp_args.invocation_path;
    if (!out_inv || !out_inv[0]) {
        out_inv = dsu__default_temp_path("dominium-invocation.tlv", inv_path, sizeof(inv_path));
    }

    ok = dsu_macos_build_invocation(&tmp_args, platform, tmp_args.ui_mode, tmp_args.frontend_id, &inv);
    if (!ok) {
        dsu_macos_log_error("failed to build invocation");
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    if (!dsu_macos_write_invocation(&inv, out_inv, &digest)) {
        dsu_macos_log_error("failed to write invocation: %s", out_inv);
        dsu_invocation_destroy(NULL, &inv);
        return 1;
    }
    dsu_macos_log_info("invocation written: %s", out_inv);
    dsu_macos_log_info("invocation digest64: 0x%016llx", (unsigned long long)digest);

    if (tmp_args.export_invocation && !tmp_args.run_plan && !tmp_args.run_apply && !tmp_args.apply_invocation) {
        dsu_invocation_destroy(NULL, &inv);
        return 0;
    }

    out_plan = tmp_args.plan_path;
    if (!out_plan || !out_plan[0]) {
        out_plan = dsu__default_temp_path("dominium-plan.tlv", plan_path, sizeof(plan_path));
    }

    if (tmp_args.run_plan || tmp_args.run_apply || tmp_args.apply_invocation) {
        if (dsu_macos_bridge_plan(paths,
                                  out_inv,
                                  out_plan,
                                  tmp_args.state_path,
                                  tmp_args.deterministic,
                                  tmp_args.quiet,
                                  tmp_args.want_json) != 0) {
            dsu_macos_log_error("plan failed");
            dsu_invocation_destroy(NULL, &inv);
            return 1;
        }
    }

    if (tmp_args.run_plan && !tmp_args.run_apply && !tmp_args.apply_invocation) {
        dsu_invocation_destroy(NULL, &inv);
        return 0;
    }

    if (tmp_args.apply_invocation) {
        if (dsu_macos_bridge_apply_invocation(paths, out_inv, tmp_args.deterministic, tmp_args.dry_run, tmp_args.quiet, tmp_args.want_json) != 0) {
            dsu_macos_log_error("apply (invocation) failed");
            dsu_invocation_destroy(NULL, &inv);
            return 1;
        }
    } else if (tmp_args.run_apply || !tmp_args.export_invocation) {
        if (dsu_macos_bridge_apply_plan(paths, out_plan, tmp_args.deterministic, tmp_args.dry_run, tmp_args.quiet, tmp_args.want_json) != 0) {
            dsu_macos_log_error("apply failed");
            dsu_invocation_destroy(NULL, &inv);
            return 1;
        }
    }

    if (tmp_args.install_root && tmp_args.install_root[0]) {
        dsu__build_state_path(tmp_args.install_root, state_path, sizeof(state_path));
        if (dsu__streq(tmp_args.operation, "uninstall")) {
            (void)dsu__run_platform_unregister(paths, state_path, tmp_args.deterministic, tmp_args.quiet);
        } else {
            (void)dsu__run_platform_register(paths, state_path, tmp_args.deterministic, tmp_args.quiet);
        }
    }

    dsu_invocation_destroy(NULL, &inv);
    return 0;
}

int main(int argc, char **argv) {
    dsu_macos_cli_args_t args;
    dsu_macos_bridge_paths_t paths;
    dsu_macos_ui_state_t ui;
    dsu_manifest_t *manifest = NULL;
    dsu_ctx_t *ctx = NULL;
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    char manifest_path[512];
    char install_root[512];
    char state_path[512];
    char platform_buf[64];
    char core_path[512];
    char adapter_path[512];
    const char *platform;
    int exit_code = 1;

    if (!dsu_macos_args_parse(argc, argv, &args)) {
        dsu__usage(stderr);
        return 2;
    }

    if (args.want_help) {
        dsu__usage(stdout);
        return 0;
    }
    if (args.want_version) {
        fprintf(stdout, "%s %s\n", DSU_MACOS_TUI_NAME, DSU_MACOS_TUI_VERSION);
        return 0;
    }

    if (args.log_path) {
        dsu_macos_log_set_file(args.log_path);
    }

    memset(&paths, 0, sizeof(paths));
    platform = args.platform ? args.platform : dsu__default_platform();
    strncpy(platform_buf, platform, sizeof(platform_buf) - 1u);
    platform_buf[sizeof(platform_buf) - 1u] = '\0';

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    if (dsu_ctx_create(&cfg, &cbs, NULL, &ctx) != DSU_STATUS_SUCCESS) {
        dsu_macos_log_error("failed to init setup core");
        return 1;
    }

    dsu__default_manifest_path(argv[0], manifest_path, sizeof(manifest_path));
    if (args.manifest_path && args.manifest_path[0]) {
        strncpy(manifest_path, args.manifest_path, sizeof(manifest_path) - 1u);
        manifest_path[sizeof(manifest_path) - 1u] = '\0';
    }

    if (dsu_manifest_load_file(ctx, manifest_path, &manifest) != DSU_STATUS_SUCCESS) {
        dsu_macos_log_error("failed to load manifest: %s", manifest_path);
        dsu_ctx_destroy(ctx);
        return 1;
    }

    dsu_macos_ui_state_init(&ui);
    strncpy(install_root, "", sizeof(install_root) - 1u);
    install_root[sizeof(install_root) - 1u] = '\0';
    state_path[0] = '\0';

    if (args.non_interactive || args.use_defaults || !dsu_macos_tui_is_tty()) {
        dsu_manifest_install_scope_t scope = dsu__scope_from_str(args.scope, DSU_MANIFEST_INSTALL_SCOPE_USER);
        if ((!args.install_root || !args.install_root[0]) &&
            dsu__find_manifest_install_root(manifest, scope, platform_buf, install_root, sizeof(install_root))) {
            args.install_root = install_root;
        }
        if ((!args.state_path || !args.state_path[0]) && dsu__operation_needs_state(args.operation)) {
            dsu_manifest_install_scope_t detected_scope = 0;
            if (dsu__detect_installed_state(manifest, platform_buf, state_path, sizeof(state_path), &detected_scope)) {
                args.state_path = state_path;
            }
        }
        paths.manifest_path = manifest_path;
        paths.core_exe_path = dsu__resolve_core_path(argv[0], core_path, sizeof(core_path));
        paths.adapter_exe_path = dsu__resolve_exe_path(argv[0], "dominium-setup-macos", adapter_path, sizeof(adapter_path));
        exit_code = dsu__run_non_interactive(&args, &paths, platform_buf, manifest_path);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return exit_code;
    }

    dsu_macos_tui_clear();
    fprintf(stdout, "%s %s\n", DSU_MACOS_TUI_NAME, DSU_MACOS_TUI_VERSION);

    if (dsu__detect_installed_state(manifest, platform_buf, state_path, sizeof(state_path), &ui.scope)) {
        ui.installed_detected = 1;
        fprintf(stdout, "Existing installation detected (%s).\n", state_path);
    } else {
        ui.installed_detected = 0;
        fprintf(stdout, "No existing installation detected.\n");
    }

    {
        const char *ops_fresh[] = {"Install", "Upgrade", "Repair", "Uninstall"};
        int op_choice = dsu__prompt_menu("Select operation", ops_fresh, 4, ui.installed_detected ? 1 : 0);
        switch (op_choice) {
            case 1: ui.operation = (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE; break;
            case 2: ui.operation = (dsu_u8)DSU_INVOCATION_OPERATION_REPAIR; break;
            case 3: ui.operation = (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL; break;
            default: ui.operation = (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL; break;
        }
    }

    {
        const char *modes[] = {"Quick Install", "Custom Install"};
        int mode_choice = dsu__prompt_menu("Select install mode", modes, 2, 0);
        ui.install_mode = (mode_choice == 1) ? DSU_MACOS_UI_INSTALL_MODE_CUSTOM : DSU_MACOS_UI_INSTALL_MODE_QUICK;
    }

    if (ui.install_mode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
        const char *scopes[] = {"User", "System", "Portable"};
        int scope_choice = dsu__prompt_menu("Select scope", scopes, 3, 0);
        if (scope_choice == 1) {
            ui.scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
        } else if (scope_choice == 2) {
            ui.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        } else {
            ui.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
        }
    } else if (ui.scope == 0) {
        ui.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    }

    if (!dsu__find_manifest_install_root(manifest, ui.scope, platform_buf, install_root, sizeof(install_root))) {
        dsu_macos_log_error("manifest missing install root for platform %s", platform_buf);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return 1;
    }

    if (ui.install_mode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
        char prompt[600];
        snprintf(prompt, sizeof(prompt), "Install path [%s]: ", install_root);
        fprintf(stdout, "%s", prompt);
        dsu_macos_tui_flush();
        if (dsu_macos_tui_read_line(prompt, sizeof(prompt))) {
            dsu_macos_tui_trim(prompt);
            if (prompt[0] != '\0') {
                strncpy(install_root, prompt, sizeof(install_root) - 1u);
                install_root[sizeof(install_root) - 1u] = '\0';
            }
        }
    }

    if (ui.install_mode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
        if (!dsu__select_components(manifest, &ui.selected_components, &ui.selected_count)) {
            dsu_macos_log_error("component selection failed");
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }
        ui.enable_shortcuts = dsu__prompt_yes_no("Enable shortcuts?", 1);
        ui.enable_file_assoc = dsu__prompt_yes_no("Enable file associations?", 0);
        ui.enable_url_handlers = dsu__prompt_yes_no("Enable URL handlers?", 0);
    }

    {
        char *components_csv = NULL;
        dsu_macos_cli_args_t call_args;
        dsu_invocation_t inv;
        dsu_u64 digest = 0u;
        char inv_path[512];
        char plan_path[512];
        const char *out_inv;
        const char *out_plan;

        memset(&call_args, 0, sizeof(call_args));
        call_args.deterministic = 1;
        call_args.platform = platform_buf;
        call_args.ui_mode = "tui";
        call_args.frontend_id = "tui-macos";
        call_args.scope = (ui.scope == DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) ? "system" :
                          (ui.scope == DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) ? "portable" : "user";
        call_args.operation = (ui.operation == DSU_INVOCATION_OPERATION_UPGRADE) ? "upgrade" :
                              (ui.operation == DSU_INVOCATION_OPERATION_REPAIR) ? "repair" :
                              (ui.operation == DSU_INVOCATION_OPERATION_UNINSTALL) ? "uninstall" : "install";
        call_args.install_root = install_root;

        if (ui.selected_components && ui.selected_count) {
            components_csv = dsu__csv_from_list(ui.selected_components, ui.selected_count);
            call_args.components_csv = components_csv;
        }
        call_args.policy_shortcuts = ui.enable_shortcuts ? 1 : 0;
        call_args.policy_file_assoc = ui.enable_file_assoc ? 1 : 0;
        call_args.policy_url_handlers = ui.enable_url_handlers ? 1 : 0;

        dsu_invocation_init(&inv);
        if (!dsu_macos_build_invocation(&call_args, platform_buf, "tui", "tui-macos", &inv)) {
            dsu_macos_log_error("failed to build invocation");
            free(components_csv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }

        out_inv = args.out_path ? args.out_path : args.invocation_path;
        if (!out_inv || !out_inv[0]) {
            out_inv = dsu__default_temp_path("dominium-invocation.tlv", inv_path, sizeof(inv_path));
        }
        if (!dsu_macos_write_invocation(&inv, out_inv, &digest)) {
            dsu_macos_log_error("failed to write invocation");
            free(components_csv);
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }

        fprintf(stdout, "\nSummary\n");
        fprintf(stdout, "  Operation: %s\n", call_args.operation);
        fprintf(stdout, "  Scope: %s\n", call_args.scope);
        fprintf(stdout, "  Install root: %s\n", install_root);
        fprintf(stdout, "  Invocation: %s\n", out_inv);
        fprintf(stdout, "  Digest64: 0x%016llx\n", (unsigned long long)digest);
        fprintf(stdout, "  CLI: dominium-setup export-invocation --manifest \"%s\" --op %s --scope %s --platform %s --install-root \"%s\" --ui-mode tui --frontend-id tui-macos --out \"%s\" --deterministic 1",
                manifest_path,
                call_args.operation,
                call_args.scope,
                platform_buf,
                install_root,
                out_inv);
        if (components_csv && components_csv[0]) {
            fprintf(stdout, " --components \"%s\"", components_csv);
        }
        if (ui.enable_shortcuts) {
            fprintf(stdout, " --shortcuts");
        }
        if (ui.enable_file_assoc) {
            fprintf(stdout, " --file-assoc");
        }
        if (ui.enable_url_handlers) {
            fprintf(stdout, " --url-handlers");
        }
        fprintf(stdout, "\n");

        if (!dsu__prompt_yes_no("Proceed?", 1)) {
            free(components_csv);
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 0;
        }

        paths.manifest_path = manifest_path;
        paths.core_exe_path = dsu__resolve_core_path(argv[0], core_path, sizeof(core_path));
        paths.adapter_exe_path = dsu__resolve_exe_path(argv[0], "dominium-setup-macos", adapter_path, sizeof(adapter_path));

        out_plan = args.plan_path;
        if (!out_plan || !out_plan[0]) {
            out_plan = dsu__default_temp_path("dominium-plan.tlv", plan_path, sizeof(plan_path));
        }

        {
            const char *plan_state = NULL;
            if (args.state_path && args.state_path[0]) {
                plan_state = args.state_path;
            } else if (ui.operation != DSU_INVOCATION_OPERATION_INSTALL && state_path[0] != '\0') {
                plan_state = state_path;
            }
            if (dsu_macos_bridge_plan(&paths, out_inv, out_plan, plan_state, 1, 0, 0) != 0) {
                dsu_macos_log_error("plan failed");
                free(components_csv);
                dsu_invocation_destroy(NULL, &inv);
                dsu_manifest_destroy(ctx, manifest);
                dsu_ctx_destroy(ctx);
                return 1;
            }
        }

        if (dsu_macos_bridge_apply_plan(&paths, out_plan, 1, 0, 0, 0) != 0) {
            dsu_macos_log_error("apply failed");
            free(components_csv);
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }

        dsu__build_state_path(install_root, state_path, sizeof(state_path));
        if (ui.operation == DSU_INVOCATION_OPERATION_UNINSTALL) {
            (void)dsu__run_platform_unregister(&paths, state_path, 1, 0);
        } else {
            (void)dsu__run_platform_register(&paths, state_path, 1, 0);
        }

        free(components_csv);
        dsu_invocation_destroy(NULL, &inv);
    }

    fprintf(stdout, "\nDone.\n");
    if (ui.selected_components) {
        dsu__list_free(ui.selected_components, ui.selected_count);
        ui.selected_components = NULL;
        ui.selected_count = 0u;
    }
    dsu_manifest_destroy(ctx, manifest);
    dsu_ctx_destroy(ctx);
    exit_code = 0;
    return exit_code;
}
