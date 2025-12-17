/*
FILE: source/dominium/setup/tests/dsu_core_smoke_test.c
MODULE: Dominium Setup
PURPOSE: Lightweight smoke test for Setup Core Plan S-1 scaffolding.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_execute.h"
#include "dsu/dsu_log.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"

static int write_text_file(const char *path, const char *text) {
    FILE *f;
    size_t n;
    if (!path || !text) {
        return 0;
    }
    f = fopen(path, "wb");
    if (!f) {
        return 0;
    }
    n = strlen(text);
    if (n != 0u) {
        if (fwrite(text, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) {
        return 0;
    }
    return 1;
}

static int read_all_bytes(const char *path, unsigned char **out_bytes, unsigned long *out_len) {
    FILE *f;
    long sz;
    unsigned char *buf;
    size_t nread;
    if (!path || !out_bytes || !out_len) {
        return 0;
    }
    *out_bytes = NULL;
    *out_len = 0ul;
    f = fopen(path, "rb");
    if (!f) {
        return 0;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return 0;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    buf = (unsigned char *)malloc((size_t)sz);
    if (!buf && sz != 0) {
        fclose(f);
        return 0;
    }
    nread = (sz == 0) ? 0u : fread(buf, 1u, (size_t)sz, f);
    fclose(f);
    if (nread != (size_t)sz) {
        free(buf);
        return 0;
    }
    *out_bytes = buf;
    *out_len = (unsigned long)sz;
    return 1;
}

static int bytes_equal(const unsigned char *a, unsigned long a_len,
                       const unsigned char *b, unsigned long b_len) {
    if (a_len != b_len) {
        return 0;
    }
    if (a_len == 0ul) {
        return 1;
    }
    if (!a || !b) {
        return 0;
    }
    return memcmp(a, b, (size_t)a_len) == 0;
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

int main(void) {
    const char *manifest_path = "dsu_test_manifest.dsumf";
    const char *plan_a_path = "dsu_test_plan_a.dsuplan";
    const char *plan_b_path = "dsu_test_plan_b.dsuplan";
    const char *log_plan_a = "dsu_test_plan_a.dsulog";
    const char *log_plan_b = "dsu_test_plan_b.dsulog";
    const char *log_dry_a = "dsu_test_dry_a.dsulog";
    const char *log_dry_b = "dsu_test_dry_b.dsulog";

    const char *manifest_text =
        "product_id=dominium\n"
        "version=1.0.0\n"
        "install_root=C:/Dominium\n"
        "components=[core,data]\n";

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_resolved_t *resolved = NULL;
    dsu_plan_t *plan = NULL;
    dsu_plan_t *plan_roundtrip = NULL;
    dsu_log_t *log_roundtrip = NULL;
    dsu_execute_options_t exec_opts;
    dsu_status_t st;
    unsigned long expected_plan_id = 1032754275ul;
    unsigned long i;
    int ok = 1;

    unsigned char *plan_a_bytes = NULL;
    unsigned char *plan_b_bytes = NULL;
    unsigned long plan_a_len = 0ul;
    unsigned long plan_b_len = 0ul;

    unsigned char *dry_a_bytes = NULL;
    unsigned char *dry_b_bytes = NULL;
    unsigned long dry_a_len = 0ul;
    unsigned long dry_b_len = 0ul;

    if (!write_text_file(manifest_path, manifest_text)) {
        fprintf(stderr, "FAIL: could not write manifest\n");
        return 1;
    }

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

    ok &= expect(dsu_ctx_reset_audit_log(ctx) == DSU_STATUS_SUCCESS, "reset audit log");

    st = dsu_manifest_load_file(ctx, manifest_path, &manifest);
    ok &= expect(st == DSU_STATUS_SUCCESS && manifest != NULL, "manifest load");

    st = dsu_resolve(ctx, manifest, &resolved);
    ok &= expect(st == DSU_STATUS_SUCCESS && resolved != NULL, "resolve");

    st = dsu_plan_build(ctx, manifest, resolved, &plan);
    ok &= expect(st == DSU_STATUS_SUCCESS && plan != NULL, "plan build");
    ok &= expect((unsigned long)dsu_plan_id_hash32(plan) == expected_plan_id, "plan id hash stable");

    st = dsu_plan_write_file(ctx, plan, plan_a_path);
    ok &= expect(st == DSU_STATUS_SUCCESS, "plan write A");
    st = dsu_log_write_file(ctx, dsu_ctx_get_audit_log(ctx), log_plan_a);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write plan audit log");

    st = dsu_log_read_file(ctx, log_plan_a, &log_roundtrip);
    ok &= expect(st == DSU_STATUS_SUCCESS && log_roundtrip != NULL, "read plan audit log");
    ok &= expect((unsigned long)dsu_log_event_count(log_roundtrip) == 4ul, "plan audit log event count");
    for (i = 0ul; i < dsu_log_event_count(log_roundtrip); ++i) {
        dsu_u32 ts = 123u;
        (void)dsu_log_event_get(log_roundtrip, (dsu_u32)i, NULL, NULL, NULL, &ts, NULL);
        ok &= expect(ts == 0u, "audit timestamp is 0 in deterministic mode");
    }

    st = dsu_log_write_file(ctx, log_roundtrip, log_plan_b);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write roundtrip log");

    st = dsu_plan_write_file(ctx, plan, plan_b_path);
    ok &= expect(st == DSU_STATUS_SUCCESS, "plan write B");

    ok &= expect(read_all_bytes(plan_a_path, &plan_a_bytes, &plan_a_len), "read plan A");
    ok &= expect(read_all_bytes(plan_b_path, &plan_b_bytes, &plan_b_len), "read plan B");
    ok &= expect(bytes_equal(plan_a_bytes, plan_a_len, plan_b_bytes, plan_b_len), "plan bytes deterministic");

    st = dsu_plan_read_file(ctx, plan_a_path, &plan_roundtrip);
    ok &= expect(st == DSU_STATUS_SUCCESS && plan_roundtrip != NULL, "plan read roundtrip");
    ok &= expect((unsigned long)dsu_plan_id_hash32(plan_roundtrip) == expected_plan_id, "plan id after read");
    ok &= expect(dsu_plan_step_count(plan_roundtrip) == dsu_plan_step_count(plan), "step count after read");

    /* Dry-run determinism check. */
    ok &= expect(dsu_ctx_reset_audit_log(ctx) == DSU_STATUS_SUCCESS, "reset audit log before dry-run");
    dsu_execute_options_init(&exec_opts);
    exec_opts.log_path = log_dry_a;
    st = dsu_execute_plan(ctx, plan, &exec_opts);
    ok &= expect(st == DSU_STATUS_SUCCESS, "dry-run A");

    ok &= expect(dsu_ctx_reset_audit_log(ctx) == DSU_STATUS_SUCCESS, "reset audit log before dry-run B");
    dsu_execute_options_init(&exec_opts);
    exec_opts.log_path = log_dry_b;
    st = dsu_execute_plan(ctx, plan, &exec_opts);
    ok &= expect(st == DSU_STATUS_SUCCESS, "dry-run B");

    ok &= expect(read_all_bytes(log_dry_a, &dry_a_bytes, &dry_a_len), "read dry log A");
    ok &= expect(read_all_bytes(log_dry_b, &dry_b_bytes, &dry_b_len), "read dry log B");
    ok &= expect(bytes_equal(dry_a_bytes, dry_a_len, dry_b_bytes, dry_b_len), "dry-run log bytes deterministic");

done:
    if (plan_roundtrip) dsu_plan_destroy(ctx, plan_roundtrip);
    if (plan) dsu_plan_destroy(ctx, plan);
    if (resolved) dsu_resolved_destroy(ctx, resolved);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (log_roundtrip) dsu_log_destroy(ctx, log_roundtrip);
    if (ctx) dsu_ctx_destroy(ctx);

    free(plan_a_bytes);
    free(plan_b_bytes);
    free(dry_a_bytes);
    free(dry_b_bytes);

    remove(manifest_path);
    remove(plan_a_path);
    remove(plan_b_path);
    remove(log_plan_a);
    remove(log_plan_b);
    remove(log_dry_a);
    remove(log_dry_b);

    return ok ? 0 : 1;
}
