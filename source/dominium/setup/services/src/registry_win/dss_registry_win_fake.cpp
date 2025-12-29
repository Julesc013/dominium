#include "dss/dss_services.h"

void dss_registry_win_init_stub(dss_registry_win_api_t *api, dss_u32 kind);

void dss_registry_win_init_fake(dss_registry_win_api_t *api) {
    dss_registry_win_init_stub(api, 2u);
}
