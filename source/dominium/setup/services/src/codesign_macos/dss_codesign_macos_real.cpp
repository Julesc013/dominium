#include "dss/dss_services.h"

void dss_codesign_macos_init_stub(dss_codesign_macos_api_t *api, dss_u32 kind);

void dss_codesign_macos_init_real(dss_codesign_macos_api_t *api) {
#if defined(__APPLE__)
    dss_codesign_macos_init_stub(api, 1u);
#else
    dss_codesign_macos_init_stub(api, 1u);
#endif
}
