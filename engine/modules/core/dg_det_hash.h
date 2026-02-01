/*
FILE: source/domino/core/dg_det_hash.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dg_det_hash
RESPONSIBILITY: Defines internal contract for `dg_det_hash`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
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

