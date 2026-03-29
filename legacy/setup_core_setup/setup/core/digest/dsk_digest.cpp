#include "dsk/dsk_digest.h"

static const dsk_u64 DSK_FNV1A_OFFSET = 14695981039346656037ULL;
static const dsk_u64 DSK_FNV1A_PRIME = 1099511628211ULL;

dsk_u64 dsk_digest64_init(void) {
    return DSK_FNV1A_OFFSET;
}

dsk_u64 dsk_digest64_update(dsk_u64 hash, const dsk_u8 *data, dsk_u32 len) {
    dsk_u32 i;
    if (!data || len == 0u) {
        return hash;
    }
    for (i = 0u; i < len; ++i) {
        hash ^= (dsk_u64)data[i];
        hash *= DSK_FNV1A_PRIME;
    }
    return hash;
}

dsk_u64 dsk_digest64_bytes(const dsk_u8 *data, dsk_u32 len) {
    return dsk_digest64_update(dsk_digest64_init(), data, len);
}
