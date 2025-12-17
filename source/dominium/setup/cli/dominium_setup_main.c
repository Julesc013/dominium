/*
FILE: source/dominium/setup/cli/dominium_setup_main.c
MODULE: Dominium Setup
PURPOSE: Minimal setup control-plane CLI for Plan S-1 (plan + dry-run).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_execute.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_state.h"
#include "dsu/dsu_txn.h"

#define DSU_CLI_NAME "dominium-setup"
#define DSU_CLI_VERSION "0.1.0"

typedef struct dsu_cli_opts_t {
    int deterministic;
    int json;
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
        case DSU_STATUS_INVALID_ARGS: return 2;
        case DSU_STATUS_IO_ERROR: return 3;
        case DSU_STATUS_PARSE_ERROR: return 4;
        case DSU_STATUS_UNSUPPORTED_VERSION: return 5;
        case DSU_STATUS_INTEGRITY_ERROR: return 6;
        case DSU_STATUS_INTERNAL_ERROR: return 7;
        case DSU_STATUS_MISSING_COMPONENT: return 8;
        case DSU_STATUS_UNSATISFIED_DEPENDENCY: return 9;
        case DSU_STATUS_VERSION_CONFLICT: return 10;
        case DSU_STATUS_EXPLICIT_CONFLICT: return 11;
        case DSU_STATUS_PLATFORM_INCOMPATIBLE: return 12;
        case DSU_STATUS_ILLEGAL_DOWNGRADE: return 13;
        case DSU_STATUS_INVALID_REQUEST: return 2;
        default: return 1;
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

static void dsu_cli_print_usage(FILE *out) {
    fprintf(out,
            "Usage:\n"
            "  %s version [--json]\n"
            "  %s manifest-validate --in <file> [--deterministic] [--json]\n"
            "  %s manifest-dump --in <file> --out <json> [--deterministic] [--json]\n"
            "  %s resolve --manifest <file> [--installed-state <file>] [--install|--upgrade|--repair|--uninstall] [--components a,b,c] [--scope portable|user|system] [--platform <triple>] [--exclude a,b,c] [--allow-prerelease] --json\n"
            "  %s plan --manifest <path> --out <planfile> --log <logfile> [--deterministic] [--json]\n"
            "  %s dry-run --plan <planfile> --log <logfile> [--deterministic] [--json]\n"
            "  %s install --plan <planfile> [--dry-run] [--deterministic] [--json]\n"
            "  %s uninstall --state <statefile> [--dry-run] [--deterministic] [--json]\n"
            "  %s verify --state <statefile> [--deterministic] [--json]\n"
            "  %s rollback --journal <journalfile> [--dry-run] [--deterministic] [--json]\n",
            DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME,
            DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME, DSU_CLI_NAME);
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

static int dsu_cli_cmd_version(int argc, char **argv, const dsu_cli_opts_t *opts) {
    (void)argc;
    (void)argv;
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "version"); fputc(',', stdout);
        fputs("\"name\":", stdout); dsu_cli_json_put_escaped(stdout, DSU_CLI_NAME); fputc(',', stdout);
        fputs("\"version\":", stdout); dsu_cli_json_put_escaped(stdout, DSU_CLI_VERSION);
        fputs("}\n", stdout);
    } else {
        fprintf(stdout, "%s %s\n", DSU_CLI_NAME, DSU_CLI_VERSION);
    }
    return 0;
}

static int dsu_cli_cmd_plan(const char *manifest_path,
                            const char *out_plan_path,
                            const char *out_log_path,
                            const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
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
    {
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        st = dsu_resolve_components(ctx, manifest, NULL, &req, &resolved);
        if (st != DSU_STATUS_SUCCESS) {
            goto done;
        }
    }
    st = dsu_plan_build(ctx, manifest, manifest_path, resolved, &plan);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_plan_write_file(ctx, plan, out_plan_path);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), out_log_path);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "plan"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "ok"); fputc(',', stdout);
        fputs("\"deterministic\":", stdout); fputs((opts->deterministic ? "true" : "false"), stdout); fputc(',', stdout);
        fputs("\"plan_file\":", stdout); dsu_cli_json_put_escaped(stdout, out_plan_path); fputc(',', stdout);
        fputs("\"log_file\":", stdout); dsu_cli_json_put_escaped(stdout, out_log_path); fputc(',', stdout);
        fprintf(stdout, "\"plan_id_hash32\":%lu,", (unsigned long)dsu_plan_id_hash32(plan));
        fputs("\"plan_id_hash64\":", stdout);
        {
            dsu_u64 id64 = dsu_plan_id_hash64(plan);
            unsigned long hi = (unsigned long)((id64 >> 32) & 0xFFFFFFFFu);
            unsigned long lo = (unsigned long)(id64 & 0xFFFFFFFFu);
            fprintf(stdout, "\"0x%08lx%08lx\",", hi, lo);
        }
        fprintf(stdout, "\"component_count\":%lu,", (unsigned long)dsu_plan_component_count(plan));
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
        fprintf(stdout, "components=%lu\n", (unsigned long)dsu_plan_component_count(plan));
        fprintf(stdout, "steps=%lu\n", (unsigned long)dsu_plan_step_count(plan));
        fprintf(stdout, "plan_file=%s\n", out_plan_path);
        fprintf(stdout, "log_file=%s\n", out_log_path);
    }

done:
    if (plan) dsu_plan_destroy(ctx, plan);
    if (resolved) dsu_resolve_result_destroy(ctx, resolved);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);

    if (st != DSU_STATUS_SUCCESS) {
        if (opts && opts->json) {
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "plan"); fputc(',', stdout);
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
    req.scope = scope;
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
    /* JSON output is required for this command. */
    fputc('{', stdout);
    fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "resolve"); fputc(',', stdout);
    fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS ? "ok" : "error")); fputc(',', stdout);
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
        fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_install_root(result)); fputc(',', stdout);
        fputs("\"manifest_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_resolve_result_manifest_digest64(result)); fputc(',', stdout);
        fputs("\"resolved_digest64\":", stdout); dsu_cli_json_put_u64_hex(stdout, dsu_resolve_result_resolved_digest64(result)); fputc(',', stdout);
    } else {
        fputs("\"product_id\":", stdout); dsu_cli_json_put_escaped(stdout, ""); fputc(',', stdout);
        fputs("\"product_version\":", stdout); dsu_cli_json_put_escaped(stdout, ""); fputc(',', stdout);
        fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, ""); fputc(',', stdout);
        fputs("\"manifest_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
        fputs("\"resolved_digest64\":", stdout); dsu_cli_json_put_escaped(stdout, "0x0000000000000000"); fputc(',', stdout);
    }

    if (st != DSU_STATUS_SUCCESS) {
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));
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
                dsu_resolve_log_code_t code = dsu_resolve_result_log_code(result, i);
                const char *name = "unknown";
                if (code == DSU_RESOLVE_LOG_SEED_USER) name = "seed_user";
                else if (code == DSU_RESOLVE_LOG_SEED_DEFAULT) name = "seed_default";
                else if (code == DSU_RESOLVE_LOG_ADD_DEPENDENCY) name = "add_dependency";
                else if (code == DSU_RESOLVE_LOG_CONFLICT) name = "conflict";
                else if (code == DSU_RESOLVE_LOG_PLATFORM_FILTER) name = "platform_filter";
                else if (code == DSU_RESOLVE_LOG_RECONCILE_INSTALLED) name = "reconcile_installed";
                dsu_cli_json_put_escaped(stdout, name);
            }
            fputc(',', stdout);
            fputs("\"a\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_log_a(result, i)); fputc(',', stdout);
            fputs("\"b\":", stdout); dsu_cli_json_put_escaped(stdout, dsu_resolve_result_log_b(result, i));
            fputc('}', stdout);
        }
    }
    fputs("]", stdout);

    fputs("}\n", stdout);

    if (result) dsu_resolve_result_destroy(ctx, result);
    if (installed) dsu_state_destroy(ctx, installed);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
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

    if (opts && opts->json) {
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
        if (opts && opts->json) {
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

static int dsu_cli_cmd_install(const char *plan_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_plan_t *plan = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;

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
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "install"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));        
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); fputs((opts && opts->dry_run) ? "true" : "false", stdout);
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
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (plan) dsu_plan_destroy(ctx, plan);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_uninstall(const char *state_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;

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
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "uninstall"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); fputs((opts && opts->dry_run) ? "true" : "false", stdout);
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
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

static int dsu_cli_cmd_verify(const char *state_path, const dsu_cli_opts_t *opts) {
    dsu_ctx_t *ctx = NULL;
    dsu_state_t *state = NULL;
    dsu_txn_options_t txn_opts;
    dsu_txn_result_t res;
    dsu_status_t st;

    dsu_txn_options_init(&txn_opts);
    dsu_txn_result_init(&res);

    st = dsu_cli_ctx_create(opts, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_state_load_file(ctx, state_path, &state);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_txn_verify_state(ctx, state, &txn_opts, &res);

done:
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "verify"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout);
        if (st == DSU_STATUS_SUCCESS || st == DSU_STATUS_INTEGRITY_ERROR) {
            fputc(',', stdout);
            fputs("\"state_file\":", stdout); dsu_cli_json_put_escaped(stdout, state_path); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.install_root); fputc(',', stdout);
            fprintf(stdout, "\"verified_ok\":%lu,", (unsigned long)res.verified_ok);
            fprintf(stdout, "\"verified_missing\":%lu,", (unsigned long)res.verified_missing);
            fprintf(stdout, "\"verified_mismatch\":%lu", (unsigned long)res.verified_mismatch);
        }
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "ok\n");
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (state) dsu_state_destroy(ctx, state);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
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
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "rollback"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d,", dsu_cli_exit_code(st));
        fputs("\"deterministic\":", stdout); fputs((opts && opts->deterministic) ? "true" : "false", stdout); fputc(',', stdout);
        fputs("\"dry_run\":", stdout); fputs((opts && opts->dry_run) ? "true" : "false", stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fputc(',', stdout);
            fputs("\"journal_file\":", stdout); dsu_cli_json_put_escaped(stdout, journal_path); fputc(',', stdout);
            fputs("\"journal_id\":", stdout); dsu_cli_json_put_u64_hex(stdout, res.journal_id); fputc(',', stdout);
            fputs("\"install_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.install_root); fputc(',', stdout);
            fputs("\"txn_root\":", stdout); dsu_cli_json_put_escaped(stdout, res.txn_root); fputc(',', stdout);
            fprintf(stdout, "\"journal_entry_count\":%lu,", (unsigned long)res.journal_entry_count);
            fprintf(stdout, "\"commit_progress_before\":%lu", (unsigned long)res.commit_progress);
        }
        fputs("}\n", stdout);
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

static int dsu_cli_cmd_manifest_validate(const char *in_path, const dsu_cli_opts_t *opts) {
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
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "manifest-validate"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "\"content_digest32\":%lu,", (unsigned long)dsu_manifest_content_digest32(manifest));
            fputs("\"content_digest64\":", stdout);
            {
                dsu_u64 d64 = dsu_manifest_content_digest64(manifest);
                unsigned long hi = (unsigned long)((d64 >> 32) & 0xFFFFFFFFu);
                unsigned long lo = (unsigned long)(d64 & 0xFFFFFFFFu);
                fprintf(stdout, "\"0x%08lx%08lx\",", hi, lo);
            }
        }
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d", dsu_cli_exit_code(st));
        fputs("}\n", stdout);
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

static int dsu_cli_cmd_manifest_dump(const char *in_path, const char *out_path, const dsu_cli_opts_t *opts) {
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
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }

    st = dsu_manifest_write_json_file(ctx, manifest, out_path);

done:
    if (opts && opts->json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "manifest-dump"); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "ok" : "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, (st == DSU_STATUS_SUCCESS) ? "" : dsu_cli_status_name(st)); fputc(',', stdout);
        fprintf(stdout, "\"exit_code\":%d", dsu_cli_exit_code(st));
        fputs("}\n", stdout);
    } else {
        if (st == DSU_STATUS_SUCCESS) {
            fprintf(stdout, "wrote %s\n", out_path ? out_path : "");
        } else {
            fprintf(stderr, "error: %s\n", dsu_cli_status_name(st));
        }
    }

    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    return dsu_cli_exit_code(st);
}

int main(int argc, char **argv) {
    dsu_cli_opts_t opts;
    const char *cmd;
    int i;

    opts.deterministic = 1;
    opts.json = 0;
    opts.dry_run = 0;

    if (argc < 2) {
        dsu_cli_print_usage(stderr);
        return 2;
    }

    cmd = argv[1];

    /* Global flags after command. */
    for (i = 2; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) continue;
        if (dsu_cli_streq(arg, "--json")) {
            opts.json = 1;
        } else if (dsu_cli_streq(arg, "--dry-run")) {
            opts.dry_run = 1;
        } else if (dsu_cli_streq(arg, "--deterministic")) {
            opts.deterministic = 1;
        } else if (dsu_cli_streq(arg, "--nondeterministic") || dsu_cli_streq(arg, "--non-deterministic")) {
            opts.deterministic = 0;
        }
    }

    if (dsu_cli_streq(cmd, "version")) {
        return dsu_cli_cmd_version(argc - 1, argv + 1, &opts);
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "manifest-validate"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_manifest_validate(in_path, &opts);
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "manifest-dump"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_manifest_dump(in_path, out_path, &opts);
    }

    if (dsu_cli_streq(cmd, "resolve")) {
        const char *manifest_path = NULL;
        const char *installed_state_path = NULL;
        const char *components_csv = NULL;
        const char *exclude_csv = NULL;
        const char *scope_str = NULL;
        const char *platform_str = NULL;
        int allow_prerelease = 0;
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
            v = dsu_cli_kv_value_inline(arg, "--installed-state");
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
            v = dsu_cli_kv_value_inline(arg, "--platform");
            if (v) {
                platform_str = v;
                continue;
            }

            if (dsu_cli_streq(arg, "--manifest") && i + 1 < argc) {
                manifest_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--installed-state") && i + 1 < argc) {
                installed_state_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--components") && i + 1 < argc) {
                components_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--exclude") && i + 1 < argc) {
                exclude_csv = argv[++i];
            } else if (dsu_cli_streq(arg, "--scope") && i + 1 < argc) {
                scope_str = argv[++i];
            } else if (dsu_cli_streq(arg, "--platform") && i + 1 < argc) {
                platform_str = argv[++i];
            } else if (dsu_cli_streq(arg, "--allow-prerelease")) {
                allow_prerelease = 1;
            } else if (dsu_cli_streq(arg, "--install")) {
                if (op_set) ok = 0;
                op_set = 1;
                op = DSU_RESOLVE_OPERATION_INSTALL;
            } else if (dsu_cli_streq(arg, "--upgrade")) {
                if (op_set) ok = 0;
                op_set = 1;
                op = DSU_RESOLVE_OPERATION_UPGRADE;
            } else if (dsu_cli_streq(arg, "--repair")) {
                if (op_set) ok = 0;
                op_set = 1;
                op = DSU_RESOLVE_OPERATION_REPAIR;
            } else if (dsu_cli_streq(arg, "--uninstall")) {
                if (op_set) ok = 0;
                op_set = 1;
                op = DSU_RESOLVE_OPERATION_UNINSTALL;
            }
        }

        if (!ok || !manifest_path) {
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "resolve"); fputc(',', stdout);
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
            fputs("}\n", stdout);
            return 2;
        }
        if (scope_str && !dsu_cli_parse_scope(scope_str, &scope)) {
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "resolve"); fputc(',', stdout);
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
            fputs("}\n", stdout);
            return 2;
        }
        if (components_csv && !dsu_cli_csv_list_parse(components_csv, &components)) {
            dsu_cli_csv_list_free(&components);
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "resolve"); fputc(',', stdout);
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
            fputs("}\n", stdout);
            return 2;
        }
        if (exclude_csv && !dsu_cli_csv_list_parse(exclude_csv, &exclude)) {
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            fputc('{', stdout);
            fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "resolve"); fputc(',', stdout);
            fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
            fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
            fputs("}\n", stdout);
            return 2;
        }

        {
            int rc = dsu_cli_cmd_resolve(manifest_path,
                                         installed_state_path,
                                         op,
                                         &components,
                                         &exclude,
                                         scope,
                                         platform_str,
                                         allow_prerelease,
                                         &opts);
            dsu_cli_csv_list_free(&components);
            dsu_cli_csv_list_free(&exclude);
            return rc;
        }
    }

    if (dsu_cli_streq(cmd, "plan")) {
        const char *manifest_path = NULL;
        const char *out_plan_path = NULL;
        const char *out_log_path = NULL;

        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;

            v = dsu_cli_kv_value_inline(arg, "--manifest");
            if (v) {
                manifest_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--out");
            if (v) {
                out_plan_path = v;
                continue;
            }
            v = dsu_cli_kv_value_inline(arg, "--log");
            if (v) {
                out_log_path = v;
                continue;
            }

            if (dsu_cli_streq(arg, "--manifest") && i + 1 < argc) {
                manifest_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--out") && i + 1 < argc) {
                out_plan_path = argv[++i];
            } else if (dsu_cli_streq(arg, "--log") && i + 1 < argc) {
                out_log_path = argv[++i];
            }
        }

        if (!manifest_path || !out_plan_path || !out_log_path) {
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "plan"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_plan(manifest_path, out_plan_path, out_log_path, &opts);
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "dry-run"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_dry_run(plan_path, out_log_path, &opts);
    }

    if (dsu_cli_streq(cmd, "install")) {
        const char *plan_path = NULL;
        for (i = 2; i < argc; ++i) {
            const char *arg = argv[i];
            const char *v;
            if (!arg) continue;
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "install"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_install(plan_path, &opts);
    }

    if (dsu_cli_streq(cmd, "uninstall")) {
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "uninstall"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_uninstall(state_path, &opts);
    }

    if (dsu_cli_streq(cmd, "verify")) {
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "verify"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_verify(state_path, &opts);
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
            if (opts.json) {
                fputc('{', stdout);
                fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, "rollback"); fputc(',', stdout);
                fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
                fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
                fputs("}\n", stdout);
            } else {
                dsu_cli_print_usage(stderr);
            }
            return 2;
        }
        return dsu_cli_cmd_rollback(journal_path, &opts);
    }

    if (opts.json) {
        fputc('{', stdout);
        fputs("\"command\":", stdout); dsu_cli_json_put_escaped(stdout, cmd); fputc(',', stdout);
        fputs("\"status\":", stdout); dsu_cli_json_put_escaped(stdout, "error"); fputc(',', stdout);
        fputs("\"error\":", stdout); dsu_cli_json_put_escaped(stdout, "invalid_args");
        fputs("}\n", stdout);
    } else {
        dsu_cli_print_usage(stderr);
    }
    return 2;
}
