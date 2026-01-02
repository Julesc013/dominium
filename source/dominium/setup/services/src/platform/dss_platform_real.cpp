#include "dss_platform_internal.h"

static dss_error_t dss_platform_get_triple(void *vctx, std::string *out_triple) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_triple) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_triple = ctx->triple;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_platform_get_os_family(void *vctx, dss_u16 *out_family) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_family) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_family = ctx->os_family;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_platform_get_arch(void *vctx, dss_u16 *out_arch) {
    dss_platform_context_t *ctx = reinterpret_cast<dss_platform_context_t *>(vctx);
    if (!ctx || !out_arch) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_arch = ctx->arch;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

static void dss_platform_fill_real(dss_platform_context_t *ctx) {
    if (!ctx) {
        return;
    }
#if defined(_WIN32)
    ctx->os_family = DSS_OS_FAMILY_WINDOWS;
    ctx->triple = "win32";
#elif defined(__APPLE__)
    ctx->os_family = DSS_OS_FAMILY_MACOS;
    ctx->triple = "macos";
#elif defined(__linux__)
    ctx->os_family = DSS_OS_FAMILY_LINUX;
    ctx->triple = "linux";
#else
    ctx->os_family = DSS_OS_FAMILY_UNKNOWN;
    ctx->triple = "unknown";
#endif

#if defined(_M_X64) || defined(__x86_64__) || defined(__amd64__)
    ctx->arch = DSS_ARCH_X64;
#elif defined(_M_IX86) || defined(__i386__)
    ctx->arch = DSS_ARCH_X86;
#elif defined(_M_ARM64) || defined(__aarch64__)
    ctx->arch = DSS_ARCH_ARM64;
#elif defined(_M_ARM) || defined(__arm__)
    ctx->arch = DSS_ARCH_ARM32;
#else
    ctx->arch = DSS_ARCH_UNKNOWN;
#endif
}

void dss_platform_init_real(dss_platform_api_t *api) {
    dss_platform_context_t *ctx;
    if (!api) {
        return;
    }
    ctx = new dss_platform_context_t();
    ctx->kind = 1u;
    dss_platform_fill_real(ctx);
    api->ctx = ctx;
    api->get_platform_triple = dss_platform_get_triple;
    api->get_os_family = dss_platform_get_os_family;
    api->get_arch = dss_platform_get_arch;
}

void dss_platform_shutdown(dss_platform_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_platform_context_t *>(api->ctx);
    api->ctx = 0;
    api->get_platform_triple = 0;
    api->get_os_family = 0;
    api->get_arch = 0;
}
