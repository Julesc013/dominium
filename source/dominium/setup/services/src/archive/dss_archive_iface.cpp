#include "dss/dss_archive.h"

void dss_archive_shutdown(dss_archive_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->extract_deterministic = 0;
    api->validate_archive_table = 0;
}
