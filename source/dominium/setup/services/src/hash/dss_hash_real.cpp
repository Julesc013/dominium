#include "dss_hash_internal.h"

static dss_error_t dss_hash_real_bytes(void *ctx,
                                       const dss_u8 *data,
                                       dss_u32 len,
                                       dss_u64 *out_digest) {
    (void)ctx;
    return dss_hash_compute_bytes(data, len, out_digest);
}

static dss_error_t dss_hash_real_file(void *ctx,
                                      const char *path,
                                      dss_u64 *out_digest) {
    (void)ctx;
    return dss_hash_compute_file(path, out_digest);
}

void dss_hash_init_real(dss_hash_api_t *api) {
    dss_u32 *kind;
    if (!api) {
        return;
    }
    kind = new dss_u32(1u);
    api->ctx = kind;
    api->compute_digest64_bytes = dss_hash_real_bytes;
    api->compute_digest64_file = dss_hash_real_file;
}
