#include "dss/dss_services.h"

static dss_error_t dss_registry_win_read_string_stub(void *ctx,
                                                     const char *key,
                                                     const char *value,
                                                     std::string *out_value) {
    (void)ctx;
    (void)key;
    (void)value;
    if (out_value) {
        out_value->clear();
    }
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

void dss_registry_win_shutdown(dss_registry_win_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->read_string = 0;
}

/* Shared stub initializer for non-Windows or placeholder impls. */
void dss_registry_win_init_stub(dss_registry_win_api_t *api, dss_u32 kind) {
    if (!api) {
        return;
    }
    api->ctx = new dss_u32(kind);
    api->read_string = dss_registry_win_read_string_stub;
}
