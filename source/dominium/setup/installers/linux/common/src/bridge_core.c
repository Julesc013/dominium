/*
FILE: source/dominium/setup/installers/linux/common/src/bridge_core.c
MODULE: Dominium Setup Linux
PURPOSE: Bridge to Setup Core CLI from Linux frontends.
*/
#include "dsu_linux_bridge.h"
#include "dsu_linux_log.h"

#include <stdlib.h>
#include <string.h>

typedef struct dsu__str_builder_t {
    char *buf;
    size_t len;
    size_t cap;
} dsu__str_builder_t;

static int dsu__sb_reserve(dsu__str_builder_t *sb, size_t add) {
    size_t need;
    char *next;
    if (!sb) return 0;
    need = sb->len + add + 1u;
    if (need <= sb->cap) return 1;
    if (sb->cap == 0u) sb->cap = 128u;
    while (sb->cap < need) sb->cap *= 2u;
    next = (char *)realloc(sb->buf, sb->cap);
    if (!next) return 0;
    sb->buf = next;
    return 1;
}

static int dsu__sb_append(dsu__str_builder_t *sb, const char *s) {
    size_t n;
    if (!sb || !s) return 0;
    n = strlen(s);
    if (!dsu__sb_reserve(sb, n)) return 0;
    memcpy(sb->buf + sb->len, s, n);
    sb->len += n;
    sb->buf[sb->len] = '\0';
    return 1;
}

static int dsu__sb_append_ch(dsu__str_builder_t *sb, char c) {
    if (!sb) return 0;
    if (!dsu__sb_reserve(sb, 1u)) return 0;
    sb->buf[sb->len++] = c;
    sb->buf[sb->len] = '\0';
    return 1;
}

static char *dsu__dup(const char *s) {
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

static char *dsu__quote_arg(const char *s) {
    const char *p;
    size_t extra = 0u;
    size_t len;
    char *out;
    size_t idx = 0u;
    int needs = 0;
    if (!s) return NULL;
    for (p = s; *p; ++p) {
        if (*p == ' ' || *p == '\t') {
            needs = 1;
        }
        if (*p == '"') {
            needs = 1;
            extra += 1u;
        }
    }
    if (!needs) {
        return dsu__dup(s);
    }
    len = strlen(s);
    out = (char *)malloc(len + extra + 3u);
    if (!out) return NULL;
    out[idx++] = '"';
    for (p = s; *p; ++p) {
        if (*p == '"') {
            out[idx++] = '\\';
        }
        out[idx++] = *p;
    }
    out[idx++] = '"';
    out[idx] = '\0';
    return out;
}

static char *dsu__build_cmd(const char *exe_path,
                            const char *subcommand,
                            const char *args,
                            int deterministic,
                            int quiet) {
    dsu__str_builder_t sb;
    char *exe_q;

    memset(&sb, 0, sizeof(sb));
    exe_q = dsu__quote_arg(exe_path ? exe_path : "");
    if (!exe_q) return NULL;

    if (!dsu__sb_append(&sb, exe_q)) {
        free(exe_q);
        free(sb.buf);
        return NULL;
    }
    free(exe_q);
    if (subcommand && subcommand[0]) {
        if (!dsu__sb_append_ch(&sb, ' ') || !dsu__sb_append(&sb, subcommand)) {
            free(sb.buf);
            return NULL;
        }
    }
    if (args && args[0]) {
        if (!dsu__sb_append_ch(&sb, ' ') || !dsu__sb_append(&sb, args)) {
            free(sb.buf);
            return NULL;
        }
    }
    if (deterministic >= 0) {
        if (!dsu__sb_append(&sb, " --deterministic ") ||
            !dsu__sb_append(&sb, deterministic ? "1" : "0")) {
            free(sb.buf);
            return NULL;
        }
    }
    if (quiet) {
        if (!dsu__sb_append(&sb, " --quiet")) {
            free(sb.buf);
            return NULL;
        }
    }
    return sb.buf;
}

int dsu_linux_bridge_spawn(const char *cmdline, int quiet) {
    int exit_code = -1;
    (void)quiet;
    if (cmdline && cmdline[0]) {
        exit_code = system(cmdline);
    }
    return exit_code;
}

int dsu_linux_bridge_export_invocation(const dsu_linux_bridge_paths_t *paths,
                                       const char *args,
                                       int deterministic,
                                       int quiet,
                                       int format_json) {
    char *cmd;
    dsu__str_builder_t sb;
    int code;
    if (!paths || !paths->core_exe_path) {
        return -1;
    }
    cmd = dsu__build_cmd(paths->core_exe_path, "export-invocation", args, deterministic, quiet);
    if (!cmd) {
        return -1;
    }
    if (format_json) {
        memset(&sb, 0, sizeof(sb));
        if (!dsu__sb_append(&sb, cmd) || !dsu__sb_append(&sb, " --json")) {
            free(cmd);
            free(sb.buf);
            return -1;
        }
        code = dsu_linux_bridge_spawn(sb.buf, quiet);
        free(sb.buf);
        free(cmd);
        return code;
    }
    code = dsu_linux_bridge_spawn(cmd, quiet);
    free(cmd);
    return code;
}

int dsu_linux_bridge_plan(const dsu_linux_bridge_paths_t *paths,
                          const char *invocation_path,
                          const char *plan_path,
                          const char *state_path,
                          int deterministic,
                          int quiet,
                          int format_json) {
    char *inv_q = NULL;
    char *plan_q = NULL;
    char *man_q = NULL;
    char *state_q = NULL;
    dsu__str_builder_t sb;
    char *cmd = NULL;
    int code;

    if (!paths || !paths->core_exe_path || !paths->manifest_path || !invocation_path || !plan_path) {
        return -1;
    }
    memset(&sb, 0, sizeof(sb));
    inv_q = dsu__quote_arg(invocation_path);
    plan_q = dsu__quote_arg(plan_path);
    man_q = dsu__quote_arg(paths->manifest_path);
    if (!inv_q || !plan_q || !man_q) {
        free(inv_q);
        free(plan_q);
        free(man_q);
        return -1;
    }
    if (state_path && state_path[0]) {
        state_q = dsu__quote_arg(state_path);
        if (!state_q) {
            free(inv_q);
            free(plan_q);
            free(man_q);
            return -1;
        }
    }

    cmd = dsu__build_cmd(paths->core_exe_path, "plan", NULL, deterministic, quiet);
    if (!cmd) {
        free(inv_q);
        free(plan_q);
        free(man_q);
        free(state_q);
        return -1;
    }
    if (!dsu__sb_append(&sb, cmd) ||
        !dsu__sb_append(&sb, " --manifest ") ||
        !dsu__sb_append(&sb, man_q) ||
        (state_q && (!dsu__sb_append(&sb, " --state ") || !dsu__sb_append(&sb, state_q))) ||
        !dsu__sb_append(&sb, " --invocation ") ||
        !dsu__sb_append(&sb, inv_q) ||
        !dsu__sb_append(&sb, " --out ") ||
        !dsu__sb_append(&sb, plan_q)) {
        free(inv_q);
        free(plan_q);
        free(man_q);
        free(state_q);
        free(cmd);
        free(sb.buf);
        return -1;
    }
    free(inv_q);
    free(plan_q);
    free(man_q);
    free(state_q);
    free(cmd);
    if (format_json) {
        if (!dsu__sb_append(&sb, " --json")) {
            free(sb.buf);
            return -1;
        }
    }
    code = dsu_linux_bridge_spawn(sb.buf, quiet);
    free(sb.buf);
    return code;
}

int dsu_linux_bridge_apply_plan(const dsu_linux_bridge_paths_t *paths,
                                const char *plan_path,
                                int deterministic,
                                int dry_run,
                                int quiet,
                                int format_json) {
    char *plan_q = NULL;
    dsu__str_builder_t sb;
    char *cmd = NULL;
    int code;

    if (!paths || !paths->core_exe_path || !plan_path) {
        return -1;
    }
    memset(&sb, 0, sizeof(sb));
    plan_q = dsu__quote_arg(plan_path);
    if (!plan_q) return -1;

    cmd = dsu__build_cmd(paths->core_exe_path, "apply", NULL, deterministic, quiet);
    if (!cmd) {
        free(plan_q);
        return -1;
    }
    if (!dsu__sb_append(&sb, cmd) ||
        !dsu__sb_append(&sb, " --plan ") ||
        !dsu__sb_append(&sb, plan_q)) {
        free(plan_q);
        free(cmd);
        free(sb.buf);
        return -1;
    }
    free(plan_q);
    free(cmd);
    if (dry_run) {
        if (!dsu__sb_append(&sb, " --dry-run")) {
            free(sb.buf);
            return -1;
        }
    }
    if (format_json) {
        if (!dsu__sb_append(&sb, " --json")) {
            free(sb.buf);
            return -1;
        }
    }
    code = dsu_linux_bridge_spawn(sb.buf, quiet);
    free(sb.buf);
    return code;
}

int dsu_linux_bridge_apply_invocation(const dsu_linux_bridge_paths_t *paths,
                                      const char *invocation_path,
                                      int deterministic,
                                      int dry_run,
                                      int quiet,
                                      int format_json) {
    char *inv_q = NULL;
    dsu__str_builder_t sb;
    char *cmd = NULL;
    int code;

    if (!paths || !paths->core_exe_path || !invocation_path) {
        return -1;
    }
    memset(&sb, 0, sizeof(sb));
    inv_q = dsu__quote_arg(invocation_path);
    if (!inv_q) return -1;

    cmd = dsu__build_cmd(paths->core_exe_path, "apply", NULL, deterministic, quiet);
    if (!cmd) {
        free(inv_q);
        return -1;
    }
    if (!dsu__sb_append(&sb, cmd) ||
        !dsu__sb_append(&sb, " --invocation ") ||
        !dsu__sb_append(&sb, inv_q)) {
        free(inv_q);
        free(cmd);
        free(sb.buf);
        return -1;
    }
    free(inv_q);
    free(cmd);
    if (dry_run) {
        if (!dsu__sb_append(&sb, " --dry-run")) {
            free(sb.buf);
            return -1;
        }
    }
    if (format_json) {
        if (!dsu__sb_append(&sb, " --json")) {
            free(sb.buf);
            return -1;
        }
    }
    code = dsu_linux_bridge_spawn(sb.buf, quiet);
    free(sb.buf);
    return code;
}
