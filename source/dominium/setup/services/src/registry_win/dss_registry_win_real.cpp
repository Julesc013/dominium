#include "dss/dss_services.h"

void dss_registry_win_init_stub(dss_registry_win_api_t *api, dss_u32 kind);

void dss_registry_win_init_real(dss_registry_win_api_t *api) {
#if defined(_WIN32)
    dss_registry_win_init_stub(api, 1u);
#else
    dss_registry_win_init_stub(api, 1u);
#endif
}
