#include "dss_hash_internal.h"

#include <cstdio>

static const dss_u64 DSS_FNV1A_OFFSET = 14695981039346656037ULL;
static const dss_u64 DSS_FNV1A_PRIME = 1099511628211ULL;

static dss_u64 dss_hash_update(dss_u64 hash, const dss_u8 *data, dss_u32 len) {
    dss_u32 i;
    if (!data || len == 0u) {
        return hash;
    }
    for (i = 0u; i < len; ++i) {
        hash ^= (dss_u64)data[i];
        hash *= DSS_FNV1A_PRIME;
    }
    return hash;
}

dss_error_t dss_hash_compute_bytes(const dss_u8 *data,
                                   dss_u32 len,
                                   dss_u64 *out_digest) {
    if (!out_digest) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    *out_digest = dss_hash_update(DSS_FNV1A_OFFSET, data, len);
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_hash_compute_file(const char *path,
                                  dss_u64 *out_digest) {
    dss_u64 hash = DSS_FNV1A_OFFSET;
    dss_u8 buffer[4096];
    FILE *f;
    size_t n;
    if (!path || !out_digest) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE, 0u);
    }
    f = std::fopen(path, "rb");
    if (!f) {
        return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_IO, DSS_SUBCODE_NONE, 0u);
    }
    while ((n = std::fread(buffer, 1u, sizeof(buffer), f)) > 0u) {
        hash = dss_hash_update(hash, buffer, (dss_u32)n);
    }
    std::fclose(f);
    *out_digest = hash;
    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

void dss_hash_shutdown(dss_hash_api_t *api) {
    if (!api) {
        return;
    }
    delete reinterpret_cast<dss_u32 *>(api->ctx);
    api->ctx = 0;
    api->compute_digest64_bytes = 0;
    api->compute_digest64_file = 0;
}
