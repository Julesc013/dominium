/*
FILE: source/dominium/setup/tests/dsu_cli_test.c
MODULE: Dominium Setup
PURPOSE: Plan S-7 CLI contract tests (golden JSON + exit codes + E2E + rollback mock).
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#define DSU_CHDIR _chdir
#define DSU_GETCWD _getcwd
#define DSU_POPEN _popen
#define DSU_PCLOSE _pclose
#else
#include <unistd.h>
#include <sys/wait.h>
#define DSU_CHDIR chdir
#define DSU_GETCWD getcwd
#define DSU_POPEN popen
#define DSU_PCLOSE pclose
#endif

#include "dsu/dsu_ctx.h"
#include "dsu/dsu_fs.h"
#include "dsu/dsu_manifest.h"

#include "../core/src/fs/dsu_platform_iface.h"
#include "../core/src/txn/dsu_journal.h"

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

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t nw;
    if (!path) return 0;
    f = fopen(path, "wb");
    if (!f) return 0;
    nw = fwrite(bytes, 1u, (size_t)len, f);
    fclose(f);
    return nw == (size_t)len;
}

static int read_all_bytes(const char *path, unsigned char **out_bytes, unsigned long *out_len) {
    FILE *f;
    unsigned char *p;
    unsigned long len;
    size_t n;
    if (out_bytes) *out_bytes = NULL;
    if (out_len) *out_len = 0ul;
    if (!path || !out_bytes || !out_len) return 0;
    f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 0;
    }
    len = (unsigned long)ftell(f);
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    p = (unsigned char *)malloc((size_t)(len + 1ul));
    if (!p && len != 0ul) {
        fclose(f);
        return 0;
    }
    n = fread(p, 1u, (size_t)len, f);
    fclose(f);
    if (n != (size_t)len) {
        free(p);
        return 0;
    }
    p[len] = 0u;
    *out_bytes = p;
    *out_len = len;
    return 1;
}

static int path_join(const char *a, const char *b, char *out_path, unsigned long out_cap) {
    dsu_status_t st;
    if (!out_path || out_cap == 0ul) return 0;
    out_path[0] = '\0';
    st = dsu_fs_path_join(a, b, out_path, (dsu_u32)out_cap);
    return st == DSU_STATUS_SUCCESS;
}

static int mkdir_p_rel(const char *rel_path) {
    char canon[1024];
    unsigned long i;
    unsigned long n;
    dsu_status_t st;
    if (!rel_path) return 0;
    if (rel_path[0] == '\0') return 1;
    st = dsu_fs_path_canonicalize(rel_path, canon, (dsu_u32)sizeof(canon));
    if (st != DSU_STATUS_SUCCESS) return 0;
    n = (unsigned long)strlen(canon);
    if (n == 0ul) return 1;
    for (i = 0ul; i <= n; ++i) {
        char c = canon[i];
        if (c == '/' || c == '\0') {
            char part[1024];
            if (i == 0ul) continue;
            if (i >= (unsigned long)sizeof(part)) return 0;
            memcpy(part, canon, (size_t)i);
            part[i] = '\0';
            if (dsu_platform_mkdir(part) != DSU_STATUS_SUCCESS) return 0;
        }
    }
    return 1;
}

static dsu_status_t rm_rf(const char *path) {
    dsu_u8 exists;
    dsu_u8 is_dir;
    dsu_u8 is_symlink;
    dsu_status_t st;
    dsu_platform_dir_entry_t *ents = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;
    if (!path || path[0] == '\0') return DSU_STATUS_INVALID_ARGS;
    st = dsu_platform_path_info(path, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS) return st;
    if (!exists) return DSU_STATUS_SUCCESS;
    if (is_symlink || !is_dir) {
        return dsu_platform_remove_file(path);
    }
    st = dsu_platform_list_dir(path, &ents, &count);
    if (st != DSU_STATUS_SUCCESS) return st;
    for (i = 0u; i < count; ++i) {
        const char *name = ents[i].name ? ents[i].name : "";
        char child[1024];
        if (name[0] == '\0') continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;
        if (!path_join(path, name, child, (unsigned long)sizeof(child))) {
            dsu_platform_free_dir_entries(ents, count);
            return DSU_STATUS_INVALID_ARGS;
        }
        st = rm_rf(child);
        if (st != DSU_STATUS_SUCCESS) {
            dsu_platform_free_dir_entries(ents, count);
            return st;
        }
    }
    dsu_platform_free_dir_entries(ents, count);
    return dsu_platform_rmdir(path);
}

static int file_exists(const char *path) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    if (!path) return 0;
    if (dsu_platform_path_info(path, &exists, &is_dir, &is_symlink) != DSU_STATUS_SUCCESS) return 0;
    return exists && !is_dir;
}

static int expect(int ok, const char *msg) {
    if (ok) return 1;
    fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 0;
}

static int expect_bytes_equal(const unsigned char *a, unsigned long alen,
                              const unsigned char *b, unsigned long blen,
                              const char *msg) {
    unsigned long i;
    if (alen != blen) {
        fprintf(stderr, "FAIL: %s (len %lu != %lu)\n", msg ? msg : "(null)", alen, blen);
        return 0;
    }
    for (i = 0ul; i < alen; ++i) {
        if (a[i] != b[i]) {
            fprintf(stderr, "FAIL: %s (mismatch at %lu: %u != %u)\n",
                    msg ? msg : "(null)", i, (unsigned)a[i], (unsigned)b[i]);
            return 0;
        }
    }
    return 1;
}

static int build_cmdline(const char *cli_path, const char *args, char out[4096]) {
    unsigned long need;
    unsigned long i = 0ul;
    if (!cli_path || !out) return 0;
    if (!args) args = "";
    need = (unsigned long)strlen(cli_path) + (unsigned long)strlen(args) + 4ul;
    if (need >= 4096ul) return 0;
    out[i++] = '"';
    memcpy(out + i, cli_path, strlen(cli_path));
    i += (unsigned long)strlen(cli_path);
    out[i++] = '"';
    if (args[0] != '\0') {
        out[i++] = ' ';
        memcpy(out + i, args, strlen(args));
        i += (unsigned long)strlen(args);
    }
    out[i] = '\0';
    return 1;
}

static int run_capture(const char *cli_path,
                       const char *args,
                       unsigned char **out_stdout,
                       unsigned long *out_stdout_len,
                       int *out_exit_code) {
    char cmdline[4096];
    FILE *p;
    buf_t b;
    unsigned char tmp[4096];
    size_t n;
    int status;

    if (out_stdout) *out_stdout = NULL;
    if (out_stdout_len) *out_stdout_len = 0ul;
    if (out_exit_code) *out_exit_code = 1;
    if (!cli_path || !out_stdout || !out_stdout_len || !out_exit_code) return 0;
    if (!build_cmdline(cli_path, args, cmdline)) return 0;

    memset(&b, 0, sizeof(b));
    p = DSU_POPEN(cmdline, "rb");
    if (!p) return 0;
    while ((n = fread(tmp, 1u, sizeof(tmp), p)) != 0u) {
        if (!buf_append(&b, tmp, (unsigned long)n)) {
            DSU_PCLOSE(p);
            buf_free(&b);
            return 0;
        }
    }
    status = DSU_PCLOSE(p);

#if defined(_WIN32)
    *out_exit_code = status;
#else
    if (WIFEXITED(status)) {
        *out_exit_code = WEXITSTATUS(status);
    } else {
        *out_exit_code = 1;
    }
#endif

    *out_stdout = b.data;
    *out_stdout_len = b.len;
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

static int write_manifest_fileset(const char *manifest_path,
                                  const char *install_root_path,
                                  const char *payload_path,
                                  const char *component_id) {
    /* TLV types from docs/setup/MANIFEST_SCHEMA.md */
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
    const unsigned short T_PAYLOAD = 0x004Cu;
    const unsigned short T_P_VER = 0x004Du;
    const unsigned short T_P_KIND = 0x004Eu;
    const unsigned short T_P_PATH = 0x004Fu;
    const unsigned short T_P_SHA256 = 0x0050u;

    buf_t root;
    buf_t payload;
    buf_t ir;
    buf_t comp;
    buf_t pl;
    buf_t file;
    unsigned char magic[4];
    unsigned char sha0[32];

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp, 0, sizeof(comp));
    memset(&pl, 0, sizeof(pl));
    memset(&file, 0, sizeof(file));
    memset(sha0, 0, sizeof(sha0));
    magic[0] = 'D';
    magic[1] = 'S';
    magic[2] = 'U';
    magic[3] = 'M';

    if (!manifest_path || !install_root_path || !payload_path || !component_id) {
        return 0;
    }

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, "1.0.0")) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, "stable")) goto fail;
    if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, "any-any")) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_SCOPE, 0u)) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PLATFORM, "any-any")) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, install_root_path)) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT, ir.data, ir.len)) goto fail;

    if (!buf_put_tlv_u32(&pl, T_P_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&pl, T_P_KIND, 0u)) goto fail; /* fileset */
    if (!buf_put_tlv_str(&pl, T_P_PATH, payload_path)) goto fail;
    if (!buf_put_tlv(&pl, T_P_SHA256, sha0, 32ul)) goto fail;

    if (!buf_put_tlv_u32(&comp, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, T_C_ID, component_id)) goto fail;
    if (!buf_put_tlv_u8(&comp, T_C_KIND, (unsigned char)DSU_MANIFEST_COMPONENT_KIND_OTHER)) goto fail;
    if (!buf_put_tlv_u32(&comp, T_C_FLAGS, 0ul)) goto fail;
    if (!buf_put_tlv(&comp, T_PAYLOAD, pl.data, pl.len)) goto fail;
    if (!buf_put_tlv(&root, T_COMPONENT, comp.data, comp.len)) goto fail;

    if (!buf_put_tlv(&payload, T_ROOT, root.data, root.len)) goto fail;
    if (!wrap_file(&file, magic, (unsigned short)DSU_MANIFEST_FORMAT_VERSION, &payload)) goto fail;

    if (!write_bytes_file(manifest_path, file.data, file.len)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&pl);
    buf_free(&file);
    return 1;

fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&pl);
    buf_free(&file);
    return 0;
}

static int golden_path(const char *src_dir, const char *rel, char out_path[1024]) {
    if (!src_dir || !rel || !out_path) return 0;
    out_path[0] = '\0';
    if (!path_join(src_dir, rel, out_path, 1024ul)) return 0;
    return 1;
}

static int expect_golden_stdout(const char *src_dir,
                               const char *golden_rel_path,
                               const unsigned char *stdout_bytes,
                               unsigned long stdout_len,
                               const char *msg) {
    unsigned char *gold = NULL;
    unsigned long gold_len = 0ul;
    char gp[1024];
    int ok = 1;
    ok &= expect(golden_path(src_dir, golden_rel_path, gp), "golden path");
    ok &= expect(read_all_bytes(gp, &gold, &gold_len), "read golden");
    ok &= expect_bytes_equal(stdout_bytes, stdout_len, gold, gold_len, msg);
    free(gold);
    return ok;
}

static int expect_golden_file(const char *src_dir,
                              const char *golden_rel_path,
                              const char *file_path,
                              const char *msg) {
    unsigned char *file_bytes = NULL;
    unsigned long file_len = 0ul;
    int ok = 1;
    ok &= expect(read_all_bytes(file_path, &file_bytes, &file_len), "read file");
    if (ok) {
        ok &= expect_golden_stdout(src_dir, golden_rel_path, file_bytes, file_len, msg);
    }
    free(file_bytes);
    return ok;
}

int main(int argc, char **argv) {
    const char *cli_path = (argc >= 2) ? argv[1] : NULL;
    const char *src_dir = (argc >= 3) ? argv[2] : NULL;
    char cwd[1024];
    int ok = 1;

    if (!cli_path || !src_dir) {
        fprintf(stderr, "usage: dsu_cli_test <dominium-setup-exe> <tests-src-dir>\n");
        return 1;
    }

    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) {
        fprintf(stderr, "error: getcwd failed\n");
        return 1;
    }

    (void)rm_rf("dsu_cli_test_run");
    ok &= expect(mkdir_p_rel("dsu_cli_test_run/payload/bin"), "mkdir payload/bin");
    ok &= expect(mkdir_p_rel("dsu_cli_test_run/payload/data"), "mkdir payload/data");
    ok &= expect(mkdir_p_rel("dsu_cli_test_run/install"), "mkdir install");
    if (!ok) return 1;

    ok &= expect(write_bytes_file("dsu_cli_test_run/payload/bin/hello.txt",
                                 (const unsigned char *)"hello\n", 6ul),
                 "write payload hello");
    ok &= expect(write_bytes_file("dsu_cli_test_run/payload/data/config.json",
                                 (const unsigned char *)"{\"k\":1}\n", 8ul),
                 "write payload config");
    if (!ok) return 1;

    ok &= expect(DSU_CHDIR("dsu_cli_test_run") == 0, "chdir run");
    if (!ok) return 1;

    ok &= expect(write_manifest_fileset("m.dsumanifest", "install", "payload", "core"), "write manifest");
    if (!ok) return 1;

    /* Golden JSON: manifest dump */
    {
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 1;
        ok &= expect(run_capture(cli_path,
                                 "manifest dump --in m.dsumanifest --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "run manifest dump");
        ok &= expect(ec == 0, "manifest dump exit 0");
        ok &= expect_golden_stdout(src_dir, "golden/cli/manifest_dump_core.json", out, out_len, "manifest dump golden");
        free(out);
    }

    /* Golden JSON: version */
    {
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 1;
        ok &= expect(run_capture(cli_path, "version", &out, &out_len, &ec), "run version");
        ok &= expect(ec == 0, "version exit 0");
        ok &= expect_golden_stdout(src_dir, "golden/cli/version.json", out, out_len, "version golden");
        free(out);
    }

    /* Golden JSON: resolve + plan over a deterministic manifest */
    {
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 1;
        ok &= expect(run_capture(cli_path,
                                 "resolve --manifest m.dsumanifest --op install --scope portable --components core --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "run resolve");
        ok &= expect(ec == 0, "resolve exit 0");
        ok &= expect_golden_stdout(src_dir, "golden/cli/resolve_install_core.json", out, out_len, "resolve golden");
        free(out);
    }
    {
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 1;
        ok &= expect(run_capture(cli_path,
                                 "plan --manifest m.dsumanifest --op install --scope portable --components core --out out.dsuplan --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "run plan");
        ok &= expect(ec == 0, "plan exit 0");
        ok &= expect_golden_stdout(src_dir, "golden/cli/plan_install_core.json", out, out_len, "plan golden");
        free(out);
    }

    /* Invalid args exit codes (v1) */
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path, "manifest dump", &out, &out_len, &ec), "run manifest dump (missing args)");
        ok &= expect(ec == 3, "manifest dump missing args => 3");
        free(out);
    }
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path, "apply", &out, &out_len, &ec), "run apply (missing args)");
        ok &= expect(ec == 3, "apply missing args => 3");
        free(out);
    }

    /* E2E: plan -> apply(dry-run) -> apply -> report */
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path, "apply --plan out.dsuplan --dry-run --deterministic 1", &out, &out_len, &ec), "apply dry-run");
        ok &= expect(ec == 0, "apply dry-run exit 0");
        free(out);
    }
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path, "apply --plan out.dsuplan --deterministic 1", &out, &out_len, &ec), "apply");
        ok &= expect(ec == 0, "apply exit 0");
        free(out);
    }
    ok &= expect(file_exists("install/bin/hello.txt"), "installed hello exists");
    ok &= expect(file_exists("install/data/config.json"), "installed config exists");
    ok &= expect(file_exists("install/.dsu/installed_state.dsustate"), "state exists");

    /* Golden JSON: verify */
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path,
                                 "verify --state install/.dsu/installed_state.dsustate --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "verify");
        ok &= expect(ec == 0, "verify exit 0");
        ok &= expect_golden_stdout(src_dir, "golden/cli/verify_install_core.json", out, out_len, "verify golden");
        free(out);
    }
    {
        int ec = 0;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        ok &= expect(run_capture(cli_path,
                                 "report --state install/.dsu/installed_state.dsustate --out report --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "report");
        ok &= expect(ec == 0, "report exit 0");
        free(out);
    }
    ok &= expect(file_exists("report/inventory.json"), "report inventory exists");
    ok &= expect(file_exists("report/verify.json"), "report verify exists");

    /* Rollback: mocked journal (dry-run) */
    {
        char cwd2[1024];
        char install_abs[1024];
        char txn_abs[1024];
        dsu_journal_writer_t w;
        dsu_status_t st;
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 0;

        memset(&w, 0, sizeof(w));

        ok &= expect(mkdir_p_rel("jr_install"), "mkdir jr_install");
        ok &= expect(mkdir_p_rel("jr_txn"), "mkdir jr_txn");
        st = dsu_platform_get_cwd(cwd2, (dsu_u32)sizeof(cwd2));
        ok &= expect(st == DSU_STATUS_SUCCESS, "get cwd");
        ok &= expect(path_join(cwd2, "jr_install", install_abs, (unsigned long)sizeof(install_abs)), "join install abs");
        ok &= expect(path_join(cwd2, "jr_txn", txn_abs, (unsigned long)sizeof(txn_abs)), "join txn abs");
        if (!ok) return 1;

        st = dsu_journal_writer_open(&w, "mock.dsu.journal", (dsu_u64)0x1122334455667788ULL, (dsu_u64)0x99AABBCCDDEEFF00ULL);
        ok &= expect(st == DSU_STATUS_SUCCESS, "journal open");
        st = dsu_journal_writer_write_meta(&w, install_abs, txn_abs, ".dsu/installed_state.dsustate");
        ok &= expect(st == DSU_STATUS_SUCCESS, "journal write_meta");
        st = dsu_journal_writer_append_progress(&w, 0u);
        ok &= expect(st == DSU_STATUS_SUCCESS, "journal progress");
        st = dsu_journal_writer_close(&w);
        ok &= expect(st == DSU_STATUS_SUCCESS, "journal close");
        if (!ok) return 1;

        ok &= expect(run_capture(cli_path, "rollback --journal mock.dsu.journal --dry-run --deterministic 1", &out, &out_len, &ec), "rollback dry-run");
        ok &= expect(ec == 0, "rollback dry-run exit 0");
        free(out);
    }

    /* Export log: json + txt */
    {
        unsigned char *out = NULL;
        unsigned long out_len = 0ul;
        int ec = 0;
        ok &= expect(run_capture(cli_path,
                                 "export-log --log audit.dsu.log --out audit.json --format json --deterministic 1",
                                 &out, &out_len, &ec),
                     "export-log json");
        ok &= expect(ec == 0, "export-log json exit 0");
        free(out);
        ok &= expect(file_exists("audit.json"), "audit.json exists");
        ok &= expect_golden_file(src_dir, "golden/cli/export_log.json", "audit.json", "export-log golden");
        ok &= expect(run_capture(cli_path, "export-log --log audit.dsu.log --out audit.tsv --format txt", &out, &out_len, &ec), "export-log txt");
        ok &= expect(ec == 0, "export-log txt exit 0");
        free(out);
        ok &= expect(file_exists("audit.tsv"), "audit.tsv exists");
    }

    /* Cleanup + restore cwd */
    ok &= expect(DSU_CHDIR(cwd) == 0, "chdir restore");
    (void)rm_rf("dsu_cli_test_run");

    return ok ? 0 : 1;
}
