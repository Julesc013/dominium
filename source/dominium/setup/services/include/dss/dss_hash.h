#ifndef DSS_HASH_H
#define DSS_HASH_H

#include "dss_error.h"

#ifdef __cplusplus

struct dss_hash_api_t {
    void *ctx;
    dss_error_t (*compute_digest64_bytes)(void *ctx,
                                          const dss_u8 *data,
                                          dss_u32 len,
                                          dss_u64 *out_digest);
    dss_error_t (*compute_digest64_file)(void *ctx,
                                         const char *path,
                                         dss_u64 *out_digest);
};

#endif /* __cplusplus */

#endif /* DSS_HASH_H */
