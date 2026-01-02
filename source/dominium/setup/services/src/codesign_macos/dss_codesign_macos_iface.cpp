#include "dss/dss_services.h"

static dss_error_t dss_codesign_macos_sign_stub(void *ctx, const char *path) {
    (void)ctx;
    (void)path;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

void dss_codesign_macos_shutdown(dss_codesign_macos_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->sign_path = 0;
}

void dss_codesign_macos_init_stub(dss_codesign_macos_api_t *api, dss_u32 kind) {
    if (!api) {
        return;
    }
    api->ctx = new dss_u32(kind);
    api->sign_path = dss_codesign_macos_sign_stub;
}
