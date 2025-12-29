#include "dss/dss_services.h"

void dss_pkgmgr_linux_init_stub(dss_pkgmgr_linux_api_t *api, dss_u32 kind);

void dss_pkgmgr_linux_init_real(dss_pkgmgr_linux_api_t *api) {
#if defined(__linux__)
    dss_pkgmgr_linux_init_stub(api, 1u);
#else
    dss_pkgmgr_linux_init_stub(api, 1u);
#endif
}
