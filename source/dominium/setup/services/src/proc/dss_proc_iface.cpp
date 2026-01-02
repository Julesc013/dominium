#include "dss/dss_proc.h"

void dss_proc_shutdown(dss_proc_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->spawn = 0;
}
