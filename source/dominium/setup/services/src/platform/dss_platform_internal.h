#ifndef DSS_PLATFORM_INTERNAL_H
#define DSS_PLATFORM_INTERNAL_H

#include "dss/dss_platform.h"

#ifdef __cplusplus
#include <string>

struct dss_platform_context_t {
    dss_u32 kind;
    std::string triple;
    dss_u16 os_family;
    dss_u16 arch;
};

#endif /* __cplusplus */

#endif /* DSS_PLATFORM_INTERNAL_H */
