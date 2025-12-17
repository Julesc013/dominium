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

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) {
        return 0;
    }
    f = fopen(path, "wb");
    if (!f) {
        return 0;
    }
    n = (size_t)len;
    if (n != 0u) {
        if (fwrite(bytes, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) {
        return 0;
    }
    return 1;
}

typedef struct buf_t {
    unsigned char *data;
    unsigned long len;
    unsigned long cap;
} buf_t;

static void buf_free(buf_t *b) {
    if (!b) return;
    free(b->data);
    b->data = NULL;
    b->len = 0ul;
    b->cap = 0ul;
}

static int buf_reserve(buf_t *b, unsigned long add) {
    unsigned long need;
    unsigned long new_cap;
    unsigned char *p;
    if (!b) return 0;
    if (add == 0ul) return 1;
    need = b->len + add;
    if (need < b->len) return 0;
    if (need <= b->cap) return 1;
    new_cap = (b->cap == 0ul) ? 256ul : b->cap;
    while (new_cap < need) {
        if (new_cap > 0x7FFFFFFFul) {
            new_cap = need;
            break;
        }
        new_cap *= 2ul;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) return 0;
    b->data = p;
    b->cap = new_cap;
    return 1;
}

static int buf_append(buf_t *b, const void *bytes, unsigned long n) {
    if (!b) return 0;
    if (n == 0ul) return 1;
    if (!bytes) return 0;
    if (!buf_reserve(b, n)) return 0;
    memcpy(b->data + b->len, bytes, (size_t)n);
    b->len += n;
    return 1;
}

static int buf_put_u8(buf_t *b, unsigned char v) {
    return buf_append(b, &v, 1ul);
}

static int buf_put_u16le(buf_t *b, unsigned short v) {
    unsigned char tmp[2];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    return buf_append(b, tmp, 2ul);
}

static int buf_put_u32le(buf_t *b, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_append(b, tmp, 4ul);
}

static int buf_put_tlv(buf_t *b, unsigned short type, const void *payload, unsigned long payload_len) {
    if (!buf_put_u16le(b, type)) return 0;
    if (!buf_put_u32le(b, payload_len)) return 0;
    return buf_append(b, payload, payload_len);
}

static int buf_put_tlv_u32(buf_t *b, unsigned short type, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_put_tlv(b, type, tmp, 4ul);
}

static int buf_put_tlv_u8(buf_t *b, unsigned short type, unsigned char v) {
    return buf_put_tlv(b, type, &v, 1ul);
}

static int buf_put_tlv_str(buf_t *b, unsigned short type, const char *s) {
    unsigned long n;
    if (!s) s = "";
    n = (unsigned long)strlen(s);
    return buf_put_tlv(b, type, s, n);
}

static unsigned long header_checksum32_base(const unsigned char hdr[20]) {
    unsigned long sum = 0ul;
    unsigned long i;
    for (i = 0ul; i < 16ul; ++i) {
        sum += (unsigned long)hdr[i];
    }
    return sum;
}

static int build_minimal_manifest_file(buf_t *out_file) {
    /* TLV + file header constants matching dsu_manifest.c */
    const unsigned short T_ROOT = 0x0001u;
    const unsigned short T_ROOT_VER = 0x0002u;
    const unsigned short T_PRODUCT_ID = 0x0010u;
    const unsigned short T_PRODUCT_VER = 0x0011u;
    const unsigned short T_BUILD_CHANNEL = 0x0012u;
    const unsigned short T_PLATFORM_TARGET = 0x0020u;
    const unsigned short T_INSTALL_ROOT = 0x0030u;
    const unsigned short T_IR_VER = 0x0031u;
    const unsigned short T_IR_SCOPE = 0x0032u;
    const unsigned short T_IR_PLATFORM = 0x0033u;
    const unsigned short T_IR_PATH = 0x0034u;
    const unsigned short T_COMPONENT = 0x0040u;
    const unsigned short T_C_VER = 0x0041u;
    const unsigned short T_C_ID = 0x0042u;
    const unsigned short T_C_KIND = 0x0044u;
    const unsigned short T_C_FLAGS = 0x0045u;

    buf_t root;
    buf_t payload;
    buf_t ir;
    buf_t comp;
    unsigned char hdr[20];
    unsigned long checksum;

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp, 0, sizeof(comp));
    memset(out_file, 0, sizeof(*out_file));

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, "1.0.0")) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, "stable")) goto fail;
    if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, "any-any")) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_SCOPE, 0u)) goto fail; /* portable */
    if (!buf_put_tlv_str(&ir, T_IR_PLATFORM, "any-any")) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, "C:/Dominium")) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT, ir.data, ir.len)) goto fail;
    buf_free(&ir);

    /* component core */
    if (!buf_put_tlv_u32(&comp, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, T_C_ID, "core")) goto fail;
    if (!buf_put_tlv_u8(&comp, T_C_KIND, 5u)) goto fail; /* other */
    if (!buf_put_tlv_u32(&comp, T_C_FLAGS, 0ul)) goto fail;
    if (!buf_put_tlv(&root, T_COMPONENT, comp.data, comp.len)) goto fail;
    buf_free(&comp);

    /* component data */
    if (!buf_put_tlv_u32(&comp, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, T_C_ID, "data")) goto fail;
    if (!buf_put_tlv_u8(&comp, T_C_KIND, 5u)) goto fail;
    if (!buf_put_tlv_u32(&comp, T_C_FLAGS, 0ul)) goto fail;
    if (!buf_put_tlv(&root, T_COMPONENT, comp.data, comp.len)) goto fail;
    buf_free(&comp);

    if (!buf_put_tlv(&payload, T_ROOT, root.data, root.len)) goto fail;
    buf_free(&root);

    /* DSUM file header (20 bytes) */
    hdr[0] = 'D';
    hdr[1] = 'S';
    hdr[2] = 'U';
    hdr[3] = 'M';
    /* version u16 = 2 */
    hdr[4] = 2u;
    hdr[5] = 0u;
    /* endian marker 0xFFFE */
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    /* header size = 20 */
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    /* payload length */
    hdr[12] = (unsigned char)(payload.len & 0xFFul);
    hdr[13] = (unsigned char)((payload.len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload.len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload.len >> 24) & 0xFFul);
    /* checksum placeholder */
    hdr[16] = 0u;
    hdr[17] = 0u;
    hdr[18] = 0u;
    hdr[19] = 0u;
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);

    if (!buf_append(out_file, hdr, 20ul)) goto fail;
    if (!buf_append(out_file, payload.data, payload.len)) goto fail;
    buf_free(&payload);
    return 1;

fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(out_file);
    return 0;
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
    const char *manifest_path = "dsu_test_manifest.dsumanifest";
    const char *plan_a_path = "dsu_test_plan_a.dsuplan";
    const char *plan_b_path = "dsu_test_plan_b.dsuplan";
    const char *log_plan_a = "dsu_test_plan_a.dsulog";
    const char *log_plan_b = "dsu_test_plan_b.dsulog";
    const char *log_dry_a = "dsu_test_dry_a.dsulog";
    const char *log_dry_b = "dsu_test_dry_b.dsulog";

    buf_t mf_bytes;

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_resolved_t *resolved = NULL;
    dsu_plan_t *plan = NULL;
    dsu_plan_t *plan_roundtrip = NULL;
    dsu_log_t *log_roundtrip = NULL;
    dsu_execute_options_t exec_opts;
    dsu_status_t st;
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

    memset(&mf_bytes, 0, sizeof(mf_bytes));
    ok &= expect(build_minimal_manifest_file(&mf_bytes), "build minimal manifest bytes");
    ok &= expect(write_bytes_file(manifest_path, mf_bytes.data, mf_bytes.len), "write minimal manifest file");
    buf_free(&mf_bytes);
    if (!ok) goto done;

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
    ok &= expect(dsu_plan_id_hash32(plan_roundtrip) == dsu_plan_id_hash32(plan), "plan id after read");
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
