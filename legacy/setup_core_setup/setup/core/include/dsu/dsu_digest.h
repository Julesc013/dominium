/*
FILE: source/dominium/setup/core/include/dsu/dsu_digest.h
MODULE: Dominium Setup
PURPOSE: Deterministic non-cryptographic digests for plan/manifest IDs.
*/
#ifndef DSU_DIGEST_H_INCLUDED
#define DSU_DIGEST_H_INCLUDED

#include "dsu_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* FNV-1a 32-bit */
DSU_API dsu_u32 dsu_digest32_init(void);
DSU_API dsu_u32 dsu_digest32_update(dsu_u32 state, const void *bytes, dsu_u32 len);
DSU_API dsu_u32 dsu_digest32_bytes(const void *bytes, dsu_u32 len);
DSU_API dsu_u32 dsu_digest32_str(const char *s);

/* FNV-1a 64-bit */
DSU_API dsu_u64 dsu_digest64_init(void);
DSU_API dsu_u64 dsu_digest64_update(dsu_u64 state, const void *bytes, dsu_u32 len);
DSU_API dsu_u64 dsu_digest64_bytes(const void *bytes, dsu_u32 len);
DSU_API dsu_u64 dsu_digest64_str(const char *s);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_DIGEST_H_INCLUDED */

