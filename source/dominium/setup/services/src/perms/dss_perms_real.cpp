#include "dss_perms_internal.h"

#include <cstdlib>

static dss_error_t dss_perms_is_elevated_stub(void *ctx, dss_bool *out_is_elevated) {
    (void)ctx;
    if (!out_is_elevated) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_is_elevated = DSS_FALSE;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_perms_request_elevation_stub(void *ctx, dss_bool *out_supported) {
    (void)ctx;
    if (!out_supported) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_supported = DSS_FALSE;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_perms_user_paths_stub(void *ctx, dss_scope_paths_t *out_paths) {
    dss_perms_context_t *perms = reinterpret_cast<dss_perms_context_t *>(ctx);
    if (!out_paths) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (perms) {
        out_paths->install_root = perms->user_install_root;
        out_paths->data_root = perms->user_data_root;
    } else {
        out_paths->install_root.clear();
        out_paths->data_root.clear();
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_perms_system_paths_stub(void *ctx, dss_scope_paths_t *out_paths) {
    dss_perms_context_t *perms = reinterpret_cast<dss_perms_context_t *>(ctx);
    if (!out_paths) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    if (perms) {
        out_paths->install_root = perms->system_install_root;
        out_paths->data_root = perms->system_data_root;
    } else {
        out_paths->install_root.clear();
        out_paths->data_root.clear();
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static std::string dss_env_or_default(const char *name, const char *fallback) {
    const char *val = name ? std::getenv(name) : 0;
    if (val && val[0]) {
        return std::string(val);
    }
    return fallback ? std::string(fallback) : std::string();
}

void dss_perms_init_real(dss_perms_api_t *api) {
    dss_perms_context_t *ctx;
    std::string user_root;
    std::string system_root;
    if (!api) {
        return;
    }
    ctx = new dss_perms_context_t();
#if defined(_WIN32)
    {
        std::string fallback = dss_env_or_default("LOCALAPPDATA", ".");
        user_root = dss_env_or_default("DOMINIUM_USER_ROOT", fallback.c_str());
        if (!user_root.empty()) {
            user_root += "/Dominium";
        }
    }
    {
        std::string fallback = dss_env_or_default("ProgramFiles", ".");
        system_root = dss_env_or_default("DOMINIUM_SYSTEM_ROOT", fallback.c_str());
        if (!system_root.empty()) {
            system_root += "/Dominium";
        }
    }
#else
    {
        std::string fallback = dss_env_or_default("HOME", ".");
        fallback += "/.dominium";
        user_root = dss_env_or_default("DOMINIUM_USER_ROOT", fallback.c_str());
    }
    system_root = dss_env_or_default("DOMINIUM_SYSTEM_ROOT", "/opt/dominium");
#endif
    ctx->user_install_root = user_root;
    ctx->system_install_root = system_root;
    ctx->user_data_root = user_root.empty() ? std::string() : (user_root + "/data");
    ctx->system_data_root = system_root.empty() ? std::string() : (system_root + "/data");
    api->ctx = ctx;
    api->is_elevated = dss_perms_is_elevated_stub;
    api->request_elevation_supported = dss_perms_request_elevation_stub;
    api->get_user_scope_paths = dss_perms_user_paths_stub;
    api->get_system_scope_paths = dss_perms_system_paths_stub;
}
