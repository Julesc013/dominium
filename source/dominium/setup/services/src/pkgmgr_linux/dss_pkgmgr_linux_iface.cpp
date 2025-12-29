#include "dss/dss_services.h"

static dss_error_t dss_pkgmgr_linux_query_stub(void *ctx,
                                               const char *package_name,
                                               dss_bool *out_installed) {
    (void)ctx;
    (void)package_name;
    if (out_installed) {
        *out_installed = DSS_FALSE;
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

void dss_pkgmgr_linux_shutdown(dss_pkgmgr_linux_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->query_installed = 0;
}

void dss_pkgmgr_linux_init_stub(dss_pkgmgr_linux_api_t *api, dss_u32 kind) {
    if (!api) {
        return;
    }
    api->ctx = new dss_u32(kind);
    api->query_installed = dss_pkgmgr_linux_query_stub;
}
