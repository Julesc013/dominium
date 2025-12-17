/*
FILE: source/dominium/setup/cli/dominium_setup_main.c
MODULE: Dominium Setup
PURPOSE: Minimal setup control-plane CLI for Plan S-1 (plan + dry-run).
*/
#include <stdio.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_execute.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"

#define DSU_CLI_NAME "dominium-setup"
#define DSU_CLI_VERSION "0.1.0"

typedef struct dsu_cli_opts_t {
    int deterministic;
    int json;
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
            "  %s plan --manifest <path> --out <planfile> --log <logfile> [--deterministic] [--json]\n"
            "  %s dry-run --plan <planfile> --log <logfile> [--deterministic] [--json]\n",
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
    dsu_resolved_t *resolved = NULL;
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
    st = dsu_resolve(ctx, manifest, &resolved);
    if (st != DSU_STATUS_SUCCESS) {
        goto done;
    }
    st = dsu_plan_build(ctx, manifest, resolved, &plan);
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
    if (resolved) dsu_resolved_destroy(ctx, resolved);
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
