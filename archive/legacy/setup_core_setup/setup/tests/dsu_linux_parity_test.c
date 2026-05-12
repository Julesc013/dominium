/*
FILE: source/dominium/setup/tests/dsu_linux_parity_test.c
MODULE: Dominium Setup
PURPOSE: Linux TUI/CLI parity checks for invocation and plan digests.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__unix__) || defined(__APPLE__)
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_invocation.h"
#include "dsu/dsu_plan.h"

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int run_cmd(const char *cmd) {
    int rc;
    if (!cmd) return 0;
    rc = system(cmd);
    return rc == 0;
}

static const char *default_platform(void) {
#if defined(__aarch64__)
    return "linux-arm64";
#elif defined(__x86_64__) || defined(__amd64__)
    return "linux-x64";
#elif defined(__i386__)
    return "linux-x86";
#else
    return "linux-x64";
#endif
}

static int mkdir_best_effort(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    if (!path || !path[0]) return 0;
    if (mkdir(path, 0755) == 0) return 1;
    if (errno == EEXIST) return 1;
    return 0;
#else
    (void)path;
    return 0;
#endif
}

int main(int argc, char **argv) {
    const char *cli_path;
    const char *tui_path;
    const char *root;
    const char *mode;
    char workdir[256];
    char workdir_abs[1024];
    char cwd[1024];
    char manifest_path[1024];
    char install_root[1024];
    char cli_inv[1024];
    char tui_inv[1024];
    char cli_plan[1024];
    char tui_plan[1024];
    char cmd[4096];
    const char *platform;
    int ok = 1;

    if (argc < 5) {
        fprintf(stderr, "usage: dsu_linux_parity_test <cli> <tui> <test-root> <invocation|plan>\n");
        return 1;
    }

    cli_path = argv[1];
    tui_path = argv[2];
    root = argv[3];
    mode = argv[4];

    platform = default_platform();
    snprintf(workdir, sizeof(workdir), "linux_parity_%lu", (unsigned long)getpid());
    ok &= expect(mkdir_best_effort(workdir), "mkdir workdir");
    if (!getcwd(cwd, sizeof(cwd))) {
        fprintf(stderr, "failed to getcwd\n");
        return 1;
    }
    snprintf(workdir_abs, sizeof(workdir_abs), "%s/%s", cwd, workdir);
    snprintf(manifest_path, sizeof(manifest_path), "%s/fixtures/manifests/minimal.dsumanifest", root);
    snprintf(install_root, sizeof(install_root), "%s/install_root", workdir_abs);
    ok &= expect(mkdir_best_effort(install_root), "mkdir install_root");

    snprintf(cli_inv, sizeof(cli_inv), "%s/cli_inv.dsuinv", workdir_abs);
    snprintf(tui_inv, sizeof(tui_inv), "%s/tui_inv.dsuinv", workdir_abs);
    snprintf(cli_plan, sizeof(cli_plan), "%s/cli_plan.dsuplan", workdir_abs);
    snprintf(tui_plan, sizeof(tui_plan), "%s/tui_plan.dsuplan", workdir_abs);

    snprintf(cmd, sizeof(cmd),
             "\"%s\" --deterministic 1 export-invocation --manifest \"%s\" --op install --scope portable --platform %s --install-root \"%s\" --ui-mode cli --frontend-id cli-linux --out \"%s\"",
             cli_path, manifest_path, platform, install_root, cli_inv);
    ok &= expect(run_cmd(cmd), "cli export invocation");

    snprintf(cmd, sizeof(cmd),
             "\"%s\" --non-interactive --manifest \"%s\" --op install --scope portable --platform %s --install-root \"%s\" --export-invocation --out \"%s\"",
             tui_path, manifest_path, platform, install_root, tui_inv);
    ok &= expect(run_cmd(cmd), "tui export invocation");
    if (!ok) return 1;

    {
        dsu_ctx_t *ctx = NULL;
        dsu_config_t cfg;
        dsu_callbacks_t cbs;
        dsu_invocation_t *inv_cli = NULL;
        dsu_invocation_t *inv_tui = NULL;
        dsu_status_t st;
        dsu_u64 d_cli;
        dsu_u64 d_tui;

        dsu_config_init(&cfg);
        dsu_callbacks_init(&cbs);
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
        st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
        ok &= expect(st == DSU_STATUS_SUCCESS && ctx != NULL, "ctx create");

        st = dsu_invocation_load(ctx, cli_inv, &inv_cli);
        ok &= expect(st == DSU_STATUS_SUCCESS && inv_cli != NULL, "load cli invocation");
        st = dsu_invocation_load(ctx, tui_inv, &inv_tui);
        ok &= expect(st == DSU_STATUS_SUCCESS && inv_tui != NULL, "load tui invocation");
        if (ok) {
            ok &= expect(dsu_invocation_validate(inv_cli) == DSU_STATUS_SUCCESS, "validate cli invocation");
            ok &= expect(dsu_invocation_validate(inv_tui) == DSU_STATUS_SUCCESS, "validate tui invocation");
            d_cli = dsu_invocation_digest(inv_cli);
            d_tui = dsu_invocation_digest(inv_tui);
            ok &= expect(d_cli == d_tui, "invocation digest parity");
        }
        if (inv_cli) dsu_invocation_destroy(ctx, inv_cli);
        if (inv_tui) dsu_invocation_destroy(ctx, inv_tui);
        if (ctx) dsu_ctx_destroy(ctx);
    }

    if (strcmp(mode, "invocation") == 0) {
        return ok ? 0 : 1;
    }
    if (strcmp(mode, "plan") != 0) {
        fprintf(stderr, "unknown mode: %s\n", mode ? mode : "");
        return 1;
    }

    snprintf(cmd, sizeof(cmd),
             "\"%s\" --deterministic 1 plan --manifest \"%s\" --invocation \"%s\" --out \"%s\"",
             cli_path, manifest_path, cli_inv, cli_plan);
    ok &= expect(run_cmd(cmd), "cli plan");

    snprintf(cmd, sizeof(cmd),
             "\"%s\" --deterministic 1 plan --manifest \"%s\" --invocation \"%s\" --out \"%s\"",
             cli_path, manifest_path, tui_inv, tui_plan);
    ok &= expect(run_cmd(cmd), "tui plan via cli");

    {
        dsu_ctx_t *ctx = NULL;
        dsu_config_t cfg;
        dsu_callbacks_t cbs;
        dsu_plan_t *plan_cli = NULL;
        dsu_plan_t *plan_tui = NULL;
        dsu_status_t st;
        dsu_u64 h_cli;
        dsu_u64 h_tui;

        dsu_config_init(&cfg);
        dsu_callbacks_init(&cbs);
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
        st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
        ok &= expect(st == DSU_STATUS_SUCCESS && ctx != NULL, "ctx create plan");

        st = dsu_plan_read_file(ctx, cli_plan, &plan_cli);
        ok &= expect(st == DSU_STATUS_SUCCESS && plan_cli != NULL, "load cli plan");
        st = dsu_plan_read_file(ctx, tui_plan, &plan_tui);
        ok &= expect(st == DSU_STATUS_SUCCESS && plan_tui != NULL, "load tui plan");
        if (ok) {
            h_cli = dsu_plan_id_hash64(plan_cli);
            h_tui = dsu_plan_id_hash64(plan_tui);
            ok &= expect(h_cli == h_tui, "plan digest parity");
        }

        if (plan_cli) dsu_plan_destroy(ctx, plan_cli);
        if (plan_tui) dsu_plan_destroy(ctx, plan_tui);
        if (ctx) dsu_ctx_destroy(ctx);
    }

    return ok ? 0 : 1;
}
