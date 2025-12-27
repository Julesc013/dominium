/*
FILE: source/dominium/setup/tests/dsu_setup_matrix_test.c
MODULE: Dominium Setup
PURPOSE: Plan S-9 integration matrix tests with sandboxed CLI runs.
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

#include "dsu/dsu_fs.h"
#include "dsu/dsu_manifest.h"

#include "../core/src/fs/dsu_platform_iface.h"

typedef struct buf_t {
    unsigned char *data;
    unsigned long len;
    unsigned long cap;
} buf_t;

typedef struct test_env_t {
    const char *cli_path;
    const char *steam_path;
    const char *linux_path;
    const char *repo_root;
} test_env_t;

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
    buf = (unsigned char *)malloc((size_t)sz + 1u);
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
    buf[sz] = 0u;
    *out_bytes = buf;
    *out_len = (unsigned long)sz;
    return 1;
}

static int bytes_equal(const unsigned char *a, unsigned long a_len,
                       const unsigned char *b, unsigned long b_len) {
    if (a_len != b_len) return 0;
    if (a_len == 0ul) return 1;
    if (!a || !b) return 0;
    return memcmp(a, b, (size_t)a_len) == 0;
}

static int bytes_contains(const unsigned char *hay, unsigned long hay_len, const char *needle) {
    unsigned long i;
    unsigned long n;
    if (!hay || !needle) return 0;
    n = (unsigned long)strlen(needle);
    if (n == 0ul) return 1;
    if (n > hay_len) return 0;
    for (i = 0ul; i + n <= hay_len; ++i) {
        if (memcmp(hay + i, needle, (size_t)n) == 0) return 1;
    }
    return 0;
}

static int path_join(const char *a, const char *b, char *out_path, unsigned long out_cap) {
    dsu_status_t st;
    if (!out_path || out_cap == 0ul) return 0;
    out_path[0] = '\0';
    st = dsu_fs_path_join(a, b, out_path, (dsu_u32)out_cap);
    return st == DSU_STATUS_SUCCESS;
}

static int path_copy(const char *src, char *dst, unsigned long dst_cap) {
    unsigned long n;
    if (!src || !dst || dst_cap == 0ul) return 0;
    n = (unsigned long)strlen(src);
    if (n + 1ul > dst_cap) return 0;
    memcpy(dst, src, (size_t)n);
    dst[n] = '\0';
    return 1;
}

static void path_to_dsu_inplace(char *s) {
    unsigned long i;
    if (!s) return;
    for (i = 0ul; s[i] != '\0'; ++i) {
        if (s[i] == '\\') s[i] = '/';
    }
}

static int mkdir_p_path(const char *path) {
    char canon[1024];
    unsigned long i;
    unsigned long n;
    dsu_status_t st;
    if (!path) return 0;
    if (path[0] == '\0') return 1;
    st = dsu_fs_path_canonicalize(path, canon, (dsu_u32)sizeof(canon));
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

static int dir_exists(const char *path) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    if (!path) return 0;
    if (dsu_platform_path_info(path, &exists, &is_dir, &is_symlink) != DSU_STATUS_SUCCESS) return 0;
    return exists && is_dir && !is_symlink;
}

static int copy_file(const char *src, const char *dst) {
    FILE *in;
    FILE *out;
    unsigned char buf[32768];
    size_t n;
    if (!src || !dst) return 0;
    in = fopen(src, "rb");
    if (!in) return 0;
    out = fopen(dst, "wb");
    if (!out) {
        fclose(in);
        return 0;
    }
    while ((n = fread(buf, 1u, sizeof(buf), in)) != 0u) {
        if (fwrite(buf, 1u, n, out) != n) {
            fclose(in);
            fclose(out);
            return 0;
        }
    }
    fclose(in);
    if (fclose(out) != 0) return 0;
    return 1;
}

static int copy_tree(const char *src, const char *dst) {
    dsu_u8 exists = 0u;
    dsu_u8 is_dir = 0u;
    dsu_u8 is_symlink = 0u;
    dsu_platform_dir_entry_t *ents = NULL;
    dsu_u32 count = 0u;
    dsu_u32 i;
    dsu_status_t st;
    if (!src || !dst) return 0;
    st = dsu_platform_path_info(src, &exists, &is_dir, &is_symlink);
    if (st != DSU_STATUS_SUCCESS || !exists) return 0;
    if (!is_dir || is_symlink) {
        return copy_file(src, dst);
    }
    if (!mkdir_p_path(dst)) return 0;
    st = dsu_platform_list_dir(src, &ents, &count);
    if (st != DSU_STATUS_SUCCESS) return 0;
    for (i = 0u; i < count; ++i) {
        const char *name = ents[i].name ? ents[i].name : "";
        char src_child[1024];
        char dst_child[1024];
        if (name[0] == '\0') continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;
        if (!path_join(src, name, src_child, (unsigned long)sizeof(src_child))) {
            dsu_platform_free_dir_entries(ents, count);
            return 0;
        }
        if (!path_join(dst, name, dst_child, (unsigned long)sizeof(dst_child))) {
            dsu_platform_free_dir_entries(ents, count);
            return 0;
        }
        if (!copy_tree(src_child, dst_child)) {
            dsu_platform_free_dir_entries(ents, count);
            return 0;
        }
    }
    dsu_platform_free_dir_entries(ents, count);
    return 1;
}

static int expect(int ok, const char *msg) {
    if (ok) return 1;
    fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 0;
}

static int build_cmdline(const char *cli_path, const char *args, char out[4096]) {
    unsigned long need;
    unsigned long i = 0ul;
    if (!cli_path || !out) return 0;
    if (!args) args = "";
    need = (unsigned long)strlen(cli_path) + (unsigned long)strlen(args) + 16ul;
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
    memcpy(out + i, " 2>&1", 5u);
    i += 5u;
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

static int run_capture_to_file(const char *cli_path,
                               const char *args,
                               const char *out_path,
                               int *out_exit_code) {
    unsigned char *out = NULL;
    unsigned long out_len = 0ul;
    int ec = 1;
    int ok = run_capture(cli_path, args, &out, &out_len, &ec);
    if (ok && out_path) {
        ok = write_bytes_file(out_path, out, out_len);
    }
    if (out_exit_code) *out_exit_code = ec;
    if (ok && ec != 0) ok = 0;
    free(out);
    return ok;
}

static int run_capture_expect_fail(const char *cli_path,
                                   const char *args,
                                   const char *out_path) {
    unsigned char *out = NULL;
    unsigned long out_len = 0ul;
    int ec = 1;
    int ok = run_capture(cli_path, args, &out, &out_len, &ec);
    if (ok && out_path) {
        ok = write_bytes_file(out_path, out, out_len);
    }
    if (ok) ok = (ec != 0);
    free(out);
    return ok;
}

static int set_env_var(const char *key, const char *val) {
#if defined(_WIN32)
    if (!key) return 0;
    if (!val) val = "";
    return _putenv_s(key, val) == 0;
#else
    if (!key) return 0;
    if (!val) return unsetenv(key) == 0;
    return setenv(key, val, 1) == 0;
#endif
}

static int write_manifest_fileset_abs(const char *manifest_path,
                                      const char *install_root_path,
                                      const char *payload_path,
                                      const char *component_id) {
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
    if (!buf_put_tlv_u8(&pl, T_P_KIND, 0u)) goto fail;
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

static int copy_fixtures(const test_env_t *env, const char *sandbox_root) {
    char fixtures_root[1024];
    char payload_src[1024];
    char manifest_src[1024];
    char user_src[1024];
    char payload_dst[1024];
    char manifest_dst[1024];
    char user_dst[1024];
    if (!env || !sandbox_root) return 0;
    if (!path_join(env->repo_root, "source/dominium/setup/tests/fixtures", fixtures_root, (unsigned long)sizeof(fixtures_root))) return 0;
    if (!path_join(fixtures_root, "payloads", payload_src, (unsigned long)sizeof(payload_src))) return 0;
    if (!path_join(fixtures_root, "manifests", manifest_src, (unsigned long)sizeof(manifest_src))) return 0;
    if (!path_join(fixtures_root, "user_data", user_src, (unsigned long)sizeof(user_src))) return 0;
    if (!path_join(sandbox_root, "payloads", payload_dst, (unsigned long)sizeof(payload_dst))) return 0;
    if (!path_join(sandbox_root, "manifests", manifest_dst, (unsigned long)sizeof(manifest_dst))) return 0;
    if (!path_join(sandbox_root, "user_data", user_dst, (unsigned long)sizeof(user_dst))) return 0;
    if (!copy_tree(payload_src, payload_dst)) return 0;
    if (!copy_tree(manifest_src, manifest_dst)) return 0;
    if (dir_exists(user_src)) {
        if (!copy_tree(user_src, user_dst)) return 0;
    }
    return 1;
}

static int sandbox_prepare(const test_env_t *env, const char *test_name, char *out_path, unsigned long out_cap) {
    char base[1024];
    if (!env || !test_name || !out_path) return 0;
    if (!path_join(env->repo_root, "build/tests/sandbox", base, (unsigned long)sizeof(base))) return 0;
    if (!path_join(base, test_name, out_path, out_cap)) return 0;
    (void)rm_rf(out_path);
    if (!mkdir_p_path(out_path)) return 0;
    return copy_fixtures(env, out_path);
}

static int read_text_contains(const char *path, const char *needle) {
    unsigned char *bytes = NULL;
    unsigned long len = 0ul;
    int ok = 0;
    if (!read_all_bytes(path, &bytes, &len)) return 0;
    ok = bytes_contains(bytes, len, needle);
    free(bytes);
    return ok;
}

static int compare_files(const char *a, const char *b) {
    unsigned char *ab = NULL;
    unsigned char *bb = NULL;
    unsigned long al = 0ul;
    unsigned long bl = 0ul;
    int ok = 0;
    if (!read_all_bytes(a, &ab, &al)) goto done;
    if (!read_all_bytes(b, &bb, &bl)) goto done;
    ok = bytes_equal(ab, al, bb, bl);
done:
    free(ab);
    free(bb);
    return ok;
}

static int run_cli_json_expect(const char *cli_path,
                               const char *args,
                               const char *out_path,
                               int expected_exit,
                               const char *expect_snippet) {
    unsigned char *out = NULL;
    unsigned long out_len = 0ul;
    int ec = 1;
    int ok = run_capture(cli_path, args, &out, &out_len, &ec);
    if (ok && out_path) {
        ok = write_bytes_file(out_path, out, out_len);
    }
    if (ok) {
        ok &= (ec == expected_exit);
    }
    if (ok && expect_snippet) {
        ok &= bytes_contains(out, out_len, expect_snippet);
    }
    free(out);
    return ok;
}

static int cli_exists(const char *p) {
    return p && p[0] != '\0' && strcmp(p, "NONE") != 0 && file_exists(p);
}

static int test_install_fresh_portable(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char plan[1024];
    char install_root[1024];
    char file_launcher[1024];
    char file_runtime[1024];
    char file_tools[1024];
    char file_pack[1024];
    char state_path[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_install_fresh_portable", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("plan.dsuplan", plan, (unsigned long)sizeof(plan)), "plan path");
    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, "bin/launcher.txt", file_launcher, (unsigned long)sizeof(file_launcher)), "launcher path");
    ok &= expect(path_join(install_root, "runtime/runtime.txt", file_runtime, (unsigned long)sizeof(file_runtime)), "runtime path");
    ok &= expect(path_join(install_root, "tools/tools.txt", file_tools, (unsigned long)sizeof(file_tools)), "tools path");
    ok &= expect(path_join(install_root, "packs/pack.txt", file_pack, (unsigned long)sizeof(file_pack)), "pack path");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state path");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation portable");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install portable");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install portable");
    ok &= expect(file_exists(file_launcher), "launcher exists");
    ok &= expect(file_exists(file_runtime), "runtime exists");
    ok &= expect(file_exists(file_tools), "tools exists");
    ok &= expect(file_exists(file_pack), "pack exists");
    ok &= expect(file_exists(state_path), "state exists");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_install_fresh_user_scope(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char file_launcher[1024];
    char state_path[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_install_fresh_user_scope", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_user", install_root, (unsigned long)sizeof(install_root)), "install root user");
    ok &= expect(path_join(install_root, "bin/launcher.txt", file_launcher, (unsigned long)sizeof(file_launcher)), "launcher user");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state user");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope user --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation user");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install user");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install user");
    ok &= expect(file_exists(file_launcher), "launcher user exists");
    ok &= expect(file_exists(state_path), "state user exists");

    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_upgrade_in_place(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char state_path[1024];
    char version_file[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_upgrade_in_place", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state path");
    ok &= expect(path_join(install_root, "bin/version.txt", version_file, (unsigned long)sizeof(version_file)), "version file");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/upgrade_v1.dsumanifest --op install --scope portable --components core --out v1.dsuinv --format json --deterministic 1",
                                    "invocation_v1.json",
                                    NULL),
                 "export invocation v1");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/upgrade_v1.dsumanifest --invocation v1.dsuinv --out v1.dsuplan --format json --deterministic 1",
                                    "plan_v1.json",
                                    NULL),
                 "plan v1");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan v1.dsuplan --deterministic 1", "apply_v1.txt", NULL),
                 "apply v1");
    ok &= expect(read_text_contains(version_file, "version v1"), "version v1 content");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/upgrade_v2.dsumanifest --state install_portable/.dsu/installed_state.dsustate --op upgrade --scope portable --components core --out v2.dsuinv --format json --deterministic 1",
                                    "invocation_v2.json",
                                    NULL),
                 "export invocation v2");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/upgrade_v2.dsumanifest --state install_portable/.dsu/installed_state.dsustate --invocation v2.dsuinv --out v2.dsuplan --format json --deterministic 1",
                                    "plan_v2.json",
                                    NULL),
                 "plan v2 upgrade");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan v2.dsuplan --deterministic 1", "apply_v2.txt", NULL),
                 "apply v2");
    ok &= expect(read_text_contains(version_file, "version v2"), "version v2 content");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_upgrade_side_by_side(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_upgrade_side_by_side", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/upgrade_v1.dsumanifest --op install --scope portable --components core --out v1.dsuinv --format json --deterministic 1",
                                    "invocation_v1.json",
                                    NULL),
                 "export invocation v1");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/upgrade_v1.dsumanifest --invocation v1.dsuinv --out v1.dsuplan --format json --deterministic 1",
                                    "plan_v1.json",
                                    NULL),
                 "plan v1");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan v1.dsuplan --deterministic 1", "apply_v1.txt", NULL),
                 "apply v1");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                     "export-invocation --manifest manifests/upgrade_v2.dsumanifest --state install_portable/.dsu/installed_state.dsustate --op upgrade --scope user --components core --out v2_side.dsuinv --format json --deterministic 1",
                                     "invocation_side.json",
                                     NULL),
                 "export invocation side");
    ok &= expect(run_cli_json_expect(env->cli_path,
                                     "plan --manifest manifests/upgrade_v2.dsumanifest --state install_portable/.dsu/installed_state.dsustate --invocation v2_side.dsuinv --out v2_side.dsuplan --format json --deterministic 1",
                                     "plan_side.json",
                                     3,
                                     "\"status_code\":3"),
                 "side-by-side upgrade rejected");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_repair_restores_missing_files(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char tools_file[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_repair_restores_missing_files", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, "tools/tools.txt", tools_file, (unsigned long)sizeof(tools_file)), "tools file");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install");
    ok &= expect(file_exists(tools_file), "tools file exists");
    if (!ok) goto done;

    ok &= expect(remove(tools_file) == 0, "remove tools file");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --state install_portable/.dsu/installed_state.dsustate --op repair --scope portable --components core --out repair.dsuinv --format json --deterministic 1",
                                    "invocation_repair.json",
                                    NULL),
                 "export invocation repair");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --state install_portable/.dsu/installed_state.dsustate --invocation repair.dsuinv --out repair.dsuplan --format json --deterministic 1",
                                    "plan_repair.json",
                                    NULL),
                 "plan repair");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan repair.dsuplan --deterministic 1", "apply_repair.txt", NULL),
                 "apply repair");
    ok &= expect(file_exists(tools_file), "tools file restored");
    ok &= expect(read_text_contains(tools_file, "tools"), "tools content restored");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_uninstall_preserves_user_data(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char launcher_file[1024];
    char user_dir[1024];
    char user_file[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_uninstall_preserves_user_data", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, "bin/launcher.txt", launcher_file, (unsigned long)sizeof(launcher_file)), "launcher file");
    ok &= expect(path_join(install_root, "user", user_dir, (unsigned long)sizeof(user_dir)), "user dir");
    ok &= expect(path_join(user_dir, "marker.txt", user_file, (unsigned long)sizeof(user_file)), "user marker");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install");
    ok &= expect(file_exists(launcher_file), "launcher exists");
    ok &= expect(mkdir_p_path(user_dir), "mkdir user dir");
    ok &= expect(copy_file("user_data/user_marker.txt", user_file), "copy user marker");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "uninstall --state install_portable/.dsu/installed_state.dsustate --log uninstall.dsu.log --deterministic 1",
                                    "uninstall.txt",
                                    NULL),
                 "uninstall");
    ok &= expect(!file_exists(launcher_file), "launcher removed");
    ok &= expect(file_exists(user_file), "user marker preserved");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_uninstall_removes_owned_files(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char launcher_file[1024];
    char state_path[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_uninstall_removes_owned_files", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, "bin/launcher.txt", launcher_file, (unsigned long)sizeof(launcher_file)), "launcher file");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state file");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install");
    ok &= expect(file_exists(launcher_file), "launcher exists");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "uninstall --state install_portable/.dsu/installed_state.dsustate --log uninstall.dsu.log --deterministic 1",
                                    "uninstall.txt",
                                    NULL),
                 "uninstall");
    ok &= expect(!file_exists(launcher_file), "launcher removed");
    ok &= expect(!file_exists(state_path), "state removed");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_verify_detects_modified_file(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char launcher_file[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_verify_detects_modified_file", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_join("install_portable", "bin/launcher.txt", launcher_file, (unsigned long)sizeof(launcher_file)), "launcher file");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply install");
    ok &= expect(write_bytes_file(launcher_file, (const unsigned char *)"tamper\n", 7ul), "modify file");
    if (!ok) goto done;

    ok &= expect(run_cli_json_expect(env->cli_path,
                                     "verify --state install_portable/.dsu/installed_state.dsustate --format json --deterministic 1",
                                     "verify.json",
                                     2,
                                     "\"status_code\":2"),
                 "verify detects modification");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_rollback_on_commit_failure(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    char install_root[1024];
    char bin_dir[1024];
    char launcher_file[1024];
    char state_path[1024];
    int ok = 1;

    ok &= expect(sandbox_prepare(env, "test_rollback_on_commit_failure", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(path_copy("install_portable", install_root, (unsigned long)sizeof(install_root)), "install root");
    ok &= expect(path_join(install_root, "bin", bin_dir, (unsigned long)sizeof(bin_dir)), "bin dir");
    ok &= expect(path_join(bin_dir, "launcher.txt", launcher_file, (unsigned long)sizeof(launcher_file)), "launcher file");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state path");
    ok &= expect(mkdir_p_path(bin_dir), "mkdir bin");
    ok &= expect(write_bytes_file(launcher_file, (const unsigned char *)"OLD\n", 4ul), "write old launcher");
    if (!ok) goto done;

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan install");
    if (!ok) goto done;

    ok &= expect(set_env_var("DSU_FAILPOINT", "mid_commit:1"), "set failpoint");
    ok &= expect(run_capture_expect_fail(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt"),
                 "apply with failpoint");
    ok &= expect(set_env_var("DSU_FAILPOINT", ""), "clear failpoint");
    ok &= expect(read_text_contains(launcher_file, "OLD"), "rollback restored old file");
    ok &= expect(!file_exists(state_path), "state not written");

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_plan_determinism_repeat_run(const test_env_t *env) {
    char base[1024];
    char run_a[1024];
    char run_b[1024];
    char shared_install[1024];
    char shared_install_dsu[1024];
    char cwd[1024];
    char plan_a[1024];
    char plan_b[1024];
    char state_path[1024];
    char audit_a[1024];
    char audit_b[1024];
    unsigned char *state_a = NULL;
    unsigned long state_a_len = 0ul;
    int ok = 1;

    ok &= expect(path_join(env->repo_root, "build/tests/sandbox/test_plan_determinism_repeat_run", base, (unsigned long)sizeof(base)), "base path");
    ok &= expect(path_join(base, "run_a", run_a, (unsigned long)sizeof(run_a)), "run_a path");
    ok &= expect(path_join(base, "run_b", run_b, (unsigned long)sizeof(run_b)), "run_b path");
    ok &= expect(path_join(base, "shared_install", shared_install, (unsigned long)sizeof(shared_install)), "shared install path");
    if (!ok) return 0;

    strcpy(shared_install_dsu, shared_install);
    path_to_dsu_inplace(shared_install_dsu);

    (void)rm_rf(base);
    ok &= expect(mkdir_p_path(run_a), "mkdir run_a");
    ok &= expect(mkdir_p_path(run_b), "mkdir run_b");
    ok &= expect(copy_fixtures(env, run_a), "copy fixtures run_a");
    ok &= expect(copy_fixtures(env, run_b), "copy fixtures run_b");
    if (!ok) return 0;

    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;

    ok &= expect(DSU_CHDIR(run_a) == 0, "chdir run_a");
    ok &= expect(write_manifest_fileset_abs("manifest_abs.dsumanifest", shared_install_dsu, "payloads/base", "core"), "write manifest a");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifest_abs.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation a");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifest_abs.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan a");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply a");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-log --log audit.dsu.log --out audit.json --format json --deterministic 1",
                                    "export_a.txt",
                                    NULL),
                 "export log a");
    ok &= expect(path_join(run_a, "plan.dsuplan", plan_a, (unsigned long)sizeof(plan_a)), "plan_a file");
    ok &= expect(path_join(shared_install, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "state path");
    ok &= expect(path_join(run_a, "audit.json", audit_a, (unsigned long)sizeof(audit_a)), "audit a");
    ok &= expect(DSU_CHDIR(cwd) == 0, "chdir restore");
    if (ok) {
        ok &= expect(read_all_bytes(state_path, &state_a, &state_a_len), "read state a");
    }
    if (!ok) goto done;

    (void)rm_rf(shared_install);
    ok &= expect(mkdir_p_path(shared_install), "reset shared install");
    if (!ok) goto done;

    ok &= expect(DSU_CHDIR(run_b) == 0, "chdir run_b");
    ok &= expect(write_manifest_fileset_abs("manifest_abs.dsumanifest", shared_install_dsu, "payloads/base", "core"), "write manifest b");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifest_abs.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    NULL),
                 "export invocation b");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifest_abs.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    NULL),
                 "plan b");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", NULL),
                 "apply b");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-log --log audit.dsu.log --out audit.json --format json --deterministic 1",
                                    "export_b.txt",
                                    NULL),
                 "export log b");
    ok &= expect(path_join(run_b, "plan.dsuplan", plan_b, (unsigned long)sizeof(plan_b)), "plan_b file");
    ok &= expect(path_join(run_b, "audit.json", audit_b, (unsigned long)sizeof(audit_b)), "audit b");
    ok &= expect(DSU_CHDIR(cwd) == 0, "chdir restore b");
    if (!ok) goto done;

    ok &= expect(compare_files(plan_a, plan_b), "plan bytes deterministic");
    ok &= expect(compare_files(audit_a, audit_b), "audit json deterministic");
    {
        unsigned char *state_b = NULL;
        unsigned long bl = 0ul;
        if (ok) {
            ok &= expect(read_all_bytes(state_path, &state_b, &bl), "read state b");
            ok &= expect(bytes_equal(state_a, state_a_len, state_b, bl), "state bytes deterministic");
        }
        free(state_b);
    }

done:
    free(state_a);
    if (ok) (void)rm_rf(base);
    return ok;
}

static int test_steam_lifecycle_simulation_mock(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    int ok = 1;
    int ec = 1;

    ok &= expect(sandbox_prepare(env, "test_steam_lifecycle_simulation_mock", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    &ec),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    &ec),
                 "plan install");
    ok &= expect(ec == 0, "plan exit 0");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", &ec),
                 "apply install");
    ok &= expect(ec == 0, "apply exit 0");
    if (!ok) goto done;

    if (cli_exists(env->steam_path)) {
        ok &= expect(run_capture_to_file(env->steam_path, "install --plan plan.dsuplan --dry-run --deterministic", "steam_install.txt", &ec),
                     "steam install dry-run");
        ok &= expect(ec == 0, "steam install exit 0");
        ok &= expect(run_capture_to_file(env->steam_path, "uninstall --state install_portable/.dsu/installed_state.dsustate --dry-run --deterministic", "steam_uninstall.txt", &ec),
                     "steam uninstall dry-run");
        ok &= expect(ec == 0, "steam uninstall exit 0");
    } else {
        ok &= expect(run_capture_to_file(env->cli_path,
                                         "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out steam_missing.dsuinv --format json --deterministic 1",
                                         "steam_missing_invocation.json",
                                         &ec),
                     "export invocation steam missing");
        ok &= expect(run_cli_json_expect(env->cli_path,
                                         "plan --manifest manifests/minimal.dsumanifest --invocation steam_missing.dsuinv --out steam_missing.dsuplan --format json --deterministic 1",
                                         "steam_missing.json",
                                         0,
                                         "\"status_code\":0"),
                     "steam adapter missing fallback");
    }

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int test_linux_pkg_lifecycle_simulation_mock(const test_env_t *env) {
    char sandbox[1024];
    char cwd[1024];
    int ok = 1;
    int ec = 1;

    ok &= expect(sandbox_prepare(env, "test_linux_pkg_lifecycle_simulation_mock", sandbox, (unsigned long)sizeof(sandbox)), "sandbox prepare");
    if (!ok) return 0;
    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) return 0;
    ok &= expect(DSU_CHDIR(sandbox) == 0, "chdir sandbox");

    ok &= expect(run_capture_to_file(env->cli_path,
                                    "export-invocation --manifest manifests/minimal.dsumanifest --op install --scope portable --components core --out plan.dsuinv --format json --deterministic 1",
                                    "invocation.json",
                                    &ec),
                 "export invocation install");
    ok &= expect(run_capture_to_file(env->cli_path,
                                    "plan --manifest manifests/minimal.dsumanifest --invocation plan.dsuinv --out plan.dsuplan --format json --deterministic 1",
                                    "plan.json",
                                    &ec),
                 "plan install");
    ok &= expect(ec == 0, "plan exit 0");
    ok &= expect(run_capture_to_file(env->cli_path, "apply --plan plan.dsuplan --deterministic 1", "apply.txt", &ec),
                 "apply install");
    ok &= expect(ec == 0, "apply exit 0");
    if (!ok) goto done;

    if (cli_exists(env->linux_path)) {
        ok &= expect(run_capture_to_file(env->linux_path, "install --plan plan.dsuplan --dry-run --deterministic", "linux_install.txt", &ec),
                     "linux install dry-run");
        ok &= expect(ec == 0, "linux install exit 0");
        ok &= expect(run_capture_to_file(env->linux_path, "uninstall --state install_portable/.dsu/installed_state.dsustate --dry-run --deterministic", "linux_uninstall.txt", &ec),
                     "linux uninstall dry-run");
        ok &= expect(ec == 0, "linux uninstall exit 0");
    } else {
        ok &= expect(run_cli_json_expect(env->cli_path,
                                         "platform-register --state install_portable/.dsu/installed_state.dsustate --format json --deterministic 1",
                                         "linux_missing.json",
                                         3,
                                         "\"status_code\":3"),
                     "linux adapter missing expected failure");
    }

done:
    (void)DSU_CHDIR(cwd);
    if (ok) (void)rm_rf(sandbox);
    return ok;
}

static int dispatch_test(const test_env_t *env, const char *name) {
    if (!env || !name) return 0;
    if (strcmp(name, "test_install_fresh_portable") == 0) return test_install_fresh_portable(env);
    if (strcmp(name, "test_install_fresh_user_scope") == 0) return test_install_fresh_user_scope(env);
    if (strcmp(name, "test_upgrade_in_place") == 0) return test_upgrade_in_place(env);
    if (strcmp(name, "test_upgrade_side_by_side") == 0) return test_upgrade_side_by_side(env);
    if (strcmp(name, "test_repair_restores_missing_files") == 0) return test_repair_restores_missing_files(env);
    if (strcmp(name, "test_uninstall_preserves_user_data") == 0) return test_uninstall_preserves_user_data(env);
    if (strcmp(name, "test_uninstall_removes_owned_files") == 0) return test_uninstall_removes_owned_files(env);
    if (strcmp(name, "test_verify_detects_modified_file") == 0) return test_verify_detects_modified_file(env);
    if (strcmp(name, "test_rollback_on_commit_failure") == 0) return test_rollback_on_commit_failure(env);
    if (strcmp(name, "test_plan_determinism_repeat_run") == 0) return test_plan_determinism_repeat_run(env);
    if (strcmp(name, "test_steam_lifecycle_simulation_mock") == 0) return test_steam_lifecycle_simulation_mock(env);
    if (strcmp(name, "test_linux_pkg_lifecycle_simulation_mock") == 0) return test_linux_pkg_lifecycle_simulation_mock(env);
    if (strcmp(name, "test_linux_portable_install_sandbox") == 0) return test_install_fresh_portable(env);
    if (strcmp(name, "test_linux_uninstall_preserves_user_data") == 0) return test_uninstall_preserves_user_data(env);
    fprintf(stderr, "unknown test name: %s\n", name);
    return 0;
}

int main(int argc, char **argv) {
    test_env_t env;
    char repo_root_buf[1024];
    if (argc < 6) {
        fprintf(stderr, "usage: dsu_setup_matrix_test <dominium-setup> <steam-adapter> <linux-adapter> <repo-root> <test-name>\n");
        return 1;
    }
    memset(&env, 0, sizeof(env));
    env.cli_path = argv[1];
    env.steam_path = argv[2];
    env.linux_path = argv[3];
    memset(repo_root_buf, 0, sizeof(repo_root_buf));
    strncpy(repo_root_buf, argv[4], sizeof(repo_root_buf) - 1u);
    path_to_dsu_inplace(repo_root_buf);
    env.repo_root = repo_root_buf;
    return dispatch_test(&env, argv[5]) ? 0 : 1;
}
