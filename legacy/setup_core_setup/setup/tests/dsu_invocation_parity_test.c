/*
FILE: source/dominium/setup/tests/dsu_invocation_parity_test.c
MODULE: Dominium Setup
PURPOSE: Parity tests for invocation digests, plan digests, and legacy isolation.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_invocation.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static char *dup_str(const char *s) {
    size_t n;
    char *p;
    if (!s) {
        s = "";
    }
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) {
        return NULL;
    }
    if (n) {
        memcpy(p, s, n);
    }
    p[n] = '\0';
    return p;
}

static int inv_set_single_list(char ***out_items, dsu_u32 *out_count, const char *value) {
    char **items;
    if (!out_items || !out_count) {
        return 0;
    }
    *out_items = NULL;
    *out_count = 0u;
    items = (char **)malloc(sizeof(*items));
    if (!items) {
        return 0;
    }
    items[0] = dup_str(value);
    if (!items[0]) {
        free(items);
        return 0;
    }
    *out_items = items;
    *out_count = 1u;
    return 1;
}

static int build_invocation(dsu_invocation_t *inv,
                            dsu_invocation_operation_t op,
                            dsu_invocation_scope_t scope,
                            const char *platform,
                            const char *install_root,
                            const char *ui_mode,
                            const char *frontend_id,
                            dsu_u32 policy_flags,
                            const char *component_id) {
    if (!inv) {
        return 0;
    }
    dsu_invocation_init(inv);
    inv->operation = (dsu_u8)op;
    inv->scope = (dsu_u8)scope;
    inv->policy_flags = policy_flags;

    inv->platform_triple = dup_str(platform);
    inv->ui_mode = dup_str(ui_mode);
    inv->frontend_id = dup_str(frontend_id);
    if (!inv->platform_triple || !inv->ui_mode || !inv->frontend_id) {
        return 0;
    }

    if (install_root) {
        if (!inv_set_single_list(&inv->install_roots, &inv->install_root_count, install_root)) {
            return 0;
        }
    }

    if (component_id) {
        if (!inv_set_single_list(&inv->selected_components, &inv->selected_component_count, component_id)) {
            return 0;
        }
    }
    return 1;
}

static int components_match(const dsu_resolve_result_t *a, const dsu_resolve_result_t *b) {
    dsu_u32 i;
    dsu_u32 count_a;
    dsu_u32 count_b;
    if (!a || !b) {
        return 0;
    }
    count_a = dsu_resolve_result_component_count(a);
    count_b = dsu_resolve_result_component_count(b);
    if (count_a != count_b) {
        return 0;
    }
    for (i = 0u; i < count_a; ++i) {
        const char *id_a = dsu_resolve_result_component_id(a, i);
        const char *id_b = dsu_resolve_result_component_id(b, i);
        const char *ver_a = dsu_resolve_result_component_version(a, i);
        const char *ver_b = dsu_resolve_result_component_version(b, i);
        if (!id_a || !id_b || !ver_a || !ver_b) {
            return 0;
        }
        if (strcmp(id_a, id_b) != 0) {
            return 0;
        }
        if (strcmp(ver_a, ver_b) != 0) {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv) {
    const char *root = (argc > 1) ? argv[1] : ".";
    char manifest_path[1024];
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_plan_t *plan_msi = NULL;
    dsu_plan_t *plan_exe = NULL;
    dsu_resolve_result_t *res_portable = NULL;
    dsu_resolve_result_t *res_user = NULL;
    dsu_invocation_t inv_msi;
    dsu_invocation_t inv_exe;
    dsu_invocation_t inv_cli;
    dsu_invocation_t inv_portable;
    dsu_invocation_t inv_user;
    dsu_invocation_t inv_legacy_bad;
    dsu_invocation_t inv_legacy_ok;
    dsu_status_t st;
    dsu_u64 digest_msi;
    dsu_u64 digest_exe;
    dsu_u64 digest_cli;
    int ok = 1;

    memset(&inv_msi, 0, sizeof(inv_msi));
    memset(&inv_exe, 0, sizeof(inv_exe));
    memset(&inv_cli, 0, sizeof(inv_cli));
    memset(&inv_portable, 0, sizeof(inv_portable));
    memset(&inv_user, 0, sizeof(inv_user));
    memset(&inv_legacy_bad, 0, sizeof(inv_legacy_bad));
    memset(&inv_legacy_ok, 0, sizeof(inv_legacy_ok));

    sprintf(manifest_path, "%s/fixtures/manifests/minimal.dsumanifest", root);

    {
        dsu_config_t cfg;
        dsu_callbacks_t cbs;
        dsu_config_init(&cfg);
        dsu_callbacks_init(&cbs);
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
        st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &manifest);
    ok &= expect(st == DSU_STATUS_SUCCESS && manifest != NULL, "manifest load");
    if (!ok) goto done;

    ok &= expect(build_invocation(&inv_msi,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "gui",
                                  "msi",
                                  DSU_INVOCATION_POLICY_DETERMINISTIC,
                                  "core"),
                 "build msi invocation");
    ok &= expect(build_invocation(&inv_exe,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "gui",
                                  "exe",
                                  DSU_INVOCATION_POLICY_DETERMINISTIC,
                                  "core"),
                 "build exe invocation");
    ok &= expect(build_invocation(&inv_cli,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "cli",
                                  "cli",
                                  DSU_INVOCATION_POLICY_DETERMINISTIC,
                                  "core"),
                 "build cli invocation");
    if (!ok) goto done;

    ok &= expect(dsu_invocation_validate(&inv_msi) == DSU_STATUS_SUCCESS, "validate msi invocation");
    ok &= expect(dsu_invocation_validate(&inv_exe) == DSU_STATUS_SUCCESS, "validate exe invocation");
    ok &= expect(dsu_invocation_validate(&inv_cli) == DSU_STATUS_SUCCESS, "validate cli invocation");
    if (!ok) goto done;

    digest_msi = dsu_invocation_digest(&inv_msi);
    digest_exe = dsu_invocation_digest(&inv_exe);
    digest_cli = dsu_invocation_digest(&inv_cli);

    ok &= expect(digest_msi != 0u, "msi invocation digest non-zero");
    ok &= expect(digest_msi == digest_exe, "msi vs exe invocation digest parity");
    ok &= expect(digest_msi == digest_cli, "cli vs gui invocation digest parity");
    if (!ok) goto done;

    st = dsu_plan_build_from_invocation(ctx, manifest, manifest_path, NULL, &inv_msi, &plan_msi);
    ok &= expect(st == DSU_STATUS_SUCCESS && plan_msi != NULL, "plan build msi");
    st = dsu_plan_build_from_invocation(ctx, manifest, manifest_path, NULL, &inv_exe, &plan_exe);
    ok &= expect(st == DSU_STATUS_SUCCESS && plan_exe != NULL, "plan build exe");
    ok &= expect(dsu_plan_id_hash64(plan_msi) == dsu_plan_id_hash64(plan_exe), "plan digest parity");
    ok &= expect(dsu_plan_invocation_digest64(plan_msi) == dsu_plan_invocation_digest64(plan_exe), "plan invocation digest parity");
    ok &= expect(dsu_plan_invocation_digest64(plan_msi) == digest_msi, "plan embeds invocation digest");
    if (!ok) goto done;

    ok &= expect(build_invocation(&inv_portable,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_PORTABLE,
                                  "any-any",
                                  "install_portable",
                                  "cli",
                                  "zip",
                                  DSU_INVOCATION_POLICY_DETERMINISTIC,
                                  "core"),
                 "build portable invocation");
    ok &= expect(build_invocation(&inv_user,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "gui",
                                  "msi",
                                  DSU_INVOCATION_POLICY_DETERMINISTIC,
                                  "core"),
                 "build user invocation");
    if (!ok) goto done;

    st = dsu_resolve_components_from_invocation(ctx, manifest, NULL, &inv_portable, &res_portable, NULL);
    ok &= expect(st == DSU_STATUS_SUCCESS && res_portable != NULL, "resolve portable");
    st = dsu_resolve_components_from_invocation(ctx, manifest, NULL, &inv_user, &res_user, NULL);
    ok &= expect(st == DSU_STATUS_SUCCESS && res_user != NULL, "resolve user");
    ok &= expect(components_match(res_portable, res_user), "portable vs user resolved set parity");
    if (!ok) goto done;

    ok &= expect(build_invocation(&inv_legacy_bad,
                                  DSU_INVOCATION_OPERATION_UPGRADE,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "cli",
                                  "legacy-dos",
                                  DSU_INVOCATION_POLICY_LEGACY_MODE,
                                  "core"),
                 "build legacy upgrade invocation");
    ok &= expect(build_invocation(&inv_legacy_ok,
                                  DSU_INVOCATION_OPERATION_INSTALL,
                                  DSU_INVOCATION_SCOPE_USER,
                                  "any-any",
                                  "install_user",
                                  "cli",
                                  "legacy-dos",
                                  DSU_INVOCATION_POLICY_LEGACY_MODE,
                                  "core"),
                 "build legacy install invocation");
    if (!ok) goto done;

    ok &= expect(dsu_invocation_validate(&inv_legacy_bad) == DSU_STATUS_INVALID_REQUEST,
                 "legacy mode rejects upgrade");
    ok &= expect(dsu_invocation_validate(&inv_legacy_ok) == DSU_STATUS_SUCCESS,
                 "legacy mode allows install");

done:
    if (res_portable) dsu_resolve_result_destroy(ctx, res_portable);
    if (res_user) dsu_resolve_result_destroy(ctx, res_user);
    if (plan_msi) dsu_plan_destroy(ctx, plan_msi);
    if (plan_exe) dsu_plan_destroy(ctx, plan_exe);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);

    dsu_invocation_destroy(NULL, &inv_msi);
    dsu_invocation_destroy(NULL, &inv_exe);
    dsu_invocation_destroy(NULL, &inv_cli);
    dsu_invocation_destroy(NULL, &inv_portable);
    dsu_invocation_destroy(NULL, &inv_user);
    dsu_invocation_destroy(NULL, &inv_legacy_bad);
    dsu_invocation_destroy(NULL, &inv_legacy_ok);

    return ok ? 0 : 1;
}
