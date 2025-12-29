#include "dss/dss_perms.h"

void dss_perms_shutdown(dss_perms_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->is_elevated = 0;
    api->request_elevation_supported = 0;
    api->get_user_scope_paths = 0;
    api->get_system_scope_paths = 0;
}
