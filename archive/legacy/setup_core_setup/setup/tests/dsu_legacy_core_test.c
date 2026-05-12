/*
FILE: source/dominium/setup/tests/dsu_legacy_core_test.c
MODULE: Dominium Setup
PURPOSE: Legacy core tests (TLV parsing, state determinism, rollback).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../installers/windows_legacy/legacy_core/include/dsu_legacy_core.h"

#if defined(_WIN32)
#include <direct.h>
#define dsu_test_mkdir _mkdir
#else
#include <sys/stat.h>
#define dsu_test_mkdir(path) mkdir((path), 0755)
#endif

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

static int buf_put_u64le(buf_t *b, unsigned long v) {
    unsigned char tmp[8];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    tmp[4] = 0u;
    tmp[5] = 0u;
    tmp[6] = 0u;
    tmp[7] = 0u;
    return buf_append(b, tmp, 8ul);
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

static char *dup_str(const char *s) {
    size_t n;
    char *p;
    if (!s) return NULL;
    n = strlen(s);
    p = (char *)malloc(n + 1u);
    if (!p) return NULL;
    memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int build_archive_file(const char *path, const char *member_path, const char *payload) {
    buf_t b;
    unsigned long path_len;
    unsigned long payload_len;
    unsigned char zero_sha[32];
    memset(&b, 0, sizeof(b));
    memset(zero_sha, 0, sizeof(zero_sha));
    path_len = (unsigned long)strlen(member_path);
    payload_len = (unsigned long)strlen(payload);

    /* DSUA header */
    if (!buf_append(&b, "DSUA", 4ul)) goto fail;
    if (!buf_put_u16le(&b, 1u)) goto fail;
    if (!buf_put_u16le(&b, 0xFFFEu)) goto fail;
    if (!buf_put_u32le(&b, 1ul)) goto fail; /* count */
    if (!buf_put_u32le(&b, 0ul)) goto fail; /* reserved */

    if (!buf_put_u32le(&b, path_len)) goto fail;
    if (!buf_append(&b, member_path, path_len)) goto fail;
    if (!buf_put_u64le(&b, payload_len)) goto fail;
    if (!buf_append(&b, zero_sha, 32ul)) goto fail;
    if (!buf_append(&b, payload, payload_len)) goto fail;

    if (!write_bytes_file(path, b.data, b.len)) goto fail;
    buf_free(&b);
    return 1;
fail:
    buf_free(&b);
    return 0;
}

static int build_manifest_file(const char *path,
                               const char *install_root,
                               const char *payload_path_a,
                               const char *payload_path_b) {
    buf_t root;
    buf_t payload;
    buf_t ir;
    buf_t comp;
    buf_t comp_payload;
    buf_t file;
    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp, 0, sizeof(comp));
    memset(&comp_payload, 0, sizeof(comp_payload));
    memset(&file, 0, sizeof(file));

    /* manifest root */
    if (!buf_put_tlv_u32(&root, 0x0002u, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, 0x0010u, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, 0x0011u, "1.0.0")) goto fail;
    if (!buf_put_tlv_str(&root, 0x0020u, "macos-x86")) goto fail;

    if (!buf_put_tlv_u32(&ir, 0x0031u, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, 0x0032u, 0u)) goto fail; /* portable */
    if (!buf_put_tlv_str(&ir, 0x0033u, "macos-x86")) goto fail;
    if (!buf_put_tlv_str(&ir, 0x0034u, install_root)) goto fail;
    if (!buf_put_tlv(&root, 0x0030u, ir.data, ir.len)) goto fail;

    if (!buf_put_tlv_u32(&comp, 0x0041u, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, 0x0042u, "core")) goto fail;
    if (!buf_put_tlv_u8(&comp, 0x0044u, 1u)) goto fail;
    if (!buf_put_tlv_u32(&comp, 0x0045u, 0x00000002ul)) goto fail; /* default selected */

    if (!buf_put_tlv_u32(&comp_payload, 0x004Du, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&comp_payload, 0x004Eu, 1u)) goto fail; /* archive */
    if (!buf_put_tlv_str(&comp_payload, 0x004Fu, payload_path_a)) goto fail;
    if (!buf_put_tlv(&comp, 0x004Cu, comp_payload.data, comp_payload.len)) goto fail;
    buf_free(&comp_payload);
    memset(&comp_payload, 0, sizeof(comp_payload));

    if (payload_path_b) {
        if (!buf_put_tlv_u32(&comp_payload, 0x004Du, 1ul)) goto fail;
        if (!buf_put_tlv_u8(&comp_payload, 0x004Eu, 1u)) goto fail;
        if (!buf_put_tlv_str(&comp_payload, 0x004Fu, payload_path_b)) goto fail;
        if (!buf_put_tlv(&comp, 0x004Cu, comp_payload.data, comp_payload.len)) goto fail;
        buf_free(&comp_payload);
    }

    if (!buf_put_tlv(&root, 0x0040u, comp.data, comp.len)) goto fail;

    if (!buf_put_tlv(&payload, 0x0001u, root.data, root.len)) goto fail;

    if (!wrap_file(&file, (const unsigned char *)"DSUM", 2u, &payload)) goto fail;

    if (!write_bytes_file(path, file.data, file.len)) goto fail;
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&file);
    return 1;
fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&comp_payload);
    buf_free(&file);
    return 0;
}

static int build_invocation_file(const char *path, const char *install_root) {
    buf_t root;
    buf_t payload;
    buf_t file;
    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&file, 0, sizeof(file));

    if (!buf_put_tlv_u32(&root, 0x0101u, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&root, 0x0110u, 0u)) goto fail; /* install */
    if (!buf_put_tlv_u8(&root, 0x0111u, 0u)) goto fail;
    if (!buf_put_tlv_str(&root, 0x0120u, "macos-x86")) goto fail;
    if (!buf_put_tlv_str(&root, 0x0130u, install_root)) goto fail;
    if (!buf_put_tlv_u32(&root, 0x0140u, 0ul)) goto fail;
    if (!buf_put_tlv_str(&root, 0x0150u, "cli")) goto fail;
    if (!buf_put_tlv_str(&root, 0x0151u, "classic-test")) goto fail;
    if (!buf_put_tlv_str(&root, 0x0160u, "core")) goto fail;

    if (!buf_put_tlv(&payload, 0x0100u, root.data, root.len)) goto fail;
    if (!wrap_file(&file, (const unsigned char *)"DSUI", 1u, &payload)) goto fail;

    if (!write_bytes_file(path, file.data, file.len)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    buf_free(&file);
    return 1;
fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&file);
    return 0;
}

int main(void) {
    const char *root = "legacy_test_tmp";
    const char *payload_dir = "legacy_test_tmp/payloads";
    const char *install_root = "legacy_test_tmp/install";
    const char *archive_path = "legacy_test_tmp/payloads/payload_a.dsuarch";
    const char *manifest_ok = "legacy_test_tmp/manifest_ok.dsumanifest";
    const char *manifest_fail = "legacy_test_tmp/manifest_fail.dsumanifest";
    const char *manifest_traversal = "legacy_test_tmp/manifest_traversal.dsumanifest";
    const char *invocation_path = "legacy_test_tmp/invocation.dsui";
    const char *state_path = "legacy_test_tmp/state.dsus";
    const char *log_path = "legacy_test_tmp/install.log";
    const char *file_rel = "test.txt";
    const char *file_abs = "legacy_test_tmp/install/test.txt";
    const char *archive_bad = "legacy_test_tmp/payloads/payload_bad.dsuarch";
    unsigned char *a_bytes = NULL;
    unsigned long a_len = 0ul;
    unsigned char *b_bytes = NULL;
    unsigned long b_len = 0ul;
    int ok = 1;
    dsu_legacy_manifest_t *m = NULL;
    dsu_legacy_invocation_t *inv = NULL;

    dsu_test_mkdir(root);
    dsu_test_mkdir(payload_dir);
    dsu_test_mkdir(install_root);

    ok &= expect(build_archive_file(archive_path, file_rel, "hello"), "build archive");
    ok &= expect(build_archive_file(archive_bad, "../evil.txt", "oops"), "build archive bad");
    ok &= expect(build_manifest_file(manifest_ok, install_root, "payloads/payload_a.dsuarch", NULL), "build manifest ok");
    ok &= expect(build_manifest_file(manifest_fail, install_root, "payloads/payload_a.dsuarch", "payloads/missing.dsuarch"), "build manifest fail");
    ok &= expect(build_manifest_file(manifest_traversal, install_root, "payloads/payload_bad.dsuarch", NULL), "build manifest traversal");
    ok &= expect(build_invocation_file(invocation_path, install_root), "build invocation");

    ok &= expect(dsu_legacy_manifest_load(manifest_ok, &m) == DSU_LEGACY_STATUS_SUCCESS, "load legacy manifest");
    ok &= expect(m && m->product_id && strcmp(m->product_id, "dominium") == 0, "manifest product id");
    if (m) dsu_legacy_manifest_free(m);
    m = NULL;

    ok &= expect(dsu_legacy_invocation_load(invocation_path, &inv) == DSU_LEGACY_STATUS_SUCCESS, "load legacy invocation");
    ok &= expect(inv && inv->install_root_count == 1u, "invocation install root count");
    if (inv) dsu_legacy_invocation_free(inv);
    inv = NULL;

    /* State determinism test */
    {
        dsu_legacy_state_t *state = (dsu_legacy_state_t *)malloc(sizeof(*state));
        ok &= expect(state != NULL, "alloc state");
        if (state) {
            memset(state, 0, sizeof(*state));
            state->product_id = dup_str("dominium");
            state->product_version = dup_str("1.0.0");
            state->platform_triple = dup_str("macos-x86");
            state->scope = 0u;
            state->install_root = dup_str("legacy_test_tmp/install");
            ok &= expect(dsu_legacy_state_add_component(state, "core", "1.0.0") == DSU_LEGACY_STATUS_SUCCESS, "state add component");
            ok &= expect(dsu_legacy_state_add_file(state, "test.txt", 5u) == DSU_LEGACY_STATUS_SUCCESS, "state add file");
            ok &= expect(dsu_legacy_state_write(state, "legacy_test_tmp/state_a.dsus") == DSU_LEGACY_STATUS_SUCCESS, "write state a");
            ok &= expect(dsu_legacy_state_write(state, "legacy_test_tmp/state_b.dsus") == DSU_LEGACY_STATUS_SUCCESS, "write state b");
            dsu_legacy_state_free(state);
        }
        ok &= expect(read_all_bytes("legacy_test_tmp/state_a.dsus", &a_bytes, &a_len), "read state a");
        ok &= expect(read_all_bytes("legacy_test_tmp/state_b.dsus", &b_bytes, &b_len), "read state b");
        ok &= expect(bytes_equal(a_bytes, a_len, b_bytes, b_len), "state deterministic bytes");
        free(a_bytes);
        free(b_bytes);
        a_bytes = NULL;
        b_bytes = NULL;
    }

    /* Apply success */
    ok &= expect(dsu_legacy_manifest_load(manifest_ok, &m) == DSU_LEGACY_STATUS_SUCCESS, "load manifest ok");
    ok &= expect(dsu_legacy_invocation_load(invocation_path, &inv) == DSU_LEGACY_STATUS_SUCCESS, "load invocation ok");
    if (ok) {
        dsu_legacy_status_t st = dsu_legacy_apply(m, inv, root, state_path, log_path);
        ok &= expect(st == DSU_LEGACY_STATUS_SUCCESS, "legacy apply success");
        ok &= expect(read_all_bytes(file_abs, &a_bytes, &a_len), "installed file present");
        ok &= expect(dsu_legacy_verify(state_path, log_path) == DSU_LEGACY_STATUS_SUCCESS, "legacy verify");
        free(a_bytes);
        a_bytes = NULL;
        remove(state_path);
        remove(file_abs);
    }
    if (m) dsu_legacy_manifest_free(m);
    if (inv) dsu_legacy_invocation_free(inv);
    m = NULL;
    inv = NULL;

    /* Apply failure + rollback */
    ok &= expect(dsu_legacy_manifest_load(manifest_fail, &m) == DSU_LEGACY_STATUS_SUCCESS, "load manifest fail");
    ok &= expect(dsu_legacy_invocation_load(invocation_path, &inv) == DSU_LEGACY_STATUS_SUCCESS, "load invocation fail");
    if (ok) {
        dsu_legacy_status_t st = dsu_legacy_apply(m, inv, root, state_path, log_path);
        ok &= expect(st != DSU_LEGACY_STATUS_SUCCESS, "legacy apply failure");
        ok &= expect(read_all_bytes(file_abs, &a_bytes, &a_len) == 0, "rollback removed file");
    }
    if (m) dsu_legacy_manifest_free(m);
    if (inv) dsu_legacy_invocation_free(inv);

    /* Apply failure on traversal */
    ok &= expect(dsu_legacy_manifest_load(manifest_traversal, &m) == DSU_LEGACY_STATUS_SUCCESS, "load manifest traversal");
    ok &= expect(dsu_legacy_invocation_load(invocation_path, &inv) == DSU_LEGACY_STATUS_SUCCESS, "load invocation traversal");
    if (ok) {
        dsu_legacy_status_t st = dsu_legacy_apply(m, inv, root, state_path, log_path);
        ok &= expect(st != DSU_LEGACY_STATUS_SUCCESS, "legacy apply traversal rejection");
        ok &= expect(read_all_bytes(file_abs, &a_bytes, &a_len) == 0, "traversal prevented file write");
    }
    if (m) dsu_legacy_manifest_free(m);
    if (inv) dsu_legacy_invocation_free(inv);

    remove(archive_path);
    remove(archive_bad);
    remove(manifest_ok);
    remove(manifest_fail);
    remove(manifest_traversal);
    remove(invocation_path);
    remove("legacy_test_tmp/state_a.dsus");
    remove("legacy_test_tmp/state_b.dsus");
    remove(log_path);
    remove(file_abs);

    return ok ? 0 : 1;
}
