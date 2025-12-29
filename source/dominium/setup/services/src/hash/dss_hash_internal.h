#ifndef DSS_HASH_INTERNAL_H
#define DSS_HASH_INTERNAL_H

#include "dss/dss_hash.h"

#ifdef __cplusplus
dss_error_t dss_hash_compute_bytes(const dss_u8 *data,
                                   dss_u32 len,
                                   dss_u64 *out_digest);
dss_error_t dss_hash_compute_file(const char *path,
                                  dss_u64 *out_digest);
#endif

#endif /* DSS_HASH_INTERNAL_H */
