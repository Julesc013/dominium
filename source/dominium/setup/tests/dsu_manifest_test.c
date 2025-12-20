/*
FILE: source/dominium/setup/tests/dsu_manifest_test.c
MODULE: Dominium Setup
PURPOSE: TLV manifest v2 tests (roundtrip, canonicalization, validation).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"

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

static int wrap_file(buf_t *out_file, const unsigned char magic[4], unsigned short version, const buf_t *payload) {
    unsigned char hdr[20];
    unsigned long checksum;
    if (!out_file || !magic || !payload) return 0;
    memset(out_file, 0, sizeof(*out_file));
    memset(hdr, 0, sizeof(hdr));
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (unsigned char)(version & 0xFFu);
    hdr[5] = (unsigned char)((version >> 8) & 0xFFu);
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload->len & 0xFFul);
    hdr[13] = (unsigned char)((payload->len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload->len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload->len >> 24) & 0xFFul);
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);
    if (!buf_append(out_file, hdr, 20ul)) return 0;
    if (!buf_append(out_file, payload->data, payload->len)) return 0;
    return 1;
}

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) return 0;
    f = fopen(path, "wb");
    if (!f) return 0;
    n = (size_t)len;
    if (n != 0u) {
        if (fwrite(bytes, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) return 0;
    return 1;
}

static int read_all_bytes(const char *path, unsigned char **out_bytes, unsigned long *out_len) {
    FILE *f;
    long sz;
    unsigned char *buf;
    size_t nread;
    if (!path || !out_bytes || !out_len) return 0;
    *out_bytes = NULL;
    *out_len = 0ul;
    f = fopen(path, "rb");
    if (!f) return 0;
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

static int bytes_equal(const unsigned char *a, unsigned long a_len, const unsigned char *b, unsigned long b_len) {
    if (a_len != b_len) return 0;
    if (a_len == 0ul) return 1;
    if (!a || !b) return 0;
    return memcmp(a, b, (size_t)a_len) == 0;
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int build_manifest_file(buf_t *out_file,
                               int include_build_channel,
                               int include_unknown_tlv,
                               const char *platform_target,
                               int duplicate_component_id,
                               int reverse_component_order) {
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
    buf_t comp_a;
    buf_t comp_b;
    unsigned char hdr[20];
    unsigned long checksum;
    const char *plat = platform_target ? platform_target : "any-any";

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp_a, 0, sizeof(comp_a));
    memset(&comp_b, 0, sizeof(comp_b));
    memset(out_file, 0, sizeof(*out_file));

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, "1.0.0")) goto fail;
    if (include_build_channel) {
        if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, "stable")) goto fail;
    }
    if (include_unknown_tlv) {
        const unsigned short T_UNKNOWN = 0x7F01u;
        const char payload_bytes[3] = {'x', 'y', 'z'};
        if (!buf_put_tlv(&root, T_UNKNOWN, payload_bytes, 3ul)) goto fail;
    }
    if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, plat)) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_SCOPE, 0u)) goto fail; /* portable */
    if (!buf_put_tlv_str(&ir, T_IR_PLATFORM, plat)) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, "C:/Dominium")) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT, ir.data, ir.len)) goto fail;
    buf_free(&ir);

    /* Two component containers with potentially swapped order/duplicates */
    if (!buf_put_tlv_u32(&comp_a, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp_a, T_C_ID, duplicate_component_id ? "Core" : "core")) goto fail;
    if (!buf_put_tlv_u8(&comp_a, T_C_KIND, 5u)) goto fail;
    if (!buf_put_tlv_u32(&comp_a, T_C_FLAGS, 0ul)) goto fail;

    if (!buf_put_tlv_u32(&comp_b, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp_b, T_C_ID, duplicate_component_id ? "core" : "data")) goto fail;
    if (!buf_put_tlv_u8(&comp_b, T_C_KIND, 5u)) goto fail;
    if (!buf_put_tlv_u32(&comp_b, T_C_FLAGS, 0ul)) goto fail;

    if (reverse_component_order) {
        if (!buf_put_tlv(&root, T_COMPONENT, comp_b.data, comp_b.len)) goto fail;
        if (!buf_put_tlv(&root, T_COMPONENT, comp_a.data, comp_a.len)) goto fail;
    } else {
        if (!buf_put_tlv(&root, T_COMPONENT, comp_a.data, comp_a.len)) goto fail;
        if (!buf_put_tlv(&root, T_COMPONENT, comp_b.data, comp_b.len)) goto fail;
    }
    buf_free(&comp_a);
    buf_free(&comp_b);

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
    buf_free(&comp_a);
    buf_free(&comp_b);
    buf_free(out_file);
    return 0;
}

static int write_manifest_variant(const char *path,
                                  int include_build_channel,
                                  int include_unknown_tlv,
                                  const char *platform_target,
                                  int duplicate_component_id,
                                  int reverse_component_order) {
    buf_t b;
    int ok;
    memset(&b, 0, sizeof(b));
    ok = build_manifest_file(&b,
                             include_build_channel,
                             include_unknown_tlv,
                             platform_target,
                             duplicate_component_id,
                             reverse_component_order);
    if (!ok) {
        buf_free(&b);
        return 0;
    }
    ok = write_bytes_file(path, b.data, b.len);
    buf_free(&b);
    return ok;
}

static unsigned long rng_next_u32(unsigned long *state) {
    unsigned long x;
    if (!state) return 0ul;
    x = *state;
    x = (1103515245ul * x + 12345ul) & 0xFFFFFFFFul;
    *state = x;
    return x;
}

static int test_tlv_fuzz_lite(void) {
    unsigned long seed = 0xC0FFEE01ul;
    dsu_ctx_t *ctx = NULL;
    int ok = 1;
    dsu_status_t st;
    unsigned long i;

    {
        dsu_config_t cfg;
        dsu_callbacks_t cbs;
        dsu_config_init(&cfg);
        dsu_callbacks_init(&cbs);
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
        st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    }
    ok &= expect(st == DSU_STATUS_SUCCESS && ctx != NULL, "ctx create (fuzz)");
    if (!ok) return 0;

    for (i = 0ul; i < 32ul; ++i) {
        char path[64];
        buf_t payload;
        buf_t file;
        unsigned long j;
        unsigned long tlv_count = (rng_next_u32(&seed) % 8ul) + 1ul;

        memset(&payload, 0, sizeof(payload));
        memset(&file, 0, sizeof(file));

        for (j = 0ul; j < tlv_count; ++j) {
            unsigned short t = (unsigned short)(rng_next_u32(&seed) & 0xFFFFu);
            unsigned long len = rng_next_u32(&seed) % 24ul;
            unsigned char bytes[32];
            unsigned long k;
            if (len > sizeof(bytes)) len = sizeof(bytes);
            for (k = 0ul; k < len; ++k) {
                bytes[k] = (unsigned char)(rng_next_u32(&seed) & 0xFFu);
            }
            if (!buf_put_tlv(&payload, t, bytes, len)) {
                ok = 0;
                break;
            }
        }

        if (!wrap_file(&file, (const unsigned char *)"DSUM", 2u, &payload)) {
            ok = 0;
        }
        buf_free(&payload);
        if (!ok) {
            buf_free(&file);
            break;
        }

        sprintf(path, "dsu_test_fuzz_%02lu.dsumanifest", i);
        ok &= expect(write_bytes_file(path, file.data, file.len), "write fuzz manifest");
        buf_free(&file);
        if (!ok) break;

        {
            dsu_manifest_t *m = NULL;
            st = dsu_manifest_load_file(ctx, path, &m);
            ok &= expect(st != DSU_STATUS_IO_ERROR && st != DSU_STATUS_INTERNAL_ERROR, "fuzz load status");
            if (st == DSU_STATUS_SUCCESS && m) {
                dsu_manifest_destroy(ctx, m);
            }
        }
        remove(path);
        if (!ok) break;
    }

    if (ctx) dsu_ctx_destroy(ctx);
    return ok;
}

int main(void) {
    const char *in_a = "dsu_test_in_a.dsumanifest";
    const char *in_b = "dsu_test_in_b.dsumanifest";
    const char *out_a = "dsu_test_out_a.dsumanifest";
    const char *out_b = "dsu_test_out_b.dsumanifest";
    const char *out_b2 = "dsu_test_out_b2.dsumanifest";
    const char *out_json_a = "dsu_test_manifest_a.json";
    const char *out_json_b = "dsu_test_manifest_b.json";

    unsigned char *a_bytes = NULL;
    unsigned long a_len = 0ul;
    unsigned char *b_bytes = NULL;
    unsigned long b_len = 0ul;

    unsigned char *json_a_bytes = NULL;
    unsigned long json_a_len = 0ul;
    unsigned char *json_b_bytes = NULL;
    unsigned long json_b_len = 0ul;

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *ma = NULL;
    dsu_manifest_t *mb = NULL;
    dsu_manifest_t *mb2 = NULL;
    dsu_status_t st;
    int ok = 1;

    /* Build two logically identical manifests with different ordering + unknown TLV in A. */
    ok &= expect(write_manifest_variant(in_a, 1, 1, "any-any", 0, 1), "write in_a");
    ok &= expect(write_manifest_variant(in_b, 1, 0, "any-any", 0, 0), "write in_b");
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

    st = dsu_manifest_load_file(ctx, in_a, &ma);
    ok &= expect(st == DSU_STATUS_SUCCESS && ma != NULL, "load in_a");
    st = dsu_manifest_load_file(ctx, in_b, &mb);
    ok &= expect(st == DSU_STATUS_SUCCESS && mb != NULL, "load in_b");
    if (!ok) goto done;

    /* Canonical TLV output must match even with unknown TLVs and ordering differences. */
    st = dsu_manifest_write_file(ctx, ma, out_a);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write out_a");
    st = dsu_manifest_write_file(ctx, mb, out_b);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write out_b");
    ok &= expect(read_all_bytes(out_a, &a_bytes, &a_len), "read out_a");
    ok &= expect(read_all_bytes(out_b, &b_bytes, &b_len), "read out_b");
    ok &= expect(bytes_equal(a_bytes, a_len, b_bytes, b_len), "canonical TLV bytes identical");
    free(a_bytes); a_bytes = NULL; a_len = 0ul;
    free(b_bytes); b_bytes = NULL; b_len = 0ul;

    /* Roundtrip: re-load canonical output and re-write; bytes must match. */
    st = dsu_manifest_load_file(ctx, out_b, &mb2);
    ok &= expect(st == DSU_STATUS_SUCCESS && mb2 != NULL, "load out_b");
    st = dsu_manifest_write_file(ctx, mb2, out_b2);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write out_b2");
    ok &= expect(read_all_bytes(out_b, &a_bytes, &a_len), "read out_b");
    ok &= expect(read_all_bytes(out_b2, &b_bytes, &b_len), "read out_b2");
    ok &= expect(bytes_equal(a_bytes, a_len, b_bytes, b_len), "roundtrip TLV bytes identical");
    free(a_bytes); a_bytes = NULL; a_len = 0ul;
    free(b_bytes); b_bytes = NULL; b_len = 0ul;

    /* JSON output determinism: writing JSON twice yields identical bytes. */
    st = dsu_manifest_write_json_file(ctx, mb, out_json_a);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write json a");
    st = dsu_manifest_write_json_file(ctx, mb, out_json_b);
    ok &= expect(st == DSU_STATUS_SUCCESS, "write json b");
    ok &= expect(read_all_bytes(out_json_a, &json_a_bytes, &json_a_len), "read json a");
    ok &= expect(read_all_bytes(out_json_b, &json_b_bytes, &json_b_len), "read json b");
    ok &= expect(bytes_equal(json_a_bytes, json_a_len, json_b_bytes, json_b_len), "json bytes deterministic");

    /* Validation failure: missing build_channel. */
    ok &= expect(write_manifest_variant("dsu_test_missing_build.dsumanifest", 0, 0, "any-any", 0, 0),
                 "write missing_build");
    {
        dsu_manifest_t *tmp = NULL;
        st = dsu_manifest_load_file(ctx, "dsu_test_missing_build.dsumanifest", &tmp);
        ok &= expect(st == DSU_STATUS_PARSE_ERROR, "missing build_channel rejected");
        if (tmp) dsu_manifest_destroy(ctx, tmp);
    }

    /* Validation failure: duplicate component id (case-insensitive after normalization). */
    ok &= expect(write_manifest_variant("dsu_test_dup_component.dsumanifest", 1, 0, "any-any", 1, 0),
                 "write dup_component");
    {
        dsu_manifest_t *tmp = NULL;
        st = dsu_manifest_load_file(ctx, "dsu_test_dup_component.dsumanifest", &tmp);
        ok &= expect(st == DSU_STATUS_PARSE_ERROR, "duplicate component id rejected");
        if (tmp) dsu_manifest_destroy(ctx, tmp);
    }

    /* Validation failure: bad platform triple. */
    ok &= expect(write_manifest_variant("dsu_test_bad_platform.dsumanifest", 1, 0, "win-x64", 0, 0),
                 "write bad_platform");
    {
        dsu_manifest_t *tmp = NULL;
        st = dsu_manifest_load_file(ctx, "dsu_test_bad_platform.dsumanifest", &tmp);
        ok &= expect(st == DSU_STATUS_PARSE_ERROR, "bad platform triple rejected");
        if (tmp) dsu_manifest_destroy(ctx, tmp);
    }

    ok &= test_tlv_fuzz_lite();

done:
    if (ma) dsu_manifest_destroy(ctx, ma);
    if (mb) dsu_manifest_destroy(ctx, mb);
    if (mb2) dsu_manifest_destroy(ctx, mb2);
    if (ctx) dsu_ctx_destroy(ctx);

    free(a_bytes);
    free(b_bytes);
    free(json_a_bytes);
    free(json_b_bytes);

    remove(in_a);
    remove(in_b);
    remove(out_a);
    remove(out_b);
    remove(out_b2);
    remove(out_json_a);
    remove(out_json_b);
    remove("dsu_test_missing_build.dsumanifest");
    remove("dsu_test_dup_component.dsumanifest");
    remove("dsu_test_bad_platform.dsumanifest");

    return ok ? 0 : 1;
}
