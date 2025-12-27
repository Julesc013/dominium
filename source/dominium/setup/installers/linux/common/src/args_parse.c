/*
FILE: source/dominium/setup/installers/linux/common/src/args_parse.c
MODULE: Dominium Setup Linux
PURPOSE: Parse CLI arguments for Linux setup frontends.
*/
#include "dsu_linux_args.h"

#include <stdlib.h>
#include <string.h>

static int streq(const char *a, const char *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    return strcmp(a, b) == 0;
}

static const char *arg_value_inline(const char *arg, const char *key) {
    size_t n;
    if (!arg || !key) return NULL;
    n = strlen(key);
    if (strncmp(arg, key, n) != 0) return NULL;
    if (arg[n] != '=') return NULL;
    return arg + n + 1;
}

int dsu_linux_args_parse(int argc, char **argv, dsu_linux_cli_args_t *out_cli) {
    dsu_linux_cli_args_t cli;
    int i;

    if (!out_cli) {
        return 0;
    }
    memset(&cli, 0, sizeof(cli));
    cli.deterministic = 1;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        const char *v;
        if (!arg) continue;

        if (streq(arg, "--help") || streq(arg, "-h")) {
            cli.want_help = 1;
            continue;
        }
        if (streq(arg, "--version")) {
            cli.want_version = 1;
            continue;
        }
        if (streq(arg, "--json")) {
            cli.want_json = 1;
            continue;
        }
        if (streq(arg, "--quiet")) {
            cli.quiet = 1;
            continue;
        }
        if (streq(arg, "--dry-run")) {
            cli.dry_run = 1;
            continue;
        }
        if (streq(arg, "--non-interactive")) {
            cli.non_interactive = 1;
            continue;
        }
        if (streq(arg, "--defaults")) {
            cli.use_defaults = 1;
            continue;
        }
        if (streq(arg, "--export-invocation")) {
            cli.export_invocation = 1;
            continue;
        }
        if (streq(arg, "--apply-invocation")) {
            cli.apply_invocation = 1;
            continue;
        }
        if (streq(arg, "--plan")) {
            cli.run_plan = 1;
            if (i + 1 < argc && argv[i + 1] && argv[i + 1][0] != '-') {
                cli.plan_path = argv[++i];
            }
            continue;
        }
        if (streq(arg, "--apply")) {
            cli.run_apply = 1;
            continue;
        }
        if (streq(arg, "--offline")) {
            cli.policy_offline = 1;
            continue;
        }
        if (streq(arg, "--allow-prerelease")) {
            cli.policy_allow_prerelease = 1;
            continue;
        }
        if (streq(arg, "--legacy")) {
            cli.policy_legacy = 1;
            continue;
        }
        if (streq(arg, "--shortcuts")) {
            cli.policy_shortcuts = 1;
            continue;
        }
        if (streq(arg, "--file-assoc")) {
            cli.policy_file_assoc = 1;
            continue;
        }
        if (streq(arg, "--url-handlers")) {
            cli.policy_url_handlers = 1;
            continue;
        }

        v = arg_value_inline(arg, "--manifest");
        if (v) { cli.manifest_path = v; continue; }
        v = arg_value_inline(arg, "--state");
        if (v) { cli.state_path = v; continue; }
        v = arg_value_inline(arg, "--invocation");
        if (v) { cli.invocation_path = v; continue; }
        v = arg_value_inline(arg, "--plan");
        if (v) { cli.plan_path = v; continue; }
        v = arg_value_inline(arg, "--log");
        if (v) { cli.log_path = v; continue; }
        v = arg_value_inline(arg, "--components");
        if (v) { cli.components_csv = v; continue; }
        v = arg_value_inline(arg, "--exclude");
        if (v) { cli.exclude_csv = v; continue; }
        v = arg_value_inline(arg, "--scope");
        if (v) { cli.scope = v; continue; }
        v = arg_value_inline(arg, "--op");
        if (v) { cli.operation = v; continue; }
        v = arg_value_inline(arg, "--platform");
        if (v) { cli.platform = v; continue; }
        v = arg_value_inline(arg, "--out");
        if (v) { cli.out_path = v; continue; }
        v = arg_value_inline(arg, "--install-root");
        if (v) { cli.install_root = v; continue; }
        v = arg_value_inline(arg, "--path");
        if (v) { cli.install_root = v; continue; }
        v = arg_value_inline(arg, "--ui-mode");
        if (v) { cli.ui_mode = v; continue; }
        v = arg_value_inline(arg, "--frontend-id");
        if (v) { cli.frontend_id = v; continue; }
        v = arg_value_inline(arg, "--deterministic");
        if (v) { cli.deterministic = atoi(v) != 0; continue; }

        if (streq(arg, "--manifest") && i + 1 < argc) {
            cli.manifest_path = argv[++i];
        } else if (streq(arg, "--state") && i + 1 < argc) {
            cli.state_path = argv[++i];
        } else if (streq(arg, "--invocation") && i + 1 < argc) {
            cli.invocation_path = argv[++i];
        } else if (streq(arg, "--plan") && i + 1 < argc) {
            cli.plan_path = argv[++i];
        } else if (streq(arg, "--log") && i + 1 < argc) {
            cli.log_path = argv[++i];
        } else if (streq(arg, "--components") && i + 1 < argc) {
            cli.components_csv = argv[++i];
        } else if (streq(arg, "--exclude") && i + 1 < argc) {
            cli.exclude_csv = argv[++i];
        } else if (streq(arg, "--scope") && i + 1 < argc) {
            cli.scope = argv[++i];
        } else if (streq(arg, "--op") && i + 1 < argc) {
            cli.operation = argv[++i];
        } else if (streq(arg, "--platform") && i + 1 < argc) {
            cli.platform = argv[++i];
        } else if (streq(arg, "--out") && i + 1 < argc) {
            cli.out_path = argv[++i];
        } else if (streq(arg, "--install-root") && i + 1 < argc) {
            cli.install_root = argv[++i];
        } else if (streq(arg, "--path") && i + 1 < argc) {
            cli.install_root = argv[++i];
        } else if (streq(arg, "--ui-mode") && i + 1 < argc) {
            cli.ui_mode = argv[++i];
        } else if (streq(arg, "--frontend-id") && i + 1 < argc) {
            cli.frontend_id = argv[++i];
        } else if (streq(arg, "--deterministic") && i + 1 < argc) {
            cli.deterministic = atoi(argv[++i]) != 0;
        }
    }

    *out_cli = cli;
    return 1;
}
