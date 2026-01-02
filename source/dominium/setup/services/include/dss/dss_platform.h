#ifndef DSS_PLATFORM_H
#define DSS_PLATFORM_H

#include "dss_error.h"

#ifdef __cplusplus
#include <string>

#define DSS_OS_FAMILY_UNKNOWN 0u
#define DSS_OS_FAMILY_WINDOWS 1u
#define DSS_OS_FAMILY_MACOS 2u
#define DSS_OS_FAMILY_LINUX 3u

#define DSS_ARCH_UNKNOWN 0u
#define DSS_ARCH_X86 1u
#define DSS_ARCH_X64 2u
#define DSS_ARCH_ARM32 3u
#define DSS_ARCH_ARM64 4u

struct dss_platform_api_t {
    void *ctx;
    dss_error_t (*get_platform_triple)(void *ctx, std::string *out_triple);
    dss_error_t (*get_os_family)(void *ctx, dss_u16 *out_family);
    dss_error_t (*get_arch)(void *ctx, dss_u16 *out_arch);
};

#endif /* __cplusplus */

#endif /* DSS_PLATFORM_H */
