/*
FILE: source/dominium/launcher/tests/launcher_state_smoke_tests.cpp
MODULE: Dominium Launcher
PURPOSE: Validate launcher installed-state contract via a real DSU install state.
*/

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#endif

extern "C" {
#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_fs.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"
#include "dsu/dsu_txn.h"
}

/* Internal-only platform helpers for directory enumeration in tests. */
extern "C" {
#include "../../setup/core/src/fs/dsu_platform_iface.h"
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int expect_st(dsu_status_t got, dsu_status_t want, const char *msg) {
    if (got != want) {
        std::fprintf(stderr, "FAIL: %s (got=%d want=%d)\n",
                     msg ? msg : "(null)", (int)got, (int)want);
        return 0;
    }
    return 1;
}

static dsu_ctx_t *create_ctx_deterministic(void) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_status_t st;
    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    if (st != DSU_STATUS_SUCCESS) {
        return NULL;
    }
    return ctx;
}

static int path_join(const char *a, const char *b, char *out_path, unsigned long out_cap) {
    dsu_status_t st;
    if (!out_path || out_cap == 0ul) return 0;
    out_path[0] = '\0';
    st = dsu_fs_path_join(a, b, out_path, (dsu_u32)out_cap);
    return st == DSU_STATUS_SUCCESS;
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

static int mkdir_p_rel(const char *rel_path) {
    char canon[1024];
    unsigned long i;
    unsigned long n;
    dsu_status_t st;
    if (!rel_path) return 0;
    if (rel_path[0] == '\0') return 1;
    st = dsu_fs_path_canonicalize(rel_path, canon, (dsu_u32)sizeof(canon));
    if (st != DSU_STATUS_SUCCESS) return 0;
    n = (unsigned long)std::strlen(canon);
    if (n == 0ul) return 1;
    for (i = 0ul; i <= n; ++i) {
        char c = canon[i];
        if (c == '/' || c == '\0') {
            char part[1024];
            if (i == 0ul) continue;
            if (i >= (unsigned long)sizeof(part)) return 0;
            std::memcpy(part, canon, (size_t)i);
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
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) continue;
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

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) {
        return 0;
    }
    f = std::fopen(path, "wb");
    if (!f) {
        return 0;
    }
    n = (size_t)len;
    if (n != 0u) {
        if (std::fwrite(bytes, 1u, n, f) != n) {
            std::fclose(f);
            return 0;
        }
    }
    if (std::fclose(f) != 0) {
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
    std::free(b->data);
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
    p = (unsigned char *)std::realloc(b->data, (size_t)new_cap);
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
    std::memcpy(b->data + b->len, bytes, (size_t)n);
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
    n = (unsigned long)std::strlen(s);
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
    std::memset(out_file, 0, sizeof(*out_file));
    std::memset(hdr, 0, sizeof(hdr));
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

    std::memset(&root, 0, sizeof(root));
    std::memset(&payload, 0, sizeof(payload));
    std::memset(&ir, 0, sizeof(ir));
    std::memset(&comp, 0, sizeof(comp));
    std::memset(&pl, 0, sizeof(pl));
    std::memset(&file, 0, sizeof(file));
    std::memset(sha0, 0, sizeof(sha0));
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

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        if (is_sep(path[i - 1u])) {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

#if defined(_WIN32)
static std::string path_to_native_win32(const char *path) {
    std::string out = path ? path : "";
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '/') out[i] = '\\';
    }
    return out;
}
#endif

static int run_launcher_smoke(const std::string& launcher_path, const std::string& state_arg) {
#if defined(_WIN32)
    std::string cmd = std::string("\"") + launcher_path + "\" --smoke-test --state \"" + state_arg + "\"";
    std::vector<char> cmdline(cmd.begin(), cmd.end());
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    DWORD exit_code = 1;
    cmdline.push_back('\0');
    std::memset(&si, 0, sizeof(si));
    std::memset(&pi, 0, sizeof(pi));
    si.cb = sizeof(si);
    if (!CreateProcessA(NULL, &cmdline[0], NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        return -1;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    if (!GetExitCodeProcess(pi.hProcess, &exit_code)) {
        exit_code = 1;
    }
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return (int)exit_code;
#else
    std::string cmd = std::string("\"") + launcher_path + "\" --smoke-test --state \"" + state_arg + "\"";
    return std::system(cmd.c_str());
#endif
}

int main(int argc, char **argv) {
    const char *base = "launcher_state_smoke";
    const char *component_id = "core";
    const char *payload_rel = "payload";
    int ok = 1;

    char manifest_path[1024];
    char payload_root[1024];
    char payload_bin_dir[1024];
    char payload_launcher[1024];
    char payload_game[1024];
    char install_root[1024];
    char install_bin_dir[1024];
    char install_launcher[1024];
    char install_game[1024];
    char state_path[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *m = NULL;
    dsu_resolve_result_t *r = NULL;
    dsu_plan_t *p = NULL;
    dsu_txn_options_t opts;
    dsu_txn_result_t res;
    dsu_status_t st;

#if defined(_WIN32) || defined(_WIN64)
    const char *launcher_name = "dominium-launcher.exe";
    const char *game_name = "dominium_game.exe";
#else
    const char *launcher_name = "dominium-launcher";
    const char *game_name = "dominium_game";
#endif

    (void)rm_rf(base);
    ok &= expect(mkdir_p_rel(base), "mkdir base");

    ok &= expect(path_join(base, "payload", payload_root, (unsigned long)sizeof(payload_root)), "join payload root");
    ok &= expect(path_join(payload_root, "bin", payload_bin_dir, (unsigned long)sizeof(payload_bin_dir)), "join payload/bin");
    ok &= expect(mkdir_p_rel(payload_bin_dir), "mkdir payload/bin");

    ok &= expect(path_join(payload_bin_dir, launcher_name, payload_launcher, (unsigned long)sizeof(payload_launcher)), "join payload launcher");
    ok &= expect(path_join(payload_bin_dir, game_name, payload_game, (unsigned long)sizeof(payload_game)), "join payload game");
    ok &= expect(write_bytes_file(payload_launcher, (const unsigned char *)"launcher\n", 9ul), "write payload launcher");
    ok &= expect(write_bytes_file(payload_game, (const unsigned char *)"game\n", 5ul), "write payload game");

    ok &= expect(path_join(base, "install", install_root, (unsigned long)sizeof(install_root)), "join install root");
    ok &= expect(path_join(install_root, "bin", install_bin_dir, (unsigned long)sizeof(install_bin_dir)), "join install/bin");
    ok &= expect(path_join(install_bin_dir, launcher_name, install_launcher, (unsigned long)sizeof(install_launcher)), "join install launcher");
    ok &= expect(path_join(install_bin_dir, game_name, install_game, (unsigned long)sizeof(install_game)), "join install game");
    ok &= expect(path_join(install_root, ".dsu/installed_state.dsustate", state_path, (unsigned long)sizeof(state_path)), "join state path");
    ok &= expect(path_join(base, "m.dsumanifest", manifest_path, (unsigned long)sizeof(manifest_path)), "join manifest path");
    ok &= expect(write_manifest_fileset(manifest_path, install_root, payload_rel, component_id), "write manifest");
    if (!ok) goto done;

    ok &= expect(set_env_var("DSU_TEST_SEED", "1"), "set DSU_TEST_SEED");
    ctx = create_ctx_deterministic();
    ok &= expect(ctx != NULL, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, manifest_path, &m);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "manifest load");
    ok &= expect(m != NULL, "manifest != NULL");
    if (!ok) goto done;

    {
        const char *const requested[] = {"core"};
        dsu_resolve_request_t req;
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.requested_components = requested;
        req.requested_component_count = 1u;
        st = dsu_resolve_components(ctx, m, NULL, &req, &r);
    }
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "resolve");
    ok &= expect(r != NULL, "resolve != NULL");
    if (!ok) goto done;

    st = dsu_plan_build(ctx, m, manifest_path, r, &p);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "plan build");
    ok &= expect(p != NULL, "plan != NULL");
    if (!ok) goto done;

    st = dsu_ctx_reset_audit_log(ctx);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "reset audit log");
    if (!ok) goto done;

    dsu_txn_options_init(&opts);
    dsu_txn_result_init(&res);
    st = dsu_txn_apply_plan(ctx, p, &opts, &res);
    ok &= expect_st(st, DSU_STATUS_SUCCESS, "txn apply plan");
    if (!ok) goto done;

    ok &= expect(file_exists(state_path), "state exists");
    ok &= expect(file_exists(install_launcher), "launcher file exists");
    ok &= expect(file_exists(install_game), "game file exists");
    if (!ok) goto done;

    {
        char cwd[1024];
        std::string argv0 = (argc > 0 && argv && argv[0]) ? std::string(argv[0]) : std::string();
        std::string dir = dirname_of(argv0);
        if (dir.empty() && !argv0.empty()) {
            if (dsu_platform_get_cwd(cwd, (dsu_u32)sizeof(cwd)) == DSU_STATUS_SUCCESS) {
                char joined[1024];
                if (path_join(cwd, argv0.c_str(), joined, (unsigned long)sizeof(joined))) {
                    argv0 = joined;
                    dir = dirname_of(argv0);
                }
            }
        }
        if (dir.empty()) {
            dir = ".";
        }
        std::string launcher_path = dir + "/" + launcher_name;
        std::string state_arg = std::string(state_path);
#if defined(_WIN32)
        launcher_path = path_to_native_win32(launcher_path.c_str());
        state_arg = path_to_native_win32(state_arg.c_str());
#endif
        int rc = run_launcher_smoke(launcher_path, state_arg);
        if (rc != 0) {
            std::fprintf(stderr,
                         "Launcher smoke failed: launcher=%s state=%s rc=%d\n",
                         launcher_path.c_str(),
                         state_arg.c_str(),
                         rc);
        }
        ok &= expect(rc == 0, "launcher --smoke-test succeeds");
    }

done:
    (void)set_env_var("DSU_TEST_SEED", "");
    if (p) dsu_plan_destroy(ctx, p);
    if (r) dsu_resolve_result_destroy(ctx, r);
    if (m) dsu_manifest_destroy(ctx, m);
    if (ctx) dsu_ctx_destroy(ctx);
    (void)rm_rf(base);
    return ok ? 0 : 1;
}
