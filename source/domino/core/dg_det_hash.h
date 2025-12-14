/* Deterministic integer hashing helpers (C89).
 *
 * These functions provide bit-stable mixing for stable IDs in deterministic
 * simulation paths (stride decimation, scheduling jitter, etc.).
 *
 * Hashing MUST NOT depend on pointer identity or host endianness.
 */
#ifndef DG_DET_HASH_H
#define DG_DET_HASH_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Bit-mix a 64-bit value into a 64-bit hash.
 * This is a pure function with deterministic arithmetic semantics.
 */
u64 dg_det_hash_u64(u64 v);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DET_HASH_H */

