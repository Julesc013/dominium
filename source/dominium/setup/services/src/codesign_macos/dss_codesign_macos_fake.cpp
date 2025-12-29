#include "dss/dss_services.h"

void dss_codesign_macos_init_stub(dss_codesign_macos_api_t *api, dss_u32 kind);

void dss_codesign_macos_init_fake(dss_codesign_macos_api_t *api) {
    dss_codesign_macos_init_stub(api, 2u);
}
