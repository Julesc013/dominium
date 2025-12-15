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

