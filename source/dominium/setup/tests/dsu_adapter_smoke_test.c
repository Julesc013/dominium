/*
FILE: source/dominium/setup/tests/dsu_adapter_smoke_test.c
MODULE: Dominium Setup
PURPOSE: Adapter-level smoke tests (Plan S-6; Windows CI-safe, no registry writes).
*/
#if !defined(_WIN32)
#error "dsu_adapter_smoke_test.c is Windows-only"
#endif

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"
#include "dsu/dsu_resolve.h"

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

static int buf_put_u8(buf_t *b, unsigned char v) { return buf_append(b, &v, 1ul); }

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

static int path_dirname_inplace(char *path) {
    size_t n;
    if (!path) return 0;
    n = strlen(path);
    while (n > 0u) {
        char c = path[n - 1u];
        if (c == '\\' || c == '/') {
            path[n - 1u] = '\0';
            return 1;
        }
        --n;
    }
    return 0;
}

static void backslashes_to_slashes(char *s) {
    size_t i;
    if (!s) return;
    for (i = 0u; s[i] != '\0'; ++i) {
        if (s[i] == '\\') s[i] = '/';
    }
}

static int rm_tree(const char *path) {
    char pattern[MAX_PATH];
    WIN32_FIND_DATAA fd;
    HANDLE h;
    if (!path || path[0] == '\0') return 0;
    sprintf(pattern, "%s\\*", path);
    h = FindFirstFileA(pattern, &fd);
    if (h == INVALID_HANDLE_VALUE) {
        RemoveDirectoryA(path);
        return 1;
    }
    do {
        char child[MAX_PATH];
        if (strcmp(fd.cFileName, ".") == 0 || strcmp(fd.cFileName, "..") == 0) continue;
        sprintf(child, "%s\\%s", path, fd.cFileName);
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            rm_tree(child);
        } else {
            DeleteFileA(child);
        }
    } while (FindNextFileA(h, &fd));
    FindClose(h);
    RemoveDirectoryA(path);
    return 1;
}

static int run_process(const char *exe_path, const char *args, const char *cwd) {
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    DWORD exit_code = 0;
    char cmdline[4096];

    if (!exe_path || exe_path[0] == '\0') return 0;
    if (!args) args = "";

    memset(&si, 0, sizeof(si));
    memset(&pi, 0, sizeof(pi));
    si.cb = sizeof(si);

    if ((strlen(exe_path) + strlen(args) + 4u) >= sizeof(cmdline)) {
        return 0;
    }
    sprintf(cmdline, "\"%s\" %s", exe_path, args);

    if (!CreateProcessA(exe_path,
                        cmdline,
                        NULL,
                        NULL,
                        FALSE,
                        0,
                        NULL,
                        cwd,
                        &si,
                        &pi)) {
        return 0;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    GetExitCodeProcess(pi.hProcess, &exit_code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return exit_code == 0u;
}

static int write_minimal_manifest(const char *path, const char *install_root_dsu) {
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
    buf_t file_bytes;
    unsigned char hdr[20];
    unsigned long checksum;

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&ir, 0, sizeof(ir));
    memset(&comp, 0, sizeof(comp));
    memset(&file_bytes, 0, sizeof(file_bytes));

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, "dominium")) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, "1.0.0")) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, "stable")) goto fail;
    if (!buf_put_tlv_str(&root, T_PLATFORM_TARGET, "any-any")) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_SCOPE, 0u)) goto fail; /* portable */
    if (!buf_put_tlv_str(&ir, T_IR_PLATFORM, "any-any")) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, install_root_dsu)) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT, ir.data, ir.len)) goto fail;

    if (!buf_put_tlv_u32(&comp, T_C_VER, 1ul)) goto fail;
    if (!buf_put_tlv_str(&comp, T_C_ID, "core")) goto fail;
    if (!buf_put_tlv_u8(&comp, T_C_KIND, 5u)) goto fail; /* other */
    if (!buf_put_tlv_u32(&comp, T_C_FLAGS, 0ul)) goto fail;
    if (!buf_put_tlv(&root, T_COMPONENT, comp.data, comp.len)) goto fail;

    if (!buf_put_tlv(&payload, T_ROOT, root.data, root.len)) goto fail;

    /* DSUM file header (20 bytes), format_version=2 */
    hdr[0] = 'D';
    hdr[1] = 'S';
    hdr[2] = 'U';
    hdr[3] = 'M';
    hdr[4] = 2u;
    hdr[5] = 0u;
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload.len & 0xFFul);
    hdr[13] = (unsigned char)((payload.len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload.len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload.len >> 24) & 0xFFul);
    hdr[16] = 0u;
    hdr[17] = 0u;
    hdr[18] = 0u;
    hdr[19] = 0u;
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);

    if (!buf_append(&file_bytes, hdr, 20ul)) goto fail;
    if (!buf_append(&file_bytes, payload.data, payload.len)) goto fail;

    if (!write_bytes_file(path, file_bytes.data, file_bytes.len)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&file_bytes);
    return 1;

fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&ir);
    buf_free(&comp);
    buf_free(&file_bytes);
    return 0;
}

static int expect(int cond, const char *msg) {
    if (!cond) {
        fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
        return 0;
    }
    return 1;
}

static int is_config_dir(const char *name) {
    if (!name || name[0] == '\0') return 0;
    if (_stricmp(name, "Debug") == 0) return 1;
    if (_stricmp(name, "Release") == 0) return 1;
    if (_stricmp(name, "RelWithDebInfo") == 0) return 1;
    if (_stricmp(name, "MinSizeRel") == 0) return 1;
    return 0;
}

int main(void) {
    char self[MAX_PATH];
    char self_dir[MAX_PATH];
    char config_dir[MAX_PATH];
    char setup_dir[MAX_PATH];
    char win_exe[MAX_PATH];
    char steam_exe[MAX_PATH];
    char cwd[MAX_PATH];
    char install_root_native[MAX_PATH];
    char install_root_dsu[MAX_PATH];
    char manifest_path[MAX_PATH];
    char plan_path[MAX_PATH];
    char state_path_dsu[1024];

    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_resolve_result_t *res = NULL;
    dsu_plan_t *plan = NULL;
    dsu_status_t st;
    int ok = 1;
    int has_config = 0;

    /* Derive build/config paths from this test executable path. */
    memset(self, 0, sizeof(self));
    if (GetModuleFileNameA(NULL, self, (DWORD)sizeof(self)) == 0u) {
        fprintf(stderr, "FAIL: GetModuleFileNameA\n");
        return 1;
    }
    strcpy(self_dir, self);
    ok &= expect(path_dirname_inplace(self_dir), "self_dir dirname");

    /* config dir name (e.g. Debug/Release) */
    {
        const char *seg = strrchr(self_dir, '\\');
        seg = seg ? (seg + 1) : self_dir;
        if (is_config_dir(seg)) {
            strncpy(config_dir, seg, sizeof(config_dir));
            config_dir[sizeof(config_dir) - 1u] = '\0';
            has_config = 1;
        } else {
            config_dir[0] = '\0';
            has_config = 0;
        }
    }

    strcpy(setup_dir, self_dir);
    if (has_config) {
        ok &= expect(path_dirname_inplace(setup_dir), "setup_dir up1");
    }
    ok &= expect(path_dirname_inplace(setup_dir), "setup_dir up2");

    if (has_config) {
        sprintf(win_exe, "%s\\adapters\\windows\\%s\\dominium-setup-win.exe", setup_dir, config_dir);
        sprintf(steam_exe, "%s\\adapters\\steam\\%s\\dominium-setup-steam.exe", setup_dir, config_dir);
    } else {
        sprintf(win_exe, "%s\\adapters\\windows\\dominium-setup-win.exe", setup_dir);
        sprintf(steam_exe, "%s\\adapters\\steam\\dominium-setup-steam.exe", setup_dir);
    }

    strcpy(cwd, self_dir);

    sprintf(install_root_native, "%s\\dsu_adapter_test_root", cwd);
    {
        char install_root_txn[MAX_PATH];
        if (strlen(install_root_native) + 5u <= sizeof(install_root_txn)) {
            sprintf(install_root_txn, "%s.txn", install_root_native);
            (void)rm_tree(install_root_txn);
        }
    }
    (void)rm_tree(install_root_native);
    CreateDirectoryA(install_root_native, NULL);

    strcpy(install_root_dsu, install_root_native);
    backslashes_to_slashes(install_root_dsu);

    sprintf(manifest_path, "%s\\dsu_adapter_test.dsumanifest", cwd);
    sprintf(plan_path, "%s\\dsu_adapter_test.dsuplan", cwd);
    sprintf(state_path_dsu, "%s/.dsu/installed_state.dsustate", install_root_dsu);

    ok &= expect(write_minimal_manifest(manifest_path, install_root_dsu), "write minimal manifest");
    if (!ok) goto done;

    /* Build a minimal plan via Setup Core (no payloads/actions). */
    {
        dsu_config_t cfg;
        dsu_callbacks_t cbs;
        const char *req_ids[1];
        dsu_resolve_request_t req;

        dsu_config_init(&cfg);
        dsu_callbacks_init(&cbs);
        cfg.flags |= DSU_CONFIG_FLAG_DETERMINISTIC;
        st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
        ok &= expect(st == DSU_STATUS_SUCCESS && ctx != NULL, "ctx create");
        if (!ok) goto done;

        st = dsu_manifest_load_file(ctx, manifest_path, &manifest);
        ok &= expect(st == DSU_STATUS_SUCCESS && manifest != NULL, "manifest load");
        if (!ok) goto done;

        req_ids[0] = "core";
        dsu_resolve_request_init(&req);
        req.operation = DSU_RESOLVE_OPERATION_INSTALL;
        req.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
        req.allow_prerelease = 0;
        req.target_platform = "any-any";
        req.requested_components = req_ids;
        req.requested_component_count = 1u;

        st = dsu_resolve_components(ctx, manifest, NULL, &req, &res);
        ok &= expect(st == DSU_STATUS_SUCCESS && res != NULL, "resolve");
        if (!ok) goto done;

        st = dsu_plan_build(ctx, manifest, manifest_path, res, 0x1111222233334444ULL, &plan);
        ok &= expect(st == DSU_STATUS_SUCCESS && plan != NULL, "plan build");
        if (!ok) goto done;

        st = dsu_plan_write_file(ctx, plan, plan_path);
        ok &= expect(st == DSU_STATUS_SUCCESS, "plan write");
        if (!ok) goto done;
    }

    /* Windows adapter: install (non-dry-run) to produce installed state */
    ok &= expect(run_process(win_exe, "install --plan \"dsu_adapter_test.dsuplan\" --deterministic /quiet", cwd), "win install");
    if (!ok) goto done;

    /* Windows adapter: dry-run invocation */
    ok &= expect(run_process(win_exe, "install --plan \"dsu_adapter_test.dsuplan\" --dry-run --deterministic /quiet", cwd), "win install dry-run");
    if (!ok) goto done;

    /* Windows adapter: idempotent platform register/unregister against state with no intents */
    {
        char args[2048];
        sprintf(args, "platform-register --state \"%s\" --deterministic /quiet", state_path_dsu);
        ok &= expect(run_process(win_exe, args, cwd), "win platform-register");
        sprintf(args, "platform-unregister --state \"%s\" --deterministic /quiet", state_path_dsu);
        ok &= expect(run_process(win_exe, args, cwd), "win platform-unregister");
        ok &= expect(run_process(win_exe, args, cwd), "win platform-unregister idempotent");
        if (!ok) goto done;
    }

    /* Steam adapter: lifecycle simulation (install dry-run) */
    ok &= expect(run_process(steam_exe, "install --plan \"dsu_adapter_test.dsuplan\" --dry-run --deterministic", cwd), "steam install dry-run");

    /* Cleanup: uninstall via Windows adapter */
    {
        char args[2048];
        sprintf(args, "uninstall --state \"%s\" --deterministic /quiet", state_path_dsu);
        ok &= expect(run_process(win_exe, args, cwd), "win uninstall");
    }

done:
    if (plan) dsu_plan_destroy(ctx, plan);
    if (res) dsu_resolve_result_destroy(ctx, res);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);

    DeleteFileA(manifest_path);
    DeleteFileA(plan_path);
    rm_tree(install_root_native);
    {
        char install_root_txn[MAX_PATH];
        if (strlen(install_root_native) + 5u <= sizeof(install_root_txn)) {
            sprintf(install_root_txn, "%s.txn", install_root_native);
            rm_tree(install_root_txn);
        }
    }

    return ok ? 0 : 1;
}
