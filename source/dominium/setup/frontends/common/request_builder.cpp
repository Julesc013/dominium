#include "request_builder.h"

#include <algorithm>
#include <cctype>

namespace {

static std::string dsk_lowercase_copy(const std::string &value) {
    std::string out = value;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        char c = out[i];
        if (c >= 'A' && c <= 'Z') {
            out[i] = (char)(c - 'A' + 'a');
        }
    }
    return out;
}

static void dsk_trim_in_place(std::string &value) {
    size_t start = 0u;
    size_t end = value.size();
    while (start < end && (value[start] == ' ' || value[start] == '\t')) {
        ++start;
    }
    while (end > start && (value[end - 1u] == ' ' || value[end - 1u] == '\t')) {
        --end;
    }
    if (start != 0u || end != value.size()) {
        value = value.substr(start, end - start);
    }
}

static void dsk_normalize_component_list(std::vector<std::string> &values) {
    size_t i;
    for (i = 0u; i < values.size(); ++i) {
        dsk_trim_in_place(values[i]);
        values[i] = dsk_lowercase_copy(values[i]);
    }
    values.erase(std::remove(values.begin(), values.end(), std::string()), values.end());
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
}

static std::string dsk_dirname_from_path(const std::string &path) {
    size_t i;
    if (path.empty()) {
        return std::string();
    }
    i = path.find_last_of("/\\");
    if (i == std::string::npos) {
        return std::string();
    }
    if (i == 0u) {
        return path.substr(0u, 1u);
    }
    if (i == 2u && path.size() > 2u && path[1u] == ':') {
        return path.substr(0u, 3u);
    }
    return path.substr(0u, i);
}

static dsk_status_t dsk_canon_path(const dss_services_t *services,
                                   const std::string &path,
                                   std::string *out_path) {
    if (!out_path) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND,
                              DSK_CODE_INVALID_ARGS,
                              DSK_SUBCODE_NONE,
                              0u);
    }
    if (path.empty()) {
        out_path->clear();
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    if (services && services->fs.canonicalize_path) {
        dss_error_t st = services->fs.canonicalize_path(services->fs.ctx,
                                                        path.c_str(),
                                                        out_path);
        if (!dss_error_is_ok(st)) {
            return dss_to_dsk_error(st);
        }
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }
    *out_path = path;
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

} // namespace

void dsk_request_build_opts_init(dsk_request_build_opts_t *opts) {
    if (!opts) {
        return;
    }
    opts->operation = 0u;
    opts->install_scope = 0u;
    opts->ui_mode = 0u;
    opts->policy_flags = 0u;
    opts->required_caps = 0u;
    opts->prohibited_caps = 0u;
    opts->ownership_preference = DSK_OWNERSHIP_ANY;
    opts->preferred_install_root.clear();
    opts->payload_root.clear();
    opts->requested_splat_id.clear();
    opts->frontend_id.clear();
    opts->target_platform_triple.clear();
    opts->manifest_path.clear();
    opts->requested_components.clear();
    opts->excluded_components.clear();
}

dsk_status_t dsk_request_build_request(const dsk_request_build_opts_t *opts,
                                       const dss_services_t *services,
                                       dsk_request_t *out_request) {
    dsk_status_t st;
    dsk_manifest_t manifest;
    std::string preferred_root;
    std::string payload_root;
    std::string platform_triple;
    std::string manifest_path;
    std::vector<dsk_u8> manifest_bytes;

    if (!opts || !out_request) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND,
                              DSK_CODE_INVALID_ARGS,
                              DSK_SUBCODE_NONE,
                              0u);
    }
    if (opts->operation == 0u || opts->install_scope == 0u || opts->ui_mode == 0u ||
        opts->frontend_id.empty()) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND,
                              DSK_CODE_VALIDATION_ERROR,
                              DSK_SUBCODE_MISSING_FIELD,
                              DSK_ERROR_FLAG_USER_ACTIONABLE);
    }

    dsk_request_clear(out_request);
    out_request->operation = opts->operation;
    out_request->install_scope = opts->install_scope;
    out_request->ui_mode = opts->ui_mode;
    out_request->frontend_id = opts->frontend_id;
    out_request->policy_flags = opts->policy_flags;
    out_request->required_caps = opts->required_caps;
    out_request->prohibited_caps = opts->prohibited_caps;
    out_request->ownership_preference = opts->ownership_preference;
    out_request->requested_splat_id = opts->requested_splat_id;

    out_request->requested_components = opts->requested_components;
    out_request->excluded_components = opts->excluded_components;
    dsk_normalize_component_list(out_request->requested_components);
    dsk_normalize_component_list(out_request->excluded_components);

    if (!opts->preferred_install_root.empty()) {
        st = dsk_canon_path(services, opts->preferred_install_root, &preferred_root);
        if (!dsk_error_is_ok(st)) {
            return st;
        }
        out_request->preferred_install_root = preferred_root;
    }

    if (!opts->payload_root.empty()) {
        st = dsk_canon_path(services, opts->payload_root, &payload_root);
        if (!dsk_error_is_ok(st)) {
            return st;
        }
        out_request->payload_root = payload_root;
    } else if (!opts->manifest_path.empty()) {
        st = dsk_canon_path(services, opts->manifest_path, &manifest_path);
        if (!dsk_error_is_ok(st)) {
            return st;
        }
        payload_root = dsk_dirname_from_path(manifest_path);
        if (!payload_root.empty()) {
            out_request->payload_root = payload_root;
        }
    }

    if (!opts->manifest_path.empty() && services && services->fs.read_file_bytes) {
        dss_error_t fst = services->fs.read_file_bytes(services->fs.ctx,
                                                       manifest_path.empty()
                                                       ? opts->manifest_path.c_str()
                                                       : manifest_path.c_str(),
                                                       &manifest_bytes);
        if (!dss_error_is_ok(fst)) {
            return dss_to_dsk_error(fst);
        }
        st = dsk_manifest_parse(manifest_bytes.empty() ? 0 : &manifest_bytes[0],
                                (dsk_u32)manifest_bytes.size(),
                                &manifest);
        if (!dsk_error_is_ok(st)) {
            return st;
        }
    }

    if (!opts->target_platform_triple.empty()) {
        platform_triple = opts->target_platform_triple;
    } else if (services && services->platform.get_platform_triple) {
        dss_error_t pst = services->platform.get_platform_triple(services->platform.ctx,
                                                                 &platform_triple);
        if (!dss_error_is_ok(pst)) {
            return dss_to_dsk_error(pst);
        }
    }

    if (platform_triple.empty()) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND,
                              DSK_CODE_VALIDATION_ERROR,
                              DSK_SUBCODE_MISSING_FIELD,
                              DSK_ERROR_FLAG_USER_ACTIONABLE);
    }
    out_request->target_platform_triple = platform_triple;

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_status_t dsk_request_build_bytes(const dsk_request_build_opts_t *opts,
                                     const dss_services_t *services,
                                     std::vector<dsk_u8> *out_bytes,
                                     dsk_request_t *out_request) {
    dsk_request_t request;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    if (!out_bytes) {
        return dsk_error_make(DSK_DOMAIN_FRONTEND,
                              DSK_CODE_INVALID_ARGS,
                              DSK_SUBCODE_NONE,
                              0u);
    }
    if (!out_request) {
        out_request = &request;
    }

    st = dsk_request_build_request(opts, services, out_request);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    st = dsk_request_write(out_request, &buf);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    out_bytes->assign(buf.data, buf.data + buf.size);
    dsk_tlv_buffer_free(&buf);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}

dsk_u16 dsk_request_parse_operation(const char *value) {
    std::string v = dsk_lowercase_copy(value ? value : "");
    if (v == "install") return DSK_OPERATION_INSTALL;
    if (v == "upgrade") return DSK_OPERATION_UPGRADE;
    if (v == "repair") return DSK_OPERATION_REPAIR;
    if (v == "uninstall") return DSK_OPERATION_UNINSTALL;
    if (v == "verify") return DSK_OPERATION_VERIFY;
    if (v == "status") return DSK_OPERATION_STATUS;
    return 0u;
}

dsk_u16 dsk_request_parse_scope(const char *value) {
    std::string v = dsk_lowercase_copy(value ? value : "");
    if (v == "user") return DSK_INSTALL_SCOPE_USER;
    if (v == "system") return DSK_INSTALL_SCOPE_SYSTEM;
    if (v == "portable") return DSK_INSTALL_SCOPE_PORTABLE;
    return 0u;
}

dsk_u16 dsk_request_parse_ui_mode(const char *value) {
    std::string v = dsk_lowercase_copy(value ? value : "");
    if (v == "gui") return DSK_UI_MODE_GUI;
    if (v == "tui") return DSK_UI_MODE_TUI;
    if (v == "cli") return DSK_UI_MODE_CLI;
    return 0u;
}

dsk_u16 dsk_request_parse_ownership(const char *value) {
    std::string v = dsk_lowercase_copy(value ? value : "");
    if (v == "portable") return DSK_OWNERSHIP_PORTABLE;
    if (v == "pkg") return DSK_OWNERSHIP_PKG;
    if (v == "steam") return DSK_OWNERSHIP_STEAM;
    if (v == "any") return DSK_OWNERSHIP_ANY;
    return 0u;
}
