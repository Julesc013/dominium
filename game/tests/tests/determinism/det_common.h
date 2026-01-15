/*
FILE: tests/determinism/det_common.h
MODULE: Repository
LAYER / SUBSYSTEM: tests/determinism
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Determinism harness common helpers (C89). */
#ifndef DET_COMMON_H
#define DET_COMMON_H

#include <string.h>

#include "domino/core/types.h"
#include "core/dg_det_hash.h"

#define DET_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

static u64 det_hash_step_u64(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

static u64 det_hash_step_i64(u64 h, i64 v) {
    return dg_det_hash_u64(h ^ (u64)v);
}

#endif /* DET_COMMON_H */

