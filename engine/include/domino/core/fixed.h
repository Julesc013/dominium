/*
FILE: include/domino/core/fixed.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/fixed
RESPONSIBILITY: Defines the public contract for `fixed` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-critical fixed-point math; see `docs/specs/SPEC_DETERMINISM.md` and `docs/specs/SPEC_NUMERIC.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Domino fixed-point declarations (C89).
 * All arithmetic is integer-only; determinism across platforms is required.
 *
 * Rounding/shift notes:
 * - This API uses signed shifts for scaling. On supported toolchains, right shift
 *   is arithmetic (see `source/domino/core/det_invariants.h`), which implies
 *   floor-like behavior for negative values when dropping fractional bits.
 */
#ifndef DOMINO_CORE_FIXED_H
#define DOMINO_CORE_FIXED_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* q4_12
 * Purpose: Signed Q4.12 fixed-point scalar (small-range).
 * Representation: `i16` scaled by `2^Q4_12_FRAC_BITS`.
 */
typedef i16 q4_12;   /* 4 integer bits, 12 fractional */
/* q16_16
 * Purpose: Signed Q16.16 fixed-point scalar (general-purpose sim scalar).
 * Representation: `i32` scaled by `2^Q16_16_FRAC_BITS`.
 */
typedef i32 q16_16;  /* 16 integer bits, 16 fractional */
/* q24_8
 * Purpose: Signed Q24.8 fixed-point scalar (medium precision).
 * Representation: `i32` scaled by `2^Q24_8_FRAC_BITS`.
 */
typedef i32 q24_8;   /* 24 integer bits, 8 fractional */
/* q48_16
 * Purpose: Signed Q48.16 fixed-point scalar (large-range quantities).
 * Representation: `i64` scaled by `2^Q48_16_FRAC_BITS`.
 */
typedef i64 q48_16;  /* 48 integer bits, 16 fractional */
/* q32_32
 * Purpose: Signed Q32.32 fixed-point scalar (high-precision intermediate).
 * Representation: `i64` scaled by `2^Q32_32_FRAC_BITS`.
 */
typedef i64 q32_32;  /* 32 integer bits, 32 fractional */

#define Q4_12_FRAC_BITS   12
#define Q16_16_FRAC_BITS  16
#define Q24_8_FRAC_BITS   8
#define Q48_16_FRAC_BITS  16
#define Q32_32_FRAC_BITS  32

/*------------------------------------------------------------
 * Integer conversions
 *------------------------------------------------------------*/

/* d_q4_12_from_int
 * Purpose: Convert an integer to Q4.12 (scaled by 2^12).
 * Parameters:
 *   value (in): Integer value.
 * Returns:
 *   Q4.12 value, saturated to the representable q4_12 range.
 * Preconditions:
 *   `value << Q4_12_FRAC_BITS` must not overflow signed `i32` (C89 left-shift UB).
 */
q4_12  d_q4_12_from_int(i32 value);
/* d_q4_12_to_int
 * Purpose: Convert Q4.12 to integer by dropping fractional bits.
 * Parameters:
 *   value (in): Q4.12 value.
 * Returns:
 *   Integer value produced by arithmetic right shift (implementation-defined for negative on paper;
 *   determinism assumes arithmetic shift per `source/domino/core/det_invariants.h`).
 */
i32    d_q4_12_to_int(q4_12 value);

/* d_q16_16_from_int
 * Purpose: Convert an integer to Q16.16 (scaled by 2^16).
 * Parameters:
 *   value (in): Integer value.
 * Returns:
 *   Q16.16 value (`value << Q16_16_FRAC_BITS`).
 * Preconditions:
 *   `value << Q16_16_FRAC_BITS` must not overflow signed `i32` (C89 left-shift UB).
 */
q16_16 d_q16_16_from_int(i32 value);
/* d_q16_16_to_int
 * Purpose: Convert Q16.16 to integer by dropping fractional bits.
 * Parameters:
 *   value (in): Q16.16 value.
 * Returns:
 *   Integer value produced by arithmetic right shift (see `source/domino/core/det_invariants.h`).
 */
i32    d_q16_16_to_int(q16_16 value);

/* d_q24_8_from_int
 * Purpose: Convert an integer to Q24.8 (scaled by 2^8).
 * Parameters:
 *   value (in): Integer value.
 * Returns:
 *   Q24.8 value (`value << Q24_8_FRAC_BITS`).
 * Preconditions:
 *   `value << Q24_8_FRAC_BITS` must not overflow signed `i32` (C89 left-shift UB).
 */
q24_8  d_q24_8_from_int(i32 value);
/* d_q24_8_to_int
 * Purpose: Convert Q24.8 to integer by dropping fractional bits.
 * Parameters:
 *   value (in): Q24.8 value.
 * Returns:
 *   Integer value produced by arithmetic right shift (see `source/domino/core/det_invariants.h`).
 */
i32    d_q24_8_to_int(q24_8 value);

/* d_q48_16_from_int
 * Purpose: Convert an integer to Q48.16 (scaled by 2^16).
 * Parameters:
 *   value (in): Integer value.
 * Returns:
 *   Q48.16 value, saturated to the representable q48_16 range.
 */
q48_16 d_q48_16_from_int(i64 value);
/* d_q48_16_to_int
 * Purpose: Convert Q48.16 to integer by dropping fractional bits.
 * Parameters:
 *   value (in): Q48.16 value.
 * Returns:
 *   Integer value produced by arithmetic right shift (see `source/domino/core/det_invariants.h`).
 */
i64    d_q48_16_to_int(q48_16 value);

/*------------------------------------------------------------
 * Debug/tooling conversions (not for deterministic simulation)
 *------------------------------------------------------------*/

/* d_q4_12_to_double
 * Purpose: Convert Q4.12 to double for UI/debug tools.
 * Parameters:
 *   value (in): Q4.12 value.
 * Returns:
 *   Floating-point approximation. Not for deterministic paths.
 */
double d_q4_12_to_double(q4_12 value);     /* NOTE: tools/tests only */
/* d_q4_12_from_double
 * Purpose: Convert double to Q4.12 for UI/debug tools.
 * Parameters:
 *   value (in): Floating-point value.
 * Returns:
 *   Quantized Q4.12 value. Not for deterministic paths.
 */
q4_12  d_q4_12_from_double(double value);  /* NOTE: tools/tests only */

/* d_q16_16_to_double
 * Purpose: Convert Q16.16 to double for UI/debug tools.
 * Parameters:
 *   value (in): Q16.16 value.
 * Returns:
 *   Floating-point approximation. Not for deterministic paths.
 */
double d_q16_16_to_double(q16_16 value);     /* NOTE: tools/tests only */
/* d_q16_16_from_double
 * Purpose: Convert double to Q16.16 for UI/debug tools.
 * Parameters:
 *   value (in): Floating-point value.
 * Returns:
 *   Quantized Q16.16 value. Not for deterministic paths.
 */
q16_16 d_q16_16_from_double(double value);   /* NOTE: tools/tests only */

/* d_q24_8_to_double
 * Purpose: Convert Q24.8 to double for UI/debug tools.
 * Parameters:
 *   value (in): Q24.8 value.
 * Returns:
 *   Floating-point approximation. Not for deterministic paths.
 */
double d_q24_8_to_double(q24_8 value);     /* NOTE: tools/tests only */
/* d_q24_8_from_double
 * Purpose: Convert double to Q24.8 for UI/debug tools.
 * Parameters:
 *   value (in): Floating-point value.
 * Returns:
 *   Quantized Q24.8 value. Not for deterministic paths.
 */
q24_8  d_q24_8_from_double(double value);  /* NOTE: tools/tests only */

/* d_q48_16_to_double
 * Purpose: Convert Q48.16 to double for UI/debug tools.
 * Parameters:
 *   value (in): Q48.16 value.
 * Returns:
 *   Floating-point approximation. Not for deterministic paths.
 */
double d_q48_16_to_double(q48_16 value);     /* NOTE: tools/tests only */
/* d_q48_16_from_double
 * Purpose: Convert double to Q48.16 for UI/debug tools.
 * Parameters:
 *   value (in): Floating-point value.
 * Returns:
 *   Quantized Q48.16 value. Not for deterministic paths.
 */
q48_16 d_q48_16_from_double(double value);   /* NOTE: tools/tests only */

/*------------------------------------------------------------
 * Basic arithmetic (saturating)
 *------------------------------------------------------------*/

/* d_q4_12_add
 * Purpose: Add two Q4.12 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated sum.
 */
q4_12  d_q4_12_add(q4_12 a, q4_12 b);
/* d_q4_12_sub
 * Purpose: Subtract two Q4.12 values with saturation (`a - b`).
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated difference.
 */
q4_12  d_q4_12_sub(q4_12 a, q4_12 b);
/* d_q4_12_mul
 * Purpose: Multiply two Q4.12 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated product, rescaled by dropping `Q4_12_FRAC_BITS` via signed shift.
 */
q4_12  d_q4_12_mul(q4_12 a, q4_12 b);
/* d_q4_12_div
 * Purpose: Divide two Q4.12 values with saturation.
 * Parameters:
 *   a (in): Numerator.
 *   b (in): Denominator.
 * Returns:
 *   Saturated quotient. If `b == 0`, returns Q4.12 max/min depending on sign of `a`.
 */
q4_12  d_q4_12_div(q4_12 a, q4_12 b);

/* d_q16_16_add
 * Purpose: Add two Q16.16 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated sum.
 */
q16_16 d_q16_16_add(q16_16 a, q16_16 b);
/* d_q16_16_sub
 * Purpose: Subtract two Q16.16 values with saturation (`a - b`).
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated difference.
 */
q16_16 d_q16_16_sub(q16_16 a, q16_16 b);
/* d_q16_16_mul
 * Purpose: Multiply two Q16.16 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated product, rescaled by dropping `Q16_16_FRAC_BITS` via signed shift.
 */
q16_16 d_q16_16_mul(q16_16 a, q16_16 b);
/* d_q16_16_div
 * Purpose: Divide two Q16.16 values with saturation.
 * Parameters:
 *   a (in): Numerator.
 *   b (in): Denominator.
 * Returns:
 *   Saturated quotient. If `b == 0`, returns Q16.16 max/min depending on sign of `a`.
 */
q16_16 d_q16_16_div(q16_16 a, q16_16 b);

/* d_q24_8_add
 * Purpose: Add two Q24.8 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated sum.
 */
q24_8  d_q24_8_add(q24_8 a, q24_8 b);
/* d_q24_8_sub
 * Purpose: Subtract two Q24.8 values with saturation (`a - b`).
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated difference.
 */
q24_8  d_q24_8_sub(q24_8 a, q24_8 b);
/* d_q24_8_mul
 * Purpose: Multiply two Q24.8 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated product, rescaled by dropping `Q24_8_FRAC_BITS` via signed shift.
 */
q24_8  d_q24_8_mul(q24_8 a, q24_8 b);
/* d_q24_8_div
 * Purpose: Divide two Q24.8 values with saturation.
 * Parameters:
 *   a (in): Numerator.
 *   b (in): Denominator.
 * Returns:
 *   Saturated quotient. If `b == 0`, returns Q24.8 max/min depending on sign of `a`.
 */
q24_8  d_q24_8_div(q24_8 a, q24_8 b);

/* d_q48_16_add
 * Purpose: Add two Q48.16 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated sum.
 */
q48_16 d_q48_16_add(q48_16 a, q48_16 b);
/* d_q48_16_sub
 * Purpose: Subtract two Q48.16 values with saturation (`a - b`).
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated difference.
 */
q48_16 d_q48_16_sub(q48_16 a, q48_16 b);
/* d_q48_16_mul
 * Purpose: Multiply two Q48.16 values with saturation.
 * Parameters:
 *   a,b (in): Operands.
 * Returns:
 *   Saturated product (uses internal 64x64->128 emulation; see `source/domino/core/fixed.c`).
 */
q48_16 d_q48_16_mul(q48_16 a, q48_16 b);
/* d_q48_16_div
 * Purpose: Divide two Q48.16 values with saturation.
 * Parameters:
 *   a (in): Numerator.
 *   b (in): Denominator.
 * Returns:
 *   Saturated quotient. If `b == 0`, returns Q48.16 max/min depending on sign of `a`.
 */
q48_16 d_q48_16_div(q48_16 a, q48_16 b);

/*------------------------------------------------------------
 * Cross-format helpers
 *------------------------------------------------------------*/

/* d_q16_16_from_q4_12
 * Purpose: Convert Q4.12 to Q16.16 by upscaling the fractional bits.
 * Parameters:
 *   v (in): Q4.12 value.
 * Returns:
 *   Equivalent Q16.16 value.
 */
q16_16 d_q16_16_from_q4_12(q4_12 v);
/* d_q4_12_from_q16_16
 * Purpose: Convert Q16.16 to Q4.12 by dropping low fractional bits (no saturation).
 * Parameters:
 *   v (in): Q16.16 value.
 * Returns:
 *   Q4.12 value (may overflow if `v` is outside representable q4_12 range).
 */
q4_12  d_q4_12_from_q16_16(q16_16 v);

/* d_q24_8_from_q16_16
 * Purpose: Convert Q16.16 to Q24.8 by dropping low fractional bits.
 * Parameters:
 *   v (in): Q16.16 value.
 * Returns:
 *   Q24.8 value with saturation to `i32` range.
 */
q24_8  d_q24_8_from_q16_16(q16_16 v);
/* d_q16_16_from_q24_8
 * Purpose: Convert Q24.8 to Q16.16 by upscaling the fractional bits.
 * Parameters:
 *   v (in): Q24.8 value.
 * Returns:
 *   Equivalent Q16.16 value with saturation to `i32` range.
 */
q16_16 d_q16_16_from_q24_8(q24_8 v);

/* d_q48_16_from_q16_16
 * Purpose: Widen Q16.16 to Q48.16 (no rescale; preserves 16 fractional bits).
 * Parameters:
 *   v (in): Q16.16 value.
 * Returns:
 *   Equivalent Q48.16 value.
 */
q48_16 d_q48_16_from_q16_16(q16_16 v);
/* d_q16_16_from_q48_16
 * Purpose: Narrow Q48.16 to Q16.16 with saturation.
 * Parameters:
 *   v (in): Q48.16 value.
 * Returns:
 *   Saturated Q16.16 value.
 */
q16_16 d_q16_16_from_q48_16(q48_16 v);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_FIXED_H */
