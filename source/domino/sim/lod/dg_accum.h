/* Accumulator-safe deferral helpers for deterministic LOD (C89).
 *
 * Accumulators store "owed" changes when work is decimated (stride) or
 * deferred by budgets. Application is deterministic and lossless: the total
 * applied delta equals the total added delta, independent of deferral.
 */
#ifndef DG_ACCUM_H
#define DG_ACCUM_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_accum_type {
    DG_ACCUM_SCALAR_Q32_32 = 1,
    DG_ACCUM_VEC3_Q32_32 = 2,
    DG_ACCUM_COUNT_I64 = 3
} dg_accum_type;

typedef struct dg_accum_vec3_q32_32 {
    q32_32 x;
    q32_32 y;
    q32_32 z;
} dg_accum_vec3_q32_32;

typedef union dg_accum_value {
    q32_32             scalar;
    dg_accum_vec3_q32_32 vec3;
    i64                count;
} dg_accum_value;

typedef struct dg_accum {
    dg_accum_type  type;
    dg_tick        last_add_tick;
    dg_accum_value owed;

    /* Optional per-apply-unit chunk size (all components non-negative).
     * If unit is 0, dg_accum_apply applies all owed in a single unit.
     */
    dg_accum_value unit;
} dg_accum;

typedef void (*dg_accum_apply_fn)(void *user_ctx, dg_accum_type type, dg_accum_value delta);

void dg_accum_init_scalar(dg_accum *a, q32_32 unit);
void dg_accum_init_vec3(dg_accum *a, dg_accum_vec3_q32_32 unit);
void dg_accum_init_count(dg_accum *a, i64 unit);

void dg_accum_clear(dg_accum *a);
d_bool dg_accum_is_empty(const dg_accum *a);

/* Add an owed delta for this tick. The meaning/scale of delta is type-specific
 * (q32_32 for scalar/vec3; i64 for count).
 */
void dg_accum_add(dg_accum *a, dg_accum_value delta, dg_tick tick);

/* Apply owed changes under a caller-owned budget counter.
 * Returns number of apply units consumed.
 */
u32 dg_accum_apply(dg_accum *a, dg_accum_apply_fn apply_fn, void *user_ctx, u32 max_units, u32 *budget_units);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_ACCUM_H */

