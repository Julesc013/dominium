/*
FILE: source/dominium/setup/tests/dsu_job_resume_test.c
MODULE: Dominium Setup
PURPOSE: Verify resumable setup jobs across a forced interruption.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <direct.h>
#define DSU_CHDIR _chdir
#define DSU_GETCWD _getcwd
#else
#include <unistd.h>
#define DSU_CHDIR chdir
#define DSU_GETCWD getcwd
#endif

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_fs.h"
#include "dsu/dsu_invocation.h"
#include "dsu/dsu_job.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_plan.h"

#include "../core/src/fs/dsu_platform_iface.h"

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
    size_t nw;
    if (!path) return 0;
    f = fopen(path, "wb");
    if (!f) return 0;
    nw = fwrite(bytes, 1u, (size_t)len, f);
    fclose(f);
    return nw == (size_t)len;
}

static int write_manifest_fileset(const char *manifest_path,
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

int main(void) {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_plan_t *plan = NULL;
    dsu_invocation_t inv;
    dsu_job_input_t job_input;
    dsu_job_options_t job_opts;
    dsu_job_run_result_t run_res;
    dsu_job_run_result_t resume_res;
    dsu_status_t st;
    char cwd[1024];
    char job_root[DSU_JOB_PATH_MAX];
    char abs_install_root[1024];
    char abs_joined[1024];
    int ok = 1;
    const char *roots[1];
    const char *components[1];

    if (!DSU_GETCWD(cwd, (int)sizeof(cwd))) {
        fprintf(stderr, "error: getcwd failed\n");
        return 1;
    }

    (void)rm_rf("dsu_job_resume_test_run");
    ok &= expect(mkdir_p_rel("dsu_job_resume_test_run/payload/bin"), "mkdir payload/bin");
    ok &= expect(mkdir_p_rel("dsu_job_resume_test_run/install"), "mkdir install");
    if (!ok) return 1;

    ok &= expect(write_bytes_file("dsu_job_resume_test_run/payload/bin/hello.txt",
                                 (const unsigned char *)"hello\n", 6ul),
                 "write payload");
    ok &= expect(write_manifest_fileset("dsu_job_resume_test_run/m.dsumanifest",
                                        "install",
                                        "payload",
                                        "core"),
                 "write manifest");
    if (!ok) return 1;

    ok &= expect(DSU_CHDIR("dsu_job_resume_test_run") == 0, "chdir run");
    if (!ok) return 1;

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    st = dsu_ctx_create(&cfg, &cbs, NULL, &ctx);
    ok &= expect(st == DSU_STATUS_SUCCESS, "ctx create");
    if (!ok) goto done;

    st = dsu_manifest_load_file(ctx, "m.dsumanifest", &manifest);
    ok &= expect(st == DSU_STATUS_SUCCESS, "manifest load");
    if (!ok) goto done;

    roots[0] = "install";
    components[0] = "core";

    dsu_invocation_init(&inv);
    inv.operation = (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
    inv.scope = (dsu_u8)DSU_INVOCATION_SCOPE_PORTABLE;
    inv.policy_flags = (dsu_u32)DSU_INVOCATION_POLICY_DETERMINISTIC;
    inv.install_roots = (char **)roots;
    inv.install_root_count = 1u;
    inv.selected_components = (char **)components;
    inv.selected_component_count = 1u;

    st = dsu_plan_build_from_invocation(ctx,
                                        manifest,
                                        "m.dsumanifest",
                                        NULL,
                                        &inv,
                                        &plan);
    ok &= expect(st == DSU_STATUS_SUCCESS, "plan build");
    if (!ok) goto done;

    st = dsu_plan_validate(plan);
    ok &= expect(st == DSU_STATUS_SUCCESS, "plan validate");
    if (!ok) goto done;

    st = dsu_plan_write_file(ctx, plan, "out.dsuplan");
    ok &= expect(st == DSU_STATUS_SUCCESS, "plan write");
    if (!ok) goto done;

    st = dsu_platform_get_cwd(abs_install_root, (dsu_u32)sizeof(abs_install_root));
    ok &= expect(st == DSU_STATUS_SUCCESS, "get cwd");
    ok &= expect(path_join(abs_install_root, "install", abs_joined, (unsigned long)sizeof(abs_joined)), "abs install root");
    if (!ok) goto done;

    st = dsu_job_build_root_for_install_root(abs_joined,
                                             job_root,
                                             (dsu_u32)sizeof(job_root));
    ok &= expect(st == DSU_STATUS_SUCCESS, "job root");
    if (!ok) goto done;

    dsu_job_input_init(&job_input);
    job_input.job_type = (dsu_u32)CORE_JOB_TYPE_SETUP_INSTALL;
    job_input.dry_run = 0u;
    strncpy(job_input.plan_path, "out.dsuplan", sizeof(job_input.plan_path) - 1u);
    job_input.plan_path[sizeof(job_input.plan_path) - 1u] = '\0';

    dsu_job_options_init(&job_opts);
    job_opts.stop_after_step = 1u;

    st = dsu_job_run(ctx, &job_input, job_root, &job_opts, &run_res);
    ok &= expect(st != DSU_STATUS_SUCCESS, "job stop after step");
    ok &= expect(run_res.state.outcome == (u32)CORE_JOB_OUTCOME_NONE, "job outcome none");

    st = dsu_job_resume(ctx, job_root, run_res.state.job_id, &resume_res);
    ok &= expect(st == DSU_STATUS_SUCCESS, "job resume");
    ok &= expect(resume_res.state.outcome == (u32)CORE_JOB_OUTCOME_OK, "job outcome ok");
    ok &= expect(file_exists("install/bin/hello.txt"), "installed file exists");

done:
    if (plan) dsu_plan_destroy(ctx, plan);
    if (manifest) dsu_manifest_destroy(ctx, manifest);
    if (ctx) dsu_ctx_destroy(ctx);
    ok &= expect(DSU_CHDIR(cwd) == 0, "chdir restore");
    (void)rm_rf("dsu_job_resume_test_run");
    return ok ? 0 : 1;
}
