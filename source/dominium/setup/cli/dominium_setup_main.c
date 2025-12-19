/*
FILE: source/dominium/setup/cli/dominium_setup_main.c
MODULE: Dominium Setup
PURPOSE: Minimal setup control-plane CLI for Plan S-1 (plan + dry-run).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#include <fcntl.h>
#include <io.h>
#else
#include <sys/stat.h>
#endif

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_execute.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_platform_iface.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_report.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_state.h"
#include "dsu/dsu_txn.h"

#define DSU_CLI_NAME "dominium-setup"
#define DSU_CLI_VERSION "1.0.0"
#define DSU_CLI_JSON_SCHEMA_VERSION 1u

typedef struct dsu_cli_opts_t {
    int deterministic;
    int quiet;
    int format_json;
    int dry_run;
} dsu_cli_opts_t;

static const char *dsu_cli_status_name(dsu_status_t st) {
    switch (st) {
        case DSU_STATUS_SUCCESS: return "success";
        case DSU_STATUS_INVALID_ARGS: return "invalid_args";
        case DSU_STATUS_IO_ERROR: return "io_error";
        case DSU_STATUS_PARSE_ERROR: return "parse_error";
        case DSU_STATUS_UNSUPPORTED_VERSION: return "unsupported_version";
        case DSU_STATUS_INTEGRITY_ERROR: return "integrity_error";
        case DSU_STATUS_INTERNAL_ERROR: return "internal_error";
        case DSU_STATUS_MISSING_COMPONENT: return "missing_component";
        case DSU_STATUS_UNSATISFIED_DEPENDENCY: return "unsatisfied_dependency";
        case DSU_STATUS_VERSION_CONFLICT: return "version_conflict";
        case DSU_STATUS_EXPLICIT_CONFLICT: return "explicit_conflict";
        case DSU_STATUS_PLATFORM_INCOMPATIBLE: return "platform_incompatible";
        case DSU_STATUS_ILLEGAL_DOWNGRADE: return "illegal_downgrade";
        case DSU_STATUS_INVALID_REQUEST: return "invalid_request";
        default: return "unknown";
    }
}

static int dsu_cli_exit_code(dsu_status_t st) {
    switch (st) {
        case DSU_STATUS_SUCCESS: return 0;
        case DSU_STATUS_INTEGRITY_ERROR: return 2; /* verification / integrity issues */
        case DSU_STATUS_INVALID_ARGS:
        case DSU_STATUS_PARSE_ERROR:
        case DSU_STATUS_INVALID_REQUEST:
        case DSU_STATUS_MISSING_COMPONENT:
        case DSU_STATUS_UNSATISFIED_DEPENDENCY:
        case DSU_STATUS_VERSION_CONFLICT:
        case DSU_STATUS_EXPLICIT_CONFLICT:
        case DSU_STATUS_ILLEGAL_DOWNGRADE:
            return 3; /* invalid input/state */
        case DSU_STATUS_UNSUPPORTED_VERSION:
        case DSU_STATUS_PLATFORM_INCOMPATIBLE:
            return 4; /* unsupported operation */
        default:
            return 1; /* generic failure */
    }
}

static void dsu_cli_json_put_escaped(FILE *out, const char *s) {
    const unsigned char *p = (const unsigned char *)(s ? s : "");
    unsigned char c;
    fputc('"', out);
    while ((c = *p++) != 0u) {
        if (c == '\\' || c == '"') {
            fputc('\\', out);
            fputc((int)c, out);
        } else if (c == '\b') {
            fputs("\\b", out);
        } else if (c == '\f') {
            fputs("\\f", out);
        } else if (c == '\n') {
            fputs("\\n", out);
        } else if (c == '\r') {
            fputs("\\r", out);
        } else if (c == '\t') {
            fputs("\\t", out);
        } else if (c < 0x20u) {
            static const char hex[] = "0123456789abcdef";
            fputs("\\u00", out);
            fputc(hex[(c >> 4) & 0xFu], out);
            fputc(hex[c & 0xFu], out);
        } else {
            fputc((int)c, out);
        }
    }
    fputc('"', out);
}

static void dsu_cli_json_put_path(FILE *out, const char *path) {
    const unsigned char *p = (const unsigned char *)(path ? path : "");
    unsigned char c;
    fputc('"', out);
    while ((c = *p++) != 0u) {
        if (c == '\\') c = '/';
        if (c == '\\' || c == '"') {
            fputc('\\', out);
            fputc((int)c, out);
        } else if (c == '\b') {
            fputs("\\b", out);
        } else if (c == '\f') {
            fputs("\\f", out);
        } else if (c == '\n') {
            fputs("\\n", out);
        } else if (c == '\r') {
            fputs("\\r", out);
        } else if (c == '\t') {
            fputs("\\t", out);
        } else if (c < 0x20u) {
            static const char hex[] = "0123456789abcdef";
            fputs("\\u00", out);
            fputc(hex[(c >> 4) & 0xFu], out);
            fputc(hex[c & 0xFu], out);
        } else {
            fputc((int)c, out);
        }
    }
    fputc('"', out);
}

static void dsu_cli_json_put_bool(FILE *out, int v) {
    fputs(v ? "true" : "false", out);
}

static const char *dsu_cli_result_status_string(int status_code) {
    switch (status_code) {
        case 0: return "ok";
        case 2: return "verification_failed";
        case 3: return "invalid_input";
        case 4: return "unsupported";
        case 5: return "partial_success";
        default: return "error";
    }
}

static void dsu_cli_json_begin_envelope(FILE *out, const char *command, int status_code) {
    if (!out) out = stdout;
    fputc('{', out);
    fputs("\"schema_version\":", out);
    fprintf(out, "%lu", (unsigned long)DSU_CLI_JSON_SCHEMA_VERSION);
    fputc(',', out);
    fputs("\"command\":", out);
    dsu_cli_json_put_escaped(out, command ? command : "");
    fputc(',', out);
    fputs("\"status\":", out);
    dsu_cli_json_put_escaped(out, dsu_cli_result_status_string(status_code));
    fputc(',', out);
    fputs("\"status_code\":", out);
    fprintf(out, "%d", status_code);
    fputc(',', out);
    fputs("\"details\":{", out);
}

static void dsu_cli_json_end_envelope(FILE *out) {
    if (!out) out = stdout;
    fputs("}}\n", out);
}

static void dsu_cli_json_error_envelope(const char *command, int status_code, dsu_status_t core_status, const char *error_code) {
    dsu_cli_json_begin_envelope(stdout, command ? command : "", status_code);
    fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)core_status); fputc(',', stdout);
    fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(core_status)); fputc(',', stdout);
    fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, error_code ? error_code : dsu_cli_status_name(core_status));
    dsu_cli_json_end_envelope(stdout);
}

static int dsu_cli_streq(const char *a, const char *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    return strcmp(a, b) == 0;
}

static const char *dsu_cli_kv_value_inline(const char *arg, const char *key) {
    size_t n;
    if (!arg || !key) return NULL;
    n = strlen(key);
    if (strncmp(arg, key, n) != 0) return NULL;
    if (arg[n] != '=') return NULL;
    return arg + n + 1;
}

static void dsu_cli_print_help_root(FILE *out) {
    fprintf(out,
            "%s %s\n"
            "\n"
            "Usage:\n"
            "  %s help [command]\n"
            "  %s version\n"
            "  %s manifest validate --in <file>\n"
            "  %s manifest dump --in <file> [--out <file>] [--format json]\n"
            "  %s resolve --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall>\n"
            "               [--components <csv>] [--exclude <csv>] [--scope <portable|user|system>]\n"
            "  %s plan --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall>\n"
            "            [--components <csv>] [--exclude <csv>] [--scope <portable|user|system>] --out <planfile>\n"
            "  %s apply --plan <planfile> [--dry-run]\n"
            "  %s verify --state <file> [--format json|txt]\n"
            "  %s list --state <file> [--format json|txt]\n"
            "  %s report --state <file> --out <dir> [--format json|txt]\n"
            "  %s uninstall-preview --state <file> [--components <csv>] [--format json|txt]\n"
            "  %s rollback --journal <file> [--dry-run]\n"
            "  %s export-log --log <file> --out <file> --format json|txt\n"
            "\n"
            "Global flags:\n"
            "  --deterministic <0|1>   Default: 1\n"
            "  --quiet                 Suppress non-essential text\n"
            "  --json                  Shorthand for --format json\n",
            DSU_CLI_NAME, DSU_CLI_VERSION,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME,
            DSU_CLI_NAME);
}

static void dsu_cli_print_help_command(FILE *out, int argc, char **argv) {
    const char *a = (argc > 0) ? argv[0] : NULL;
    const char *b = (argc > 1) ? argv[1] : NULL;

    if (!a || a[0] == '\0') {
        dsu_cli_print_help_root(out);
        return;
    }

    if (dsu_cli_streq(a, "manifest") && (!b || b[0] == '\0')) {
        fprintf(out,
                "Usage:\n"
                "  %s manifest validate --in <file>\n"
                "  %s manifest dump --in <file> [--out <file>] [--format json]\n",
                DSU_CLI_NAME, DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "manifest") && dsu_cli_streq(b, "validate")) {
        fprintf(out,
                "Usage:\n"
                "  %s manifest validate --in <file>\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "manifest") && dsu_cli_streq(b, "dump")) {
        fprintf(out,
                "Usage:\n"
                "  %s manifest dump --in <file> [--out <file>] [--format json]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "version")) {
        fprintf(out,
                "Usage:\n"
                "  %s version\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "resolve")) {
        fprintf(out,
                "Usage:\n"
                "  %s resolve --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall>\n"
                "               [--components <csv>] [--exclude <csv>] [--scope <portable|user|system>]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "plan")) {
        fprintf(out,
                "Usage:\n"
                "  %s plan --manifest <file> [--state <file>] --op <install|upgrade|repair|uninstall>\n"
                "            [--components <csv>] [--exclude <csv>] [--scope <portable|user|system>] --out <planfile>\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "apply")) {
        fprintf(out,
                "Usage:\n"
                "  %s apply --plan <planfile> [--dry-run]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "verify")) {
        fprintf(out,
                "Usage:\n"
                "  %s verify --state <file> [--format json|txt]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "list")) {
        fprintf(out,
                "Usage:\n"
                "  %s list --state <file> [--format json|txt]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "report")) {
        fprintf(out,
                "Usage:\n"
                "  %s report --state <file> --out <dir> [--format json|txt]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "uninstall-preview")) {
        fprintf(out,
                "Usage:\n"
                "  %s uninstall-preview --state <file> [--components <csv>] [--format json|txt]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "rollback")) {
        fprintf(out,
                "Usage:\n"
                "  %s rollback --journal <file> [--dry-run]\n",
                DSU_CLI_NAME);
        return;
    }

    if (dsu_cli_streq(a, "export-log")) {
        fprintf(out,
                "Usage:\n"
                "  %s export-log --log <file> --out <file> --format json|txt\n",
                DSU_CLI_NAME);
        return;
    }

    dsu_cli_print_help_root(out);
}

static dsu_status_t dsu_cli_ctx_create(const dsu_cli_opts_t *opts, dsu_ctx_t **out_ctx) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_u32 flags;

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);

    flags = cfg.flags;
    if (!opts || !opts->deterministic) {
        flags &= ~DSU_CONFIG_FLAG_DETERMINISTIC;
    } else {
        flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    }
    cfg.flags = flags;

    return dsu_ctx_create(&cfg, &cbs, NULL, out_ctx);
}

static void dsu_cli_json_put_u64_hex(FILE *out, dsu_u64 v);
static const char *dsu_cli_scope_name(dsu_manifest_install_scope_t scope);
static const char *dsu_cli_operation_name(dsu_resolve_operation_t op);

static int dsu_cli_cmd_version(int argc, char **argv, const dsu_cli_opts_t *opts) {
    (void)argc;
    (void)argv;
    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, "version", 0);
        fputs("\"core_status\":0,", stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(DSU_STATUS_SUCCESS)); fputc(',', stdout);
        fputs("\"name\":", stdout); dsu_cli_json_put_escaped(stdout, DSU_CLI_NAME); fputc(',', stdout);
        fputs("\"version\":", stdout); dsu_cli_json_put_escaped(stdout, DSU_CLI_VERSION);
        dsu_cli_json_end_envelope(stdout);
    } else {
        fprintf(stdout, "%s %s\n", DSU_CLI_NAME, DSU_CLI_VERSION);
    }
    return 0;
}

static int dsu_cli_cmd_plan(const char *manifest_path,
                            const char *installed_state_path,
                            dsu_resolve_operation_t op,
                            int scope_set,
                            dsu_manifest_install_scope_t scope,
                            const char *const *requested_components,
                            dsu_u32 requested_component_count,
                            const char *const *excluded_components,
                            dsu_u32 excluded_component_count,
                            const char *out_plan_path,
                            const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_state_t *installed = NULL;
    dsu_resolve_result_t *resolved = NULL;
    dsu_plan_t *plan = NULL;
    dsu_status_t st;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_manifest_load_file(ctx, manifest_path, &manifest);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    if (installed_state_path) {
        st = dsu_state_load_file(ctx, installed_state_path, &installed);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
    }

    {
        dsu_resolve_request_t req;
        dsu_manifest_install_scope_t eff_scope = scope;

        dsu_resolve_request_init(&req);
        req.operation = op;
        if (op == DSU_RESOLVE_OPERATION_INSTALL || op == DSU_RESOLVE_OPERATION_UPGRADE) {
            if (!scope_set) {
                if (!dsu_cli_manifest_infer_single_scope(manifest, &eff_scope)) {
                    st = DSU_STATUS_INVALID_ARGS;
                    goto done;
                }
            }
        } else {
            if (!scope_set && installed) {
                eff_scope = dsu_state_install_scope(installed);
            } else if (!scope_set) {
                (void)dsu_cli_manifest_infer_single_scope(manifest, &eff_scope);
            }
        }
        if (installed && scope_set && dsu_state_install_scope(installed) != eff_scope) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        req.scope = eff_scope;
        req.allow_prerelease = DSU_FALSE;
        req.target_platform = NULL;
        req.requested_components = (requested_component_count != 0u) ? requested_components : NULL;
        req.requested_component_count = requested_component_count;
        req.excluded_components = (excluded_component_count != 0u) ? excluded_components : NULL;
        req.excluded_component_count = excluded_component_count;
        req.pins = NULL;
        req.pin_count = 0u;

        st = dsu_resolve_components(ctx, manifest, installed, &req, &resolved);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
    }
    st = dsu_plan_build(ctx, manifest, manifest_path, resolved, &plan);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_plan_validate(plan);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_plan_write_file(ctx, plan, out_plan_path);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, "plan", 0);
        fputs("\"core_status\":0,", stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(DSU_STATUS_SUCCESS)); fputc(',', stdout);
        fputs("\"deterministic\":", stdout); dsu_cli_json_put_bool(stdout, opts->deterministic); fputc(',', stdout);
        fputs("\"operation\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_operation_name(dsu_plan_operation(plan))); fputc(',', stdout);
        fputs("\"scope\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_scope_name(dsu_plan_scope(plan))); fputc(',', stdout);
        fputs("\"platform\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_plan_platform(plan)); fputc(',', stdout);
        fputs("\"manifest_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_plan_manifest_digest64(plan)); fputc(',', stdout);
        fputs("\"resolved_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_plan_resolved_set_digest64(plan)); fputc(',', stdout);
        fputs("\"plan_file\":", stdout); dsu_cli_json_put_path(stdout, out_plan_path); fputc(',', stdout);
        fprintf(stdout, "\"plan_id_hash32\":%lu,", (unsigned long)dsu_plan_id_hash32(plan));
        fputs("\"plan_id_hash64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_plan_id_hash64(plan)); fputc(',', stdout);
        fprintf(stdout, "\"component_count\":%lu,", (unsigned long)dsu_plan_component_count(plan));
        fprintf(stdout, "\"step_count\":%lu,", (unsigned long)dsu_plan_step_count(plan));
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        dsu_cli_json_end_envelope(stdout);
    } else {
        fprintf(stdout, "plan_id_hash32=%lu\n", (unsigned long)dsu_plan_id_hash32(plan));
        {
            dsu_u64 id64 = dsu_plan_id_hash64(plan);
            unsigned long hi = (unsigned long)((id64 >> 32) & 0xFFFFFFFFu);
            unsigned long lo = (unsigned long)(id64 & 0xFFFFFFFFu);
            fprintf(stdout, "plan_id_hash64=0x%08lx%08lx\n", hi, lo);
        }
        fprintf(stdout, "components=%lu\n", (unsigned long)dsu_plan_component_count(plan));
        fprintf(stdout, "steps=%lu\n", (unsigned long)dsu_plan_step_count(plan));
        fprintf(stdout, "plan_file=%s\n", out_plan_path);
    }

done:
    if (plan) dsu_plan_destroy(ctx, plan);
    if (resolved) dsu_resolve_result_destroy(ctx, resolved);
    if (installed) dsu_state_destroy(ctx, installed);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);

    if (st != DSU_STATUS_SUCCESS) {
        if (opts && opts->format_json) {
            int code = dsu_cli_exit_code(st);
            dsu_cli_json_begin_envelope(stdout, "plan", code);
            fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
            fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
            dsu_cli_json_end_envelope(stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }
    return dsu_cli_exit_code(st);
}

static void dsu_cli_json_put_u64_hex(FILE *out, dsu_u64 v) {
    unsigned long hi = (unsigned long)((v >> 32) & 0xFFFFFFFFu);
    unsigned long lo = (unsigned long)(v & 0xFFFFFFFFu);
    fputc('"', out);
    fprintf(out, "0x%08lx%08lx", hi, lo);
    fputc('"', out);
}

static const char *dsu_cli_scope_name(dsu_manifest_install_scope_t scope) {
    switch (scope) {
        case DSU_MANIFEST_INSTALL_SCOPE_PORTABLE: return "portable";
        case DSU_MANIFEST_INSTALL_SCOPE_USER: return "user";
        case DSU_MANIFEST_INSTALL_SCOPE_SYSTEM: return "system";
        default: return "unknown";
    }
}

static int dsu_cli_parse_scope(const char *s, dsu_manifest_install_scope_t *out_scope) {
    if (!out_scope) return 0;
    *out_scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    if (!s) return 0;
    if (dsu_cli_streq(s, "portable")) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        return 1;
    }
    if (dsu_cli_streq(s, "user")) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
        return 1;
    }
    if (dsu_cli_streq(s, "system")) {
        *out_scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
        return 1;
    }
    return 0;
}

static int dsu_cli_manifest_infer_single_scope(const dsu_manifest_t *manifest, dsu_manifest_install_scope_t *out_scope) {
    int seen_portable = 0;
    int seen_user = 0;
    int seen_system = 0;
    int count = 0;
    dsu_u32 i;

    if (!out_scope) return 0;
    *out_scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    if (!manifest) return 0;

    for (i = 0u; i < dsu_manifest_install_root_count(manifest); ++i) {
        dsu_manifest_install_scope_t s = dsu_manifest_install_root_scope(manifest, i);
        if (s == DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) {
            if (!seen_portable) {
                seen_portable = 1;
                ++count;
                *out_scope = s;
            }
        } else if (s == DSU_MANIFEST_INSTALL_SCOPE_USER) {
            if (!seen_user) {
                seen_user = 1;
                ++count;
                *out_scope = s;
            }
        } else if (s == DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
            if (!seen_system) {
                seen_system = 1;
                ++count;
                *out_scope = s;
            }
        } else {
            return 0;
        }
    }

    return count == 1;
}

static const char *dsu_cli_operation_name(dsu_resolve_operation_t op) {
    switch (op) {
        case DSU_RESOLVE_OPERATION_INSTALL: return "install";
        case DSU_RESOLVE_OPERATION_UPGRADE: return "upgrade";
        case DSU_RESOLVE_OPERATION_REPAIR: return "repair";
        case DSU_RESOLVE_OPERATION_UNINSTALL: return "uninstall";
        default: return "unknown";
    }
}

static const char *dsu_cli_source_name(dsu_resolve_source_t s) {
    switch (s) {
        case DSU_RESOLVE_SOURCE_DEFAULT: return "default";
        case DSU_RESOLVE_SOURCE_USER: return "user";
        case DSU_RESOLVE_SOURCE_DEPENDENCY: return "dependency";
        case DSU_RESOLVE_SOURCE_INSTALLED: return "installed";
        default: return "unknown";
    }
}

static const char *dsu_cli_action_name(dsu_resolve_component_action_t a) {
    switch (a) {
        case DSU_RESOLVE_COMPONENT_ACTION_NONE: return "none";
        case DSU_RESOLVE_COMPONENT_ACTION_INSTALL: return "install";
        case DSU_RESOLVE_COMPONENT_ACTION_UPGRADE: return "upgrade";
        case DSU_RESOLVE_COMPONENT_ACTION_REPAIR: return "repair";
        case DSU_RESOLVE_COMPONENT_ACTION_UNINSTALL: return "uninstall";
        default: return "unknown";
    }
}

typedef struct dsu_cli_csv_list_t {
    char *buf;
    const char **items;
    dsu_u32 count;
} dsu_cli_csv_list_t;

static void dsu_cli_csv_list_free(dsu_cli_csv_list_t *l) {
    if (!l) return;
    free(l->buf);
    free(l->items);
    l->buf = NULL;
    l->items = NULL;
    l->count = 0u;
}

static int dsu_cli_is_space(int c) {
    return (c == ' ' || c == '\t' || c == '\r' || c == '\n');
}

static int dsu_cli_csv_list_parse(const char *s, dsu_cli_csv_list_t *out) {
    unsigned long n;
    unsigned long i;
    unsigned long cap;
    char *buf;
    const char **items;
    unsigned long count;
    char *p;

    if (!out) return 0;
    out->buf = NULL;
    out->items = NULL;
    out->count = 0u;
    if (!s || s[0] == '\0') return 1;

    n = (unsigned long)strlen(s);
    buf = (char *)malloc((size_t)n + 1u);
    if (!buf) return 0;
    memcpy(buf, s, (size_t)n + 1u);

    count = 1ul;
    for (i = 0ul; i < n; ++i) {
        if (buf[i] == ',') {
            ++count;
        }
    }

    items = (const char **)malloc((size_t)count * sizeof(*items));
    if (!items) {
        free(buf);
        return 0;
    }
    cap = count;
    count = 0ul;

    p = buf;
    while (*p) {
        char *start = p;
        char *end;
        while (*p && *p != ',') {
            ++p;
        }
        if (*p == ',') {
            *p++ = '\0';
        }

        while (*start && dsu_cli_is_space((unsigned char)*start)) {
            ++start;
        }
        end = start + strlen(start);
        while (end > start && dsu_cli_is_space((unsigned char)end[-1])) {
            end[-1] = '\0';
            --end;
        }
        if (start[0] == '\0') {
            free(buf);
            free(items);
            return 0;
        }
        if (count < cap) {
            items[count++] = start;
        }
    }

    out->buf = buf;
    out->items = items;
    out->count = (dsu_u32)count;
    return 1;
}

static int dsu_cli_cmd_resolve(const char *manifest_path,
                               const char *installed_state_path,
                               dsu_resolve_operation_t op,
                               const dsu_cli_csv_list_t *components,
                               const dsu_cli_csv_list_t *exclude,
                               int scope_set,
                               dsu_manifest_install_scope_t scope,
                               const char *platform,
                               int allow_prerelease,
                               const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_state_t *installed = NULL;
    dsu_resolve_result_t *result = NULL;
    dsu_resolve_request_t req;
    dsu_status_t st;
    dsu_u32 i;

    (void)opts;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_manifest_load_file(ctx, manifest_path, &manifest);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    if (installed_state_path) {
        st = dsu_state_load_file(ctx, installed_state_path, &installed);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
    }

    dsu_resolve_request_init(&req);
    req.operation = op;
    {
        dsu_manifest_install_scope_t eff_scope = scope;
        if (op == DSU_RESOLVE_OPERATION_INSTALL || op == DSU_RESOLVE_OPERATION_UPGRADE) {
            if (!scope_set) {
                if (!dsu_cli_manifest_infer_single_scope(manifest, &eff_scope)) {
                    st = DSU_STATUS_INVALID_ARGS;
                    goto done;
                }
            }
        } else {
            if (!scope_set && installed) {
                eff_scope = dsu_state_install_scope(installed);
            } else if (!scope_set) {
                (void)dsu_cli_manifest_infer_single_scope(manifest, &eff_scope);
            }
        }
        if (installed && scope_set && dsu_state_install_scope(installed) != eff_scope) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        req.scope = eff_scope;
    }
    req.allow_prerelease = allow_prerelease ? DSU_TRUE : DSU_FALSE;
    req.target_platform = platform;
    req.requested_components = (components && components->count) ? components->items : NULL;
    req.requested_component_count = (components ? components->count : 0u);
    req.excluded_components = (exclude && exclude->count) ? exclude->items : NULL;
    req.excluded_component_count = (exclude ? exclude->count : 0u);
    req.pins = NULL;
    req.pin_count = 0u;

    st = dsu_resolve_components(ctx, manifest, installed, &req, &result);

done:
    {
        int code = dsu_cli_exit_code(st);
        dsu_cli_json_begin_envelope(stdout, "resolve", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        if (result) {
            fputs("\"operation\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_operation_name(dsu_resolve_result_operation(result))); fputc(',', stdout);
            fputs("\"scope\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_scope_name(dsu_resolve_result_scope(result))); fputc(',', stdout);
            fputs("\"platform\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_platform(result)); fputc(',', stdout);
        } else {
            fputs("\"operation\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_operation_name(op)); fputc(',', stdout);
            fputs("\"scope\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_scope_name(scope)); fputc(',', stdout);
            fputs("\"platform\":", stdout); dsu_cli_json_put_escaped(stdout, platform ? platform : ""); fputc(',', stdout);
        }
        fputs("\"allow_prerelease\":", stdout); fputs((allow_prerelease ? "true" : "false"), stdout); fputc(',', stdout);
        if (result) {
            fputs("\"product_id\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_product_id(result)); fputc(',', stdout);
            fputs("\"product_version\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_product_version(result)); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_path(stdout, dsu_resolve_result_install_root(result)); fputc(',', stdout);
            fputs("\"manifest_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_resolve_result_manifest_digest64(result)); fputc(',', stdout);
            fputs("\"resolved_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_resolve_result_resolved_digest64(result)); fputc(',', stdout);
        } else {
            fputs("\"product_id\":", stdout); dsu_cli_json_put_escaped(stdout, ""); fputc(',', stdout);
            fputs("\"product_version\":", stdout); dsu_cli_json_put_escaped(stdout, ""); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_path(stdout, ""); fputc(',', stdout);
            fputs("\"manifest_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
            fputs("\"resolved_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
        }

        fputs("\"components\":[", stdout);
        if (result) {
            dsu_u32 n = dsu_resolve_result_component_count(result);
            for (i = 0u; i < n; ++i) {
                if (i) fputc(',', stdout);
                fputc('{', stdout);
                fputs("\"component_id\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_component_id(result, i)); fputc(',', stdout);
                fputs("\"version\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_component_version(result, i)); fputc(',', stdout);
                fputs("\"source\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_source_name(dsu_resolve_result_component_source(result, i))); fputc(',', stdout);
                fputs("\"action\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_action_name(dsu_resolve_result_component_action(result, i)));
                fputc('}', stdout);
            }
        }
        fputs("],", stdout);

        fputs("\"log\":[", stdout);
        if (result) {
            dsu_u32 nlog = dsu_resolve_result_log_count(result);
            for (i = 0u; i < nlog; ++i) {
                if (i) fputc(',', stdout);
                fputc('{', stdout);
                fputs("\"event\":", stdout);
                {
                    dsu_resolve_log_code_t code2 = dsu_resolve_result_log_code(result, i);
                    const char *name = "unknown";
                    if (code2 == DSU_RESOLVE_LOG_SEED_USER) name = "seed_user";
                    else if (code2 == DSU_RESOLVE_LOG_SEED_DEFAULT) name = "seed_default";
                    else if (code2 == DSU_RESOLVE_LOG_ADD_DEPENDENCY) name = "add_dependency";
                    else if (code2 == DSU_RESOLVE_LOG_CONFLICT) name = "conflict";
                    else if (code2 == DSU_RESOLVE_LOG_PLATFORM_FILTER) name = "platform_filter";
                    else if (code2 == DSU_RESOLVE_LOG_RECONCILE_INSTALLED) name = "reconcile_installed";
                    dsu_cli_json_put_escaped(stdout, name);
                }
                fputc(',', stdout);
                fputs("\"a\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_log_a(result, i)); fputc(',', stdout);
                fputs("\"b\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_log_b(result, i));
                fputc('}', stdout);
            }
        }
        fputs("]", stdout);
        dsu_cli_json_end_envelope(stdout);

        if (result) dsu_resolve_result_destroy(ctx, result);
        if (installed) dsu_state_destroy(ctx, installed);
        if (manifest) dsu_manifest_destroy(ctx, manifest);
        if (ctx) dsu_ctx_destroy(ctx);
        return code;
    }
}

static int dsu_cli_cmd_dry_run(const char *plan_path,
                               const char *out_log_path,
                               const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_plan_t *plan = NULL;
    dsu_execute_options_t exec_opts;
    dsu_status_t st;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_plan_read_file(ctx, plan_path, &plan);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    dsu_execute_options_init(&exec_opts);
    exec_opts.log_path = out_log_path;
    st = dsu_execute_plan(ctx, plan, &exec_opts);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    if (opts && opts->format_json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "dry-run"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "ok"); fputc(',', stdout);
        fputs("\"deterministic\":", stdout); fputs((opts->deterministic ? "true" : "false"), stdout); fputc(',', stdout);
        fputs("\"plan_file\":", stdout); dsu_cli_json_put_escaped(stdout, plan_path); fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_escaped(stdout, out_log_path); fputc(',', stdout);
        fprintf(stdout, "\"plan_id_hash32\":%lu,", (unsigned long)dsu_plan_id_hash32(plan));
        fputs("\"plan_id_hash64\":", stdout);
        {
            dsu_u64 id64 = dsu_plan_id_hash64(plan);
            unsigned long hi = (unsigned long)((id64 >> 32) & 0xFFFFFFFFu);
            unsigned long lo = (unsigned long)(id64 & 0xFFFFFFFFu);
            fprintf(stdout, "\"0x%08lx%08lx\",", hi, lo);
        }
        fprintf(stdout, "\"step_count\":%lu", (unsigned long)dsu_plan_step_count(plan));
        fputs("}\n", stdout);
    } else {
        fprintf(stdout, "plan_id_hash32=%lu\n", (unsigned long)dsu_plan_id_hash32(plan));
        {
            dsu_u64 id64 = dsu_plan_id_hash64(plan);
            unsigned long hi = (unsigned long)((id64 >> 32) & 0xFFFFFFFFu);
            unsigned long lo = (unsigned long)(id64 & 0xFFFFFFFFu);
            fprintf(stdout, "plan_id_hash64=0x%08lx%08lx\n", hi, lo);
        }
        fprintf(stdout, "steps=%lu\n", (unsigned long)dsu_plan_step_count(plan));
        fprintf(stdout, "log_file=%s\n", out_log_path);
    }

done:
    if (plan) dsu_plan_destroy(ctx, plan);
    if (ctx) dsu_ctx_destroy(ctx);

    if (st != DSU_STATUS_SUCCESS) {
        if (opts && opts->format_json) {
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "dry-run"); fputc(',', stdout);
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
            fprintf(stdout, "\"exit_code\":%d", dsu_cli_exit_code(st));
            fputs("}\n", stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_install(const char *plan_path, const char *out_log_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_plan_t *plan = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    dsu_status_t log_st = DSU_STATUS_SUCCESS;
    const char *log_path = out_log_path ? out_log_path : "audit.dsu.log";

    dsu_txn_options_init(&txn_opts);
    dsu_txn_result_init(&res);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_plan_read_file(ctx, plan_path, &plan);
    if (st != DSU_STATUS_SUCCESS) goto done;

    txn_opts.dry_run = (dsu_bool)((opts && opts->dry_run) ? 1 : 0);
    st = dsu_txn_apply_plan(ctx, plan, &txn_opts, &res);

done:
    if (ctx && log_path && log_path[0] != '\0') {
        log_st = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), log_path);
        if (st == DSU_STATUS_SUCCESS && log_st != DSU_STATUS_SUCCESS) {
            st = log_st;
        }
    }
    if (opts && opts->format_json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "install"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));        
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); fputs((opts && opts->dry_run) ? "true" : "false", stdout);
        fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_escaped(stdout, log_path);        
        if (st == DSU_STATUS_SUCCESS) {
            fputc(',', stdout);
            fputs("\"plan_file\":", stdout); dsu_cli_json_put_escaped(stdout, plan_path); fputc(',', stdout);
            fputs("\"plan_id_hash64\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.digest64); fputc(',', stdout);
            fputs("\"journal_id\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.journal_id); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.install_root); fputc(',', stdout);
            fputs("\"txn_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.txn_root); fputc(',', stdout);
            fputs("\"journal_file\":", stdout); dsu_cli_json_put_escaped(stdout, res.journal_path); fputc(',', stdout);
            fprintf(stdout, "\"journal_entry_count\":%lu,", (unsigned long)res.journal_entry_count);
            fprintf(stdout, "\"commit_progress\":%lu,", (unsigned long)res.commit_progress);
            fprintf(stdout, "\"staged_file_count\":%lu,", (unsigned long)res.staged_file_count);
            fprintf(stdout, "\"verified_ok\":%lu,", (unsigned long)res.verified_ok);
            fprintf(stdout, "\"verified_missing\":%lu,", (unsigned long)res.verified_missing);
            fprintf(stdout, "\"verified_mismatch\":%lu", (unsigned long)res.verified_mismatch);
        }
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "journal_id=0x%08lx%08lx\n",
                    (unsigned long)((res.journal_id >> 32) & 0xFFFFFFFFu),
                    (unsigned long)(res.journal_id & 0xFFFFFFFFu));
            fprintf(stdout, "journal_file=%s\n", res.journal_path);
            fprintf(stdout, "log_file=%s\n", log_path);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (plan) dsu_plan_destroy(ctx, plan);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_apply(const char *plan_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_plan_t *plan = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    dsu_status_t log_st = DSU_STATUS_SUCCESS;
    const char *log_path = "audit.dsu.log";

    dsu_txn_options_init(&txn_opts);
    dsu_txn_result_init(&res);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_plan_read_file(ctx, plan_path, &plan);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_plan_validate(plan);
    if (st != DSU_STATUS_SUCCESS) goto done;

    txn_opts.dry_run = (dsu_bool)((opts && opts->dry_run) ? 1 : 0);
    st = dsu_txn_apply_plan(ctx, plan, &txn_opts, &res);

done:
    if (ctx && log_path && log_path[0] != '\0') {
        log_st = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), log_path);
        if (st == DSU_STATUS_SUCCESS && log_st != DSU_STATUS_SUCCESS) {
            st = log_st;
        }
    }
    if (opts && opts->format_json) {
        int code = dsu_cli_exit_code(st);
        dsu_cli_json_begin_envelope(stdout, "apply", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"deterministic\":", stdout); dsu_cli_json_put_bool(stdout, (opts && opts->deterministic)); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); dsu_cli_json_put_bool(stdout, (opts && opts->dry_run)); fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_path(stdout, log_path);
        if (st == DSU_STATUS_SUCCESS) {
            fputc(',', stdout);
            fputs("\"plan_file\":", stdout); dsu_cli_json_put_path(stdout, plan_path); fputc(',', stdout);
            fputs("\"plan_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.digest64); fputc(',', stdout);
            fputs("\"journal_id\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.journal_id); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_path(stdout, res.install_root); fputc(',', stdout);
            fputs("\"txn_root\":", stdout); dsu_cli_json_put_path(stdout, res.txn_root); fputc(',', stdout);
            fputs("\"journal_file\":", stdout); dsu_cli_json_put_path(stdout, res.journal_path); fputc(',', stdout);
            fprintf(stdout, "\"journal_entry_count\":%lu,", (unsigned long)res.journal_entry_count);
            fprintf(stdout, "\"commit_progress\":%lu,", (unsigned long)res.commit_progress);
            fprintf(stdout, "\"staged_file_count\":%lu,", (unsigned long)res.staged_file_count);
            fprintf(stdout, "\"verified_ok\":%lu,", (unsigned long)res.verified_ok);
            fprintf(stdout, "\"verified_missing\":%lu,", (unsigned long)res.verified_missing);
            fprintf(stdout, "\"verified_mismatch\":%lu,", (unsigned long)res.verified_mismatch);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "journal_id=0x%08lx%08lx\n",
                    (unsigned long)((res.journal_id >> 32) & 0xFFFFFFFFu),
                    (unsigned long)(res.journal_id & 0xFFFFFFFFu));
            fprintf(stdout, "journal_file=%s\n", res.journal_path);
            fprintf(stdout, "log_file=%s\n", log_path);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (plan) dsu_plan_destroy(ctx, plan);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_uninstall(const char *state_path, const char *out_log_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;
    dsu_status_t log_st = DSU_STATUS_SUCCESS;
    const char *log_path = out_log_path ? out_log_path : "audit.dsu.log";

    dsu_txn_options_init(&txn_opts);
    dsu_txn_result_init(&res);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load_file(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    txn_opts.dry_run = (dsu_bool)((opts && opts->dry_run) ? 1 : 0);
    st = dsu_txn_uninstall_state(ctx, state, state_path, &txn_opts, &res);

done:
    if (ctx && log_path && log_path[0] != '\0') {
        log_st = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), log_path);
        if (st == DSU_STATUS_SUCCESS && log_st != DSU_STATUS_SUCCESS) {
            st = log_st;
        }
    }
    if (opts && opts->format_json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "uninstall"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); fputs((opts && opts->dry_run) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_escaped(stdout, log_path);
        if (st == DSU_STATUS_SUCCESS) {
            fputc(',', stdout);
            fputs("\"state_file\":", stdout); dsu_cli_json_put_escaped(stdout, state_path); fputc(',', stdout);
            fputs("\"journal_id\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.journal_id); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.install_root); fputc(',', stdout);
            fputs("\"txn_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.txn_root); fputc(',', stdout);
            fputs("\"journal_file\":", stdout); dsu_cli_json_put_escaped(stdout, res.journal_path); fputc(',', stdout);
            fprintf(stdout, "\"journal_entry_count\":%lu,", (unsigned long)res.journal_entry_count);
            fprintf(stdout, "\"commit_progress\":%lu", (unsigned long)res.commit_progress);
        }
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "journal_file=%s\n", res.journal_path);
            fprintf(stdout, "log_file=%s\n", log_path);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_list_installed(const char *command_name,
                                      const char *state_path,
                                      const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    char *report = NULL;
    dsu_status_t st;
    int code;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_report_list_installed(ctx,
                                  state,
                                  (opts && opts->format_json) ? DSU_REPORT_FORMAT_JSON : DSU_REPORT_FORMAT_TEXT,
                                  &report);
    if (st != DSU_STATUS_SUCCESS) goto done;

done:
    code = dsu_cli_exit_code(st);
    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, command_name ? command_name : "list", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_path(stdout, state_path ? state_path : ""); fputc(',', stdout);
        fputs("\"format\":", stdout); dsu_cli_json_put_escaped(stdout, "json"); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS && report) {
            fputs("\"report\":", stdout);
            fputs(report, stdout);
            fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputs("\"report\":null,", stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        fputs(report ? report : "", stdout);
    }
    if (report) dsu_report_free(ctx, report);
    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return code;
}

static int dsu_cli_cmd_verify(const char *state_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    char *report = NULL;
    dsu_report_verify_summary_t summary;
    dsu_status_t st;
    int exit_code;

    dsu_report_verify_summary_init(&summary);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_report_verify(ctx,
                           state,
                           (opts && opts->format_json) ? DSU_REPORT_FORMAT_JSON : DSU_REPORT_FORMAT_TEXT,
                           &report,
                           &summary);
    if (st != DSU_STATUS_SUCCESS) goto done;

done:
    exit_code = dsu_cli_exit_code(st);
    if (st == DSU_STATUS_SUCCESS) {
        if (summary.missing || summary.modified || summary.extra || summary.errors) {
            exit_code = 2;
        }
    }

    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, "verify", exit_code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_path(stdout, state_path ? state_path : ""); fputc(',', stdout);
        fputs("\"format\":", stdout); dsu_cli_json_put_escaped(stdout, "json"); fputc(',', stdout);
        fprintf(stdout, "\"checked\":%lu,", (unsigned long)summary.checked);
        fprintf(stdout, "\"ok\":%lu,", (unsigned long)summary.ok);
        fprintf(stdout, "\"missing\":%lu,", (unsigned long)summary.missing);
        fprintf(stdout, "\"modified\":%lu,", (unsigned long)summary.modified);
        fprintf(stdout, "\"extra\":%lu,", (unsigned long)summary.extra);
        fprintf(stdout, "\"errors\":%lu,", (unsigned long)summary.errors);
        if (st == DSU_STATUS_SUCCESS && report) {
            fputs("\"report\":", stdout);
            fputs(report, stdout);
            fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputs("\"report\":null,", stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        fputs(report ? report : "", stdout);
    }

    if (report) dsu_report_free(ctx, report);
    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return exit_code;
}

static int dsu_cli_cmd_platform_register(const char *state_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_status_t st;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_platform_register_from_state(ctx, state);

done:
    if (opts && opts->format_json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "platform-register"); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_escaped(stdout, state_path ? state_path : ""); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "ok");
        } else {
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fputs("ok\n", stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_platform_unregister(const char *state_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_status_t st;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_platform_unregister_from_state(ctx, state);

done:
    if (opts && opts->format_json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "platform-unregister"); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_escaped(stdout, state_path ? state_path : ""); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "ok");
        } else {
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fputs("ok\n", stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_uninstall_preview(const char *state_path, const char *components_csv, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    char *report = NULL;
    dsu_status_t st;
    int exit_code;

    char *csv_buf = NULL;
    const char **items = NULL;
    dsu_u32 item_count = 0u;
    dsu_u32 item_cap = 0u;

    if (components_csv && components_csv[0] != '\0') {
        size_t n = strlen(components_csv);
        csv_buf = (char *)malloc(n + 1u);
        if (!csv_buf) {
            return 1;
        }
        memcpy(csv_buf, components_csv, n + 1u);

        /* Split in-place on commas; trim ASCII whitespace. */
        {
            char *p = csv_buf;
            while (p && *p) {
                char *seg = p;
                char *end;
                while (*p && *p != ',') ++p;
                if (*p == ',') {
                    *p++ = '\0';
                }
                while (*seg == ' ' || *seg == '\t') ++seg;
                end = seg + strlen(seg);
                while (end > seg && (end[-1] == ' ' || end[-1] == '\t')) {
                    end[-1] = '\0';
                    --end;
                }
                if (*seg == '\0') {
                    continue;
                }
                if (item_count == item_cap) {
                    dsu_u32 new_cap = (item_cap == 0u) ? 8u : (item_cap * 2u);
                    const char **np = (const char **)realloc((void *)items, (size_t)new_cap * sizeof(*items));
                    if (!np) {
                        free((void *)items);
                        free(csv_buf);
                        return 1;
                    }
                    items = np;
                    item_cap = new_cap;
                }
                items[item_count++] = seg;
            }
        }
    }

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_report_uninstall_preview(ctx,
                                      state,
                                      items,
                                      item_count,
                                      (opts && opts->format_json) ? DSU_REPORT_FORMAT_JSON : DSU_REPORT_FORMAT_TEXT,
                                      &report);
    if (st != DSU_STATUS_SUCCESS) goto done;

done:
    exit_code = dsu_cli_exit_code(st);
    if (opts && opts->format_json) {
        dsu_u32 i;
        dsu_cli_json_begin_envelope(stdout, "uninstall-preview", exit_code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_path(stdout, state_path ? state_path : ""); fputc(',', stdout);
        fputs("\"format\":", stdout); dsu_cli_json_put_escaped(stdout, "json"); fputc(',', stdout);
        fputs("\"components\":[", stdout);
        for (i = 0u; i < item_count; ++i) {
            if (i) fputc(',', stdout);
            dsu_cli_json_put_escaped(stdout, items[i] ? items[i] : "");
        }
        fputs("],", stdout);
        if (st == DSU_STATUS_SUCCESS && report) {
            fputs("\"report\":", stdout);
            fputs(report, stdout);
            fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputs("\"report\":null,", stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        fputs(report ? report : "", stdout);
    }
    if (report) dsu_report_free(ctx, report);
    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    free((void *)items);
    free(csv_buf);
    return exit_code;
}

static dsu_status_t dsu_cli_write_file_bytes(const char *path, const char *bytes) {
    FILE *f;
    size_t n;
    size_t nw;
    if (!path || path[0] == '\0') return DSU_STATUS_INVALID_ARGS;
    if (!bytes) bytes = "";
    n = strlen(bytes);
    f = fopen(path, "wb");
    if (!f) return DSU_STATUS_IO_ERROR;
    nw = fwrite(bytes, 1u, n, f);
    fclose(f);
    if (nw != n) return DSU_STATUS_IO_ERROR;
    return DSU_STATUS_SUCCESS;
}

static dsu_status_t dsu_cli_join_out_path(const char *dir, const char *name, char out_path[1024]) {
    size_t a;
    size_t b;
    size_t need;
    if (!dir || !name || !out_path) return DSU_STATUS_INVALID_ARGS;
    a = strlen(dir);
    b = strlen(name);
    if (a == 0u || b == 0u) return DSU_STATUS_INVALID_ARGS;
    need = a + b + 2u;
    if (need > 1024u) return DSU_STATUS_INVALID_ARGS;
    memcpy(out_path, dir, a);
    if (dir[a - 1u] != '/' && dir[a - 1u] != '\\') {
        out_path[a++] = '/';
    }
    memcpy(out_path + a, name, b);
    out_path[a + b] = '\0';
    return DSU_STATUS_SUCCESS;
}

static int dsu_cli_cmd_report(const char *state_path, const char *out_dir, const char *format_str, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_status_t st;
    dsu_report_format_t fmt = DSU_REPORT_FORMAT_JSON;
    const char *ext = "json";
    char *report = NULL;
    dsu_report_verify_summary_t summary;
    int exit_code = 0;
    int verify_bad = 0;

    dsu_report_verify_summary_init(&summary);

    if (!state_path || !out_dir) return 3;

    if (format_str && format_str[0] != '\0') {
        if (strcmp(format_str, "txt") == 0 || strcmp(format_str, "text") == 0) {
            fmt = DSU_REPORT_FORMAT_TEXT;
            ext = "txt";
        } else if (strcmp(format_str, "json") == 0) {
            fmt = DSU_REPORT_FORMAT_JSON;
            ext = "json";
        } else {
            return 3;
        }
    }

#if defined(_WIN32)
    (void)_mkdir(out_dir);
#else
    (void)mkdir(out_dir, 0755);
#endif

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    /* inventory */
    st = dsu_report_list_installed(ctx, state, fmt, &report);
    if (st != DSU_STATUS_SUCCESS) goto done;
    {
        char out_path[1024];
        char name[64];
        sprintf(name, "inventory.%s", ext);
        st = dsu_cli_join_out_path(out_dir, name, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_cli_write_file_bytes(out_path, report);
        if (st != DSU_STATUS_SUCCESS) goto done;
    }
    dsu_report_free(ctx, report);
    report = NULL;

    /* touched paths */
    st = dsu_report_touched_paths(ctx, state, fmt, &report);
    if (st != DSU_STATUS_SUCCESS) goto done;
    {
        char out_path[1024];
        char name[64];
        sprintf(name, "touched_paths.%s", ext);
        st = dsu_cli_join_out_path(out_dir, name, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_cli_write_file_bytes(out_path, report);
        if (st != DSU_STATUS_SUCCESS) goto done;
    }
    dsu_report_free(ctx, report);
    report = NULL;

    /* uninstall preview (all components) */
    st = dsu_report_uninstall_preview(ctx, state, NULL, 0u, fmt, &report);
    if (st != DSU_STATUS_SUCCESS) goto done;
    {
        char out_path[1024];
        char name[64];
        sprintf(name, "uninstall_preview.%s", ext);
        st = dsu_cli_join_out_path(out_dir, name, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_cli_write_file_bytes(out_path, report);
        if (st != DSU_STATUS_SUCCESS) goto done;
    }
    dsu_report_free(ctx, report);
    report = NULL;

    /* verify */
    st = dsu_report_verify(ctx, state, fmt, &report, &summary);
    if (st != DSU_STATUS_SUCCESS) goto done;
    {
        char out_path[1024];
        char name[64];
        sprintf(name, "verify.%s", ext);
        st = dsu_cli_join_out_path(out_dir, name, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_cli_write_file_bytes(out_path, report);
        if (st != DSU_STATUS_SUCCESS) goto done;
    }
    if (summary.missing || summary.modified || summary.extra || summary.errors) {
        verify_bad = 1;
    }
    dsu_report_free(ctx, report);
    report = NULL;

    /* corruption assessment (no audit log required) */
    st = dsu_report_corruption_assessment(ctx, state, NULL, fmt, &report);
    if (st != DSU_STATUS_SUCCESS) goto done;
    {
        char out_path[1024];
        char name[64];
        sprintf(name, "corruption_assessment.%s", ext);
        st = dsu_cli_join_out_path(out_dir, name, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_cli_write_file_bytes(out_path, report);
        if (st != DSU_STATUS_SUCCESS) goto done;
    }
    dsu_report_free(ctx, report);
    report = NULL;

done:
    exit_code = dsu_cli_exit_code(st);
    if (st == DSU_STATUS_SUCCESS && verify_bad) {
        exit_code = 2;
    }
    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, "report", exit_code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"state_file\":", stdout); dsu_cli_json_put_path(stdout, state_path ? state_path : ""); fputc(',', stdout);
        fputs("\"out_dir\":", stdout); dsu_cli_json_put_path(stdout, out_dir ? out_dir : ""); fputc(',', stdout);
        fputs("\"format\":", stdout); dsu_cli_json_put_escaped(stdout, (fmt == DSU_REPORT_FORMAT_TEXT) ? "txt" : "json"); fputc(',', stdout);
        fprintf(stdout, "\"verify_checked\":%lu,", (unsigned long)summary.checked);
        fprintf(stdout, "\"verify_ok\":%lu,", (unsigned long)summary.ok);
        fprintf(stdout, "\"verify_missing\":%lu,", (unsigned long)summary.missing);
        fprintf(stdout, "\"verify_modified\":%lu,", (unsigned long)summary.modified);
        fprintf(stdout, "\"verify_extra\":%lu,", (unsigned long)summary.extra);
        fprintf(stdout, "\"verify_errors\":%lu,", (unsigned long)summary.errors);
        fputs("\"reports\":[", stdout);
        if (st == DSU_STATUS_SUCCESS) {
            int first = 1;
            const char *names[5];
            const char *files[5];
            char paths[5][1024];
            dsu_u32 j;

            names[0] = "inventory";
            names[1] = "touched_paths";
            names[2] = "uninstall_preview";
            names[3] = "verify";
            names[4] = "corruption_assessment";

            files[0] = "inventory";
            files[1] = "touched_paths";
            files[2] = "uninstall_preview";
            files[3] = "verify";
            files[4] = "corruption_assessment";

            for (j = 0u; j < 5u; ++j) {
                char fname[64];
                sprintf(fname, "%s.%s", files[j], ext);
                if (dsu_cli_join_out_path(out_dir, fname, paths[j]) != DSU_STATUS_SUCCESS) {
                    paths[j][0] = '\0';
                }
            }

            for (j = 0u; j < 5u; ++j) {
                if (!first) fputc(',', stdout);
                first = 0;
                fputc('{', stdout);
                fputs("\"name\":", stdout); dsu_cli_json_put_escaped(stdout, names[j]); fputc(',', stdout);
                fputs("\"file\":", stdout); dsu_cli_json_put_path(stdout, paths[j]);
                fputc('}', stdout);
            }
        }
        fputs("],", stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st));
        dsu_cli_json_end_envelope(stdout);
    } else if (!(opts && opts->quiet)) {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "ok\n");
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }
    if (report) dsu_report_free(ctx, report);
    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return exit_code;
}

static int dsu_cli_cmd_rollback(const char *journal_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;

    dsu_txn_options_init(&txn_opts);
    dsu_txn_result_init(&res);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    txn_opts.dry_run = (dsu_bool)((opts && opts->dry_run) ? 1 : 0);
    st = dsu_txn_rollback_journal(ctx, journal_path, &txn_opts, &res);

done:
    if (opts && opts->format_json) {
        int code = dsu_cli_exit_code(st);
        dsu_cli_json_begin_envelope(stdout, "rollback", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"deterministic\":", stdout); dsu_cli_json_put_bool(stdout, (opts && opts->deterministic)); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); dsu_cli_json_put_bool(stdout, (opts && opts->dry_run)); fputc(',', stdout);
        fputs("\"journal_file\":", stdout); dsu_cli_json_put_path(stdout, journal_path ? journal_path : "");
        if (st == DSU_STATUS_SUCCESS) {
            fputc(',', stdout);
            fputs("\"journal_id\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.journal_id); fputc(',', stdout);
            fputs("\"plan_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.digest64); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_path(stdout, res.install_root); fputc(',', stdout);
            fputs("\"txn_root\":", stdout); dsu_cli_json_put_path(stdout, res.txn_root); fputc(',', stdout);
            fprintf(stdout, "\"journal_entry_count\":%lu,", (unsigned long)res.journal_entry_count);
            fprintf(stdout, "\"commit_progress_before\":%lu,", (unsigned long)res.commit_progress);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "ok\n");
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_manifest_validate(const char *command_name, const char *in_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_status_t st;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_manifest_load_file(ctx, in_path, &manifest);
    if (st == DSU_STATUS_SUCCESS) {
        st = dsu_manifest_validate(manifest);
    }

done:
    if (opts && opts->format_json) {
        int code = dsu_cli_exit_code(st);
        dsu_cli_json_begin_envelope(stdout, command_name ? command_name : "manifest validate", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"in_file\":", stdout); dsu_cli_json_put_path(stdout, in_path ? in_path : ""); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "\"content_digest32\":%lu,", (unsigned long)dsu_manifest_content_digest32(manifest));
            fputs("\"content_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_manifest_content_digest64(manifest)); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
        } else {
            fputs("\"content_digest32\":0,", stdout);
            fputs("\"content_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fputs("ok\n", stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_manifest_dump(const char *command_name, const char *in_path, const char *out_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_status_t st;
    FILE *mf = NULL;
    int emit_manifest = 0;
    int cleanup_tmp = 0;
    const char *out_eff = out_path;

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_manifest_load_file(ctx, in_path, &manifest);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    if (out_eff && out_eff[0] != '\0') {
        st = dsu_manifest_write_json_file(ctx, manifest, out_eff);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
        emit_manifest = 0;
    } else {
        out_eff = ".dsu_manifest_dump.tmp.json";
        cleanup_tmp = 1;
        st = dsu_manifest_write_json_file(ctx, manifest, out_eff);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
        mf = fopen(out_eff, "rb");
        if (!mf) {
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }
        emit_manifest = 1;
    }

done:
    if (opts && opts->format_json) {
        int code = dsu_cli_exit_code(st);
        dsu_cli_json_begin_envelope(stdout, command_name ? command_name : "manifest dump", code);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"in_file\":", stdout); dsu_cli_json_put_path(stdout, in_path ? in_path : ""); fputc(',', stdout);
        fputs("\"out_file\":", stdout); dsu_cli_json_put_path(stdout, (out_path && out_path[0] != '\0') ? out_path : ""); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "\"content_digest32\":%lu,", (unsigned long)dsu_manifest_content_digest32(manifest));
            fputs("\"content_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_manifest_content_digest64(manifest)); fputc(',', stdout);
            fputs("\"wrote_file\":", stdout); dsu_cli_json_put_bool(stdout, (out_path && out_path[0] != '\0')); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "");
            if (emit_manifest && mf) {
                unsigned char buf[32768];
                size_t n;
                fputc(',', stdout);
                fputs("\"manifest\":", stdout);
                while ((n = fread(buf, 1u, sizeof(buf), mf)) != 0u) {
                    if (fwrite(buf, 1u, n, stdout) != n) {
                        st = DSU_STATUS_IO_ERROR;
                        break;
                    }
                }
                if (ferror(mf)) {
                    st = DSU_STATUS_IO_ERROR;
                }
                fclose(mf);
                mf = NULL;
            }
        } else {
            fputs("\"content_digest32\":0,", stdout);
            fputs("\"content_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
            fputs("\"wrote_file\":false,", stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st));
        }
        dsu_cli_json_end_envelope(stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            if (!(opts && opts->quiet)) {
                if (out_path && out_path[0] != '\0') {
                    fprintf(stdout, "wrote %s\n", out_path);
                } else {
                    fputs("ok\n", stdout);
                }
            }
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (mf) {
        fclose(mf);
        mf = NULL;
    }
    if (cleanup_tmp && out_eff) {
        (void)remove(out_eff);
    }
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_export_log(const char *log_path,
                                 const char *out_path,
                                 const char *format_str,
                                 const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_log_t *log = NULL;
    dsu_status_t st = DSU_STATUS_SUCCESS;
    int fmt_json = 0;
    int rc;
    dsu_u32 event_count = 0u;

    if (!log_path || log_path[0] == '\0' || !out_path || out_path[0] == '\0') {
        return 3;
    }
    if (!format_str || format_str[0] == '\0') {
        return 3;
    }
    if (strcmp(format_str, "json") == 0) {
        fmt_json = 1;
    } else if (strcmp(format_str, "txt") == 0 || strcmp(format_str, "text") == 0) {
        fmt_json = 0;
    } else {
        return 3;
    }

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_log_read_file(ctx, log_path, &log);
    if (st != DSU_STATUS_SUCCESS) goto done;
    event_count = dsu_log_event_count(log);

    if (fmt_json) {
        dsu_log_destroy(ctx, log);
        log = NULL;
        st = dsu_log_export_json(ctx, log_path, out_path);
        if (st != DSU_STATUS_SUCCESS) goto done;
    } else {
        FILE *f = NULL;
        dsu_u32 i;
        dsu_u32 count;

        f = fopen(out_path, "wb");
        if (!f) {
            st = DSU_STATUS_IO_ERROR;
            goto done;
        }

        fputs("seq\tid\tseverity\tcategory\ttimestamp\tmessage\n", f);
        count = dsu_log_event_count(log);
        for (i = 0u; i < count; ++i) {
            dsu_u32 event_id = 0u;
            dsu_u8 severity = 0u;
            dsu_u8 category = 0u;
            dsu_u32 ts = 0u;
            const char *msg = NULL;
            dsu_status_t st2 = dsu_log_event_get(log, i, &event_id, &severity, &category, &ts, &msg);
            if (st2 != DSU_STATUS_SUCCESS) {
                fclose(f);
                dsu_log_destroy(ctx, log);
                log = NULL;
                st = st2;
                goto done;
            }
            fprintf(f, "%lu\t%lu\t%u\t%u\t%lu\t", (unsigned long)(i + 1u), (unsigned long)event_id,
                    (unsigned)severity, (unsigned)category, (unsigned long)ts);
            if (msg) {
                const unsigned char *p = (const unsigned char *)msg;
                unsigned char c;
                while ((c = *p++) != 0u) {
                    if (c == '\r' || c == '\n' || c == '\t') {
                        fputc(' ', f);
                    } else {
                        fputc((int)c, f);
                    }
                }
            }
            fputc('\n', f);
        }
        fclose(f);
        dsu_log_destroy(ctx, log);
        log = NULL;
    }

done:
    rc = dsu_cli_exit_code(st);
    if (opts && opts->format_json) {
        dsu_cli_json_begin_envelope(stdout, "export-log", rc);
        fputs("\"core_status\":", stdout); fprintf(stdout, "%lu", (unsigned long)st); fputc(',', stdout);
        fputs("\"core_status_name\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_path(stdout, log_path); fputc(',', stdout);
        fputs("\"out_file\":", stdout); dsu_cli_json_put_path(stdout, out_path); fputc(',', stdout);
        fputs("\"format\":", stdout); dsu_cli_json_put_escaped(stdout, fmt_json ? "json" : "txt"); fputc(',', stdout);
        fprintf(stdout, "\"event_count\":%lu,", (unsigned long)event_count);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st));
        dsu_cli_json_end_envelope(stdout);
    } else if (!(opts && opts->quiet)) {
        if (st == DSU_STATUS_SUCCESS) {
            fputs("ok\n", stdout);
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }
    if (log) {
        dsu_log_destroy(ctx, log);
        log = NULL;
    }
    if (ctx) dsu_ctx_destroy(ctx);
    return rc;
}

int main(int argc, char **argv) {
    dsu_cli_opts_t opts;
    const char *cmd;
    int i;

#if defined(_WIN32)
    (void)_setmode(_fileno(stdout), _O_BINARY);
    (void)_setmode(_fileno(stderr), _O_BINARY);
#endif

    opts.deterministic = 1;
    opts.quiet = 0;
    opts.format_json = 1;
    opts.dry_run = 0;

    if (argc < 2) {
        dsu_cli_print_help_root(stderr);
        return 3;
    }

    cmd = argv[1];

    /* Global flags after command. */
    for (i = 2; i < argc; ++i) {
        const char *arg = argv[i];
        const char *dv;
        if (!arg) continue;
        if (dsu_cli_streq(arg, "--json")) {
            opts.format_json = 1;
        } else if (dsu_cli_streq(arg, "--quiet")) {
            opts.quiet = 1;
        } else if (dsu_cli_streq(arg, "--dry-run")) {
            opts.dry_run = 1;
        } else {
            dv = dsu_cli_kv_value_inline(arg, "--deterministic");
            if (dv) {
                if (strcmp(dv, "0") == 0) opts.deterministic = 0;
                else if (strcmp(dv, "1") == 0) opts.deterministic = 1;
                else return 3;
            } else if (dsu_cli_streq(arg, "--deterministic")) {
                if (i + 1 >= argc) return 3;
                if (strcmp(argv[i + 1], "0") == 0) opts.deterministic = 0;
                else if (strcmp(argv[i + 1], "1") == 0) opts.deterministic = 1;
                else return 3;
                ++i;
            }
        }
    }

    if (dsu_cli_streq(cmd, "version")) {
        return dsu_cli_cmd_version(argc - 1, argv + 1, &opts);
    }

    if (dsu_cli_streq(cmd, "help") || dsu_cli_streq(cmd, "--help") || dsu_cli_streq(cmd, "-h")) {
        char *help_args[2];
        int help_argc = 0;
        for (i = 2; i < argc && help_argc < 2; ++i) {
            const char *arg = argv[i];
            if (!arg || arg[0] == '-') continue;
            help_args[help_argc++] = (char *)arg;
        }
        dsu_cli_print_help_command(stdout, help_argc, help_args);
        return 0;
    }

    if (dsu_cli_streq(cmd, "manifest")) {
        const char *sub = (argc >= 3) ? argv[2] : NULL;
        if (!sub) {
            char *h[1];
            h[0] = "manifest";
            dsu_cli_print_help_command(stderr, 1, h);
            return 3;
        }

        if (dsu_cli_streq(sub, "validate")) {
            const char *in_path = NULL;
            for (i = 3; i < argc; ++i) {
                const char *arg = argv[i];
                const char *v;
                if (!arg) continue;
                v = dsu_cli_kv_value_inline(arg, "--in");
                if (v) {
                    in_path = v;
                    continue;
                }
                if (dsu_cli_streq(arg, "--in") && i + 1 < argc) {
                    in_path = argv[++i];
                }
            }
            if (!in_path) {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("manifest validate", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                } else {
                    char *h[2];
                    h[0] = "manifest";
                    h[1] = "validate";
                    dsu_cli_print_help_command(stderr, 2, h);
                }
                return 3;
            }
            return dsu_cli_cmd_manifest_validate("manifest validate", in_path, &opts);
        }

        if (dsu_cli_streq(sub, "dump")) {
            const char *in_path = NULL;
            const char *out_path = NULL;
            const char *fmt = NULL;
            for (i = 3; i < argc; ++i) {
                const char *arg = argv[i];
                const char *v;
                if (!arg) continue;
                v = dsu_cli_kv_value_inline(arg, "--in");
                if (v) {
                    in_path = v;
                    continue;
                }
                v = dsu_cli_kv_value_inline(arg, "--out");
                if (v) {
                    out_path = v;
                    continue;
                }
                v = dsu_cli_kv_value_inline(arg, "--format");
                if (v) {
                    fmt = v;
                    continue;
                }
                if (dsu_cli_streq(arg, "--in") && i + 1 < argc) {
                    in_path = argv[++i];
                    continue;
                }
                if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                    out_path = argv[++i];
                    continue;
                }
                if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                    fmt = argv[++i];
                }
            }
            if (fmt && fmt[0] != '\0' && strcmp(fmt, "json") != 0) {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("manifest dump", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                } else {
                    char *h[2];
                    h[0] = "manifest";
                    h[1] = "dump";
                    dsu_cli_print_help_command(stderr, 2, h);
                }
                return 3;
            }
            if (!in_path) {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("manifest dump", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                } else {
                    char *h[2];
                    h[0] = "manifest";
                    h[1] = "dump";
                    dsu_cli_print_help_command(stderr, 2, h);
                }
                return 3;
            }
            return dsu_cli_cmd_manifest_dump("manifest dump", in_path, out_path, &opts);
        }

        {
            char *h[1];
            h[0] = "manifest";
            dsu_cli_print_help_command(stderr, 1, h);
            return 3;
        }
    }

    if (dsu_cli_streq(cmd, "manifest-validate")) {
        const char *in_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--in");
            if (v) {
                in_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--in") && i + 1 < argc) {
                in_path = argv[++i];
            }
        }
        if (!in_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("manifest-validate", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_manifest_validate("manifest-validate", in_path, &opts);
    }

    if (dsu_cli_streq(cmd, "manifest-dump")) {
        const char *in_path = NULL;
        const char *out_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--in");
            if (v) {
                in_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--out");
            if (v) {
                out_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--in") && i + 1 < argc) {
                in_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                out_path = argv[++i];
            }
        }
        if (!in_path || !out_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("manifest-dump", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_manifest_dump("manifest-dump", in_path, out_path, &opts);
    }

    if (dsu_cli_streq(cmd, "resolve")) {
        const char *manifest_path = NULL;
        const char *installed_state_path = NULL; /* v1 flag name: --state (kept internal for now) */
        const char *components_csv = NULL;
        const char *exclude_csv = NULL;
        const char *scope_str = NULL;
        int scope_set = 0;
        const char *op_str = NULL;
        int op_set = 0;
        dsu_resolve_operation_t op = DSU_RESOLVE_OPERATION_INSTALL;
        dsu_manifest_install_scope_t scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        dsu_cli_csv_list_t components;
        dsu_cli_csv_list_t exclude;
        int ok = 1;

        memset(&components, 0, sizeof(components));
        memset(&exclude, 0, sizeof(exclude));

        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;

            v = dsu_cli_kv_value_inline(arg, "--manifest");
            if (v) {
                manifest_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                installed_state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--components");
            if (v) {
                components_csv = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--exclude");
            if (v) {
                exclude_csv = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--scope");
            if (v) {
                scope_str = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--op");
            if (v) {
                op_str = v;
                op_set = 1;
                continue;
            }

            if (dsu_cli_streq(arg, "--manifest") && i + 1 < argc) {
                manifest_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                installed_state_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--components") && i + 1 < argc) {
                components_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--exclude") && i + 1 < argc) {
                exclude_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--scope") && i + 1 < argc) {
                scope_str = argv[++i];
            } else if (dsu_cli_streq(arg, "--op") && i + 1 < argc) {
                op_str = argv[++i];
                op_set = 1;
            }
        }

        if (!ok || !manifest_path || !op_set || !op_str) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("resolve", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "resolve";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        if (dsu_cli_streq(op_str, "install")) {
            op = DSU_RESOLVE_OPERATION_INSTALL;
        } else if (dsu_cli_streq(op_str, "upgrade")) {
            op = DSU_RESOLVE_OPERATION_UPGRADE;
        } else if (dsu_cli_streq(op_str, "repair")) {
            op = DSU_RESOLVE_OPERATION_REPAIR;
        } else if (dsu_cli_streq(op_str, "uninstall")) {
            op = DSU_RESOLVE_OPERATION_UNINSTALL;
        } else {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("resolve", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "resolve";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        if (scope_str && !dsu_cli_parse_scope(scope_str, &scope)) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("resolve", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "resolve";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        if (scope_str) {
            scope_set = 1;
        }
        if (components_csv && !dsu_cli_csv_list_parse(components_csv, &components)) {
            dsu_cli_csv_list_free(&components);
            if (opts.format_json) {
                dsu_cli_json_error_envelope("resolve", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }
        if (exclude_csv && !dsu_cli_csv_list_parse(exclude_csv, &exclude)) {
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            if (opts.format_json) {
                dsu_cli_json_error_envelope("resolve", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }

        {
            int rc = dsu_cli_cmd_resolve(manifest_path,
                                         installed_state_path,
                                         op,
                                         &components,
                                         &exclude,
                                         scope_set,
                                         scope,
                                         NULL,
                                         0,
                                         &opts);
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            return rc;
        }
    }

    if (dsu_cli_streq(cmd, "plan")) {
        const char *manifest_path = NULL;
        const char *state_path = NULL;
        const char *components_csv = NULL;
        const char *exclude_csv = NULL;
        const char *scope_str = NULL;
        const char *op_str = NULL;
        const char *out_plan_path = NULL;
        int op_set = 0;
        int scope_set = 0;
        dsu_resolve_operation_t op = DSU_RESOLVE_OPERATION_INSTALL;
        dsu_manifest_install_scope_t scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        dsu_cli_csv_list_t components;
        dsu_cli_csv_list_t exclude;

        memset(&components, 0, sizeof(components));
        memset(&exclude, 0, sizeof(exclude));

        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;

            v = dsu_cli_kv_value_inline(arg, "--manifest");
            if (v) {
                manifest_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--op");
            if (v) {
                op_str = v;
                op_set = 1;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--components");
            if (v) {
                components_csv = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--exclude");
            if (v) {
                exclude_csv = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--scope");
            if (v) {
                scope_str = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--out");
            if (v) {
                out_plan_path = v;
                continue;
            }

            if (dsu_cli_streq(arg, "--manifest") && i + 1 < argc) {
                manifest_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--op") && i + 1 < argc) {
                op_str = argv[++i];
                op_set = 1;
            } else if (dsu_cli_streq(arg, "--components") && i + 1 < argc) {
                components_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--exclude") && i + 1 < argc) {
                exclude_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--scope") && i + 1 < argc) {
                scope_str = argv[++i];
            } else if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                out_plan_path = argv[++i];
            }
        }

        if (!manifest_path || !out_plan_path || !op_set) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("plan", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "plan";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }

        if (dsu_cli_streq(op_str, "install")) {
            op = DSU_RESOLVE_OPERATION_INSTALL;
        } else if (dsu_cli_streq(op_str, "upgrade")) {
            op = DSU_RESOLVE_OPERATION_UPGRADE;
        } else if (dsu_cli_streq(op_str, "repair")) {
            op = DSU_RESOLVE_OPERATION_REPAIR;
        } else if (dsu_cli_streq(op_str, "uninstall")) {
            op = DSU_RESOLVE_OPERATION_UNINSTALL;
        } else {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("plan", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }
        if (scope_str && !dsu_cli_parse_scope(scope_str, &scope)) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("plan", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }
        if (scope_str) {
            scope_set = 1;
        }
        if (components_csv && !dsu_cli_csv_list_parse(components_csv, &components)) {
            dsu_cli_csv_list_free(&components);
            if (opts.format_json) {
                dsu_cli_json_error_envelope("plan", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }
        if (exclude_csv && !dsu_cli_csv_list_parse(exclude_csv, &exclude)) {
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            if (opts.format_json) {
                dsu_cli_json_error_envelope("plan", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            }
            return 3;
        }

        {
            int rc = dsu_cli_cmd_plan(manifest_path,
                                      state_path,
                                      op,
                                      scope_set,
                                      scope,
                                      (components.count != 0u) ? components.items : NULL,
                                      components.count,
                                      (exclude.count != 0u) ? exclude.items : NULL,
                                      exclude.count,
                                      out_plan_path,
                                      &opts);
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            return rc;
        }
    }

    if (dsu_cli_streq(cmd, "dry-run")) {
        const char *plan_path = NULL;
        const char *out_log_path = NULL;

        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;

            v = dsu_cli_kv_value_inline(arg, "--plan");
            if (v) {
                plan_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--log");
            if (v) {
                out_log_path = v;
                continue;
            }

            if (dsu_cli_streq(arg, "--plan") && i + 1 < argc) {
                plan_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--log") && i + 1 < argc) {
                out_log_path = argv[++i];
            }
        }

        if (!plan_path || !out_log_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("dry-run", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_dry_run(plan_path, out_log_path, &opts);
    }

    if (dsu_cli_streq(cmd, "apply")) {
        const char *plan_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            if (dsu_cli_streq(arg, "--dry-run")) {
                opts.dry_run = 1;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--plan");
            if (v) {
                plan_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--plan") && i + 1 < argc) {
                plan_path = argv[++i];
            }
        }
        if (!plan_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("apply", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "apply";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        return dsu_cli_cmd_apply(plan_path, &opts);
    }

    if (dsu_cli_streq(cmd, "install")) {
        const char *plan_path = NULL;
        const char *out_log_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--plan");
            if (v) {
                plan_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--log");
            if (v) {
                out_log_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--plan") && i + 1 < argc) {
                plan_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--log") && i + 1 < argc) {
                out_log_path = argv[++i];
            }
        }
        if (!plan_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("install", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_install(plan_path, out_log_path, &opts);
    }

    if (dsu_cli_streq(cmd, "list")) {
        const char *state_path = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
            }
        }
        if (fmt && fmt[0] != '\0') {
            if (strcmp(fmt, "txt") == 0 || strcmp(fmt, "text") == 0) {
                opts.format_json = 0;
            } else if (strcmp(fmt, "json") == 0) {
                opts.format_json = 1;
            } else {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("list", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                }
                return 3;
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("list", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "list";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        return dsu_cli_cmd_list_installed("list", state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "list-installed")) {
        const char *state_path = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
            }
        }
        if (fmt && fmt[0] != '\0') {
            if (strcmp(fmt, "txt") == 0 || strcmp(fmt, "text") == 0) {
                opts.format_json = 0;
            } else if (strcmp(fmt, "json") == 0) {
                opts.format_json = 1;
            } else {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("list-installed", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                }
                return 3;
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("list-installed", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_list_installed("list-installed", state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "uninstall")) {
        const char *state_path = NULL;
        const char *out_log_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--log");
            if (v) {
                out_log_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--log") && i + 1 < argc) {
                out_log_path = argv[++i];
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("uninstall", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_uninstall(state_path, out_log_path, &opts);
    }

    if (dsu_cli_streq(cmd, "verify")) {
        const char *state_path = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
            }
        }
        if (fmt && fmt[0] != '\0') {
            if (strcmp(fmt, "txt") == 0 || strcmp(fmt, "text") == 0) {
                opts.format_json = 0;
            } else if (strcmp(fmt, "json") == 0) {
                opts.format_json = 1;
            } else {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("verify", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                }
                return 3;
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("verify", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_verify(state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "platform-register")) {
        const char *state_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("platform-register", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_platform_register(state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "platform-unregister")) {
        const char *state_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("platform-unregister", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_platform_unregister(state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "uninstall-preview")) {
        const char *state_path = NULL;
        const char *components_csv = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--components");
            if (v) {
                components_csv = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--components") && i + 1 < argc) {
                components_csv = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
                continue;
            }
        }
        if (fmt && fmt[0] != '\0') {
            if (strcmp(fmt, "txt") == 0 || strcmp(fmt, "text") == 0) {
                opts.format_json = 0;
            } else if (strcmp(fmt, "json") == 0) {
                opts.format_json = 1;
            } else {
                if (opts.format_json) {
                    dsu_cli_json_error_envelope("uninstall-preview", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
                }
                return 3;
            }
        }
        if (!state_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("uninstall-preview", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_uninstall_preview(state_path, components_csv, &opts);
    }

    if (dsu_cli_streq(cmd, "report")) {
        const char *state_path = NULL;
        const char *out_dir = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--state");
            if (v) {
                state_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--out");
            if (v) {
                out_dir = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--state") && i + 1 < argc) {
                state_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                out_dir = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
                continue;
            }
        }
        if (!state_path || !out_dir) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("report", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_report(state_path, out_dir, fmt, &opts);
    }

    if (dsu_cli_streq(cmd, "rollback")) {
        const char *journal_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--journal");
            if (v) {
                journal_path = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--journal") && i + 1 < argc) {
                journal_path = argv[++i];
            }
        }
        if (!journal_path) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("rollback", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                dsu_cli_print_help_root(stderr);
            }
            return 3;
        }
        return dsu_cli_cmd_rollback(journal_path, &opts);
    }

    if (dsu_cli_streq(cmd, "export-log")) {
        const char *log_path = NULL;
        const char *out_path = NULL;
        const char *fmt = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
            v = dsu_cli_kv_value_inline(arg, "--log");
            if (v) {
                log_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--out");
            if (v) {
                out_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--format");
            if (v) {
                fmt = v;
                continue;
            }
            if (dsu_cli_streq(arg, "--log") && i + 1 < argc) {
                log_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                out_path = argv[++i];
                continue;
            }
            if (dsu_cli_streq(arg, "--format") && i + 1 < argc) {
                fmt = argv[++i];
            }
        }
        if (!log_path || !out_path || !fmt) {
            if (opts.format_json) {
                dsu_cli_json_error_envelope("export-log", 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
            } else {
                char *h[1];
                h[0] = "export-log";
                dsu_cli_print_help_command(stderr, 1, h);
            }
            return 3;
        }
        return dsu_cli_cmd_export_log(log_path, out_path, fmt, &opts);
    }

    if (opts.format_json) {
        dsu_cli_json_error_envelope(cmd, 3, DSU_STATUS_INVALID_ARGS, "invalid_args");
    } else {
        dsu_cli_print_help_root(stderr);
    }
    return 3;
}
