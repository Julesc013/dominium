#include "dsk/dsk_audit.h"
#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_jobs.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_resume.h"
#include "dsk/dsk_splat.h"
#include "dsk/dsk_splat_caps.h"
#include "dsk_resolve.h"
#include "dss/dss_services.h"

#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <io.h>
#include <sys/stat.h>
#include <errno.h>
#else
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#endif

#ifndef SETUP2_TESTS_SANDBOX_ROOT
#define SETUP2_TESTS_SANDBOX_ROOT "."
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static dsk_u32 dsk_error_subcode(dsk_status_t st) {
    dsk_u32 i;
    for (i = 0u; i < st.detail_count; ++i) {
        if (st.details[i].key_id == (u32)ERR_DETAIL_KEY_SUBCODE &&
            st.details[i].type == (u32)ERR_DETAIL_TYPE_U32) {
            return st.details[i].v.u32_value;
        }
    }
    return 0u;
}

static int fail_status(const char *msg, dsk_status_t st) {
    std::fprintf(stderr,
                 "FAIL: %s (domain=%u code=%u subcode=%u flags=%u)\n",
                 msg,
                 (unsigned)st.domain,
                 (unsigned)st.code,
                 (unsigned)dsk_error_subcode(st),
                 (unsigned)st.flags);
    return 1;
}

static int make_dir_one(const std::string &path) {
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return 1;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return 1;
    }
#endif
    return errno == EEXIST;
}

static int make_dir_recursive(const std::string &path) {
    size_t i;
    std::string current;
    if (path.empty()) {
        return 0;
    }
    for (i = 0u; i <= path.size(); ++i) {
        char c = (i < path.size()) ? path[i] : '\0';
        if (c == '/' || c == '\\' || c == '\0') {
            if (!current.empty()) {
                if (!make_dir_one(current)) {
                    return 0;
                }
            }
        }
        if (c != '\0') {
            current.push_back(c);
        }
    }
    return 1;
}

static int remove_dir_recursive(const std::string &path) {
#if defined(_WIN32)
    std::string pattern = path + "\\*";
    struct _finddata_t data;
    intptr_t handle = _findfirst(pattern.c_str(), &data);
    if (handle == -1) {
        return (errno == ENOENT) ? 1 : 0;
    }
    do {
        const char *name = data.name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "\\" + name;
        if (data.attrib & _A_SUBDIR) {
            if (!remove_dir_recursive(child)) {
                _findclose(handle);
                return 0;
            }
            _rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    } while (_findnext(handle, &data) == 0);
    _findclose(handle);
    _rmdir(path.c_str());
    return 1;
#else
    DIR *dir = opendir(path.c_str());
    if (!dir) {
        return (errno == ENOENT) ? 1 : 0;
    }
    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        const char *name = ent->d_name;
        if (std::strcmp(name, ".") == 0 || std::strcmp(name, "..") == 0) {
            continue;
        }
        std::string child = path + "/" + name;
        struct stat st;
        if (stat(child.c_str(), &st) != 0) {
            continue;
        }
        if (S_ISDIR(st.st_mode)) {
            if (!remove_dir_recursive(child)) {
                closedir(dir);
                return 0;
            }
            rmdir(child.c_str());
        } else {
            std::remove(child.c_str());
        }
    }
    closedir(dir);
    rmdir(path.c_str());
    return 1;
#endif
}

static void set_failpoint(const char *name) {
#if defined(_WIN32)
    std::string env = "DSK_FAILPOINT=";
    if (name) {
        env += name;
    }
    _putenv(env.c_str());
#else
    if (!name) {
        setenv("DSK_FAILPOINT", "", 1);
    } else {
        setenv("DSK_FAILPOINT", name, 1);
    }
#endif
}

static int write_bytes(const dss_fs_api_t *fs,
                       const char *path,
                       const std::vector<dsk_u8> &data) {
    if (!fs || !fs->write_file_bytes_atomic) {
        return 0;
    }
    return dss_error_is_ok(fs->write_file_bytes_atomic(fs->ctx,
                                                       path,
                                                       data.empty() ? 0 : &data[0],
                                                       (dss_u32)data.size()));
}

static int read_bytes(const dss_fs_api_t *fs,
                      const char *path,
                      std::vector<dsk_u8> &out) {
    if (!fs || !fs->read_file_bytes) {
        return 0;
    }
    return dss_error_is_ok(fs->read_file_bytes(fs->ctx, path, &out));
}

static void build_manifest(dsk_manifest_t *out_manifest,
                           dsk_u64 artifact_digest,
                           dsk_u64 artifact_size) {
    dsk_manifest_clear(out_manifest);
    out_manifest->product_id = "dominium";
    out_manifest->version = "1.0.0";
    out_manifest->build_id = "dev";
    out_manifest->supported_targets.push_back("win32_nt5");
    {
        dsk_layout_template_t layout;
        layout.template_id = "root_base";
        layout.target_root = "primary";
        layout.path_prefix = "app";
        out_manifest->layout_templates.push_back(layout);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "base";
        comp.kind = "runtime";
        comp.default_selected = DSK_TRUE;
        {
            dsk_artifact_t art;
            art.artifact_id = "base_art";
            art.hash = "basehash";
            art.digest64 = artifact_digest;
            art.size = artifact_size;
            art.source_path = "base.bin";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }
}

static void build_request(dsk_request_t *out_request, const char *payload_root) {
    dsk_request_clear(out_request);
    out_request->operation = DSK_OPERATION_INSTALL;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->frontend_id = "cli";
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = "win32_nt5";
    out_request->payload_root = payload_root ? payload_root : "payloads";
}

static dsk_status_t write_manifest_bytes(const dsk_manifest_t &manifest,
                                         std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_manifest_write(&manifest, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static dsk_status_t write_request_bytes(const dsk_request_t &request,
                                        std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_request_write(&request, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static int build_plan_bytes(const std::vector<dsk_u8> &payload,
                            dsk_plan_t *out_plan,
                            std::vector<dsk_u8> &out_plan_bytes) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    dsk_splat_candidate_t candidate;
    std::vector<dsk_plan_refusal_t> refusals;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    dsk_u64 caps_digest;
    dsk_status_t st;
    dsk_tlv_buffer_t plan_buf;

    build_manifest(&manifest,
                   dsk_digest64_bytes(payload.empty() ? 0 : &payload[0], (dsk_u32)payload.size()),
                   (dsk_u64)payload.size());
    build_request(&request, "payloads");

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, &refusals);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }

    if (!dsk_splat_registry_find("splat_portable", &candidate)) {
        return 0;
    }
    caps_digest = candidate.caps_digest64;

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    manifest_digest = dsk_digest64_bytes(&manifest_bytes[0], (dsk_u32)manifest_bytes.size());
    request_digest = dsk_digest64_bytes(&request_bytes[0], (dsk_u32)request_bytes.size());

    st = dsk_plan_build(manifest,
                        request,
                        "splat_portable",
                        candidate.caps,
                        caps_digest,
                        resolved,
                        manifest_digest,
                        request_digest,
                        out_plan);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }

    st = dsk_plan_write(out_plan, &plan_buf);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    out_plan_bytes.assign(plan_buf.data, plan_buf.data + plan_buf.size);
    dsk_tlv_buffer_free(&plan_buf);
    return 1;
}

static int init_services(const char *case_name, dss_services_t *services, std::string &root_out) {
    dss_services_config_t cfg;
    std::string root = std::string(SETUP2_TESTS_SANDBOX_ROOT) + "/" + case_name;
    remove_dir_recursive(root);
    if (!make_dir_recursive(root)) {
        return 0;
    }
    dss_services_config_init(&cfg);
    cfg.sandbox_root = root.c_str();
    cfg.platform_triple = "win32_nt5";
    if (!dss_error_is_ok(dss_services_init_fake(&cfg, services))) {
        return 0;
    }
    root_out = root;
    return 1;
}

static int write_payload(const dss_services_t *services, const std::vector<dsk_u8> &payload) {
    if (!services || !services->fs.make_dir) {
        return 0;
    }
    if (!dss_error_is_ok(services->fs.make_dir(services->fs.ctx, "payloads"))) {
        return 0;
    }
    return write_bytes(&services->fs, "payloads/base.bin", payload);
}

static int read_install_file(const dss_services_t *services,
                             std::vector<dsk_u8> &out_bytes) {
    dss_scope_paths_t paths;
    if (!services || !services->perms.get_user_scope_paths) {
        return 0;
    }
    if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
        return 0;
    }
    if (paths.install_root.empty()) {
        return 0;
    }
    std::string path = paths.install_root + "/app/base.bin";
    return read_bytes(&services->fs, path.c_str(), out_bytes);
}

static int write_install_file(const dss_services_t *services,
                              const std::vector<dsk_u8> &bytes) {
    dss_scope_paths_t paths;
    if (!services || !services->perms.get_user_scope_paths || !services->fs.make_dir) {
        return 0;
    }
    if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
        return 0;
    }
    if (paths.install_root.empty()) {
        return 0;
    }
    if (!dss_error_is_ok(services->fs.make_dir(services->fs.ctx, paths.install_root.c_str()))) {
        return 0;
    }
    {
        std::string app_dir = paths.install_root + "/app";
        if (!dss_error_is_ok(services->fs.make_dir(services->fs.ctx, app_dir.c_str()))) {
            return 0;
        }
    }
    {
        std::string path = paths.install_root + "/app/base.bin";
        return write_bytes(&services->fs, path.c_str(), bytes);
    }
}

static int test_apply_fresh_install_succeeds(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> installed;
    std::vector<dsk_u8> state_bytes;
    std::vector<dsk_u8> audit_bytes;
    dsk_installed_state_t state;
    dsk_audit_t audit;
    dsk_apply_request_t apply;
    dsk_status_t st;

    payload.assign(4u, 0u);
    payload[0] = 't';
    payload[1] = 'e';
    payload[2] = 's';
    payload[3] = 't';

    if (!init_services("apply_fresh", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("apply failed", st);
    }

    if (!read_bytes(&services.fs, "out/state.tlv", state_bytes)) {
        dss_services_shutdown(&services);
        return fail("state not written");
    }
    if (!dsk_error_is_ok(dsk_installed_state_parse(&state_bytes[0],
                                                    (dsk_u32)state_bytes.size(),
                                                    &state))) {
        dss_services_shutdown(&services);
        return fail("state parse failed");
    }
    if (!read_bytes(&services.fs, "out/audit.tlv", audit_bytes)) {
        dss_services_shutdown(&services);
        return fail("audit not written");
    }
    if (!dsk_error_is_ok(dsk_audit_parse(&audit_bytes[0],
                                         (dsk_u32)audit_bytes.size(),
                                         &audit))) {
        dss_services_shutdown(&services);
        return fail("audit parse failed");
    }
    if (!read_install_file(&services, installed)) {
        dss_services_shutdown(&services);
        return fail("installed file missing");
    }
    if (installed != payload) {
        dss_services_shutdown(&services);
        return fail("installed file mismatch");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_fail_mid_commit_then_rollback_restores_pristine(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> old_payload;
    std::vector<dsk_u8> installed;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;

    payload.assign(5u, 0u);
    payload[0] = 'n';
    payload[1] = 'e';
    payload[2] = 'w';
    payload[3] = '!';
    payload[4] = '\n';

    old_payload.assign(3u, 0u);
    old_payload[0] = 'o';
    old_payload[1] = 'l';
    old_payload[2] = 'd';

    if (!init_services("commit_fail_rollback", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!write_install_file(&services, old_payload)) {
        dss_services_shutdown(&services);
        return fail("install seed failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint("mid_commit_step_2");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("expected apply failure");
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = "out/journal.tlv";
    resume.out_audit_path = "out/rollback_audit.tlv";
    st = dsk_rollback(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("rollback failed", st);
    }

    if (!read_install_file(&services, installed)) {
        dss_services_shutdown(&services);
        return fail("installed file missing after rollback");
    }
    if (installed != old_payload) {
        dss_services_shutdown(&services);
        return fail("rollback did not restore old payload");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_fail_mid_commit_then_resume_completes(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> old_payload;
    std::vector<dsk_u8> installed;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;

    payload.assign(6u, 0u);
    payload[0] = 'n';
    payload[1] = 'e';
    payload[2] = 'w';
    payload[3] = '2';
    payload[4] = '!';
    payload[5] = '\n';

    old_payload.assign(3u, 0u);
    old_payload[0] = 'o';
    old_payload[1] = 'l';
    old_payload[2] = 'd';

    if (!init_services("commit_fail_resume", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!write_install_file(&services, old_payload)) {
        dss_services_shutdown(&services);
        return fail("install seed failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint("mid_commit_step_2");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("expected apply failure");
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = "out/journal.tlv";
    resume.out_state_path = "out/state.tlv";
    resume.out_audit_path = "out/resume_audit.tlv";
    st = dsk_resume(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("resume failed", st);
    }

    if (!read_install_file(&services, installed)) {
        dss_services_shutdown(&services);
        return fail("installed file missing after resume");
    }
    if (installed != payload) {
        dss_services_shutdown(&services);
        return fail("resume did not install payload");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_crash_during_stage_then_resume(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> installed;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;

    payload.assign(4u, 0u);
    payload[0] = 's';
    payload[1] = 't';
    payload[2] = 'a';
    payload[3] = 'g';

    if (!init_services("stage_fail_resume", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint("after_stage_extract");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("expected stage failure");
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = "out/journal.tlv";
    resume.out_state_path = "out/state.tlv";
    resume.out_audit_path = "out/resume_audit.tlv";
    st = dsk_resume(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("resume failed", st);
    }

    if (!read_install_file(&services, installed)) {
        dss_services_shutdown(&services);
        return fail("installed file missing after resume");
    }
    if (installed != payload) {
        dss_services_shutdown(&services);
        return fail("resume did not install payload");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_no_in_place_mutation(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> installed;
    dsk_apply_request_t apply;
    dsk_status_t st;

    payload.assign(3u, 0u);
    payload[0] = 'n';
    payload[1] = 'e';
    payload[2] = 'w';

    if (!init_services("no_in_place", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint("after_stage_extract");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("expected stage failure");
    }

    set_failpoint(0);
    if (read_install_file(&services, installed)) {
        dss_services_shutdown(&services);
        return fail("live install mutated before commit");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_deterministic_journals(void) {
    dss_services_t services;
    std::string root;
    dsk_plan_t plan;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload;
    std::vector<dsk_u8> journal_a;
    std::vector<dsk_u8> journal_b;
    std::vector<dsk_u8> txn_a;
    std::vector<dsk_u8> txn_b;
    dsk_apply_request_t apply;
    dsk_status_t st;

    payload.assign(5u, 0u);
    payload[0] = 'd';
    payload[1] = 'e';
    payload[2] = 't';
    payload[3] = '1';
    payload[4] = '\n';

    if (!init_services("deterministic_journals", &services, root)) {
        return fail("init services failed");
    }
    if (!build_plan_bytes(payload, &plan, plan_bytes)) {
        dss_services_shutdown(&services);
        return fail("plan build failed");
    }
    if (!write_payload(&services, payload)) {
        dss_services_shutdown(&services);
        return fail("payload write failed");
    }
    if (!services.fs.make_dir ||
        !dss_error_is_ok(services.fs.make_dir(services.fs.ctx, "out"))) {
        dss_services_shutdown(&services);
        return fail("output dir failed");
    }

    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("first apply failed", st);
    }
    if (!read_bytes(&services.fs, "out/journal.tlv", journal_a)) {
        dss_services_shutdown(&services);
        return fail("journal A missing");
    }
    if (!read_bytes(&services.fs, "out/journal.tlv.txn.tlv", txn_a)) {
        dss_services_shutdown(&services);
        return fail("txn A missing");
    }

    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail_status("second apply failed", st);
    }
    if (!read_bytes(&services.fs, "out/journal.tlv", journal_b)) {
        dss_services_shutdown(&services);
        return fail("journal B missing");
    }
    if (!read_bytes(&services.fs, "out/journal.tlv.txn.tlv", txn_b)) {
        dss_services_shutdown(&services);
        return fail("txn B missing");
    }

    if (journal_a.size() != journal_b.size() ||
        std::memcmp(&journal_a[0], &journal_b[0], journal_a.size()) != 0) {
        dss_services_shutdown(&services);
        return fail("job journal not deterministic");
    }
    if (txn_a.size() != txn_b.size() ||
        std::memcmp(&txn_a[0], &txn_b[0], txn_a.size()) != 0) {
        dss_services_shutdown(&services);
        return fail("txn journal not deterministic");
    }

    dss_services_shutdown(&services);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: setup2_apply_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "apply_fresh_install_succeeds") == 0) {
        return test_apply_fresh_install_succeeds();
    }
    if (std::strcmp(argv[1], "fail_mid_commit_then_rollback_restores_pristine") == 0) {
        return test_fail_mid_commit_then_rollback_restores_pristine();
    }
    if (std::strcmp(argv[1], "fail_mid_commit_then_resume_completes") == 0) {
        return test_fail_mid_commit_then_resume_completes();
    }
    if (std::strcmp(argv[1], "crash_during_stage_then_resume") == 0) {
        return test_crash_during_stage_then_resume();
    }
    if (std::strcmp(argv[1], "no_in_place_mutation") == 0) {
        return test_no_in_place_mutation();
    }
    if (std::strcmp(argv[1], "deterministic_journals") == 0) {
        return test_deterministic_journals();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
