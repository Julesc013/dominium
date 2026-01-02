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

#include <cstdio>
#include <cstdlib>
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

struct conformance_case_result_t {
    std::string name;
    std::string status;
    std::string duration_policy;
    std::string sandbox_root;
    std::string manifest_path;
    std::string request_path;
    std::string plan_path;
    std::string state_path;
    std::string audit_path;
    std::string journal_path;
    std::string txn_path;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    dsk_u64 plan_digest;
    dsk_u64 state_digest;
    dsk_u64 audit_digest;
    dsk_u64 journal_digest;
    dsk_u64 txn_digest;
};

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

static std::string join_path(const std::string &a, const std::string &b) {
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/' || a[a.size() - 1u] == '\\') {
        return a + b;
    }
    return a + "/" + b;
}

static int read_file_native(const std::string &path, std::vector<dsk_u8> &out) {
    std::FILE *in = std::fopen(path.c_str(), "rb");
    if (!in) {
        return 0;
    }
    std::fseek(in, 0, SEEK_END);
    long size = std::ftell(in);
    std::fseek(in, 0, SEEK_SET);
    if (size < 0) {
        std::fclose(in);
        return 0;
    }
    out.resize((size_t)size);
    if (size > 0 && std::fread(&out[0], 1u, (size_t)size, in) != (size_t)size) {
        std::fclose(in);
        return 0;
    }
    std::fclose(in);
    return 1;
}

static int write_file_native(const std::string &path, const std::vector<dsk_u8> &data) {
    std::FILE *out = std::fopen(path.c_str(), "wb");
    if (!out) {
        return 0;
    }
    if (!data.empty()) {
        if (std::fwrite(&data[0], 1u, data.size(), out) != data.size()) {
            std::fclose(out);
            return 0;
        }
    }
    std::fclose(out);
    return 1;
}

static int write_text_native(const std::string &path, const std::string &text) {
    std::vector<dsk_u8> data(text.begin(), text.end());
    return write_file_native(path, data);
}

static dsk_u64 digest_bytes(const std::vector<dsk_u8> &bytes) {
    if (bytes.empty()) {
        return 0u;
    }
    return dsk_digest64_bytes(&bytes[0], (dsk_u32)bytes.size());
}

static int read_file_fs(const dss_fs_api_t *fs,
                        const char *path,
                        std::vector<dsk_u8> &out) {
    if (!fs || !fs->read_file_bytes) {
        return 0;
    }
    return dss_error_is_ok(fs->read_file_bytes(fs->ctx, path, &out));
}

static int write_file_fs(const dss_fs_api_t *fs,
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

static int ensure_dir_fs(const dss_fs_api_t *fs, const char *path) {
    if (!fs || !fs->make_dir) {
        return 0;
    }
    return dss_error_is_ok(fs->make_dir(fs->ctx, path));
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

static std::string hex_u64(dsk_u64 value) {
    char buf[32];
    std::sprintf(buf, "0x%016llx", (unsigned long long)value);
    return std::string(buf);
}

static void json_escape(const std::string &in, std::string &out) {
    size_t i;
    for (i = 0u; i < in.size(); ++i) {
        unsigned char c = (unsigned char)in[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '\"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20u) {
                char buf[8];
                std::sprintf(buf, "\\u%04x", (unsigned)c);
                out += buf;
            } else {
                out.push_back((char)c);
            }
            break;
        }
    }
}

static void json_key_value(std::string &out, const char *key, const std::string &value, int trailing_comma) {
    std::string escaped;
    out += "    \"";
    out += key ? key : "";
    out += "\": \"";
    json_escape(value, escaped);
    out += escaped;
    out += "\"";
    out += trailing_comma ? ",\n" : "\n";
}

static void json_key_value_u64(std::string &out, const char *key, dsk_u64 value, int trailing_comma) {
    out += "    \"";
    out += key ? key : "";
    out += "\": \"";
    out += hex_u64(value);
    out += "\"";
    out += trailing_comma ? ",\n" : "\n";
}

static void json_case_to_string(const conformance_case_result_t &res, std::string &out) {
    out += "  {\n";
    out += "    \"name\": \"";
    {
        std::string escaped;
        json_escape(res.name, escaped);
        out += escaped;
    }
    out += "\",\n";
    out += "    \"status\": \"";
    {
        std::string escaped;
        json_escape(res.status, escaped);
        out += escaped;
    }
    out += "\",\n";
    out += "    \"duration_policy\": \"";
    {
        std::string escaped;
        json_escape(res.duration_policy, escaped);
        out += escaped;
    }
    out += "\",\n";
    out += "    \"artifacts\": {\n";
    json_key_value(out, "sandbox_root", res.sandbox_root, 1);
    json_key_value(out, "manifest", res.manifest_path, 1);
    json_key_value(out, "request", res.request_path, 1);
    json_key_value(out, "plan", res.plan_path, 1);
    json_key_value(out, "state", res.state_path, 1);
    json_key_value(out, "audit", res.audit_path, 1);
    json_key_value(out, "journal", res.journal_path, 1);
    json_key_value(out, "txn_journal", res.txn_path, 0);
    out += "    },\n";
    out += "    \"digests\": {\n";
    json_key_value_u64(out, "manifest", res.manifest_digest, 1);
    json_key_value_u64(out, "request", res.request_digest, 1);
    json_key_value_u64(out, "plan", res.plan_digest, 1);
    json_key_value_u64(out, "state", res.state_digest, 1);
    json_key_value_u64(out, "audit", res.audit_digest, 1);
    json_key_value_u64(out, "journal", res.journal_digest, 1);
    json_key_value_u64(out, "txn_journal", res.txn_digest, 0);
    out += "    }\n";
    out += "  }";
}

static std::string fixture_manifest_v1_name(void) { return "manifest_v1.tlv"; }
static std::string fixture_manifest_v2_name(void) { return "manifest_v2.tlv"; }
static std::string fixture_request_quick_name(void) { return "request_quick.tlv"; }
static std::string fixture_request_custom_name(void) { return "request_custom.tlv"; }

static void payload_bytes_base_v1(std::vector<dsk_u8> &out) {
    const char text[] = "base-v1\n";
    out.assign(text, text + sizeof(text) - 1u);
}

static void payload_bytes_extras_v1(std::vector<dsk_u8> &out) {
    const char text[] = "extras-v1\n";
    out.assign(text, text + sizeof(text) - 1u);
}

static void payload_bytes_base_v2(std::vector<dsk_u8> &out) {
    const char text[] = "base-v2\n";
    out.assign(text, text + sizeof(text) - 1u);
}

static void payload_bytes_extras_v2(std::vector<dsk_u8> &out) {
    const char text[] = "extras-v1\n";
    out.assign(text, text + sizeof(text) - 1u);
}

static int emit_fixture_manifest(const std::string &path,
                                 const std::string &version,
                                 dsk_u64 base_digest,
                                 dsk_u64 base_size,
                                 dsk_u64 extras_digest,
                                 dsk_u64 extras_size) {
    dsk_manifest_t manifest;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    dsk_manifest_clear(&manifest);
    manifest.product_id = "dominium";
    manifest.version = version;
    manifest.build_id = "fixture";
    manifest.supported_targets.push_back("win32_nt5");
    {
        dsk_layout_template_t layout;
        layout.template_id = "root_base";
        layout.target_root = "primary";
        layout.path_prefix = "app";
        manifest.layout_templates.push_back(layout);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "base";
        comp.kind = "runtime";
        comp.default_selected = DSK_TRUE;
        {
            dsk_artifact_t art;
            art.artifact_id = "base_art";
            art.hash = "fixture";
            art.digest64 = base_digest;
            art.size = base_size;
            art.source_path = "base.bin";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        manifest.components.push_back(comp);
    }
    {
        dsk_manifest_component_t comp;
        comp.component_id = "extras";
        comp.kind = "tool";
        comp.default_selected = DSK_FALSE;
        {
            dsk_artifact_t art;
            art.artifact_id = "extras_art";
            art.hash = "fixture";
            art.digest64 = extras_digest;
            art.size = extras_size;
            art.source_path = "extras.bin";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        manifest.components.push_back(comp);
    }

    st = dsk_manifest_write(&manifest, &buf);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    {
        std::vector<dsk_u8> bytes(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
        return write_file_native(path, bytes);
    }
}

static int emit_fixture_request(const std::string &path,
                                dsk_u16 operation,
                                dsk_u16 scope,
                                const std::string &payload_root,
                                const std::vector<std::string> &requested_components) {
    dsk_request_t request;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    dsk_request_clear(&request);
    request.operation = operation;
    request.install_scope = scope;
    request.ui_mode = DSK_UI_MODE_CLI;
    request.policy_flags = DSK_POLICY_DETERMINISTIC;
    request.target_platform_triple = "win32_nt5";
    request.frontend_id = "fixture-cli";
    request.payload_root = payload_root;
    request.requested_components = requested_components;

    st = dsk_request_write(&request, &buf);
    if (!dsk_error_is_ok(st)) {
        return 0;
    }
    {
        std::vector<dsk_u8> bytes(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
        return write_file_native(path, bytes);
    }
}

static int emit_fixtures(const std::string &root) {
    std::vector<dsk_u8> base_v1;
    std::vector<dsk_u8> extras_v1;
    std::vector<dsk_u8> base_v2;
    std::vector<dsk_u8> extras_v2;
    std::string payload_v1 = join_path(root, "payloads/v1");
    std::string payload_v2 = join_path(root, "payloads/v2");

    payload_bytes_base_v1(base_v1);
    payload_bytes_extras_v1(extras_v1);
    payload_bytes_base_v2(base_v2);
    payload_bytes_extras_v2(extras_v2);

    if (!make_dir_recursive(payload_v1) || !make_dir_recursive(payload_v2)) {
        return 0;
    }
    if (!write_file_native(join_path(payload_v1, "base.bin"), base_v1)) return 0;
    if (!write_file_native(join_path(payload_v1, "extras.bin"), extras_v1)) return 0;
    if (!write_file_native(join_path(payload_v2, "base.bin"), base_v2)) return 0;
    if (!write_file_native(join_path(payload_v2, "extras.bin"), extras_v2)) return 0;

    if (!emit_fixture_manifest(join_path(root, fixture_manifest_v1_name()),
                               "1.0.0",
                               digest_bytes(base_v1),
                               (dsk_u64)base_v1.size(),
                               digest_bytes(extras_v1),
                               (dsk_u64)extras_v1.size())) {
        return 0;
    }
    if (!emit_fixture_manifest(join_path(root, fixture_manifest_v2_name()),
                               "2.0.0",
                               digest_bytes(base_v2),
                               (dsk_u64)base_v2.size(),
                               digest_bytes(extras_v2),
                               (dsk_u64)extras_v2.size())) {
        return 0;
    }
    {
        std::vector<std::string> requested;
        if (!emit_fixture_request(join_path(root, fixture_request_quick_name()),
                                  DSK_OPERATION_INSTALL,
                                  DSK_INSTALL_SCOPE_PORTABLE,
                                  "payloads/v1",
                                  requested)) {
            return 0;
        }
        requested.clear();
        requested.push_back("base");
        requested.push_back("extras");
        if (!emit_fixture_request(join_path(root, fixture_request_custom_name()),
                                  DSK_OPERATION_INSTALL,
                                  DSK_INSTALL_SCOPE_PORTABLE,
                                  "payloads/v1",
                                  requested)) {
            return 0;
        }
    }
    return 1;
}

static int init_services(const std::string &sandbox_root,
                         const char *platform_triple,
                         dss_services_t *out_services) {
    dss_services_config_t cfg;
    dss_services_config_init(&cfg);
    cfg.sandbox_root = sandbox_root.c_str();
    cfg.platform_triple = platform_triple ? platform_triple : "";
    return dss_error_is_ok(dss_services_init_fake(&cfg, out_services));
}

static int load_fixture_bytes(const std::string &path, std::vector<dsk_u8> &out) {
    return read_file_native(path, out);
}

static dsk_status_t build_plan_from_bytes(const std::vector<dsk_u8> &manifest_bytes,
                                          const std::vector<dsk_u8> &request_bytes,
                                          const dss_services_t *services,
                                          dsk_plan_t *out_plan,
                                          std::vector<dsk_u8> &out_plan_bytes) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    std::vector<dsk_plan_refusal_t> refusals;
    dsk_splat_selection_t selection;
    dsk_splat_candidate_t selected;
    dsk_status_t st;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    dsk_tlv_buffer_t buf;
    size_t i;

    dsk_manifest_clear(&manifest);
    dsk_request_clear(&request);
    resolved.components.clear();
    resolved.digest64 = 0u;
    refusals.clear();
    dsk_splat_caps_clear(&selected.caps);
    selected.caps_digest64 = 0u;

    st = dsk_manifest_parse(&manifest_bytes[0], (dsk_u32)manifest_bytes.size(), &manifest);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    st = dsk_request_parse(&request_bytes[0], (dsk_u32)request_bytes.size(), &request);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    if (services && services->platform.get_platform_triple) {
        std::string platform_override;
        dss_error_t pst = services->platform.get_platform_triple(services->platform.ctx, &platform_override);
        if (dss_error_is_ok(pst) && !platform_override.empty()) {
            request.target_platform_triple = platform_override;
        }
    }

    st = dsk_splat_select(manifest, request, &selection);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    for (i = 0u; i < selection.candidates.size(); ++i) {
        if (selection.candidates[i].id == selection.selected_id) {
            selected = selection.candidates[i];
            break;
        }
    }
    if (selected.id.empty()) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_VALIDATION_ERROR, DSK_SUBCODE_SPLAT_NOT_FOUND, 0u);
    }

    st = dsk_resolve_components(manifest,
                                request,
                                request.target_platform_triple,
                                &resolved,
                                &refusals);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    manifest_digest = digest_bytes(manifest_bytes);
    request_digest = digest_bytes(request_bytes);
    st = dsk_plan_build(manifest,
                        request,
                        selection.selected_id,
                        selected.caps,
                        selected.caps_digest64,
                        resolved,
                        manifest_digest,
                        request_digest,
                        out_plan);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    st = dsk_plan_write(out_plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    out_plan_bytes.assign(buf.data, buf.data + buf.size);
    dsk_tlv_buffer_free(&buf);
    return st;
}

static int write_payloads_to_sandbox(const dss_services_t *services,
                                     const std::string &payload_root,
                                     const std::vector<dsk_u8> &base_bytes,
                                     const std::vector<dsk_u8> &extras_bytes) {
    if (!services) {
        return 0;
    }
    if (!ensure_dir_fs(&services->fs, payload_root.c_str())) {
        return 0;
    }
    {
        std::string base_path = join_path(payload_root, "base.bin");
        if (!write_file_fs(&services->fs, base_path.c_str(), base_bytes)) {
            return 0;
        }
    }
    {
        std::string extras_path = join_path(payload_root, "extras.bin");
        if (!write_file_fs(&services->fs, extras_path.c_str(), extras_bytes)) {
            return 0;
        }
    }
    return 1;
}

static int read_installed_file(const dss_services_t *services,
                               dsk_u16 scope,
                               std::vector<dsk_u8> &out) {
    dss_scope_paths_t paths;
    if (!services || !services->perms.get_user_scope_paths || !services->perms.get_system_scope_paths) {
        return 0;
    }
    if (scope == DSK_INSTALL_SCOPE_SYSTEM) {
        if (!dss_error_is_ok(services->perms.get_system_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    } else {
        if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    }
    if (paths.install_root.empty()) {
        return 0;
    }
    std::string path = join_path(paths.install_root, "app/base.bin");
    return read_file_fs(&services->fs, path.c_str(), out);
}

static int write_installed_file(const dss_services_t *services,
                                dsk_u16 scope,
                                const std::vector<dsk_u8> &bytes) {
    dss_scope_paths_t paths;
    if (!services || !services->perms.get_user_scope_paths || !services->perms.get_system_scope_paths) {
        return 0;
    }
    if (scope == DSK_INSTALL_SCOPE_SYSTEM) {
        if (!dss_error_is_ok(services->perms.get_system_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    } else {
        if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    }
    if (paths.install_root.empty()) {
        return 0;
    }
    if (!ensure_dir_fs(&services->fs, paths.install_root.c_str())) {
        return 0;
    }
    {
        std::string app_dir = join_path(paths.install_root, "app");
        if (!ensure_dir_fs(&services->fs, app_dir.c_str())) {
            return 0;
        }
    }
    {
        std::string path = join_path(paths.install_root, "app/base.bin");
        return write_file_fs(&services->fs, path.c_str(), bytes);
    }
}

static int installed_file_exists(const dss_services_t *services, dsk_u16 scope) {
    dss_scope_paths_t paths;
    dss_bool exists = DSS_FALSE;
    if (!services || !services->perms.get_user_scope_paths || !services->perms.get_system_scope_paths) {
        return 0;
    }
    if (scope == DSK_INSTALL_SCOPE_SYSTEM) {
        if (!dss_error_is_ok(services->perms.get_system_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    } else {
        if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
            return 0;
        }
    }
    if (paths.install_root.empty()) {
        return 0;
    }
    std::string path = join_path(paths.install_root, "app/base.bin");
    if (!services->fs.exists) {
        return 0;
    }
    return dss_error_is_ok(services->fs.exists(services->fs.ctx, path.c_str(), &exists)) && exists;
}

static int write_user_data(const dss_services_t *services, const std::vector<dsk_u8> &bytes) {
    dss_scope_paths_t paths;
    if (!services || !services->perms.get_user_scope_paths) {
        return 0;
    }
    if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
        return 0;
    }
    if (paths.data_root.empty()) {
        return 0;
    }
    if (!ensure_dir_fs(&services->fs, paths.data_root.c_str())) {
        return 0;
    }
    {
        std::string path = join_path(paths.data_root, "user_data.txt");
        return write_file_fs(&services->fs, path.c_str(), bytes);
    }
}

static int user_data_exists(const dss_services_t *services) {
    dss_scope_paths_t paths;
    dss_bool exists = DSS_FALSE;
    if (!services || !services->perms.get_user_scope_paths || !services->fs.exists) {
        return 0;
    }
    if (!dss_error_is_ok(services->perms.get_user_scope_paths(services->perms.ctx, &paths))) {
        return 0;
    }
    if (paths.data_root.empty()) {
        return 0;
    }
    std::string path = join_path(paths.data_root, "user_data.txt");
    return dss_error_is_ok(services->fs.exists(services->fs.ctx, path.c_str(), &exists)) && exists;
}

static void fill_case_defaults(conformance_case_result_t *out,
                               const std::string &name,
                               const std::string &sandbox_root) {
    if (!out) {
        return;
    }
    out->name = name;
    out->status = "fail";
    out->duration_policy = "not recorded";
    out->sandbox_root = sandbox_root;
    out->manifest_path.clear();
    out->request_path.clear();
    out->plan_path.clear();
    out->state_path.clear();
    out->audit_path.clear();
    out->journal_path.clear();
    out->txn_path.clear();
    out->manifest_digest = 0u;
    out->request_digest = 0u;
    out->plan_digest = 0u;
    out->state_digest = 0u;
    out->audit_digest = 0u;
    out->journal_digest = 0u;
    out->txn_digest = 0u;
}

static void compute_case_digests(const dss_services_t *services,
                                 conformance_case_result_t *out) {
    std::vector<dsk_u8> bytes;
    if (!out) {
        return;
    }
    if (!out->manifest_path.empty() && read_file_native(out->manifest_path, bytes)) {
        out->manifest_digest = digest_bytes(bytes);
    }
    if (!out->request_path.empty()) {
        if (services && read_file_fs(&services->fs, out->request_path.c_str(), bytes)) {
            out->request_digest = digest_bytes(bytes);
        } else if (read_file_native(out->request_path, bytes)) {
            out->request_digest = digest_bytes(bytes);
        }
    }
    if (!out->plan_path.empty() && services && read_file_fs(&services->fs, out->plan_path.c_str(), bytes)) {
        dsk_plan_t plan;
        if (dsk_error_is_ok(dsk_plan_parse(&bytes[0], (dsk_u32)bytes.size(), &plan))) {
            out->plan_digest = plan.plan_digest64;
        } else {
            out->plan_digest = digest_bytes(bytes);
        }
    }
    if (!out->state_path.empty() && services && read_file_fs(&services->fs, out->state_path.c_str(), bytes)) {
        out->state_digest = digest_bytes(bytes);
    }
    if (!out->audit_path.empty() && services && read_file_fs(&services->fs, out->audit_path.c_str(), bytes)) {
        out->audit_digest = digest_bytes(bytes);
    }
    if (!out->journal_path.empty() && services && read_file_fs(&services->fs, out->journal_path.c_str(), bytes)) {
        out->journal_digest = digest_bytes(bytes);
    }
    if (!out->txn_path.empty() && services && read_file_fs(&services->fs, out->txn_path.c_str(), bytes)) {
        out->txn_digest = digest_bytes(bytes);
    }
}

static int run_case_fresh_install_portable(const std::string &fixtures_root,
                                           const std::string &sandbox_root,
                                           conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> installed;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "fresh_install_portable", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_crash_during_staging_resume(const std::string &fixtures_root,
                                                const std::string &sandbox_root,
                                                conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> installed;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "crash_during_staging_resume", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint("after_stage_extract");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = out_case->journal_path.c_str();
    resume.out_state_path = out_case->state_path.c_str();
    resume.out_audit_path = "out/resume_audit.tlv";
    st = dsk_resume(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_crash_during_commit_rollback(const std::string &fixtures_root,
                                                 const std::string &sandbox_root,
                                                 conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> old_payload;
    std::vector<dsk_u8> installed;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "crash_during_commit_rollback", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    old_payload.assign(3u, 0u);
    old_payload[0] = 'o';
    old_payload[1] = 'l';
    old_payload[2] = 'd';
    if (!write_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, old_payload)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint("mid_commit_step_2");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = out_case->journal_path.c_str();
    resume.out_audit_path = "out/rollback_audit.tlv";
    st = dsk_rollback(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != old_payload) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_crash_during_commit_resume(const std::string &fixtures_root,
                                               const std::string &sandbox_root,
                                               conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> old_payload;
    std::vector<dsk_u8> installed;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "crash_during_commit_resume", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    old_payload.assign(3u, 0u);
    old_payload[0] = 'o';
    old_payload[1] = 'l';
    old_payload[2] = 'd';
    if (!write_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, old_payload)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint("mid_commit_step_2");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = out_case->journal_path.c_str();
    resume.out_state_path = out_case->state_path.c_str();
    resume.out_audit_path = "out/resume_audit.tlv";
    st = dsk_resume(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_repair_fixes_corruption(const std::string &fixtures_root,
                                            const std::string &sandbox_root,
                                            conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> bad_payload;
    std::vector<dsk_u8> installed;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "repair_fixes_corruption", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }

    bad_payload.assign(3u, 0u);
    bad_payload[0] = 'b';
    bad_payload[1] = 'a';
    bad_payload[2] = 'd';
    if (!write_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, bad_payload)) {
        dss_services_shutdown(&services);
        return 0;
    }

    {
        dsk_request_t request;
        dsk_tlv_buffer_t buf;
        if (!dsk_error_is_ok(dsk_request_parse(&request_bytes[0],
                                               (dsk_u32)request_bytes.size(),
                                               &request))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request.operation = DSK_OPERATION_REPAIR;
        if (!dsk_error_is_ok(dsk_request_write(&request, &buf))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request_bytes.assign(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }

    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_uninstall_residue(const std::string &fixtures_root,
                                      const std::string &sandbox_root,
                                      conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> user_data;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "uninstall_leaves_only_documented_residue", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    user_data.assign(4u, 0u);
    user_data[0] = 'u';
    user_data[1] = 's';
    user_data[2] = 'e';
    user_data[3] = 'r';
    if (!write_user_data(&services, user_data)) {
        dss_services_shutdown(&services);
        return 0;
    }

    {
        dsk_request_t request;
        dsk_tlv_buffer_t buf;
        if (!dsk_error_is_ok(dsk_request_parse(&request_bytes[0],
                                               (dsk_u32)request_bytes.size(),
                                               &request))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request.operation = DSK_OPERATION_UNINSTALL;
        if (!dsk_error_is_ok(dsk_request_write(&request, &buf))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request_bytes.assign(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed_file_exists(&services, DSK_INSTALL_SCOPE_PORTABLE)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!user_data_exists(&services)) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_upgrade_preserves_user_data(const std::string &fixtures_root,
                                                const std::string &sandbox_root,
                                                conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_v1;
    std::vector<dsk_u8> manifest_v2;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base_v1;
    std::vector<dsk_u8> payload_extras_v1;
    std::vector<dsk_u8> payload_base_v2;
    std::vector<dsk_u8> payload_extras_v2;
    std::vector<dsk_u8> installed;
    std::vector<dsk_u8> user_data;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_resume_request_t resume;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");

    fill_case_defaults(out_case, "upgrade_preserves_user_data_and_can_rollback", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v2_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(join_path(fixtures_root, fixture_manifest_v1_name()), manifest_v1) ||
        !load_fixture_bytes(join_path(fixtures_root, fixture_manifest_v2_name()), manifest_v2) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base_v1);
    payload_bytes_extras_v1(payload_extras_v1);
    payload_bytes_base_v2(payload_base_v2);
    payload_bytes_extras_v2(payload_extras_v2);

    if (!write_payloads_to_sandbox(&services, "payloads/v1", payload_base_v1, payload_extras_v1)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_payloads_to_sandbox(&services, "payloads/v2", payload_base_v2, payload_extras_v2)) {
        dss_services_shutdown(&services);
        return 0;
    }

    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_v1, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    user_data.assign(5u, 0u);
    user_data[0] = 'd';
    user_data[1] = 'a';
    user_data[2] = 't';
    user_data[3] = 'a';
    user_data[4] = '1';
    if (!write_user_data(&services, user_data)) {
        dss_services_shutdown(&services);
        return 0;
    }

    {
        dsk_request_t request;
        dsk_tlv_buffer_t buf;
        if (!dsk_error_is_ok(dsk_request_parse(&request_bytes[0],
                                               (dsk_u32)request_bytes.size(),
                                               &request))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request.operation = DSK_OPERATION_UPGRADE;
        request.payload_root = "payloads/v2";
        if (!dsk_error_is_ok(dsk_request_write(&request, &buf))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request_bytes.assign(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
    }

    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_v2, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    set_failpoint("mid_commit_step_2");
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    set_failpoint(0);
    dsk_resume_request_init(&resume);
    resume.services = &services;
    resume.journal_path = out_case->journal_path.c_str();
    resume.out_audit_path = "out/rollback_audit.tlv";
    st = dsk_rollback(&resume);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base_v1) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!user_data_exists(&services)) {
        dss_services_shutdown(&services);
        return 0;
    }

    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base_v2) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!user_data_exists(&services)) {
        dss_services_shutdown(&services);
        return 0;
    }

    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_offline_install_works(const std::string &fixtures_root,
                                          const std::string &sandbox_root,
                                          conformance_case_result_t *out_case) {
    dss_services_t services;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_bytes;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    std::vector<dsk_u8> installed;
    dsk_plan_t plan;
    dsk_apply_request_t apply;
    dsk_status_t st;
    std::string out_dir = join_path(sandbox_root, "out");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "offline_install_works", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(sandbox_root) || !make_dir_recursive(out_dir)) {
        return 0;
    }
    if (!init_services(sandbox_root, "win32_nt5", &services)) {
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->request_path.c_str(), request_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }

    {
        dsk_request_t request;
        dsk_tlv_buffer_t buf;
        if (!dsk_error_is_ok(dsk_request_parse(&request_bytes[0],
                                               (dsk_u32)request_bytes.size(),
                                               &request))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request.policy_flags = (request.policy_flags | DSK_POLICY_OFFLINE);
        if (!dsk_error_is_ok(dsk_request_write(&request, &buf))) {
            dss_services_shutdown(&services);
            return 0;
        }
        request_bytes.assign(buf.data, buf.data + buf.size);
        dsk_tlv_buffer_free(&buf);
    }

    dsk_plan_clear(&plan);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services, &plan, plan_bytes);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!write_file_fs(&services.fs, out_case->plan_path.c_str(), plan_bytes)) {
        dss_services_shutdown(&services);
        return 0;
    }
    set_failpoint(0);
    dsk_apply_request_init(&apply);
    apply.services = &services;
    apply.plan_bytes = &plan_bytes[0];
    apply.plan_size = (dsk_u32)plan_bytes.size();
    apply.out_state_path = out_case->state_path.c_str();
    apply.out_audit_path = out_case->audit_path.c_str();
    apply.out_journal_path = out_case->journal_path.c_str();
    apply.dry_run = 0u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (!read_installed_file(&services, DSK_INSTALL_SCOPE_PORTABLE, installed)) {
        dss_services_shutdown(&services);
        return 0;
    }
    if (installed != payload_base) {
        dss_services_shutdown(&services);
        return 0;
    }
    out_case->status = "pass";
    compute_case_digests(&services, out_case);
    dss_services_shutdown(&services);
    return 1;
}

static int run_case_determinism_repeatability(const std::string &fixtures_root,
                                              const std::string &sandbox_root,
                                              conformance_case_result_t *out_case) {
    dss_services_t services_a;
    dss_services_t services_b;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    std::vector<dsk_u8> plan_a;
    std::vector<dsk_u8> plan_b;
    std::vector<dsk_u8> journal_a;
    std::vector<dsk_u8> journal_b;
    std::vector<dsk_u8> txn_a;
    std::vector<dsk_u8> txn_b;
    std::vector<dsk_u8> payload_base;
    std::vector<dsk_u8> payload_extras;
    dsk_plan_t plan_obj_a;
    dsk_plan_t plan_obj_b;
    dsk_apply_request_t apply;
    dsk_status_t st;
    std::string root_a = join_path(sandbox_root, "a");
    std::string root_b = join_path(sandbox_root, "b");
    std::string payload_root = "payloads/v1";

    fill_case_defaults(out_case, "determinism_repeatability", sandbox_root);
    std::string fixture_request = join_path(fixtures_root, fixture_request_quick_name());
    out_case->manifest_path = join_path(fixtures_root, fixture_manifest_v1_name());
    out_case->request_path = join_path("out", "request.tlv");
    out_case->plan_path = join_path("out", "plan.tlv");
    out_case->state_path = join_path("out", "state.tlv");
    out_case->audit_path = join_path("out", "audit.tlv");
    out_case->journal_path = join_path("out", "journal.tlv");
    out_case->txn_path = join_path("out", "journal.tlv.txn.tlv");

    remove_dir_recursive(sandbox_root);
    if (!make_dir_recursive(root_a) || !make_dir_recursive(root_b)) {
        return 0;
    }
    if (!init_services(root_a, "win32_nt5", &services_a)) {
        return 0;
    }
    if (!init_services(root_b, "win32_nt5", &services_b)) {
        dss_services_shutdown(&services_a);
        return 0;
    }
    if (!load_fixture_bytes(out_case->manifest_path, manifest_bytes) ||
        !load_fixture_bytes(fixture_request, request_bytes)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    payload_bytes_base_v1(payload_base);
    payload_bytes_extras_v1(payload_extras);
    if (!write_payloads_to_sandbox(&services_a, payload_root, payload_base, payload_extras) ||
        !write_payloads_to_sandbox(&services_b, payload_root, payload_base, payload_extras)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }

    dsk_plan_clear(&plan_obj_a);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services_a, &plan_obj_a, plan_a);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    dsk_plan_clear(&plan_obj_b);
    st = build_plan_from_bytes(manifest_bytes, request_bytes, &services_b, &plan_obj_b, plan_b);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    if (plan_a.size() != plan_b.size() ||
        std::memcmp(&plan_a[0], &plan_b[0], plan_a.size()) != 0) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }

    out_case->sandbox_root = root_a;
    {
        std::string out_dir_a = join_path(root_a, "out");
        std::string out_dir_b = join_path(root_b, "out");
        make_dir_recursive(out_dir_a);
        make_dir_recursive(out_dir_b);
        write_file_fs(&services_a.fs, "out/request.tlv", request_bytes);
        write_file_fs(&services_b.fs, "out/request.tlv", request_bytes);
        write_file_fs(&services_a.fs, "out/plan.tlv", plan_a);
        write_file_fs(&services_b.fs, "out/plan.tlv", plan_b);
    }

    dsk_apply_request_init(&apply);
    apply.services = &services_a;
    apply.plan_bytes = &plan_a[0];
    apply.plan_size = (dsk_u32)plan_a.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 1u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    dsk_apply_request_init(&apply);
    apply.services = &services_b;
    apply.plan_bytes = &plan_b[0];
    apply.plan_size = (dsk_u32)plan_b.size();
    apply.out_state_path = "out/state.tlv";
    apply.out_audit_path = "out/audit.tlv";
    apply.out_journal_path = "out/journal.tlv";
    apply.dry_run = 1u;
    st = dsk_apply_plan(&apply);
    if (!dsk_error_is_ok(st)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    if (!read_file_fs(&services_a.fs, "out/journal.tlv", journal_a) ||
        !read_file_fs(&services_b.fs, "out/journal.tlv", journal_b)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    if (journal_a.size() != journal_b.size() ||
        std::memcmp(&journal_a[0], &journal_b[0], journal_a.size()) != 0) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    if (!read_file_fs(&services_a.fs, "out/journal.tlv.txn.tlv", txn_a) ||
        !read_file_fs(&services_b.fs, "out/journal.tlv.txn.tlv", txn_b)) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }
    if (txn_a.size() != txn_b.size() ||
        std::memcmp(&txn_a[0], &txn_b[0], txn_a.size()) != 0) {
        dss_services_shutdown(&services_a);
        dss_services_shutdown(&services_b);
        return 0;
    }

    {
        std::string json_a;
        std::string json_b;
        if (!dsk_error_is_ok(dsk_plan_dump_json(&plan_obj_a, &json_a)) ||
            !dsk_error_is_ok(dsk_plan_dump_json(&plan_obj_b, &json_b))) {
            dss_services_shutdown(&services_a);
            dss_services_shutdown(&services_b);
            return 0;
        }
        if (json_a != json_b) {
            dss_services_shutdown(&services_a);
            dss_services_shutdown(&services_b);
            return 0;
        }
        write_text_native(join_path(root_a, "out/plan.json"), json_a);
        write_text_native(join_path(root_b, "out/plan.json"), json_b);
    }

    out_case->status = "pass";
    compute_case_digests(&services_a, out_case);
    dss_services_shutdown(&services_a);
    dss_services_shutdown(&services_b);
    return 1;
}
int main(int argc, char **argv) {
    std::string sandbox_root;
    std::string fixtures_root = "tests/setup/fixtures";
    std::string out_json;
    std::string emit_root;
    dsk_bool deterministic = DSK_TRUE;
    int i;

    for (i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--sandbox-root") == 0 && i + 1 < argc) {
            sandbox_root = argv[++i];
        } else if (std::strcmp(argv[i], "--fixtures-root") == 0 && i + 1 < argc) {
            fixtures_root = argv[++i];
        } else if (std::strcmp(argv[i], "--deterministic") == 0 && i + 1 < argc) {
            deterministic = (std::strcmp(argv[++i], "0") == 0) ? DSK_FALSE : DSK_TRUE;
        } else if (std::strcmp(argv[i], "--out-json") == 0 && i + 1 < argc) {
            out_json = argv[++i];
        } else if (std::strcmp(argv[i], "--emit-fixtures") == 0 && i + 1 < argc) {
            emit_root = argv[++i];
        }
    }

    if (!emit_root.empty()) {
        if (!emit_fixtures(emit_root)) {
            std::fprintf(stderr, "failed to emit fixtures\n");
            return 1;
        }
        std::printf("ok\n");
        return 0;
    }

    if (sandbox_root.empty()) {
        std::fprintf(stderr, "usage: setup_conformance_runner --sandbox-root <path> [--fixtures-root <path>] [--deterministic 1] [--out-json <path>]\n");
        return 1;
    }
    (void)deterministic;

    std::vector<conformance_case_result_t> results;
    conformance_case_result_t case_result;
    int all_ok = 1;

    if (!run_case_fresh_install_portable(fixtures_root, join_path(sandbox_root, "fresh_install_portable"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_crash_during_staging_resume(fixtures_root, join_path(sandbox_root, "crash_during_staging_resume"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_crash_during_commit_rollback(fixtures_root, join_path(sandbox_root, "crash_during_commit_rollback"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_crash_during_commit_resume(fixtures_root, join_path(sandbox_root, "crash_during_commit_resume"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_repair_fixes_corruption(fixtures_root, join_path(sandbox_root, "repair_fixes_corruption"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_uninstall_residue(fixtures_root, join_path(sandbox_root, "uninstall_leaves_only_documented_residue"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_upgrade_preserves_user_data(fixtures_root, join_path(sandbox_root, "upgrade_preserves_user_data_and_can_rollback"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_offline_install_works(fixtures_root, join_path(sandbox_root, "offline_install_works"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    if (!run_case_determinism_repeatability(fixtures_root, join_path(sandbox_root, "determinism_repeatability"), &case_result)) {
        all_ok = 0;
    }
    results.push_back(case_result);

    {
        std::string json;
        size_t idx;
        json += "{\n";
        json += "  \"schema_version\": \"setup-conformance-1\",\n";
        json += "  \"cases\": [\n";
        for (idx = 0u; idx < results.size(); ++idx) {
            json_case_to_string(results[idx], json);
            if (idx + 1u < results.size()) {
                json += ",\n";
            } else {
                json += "\n";
            }
        }
        json += "  ]\n";
        json += "}\n";
        if (!out_json.empty()) {
            if (!write_text_native(out_json, json)) {
                std::fprintf(stderr, "failed to write json output\n");
                return 1;
            }
        } else {
            std::printf("%s", json.c_str());
        }
    }

    return all_ok ? 0 : 1;
}
