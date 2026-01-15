#ifndef DSK_DIGEST_H
#define DSK_DIGEST_H

#include "dsk_types.h"

#ifdef __cplusplus
extern "C" {
#endif

DSK_API dsk_u64 dsk_digest64_init(void);
DSK_API dsk_u64 dsk_digest64_update(dsk_u64 hash, const dsk_u8 *data, dsk_u32 len);
DSK_API dsk_u64 dsk_digest64_bytes(const dsk_u8 *data, dsk_u32 len);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_DIGEST_H */
