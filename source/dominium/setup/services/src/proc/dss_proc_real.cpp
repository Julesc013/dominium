#include "dss/dss_proc.h"

static dss_error_t dss_proc_spawn_not_supported(void *ctx,
                                                const dss_proc_spawn_t *req,
                                                dss_proc_result_t *out_result) {
    (void)ctx;
    (void)req;
    (void)out_result;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_NOT_SUPPORTED, DSS_SUBCODE_NONE, 0u);
}

void dss_proc_init_real(dss_proc_api_t *api) {
    dss_u32 *kind;
    if (!api) {
        return;
    }
    kind = new dss_u32(1u);
    api->ctx = kind;
    api->spawn = dss_proc_spawn_not_supported;
}
