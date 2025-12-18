/*
FILE: source/dominium/setup/adapters/windows/dominium_setup_adapter_windows.c
MODULE: Dominium Setup
PURPOSE: Windows setup adapter entrypoint (Plan S-6).
*/
#if !defined(_WIN32)
#error "dominium_setup_adapter_windows.c is Windows-only"
#endif

#include "dsu_windows_platform_iface.h"

#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_platform_iface.h"
#include "dsu/dsu_state.h"
#include "dsu/dsu_txn.h"

#include <stdio.h>
#include <string.h>

static void dsu__adapter_log(void *user, dsu_u32 event_id, dsu_u8 severity, dsu_u8 category, dsu_u32 timestamp, const char *message) {
    int quiet = user ? *(const int *)user : 0;
    (void)event_id;
    (void)severity;
    (void)category;
    (void)timestamp;
    if (quiet) return;
    if (message && message[0] != '\0') {
        fputs(message, stdout);
        fputc('\n', stdout);
    }
}

static void dsu__adapter_progress(void *user, dsu_u32 current, dsu_u32 total, const char *phase) {
    int quiet = user ? *(const int *)user : 0;
    (void)current;
    (void)total;
    if (quiet) return;
    if (phase && phase[0] != '\0') {
        fputs(phase, stdout);
        fputc('\n', stdout);
    }
}

static int dsu__streq(const char *a, const char *b) {
    if (!a || !b) return 0;
    return strcmp(a, b) == 0;
}

static void dsu__usage(void) {
    fprintf(stderr,
            "dominium-setup-win (Plan S-6)\n"
            "\n"
            "Commands:\n"
            "  install --plan <file> [--dry-run] [--deterministic] [--log <file>] [/quiet|/passive]\n"
            "  uninstall --state <file> [--dry-run] [--deterministic] [--log <file>] [/quiet|/passive]\n"
            "  platform-register --state <file> [--deterministic] [--log <file>] [/quiet|/passive]\n"
            "  platform-unregister --state <file> [--deterministic] [--log <file>] [/quiet|/passive]\n");
}

int main(int argc, char **argv) {
    const char *cmd = NULL;
    const char *plan_path = NULL;
    const char *state_path = NULL;
    const char *log_path = NULL;
    int quiet = 0;
    int passive = 0;
    int deterministic = 0;
    int dry_run = 0;
    int i;
    int exit_code = 1;

    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_platform_iface_t iface;
    dsu_windows_platform_user_t user;
    dsu_status_t st = DSU_STATUS_SUCCESS;

    memset(&user, 0, sizeof(user));

    for (i = 1; i < argc; ++i) {
        const char *a = argv[i];
        if (!a) continue;
        if (dsu__streq(a, "/quiet")) {
            quiet = 1;
            continue;
        }
        if (dsu__streq(a, "/passive")) {
            passive = 1;
            continue;
        }
        if (dsu__streq(a, "--deterministic")) {
            deterministic = 1;
            continue;
        }
        if (dsu__streq(a, "--dry-run")) {
            dry_run = 1;
            continue;
        }
        if (dsu__streq(a, "--plan") && i + 1 < argc) {
            plan_path = argv[++i];
            continue;
        }
        if (dsu__streq(a, "--state") && i + 1 < argc) {
            state_path = argv[++i];
            continue;
        }
        if (dsu__streq(a, "--log") && i + 1 < argc) {
            log_path = argv[++i];
            continue;
        }
        if (!cmd) {
            cmd = a;
            continue;
        }
    }

    if (!cmd) {
        dsu__usage();
        return 2;
    }
    if (passive) {
        quiet = 0;
    }

    dsu_config_init(&cfg);
    if (deterministic) {
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    }
    dsu_callbacks_init(&cbs);
    cbs.log = dsu__adapter_log;
    cbs.progress = dsu__adapter_progress;

    st = dsu_ctx_create(&cfg, &cbs, &quiet, &ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_reset_audit_log(ctx);
    if (st != DSU_STATUS_SUCCESS) goto done;

    st = dsu_windows_platform_iface_init(&iface);
    if (st != DSU_STATUS_SUCCESS) goto done;
    st = dsu_ctx_set_platform_iface(ctx, &iface, &user);
    if (st != DSU_STATUS_SUCCESS) goto done;

    if (dsu__streq(cmd, "install")) {
        dsu_plan_t *plan = NULL;
        dsu_txn_options_t txn_opts;
        dsu_txn_result_t res;
        dsu_txn_options_init(&txn_opts);
        dsu_txn_result_init(&res);
        if (!plan_path) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        st = dsu_plan_read_file(ctx, plan_path, &plan);
        if (st != DSU_STATUS_SUCCESS) goto done;
        txn_opts.dry_run = (dsu_bool)(dry_run ? 1 : 0);
        st = dsu_txn_apply_plan(ctx, plan, &txn_opts, &res);
        dsu_plan_destroy(ctx, plan);
    } else if (dsu__streq(cmd, "uninstall")) {
        dsu_state_t *state = NULL;
        dsu_txn_options_t txn_opts;
        dsu_txn_result_t res;
        dsu_txn_options_init(&txn_opts);
        dsu_txn_result_init(&res);
        if (!state_path) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        st = dsu_state_load_file(ctx, state_path, &state);
        if (st != DSU_STATUS_SUCCESS) goto done;
        txn_opts.dry_run = (dsu_bool)(dry_run ? 1 : 0);
        st = dsu_txn_uninstall_state(ctx, state, state_path, &txn_opts, &res);
        dsu_state_destroy(ctx, state);
    } else if (dsu__streq(cmd, "platform-register")) {
        dsu_state_t *state = NULL;
        if (!state_path) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        st = dsu_state_load_file(ctx, state_path, &state);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_platform_register_from_state(ctx, state);
        dsu_state_destroy(ctx, state);
    } else if (dsu__streq(cmd, "platform-unregister")) {
        dsu_state_t *state = NULL;
        if (!state_path) {
            st = DSU_STATUS_INVALID_ARGS;
            goto done;
        }
        st = dsu_state_load_file(ctx, state_path, &state);
        if (st != DSU_STATUS_SUCCESS) goto done;
        st = dsu_platform_unregister_from_state(ctx, state);
        dsu_state_destroy(ctx, state);
    } else {
        st = DSU_STATUS_INVALID_ARGS;
    }

done:
    if (ctx && log_path && log_path[0] != '\0') {
        dsu_status_t st2 = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), log_path);
        if (st == DSU_STATUS_SUCCESS && st2 != DSU_STATUS_SUCCESS) {
            st = st2;
        }
    }
    if (ctx) {
        dsu_ctx_destroy(ctx);
    }
    exit_code = (st == DSU_STATUS_SUCCESS) ? 0 : 1;
    if (st != DSU_STATUS_SUCCESS && !quiet) {
        fprintf(stderr, "error: %d\n", (int)st);
    }
    return exit_code;
}

