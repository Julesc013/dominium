#include "dss/dss_archive.h"

static dss_error_t dss_archive_fake_not_supported(void *ctx,
                                                  const char *archive_path,
                                                  const char *dest_dir) {
    (void)ctx;
    (void)archive_path;
    (void)dest_dir;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

static dss_error_t dss_archive_fake_validate(void *ctx, const char *archive_path) {
    (void)ctx;
    (void)archive_path;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

void dss_archive_init_fake(dss_archive_api_t *api) {
    dss_u32 *kind;
    if (!api) {
        return;
    }
    kind = new dss_u32(2u);
    api->ctx = kind;
    api->extract_deterministic = dss_archive_fake_not_supported;
    api->validate_archive_table = dss_archive_fake_validate;
}
