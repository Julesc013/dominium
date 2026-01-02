#include "dss/dss_proc.h"

static dss_error_t dss_proc_spawn_fake(void *ctx,
                                       const dss_proc_spawn_t *req,
                                       dss_proc_result_t *out_result) {
    (void)ctx;
    (void)req;
    if (!out_result) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    out_result->exit_code = 0;
    out_result->stdout_bytes.clear();
    out_result->stderr_bytes.clear();
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_proc_init_fake(dss_proc_api_t *api) {
    dss_u32 *kind;
    if (!api) {
        return;
    }
    kind = new dss_u32(2u);
    api->ctx = kind;
    api->spawn = dss_proc_spawn_fake;
}
