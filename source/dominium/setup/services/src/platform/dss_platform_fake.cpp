#include "dss_platform_internal.h"

static dss_error_t dss_platform_fake_get_triple(void *vctx, std::string *out_triple) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_triple) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_triple = ctx->triple;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_platform_fake_get_os_family(void *vctx, dss_u16 *out_family) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_family) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_family = ctx->os_family;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_platform_fake_get_arch(void *vctx, dss_u16 *out_arch) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_arch) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_arch = ctx->arch;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_platform_init_fake(dss_platform_api_t *api, const char *triple) {
    dss_platform_context_t *ctx;
    if (!api) {
        return;
    }
    ctx = new dss_platform_context_t();
    ctx->kind = 2u;
    ctx->triple = triple ? triple : "fake";
    ctx->os_family = DSS_OS_FAMILY_UNKNOWN;
    ctx->arch = DSS_ARCH_UNKNOWN;
    api->ctx = ctx;
    api->get_platform_triple = dss_platform_fake_get_triple;
    api->get_os_family = dss_platform_fake_get_os_family;
    api->get_arch = dss_platform_fake_get_arch;
}
