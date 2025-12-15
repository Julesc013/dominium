/* Determinism invariants (C89).
 *
 * This header is a single place to lock down deterministic assumptions and
 * canonical ordering rules for the Domino engine refactor.
 *
 * It is intentionally limited to:
 *  - compile-time assertions
 *  - macros (and only macros) for canonical comparisons / rounding / ordering
 *
 * Forbidden in deterministic paths (SIM/replay/hash/lockstep):
 *  - float/double/long double arithmetic (no FP in determinism paths)
 *  - tolerance/epsilon-based solvers or comparisons
 *  - pointer-address-based ordering or hashing of raw memory with padding
 *  - unordered iteration (hash tables, unordered_* containers, map iteration
 *    that depends on insertion order, etc.)
 *  - platform/OS/UI-driven state mutation or time sources
 *
 * See: docs/SPEC_DETERMINISM.md
 */
#ifndef D_DET_INVARIANTS_H
#define D_DET_INVARIANTS_H

#include <limits.h>

#include "domino/core/types.h"

/* Enforce "C89 only" when the compiler exposes a standard-version macro.
 * (C90 is treated equivalently here.)
 */
#if defined(__STDC_VERSION__) && (__STDC_VERSION__ >= 199901L)
#error "Determinism paths require ISO C89/C90 (no C99+)."
#endif

/* C89 static assert (typedef-based). */
#define D_STATIC_ASSERT(name, expr) typedef char name[(expr) ? 1 : -1]

/* --- Platform/implementation invariants required for bit-stable determinism --- */
D_STATIC_ASSERT(d_det_char_bit_is_8, (CHAR_BIT == 8));

/* Two's complement integers are required (no ones' complement / sign-magnitude). */
D_STATIC_ASSERT(d_det_twos_complement_required, ((~0) == -1));

/* Deterministic semantics for signed right shift and division are required. */
D_STATIC_ASSERT(d_det_arithmetic_rshift_required, ((-1 >> 1) == -1));
D_STATIC_ASSERT(d_det_truncating_div_required, ((-3 / 2) == -1));

/* Engine base type width assumptions (see domino/core/types.h). */
D_STATIC_ASSERT(d_det_u8_is_1,  (sizeof(u8)  == 1));
D_STATIC_ASSERT(d_det_i8_is_1,  (sizeof(i8)  == 1));
D_STATIC_ASSERT(d_det_u16_is_2, (sizeof(u16) == 2));
D_STATIC_ASSERT(d_det_i16_is_2, (sizeof(i16) == 2));
D_STATIC_ASSERT(d_det_u32_is_4, (sizeof(u32) == 4));
D_STATIC_ASSERT(d_det_i32_is_4, (sizeof(i32) == 4));
D_STATIC_ASSERT(d_det_u64_is_8, (sizeof(u64) == 8));
D_STATIC_ASSERT(d_det_i64_is_8, (sizeof(i64) == 8));

/* --- Canonical comparison helpers ---
 * NOTE: Macro arguments must be side-effect free; many are evaluated multiple
 * times by design (portable C89).
 */
#define D_DET_CMP_U32(a, b) ((((u32)(a)) > ((u32)(b))) - (((u32)(a)) < ((u32)(b))))
#define D_DET_CMP_I32(a, b) ((((i32)(a)) > ((i32)(b))) - (((i32)(a)) < ((i32)(b))))
#define D_DET_CMP_U64(a, b) ((((u64)(a)) > ((u64)(b))) - (((u64)(a)) < ((u64)(b))))
#define D_DET_CMP_I64(a, b) ((((i64)(a)) > ((i64)(b))) - (((i64)(a)) < ((i64)(b))))

/* Lexicographic compare helpers (x,y,z) and (a,b). */
#define D_DET_CMP2_I32(ax, ay, bx, by) \
    (D_DET_CMP_I32((ax), (bx)) ? D_DET_CMP_I32((ax), (bx)) : D_DET_CMP_I32((ay), (by)))

#define D_DET_CMP3_I32(ax, ay, az, bx, by, bz) \
    (D_DET_CMP_I32((ax), (bx)) ? D_DET_CMP_I32((ax), (bx)) : \
        (D_DET_CMP_I32((ay), (by)) ? D_DET_CMP_I32((ay), (by)) : D_DET_CMP_I32((az), (bz))))

/* --- Fixed-point rounding rules (deterministic) ---
 * All downscales must choose an explicit rule; do not rely on implicit casts.
 *
 * Required invariant for these macros:
 *  - arithmetic right shift on signed integers (asserted above)
 *
 * Naming:
 *  - FLOOR: rounds toward negative infinity (matches arithmetic right shift)
 *  - NEAR: rounds to nearest; halves are rounded away from zero
 */
#define D_DET_RSHIFT_FLOOR_I32(v, bits) ((i32)(((i32)(v)) >> (bits)))
#define D_DET_RSHIFT_FLOOR_I64(v, bits) ((i64)(((i64)(v)) >> (bits)))

/* Rounds to nearest integer at the target scale; halves away from zero. */
#define D_DET_RSHIFT_NEAR_I32(v, bits) \
    ((i32)(((v) >= 0) ? \
        (((i64)(v) + ((i64)1 << ((bits) - 1))) >> (bits)) : \
        (((i64)(v) - ((i64)1 << ((bits) - 1))) >> (bits))))

#define D_DET_RSHIFT_NEAR_I64(v, bits) \
    ((i64)(((v) >= 0) ? \
        (((i64)(v) + ((i64)1 << ((bits) - 1))) >> (bits)) : \
        (((i64)(v) - ((i64)1 << ((bits) - 1))) >> (bits))))

/* --- Canonical ordering macros ---
 * These define authoritative ordering for stable sorts in deterministic paths.
 * The "ORDER" macros return -1/0/1 like strcmp/qsort comparators.
 */

/* Stable IDs (entity/domain/packet) are ordered by numeric value. */
#define D_DET_ORDER_ENTITY_ID(a, b) D_DET_CMP_U32((a), (b))
#define D_DET_ORDER_DOMAIN_ID(a, b) D_DET_CMP_U32((a), (b))
#define D_DET_ORDER_PACKET_ID(a, b) D_DET_CMP_U32((a), (b))

/* Chunks are ordered lexicographically by their coordinate triple (cx,cy,cz). */
#define D_DET_ORDER_CHUNK_COORDS(ax, ay, az, bx, by, bz) \
    D_DET_CMP3_I32((ax), (ay), (az), (bx), (by), (bz))

/* --- Runtime determinism sentinels (debug-only) ---
 *
 * These macros are lightweight guardrails intended for critical deterministic
 * paths. They compile to assertions in debug builds and to no-ops in release
 * builds.
 */
#ifndef NDEBUG
#include <assert.h>

/* Guard for canonical iteration order checks (caller supplies condition). */
#define DG_DET_GUARD_ITER_ORDER(cond) assert((cond))

/* Guard for sorted/canonical container invariants (caller supplies condition). */
#define DG_DET_GUARD_SORTED(cond) assert((cond))

/* Marker guard for "no floats in determinism paths"; enforced primarily via
 * regression scans (see docs/DETERMINISM_REGRESSION_RULES.md).
 */
#define DG_DET_GUARD_NO_FLOATS() assert(1)
#else
#define DG_DET_GUARD_ITER_ORDER(cond) ((void)0)
#define DG_DET_GUARD_SORTED(cond)     ((void)0)
#define DG_DET_GUARD_NO_FLOATS()      ((void)0)
#endif

#endif /* D_DET_INVARIANTS_H */
