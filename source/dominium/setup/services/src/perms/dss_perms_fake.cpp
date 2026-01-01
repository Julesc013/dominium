#include "dss_perms_internal.h"

static dss_error_t dss_perms_is_elevated_fake(void *ctx, dss_bool *out_is_elevated) {
    (void)ctx;
    if (!out_is_elevated) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_is_elevated = DSS_FALSE;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_perms_request_elevation_fake(void *ctx, dss_bool *out_supported) {
    (void)ctx;
    if (!out_supported) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_supported = DSS_FALSE;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_perms_user_paths_fake(void *ctx, dss_scope_paths_t *out_paths) {
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

static dss_error_t dss_perms_system_paths_fake(void *ctx, dss_scope_paths_t *out_paths) {
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

void dss_perms_init_fake(dss_perms_api_t *api, const char *sandbox_root) {
    dss_perms_context_t *ctx;
    std::string root = sandbox_root ? sandbox_root : ".";
    if (!api) {
        return;
    }
    ctx = new dss_perms_context_t();
    ctx->user_install_root = "install";
    ctx->system_install_root = "system";
    ctx->user_data_root = "data";
    ctx->system_data_root = "data_system";
    api->ctx = ctx;
    api->is_elevated = dss_perms_is_elevated_fake;
    api->request_elevation_supported = dss_perms_request_elevation_fake;
    api->get_user_scope_paths = dss_perms_user_paths_fake;
    api->get_system_scope_paths = dss_perms_system_paths_fake;
}
