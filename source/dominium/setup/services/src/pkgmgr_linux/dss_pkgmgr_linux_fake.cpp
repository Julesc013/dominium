#include "dss/dss_services.h"

void dss_pkgmgr_linux_init_stub(dss_pkgmgr_linux_api_t *api, dss_u32 kind);

void dss_pkgmgr_linux_init_fake(dss_pkgmgr_linux_api_t *api) {
    dss_pkgmgr_linux_init_stub(api, 2u);
}
